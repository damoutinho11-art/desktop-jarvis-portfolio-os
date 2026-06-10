import json
import unittest
from pathlib import Path

from jarvis.ftaw_human_approval_review_decision_recorder import (
    FTAWHumanApprovalReviewDecision,
    FTAWHumanApprovalReviewDecisionConfig,
    build_ftaw_human_approval_review_decision_pack,
)
from jarvis.ftaw_manual_approval_review_gate import build_ftaw_manual_approval_review_gate_from_files
from jarvis.ftaw_registry_update_dry_run_pack import (
    build_ftaw_registry_update_dry_run_pack,
    build_ftaw_registry_update_dry_run_pack_from_files,
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


def _pack(
    queue_config=QUEUE_CONFIG,
    decision_config=DECISION_CONFIG,
    preview_config=PREVIEW_CONFIG,
    dry_run_config=DRY_RUN_CONFIG,
    readiness_config=READINESS_CONFIG,
    gate_config=GATE_CONFIG,
    human_decision_config=HUMAN_DECISION_CONFIG,
    registry_dry_run_config=REGISTRY_DRY_RUN_CONFIG,
):
    return build_ftaw_registry_update_dry_run_pack_from_files(
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
        gate_config,
        human_decision_config,
        registry_dry_run_config,
    )


def _complete_gate():
    return build_ftaw_manual_approval_review_gate_from_files(
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
    )


def _decision_pack(value: str | None, asset_id: str = "ftaw_global_core_candidate"):
    config = FTAWHumanApprovalReviewDecisionConfig(
        decision=None
        if value is None
        else FTAWHumanApprovalReviewDecision(
            review_packet_id="ftaw_global_core_candidate:manual_approval_review",
            asset_id=asset_id,
            human_decision=value,
            reviewer_notes="test",
        )
    )
    return build_ftaw_human_approval_review_decision_pack(_complete_gate(), config, "inline")


def _registry_approval_status() -> str:
    raw = json.loads(Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
    for asset in raw["assets"]:
        if asset["asset_id"] == "ftaw_global_core_candidate":
            return asset["approval_status"]
    raise AssertionError("missing FTAW asset")


class FTAWRegistryUpdateDryRunPackTests(unittest.TestCase):
    def test_default_fixture_blocks_and_creates_no_dry_run_plan(self) -> None:
        pack = _pack()

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)
        self.assertIsNone(pack.dry_run_plan)

    def test_partial_synthetic_fixture_blocks_and_creates_no_dry_run_plan(self) -> None:
        pack = _pack(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
            GATE_CONFIG,
            HUMAN_DECISION_CONFIG,
            REGISTRY_DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)

    def test_synthetic_complete_creates_dry_run_registry_update_plan(self) -> None:
        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
            COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.registry_update_dry_run_status, "DRY_RUN_PLANNED")
        self.assertTrue(pack.dry_run_plan_created)
        self.assertIsNotNone(pack.dry_run_plan)

    def test_dry_run_plan_has_dry_run_mode_no_mutation_no_approval_no_buy_signal(self) -> None:
        plan = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
            COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        ).dry_run_plan

        self.assertIsNotNone(plan)
        self.assertEqual(plan.registry_update_mode, "dry_run")
        self.assertFalse(plan.registry_mutation)
        self.assertFalse(plan.approved_asset)
        self.assertFalse(plan.buy_signal)

    def test_dry_run_plan_does_not_change_approval_status_or_mutate_candidate_assets(self) -> None:
        before_text = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")
        before_status = _registry_approval_status()

        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
            COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        )

        self.assertEqual(before_text, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(before_status, _registry_approval_status())
        self.assertFalse(pack.registry_mutation_performed)

    def test_dry_run_plan_does_not_create_approved_universe_file_recommendation_order_or_trade(self) -> None:
        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
            COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        )

        self.assertFalse(Path("jarvis/data/approved_universe.v4_22.json").exists())
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)

    def test_rejected_decision_blocks(self) -> None:
        pack = build_ftaw_registry_update_dry_run_pack(_decision_pack("rejected"), SOURCE_REGISTRY)

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)

    def test_needs_more_evidence_decision_blocks(self) -> None:
        pack = build_ftaw_registry_update_dry_run_pack(_decision_pack("needs_more_evidence"), SOURCE_REGISTRY)

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)

    def test_missing_decision_blocks(self) -> None:
        pack = build_ftaw_registry_update_dry_run_pack(_decision_pack(None), SOURCE_REGISTRY)

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)

    def test_asset_mismatch_blocks(self) -> None:
        pack = build_ftaw_registry_update_dry_run_pack(_decision_pack("approved_for_registry_update_dry_run", asset_id="wrong_asset"), SOURCE_REGISTRY)

        self.assertEqual(pack.registry_update_dry_run_status, "BLOCKED")
        self.assertFalse(pack.dry_run_plan_created)


if __name__ == "__main__":
    unittest.main()
