import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_asset_universe_research_priority_queue import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_queue_item,
    build_research_priority_reason,
    build_queue_id,
    classify_research_priority_bucket,
    evaluate_public_asset_universe_research_priority_queue,
    execute_authorized_research_queue_cache_write,
    load_json,
    suggest_next_research_step,
    validate_classified_record_for_queue,
    validate_queue_config,
    validate_queue_item,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_research_priority_queue.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_research_priority_queue.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_research_priority_queue.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_research_priority_queue.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _record(asset_id: str) -> dict:
    return copy.deepcopy(next(record for record in _complete_data()["classified_records"] if record["asset_id"] == asset_id))


class PublicAssetUniverseResearchPriorityQueueTests(unittest.TestCase):
    def test_default_example_blocks_safely(self) -> None:
        result = evaluate_public_asset_universe_research_priority_queue(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_BLOCKED_SAFE")
        self.assertEqual(result.queue_item_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_public_asset_universe_research_priority_queue(_complete_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_READY_SAFE")
        self.assertEqual(result.queue_item_count, 6)
        self.assertEqual(result.blocked_record_count, 0)

    def test_synthetic_problematic_returns_partial_safe(self) -> None:
        result = evaluate_public_asset_universe_research_priority_queue(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_PARTIAL_SAFE")
        self.assertEqual(result.queue_item_count, 1)
        self.assertEqual(result.blocked_record_count, 1)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_report_does_not_write(self) -> None:
        result = evaluate_public_asset_universe_research_priority_queue(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_READY_TO_WRITE_SAFE")
        self.assertEqual(result.queue_item_count, 1)
        self.assertTrue(result.no_cache_mutated)

    def test_priority_buckets_work(self) -> None:
        cases = (
            ("etf_vwce_xetra", "RESEARCH_QUEUE_HIGH_READY"),
            ("crypto_btc_public", "RESEARCH_QUEUE_MEDIUM_READY"),
            ("unknown_xyz_public", "RESEARCH_QUEUE_LOW_READY"),
            ("equity_more_data_public", "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA"),
            ("etf_stale_public", "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW"),
            ("blocked_missing_public", "RESEARCH_QUEUE_BLOCKED_SAFE"),
        )
        for asset_id, expected in cases:
            with self.subTest(asset_id=asset_id):
                self.assertEqual(classify_research_priority_bucket(_record(asset_id)), expected)

    def test_suggested_next_research_steps_work(self) -> None:
        cases = (
            ("etf_vwce_xetra", "draft_public_evidence_pack"),
            ("crypto_btc_public", "draft_public_evidence_pack"),
            ("unknown_xyz_public", "draft_public_evidence_pack"),
            ("equity_more_data_public", "collect_more_public_identifiers"),
            ("etf_stale_public", "rerun_source_refresh"),
            ("blocked_missing_public", "fix_classification_inputs"),
        )
        for asset_id, expected in cases:
            with self.subTest(asset_id=asset_id):
                record = _record(asset_id)
                self.assertEqual(suggest_next_research_step(record, classify_research_priority_bucket(record)), expected)

    def test_reason_text_is_deterministic_and_not_buy_sell_recommendation_language(self) -> None:
        record = _record("etf_vwce_xetra")
        reason = build_research_priority_reason(record, classify_research_priority_bucket(record))

        self.assertIn("Workflow bucket RESEARCH_QUEUE_HIGH_READY", reason)
        lowered = reason.lower()
        for forbidden in ("buy", "sell", "recommendation"):
            self.assertNotIn(forbidden, lowered)

    def test_unsafe_classified_records_are_blocked(self) -> None:
        cases = (
            ("evidence_status", "VERIFIED"),
            ("approval_status", "APPROVED"),
            ("investability_status", "INVESTABLE"),
            ("execution_status", "EXECUTABLE"),
            ("screening_status", "SCREENED"),
            ("research_score_status", "SCORED"),
            ("recommendation_status", "BUY"),
        )
        for field, value in cases:
            with self.subTest(field=field):
                record = _record("etf_vwce_xetra")
                record[field] = value
                reasons = validate_classified_record_for_queue(record)
                self.assertTrue(any(field in reason for reason in reasons))

    def test_queue_items_preserve_safe_statuses(self) -> None:
        item = build_queue_item(_record("etf_vwce_xetra"), "2026-06-13")

        self.assertEqual(validate_queue_item(item), ())
        self.assertEqual(item["evidence_pack_status"], "NOT_GENERATED")
        self.assertEqual(item["evidence_status"], "UNVERIFIED_PUBLIC_DATA")
        self.assertEqual(item["approval_status"], "NOT_APPROVED")
        self.assertEqual(item["investability_status"], "NOT_INVESTABLE")
        self.assertEqual(item["execution_status"], "NO_EXECUTION")
        self.assertEqual(item["recommendation_status"], "NO_RECOMMENDATION")
        self.assertEqual(item["allocation_status"], "NO_ALLOCATION")
        self.assertEqual(item["trade_status"], "NO_TRADE")

    def test_queue_id_is_deterministic(self) -> None:
        self.assertEqual(build_queue_id(_record("etf_vwce_xetra")), "research_queue::etf_vwce_xetra")

    def test_duplicate_asset_id_is_detected(self) -> None:
        config = _complete_data()
        config["classified_records"].append(copy.deepcopy(config["classified_records"][0]))

        result = evaluate_public_asset_universe_research_priority_queue(config)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_PARTIAL_SAFE")
        self.assertEqual(result.duplicate_asset_id_count, 1)

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_research_priority_queue(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_research_queue_cache_write(
                config,
                result.queue_items,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["items"][0]["approval_status"], "NOT_APPROVED")
        self.assertEqual(metadata["queue_item_count"], 1)
        self.assertIn("content_sha256", metadata)
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_public_asset_universe_research_priority_queue(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_research_queue_cache_write(config, result.queue_items, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.research_queue.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_asset_universe_research_priority_queue(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_research_queue_cache_write(config, result.queue_items, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("research queue output root", write_result["blockers"][0])

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_queue_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_queue_config(mutated))

    def test_next_manual_actions_are_validated(self) -> None:
        config = _complete_data()
        for action in ("review_research_priority_queue", "proceed_to_public_evidence_pack_draft_generator", "fix_classified_records", "rerun_classifier", "no_manual_asset_entry_required"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_queue_config(mutated) if "next_manual_action" in reason])
        for action in ("evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_queue_config(mutated) if "next_manual_action" in reason])

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_public_asset_universe_research_priority_queue as module

        self.assertTrue(hasattr(module, "evaluate_public_asset_universe_research_priority_queue"))


if __name__ == "__main__":
    unittest.main()
