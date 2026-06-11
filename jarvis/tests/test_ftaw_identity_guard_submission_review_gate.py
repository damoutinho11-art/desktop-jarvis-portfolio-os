import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_identity_guard_submission_review_gate import (
    build_ftaw_identity_guard_submission_review_gate,
    build_ftaw_identity_guard_submission_review_gate_from_files,
)
from jarvis.ftaw_identity_guard_submission_dry_run_pack import FTAWIdentityGuardSubmissionDryRunItem
from jarvis.tests.test_ftaw_identity_guard_submission_dry_run_pack import (
    COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
    PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
    SUBMISSION_DRY_RUN_CONFIG,
    _complete_pack,
    _pack as _dry_run_pack,
    _partial_pack as _partial_dry_run_pack,
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


REVIEW_GATE_CONFIG = "jarvis/data/ftaw_identity_guard_submission_review_gate.example.json"
PARTIAL_REVIEW_GATE_CONFIG = "jarvis/data/ftaw_identity_guard_submission_review_gate.synthetic_partial.example.json"
COMPLETE_REVIEW_GATE_CONFIG = "jarvis/data/ftaw_identity_guard_submission_review_gate.synthetic_complete.example.json"


def _gate(
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
    review_gate_config=REVIEW_GATE_CONFIG,
):
    return build_ftaw_identity_guard_submission_review_gate_from_files(
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
        review_gate_config,
    )


def _partial_gate():
    return _gate(
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
        review_gate_config=PARTIAL_REVIEW_GATE_CONFIG,
    )


def _complete_gate():
    return _gate(
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
        COMPLETE_REVIEW_GATE_CONFIG,
    )


class FTAWIdentityGuardSubmissionReviewGateTests(unittest.TestCase):
    def test_default_blocks_without_dry_run_packet(self) -> None:
        gate = _gate()

        self.assertEqual(gate.gate_status, "BLOCKED_NO_IDENTITY_GUARD_DRY_RUN_PACKET")
        self.assertEqual(gate.present_packet_item_count, 0)

    def test_partial_is_not_fully_ready_and_has_blocked_reasons(self) -> None:
        gate = _partial_gate()

        self.assertEqual(gate.gate_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_REVIEW_READY")
        self.assertTrue(gate.blocked_reasons)
        self.assertGreater(gate.missing_packet_item_count, 0)

    def test_complete_reaches_ready_for_explicit_manual_submission_command(self) -> None:
        gate = _complete_gate()

        self.assertEqual(gate.gate_status, "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND")

    def test_complete_has_exactly_five_required_public_packet_items(self) -> None:
        gate = _complete_gate()

        self.assertEqual(gate.required_packet_item_count, 5)
        self.assertEqual(gate.present_packet_item_count, 5)
        self.assertEqual(gate.missing_packet_item_count, 0)
        self.assertEqual(
            {check.evidence_type for check in gate.readiness_checks},
            {"fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data"},
        )

    def test_missing_packet_items_block_readiness(self) -> None:
        dry_run = _complete_pack()
        trimmed = replace(
            dry_run,
            packet_items=dry_run.packet_items[:-1],
            dry_run_packet_item_count=len(dry_run.packet_items) - 1,
        )

        gate = build_ftaw_identity_guard_submission_review_gate(trimmed)

        self.assertEqual(gate.gate_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_REVIEW_READY")
        self.assertGreater(gate.missing_packet_item_count, 0)

    def test_manual_private_platform_and_tax_remain_outstanding(self) -> None:
        gate = _complete_gate()
        outstanding = {item.evidence_type for item in gate.manual_private_outstanding}

        self.assertIn("platform_availability", outstanding)
        self.assertIn("tax_route", outstanding)
        self.assertNotIn("platform_availability", {check.evidence_type for check in gate.readiness_checks})
        self.assertNotIn("tax_route", {check.evidence_type for check in gate.readiness_checks})

    def test_forbidden_packet_side_effect_flags_block(self) -> None:
        dry_run = _complete_pack()
        unsafe_item = replace(dry_run.packet_items[0], identity_guard_executed=True)
        unsafe = replace(dry_run, packet_items=(unsafe_item,) + dry_run.packet_items[1:])

        gate = build_ftaw_identity_guard_submission_review_gate(unsafe)

        self.assertEqual(gate.gate_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_REVIEW_READY")
        self.assertTrue(any("forbidden safety" in reason for reason in gate.blocked_reasons))

    def test_no_identity_guard_execution_pass_records_queue_eligibility_or_verification(self) -> None:
        gate = _complete_gate()

        self.assertFalse(gate.identity_guard_executed)
        self.assertFalse(gate.identity_guard_pass_records_created)
        self.assertFalse(gate.queue_eligibility_created)
        self.assertFalse(gate.evidence_verified)
        self.assertTrue(all(not check.identity_guard_executed for check in gate.readiness_checks))
        self.assertTrue(all(not check.identity_guard_pass_created for check in gate.readiness_checks))
        self.assertTrue(all(not check.queue_eligibility_created for check in gate.readiness_checks))
        self.assertTrue(all(not check.evidence_verified for check in gate.readiness_checks))

    def test_no_approval_registry_mutation_or_verified_evidence_promotion(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        gate = _complete_gate()

        self.assertFalse(gate.approvals_created)
        self.assertFalse(gate.registry_mutation)
        self.assertFalse(gate.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_no_recommendations_orders_trades_executor_ingest_fetch_downloads_or_extraction(self) -> None:
        gate = _complete_gate()

        self.assertFalse(gate.allocation_recommendation_created)
        self.assertFalse(gate.buy_sell_requests_created)
        self.assertFalse(gate.trades_executed)
        self.assertFalse(gate.executor_created)
        self.assertFalse(gate.private_file_auto_ingest)
        self.assertFalse(gate.automatic_source_fetching)
        self.assertFalse(gate.automatic_downloads)
        self.assertFalse(gate.automatic_fact_extraction)


if __name__ == "__main__":
    unittest.main()
