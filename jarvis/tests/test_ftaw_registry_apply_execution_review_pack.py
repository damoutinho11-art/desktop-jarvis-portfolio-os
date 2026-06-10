import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_explicit_manual_apply_command_contract import FTAWExplicitManualApplyCommandContractPack, COMMAND_TYPE
from jarvis.ftaw_registry_apply_execution_review_pack import (
    build_ftaw_registry_apply_execution_review_pack,
    build_ftaw_registry_apply_execution_review_pack_from_files,
)
from jarvis.ftaw_registry_update_apply_gate import FTAWRegistryUpdateApplyGatePack


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
PARTIAL_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
COMPLETE_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_complete.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
PARTIAL_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
COMPLETE_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_complete.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
PARTIAL_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
COMPLETE_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
PARTIAL_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
COMPLETE_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json"
READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.example.json"
PARTIAL_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_pass.example.json"
COMPLETE_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_complete.example.json"
GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.example.json"
COMPLETE_GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.synthetic_complete.example.json"
HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.example.json"
COMPLETE_HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.synthetic_complete.example.json"
REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.example.json"
COMPLETE_REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.synthetic_complete.example.json"
APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.example.json"
COMPLETE_APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.synthetic_complete.example.json"
COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json"
COMPLETE_COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.synthetic_complete.example.json"
EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.example.json"
COMPLETE_EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.synthetic_complete.example.json"


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
):
    return build_ftaw_registry_apply_execution_review_pack_from_files(
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
    )


def _ready_contract() -> FTAWExplicitManualApplyCommandContractPack:
    return FTAWExplicitManualApplyCommandContractPack(
        contract_validation_status="READY_FOR_MANUAL_REGISTRY_APPLY_EXECUTION_REVIEW",
        target_asset="ftaw_global_core_candidate",
        apply_gate_status="READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY",
        command_file_used="inline",
        command_type=COMMAND_TYPE,
        asset_id_match=True,
        current_status_match=True,
        proposed_status_match=True,
        dry_run_fingerprint_match=True,
        safety_confirmations_complete=True,
        explicit_confirmation_phrase_match=True,
        replay_protection_fields_present=True,
        apply_executed=False,
        registry_file_written=False,
        approved_asset=False,
        buy_signal=False,
        blocked_reasons=(),
    )


def _ready_gate() -> FTAWRegistryUpdateApplyGatePack:
    return FTAWRegistryUpdateApplyGatePack(
        apply_gate_status="READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY",
        target_asset="ftaw_global_core_candidate",
        dry_run_status="DRY_RUN_PLANNED",
        current_approval_status="candidate_unreviewed",
        proposed_approval_status="approved_by_human_review_dry_run",
        registry_update_mode="dry_run",
        registry_mutation=False,
        approved_asset=False,
        buy_signal=False,
        explicit_manual_apply_required=True,
        apply_executed=False,
        registry_file_written=False,
        blocked_reasons=(),
        next_manual_action="inline",
    )


class FTAWRegistryApplyExecutionReviewPackTests(unittest.TestCase):
    def test_default_fixture_blocks_execution_review(self) -> None:
        self.assertEqual(_pack().execution_review_status, "BLOCKED")

    def test_partial_synthetic_fixture_blocks_execution_review(self) -> None:
        pack = _pack(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
            GATE_CONFIG,
            HUMAN_DECISION_CONFIG,
            REGISTRY_DRY_RUN_CONFIG,
            APPLY_GATE_CONFIG,
            COMMAND_CONFIG,
            EXECUTION_REVIEW_CONFIG,
        )

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_synthetic_complete_reaches_final_manual_registry_apply_preflight(self) -> None:
        pack = _pack(
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
        )

        self.assertEqual(pack.execution_review_status, "READY_FOR_FINAL_MANUAL_REGISTRY_APPLY_PREFLIGHT")

    def test_ready_preflight_has_all_execution_and_approval_flags_false(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), _ready_gate())

        self.assertFalse(pack.apply_executed)
        self.assertFalse(pack.registry_file_written)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.buy_signal)

    def test_contract_status_below_ready_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), contract_validation_status="BLOCKED"), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_apply_gate_status_below_ready_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), apply_gate_status="BLOCKED"))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_dry_run_status_below_planned_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), dry_run_status="BLOCKED"))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_wrong_command_type_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), command_type="wrong"), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_missing_or_wrong_confirmation_phrase_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), explicit_confirmation_phrase_match=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_missing_safety_confirmation_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), safety_confirmations_complete=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_missing_replay_protection_fields_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), replay_protection_fields_present=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_asset_mismatch_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), target_asset="wrong_asset"), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_current_status_mismatch_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), current_status_match=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_proposed_status_mismatch_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), proposed_status_match=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_dry_run_fingerprint_mismatch_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(replace(_ready_contract(), dry_run_fingerprint_match=False), _ready_gate())

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_non_dry_run_mode_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), registry_update_mode="apply"))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_registry_mutation_true_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), registry_mutation=True))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_approved_asset_true_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), approved_asset=True))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_buy_signal_true_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), buy_signal=True))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_apply_executed_true_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), apply_executed=True))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_registry_file_written_true_blocks(self) -> None:
        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), replace(_ready_gate(), registry_file_written=True))

        self.assertEqual(pack.execution_review_status, "BLOCKED")

    def test_no_registry_outputs_or_side_effects(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_registry_apply_execution_review_pack(_ready_contract(), _ready_gate())

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(Path("jarvis/data/approved_universe.v4_25.json").exists())
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
