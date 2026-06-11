import unittest
from pathlib import Path

from jarvis.ftaw_identity_guard_submission_dry_run_pack import (
    build_ftaw_identity_guard_submission_dry_run_pack,
    build_ftaw_identity_guard_submission_dry_run_pack_from_files,
)
from jarvis.tests.test_ftaw_manual_public_source_reference_entry_recorder import (
    COMPLETE_RECORDER_CONFIG,
    PARTIAL_RECORDER_CONFIG,
    RECORDER_CONFIG,
)
from jarvis.tests.test_ftaw_manual_source_fact_entry_pack import (
    COMPLETE_FACT_CONFIG,
    FACT_CONFIG,
    PARTIAL_FACT_CONFIG,
)
from jarvis.tests.test_ftaw_real_evidence_collection_checklist_pack import (
    CHECKLIST_CONFIG,
    COMPLETE_CHECKLIST_CONFIG,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import (
    APPLY_GATE_CONFIG,
    AUDIT_CONFIG,
    COMMAND_CONFIG,
    COMPLETE_APPLY_GATE_CONFIG,
    COMPLETE_AUDIT_CONFIG,
    COMPLETE_COMMAND_CONFIG,
    COMPLETE_DECISION_CONFIG,
    COMPLETE_DRY_RUN_CONFIG,
    COMPLETE_EXECUTION_REVIEW_CONFIG,
    COMPLETE_GATE_CONFIG,
    COMPLETE_HUMAN_DECISION_CONFIG,
    COMPLETE_PREVIEW_CONFIG,
    COMPLETE_QUEUE_CONFIG,
    COMPLETE_READINESS_CONFIG,
    COMPLETE_REAL_INTAKE_CONFIG,
    COMPLETE_REGISTRY_DRY_RUN_CONFIG,
    DECISION_CONFIG,
    DRY_RUN_CONFIG,
    EXECUTION_REVIEW_CONFIG,
    GATE_CONFIG,
    GUARD_CONFIG,
    HUMAN_DECISION_CONFIG,
    INTAKE_CONFIG,
    PARTIAL_DECISION_CONFIG,
    PARTIAL_DRY_RUN_CONFIG,
    PARTIAL_PREVIEW_CONFIG,
    PARTIAL_QUEUE_CONFIG,
    PARTIAL_READINESS_CONFIG,
    PREVIEW_CONFIG,
    QUEUE_CONFIG,
    READINESS_CONFIG,
    REAL_INTAKE_CONFIG,
    REGISTRY_DRY_RUN_CONFIG,
    SOURCE_REGISTRY,
    URL_FETCH_CONFIG,
)
from jarvis.tests.test_ftaw_real_manual_identity_guard_review_decision_recorder import (
    COMPLETE_REVIEW_DECISION_CONFIG,
    PARTIAL_REVIEW_DECISION_CONFIG,
    REVIEW_DECISION_CONFIG,
)
from jarvis.tests.test_ftaw_real_manual_source_fact_identity_guard_bridge import (
    BRIDGE_CONFIG,
    COMPLETE_BRIDGE_CONFIG,
    PARTIAL_BRIDGE_CONFIG,
)
from jarvis.tests.test_ftaw_real_public_source_reference_intake_plan import (
    COMPLETE_PLAN_CONFIG,
    PLAN_CONFIG,
)


SUBMISSION_DRY_RUN_CONFIG = "jarvis/data/ftaw_identity_guard_submission_dry_run_pack.example.json"
PARTIAL_SUBMISSION_DRY_RUN_CONFIG = "jarvis/data/ftaw_identity_guard_submission_dry_run_pack.synthetic_partial.example.json"
COMPLETE_SUBMISSION_DRY_RUN_CONFIG = "jarvis/data/ftaw_identity_guard_submission_dry_run_pack.synthetic_complete.example.json"


def _pack(
    queue_config=QUEUE_CONFIG,
    decision_config=DECISION_CONFIG,
    preview_config=PREVIEW_CONFIG,
    dry_run_config=DRY_RUN_CONFIG,
    readiness_config=READINESS_CONFIG,
    approval_gate_config=GATE_CONFIG,
    human_decision_config=HUMAN_DECISION_CONFIG,
    registry_dry_run_config=REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=APPLY_GATE_CONFIG,
    command_config=COMMAND_CONFIG,
    execution_review_config=EXECUTION_REVIEW_CONFIG,
    audit_config=AUDIT_CONFIG,
    real_intake_config=REAL_INTAKE_CONFIG,
    checklist_config=CHECKLIST_CONFIG,
    plan_config=PLAN_CONFIG,
    recorder_config=RECORDER_CONFIG,
    fact_config=FACT_CONFIG,
    bridge_config=BRIDGE_CONFIG,
    review_decision_config=REVIEW_DECISION_CONFIG,
    submission_dry_run_config=SUBMISSION_DRY_RUN_CONFIG,
):
    return build_ftaw_identity_guard_submission_dry_run_pack_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        queue_config,
        decision_config,
        preview_config,
        dry_run_config,
        readiness_config,
        approval_gate_config,
        human_decision_config,
        registry_dry_run_config,
        apply_gate_config,
        command_config,
        execution_review_config,
        audit_config,
        real_intake_config,
        checklist_config,
        plan_config,
        recorder_config,
        fact_config,
        bridge_config,
        review_decision_config,
        submission_dry_run_config,
    )


