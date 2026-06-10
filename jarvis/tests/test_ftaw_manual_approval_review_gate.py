import unittest
from pathlib import Path

from jarvis.ftaw_candidate_readiness_pack import FTAWCandidateReadinessPack, build_ftaw_candidate_readiness_pack
from jarvis.ftaw_manual_approval_review_gate import (
    build_ftaw_manual_approval_review_gate,
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


def _gate(queue_config=QUEUE_CONFIG, decision_config=DECISION_CONFIG, preview_config=PREVIEW_CONFIG, dry_run_config=DRY_RUN_CONFIG, readiness_config=READINESS_CONFIG, gate_config=GATE_CONFIG):
    return build_ftaw_manual_approval_review_gate_from_files(
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
    )


def _complete_readiness():
    return build_ftaw_candidate_readiness_pack(
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
    )


class FTAWManualApprovalReviewGateTests(unittest.TestCase):
    def test_default_fixture_blocks_and_creates_no_packet(self) -> None:
        gate = _gate()

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertFalse(gate.review_packet_created)
        self.assertIsNone(gate.review_packet)

    def test_partial_synthetic_fixture_blocks_and_creates_no_packet(self) -> None:
        gate = _gate(PARTIAL_QUEUE_CONFIG, PARTIAL_DECISION_CONFIG, PARTIAL_PREVIEW_CONFIG, PARTIAL_DRY_RUN_CONFIG, PARTIAL_READINESS_CONFIG)

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertFalse(gate.review_packet_created)
        self.assertIn("missing evidence types remain.", gate.blocked_reasons)

    def test_synthetic_complete_creates_manual_approval_review_packet(self) -> None:
        gate = _gate(COMPLETE_QUEUE_CONFIG, COMPLETE_DECISION_CONFIG, COMPLETE_PREVIEW_CONFIG, COMPLETE_DRY_RUN_CONFIG, COMPLETE_READINESS_CONFIG, COMPLETE_GATE_CONFIG)

        self.assertEqual(gate.approval_review_gate_status, "READY_FOR_HUMAN_APPROVAL_REVIEW")
        self.assertTrue(gate.review_packet_created)
        self.assertIsNotNone(gate.review_packet)

    def test_synthetic_complete_packet_is_review_only_not_approval_or_buy_signal(self) -> None:
        packet = _gate(COMPLETE_QUEUE_CONFIG, COMPLETE_DECISION_CONFIG, COMPLETE_PREVIEW_CONFIG, COMPLETE_DRY_RUN_CONFIG, COMPLETE_READINESS_CONFIG, COMPLETE_GATE_CONFIG).review_packet

        self.assertIsNotNone(packet)
        self.assertTrue(packet.approval_review_only)
        self.assertFalse(packet.approved)
        self.assertFalse(packet.approval_status_change)
        self.assertFalse(packet.buy_signal)

    def test_missing_evidence_types_block(self) -> None:
        readiness = _complete_readiness()
        partial = FTAWCandidateReadinessPack(
            target_asset=readiness.target_asset,
            candidate_readiness_status="READY_FOR_MANUAL_APPROVAL_REVIEW",
            source_fact_status=readiness.source_fact_status,
            identity_guard_status=readiness.identity_guard_status,
            verification_queue_status=readiness.verification_queue_status,
            manual_decision_status=readiness.manual_decision_status,
            preview_bridge_status=readiness.preview_bridge_status,
            promotion_dry_run_status=readiness.promotion_dry_run_status,
            required_evidence_types_count=5,
            planned_promotion_evidence_types_count=4,
            missing_evidence_types_count=1,
            planned_promotion_evidence_types=("fund_metadata", "fee_metadata", "distribution_policy", "exposure_data"),
            missing_evidence_types=("market_data",),
            blocked_reasons=(),
            next_manual_action=readiness.next_manual_action,
            ready_for_manual_approval_review=True,
        )

        gate = build_ftaw_manual_approval_review_gate(partial)

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertFalse(gate.review_packet_created)

    def test_non_dry_run_promotion_mode_blocks(self) -> None:
        gate = build_ftaw_manual_approval_review_gate(_complete_readiness(), promotion_modes=("dry_run", "dry_run", "live", "dry_run", "dry_run"))

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertIn("all planned promotions must remain dry_run.", gate.blocked_reasons)

    def test_readiness_status_below_approval_review_blocks(self) -> None:
        gate = _gate(PARTIAL_QUEUE_CONFIG, PARTIAL_DECISION_CONFIG, PARTIAL_PREVIEW_CONFIG, PARTIAL_DRY_RUN_CONFIG, PARTIAL_READINESS_CONFIG)

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertIn("candidate readiness status is READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION.", gate.blocked_reasons)

    def test_ready_for_manual_approval_review_false_blocks(self) -> None:
        readiness = _complete_readiness()
        altered = FTAWCandidateReadinessPack(
            target_asset=readiness.target_asset,
            candidate_readiness_status="READY_FOR_MANUAL_APPROVAL_REVIEW",
            source_fact_status=readiness.source_fact_status,
            identity_guard_status=readiness.identity_guard_status,
            verification_queue_status=readiness.verification_queue_status,
            manual_decision_status=readiness.manual_decision_status,
            preview_bridge_status=readiness.preview_bridge_status,
            promotion_dry_run_status=readiness.promotion_dry_run_status,
            required_evidence_types_count=readiness.required_evidence_types_count,
            planned_promotion_evidence_types_count=readiness.planned_promotion_evidence_types_count,
            missing_evidence_types_count=0,
            planned_promotion_evidence_types=readiness.planned_promotion_evidence_types,
            missing_evidence_types=(),
            blocked_reasons=(),
            next_manual_action=readiness.next_manual_action,
            ready_for_manual_approval_review=False,
        )

        gate = build_ftaw_manual_approval_review_gate(altered)

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED")
        self.assertIn("ready_for_manual_approval_review is false.", gate.blocked_reasons)

    def test_no_verified_promotion_registry_mutation_recommendation_order_or_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        gate = _gate(COMPLETE_QUEUE_CONFIG, COMPLETE_DECISION_CONFIG, COMPLETE_PREVIEW_CONFIG, COMPLETE_DRY_RUN_CONFIG, COMPLETE_READINESS_CONFIG, COMPLETE_GATE_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(gate.no_verified_evidence_promotion)
        self.assertFalse(gate.approvals_created)
        self.assertFalse(gate.registry_mutation_performed)
        self.assertFalse(gate.allocation_recommendation_created)
        self.assertFalse(gate.buy_sell_requests_created)
        self.assertFalse(gate.trades_executed)


if __name__ == "__main__":
    unittest.main()
