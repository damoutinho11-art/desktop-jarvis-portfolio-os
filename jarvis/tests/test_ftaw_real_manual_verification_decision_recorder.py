import unittest
from pathlib import Path

from jarvis.ftaw_real_manual_verification_decision_recorder import (
    build_ftaw_real_manual_verification_decision_recorder,
    build_ftaw_real_manual_verification_decision_recorder_from_files,
)
from jarvis.tests.test_ftaw_real_identity_guarded_verification_queue_dry_run_bridge import (
    COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
    PARTIAL_QUEUE_DRY_RUN_BRIDGE_CONFIG,
    QUEUE_DRY_RUN_BRIDGE_CONFIG,
    _complete_queue_dry_run_bridge,
)
from jarvis.tests.test_ftaw_manual_identity_guard_result_recorder import (
    COMPLETE_RESULT_RECORDER_CONFIG,
    PARTIAL_RESULT_RECORDER_CONFIG,
    RESULT_RECORDER_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_execution_review_pack import (
    COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
    EXECUTION_REVIEW_PACK_CONFIG,
    PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
)
from jarvis.tests.test_ftaw_explicit_manual_identity_guard_submission_command_contract import (
    COMMAND_CONTRACT_CONFIG,
    COMPLETE_COMMAND_CONTRACT_CONFIG,
    PARTIAL_COMMAND_CONTRACT_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_review_gate import (
    COMPLETE_REVIEW_GATE_CONFIG,
    PARTIAL_REVIEW_GATE_CONFIG,
    REVIEW_GATE_CONFIG,
)
from jarvis.tests.test_ftaw_identity_guard_submission_dry_run_pack import (
    COMPLETE_SUBMISSION_DRY_RUN_CONFIG,
    PARTIAL_SUBMISSION_DRY_RUN_CONFIG,
    SUBMISSION_DRY_RUN_CONFIG,
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


REAL_MANUAL_DECISION_CONFIG = "jarvis/data/ftaw_real_manual_verification_decision_recorder.example.json"
PARTIAL_REAL_MANUAL_DECISION_CONFIG = "jarvis/data/ftaw_real_manual_verification_decision_recorder.synthetic_partial.example.json"
COMPLETE_REAL_MANUAL_DECISION_CONFIG = "jarvis/data/ftaw_real_manual_verification_decision_recorder.synthetic_complete.example.json"


def _real_manual_decision_recorder(
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
    command_contract_config=COMMAND_CONTRACT_CONFIG,
    submission_execution_review_config=EXECUTION_REVIEW_PACK_CONFIG,
    result_recorder_config=RESULT_RECORDER_CONFIG,
    queue_dry_run_bridge_config=QUEUE_DRY_RUN_BRIDGE_CONFIG,
    real_manual_decision_config=REAL_MANUAL_DECISION_CONFIG,
):
    return build_ftaw_real_manual_verification_decision_recorder_from_files(
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
        command_contract_config,
        submission_execution_review_config,
        result_recorder_config,
        queue_dry_run_bridge_config,
        real_manual_decision_config,
    )


def _partial_real_manual_decision_recorder():
    return _real_manual_decision_recorder(
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
        command_contract_config=PARTIAL_COMMAND_CONTRACT_CONFIG,
        submission_execution_review_config=PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
        result_recorder_config=PARTIAL_RESULT_RECORDER_CONFIG,
        queue_dry_run_bridge_config=PARTIAL_QUEUE_DRY_RUN_BRIDGE_CONFIG,
        real_manual_decision_config=PARTIAL_REAL_MANUAL_DECISION_CONFIG,
    )


def _complete_real_manual_decision_recorder():
    return _real_manual_decision_recorder(
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
        COMPLETE_COMMAND_CONTRACT_CONFIG,
        COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
        COMPLETE_RESULT_RECORDER_CONFIG,
        COMPLETE_QUEUE_DRY_RUN_BRIDGE_CONFIG,
        COMPLETE_REAL_MANUAL_DECISION_CONFIG,
    )


def _accept_entry(evidence_type: str) -> dict:
    return {
        "evidence_type": evidence_type,
        "source_reference_id": f"ftaw_{evidence_type}_reference_slot",
        "manual_verification_decision": "accept_for_verified_evidence_preview",
        "reviewed_by_user": True,
        "user_asserted_manual_verification_decision_completed": True,
        "user_asserted_no_evidence_verification": True,
        "user_asserted_no_queue_eligibility": True,
        "user_asserted_no_promotion": True,
        "reviewer_notes": "Synthetic direct accept.",
    }


class FTAWRealManualVerificationDecisionRecorderTests(unittest.TestCase):
    def test_default_blocks_without_verification_queue_dry_run(self) -> None:
        pack = _real_manual_decision_recorder()

        self.assertEqual(pack.decision_recorder_status, "BLOCKED_NO_VERIFICATION_QUEUE_DRY_RUN")

    def test_partial_records_decisions_and_blocks_with_reasons(self) -> None:
        pack = _partial_real_manual_decision_recorder()

        self.assertEqual(pack.decision_recorder_status, "PARTIAL_MANUAL_VERIFICATION_DECISIONS_RECORDED")
        self.assertEqual(pack.accepted_for_preview_count, 1)
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_verified_evidence_preview_review_status(self) -> None:
        pack = _complete_real_manual_decision_recorder()

        self.assertEqual(pack.decision_recorder_status, "MANUAL_VERIFICATION_DECISIONS_RECORDED_FOR_VERIFIED_EVIDENCE_PREVIEW_REVIEW")

    def test_complete_records_five_accept_decisions(self) -> None:
        pack = _complete_real_manual_decision_recorder()

        self.assertEqual(pack.manual_decision_count, 5)
        self.assertEqual(pack.accepted_for_preview_count, 5)
        self.assertEqual(pack.missing_decision_count, 0)
        self.assertTrue(all(record.verified_evidence_preview_ready for record in pack.decision_records))

    def test_missing_decision_blocks(self) -> None:
        pack = build_ftaw_real_manual_verification_decision_recorder(
            _complete_queue_dry_run_bridge(),
            tuple(_accept_entry(evidence_type) for evidence_type in ("fund_metadata", "fee_metadata", "distribution_policy", "market_data")),
        )

        self.assertEqual(pack.decision_recorder_status, "PARTIAL_MANUAL_VERIFICATION_DECISIONS_RECORDED")
        self.assertEqual(pack.missing_decision_count, 1)

    def test_reject_blocks(self) -> None:
        entry = _accept_entry("fund_metadata")
        entry["manual_verification_decision"] = "reject"

        pack = build_ftaw_real_manual_verification_decision_recorder(_complete_queue_dry_run_bridge(), (entry,))

        self.assertEqual(pack.decision_recorder_status, "PARTIAL_MANUAL_VERIFICATION_DECISIONS_RECORDED")
        self.assertTrue(any("reject" in reason for reason in pack.blocked_reasons))

    def test_needs_correction_blocks(self) -> None:
        entry = _accept_entry("fund_metadata")
        entry["manual_verification_decision"] = "needs_correction"

        pack = build_ftaw_real_manual_verification_decision_recorder(_complete_queue_dry_run_bridge(), (entry,))

        self.assertEqual(pack.decision_recorder_status, "PARTIAL_MANUAL_VERIFICATION_DECISIONS_RECORDED")
        self.assertTrue(any("needs correction" in reason for reason in pack.blocked_reasons))

    def test_platform_and_tax_remain_excluded_outstanding(self) -> None:
        pack = _complete_real_manual_decision_recorder()

        self.assertIn("platform_availability", pack.manual_private_outstanding)
        self.assertIn("tax_route", pack.manual_private_outstanding)
        self.assertNotIn("platform_availability", {record.evidence_type for record in pack.decision_records})
        self.assertNotIn("tax_route", {record.evidence_type for record in pack.decision_records})

    def test_no_queue_eligibility_verification_or_promotion(self) -> None:
        pack = _complete_real_manual_decision_recorder()

        self.assertFalse(pack.real_queue_item_created)
        self.assertFalse(pack.queue_eligibility_created)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertTrue(all(not record.evidence_verified for record in pack.decision_records))
        self.assertTrue(all(not record.verified_evidence_promoted for record in pack.decision_records))
        self.assertTrue(all(not record.queue_eligibility_created for record in pack.decision_records))

    def test_no_approval_registry_mutation_or_buy_signal(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_real_manual_decision_recorder()

        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(all(not record.approved_asset and not record.registry_mutation and not record.buy_signal for record in pack.decision_records))

    def test_no_recommendations_orders_trades_executor_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_real_manual_decision_recorder()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)


if __name__ == "__main__":
    unittest.main()
