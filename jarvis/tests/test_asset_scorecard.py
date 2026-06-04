import unittest

from jarvis.asset_scorecard import AssetScorecard


class AssetScorecardTests(unittest.TestCase):
    def test_scorecard_serializes_to_dict(self) -> None:
        scorecard = AssetScorecard(
            asset_id="asset_1",
            asset_type="ETF",
            approval_status="candidate_unreviewed",
            approved_for_allocation=False,
            manual_approval_required=True,
            final_candidate_score=42.5,
            score_breakdown={"data_quality_score": 50.0},
            reasons=("offline scoring only",),
            warnings=("placeholder data",),
            blockers=("not approved_investable",),
        )

        payload = scorecard.to_dict()

        self.assertEqual(payload["asset_id"], "asset_1")
        self.assertFalse(payload["approved_for_allocation"])
        self.assertTrue(payload["manual_approval_required"])
        self.assertEqual(payload["warnings"], ["placeholder data"])


if __name__ == "__main__":
    unittest.main()