def _partial_pack():
    return _pack(
        PARTIAL_QUEUE_CONFIG,
        PARTIAL_DECISION_CONFIG,
        PARTIAL_PREVIEW_CONFIG,
        PARTIAL_DRY_RUN_CONFIG,
        PARTIAL_READINESS_CONFIG,
        recorder_config=PARTIAL_RECORDER_CONFIG,
        fact_config=PARTIAL_FACT_CONFIG,
        bridge_config=PARTIAL_BRIDGE_CONFIG,
        review_decision_config=PARTIAL_REVIEW_DECISION_CONFIG,
        submission_dry_run_config=PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
    )


def _complete_pack():
    return _pack(
        COMPLETE_QUEUE_CONFIG,
        COMPLETE_DECISION_CONFIG,
        COMPLETE_PREVIEW_CONFIG,
        COMPLETE_DRY_RUN_CONFIG,
        COMPLETE_READINESS_CONFIG,
        COMPLETE_GATE_CONFIG,
        COMPLETE_HUMAN_DECISION_CONFIG,
        COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        COMPLETE_APPLY_GATE_CONFIG,
        COMPLETE_COMMAND_CONFIG,
        COMPLETE_EXECUTION_REVIEW_CONFIG,
        COMPLETE_AUDIT_CONFIG,
        COMPLETE_REAL_INTAKE_CONFIG,
        COMPLETE_CHECKLIST_CONFIG,
        COMPLETE_PLAN_CONFIG,
        COMPLETE_RECORDER_CONFIG,
        COMPLETE_FACT_CONFIG,
        COMPLETE_BRIDGE_CONFIG,
        COMPLETE_REVIEW_DECISION_CONFIG,
        COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
    )


class FTAWIdentityGuardSubmissionDryRunPackTests(unittest.TestCase):
    def test_default_blocks_without_manual_identity_decisions(self) -> None:
        pack = _pack()

        self.assertEqual(pack.dry_run_status, "BLOCKED_NO_MANUAL_IDENTITY_GUARD_DECISIONS")

    def test_partial_records_only_valid_accepted_decisions_and_lists_blockers(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.dry_run_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY")
        self.assertEqual(pack.accepted_decision_count, 1)
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_identity_guard_submission_dry_run_ready(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.dry_run_status, "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY")

    def test_complete_includes_exactly_five_public_evidence_types(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.dry_run_packet_item_count, 5)
        self.assertEqual(
            {item.evidence_type for item in pack.packet_items},
            {"fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data"},
        )
        self.assertNotIn("platform_availability", {item.evidence_type for item in pack.packet_items})
        self.assertNotIn("tax_route", {item.evidence_type for item in pack.packet_items})

    def test_manual_private_items_remain_outstanding(self) -> None:
        pack = _complete_pack()
        outstanding = {item.evidence_type: item.reason for item in pack.manual_private_outstanding}

        self.assertIn("platform_availability", outstanding)
        self.assertIn("tax_route", outstanding)

    def test_reject_needs_correction_and_missing_decisions_are_excluded_or_blocking(self) -> None:
        partial = _partial_pack()

        self.assertEqual(partial.accepted_decision_count, 1)
        self.assertGreater(partial.missing_decision_count, 0)
        self.assertTrue(any("correction" in reason or "missing" in reason for reason in partial.blocked_reasons))

    def test_all_packet_items_have_safe_dry_run_flags(self) -> None:
        pack = _complete_pack()

        self.assertTrue(all(not item.identity_guard_executed for item in pack.packet_items))
        self.assertTrue(all(not item.identity_guard_pass_created for item in pack.packet_items))
        self.assertTrue(all(not item.queue_eligibility_created for item in pack.packet_items))
        self.assertTrue(all(not item.evidence_verified for item in pack.packet_items))
        self.assertTrue(all(not item.approved_asset for item in pack.packet_items))
        self.assertTrue(all(not item.buy_signal for item in pack.packet_items))

    def test_missing_accepted_decisions_block_readiness(self) -> None:
        from jarvis.tests.test_ftaw_real_manual_identity_guard_review_decision_recorder import _load_complete_bridge_pack_for_direct_tests
        from jarvis.tests.test_ftaw_real_manual_identity_guard_review_decision_recorder import _load_complete_fact_pack_for_direct_tests
        from jarvis.ftaw_real_manual_identity_guard_review_decision_recorder import (
            build_ftaw_real_manual_identity_guard_review_decision_recorder,
        )

        decision_pack = build_ftaw_real_manual_identity_guard_review_decision_recorder(
            _load_complete_bridge_pack_for_direct_tests(),
            _load_complete_fact_pack_for_direct_tests(),
            (),
        )

        pack = build_ftaw_identity_guard_submission_dry_run_pack(decision_pack)

        self.assertEqual(pack.dry_run_status, "BLOCKED_NO_MANUAL_IDENTITY_GUARD_DECISIONS")
        self.assertGreater(pack.missing_decision_count, 0)

    def test_pack_does_not_execute_verify_pass_queue_or_extract(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.automatic_fact_extraction)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.identity_guard_executed)
        self.assertFalse(pack.identity_guard_pass_records_created)
        self.assertFalse(pack.queue_eligibility_created)

    def test_pack_does_not_approve_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_pack_does_not_create_recommendations_orders_trades_executor_ingest_fetch_or_download(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)


if __name__ == "__main__":
    unittest.main()
