import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_asset_universe_normalizer import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_asset_id,
    execute_authorized_normalized_cache_write,
    evaluate_public_asset_universe_normalizer,
    load_json,
    normalize_asset_type,
    normalize_currency,
    normalize_raw_record,
    normalize_symbol,
    validate_normalized_record,
    validate_normalizer_config,
    validate_raw_input,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


class PublicAssetUniverseNormalizerTests(unittest.TestCase):
    def test_default_example_is_safe_ready_noop(self) -> None:
        result = evaluate_public_asset_universe_normalizer(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE")
        self.assertEqual(result.normalized_record_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)
        self.assertTrue(result.normalized_data_unverified)

    def test_synthetic_complete_normalizes_three_asset_types(self) -> None:
        result = evaluate_public_asset_universe_normalizer(_complete_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE")
        self.assertEqual(result.normalized_record_count, 3)
        self.assertEqual({record["asset_type"] for record in result.normalized_records}, {"ETF", "EQUITY", "CRYPTO_ASSET"})
        self.assertEqual({record["approval_status"] for record in result.normalized_records}, {"NOT_APPROVED"})
        self.assertEqual({record["investability_status"] for record in result.normalized_records}, {"NOT_INVESTABLE"})
        self.assertEqual({record["classification_status"] for record in result.normalized_records}, {"NOT_CLASSIFIED"})

    def test_problematic_fixture_skips_stale_or_bad_integrity_input(self) -> None:
        result = evaluate_public_asset_universe_normalizer(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_PARTIAL_SAFE")
        self.assertEqual(result.normalized_record_count, 1)
        self.assertEqual(result.skipped_input_count, 1)

    def test_authorized_fixture_is_ready_to_write_but_not_written_by_evaluation(self) -> None:
        result = evaluate_public_asset_universe_normalizer(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_TO_WRITE_SAFE")
        self.assertEqual(result.normalized_record_count, 1)
        self.assertTrue(result.no_cache_mutated)

    def test_safety_controls_are_required(self) -> None:
        config = _complete_data()
        safety = config["safety_controls"]
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_normalizer_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_normalizer_config(mutated))

    def test_blocked_next_manual_actions_rejected(self) -> None:
        config = _complete_data()
        for action in ("classification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertIn("next_manual_action must be valid.", validate_normalizer_config(mutated))

    def test_normalization_helpers(self) -> None:
        self.assertEqual(normalize_asset_type("exchange traded fund"), "ETF")
        self.assertEqual(normalize_asset_type("stock"), "EQUITY")
        self.assertEqual(normalize_asset_type("crypto"), "CRYPTO_ASSET")
        self.assertEqual(normalize_symbol(" vw ce "), "VWCE")
        self.assertEqual(normalize_currency("eur"), "EUR")
        self.assertEqual(normalize_currency("euro"), "UNKNOWN")

    def test_build_asset_id_is_deterministic(self) -> None:
        record = {"asset_type": "ETF", "ticker": "VWCE", "exchange": "XETRA"}

        self.assertEqual(build_asset_id(record), "etf_vwce_xetra")

    def test_normalized_record_contains_no_unsafe_statuses(self) -> None:
        raw_input = _complete_data()["raw_inputs"][0]
        record = normalize_raw_record(raw_input["raw_records_inline"][0], raw_input, "2026-06-13")

        self.assertEqual(validate_normalized_record(record), ())
        self.assertEqual(record["evidence_status"], "UNVERIFIED_PUBLIC_DATA")
        self.assertEqual(record["approval_status"], "NOT_APPROVED")
        self.assertEqual(record["execution_status"], "NO_EXECUTION")
        self.assertTrue(record["manual_approval_required"])

    def test_unsafe_raw_fields_block(self) -> None:
        raw_input = copy.deepcopy(_complete_data()["raw_inputs"][0])
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "buy_signal", "trade_executed", "registry_mutation"):
            with self.subTest(field=field):
                mutated = copy.deepcopy(raw_input)
                mutated[field] = True
                reasons = validate_raw_input(mutated, "jarvis\\local\\public_asset_universe\\")
                self.assertTrue(any(field in reason for reason in reasons))

    def test_file_backed_paths_must_stay_in_cache_root(self) -> None:
        raw_input = copy.deepcopy(_complete_data()["raw_inputs"][0])
        raw_input["input_mode"] = "file_backed"
        raw_input["raw_cache_path"] = "docs/unsafe.raw.json"
        raw_input["metadata_path"] = "jarvis/local/public_asset_universe/metadata/safe.metadata.json"

        reasons = validate_raw_input(raw_input, "jarvis/local/public_asset_universe")

        self.assertTrue(any("docs" in reason or "configured root" in reason for reason in reasons))

    def test_file_backed_inline_json_loads_from_temp_cache_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path = root / "raw.json"
            metadata_path = root / "metadata.json"
            raw_path.write_text(json.dumps({"records": [{"ticker": "TMP", "name": "Temp asset", "asset_type": "equity", "currency": "USD"}]}), encoding="utf-8")
            metadata_path.write_text("{}", encoding="utf-8")
            config = copy.deepcopy(_complete_data())
            config["cache_root"] = str(root)
            raw_input = copy.deepcopy(config["raw_inputs"][0])
            raw_input["source_id"] = "temp_file_source"
            raw_input["source_name"] = "Temp file source"
            raw_input["source_category_id"] = "equity_listing_sources"
            raw_input["expected_asset_type"] = "EQUITY"
            raw_input["input_mode"] = "file_backed"
            raw_input["raw_cache_path"] = str(raw_path)
            raw_input["metadata_path"] = str(metadata_path)
            raw_input.pop("raw_records_inline", None)
            config["raw_inputs"] = [raw_input]

            result = evaluate_public_asset_universe_normalizer(config)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE")
        self.assertEqual(result.normalized_record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol_or_identifier"], "TMP")

    def test_duplicate_asset_ids_are_blocked(self) -> None:
        config = _complete_data()
        config["raw_inputs"][0]["raw_records_inline"].append(copy.deepcopy(config["raw_inputs"][0]["raw_records_inline"][0]))

        result = evaluate_public_asset_universe_normalizer(config)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_BLOCKED_SAFE")
        self.assertEqual(result.duplicate_asset_id_count, 1)

    def test_wrong_authorization_phrase_blocks_write_helper(self) -> None:
        config = _complete_data()
        result = evaluate_public_asset_universe_normalizer(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_normalized_cache_write(config, result.normalized_records, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.normalized.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_NORMALIZER_BLOCKED_SAFE")

    def test_authorized_write_helper_writes_only_to_explicit_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_normalizer(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_normalized_cache_write(
                config,
                result.normalized_records,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_NORMALIZER_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["records"][0]["approval_status"], "NOT_APPROVED")
        self.assertTrue(payload["normalized_data_unverified"])
        self.assertFalse(metadata["approved_asset"])
        self.assertFalse(metadata["trade_executed"])

    def test_authorized_write_helper_blocks_docs_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_normalizer(config)

        write_result = execute_authorized_normalized_cache_write(config, result.normalized_records, output_root_override="docs")

        self.assertFalse(write_result["written"])
        self.assertIn("normalized output root", write_result["blockers"][0])

    def test_normalizer_does_not_create_recommendations_or_trades(self) -> None:
        result = evaluate_public_asset_universe_normalizer(_complete_data())

        for record in result.normalized_records:
            self.assertEqual(record["approval_status"], "NOT_APPROVED")
            self.assertEqual(record["investability_status"], "NOT_INVESTABLE")
            self.assertEqual(record["execution_status"], "NO_EXECUTION")
            self.assertNotIn("portfolio_weight", record)
            self.assertNotIn("buy_signal", record)
            self.assertNotIn("sell_signal", record)
            self.assertNotIn("trade_executed", record)


if __name__ == "__main__":
    unittest.main()
