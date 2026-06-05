import unittest

from jarvis.asset_registry import load_asset_registry
from jarvis.candidate_evidence_matrix import build_candidate_evidence_matrix
from jarvis.exposure_loader import load_exposure_data
from jarvis.market_data_loader import load_market_data


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
MARKET_V2 = "jarvis/data/market_data.v2.example.json"
EXPOSURE_V2 = "jarvis/data/asset_exposure.v2.example.json"
POLICY = "jarvis/data/portfolio_policy.example.json"


class CandidateEvidenceV2FixtureTests(unittest.TestCase):
    def test_market_data_v2_loads(self) -> None:
        snapshot = load_market_data(MARKET_V2)

        self.assertEqual(snapshot.base_currency, "EUR")
        self.assertGreaterEqual(len(snapshot.series), 16)

    def test_asset_exposure_v2_loads(self) -> None:
        snapshot = load_exposure_data(EXPOSURE_V2)

        self.assertGreaterEqual(len(snapshot.assets), 9)
        self.assertIn("vwce_global_core_candidate", snapshot.by_asset_id())

    def test_v2_fixtures_produce_at_least_one_eligible_etf_candidate(self) -> None:
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)

        self.assertTrue(
            any(row.asset_type == "ETF" and row.eligible_for_manual_review for row in matrix.rows)
        )

    def test_v2_fixtures_produce_at_least_one_eligible_crypto_candidate(self) -> None:
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)

        self.assertTrue(
            any(row.asset_type == "crypto" and row.eligible_for_manual_review for row in matrix.rows)
        )

    def test_no_candidate_becomes_approved_investable(self) -> None:
        registry = load_asset_registry(REGISTRY)
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)

        self.assertFalse(any(asset.approval_status == "approved_investable" for asset in registry.assets))
        self.assertFalse(any(row.approval_status == "approved_investable" for row in matrix.rows))

    def test_no_buy_sell_request_is_created(self) -> None:
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)

        self.assertFalse(matrix.buy_sell_requests_created)

    def test_no_allocation_recommendation_is_created(self) -> None:
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)

        self.assertFalse(hasattr(matrix, "allocation_recommendations"))

    def test_missing_evidence_candidates_remain_blocked(self) -> None:
        matrix = build_candidate_evidence_matrix(REGISTRY, MARKET_V2, EXPOSURE_V2, POLICY)
        blocked = [row for row in matrix.rows if not row.eligible_for_manual_review]

        self.assertTrue(blocked)
        self.assertTrue(any("market_data" in row.missing_evidence for row in blocked))


if __name__ == "__main__":
    unittest.main()
