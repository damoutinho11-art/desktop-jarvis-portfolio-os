import unittest
from pathlib import Path

from jarvis.ftaw_real_human_approval_review_decision_recorder import (
    build_ftaw_real_human_approval_review_decision_recorder,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import SOURCE_REGISTRY
from jarvis.tests.test_ftaw_real_manual_approval_review_gate import (
    _complete_real_manual_approval_review_gate,
    _partial_real_manual_approval_review_gate,
    _real_manual_approval_review_gate,
)


REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG = "jarvis/data/ftaw_real_human_approval_review_decision_recorder.example.json"
PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG = (
    "jarvis/data/ftaw_real_human_approval_review_decision_recorder.synthetic_partial.example.json"
)
COMPLETE_REAL_HUMAN_APPROVAL_REVIEW_DECISION_CONFIG = (
    "jarvis/data/ftaw_real_human_approval_review_decision_recorder.synthetic_complete.example.json"
)


def _decision(decision: str = "approve_for_registry_update_dry_run", asset_id: str = "ftaw_global_core_candidate") -> dict:
    return {
        "asset_id": asset_id,
        "decision": decision,
        "reviewed_by_user": True,
        "user_asserted_manual_approval_review": True,
        "user_asserted_no_registry_mutation": True,
        "user_asserted_no_allocation_recommendation": True,
        "user_asserted_no_buy_signal": True,
        "user_asserted_no_trade": True,
        "reviewer_notes": "Synthetic decision.",
    }


def _complete_recorder(decision: str = "approve_for_registry_update_dry_run"):
    return build_ftaw_real_human_approval_review_decision_recorder(_complete_real_manual_approval_review_gate(), _decision(decision))


class FTAWRealHumanApprovalReviewDecisionRecorderTests(unittest.TestCase):
    def test_default_blocks_without_v4_44_packet(self) -> None:
        pack = build_ftaw_real_human_approval_review_decision_recorder(_real_manual_approval_review_gate(), {})

        self.assertEqual(pack.recorder_status, "BLOCKED_NO_REAL_MANUAL_APPROVAL_REVIEW_PACKET")
        self.assertFalse(pack.decision_recorded)
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_defer_records_but_does_not_set_registry_dry_run_ready(self) -> None:
        pack = _complete_recorder("defer")

        self.assertEqual(pack.recorder_status, "REAL_HUMAN_APPROVAL_REVIEW_DEFERRED")
        self.assertTrue(pack.decision_recorded)
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_reject_records_but_does_not_set_registry_dry_run_ready(self) -> None:
        pack = _complete_recorder("reject")

        self.assertEqual(pack.recorder_status, "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED")
        self.assertTrue(pack.decision_recorded)
        self.assertFalse(pack.registry_update_dry_run_ready)
        self.assertTrue(any("reject" in reason for reason in pack.blocked_reasons))

    def test_needs_correction_records_and_blocks_with_reasons(self) -> None:
        pack = _complete_recorder("needs_correction")

        self.assertEqual(pack.recorder_status, "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED")
        self.assertTrue(pack.decision_recorded)
        self.assertFalse(pack.registry_update_dry_run_ready)
        self.assertTrue(any("needs correction" in reason for reason in pack.blocked_reasons))

    def test_approve_for_registry_update_dry_run_reaches_ready_status(self) -> None:
        pack = _complete_recorder()

        self.assertEqual(pack.recorder_status, "REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED_FOR_REGISTRY_DRY_RUN")
        self.assertTrue(pack.decision_recorded)
        self.assertTrue(pack.registry_update_dry_run_ready)

    def test_missing_confirmation_blocks(self) -> None:
        entry = _decision()
        entry["user_asserted_no_trade"] = False

        pack = build_ftaw_real_human_approval_review_decision_recorder(_complete_real_manual_approval_review_gate(), entry)

        self.assertEqual(pack.recorder_status, "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED")
        self.assertFalse(pack.registry_update_dry_run_ready)
        self.assertTrue(any("blocked_missing_user_confirmation" in reason for reason in pack.blocked_reasons))

    def test_wrong_asset_blocks(self) -> None:
        pack = build_ftaw_real_human_approval_review_decision_recorder(
            _complete_real_manual_approval_review_gate(),
            _decision(asset_id="wrong_asset"),
        )

        self.assertEqual(pack.recorder_status, "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED")
        self.assertFalse(pack.registry_update_dry_run_ready)
        self.assertTrue(any("blocked_asset_mismatch" in reason for reason in pack.blocked_reasons))

    def test_approval_flags_remain_false(self) -> None:
        pack = _complete_recorder()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.approval_status_change)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.allocation_recommendation)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.trade_executed)
        self.assertIsNotNone(pack.decision_record)
        self.assertFalse(pack.decision_record.approved_asset)
        self.assertFalse(pack.decision_record.approval_status_change)

    def test_no_registry_candidate_mutation_or_recommendation_order_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_recorder()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)

    def test_no_private_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_recorder()

        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)

    def test_partial_gate_blocks_even_with_decision(self) -> None:
        pack = build_ftaw_real_human_approval_review_decision_recorder(_partial_real_manual_approval_review_gate(), _decision())

        self.assertEqual(pack.recorder_status, "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED")
        self.assertFalse(pack.registry_update_dry_run_ready)
        self.assertTrue(any("approval review gate status" in reason for reason in pack.blocked_reasons))


if __name__ == "__main__":
    unittest.main()
