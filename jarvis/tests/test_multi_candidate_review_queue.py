import json
import tempfile
import unittest
from pathlib import Path

from jarvis.multi_candidate_review_queue import (
    MultiCandidateReviewQueueConfig,
    build_multi_candidate_review_queue,
    build_multi_candidate_review_queue_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
FRESHNESS_POLICY = "jarvis/data/evidence_freshness_policy.example.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
TARGET = "vwce_global_core_candidate"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        return Path(file.name)


def _private_intake_payload() -> dict:
    return json.loads(Path(PRIVATE_INTAKE).read_text(encoding="utf-8"))


class MultiCandidateReviewQueueTests(unittest.TestCase):
    def test_vwce_is_already_reviewed_when_private_copy_is_supplied(self) -> None:
        queue = build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)
        by_id = {item.asset_id: item for item in queue.items}

        self.assertEqual(by_id[TARGET].review_queue_status, "already_reviewed")
        self.assertEqual(by_id[TARGET].reviewed_status_if_private_copy, "candidate_reviewed")
        self.assertEqual(queue.summary.already_reviewed_count, 1)

    def test_source_registry_remains_unmutated(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_candidate_reviewed_is_not_treated_as_approved_investable(self) -> None:
        queue = build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)
        by_id = {item.asset_id: item for item in queue.items}

        self.assertEqual(by_id[TARGET].review_queue_status, "already_reviewed")
        self.assertEqual(queue.summary.approved_investable_count, 0)

    def test_no_buy_sell_requests_are_created(self) -> None:
        queue = build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)

        self.assertFalse(queue.buy_sell_requests_created)
        self.assertFalse(queue.allocation_recommendation_created)
        self.assertFalse(queue.trades_executed)

    def test_queue_prioritizes_global_core_over_speculative_crypto(self) -> None:
        queue = build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)
        top_sleeves = [item.sleeve for item in queue.top_next_evidence_candidates]

        self.assertIn("global_core", top_sleeves)
        if "speculative_crypto" in top_sleeves:
            self.assertLess(top_sleeves.index("global_core"), top_sleeves.index("speculative_crypto"))

    def test_missing_evidence_creates_needs_verified_evidence(self) -> None:
        queue = build_multi_candidate_review_queue_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG)
        by_id = {item.asset_id: item for item in queue.items}

        item = by_id["spyi_imie_global_core_candidate"]
        self.assertEqual(item.review_queue_status, "needs_verified_evidence")
        self.assertIn("market_data", item.missing_evidence_types)

    def test_stale_evidence_creates_needs_freshness_check(self) -> None:
        payload = _private_intake_payload()
        for record in payload["records"]:
            if record["evidence_type"] == "market_data":
                record["as_of"] = "2026-01-01"
        intake_path = _write_json(payload)
        queue = build_multi_candidate_review_queue(
            SOURCE_REGISTRY,
            None,
            MultiCandidateReviewQueueConfig(
                verified_evidence_intake_path=str(intake_path),
                freshness_policy_path=FRESHNESS_POLICY,
            ),
        )
        by_id = {item.asset_id: item for item in queue.items}

        self.assertEqual(by_id[TARGET].review_queue_status, "needs_freshness_check")
        self.assertIn("market_data", by_id[TARGET].stale_evidence_types)

    def test_complete_fresh_evidence_without_private_copy_is_ready_for_review(self) -> None:
        queue = build_multi_candidate_review_queue(
            SOURCE_REGISTRY,
            None,
            MultiCandidateReviewQueueConfig(
                verified_evidence_intake_path=PRIVATE_INTAKE,
                freshness_policy_path=FRESHNESS_POLICY,
            ),
        )
        by_id = {item.asset_id: item for item in queue.items}

        self.assertEqual(by_id[TARGET].review_queue_status, "ready_for_review")


if __name__ == "__main__":
    unittest.main()
