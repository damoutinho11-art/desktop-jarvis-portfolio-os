import unittest
from pathlib import Path

from jarvis.ftaw_manual_identity_guard_result_recorder import build_ftaw_manual_identity_guard_result_recorder
from jarvis.ftaw_manual_identity_guard_result_recorder import build_ftaw_manual_identity_guard_result_recorder_from_files
from jarvis.tests.test_ftaw_identity_guard_submission_execution_review_pack import (
    COMPLETE_EXECUTION_REVIEW_PACK_CONFIG,
    EXECUTION_REVIEW_PACK_CONFIG,
    PARTIAL_EXECUTION_REVIEW_PACK_CONFIG,
    _complete_execution_review_pack,
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


RESULT_RECORDER_CONFIG = "jarvis/data/ftaw_manual_identity_guard_result_recorder.example.json"
PARTIAL_RESULT_RECORDER_CONFIG = "jarvis/data/ftaw_manual_identity_guard_result_recorder.synthetic_partial.example.json"
COMPLETE_RESULT_RECORDER_CONFIG = "jarvis/data/ftaw_manual_identity_guard_result_recorder.synthetic_complete.example.json"


def _result_recorder(
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
):
    return build_ftaw_manual_identity_guard_result_recorder_from_files(
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
    )


def _partial_result_recorder():
    return _result_recorder(
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
    )


def _complete_result_recorder():
    return _result_recorder(
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
    )


def _pass_entry(evidence_type: str) -> dict:
    return {
        "evidence_type": evidence_type,
        "source_reference_id": f"ftaw_{evidence_type}_reference_slot",
        "manual_identity_guard_result": "pass",
        "reviewed_by_user": True,
        "user_asserted_manual_identity_review_completed": True,
        "user_asserted_no_auto_execution": True,
        "user_asserted_no_evidence_verification": True,
        "user_asserted_no_queue_eligibility": True,
        "reviewer_notes": "Synthetic direct test pass.",
    }


class FTAWManualIdentityGuardResultRecorderTests(unittest.TestCase):
    def test_default_blocks_without_final_preflight(self) -> None:
        pack = _result_recorder()

        self.assertEqual(pack.result_recorder_status, "BLOCKED_NO_FINAL_MANUAL_IDENTITY_GUARD_PREFLIGHT")

    def test_partial_records_valid_results_and_lists_blocked_reasons(self) -> None:
        pack = _partial_result_recorder()

        self.assertEqual(pack.result_recorder_status, "PARTIAL_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED")
        self.assertEqual(pack.manual_result_count, 3)
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_queue_dry_run_review_status(self) -> None:
        pack = _complete_result_recorder()

        self.assertEqual(pack.result_recorder_status, "MANUAL_IDENTITY_GUARD_RESULTS_RECORDED_FOR_QUEUE_DRY_RUN_REVIEW")

    def test_complete_records_exactly_five_public_results(self) -> None:
        pack = _complete_result_recorder()

        self.assertEqual(pack.manual_result_count, 5)
        self.assertEqual(pack.pass_count, 5)
        self.assertEqual({record.evidence_type for record in pack.result_records}, {"fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data"})

    def test_missing_result_blocks(self) -> None:
        pack = build_ftaw_manual_identity_guard_result_recorder(
            _complete_execution_review_pack(),
            tuple(_pass_entry(evidence_type) for evidence_type in ("fund_metadata", "fee_metadata", "distribution_policy", "market_data")),
        )

        self.assertEqual(pack.result_recorder_status, "PARTIAL_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED")
        self.assertEqual(pack.missing_result_count, 1)

    def test_fail_blocks(self) -> None:
        entry = _pass_entry("fund_metadata")
        entry["manual_identity_guard_result"] = "fail"

        pack = build_ftaw_manual_identity_guard_result_recorder(_complete_execution_review_pack(), (entry,))

        self.assertEqual(pack.result_recorder_status, "PARTIAL_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED")
        self.assertTrue(any("fail" in reason for reason in pack.blocked_reasons))

    def test_needs_correction_blocks(self) -> None:
        entry = _pass_entry("fund_metadata")
        entry["manual_identity_guard_result"] = "needs_correction"

        pack = build_ftaw_manual_identity_guard_result_recorder(_complete_execution_review_pack(), (entry,))

        self.assertEqual(pack.result_recorder_status, "PARTIAL_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED")
        self.assertTrue(any("needs correction" in reason for reason in pack.blocked_reasons))

    def test_platform_and_tax_remain_excluded_outstanding(self) -> None:
        pack = _complete_result_recorder()

        self.assertIn("platform_availability", pack.manual_private_outstanding)
        self.assertIn("tax_route", pack.manual_private_outstanding)
        self.assertNotIn("platform_availability", {record.evidence_type for record in pack.result_records})
        self.assertNotIn("tax_route", {record.evidence_type for record in pack.result_records})

    def test_no_system_identity_execution_verification_or_queue_eligibility(self) -> None:
        pack = _complete_result_recorder()

        self.assertFalse(pack.system_identity_guard_execution)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.queue_eligibility_created)
        self.assertTrue(all(not record.identity_guard_executed_by_system for record in pack.result_records))
        self.assertTrue(all(not record.evidence_verified for record in pack.result_records))
        self.assertTrue(all(not record.queue_eligibility_created for record in pack.result_records))

    def test_no_approval_registry_mutation_or_verified_evidence_promotion(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_result_recorder()

        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_no_recommendations_orders_trades_executor_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_result_recorder()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)
        self.assertTrue(all(not record.approved_asset and not record.registry_mutation and not record.buy_signal for record in pack.result_records))


if __name__ == "__main__":
    unittest.main()
