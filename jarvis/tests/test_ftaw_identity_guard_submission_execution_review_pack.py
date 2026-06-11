import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_explicit_manual_identity_guard_submission_command_contract import (
    build_ftaw_explicit_manual_identity_guard_submission_command_contract,
)
from jarvis.ftaw_identity_guard_submission_execution_review_pack import (
    build_ftaw_identity_guard_submission_execution_review_pack,
    build_ftaw_identity_guard_submission_execution_review_pack_from_files,
)
from jarvis.tests.test_ftaw_explicit_manual_identity_guard_submission_command_contract import (
    COMMAND_CONTRACT_CONFIG,
    COMPLETE_COMMAND_CONTRACT_CONFIG,
    PARTIAL_COMMAND_CONTRACT_CONFIG,
    _complete_command,
    _complete_contract,
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


EXECUTION_REVIEW_PACK_CONFIG = "jarvis/data/ftaw_identity_guard_submission_execution_review_pack.example.json"
PARTIAL_EXECUTION_REVIEW_PACK_CONFIG = "jarvis/data/ftaw_identity_guard_submission_execution_review_pack.synthetic_partial.example.json"
COMPLETE_EXECUTION_REVIEW_PACK_CONFIG = "jarvis/data/ftaw_identity_guard_submission_execution_review_pack.synthetic_complete.example.json"


def _execution_review_pack(
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
):
    return build_ftaw_identity_guard_submission_execution_review_pack_from_files(
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
    )


def _partial_execution_review_pack():
    return _execution_review_pack(
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
    )


def _complete_execution_review_pack():
    return _execution_review_pack(
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
    )


class FTAWIdentityGuardSubmissionExecutionReviewPackTests(unittest.TestCase):
    def test_default_blocks_without_ready_command_contract(self) -> None:
        pack = _execution_review_pack()

        self.assertEqual(pack.execution_review_status, "BLOCKED_NO_IDENTITY_GUARD_SUBMISSION_COMMAND_CONTRACT")
        self.assertFalse(pack.final_preflight_ready)

    def test_partial_blocks_with_reasons(self) -> None:
        pack = _partial_execution_review_pack()

        self.assertEqual(pack.execution_review_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY")
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_final_manual_prefight(self) -> None:
        pack = _complete_execution_review_pack()

        self.assertEqual(pack.execution_review_status, "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT")
        self.assertTrue(pack.final_preflight_ready)

    def test_complete_replays_all_upstream_ready_states(self) -> None:
        pack = _complete_execution_review_pack()

        self.assertEqual(pack.dry_run_status, "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY")
        self.assertEqual(pack.review_gate_status, "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND")
        self.assertEqual(pack.upstream_v4_36_status, "READY_FOR_MANUAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW")

    def test_complete_confirms_asset_command_confirmations_and_packet_items(self) -> None:
        pack = _complete_execution_review_pack()

        self.assertTrue(pack.asset_match)
        self.assertTrue(pack.command_type_match)
        self.assertTrue(pack.all_confirmations_true)
        self.assertEqual(pack.packet_item_count, 5)
        self.assertEqual(pack.required_packet_item_count, 5)

    def test_platform_and_tax_remain_excluded_outstanding(self) -> None:
        contract = _complete_contract()

        self.assertEqual(contract.manual_private_outstanding_count, 2)
        self.assertEqual(_complete_execution_review_pack().manual_private_outstanding_count, 2)

    def test_missing_packet_item_blocks_readiness(self) -> None:
        contract = replace(_complete_contract(), packet_item_count=4)

        pack = build_ftaw_identity_guard_submission_execution_review_pack(contract)

        self.assertEqual(pack.execution_review_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY")
        self.assertFalse(pack.final_preflight_ready)

    def test_missing_confirmation_blocks_readiness(self) -> None:
        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(
            _complete_gate(),
            {key: value for key, value in _complete_command().items() if key != "user_confirmed_no_trade"},
        )

        pack = build_ftaw_identity_guard_submission_execution_review_pack(contract)

        self.assertEqual(pack.execution_review_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY")
        self.assertFalse(pack.all_confirmations_true)

    def test_asset_mismatch_blocks_readiness(self) -> None:
        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(
            _complete_gate(),
            _complete_command(command_target_asset_id="other_asset"),
        )

        pack = build_ftaw_identity_guard_submission_execution_review_pack(contract)

        self.assertEqual(pack.execution_review_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY")
        self.assertFalse(pack.asset_match)

    def test_wrong_command_type_blocks_readiness(self) -> None:
        contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract(
            _complete_gate(),
            _complete_command(command_type="wrong"),
        )

        pack = build_ftaw_identity_guard_submission_execution_review_pack(contract)

        self.assertEqual(pack.execution_review_status, "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY")
        self.assertFalse(pack.command_type_match)

    def test_no_identity_guard_execution_pass_records_queue_or_verification(self) -> None:
        pack = _complete_execution_review_pack()

        self.assertFalse(pack.identity_guard_executed)
        self.assertFalse(pack.identity_guard_pass_records_created)
        self.assertFalse(pack.queue_eligibility_created)
        self.assertFalse(pack.evidence_verified)

    def test_no_approval_registry_mutation_or_verified_evidence_promotion(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_execution_review_pack()

        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_no_recommendations_orders_trades_executor_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_execution_review_pack()

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
