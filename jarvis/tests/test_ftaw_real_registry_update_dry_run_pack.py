import unittest
from pathlib import Path

from jarvis.ftaw_real_registry_update_dry_run_pack import (
    PROPOSED_REAL_APPROVAL_STATUS,
    build_ftaw_real_registry_update_dry_run_pack,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import SOURCE_REGISTRY
from jarvis.tests.test_ftaw_real_human_approval_review_decision_recorder import (
    _complete_recorder,
)
from jarvis.tests.test_ftaw_real_manual_approval_review_gate import _complete_real_manual_approval_review_gate
from jarvis.ftaw_real_human_approval_review_decision_recorder import (
    build_ftaw_real_human_approval_review_decision_recorder,
)


REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG = "jarvis/data/ftaw_real_registry_update_dry_run_pack.example.json"
PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG = "jarvis/data/ftaw_real_registry_update_dry_run_pack.synthetic_partial.example.json"
COMPLETE_REAL_REGISTRY_UPDATE_DRY_RUN_CONFIG = "jarvis/data/ftaw_real_registry_update_dry_run_pack.synthetic_complete.example.json"


def _default_pack():
    decision_pack = build_ftaw_real_human_approval_review_decision_recorder(_complete_real_manual_approval_review_gate(), {})
    return build_ftaw_real_registry_update_dry_run_pack(decision_pack, SOURCE_REGISTRY)


def _partial_pack():
    return build_ftaw_real_registry_update_dry_run_pack(_complete_recorder("needs_correction"), SOURCE_REGISTRY)


def _complete_pack():
    return build_ftaw_real_registry_update_dry_run_pack(_complete_recorder(), SOURCE_REGISTRY)


class FTAWRealRegistryUpdateDryRunPackTests(unittest.TestCase):
    def test_default_blocks_without_v4_45_decision(self) -> None:
        pack = _default_pack()

        self.assertEqual(pack.dry_run_status, "BLOCKED_NO_REAL_HUMAN_APPROVAL_DECISION")
        self.assertFalse(pack.dry_run_plan_created)
        self.assertIsNone(pack.dry_run_plan)
        self.assertTrue(pack.blocked_reasons)

    def test_partial_creates_blocked_partial_dry_run_plan(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.dry_run_status, "PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_READY")
        self.assertTrue(pack.dry_run_plan_created)
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_final_audit_ready(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.dry_run_status, "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT")
        self.assertTrue(pack.dry_run_plan_created)

    def test_complete_requires_v4_45_registry_dry_run_ready_true(self) -> None:
        pack = _default_pack()

        self.assertFalse(pack.upstream_v4_45_status == "REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED_FOR_REGISTRY_DRY_RUN")
        self.assertTrue(any("not registry-dry-run ready" in reason for reason in pack.blocked_reasons))

    def test_defer_reject_needs_correction_do_not_unlock_dry_run(self) -> None:
        for decision in ("defer", "reject", "needs_correction"):
            with self.subTest(decision=decision):
                pack = build_ftaw_real_registry_update_dry_run_pack(_complete_recorder(decision), SOURCE_REGISTRY)
                self.assertNotEqual(pack.dry_run_status, "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT")

    def test_proposed_status_is_dry_run_only(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.proposed_dry_run_status, PROPOSED_REAL_APPROVAL_STATUS)
        self.assertIn("dry_run", pack.proposed_dry_run_status)

    def test_current_status_remains_unchanged(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertEqual(pack.current_status, "candidate_unreviewed")
        self.assertTrue(pack.current_status_unchanged)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_dry_run_plan_safety_flags(self) -> None:
        pack = _complete_pack()
        plan = pack.dry_run_plan

        self.assertIsNotNone(plan)
        self.assertTrue(plan.dry_run)
        self.assertFalse(plan.registry_mutation)
        self.assertFalse(plan.registry_file_written)
        self.assertTrue(plan.current_status_unchanged)
        self.assertFalse(plan.approved_asset)
        self.assertFalse(plan.allocation_recommendation)
        self.assertFalse(plan.buy_signal)
        self.assertFalse(plan.trade_executed)

    def test_no_registry_candidate_mutation_or_approval_recommendation_order_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.registry_file_written)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)

    def test_no_private_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)


if __name__ == "__main__":
    unittest.main()
