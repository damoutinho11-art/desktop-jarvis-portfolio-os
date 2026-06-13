import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_asset_universe_classifier import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    classify_asset_class,
    classify_confidence,
    classify_currency_bucket,
    classify_data_completeness,
    classify_evidence_readiness,
    classify_freshness,
    classify_identifier_quality,
    classify_instrument_type,
    classify_normalized_record,
    classify_region_bucket,
    classify_venue_bucket,
    execute_authorized_classified_cache_write,
    evaluate_public_asset_universe_classifier,
    load_json,
    validate_classified_record,
    validate_classifier_config,
    validate_normalized_record_for_classification,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_classifier.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_classifier.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_classifier.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_classifier.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _complete_record(asset_id: str = "etf_vwce_xetra") -> dict:
    records = _complete_data()["normalized_records"]
    return copy.deepcopy(next(record for record in records if record["asset_id"] == asset_id))


class PublicAssetUniverseClassifierTests(unittest.TestCase):
    def test_default_example_blocks_safely(self) -> None:
        result = evaluate_public_asset_universe_classifier(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_BLOCKED_SAFE")
        self.assertEqual(result.classified_record_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_public_asset_universe_classifier(_complete_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_READY_SAFE")
        self.assertEqual(result.classified_record_count, 5)
        self.assertEqual(result.blocked_record_count, 0)
        self.assertEqual(result.duplicate_asset_id_count, 0)

    def test_synthetic_problematic_returns_partial_safe(self) -> None:
        result = evaluate_public_asset_universe_classifier(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_PARTIAL_SAFE")
        self.assertEqual(result.classified_record_count, 2)
        self.assertEqual(result.blocked_record_count, 1)

    def test_synthetic_authorized_write_evaluates_ready_to_write_without_writing(self) -> None:
        result = evaluate_public_asset_universe_classifier(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_READY_TO_WRITE_SAFE")
        self.assertEqual(result.classified_record_count, 1)
        self.assertTrue(result.no_cache_mutated)

    def test_asset_class_and_instrument_type_classifications(self) -> None:
        cases = (
            ("etf_vwce_xetra", "ETF", "ETF"),
            ("equity_msft_nasdaq", "EQUITY", "COMMON_STOCK"),
            ("crypto_asset_btc_public", "CRYPTO_ASSET", "CRYPTO_ASSET"),
            ("market_reference_xetra_public", "MARKET_REFERENCE", "MARKET_REFERENCE"),
            ("unknown_xyz_public", "UNKNOWN_PUBLIC_ASSET", "UNKNOWN_INSTRUMENT"),
        )
        for asset_id, asset_class, instrument_type in cases:
            with self.subTest(asset_id=asset_id):
                record = _complete_record(asset_id)
                self.assertEqual(classify_asset_class(record), asset_class)
                self.assertEqual(classify_instrument_type(record), instrument_type)

    def test_region_currency_venue_and_identifier_buckets_are_deterministic(self) -> None:
        record = _complete_record("etf_vwce_xetra")

        self.assertEqual(classify_region_bucket(record), "REGION_GLOBAL")
        self.assertEqual(classify_currency_bucket(record), "CURRENCY_EUR")
        self.assertEqual(classify_venue_bucket(record), "VENUE_XETRA")
        self.assertEqual(classify_identifier_quality(record), "IDENTIFIER_ISIN_SHAPED")

    def test_completeness_buckets(self) -> None:
        complete = _complete_record()
        partial = copy.deepcopy(complete)
        partial["issuer_or_provider"] = ""
        missing = copy.deepcopy(complete)
        for field in ("display_name", "symbol_or_identifier", "issuer_or_provider", "market_or_region"):
            missing[field] = ""

        self.assertEqual(classify_data_completeness(complete), "COMPLETE_CORE_FIELDS")
        self.assertEqual(classify_data_completeness(partial), "PARTIAL_CORE_FIELDS")
        self.assertEqual(classify_data_completeness(missing), "MISSING_CORE_FIELDS")

    def test_freshness_buckets(self) -> None:
        record = _complete_record()
        cases = (
            ("CACHE_FRESH_SAFE", "FRESH_PUBLIC_DATA"),
            ("FRESH", "FRESH_PUBLIC_DATA"),
            ("CACHE_MANUAL_REVIEW_REQUIRED_SAFE", "MANUAL_REVIEW_PUBLIC_DATA"),
            ("MANUAL", "MANUAL_REVIEW_PUBLIC_DATA"),
            ("CACHE_STALE_SAFE", "STALE_PUBLIC_DATA"),
            ("STALE", "STALE_PUBLIC_DATA"),
            ("mystery", "UNKNOWN_FRESHNESS"),
        )
        for raw, expected in cases:
            with self.subTest(raw=raw):
                mutated = copy.deepcopy(record)
                mutated["data_freshness_status"] = raw
                self.assertEqual(classify_freshness(mutated), expected)

    def test_evidence_readiness_buckets(self) -> None:
        ready = _complete_record()
        needs_more = copy.deepcopy(ready)
        needs_more["issuer_or_provider"] = ""
        manual = copy.deepcopy(ready)
        manual["data_freshness_status"] = "STALE"
        blocked = copy.deepcopy(ready)
        for field in ("display_name", "symbol_or_identifier", "issuer_or_provider", "market_or_region"):
            blocked[field] = ""

        self.assertEqual(classify_evidence_readiness(ready), "READY_FOR_RESEARCH_QUEUE")
        self.assertEqual(classify_evidence_readiness(needs_more), "NEEDS_MORE_PUBLIC_DATA")
        self.assertEqual(classify_evidence_readiness(manual), "NEEDS_MANUAL_SOURCE_REVIEW")
        self.assertEqual(classify_evidence_readiness(blocked), "BLOCKED_BY_MISSING_FIELDS")

    def test_confidence_labels(self) -> None:
        high = _complete_record()
        medium = copy.deepcopy(high)
        medium["isin_or_figi_or_other_public_identifier"] = ""
        low = copy.deepcopy(high)
        low["display_name"] = ""
        low["symbol_or_identifier"] = ""
        blocked = copy.deepcopy(low)
        blocked["issuer_or_provider"] = ""
        blocked["market_or_region"] = ""

        self.assertEqual(classify_confidence(high), "HIGH_STRUCTURAL_CONFIDENCE")
        self.assertEqual(classify_confidence(medium), "MEDIUM_STRUCTURAL_CONFIDENCE")
        self.assertEqual(classify_confidence(low), "MEDIUM_STRUCTURAL_CONFIDENCE")
        self.assertEqual(classify_confidence(blocked), "BLOCKED_STRUCTURAL_CONFIDENCE")

    def test_unsafe_normalized_statuses_block(self) -> None:
        cases = (
            ("evidence_status", "VERIFIED"),
            ("approval_status", "APPROVED"),
            ("investability_status", "INVESTABLE"),
            ("execution_status", "EXECUTABLE"),
            ("screening_status", "SCREENED"),
            ("evidence_pack_status", "GENERATED"),
        )
        for field, value in cases:
            with self.subTest(field=field):
                record = _complete_record()
                record[field] = value
                reasons = validate_normalized_record_for_classification(record)
                self.assertTrue(any(field in reason for reason in reasons))

    def test_classified_record_statuses_remain_safe(self) -> None:
        record = classify_normalized_record(_complete_record(), "2026-06-13")

        self.assertEqual(validate_classified_record(record), ())
        self.assertEqual(record["evidence_status"], "UNVERIFIED_PUBLIC_DATA")
        self.assertEqual(record["approval_status"], "NOT_APPROVED")
        self.assertEqual(record["investability_status"], "NOT_INVESTABLE")
        self.assertEqual(record["execution_status"], "NO_EXECUTION")
        self.assertEqual(record["screening_status"], "NOT_SCREENED")
        self.assertEqual(record["research_score_status"], "NOT_SCORED")
        self.assertEqual(record["recommendation_status"], "NO_RECOMMENDATION")

    def test_classified_record_cannot_contain_unsafe_claims(self) -> None:
        base = classify_normalized_record(_complete_record(), "2026-06-13")
        unsafe_fields = ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created")
        for field in unsafe_fields:
            with self.subTest(field=field):
                mutated = copy.deepcopy(base)
                mutated[field] = True
                self.assertTrue(any(field in reason for reason in validate_classified_record(mutated)))
        mutated = copy.deepcopy(base)
        mutated["recommendation_status"] = "BUY"
        self.assertTrue(validate_classified_record(mutated))

    def test_duplicate_asset_id_is_detected(self) -> None:
        config = _complete_data()
        config["normalized_records"].append(copy.deepcopy(config["normalized_records"][0]))

        result = evaluate_public_asset_universe_classifier(config)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_PARTIAL_SAFE")
        self.assertEqual(result.duplicate_asset_id_count, 1)

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_classifier(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_classified_cache_write(
                config,
                result.classified_records,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["records"][0]["approval_status"], "NOT_APPROVED")
        self.assertEqual(metadata["record_count"], 1)
        self.assertIn("content_sha256", metadata)
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_write_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_public_asset_universe_classifier(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_classified_cache_write(config, result.classified_records, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.classified.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_classifier(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_classified_cache_write(config, result.classified_records, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("classified output root", write_result["blockers"][0])

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_classifier_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_classifier_config(mutated))

    def test_next_manual_actions_are_validated(self) -> None:
        config = _complete_data()
        for action in ("review_classified_public_asset_universe", "proceed_to_research_priority_queue", "fix_normalized_records", "rerun_normalizer", "no_manual_asset_entry_required"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_classifier_config(mutated) if "next_manual_action" in reason])
        for action in ("screen_now", "score_now", "evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_classifier_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_public_asset_universe_classifier as module

        self.assertTrue(hasattr(module, "evaluate_public_asset_universe_classifier"))


if __name__ == "__main__":
    unittest.main()
