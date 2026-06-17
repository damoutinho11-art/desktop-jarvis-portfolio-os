import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_1_public_source_fixture_wiring import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    SUPPORTED_FIXTURE_FORMATS,
    SUPPORTED_SOURCE_CATEGORIES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    classify_fixture_status,
    evaluate_v5_1_public_source_fixture_wiring,
    execute_authorized_v5_1_fixture_wiring_snapshot_write,
    load_json,
    map_fixture_to_pipeline,
    validate_fixture_path,
    validate_public_source_fixture_record,
    validate_v5_1_fixture_wiring_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


def _record() -> dict:
    return copy.deepcopy(_complete_data()["public_source_fixture_records"][0])


class V51PublicSourceFixtureWiringTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE")
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_executor)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(_complete_data())

        self.assertEqual(result.status, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_SAFE")
        self.assertEqual(result.fixture_count, 8)
        self.assertEqual(result.ready_fixture_count, 8)
        self.assertEqual(result.mapped_to_pipeline_count, 8)

    def test_synthetic_problematic_returns_blocked_or_partial(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(load_json(PROBLEMATIC_CONFIG))

        self.assertIn(result.status, {"V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE", "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE"})
        self.assertGreater(result.unsafe_fixture_count, 0)
        self.assertGreater(result.blocked_mapping_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_does_not_write(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_TO_WRITE_SAFE")
        self.assertEqual(result.ready_fixture_count, 1)
        self.assertTrue(result.local_fixture_only)

    def test_fixture_id_uniqueness(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(load_json(PROBLEMATIC_CONFIG))

        self.assertGreater(result.duplicate_fixture_id_count, 0)
        self.assertIn("duplicate fixture_id", " ".join(result.blockers))

    def test_supported_source_categories_and_formats_are_accepted(self) -> None:
        config = _complete_data()
        categories = {record["source_category_id"] for record in config["public_source_fixture_records"]}
        formats = {record["fixture_format"] for record in config["public_source_fixture_records"]}

        self.assertTrue(categories.issubset(SUPPORTED_SOURCE_CATEGORIES))
        self.assertTrue(formats.issubset(SUPPORTED_FIXTURE_FORMATS))
        self.assertFalse(validate_public_source_fixture_record(_record(), "jarvis/local/public_source_fixtures"))

    def test_unsupported_source_category_blocks_or_warns(self) -> None:
        record = _record()
        record["source_category_id"] = "unsupported_category"

        self.assertIn("unsupported source_category_id", " ".join(validate_public_source_fixture_record(record, "jarvis/local/public_source_fixtures")))
        self.assertFalse(map_fixture_to_pipeline(record)["mapped"])

    def test_unsupported_format_blocks_or_warns(self) -> None:
        record = _record()
        record["fixture_format"] = "xlsx"

        self.assertIn("unsupported fixture_format", " ".join(validate_public_source_fixture_record(record, "jarvis/local/public_source_fixtures")))

    def test_path_under_allowed_fixture_root_accepted(self) -> None:
        self.assertEqual(validate_fixture_path("jarvis/local/public_source_fixtures/etf/test.csv", "jarvis/local/public_source_fixtures"), ())

    def test_paths_under_committed_or_root_locations_blocked(self) -> None:
        for path in ("docs/test.csv", "templates/test.csv", "jarvis/data/test.csv", "registry/test.csv", "candidate_assets/test.csv", "test.csv"):
            with self.subTest(path=path):
                self.assertTrue(validate_fixture_path(path, "jarvis/local/public_source_fixtures"))

    def test_credential_private_account_fields_blocked(self) -> None:
        record = _record()
        record["api_key"] = "forbidden"

        self.assertIn("forbidden private/credential field", " ".join(validate_public_source_fixture_record(record, "jarvis/local/public_source_fixtures")))

    def test_forbidden_true_flags_block(self) -> None:
        for field in ("downloaded_by_jarvis", "evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "executor_created"):
            with self.subTest(field=field):
                record = _record()
                record[field] = True
                self.assertIn(f"{field} must be false", " ".join(validate_public_source_fixture_record(record, "jarvis/local/public_source_fixtures")))

    def test_fixture_status_missing_stale_manual_refresh_ready(self) -> None:
        record = _record()
        record.pop("fixture_status", None)
        record["fixture_present"] = False
        self.assertEqual(classify_fixture_status(record), "MISSING")
        record = _record()
        record.pop("fixture_status", None)
        record["stale"] = True
        self.assertEqual(classify_fixture_status(record), "STALE")
        record = _record()
        record.pop("fixture_status", None)
        record["manual_refresh_required"] = True
        self.assertEqual(classify_fixture_status(record), "MANUAL_REFRESH_REQUIRED")
        self.assertEqual(classify_fixture_status(_record()), "READY")

    def test_pipeline_mapping_works_for_all_supported_categories(self) -> None:
        for category in SUPPORTED_SOURCE_CATEGORIES:
            with self.subTest(category=category):
                record = _record()
                record["source_category_id"] = category
                mapping = map_fixture_to_pipeline(record)
                self.assertTrue(mapping["mapped"])
                self.assertIn("source_manifest", mapping["pipeline_stages"])
                self.assertIn("e2e_audit", mapping["pipeline_stages"])

    def test_operator_runbook_is_deterministic(self) -> None:
        result = evaluate_v5_1_public_source_fixture_wiring(_complete_data())

        self.assertEqual(result.operator_runbook_steps[0], "Copy the local template into jarvis/local/public_source_fixtures.")
        self.assertIn("fixture import dry-run", " ".join(result.operator_runbook_steps))

    def test_authorized_write_function_writes_snapshot_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_1_public_source_fixture_wiring(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_1_fixture_wiring_snapshot_write(
                config,
                result,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["ready_fixture_count"], 1)
        self.assertTrue(metadata["fixture_data_unverified"])
        for field in ("fetch_executed", "download_executed", "evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_1_public_source_fixture_wiring(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_1_fixture_wiring_snapshot_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_1_public_source_fixture_wiring.snapshot.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE")

    def test_unsafe_top_level_safety_controls_are_blocked(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_1_fixture_wiring_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_1_fixture_wiring_config(mutated))

    def test_valid_and_invalid_next_manual_actions(self) -> None:
        config = _complete_data()
        valid = ("review_public_source_fixture_wiring", "prepare_local_public_source_fixtures", "proceed_to_v5_2_fixture_import_dry_run", "proceed_to_v5_2_explicit_authorized_public_fetch_stub", "no_manual_asset_entry_required")
        for action in valid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_v5_1_fixture_wiring_config(mutated) if "next_manual_action" in reason])
        invalid = ("live_fetch_now", "evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation")
        for action in invalid:
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_v5_1_fixture_wiring_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_1_public_source_fixture_wiring as module

        self.assertTrue(hasattr(module, "evaluate_v5_1_public_source_fixture_wiring"))


if __name__ == "__main__":
    unittest.main()
