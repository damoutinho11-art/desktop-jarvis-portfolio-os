import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_registry_update_apply_gate import (
    build_ftaw_registry_update_apply_gate,
    build_ftaw_registry_update_apply_gate_from_files,
)
from jarvis.ftaw_registry_update_dry_run_pack import FTAWRegistryUpdateDryRunPack, FTAWRegistryUpdateDryRunPlan


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
):
    return build_ftaw_registry_update_apply_gate_from_files(
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
    )


def _ready_dry_run() -> FTAWRegistryUpdateDryRunPack:
    plan = FTAWRegistryUpdateDryRunPlan(
        asset_id="ftaw_global_core_candidate",
        current_approval_status="candidate_unreviewed",
        proposed_approval_status="approved_by_human_review_dry_run",
        proposed_registry_fields={"approval_status": "approved_by_human_review_dry_run"},
        evidence_coverage_summary="5 of 5 required evidence types have dry-run planned promotions.",
        promotion_dry_run_references=("ftaw_global_core_candidate:fund_metadata:dry_run",),
        human_approval_review_decision_reference="ftaw_global_core_candidate:manual_approval_review",
    )
    return FTAWRegistryUpdateDryRunPack(
        registry_update_dry_run_status="DRY_RUN_PLANNED",
        target_asset="ftaw_global_core_candidate",
        human_decision_status="decision_recorded_for_registry_update_dry_run",
        registry_update_dry_run_ready=True,
        dry_run_plan_created=True,
        current_approval_status="candidate_unreviewed",
        proposed_approval_status="approved_by_human_review_dry_run",
        registry_update_mode="dry_run",
        registry_mutation=False,
        approved_asset=False,
        buy_signal=False,
        blocked_reasons=(),
        dry_run_plan=plan,
    )


class FTAWRegistryUpdateApplyGateTests(unittest.TestCase):
    def test_default_fixture_blocks(self) -> None:
        gate = _gate()

        self.assertEqual(gate.apply_gate_status, "BLOCKED")

    def test_partial_synthetic_fixture_blocks(self) -> None:
        gate = _gate(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
            GATE_CONFIG,
            HUMAN_DECISION_CONFIG,
            REGISTRY_DRY_RUN_CONFIG,
            APPLY_GATE_CONFIG,
        )

        self.assertEqual(gate.apply_gate_status, "BLOCKED")

    def test_synthetic_complete_reaches_ready_for_explicit_manual_registry_apply(self) -> None:
        gate = _gate(
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

        self.assertEqual(gate.apply_gate_status, "READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY")

    def test_ready_gate_flags_are_manual_only_and_no_apply_executed(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(_ready_dry_run())

        self.assertTrue(gate.explicit_manual_apply_required)
        self.assertFalse(gate.apply_executed)
        self.assertFalse(gate.registry_file_written)
        self.assertFalse(gate.approved_asset)

    def test_ready_gate_does_not_change_approval_status_or_mutate_files(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        gate = build_ftaw_registry_update_apply_gate(_ready_dry_run())

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(gate.current_approval_status, "candidate_unreviewed")
        self.assertFalse(gate.registry_mutation_performed)

    def test_ready_gate_does_not_create_approved_universe_file(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(_ready_dry_run())

        self.assertFalse(Path("jarvis/data/approved_universe.v4_23.json").exists())
        self.assertFalse(gate.allocation_recommendation_created)
        self.assertFalse(gate.buy_sell_requests_created)
        self.assertFalse(gate.trades_executed)

    def test_non_dry_run_mode_blocks(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), registry_update_mode="apply"))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("registry_update_mode must be dry_run.", gate.blocked_reasons)

    def test_registry_mutation_true_blocks(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), registry_mutation=True))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("registry_mutation must remain false.", gate.blocked_reasons)

    def test_approved_asset_true_blocks(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), approved_asset=True))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("approved_asset must remain false.", gate.blocked_reasons)

    def test_buy_signal_true_blocks(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), buy_signal=True))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("buy_signal must remain false.", gate.blocked_reasons)

    def test_missing_proposed_approval_status_blocks(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), proposed_approval_status=None))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("proposed approval_status is missing.", gate.blocked_reasons)

    def test_asset_mismatch_blocks(self) -> None:
        plan = replace(_ready_dry_run().dry_run_plan, asset_id="wrong_asset")
        gate = build_ftaw_registry_update_apply_gate(replace(_ready_dry_run(), dry_run_plan=plan))

        self.assertEqual(gate.apply_gate_status, "BLOCKED")
        self.assertIn("dry-run plan asset_id does not match target asset.", gate.blocked_reasons)

    def test_no_verified_promotion_registry_mutation_recommendation_order_or_trade(self) -> None:
        gate = build_ftaw_registry_update_apply_gate(_ready_dry_run())

        self.assertTrue(gate.no_verified_evidence_promotion)
        self.assertFalse(gate.registry_mutation_performed)
        self.assertFalse(gate.allocation_recommendation_created)
        self.assertFalse(gate.buy_sell_requests_created)
        self.assertFalse(gate.trades_executed)


if __name__ == "__main__":
    unittest.main()
