import unittest
from pathlib import Path

from jarvis.ftaw_explicit_manual_identity_guard_submission_command_contract import (
    EXPECTED_COMMAND_TYPE,
    build_ftaw_explicit_manual_identity_guard_submission_command_contract,
    build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files,
)
from jarvis.tests.test_ftaw_identity_guard_submission_review_gate import (
    COMPLETE_REVIEW_GATE_CONFIG,
    PARTIAL_REVIEW_GATE_CONFIG,
    REVIEW_GATE_CONFIG,
    _complete_gate,
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


COMMAND_CONTRACT_CONFIG = "jarvis/data/ftaw_explicit_manual_identity_guard_submission_command_contract.example.json"
PARTIAL_COMMAND_CONTRACT_CONFIG = "jarvis/data/ftaw_explicit_manual_identity_guard_submission_command_contract.synthetic_partial.example.json"
COMPLETE_COMMAND_CONTRACT_CONFIG = "jarvis/data/ftaw_explicit_manual_identity_guard_submission_command_contract.synthetic_complete.example.json"


def _contract(
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
):
    return build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files(
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
    )


def _partial_contract():
    return _contract(
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
    )


def _complete_contract():
    return _contract(
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
    )


def _complete_command(**overrides):
    command = {
        "command_type": EXPECTED_COMMAND_TYPE,
        "command_target_asset_id": "ftaw_global_core_candidate",
        "user_confirmed_manual_identity_submission_review": True,
        "user_confirmed_no_auto_execution": True,
        "user_confirmed_no_evidence_verification": True,
        "user_confirmed_no_queue_eligibility": True,
        "user_confirmed_no_approval": True,
        "user_confirmed_no_registry_mutation": True,
        "user_confirmed_no_buy_signal": True,
        "user_confirmed_no_trade": True,
    }
    command.update(overrides)
    return command


class FTAWExplicitManualIdentityGuardSubmissionCommandContractTests(unittest.TestCase):
    def test_default_blocks_without_ready_gate_or_command(self) -> None:
        contract = _contract()

        self.assertEqual(contract.contract_status, "BLOCKED_NO_IDENTITY_GUARD_SUBMISSION_REVIEW_GATE")
        self.assertEqual(contract.command_type, None)

    def test_partial_blocks_with_missing_confirmations(self) -> None:
        contract = _partial_contract()

        self.assertEqual(contract.contract_status, "PARTIAL_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND_RECORDED")
        self.assertGreater(contract.missing_confirmation_count, 0)
        self.assertTrue(contract.blocked_reasons)

    def test_wrong_command_type_blocks(self) -> None:
        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(
            _complete_gate(),
            _complete_command(command_type="wrong"),
        )

        self.assertEqual(contract.contract_status, "PARTIAL_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND_RECORDED")
        self.assertTrue(any("command_type" in reason for reason in contract.blocked_reasons))

    def test_asset_mismatch_blocks(self) -> None:
        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(
            _complete_gate(),
            _complete_command(command_target_asset_id="other_asset"),
        )

        self.assertEqual(contract.contract_status, "PARTIAL_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND_RECORDED")
        self.assertFalse(contract.command_target_match)

    def test_missing_confirmation_blocks(self) -> None:
        command = _complete_command()
        command.pop("user_confirmed_no_trade")

        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(_complete_gate(), command)

        self.assertEqual(contract.contract_status, "PARTIAL_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND_RECORDED")
        self.assertEqual(contract.missing_confirmation_count, 1)

    def test_complete_reaches_ready_for_manual_identity_guard_submission_execution_review(self) -> None:
        contract = _complete_contract()

        self.assertEqual(contract.contract_status, "READY_FOR_MANUAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW")
        self.assertEqual(contract.missing_confirmation_count, 0)

    def test_complete_has_five_public_packet_items(self) -> None:
        contract = _complete_contract()

        self.assertEqual(contract.packet_item_count, 5)

    def test_platform_and_tax_remain_excluded_outstanding(self) -> None:
        gate = _complete_gate()

        self.assertIn("platform_availability", {item.evidence_type for item in gate.manual_private_outstanding})
        self.assertIn("tax_route", {item.evidence_type for item in gate.manual_private_outstanding})

    def test_no_identity_guard_execution_pass_records_queue_or_verification(self) -> None:
        contract = _complete_contract()

        self.assertFalse(contract.identity_guard_executed)
        self.assertFalse(contract.identity_guard_pass_records_created)
        self.assertFalse(contract.queue_eligibility_created)
        self.assertFalse(contract.evidence_verified)

    def test_no_approval_registry_mutation_or_verified_evidence_promotion(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        contract = _complete_contract()

        self.assertFalse(contract.approvals_created)
        self.assertFalse(contract.registry_mutation)
        self.assertFalse(contract.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_no_recommendations_orders_trades_executor_ingest_fetch_download_or_extraction(self) -> None:
        contract = _complete_contract()

        self.assertFalse(contract.allocation_recommendation_created)
        self.assertFalse(contract.buy_sell_requests_created)
        self.assertFalse(contract.trades_executed)
        self.assertFalse(contract.executor_created)
        self.assertFalse(contract.private_file_auto_ingest)
        self.assertFalse(contract.automatic_source_fetching)
        self.assertFalse(contract.automatic_downloads)
        self.assertFalse(contract.automatic_fact_extraction)


if __name__ == "__main__":
    unittest.main()
