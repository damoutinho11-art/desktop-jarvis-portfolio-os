import tempfile
import unittest
from pathlib import Path

from jarvis.ftaw_draft_evidence_verification_queue import (
    FTAWDraftEvidenceVerificationTask,
    build_ftaw_draft_evidence_verification_queue_from_files,
    preview_verified_evidence_record,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"
SOURCE_PACK_CONFIG = "jarvis/data/ftaw_source_collection_pack.example.json"
RESEARCH_CONFIG = "jarvis/data/ftaw_public_source_research_pack.example.json"
VERIFICATION_CONFIG = "jarvis/data/ftaw_draft_evidence_verification_queue.example.json"
TARGET = "ftaw_global_core_candidate"


def _queue():
    return build_ftaw_draft_evidence_verification_queue_from_files(
        SOURCE_REGISTRY,
        REVIEWED_REGISTRY,
        QUEUE_CONFIG,
        BATCH_CONFIG,
        EXPANDER_CONFIG,
        PLANNER_CONFIG,
        SOURCE_PACK_CONFIG,
        RESEARCH_CONFIG,
        VERIFICATION_CONFIG,
    )


class FTAWDraftEvidenceVerificationQueueTests(unittest.TestCase):
    def test_only_ftaw_is_included(self) -> None:
        queue = _queue()

        self.assertEqual(queue.target_asset_id, TARGET)
        self.assertEqual({task.asset_id for task in queue.verification_tasks}, {TARGET})

    def test_exactly_five_verification_tasks_are_produced(self) -> None:
        queue = _queue()

        self.assertEqual(queue.draft_records_count, 5)
        self.assertEqual(len(queue.verification_tasks), 5)

    def test_all_current_placeholder_tasks_recommend_needs_correction(self) -> None:
        queue = _queue()

        self.assertEqual(set(queue.recommended_decisions_by_evidence_type.values()), {"needs_correction"})

    def test_accept_with_placeholder_facts_is_blocked(self) -> None:
        task = _queue().verification_tasks[0]

        with self.assertRaises(ValueError):
            preview_verified_evidence_record(task, "accept")

    def test_accept_with_complete_non_placeholder_facts_creates_verified_preview_only(self) -> None:
        task = FTAWDraftEvidenceVerificationTask(
            task_id="verify_draft_ftaw_market_data",
            asset_id=TARGET,
            evidence_type="market_data",
            source_name="FTAW public market source",
            source_quality="manual_research",
            url_reference="https://example.invalid/ftaw-market",
            extracted_facts={
                "price": "100.00",
                "currency": "EUR",
                "source": "public market page",
                "market_date": "2026-06-08",
            },
            verification_questions=("Question?",),
            recommended_decision="accept",
            warnings=(),
            blockers=(),
        )

        preview = preview_verified_evidence_record(task, "accept", "User accepted complete market data evidence.")

        self.assertIsNotNone(preview)
        self.assertEqual(preview["asset_id"], TARGET)
        self.assertTrue(preview["verified_by_user"])
        self.assertEqual(preview["verification_notes"], "User accepted complete market data evidence.")

    def test_reject_and_needs_correction_produce_no_verified_preview(self) -> None:
        task = _queue().verification_tasks[0]

        self.assertIsNone(preview_verified_evidence_record(task, "reject"))
        self.assertIsNone(preview_verified_evidence_record(task, "needs_correction"))

    def test_no_evidence_is_verified_by_default(self) -> None:
        queue = _queue()

        self.assertEqual(queue.accepted_preview_count, 0)
        self.assertTrue(all(task.verification_status == "pending_user_verification" for task in queue.verification_tasks))

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted_previews.json"

            _queue()

            self.assertFalse(target.exists())

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        queue = _queue()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(queue.registry_mutation_performed)
        self.assertFalse(queue.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        queue = _queue()

        self.assertFalse(queue.buy_sell_requests_created)
        self.assertFalse(queue.allocation_recommendation_created)
        self.assertFalse(queue.trades_executed)


if __name__ == "__main__":
    unittest.main()
