import unittest
from pathlib import Path

from jarvis.ftaw_real_candidate_readiness_review_pack import build_ftaw_real_candidate_readiness_review_pack
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import SOURCE_REGISTRY
from jarvis.tests.test_ftaw_real_verified_evidence_promotion_dry_run_pack import (
    _complete_real_promotion_dry_run_pack,
    _partial_real_promotion_dry_run_pack,
    _real_promotion_dry_run_pack,
)


REAL_CANDIDATE_READINESS_REVIEW_CONFIG = "jarvis/data/ftaw_real_candidate_readiness_review_pack.example.json"
PARTIAL_REAL_CANDIDATE_READINESS_REVIEW_CONFIG = "jarvis/data/ftaw_real_candidate_readiness_review_pack.synthetic_partial.example.json"
COMPLETE_REAL_CANDIDATE_READINESS_REVIEW_CONFIG = "jarvis/data/ftaw_real_candidate_readiness_review_pack.synthetic_complete.example.json"


def _real_candidate_readiness_review_pack(promotion_dry_run=None):
    return build_ftaw_real_candidate_readiness_review_pack(promotion_dry_run or _real_promotion_dry_run_pack())


def _partial_real_candidate_readiness_review_pack():
    return build_ftaw_real_candidate_readiness_review_pack(_partial_real_promotion_dry_run_pack())


def _complete_real_candidate_readiness_review_pack():
    return build_ftaw_real_candidate_readiness_review_pack(_complete_real_promotion_dry_run_pack())


class FTAWRealCandidateReadinessReviewPackTests(unittest.TestCase):
    def test_default_blocks_without_v4_42_dry_run(self) -> None:
        pack = _real_candidate_readiness_review_pack()

        self.assertEqual(pack.readiness_status, "BLOCKED_NO_VERIFIED_EVIDENCE_PROMOTION_DRY_RUN")
        self.assertEqual(pack.planned_item_count, 0)

    def test_partial_reviews_only_available_items_and_blocks_with_reasons(self) -> None:
        pack = _partial_real_candidate_readiness_review_pack()

        self.assertEqual(pack.readiness_status, "PARTIAL_REAL_CANDIDATE_READINESS_REVIEW_READY")
        self.assertEqual(pack.planned_item_count, 1)
        self.assertEqual({item.evidence_type for item in pack.readiness_items}, {"fund_metadata"})
        self.assertTrue(pack.blocked_reasons)

    def test_complete_reaches_manual_approval_review_ready(self) -> None:
        pack = _complete_real_candidate_readiness_review_pack()

        self.assertEqual(pack.readiness_status, "REAL_CANDIDATE_READY_FOR_MANUAL_APPROVAL_REVIEW")

    def test_complete_has_exactly_five_readiness_items(self) -> None:
        pack = _complete_real_candidate_readiness_review_pack()

        self.assertEqual(pack.required_item_count, 5)
        self.assertEqual(pack.planned_item_count, 5)
        self.assertEqual(pack.missing_item_count, 0)
        self.assertTrue(all(item.promotion_dry_run for item in pack.readiness_items))

    def test_missing_item_blocks(self) -> None:
        pack = _partial_real_candidate_readiness_review_pack()

        self.assertEqual(pack.missing_item_count, 4)
        self.assertTrue(any("missing planned promotion dry-run item" in reason for reason in pack.blocked_reasons))

    def test_platform_and_tax_outstanding_preserved(self) -> None:
        pack = _complete_real_candidate_readiness_review_pack()

        self.assertIn("platform_availability", pack.manual_private_outstanding)
        self.assertIn("tax_route", pack.manual_private_outstanding)
        self.assertNotIn("platform_availability", {item.evidence_type for item in pack.readiness_items})
        self.assertNotIn("tax_route", {item.evidence_type for item in pack.readiness_items})

    def test_no_evidence_verification_or_actual_verified_evidence_promotion(self) -> None:
        pack = _complete_real_candidate_readiness_review_pack()

        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertTrue(all(not item.evidence_verified for item in pack.readiness_items))
        self.assertTrue(all(not item.verified_evidence_promoted for item in pack.readiness_items))

    def test_no_approval_registry_mutation_or_recommendation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_real_candidate_readiness_review_pack()

        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                not item.approved_asset
                and not item.registry_mutation
                and not item.allocation_recommendation
                for item in pack.readiness_items
            )
        )

    def test_no_buy_sell_trade_executor_ingest_fetch_download_or_extraction(self) -> None:
        pack = _complete_real_candidate_readiness_review_pack()

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)
        self.assertTrue(all(not item.buy_signal and not item.trade_executed for item in pack.readiness_items))


if __name__ == "__main__":
    unittest.main()
