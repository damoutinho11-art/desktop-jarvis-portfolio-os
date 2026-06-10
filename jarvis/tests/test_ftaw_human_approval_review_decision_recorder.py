import unittest
from pathlib import Path

from jarvis.ftaw_human_approval_review_decision_recorder import (
    FTAWHumanApprovalReviewDecision,
    FTAWHumanApprovalReviewDecisionConfig,
    build_ftaw_human_approval_review_decision_pack,
    build_ftaw_human_approval_review_decision_pack_from_files,
    load_ftaw_human_approval_review_decision_config,
)
from jarvis.ftaw_manual_approval_review_gate import (
    FTAWManualApprovalReviewGatePack,
    build_ftaw_manual_approval_review_gate_from_files,
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


def _pack(
    queue_config=QUEUE_CONFIG,
    decision_config=DECISION_CONFIG,
    preview_config=PREVIEW_CONFIG,
    dry_run_config=DRY_RUN_CONFIG,
    readiness_config=READINESS_CONFIG,
    gate_config=GATE_CONFIG,
    human_decision_config=HUMAN_DECISION_CONFIG,
):
    return build_ftaw_human_approval_review_decision_pack_from_files(
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


def _decision(value: str, asset_id: str = "ftaw_global_core_candidate", review_packet_id: str = "ftaw_global_core_candidate:manual_approval_review"):
    return FTAWHumanApprovalReviewDecisionConfig(
        decision=FTAWHumanApprovalReviewDecision(
            review_packet_id=review_packet_id,
            asset_id=asset_id,
            human_decision=value,
            reviewer_notes="test decision",
        )
    )


class FTAWHumanApprovalReviewDecisionRecorderTests(unittest.TestCase):
    def test_default_fixture_blocks_attempted_approval_review_decision(self) -> None:
        pack = _pack()

        self.assertEqual(pack.decision_status, "blocked_gate_not_ready")
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_partial_synthetic_fixture_blocks_attempted_approval_review_decision(self) -> None:
        pack = _pack(
            PARTIAL_QUEUE_CONFIG,
            PARTIAL_DECISION_CONFIG,
            PARTIAL_PREVIEW_CONFIG,
            PARTIAL_DRY_RUN_CONFIG,
            PARTIAL_READINESS_CONFIG,
            GATE_CONFIG,
            HUMAN_DECISION_CONFIG,
        )

        self.assertEqual(pack.decision_status, "blocked_gate_not_ready")
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_synthetic_complete_records_registry_update_dry_run_decision(self) -> None:
        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
        )

        self.assertEqual(pack.decision_status, "decision_recorded_for_registry_update_dry_run")
        self.assertTrue(pack.registry_update_dry_run_ready)

    def test_registry_update_dry_run_decision_does_not_approve_asset_or_change_status(self) -> None:
        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
        )

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.approval_status_change)
        self.assertFalse(pack.approvals_created)

    def test_registry_update_dry_run_decision_does_not_mutate_registry_recommend_order_or_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _pack(
            COMPLETE_QUEUE_CONFIG,
            COMPLETE_DECISION_CONFIG,
            COMPLETE_PREVIEW_CONFIG,
            COMPLETE_DRY_RUN_CONFIG,
            COMPLETE_READINESS_CONFIG,
            COMPLETE_GATE_CONFIG,
            COMPLETE_HUMAN_DECISION_CONFIG,
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)

    def test_rejected_decision_is_recorded_and_blocks_downstream_dry_run_readiness(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(_complete_gate(), _decision("rejected"), "inline")

        self.assertEqual(pack.decision_status, "decision_recorded_rejected")
        self.assertEqual(pack.rejected_count, 1)
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_needs_more_evidence_decision_is_recorded_and_blocks_downstream_dry_run_readiness(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(_complete_gate(), _decision("needs_more_evidence"), "inline")

        self.assertEqual(pack.decision_status, "decision_recorded_needs_more_evidence")
        self.assertEqual(pack.needs_more_evidence_count, 1)
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_invalid_decision_blocks(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(_complete_gate(), _decision("approve_asset_now"), "inline")

        self.assertEqual(pack.decision_status, "blocked_invalid_human_decision")
        self.assertFalse(pack.registry_update_dry_run_ready)

    def test_missing_decision_remains_pending(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(
            _complete_gate(),
            FTAWHumanApprovalReviewDecisionConfig(decision=None),
            "inline",
        )

        self.assertEqual(pack.decision_status, "pending_human_approval_review_decision")
        self.assertEqual(pack.pending_decision_count, 1)

    def test_asset_mismatch_blocks(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(_complete_gate(), _decision("approved_for_registry_update_dry_run", asset_id="wrong_asset"), "inline")

        self.assertEqual(pack.decision_status, "blocked_asset_mismatch")

    def test_unknown_review_packet_blocks(self) -> None:
        pack = build_ftaw_human_approval_review_decision_pack(
            _complete_gate(),
            _decision("approved_for_registry_update_dry_run", review_packet_id="unknown:manual_approval_review"),
            "inline",
        )

        self.assertEqual(pack.decision_status, "blocked_unknown_review_packet")

    def test_no_review_packet_blocks(self) -> None:
        gate = FTAWManualApprovalReviewGatePack(
            approval_review_gate_status="READY_FOR_HUMAN_APPROVAL_REVIEW",
            target_asset="ftaw_global_core_candidate",
            candidate_readiness_status="READY_FOR_MANUAL_APPROVAL_REVIEW",
            ready_for_manual_approval_review=True,
            required_evidence_types_count=5,
            planned_promotion_evidence_types_count=5,
            missing_evidence_types_count=0,
            missing_evidence_types=(),
            blocked_reasons=(),
            review_packet_created=False,
            next_manual_action="test",
            review_packet=None,
        )

        pack = build_ftaw_human_approval_review_decision_pack(gate, _decision("approved_for_registry_update_dry_run"), "inline")

        self.assertEqual(pack.decision_status, "blocked_no_review_packet")

    def test_decision_config_loads(self) -> None:
        config = load_ftaw_human_approval_review_decision_config(COMPLETE_HUMAN_DECISION_CONFIG)

        self.assertIsNotNone(config.decision)
        self.assertEqual(config.decision.human_decision, "approved_for_registry_update_dry_run")


if __name__ == "__main__":
    unittest.main()
