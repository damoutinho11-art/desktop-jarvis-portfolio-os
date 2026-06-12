import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_real_manual_approval_review_gate import build_ftaw_real_manual_approval_review_gate
from jarvis.tests.test_ftaw_real_candidate_readiness_review_pack import (
    _complete_real_candidate_readiness_review_pack,
    _partial_real_candidate_readiness_review_pack,
    _real_candidate_readiness_review_pack,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import SOURCE_REGISTRY


REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG = "jarvis/data/ftaw_real_manual_approval_review_gate.example.json"
PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG = "jarvis/data/ftaw_real_manual_approval_review_gate.synthetic_partial.example.json"
COMPLETE_REAL_MANUAL_APPROVAL_REVIEW_GATE_CONFIG = "jarvis/data/ftaw_real_manual_approval_review_gate.synthetic_complete.example.json"


def _real_manual_approval_review_gate(readiness=None):
    return build_ftaw_real_manual_approval_review_gate(readiness or _real_candidate_readiness_review_pack())


def _partial_real_manual_approval_review_gate():
    return build_ftaw_real_manual_approval_review_gate(_partial_real_candidate_readiness_review_pack())


def _complete_real_manual_approval_review_gate():
    return build_ftaw_real_manual_approval_review_gate(_complete_real_candidate_readiness_review_pack())


class FTAWRealManualApprovalReviewGateTests(unittest.TestCase):
    def test_default_blocks_without_v4_43_readiness(self) -> None:
        gate = _real_manual_approval_review_gate()

        self.assertEqual(gate.approval_review_gate_status, "BLOCKED_NO_REAL_CANDIDATE_READINESS_REVIEW")
        self.assertFalse(gate.approval_packet_created)
        self.assertIsNone(gate.review_packet)

    def test_partial_creates_partial_packet_and_blocks_with_reasons(self) -> None:
        gate = _partial_real_manual_approval_review_gate()

        self.assertEqual(gate.approval_review_gate_status, "PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_READY")
        self.assertTrue(gate.approval_packet_created)
        self.assertIsNotNone(gate.review_packet)
        self.assertTrue(gate.blocked_reasons)

    def test_complete_reaches_ready_for_real_human_approval_review(self) -> None:
        gate = _complete_real_manual_approval_review_gate()

        self.assertEqual(gate.approval_review_gate_status, "READY_FOR_REAL_HUMAN_APPROVAL_REVIEW")
        self.assertTrue(gate.approval_packet_created)

    def test_complete_requires_five_readiness_items(self) -> None:
        gate = _complete_real_manual_approval_review_gate()

        self.assertEqual(gate.required_item_count, 5)
        self.assertEqual(gate.readiness_item_count, 5)
        self.assertEqual(gate.missing_item_count, 0)

    def test_missing_readiness_item_blocks(self) -> None:
        readiness = _complete_real_candidate_readiness_review_pack()
        altered = replace(
            readiness,
            readiness_items=readiness.readiness_items[:4],
            planned_item_count=4,
            missing_item_count=1,
        )

        gate = build_ftaw_real_manual_approval_review_gate(altered)

        self.assertEqual(gate.approval_review_gate_status, "PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_READY")
        self.assertTrue(any("missing readiness item" in reason for reason in gate.blocked_reasons))

    def test_platform_and_tax_outstanding_preserved(self) -> None:
        gate = _complete_real_manual_approval_review_gate()

        self.assertIn("platform_availability", gate.manual_private_outstanding)
        self.assertIn("tax_route", gate.manual_private_outstanding)
        self.assertIsNotNone(gate.review_packet)
        self.assertIn("platform_availability", gate.review_packet.manual_private_outstanding)
        self.assertIn("tax_route", gate.review_packet.manual_private_outstanding)

    def test_review_packet_is_review_only_and_not_actionable(self) -> None:
        packet = _complete_real_manual_approval_review_gate().review_packet

        self.assertIsNotNone(packet)
        self.assertTrue(packet.approval_review_only)
        self.assertFalse(packet.approved_asset)
        self.assertFalse(packet.approval_status_change)
        self.assertFalse(packet.registry_mutation)
        self.assertFalse(packet.allocation_recommendation)
        self.assertFalse(packet.buy_signal)
        self.assertFalse(packet.trade_executed)

    def test_no_approval_registry_mutation_or_recommendation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        gate = _complete_real_manual_approval_review_gate()

        self.assertFalse(gate.approvals_created)
        self.assertFalse(gate.registry_mutation)
        self.assertFalse(gate.allocation_recommendation_created)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_trade_executor_verification_promotion_or_ingest_fetch_download_extraction(self) -> None:
        gate = _complete_real_manual_approval_review_gate()

        self.assertFalse(gate.buy_sell_requests_created)
        self.assertFalse(gate.trades_executed)
        self.assertFalse(gate.executor_created)
        self.assertFalse(gate.evidence_verified)
        self.assertFalse(gate.verified_evidence_promotion)
        self.assertFalse(gate.private_file_auto_ingest)
        self.assertFalse(gate.automatic_source_fetching)
        self.assertFalse(gate.automatic_downloads)
        self.assertFalse(gate.automatic_fact_extraction)


if __name__ == "__main__":
    unittest.main()
