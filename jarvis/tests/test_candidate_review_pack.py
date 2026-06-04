import unittest

from jarvis.candidate_review_pack import CandidateReviewPack


class CandidateReviewPackTests(unittest.TestCase):
    def test_review_pack_serializes(self) -> None:
        pack = CandidateReviewPack(
            asset_id="asset_1",
            asset_type="ETF",
            sleeve="quality_etf",
            approval_status="candidate_unreviewed",
            approved_for_allocation=False,
            final_candidate_score=75.0,
            market_metrics_summary={"latest_price": 100.0},
            exposure_summary={"holding_count": 3},
            warnings=("warning",),
            blockers=("not approved",),
            review_status="review_ready",
            can_submit_for_manual_approval=True,
            manual_approval_required=True,
        )

        payload = pack.to_dict()

        self.assertEqual(payload["asset_id"], "asset_1")
        self.assertTrue(payload["manual_approval_required"])
        self.assertEqual(payload["review_status"], "review_ready")

    def test_manual_approval_required_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "manual_approval_required"):
            CandidateReviewPack(
                asset_id="asset_1",
                asset_type="ETF",
                sleeve="quality_etf",
                approval_status="candidate_unreviewed",
                approved_for_allocation=False,
                final_candidate_score=75.0,
                market_metrics_summary=None,
                exposure_summary=None,
                review_status="review_ready",
                manual_approval_required=False,
            )


if __name__ == "__main__":
    unittest.main()
