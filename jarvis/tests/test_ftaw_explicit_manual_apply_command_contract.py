import unittest
from pathlib import Path

from jarvis.ftaw_explicit_manual_apply_command_contract import (
    COMMAND_TYPE,
    REQUIRED_CONFIRMATION_PHRASE,
    REQUIRED_SAFETY_CONFIRMATIONS,
    FTAWExplicitManualApplyCommand,
    FTAWExplicitManualApplyCommandConfig,
    build_expected_dry_run_plan_fingerprint,
    build_expected_dry_run_plan_reference,
    build_ftaw_explicit_manual_apply_command_contract,
    build_ftaw_explicit_manual_apply_command_contract_from_files,
)
from jarvis.ftaw_registry_update_apply_gate import (
    FTAWRegistryUpdateApplyGatePack,
    build_ftaw_registry_update_apply_gate_from_files,
)


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
):
    return build_ftaw_explicit_manual_apply_command_contract_from_files(
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
    )


def _ready_gate() -> FTAWRegistryUpdateApplyGatePack:
    return build_ftaw_registry_update_apply_gate_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        COMPLETE_QUEUE_CONFIG,
        COMPLETE_DECISION_CONFIG,
        COMPLETE_PREVIEW_CONFIG,
        COMPLETE_DRY_RUN_CONFIG,
        COMPLETE_READINESS_CONFIG,
        COMPLETE_GATE_CONFIG,
        COMPLETE_HUMAN_DECISION_CONFIG,
        COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        COMPLETE_APPLY_GATE_CONFIG,
    )


def _command(**overrides):
    gate = _ready_gate()
    values = {
        "command_id": "test-command-001",
        "asset_id": gate.target_asset,
        "dry_run_plan_reference": build_expected_dry_run_plan_reference(gate),
        "proposed_approval_status": gate.proposed_approval_status,
        "current_approval_status": gate.current_approval_status,
        "command_type": COMMAND_TYPE,
        "human_confirmation_text": REQUIRED_CONFIRMATION_PHRASE,
        "human_operator": "test_operator",
        "command_timestamp": "2026-06-10T00:00:00Z",
        "dry_run_plan_fingerprint": build_expected_dry_run_plan_fingerprint(gate),
        "safety_confirmations": {item: True for item in REQUIRED_SAFETY_CONFIRMATIONS},
    }
    values.update(overrides)
    return FTAWExplicitManualApplyCommandConfig(command=FTAWExplicitManualApplyCommand(**values))


class FTAWExplicitManualApplyCommandContractTests(unittest.TestCase):
    def test_default_fixture_blocks_command_validation(self) -> None:
        pack = _contract()

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertEqual(pack.apply_gate_status, "BLOCKED")

    def test_partial_synthetic_fixture_blocks_command_validation(self) -> None:
        pack = _contract(
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
        )

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertEqual(pack.apply_gate_status, "BLOCKED")

    def test_synthetic_complete_fixture_validates_matching_command(self) -> None:
        pack = _contract(
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
        )

        self.assertEqual(pack.contract_validation_status, "READY_FOR_MANUAL_REGISTRY_APPLY_EXECUTION_REVIEW")

    def test_valid_command_remains_non_executing_and_non_approval(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(), "inline")

        self.assertFalse(pack.apply_executed)
        self.assertFalse(pack.registry_file_written)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.approvals_created)

    def test_missing_command_is_pending(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(
            _ready_gate(),
            FTAWExplicitManualApplyCommandConfig(command=None),
            "inline",
        )

        self.assertEqual(pack.contract_validation_status, "PENDING_EXPLICIT_MANUAL_APPLY_COMMAND")

    def test_wrong_command_type_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(command_type="wrong"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("command_type is invalid.", pack.blocked_reasons)

    def test_wrong_confirmation_phrase_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(human_confirmation_text="approve"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("explicit confirmation phrase does not match.", pack.blocked_reasons)

    def test_missing_safety_confirmation_blocks(self) -> None:
        confirmations = {item: True for item in REQUIRED_SAFETY_CONFIRMATIONS}
        confirmations[REQUIRED_SAFETY_CONFIRMATIONS[0]] = False
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(safety_confirmations=confirmations), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("required safety confirmations are incomplete.", pack.blocked_reasons)

    def test_asset_mismatch_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(asset_id="wrong_asset"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("command asset_id does not match apply gate target asset.", pack.blocked_reasons)

    def test_current_status_mismatch_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(current_approval_status="candidate_reviewed"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("command current_approval_status does not match apply gate.", pack.blocked_reasons)

    def test_proposed_status_mismatch_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(proposed_approval_status="approved_investable"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("command proposed_approval_status does not match apply gate.", pack.blocked_reasons)

    def test_dry_run_fingerprint_mismatch_blocks(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(dry_run_plan_fingerprint="wrong"), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("dry-run plan reference or fingerprint does not match.", pack.blocked_reasons)

    def test_missing_replay_protection_fields_block(self) -> None:
        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(command_id="", command_timestamp=""), "inline")

        self.assertEqual(pack.contract_validation_status, "BLOCKED")
        self.assertIn("command replay-protection fields are incomplete.", pack.blocked_reasons)

    def test_no_files_or_outputs_are_mutated_or_created(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_explicit_manual_apply_command_contract(_ready_gate(), _command(), "inline")

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(Path("jarvis/data/approved_universe.v4_24.json").exists())
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
