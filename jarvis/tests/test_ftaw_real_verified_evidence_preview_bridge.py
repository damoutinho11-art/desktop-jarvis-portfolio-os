import unittest
from pathlib import Path

from jarvis.ftaw_real_manual_verification_decision_recorder import build_ftaw_real_manual_verification_decision_recorder
from jarvis.ftaw_real_verified_evidence_preview_bridge import (
    build_ftaw_real_verified_evidence_preview_bridge,
    build_ftaw_real_verified_evidence_preview_bridge_from_files,
)
from jarvis.tests.test_ftaw_real_identity_guarded_verification_queue_dry_run_bridge import _complete_queue_dry_run_bridge
from jarvis.tests.test_ftaw_real_manual_verification_decision_recorder import (
    COMPLETE_REAL_MANUAL_DECISION_CONFIG,
    PARTIAL_REAL_MANUAL_DECISION_CONFIG,
    REAL_MANUAL_DECISION_CONFIG,
    _accept_entry,
)
from jarvis.tests.test_ftaw_real_manual_verification_decision_recorder_report import _report as _v40_report
from jarvis.tests.test_ftaw_real_manual_verification_decision_recorder import _real_manual_decision_recorder
from jarvis.tests.test_ftaw_real_manual_verification_decision_recorder import (
    _complete_real_manual_decision_recorder,
    _partial_real_manual_decision_recorder,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import SOURCE_REGISTRY


REAL_PREVIEW_BRIDGE_CONFIG = "jarvis/data/ftaw_real_verified_evidence_preview_bridge.example.json"
PARTIAL_REAL_PREVIEW_BRIDGE_CONFIG = "jarvis/data/ftaw_real_verified_evidence_preview_bridge.synthetic_partial.example.json"
COMPLETE_REAL_PREVIEW_BRIDGE_CONFIG = "jarvis/data/ftaw_real_verified_evidence_preview_bridge.synthetic_complete.example.json"


def _real_preview_bridge(manual_decisions=None):
    return build_ftaw_real_verified_evidence_preview_bridge(manual_decisions or _real_manual_decision_recorder())


def _partial_real_preview_bridge():
    return build_ftaw_real_verified_evidence_preview_bridge(_partial_real_manual_decision_recorder())


def _complete_real_preview_bridge():
    return build_ftaw_real_verified_evidence_preview_bridge(_complete_real_manual_decision_recorder())


class FTAWRealVerifiedEvidencePreviewBridgeTests(unittest.TestCase):
    def test_default_blocks_without_manual_verification_decisions(self) -> None:
        pack = _real_preview_bridge()

        self.assertEqual(pack.preview_bridge_status, "BLOCKED_NO_MANUAL_VERIFICATION_DECISIONS")
        self.assertEqual(pack.preview_record_count, 0)

    def test_partial_creates_only_valid_accepted_previews_and_blocks_with_reasons(self) -> None:
        pack = _partial_real_preview_bridge()

        self.assertEqual(pack.preview_bridge_status, "PARTIAL_VERIFIED_EVIDENCE_PREVIEW_READY")
        self.assertEqual(pack.accepted_decision_count, 1)
        self.assertEqual(pack.preview_record_count, 1)
        self.assertTrue(pack.blocked_reasons)
        self.assertEqual({record.evidence_type for record in pack.preview_records}, {"fund_metadata"})

    def test_complete_reaches_promotion_dry_run_review_status(self) -> None:
        pack = _complete_real_preview_bridge()

        self.assertEqual(pack.preview_bridge_status, "VERIFIED_EVIDENCE_PREVIEW_READY_FOR_PROMOTION_DRY_RUN_REVIEW")

    def test_complete_has_exactly_five_preview_records(self) -> None:
        pack = _complete_real_preview_bridge()

        self.assertEqual(pack.accepted_decision_count, 5)
        self.assertEqual(pack.preview_record_count, 5)
        self.assertEqual(pack.missing_preview_count, 0)
        self.assertTrue(all(record.verified_evidence_preview for record in pack.preview_records))

    def test_missing_accepted_decision_blocks(self) -> None:
        manual_decisions = build_ftaw_real_manual_verification_decision_recorder(
            _complete_queue_dry_run_bridge(),
            tuple(_accept_entry(evidence_type) for evidence_type in ("fund_metadata", "fee_metadata", "distribution_policy", "market_data")),
        )

        pack = build_ftaw_real_verified_evidence_preview_bridge(manual_decisions)

        self.assertEqual(pack.preview_bridge_status, "PARTIAL_VERIFIED_EVIDENCE_PREVIEW_READY")
        self.assertEqual(pack.missing_preview_count, 1)

    def test_reject_and_needs_correction_are_excluded_and_block_readiness(self) -> None:
        reject = _accept_entry("fund_metadata")
        reject["manual_verification_decision"] = "reject"
        correction = _accept_entry("fee_metadata")
        correction["manual_verification_decision"] = "needs_correction"
        manual_decisions = build_ftaw_real_manual_verification_decision_recorder(_complete_queue_dry_run_bridge(), (reject, correction))

        pack = build_ftaw_real_verified_evidence_preview_bridge(manual_decisions)

        self.assertEqual(pack.preview_bridge_status, "PARTIAL_VERIFIED_EVIDENCE_PREVIEW_READY")
        self.assertEqual(pack.preview_record_count, 0)
        self.assertTrue(any("rejected" in reason or "needs_correction" in reason for reason in pack.blocked_reasons))

    def test_platform_and_tax_remain_excluded_outstanding(self) -> None:
        pack = _complete_real_preview_bridge()

        self.assertIn("platform_availability", pack.manual_private_outstanding)
        self.assertIn("tax_route", pack.manual_private_outstanding)
        self.assertNotIn("platform_availability", {record.evidence_type for record in pack.preview_records})
        self.assertNotIn("tax_route", {record.evidence_type for record in pack.preview_records})

    def test_no_evidence_verification_or_verified_evidence_promotion(self) -> None:
        pack = _complete_real_preview_bridge()

        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertTrue(all(not record.evidence_verified for record in pack.preview_records))
        self.assertTrue(all(not record.verified_by_user for record in pack.preview_records))
        self.assertTrue(all(not record.verified_evidence_promoted for record in pack.preview_records))

    def test_no_approval_registry_mutation_or_recommendation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_real_preview_bridge()

        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                not record.approved_asset
                and not record.registry_mutation
                and not record.allocation_recommendation
                for record in pack.preview_records
            )
        )

    def test_no_buy_sell_trade_executor_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_real_preview_bridge()

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)
        self.assertTrue(all(not record.buy_signal and not record.trade_executed for record in pack.preview_records))


if __name__ == "__main__":
    unittest.main()
