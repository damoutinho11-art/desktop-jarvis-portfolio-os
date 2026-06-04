import unittest

from jarvis.asset_approval_gate import check_asset_approval
from jarvis.asset_registry import CandidateAsset


def _asset(status: str) -> CandidateAsset:
    return CandidateAsset(
        asset_id=f"asset_{status}",
        name="Asset",
        asset_type="ETF",
        sleeve="quality_etf",
        ticker="QETF",
        isin_or_symbol="IE00TEST0001",
        platforms=("Lightyear",),
        currency="EUR",
        domicile="Ireland",
        distribution_policy="accumulating",
        ter_or_fee=0.2,
        data_source="manual_test",
        approval_status=status,
        risk_level="medium",
        provider="Provider",
        index_tracked="Quality Index",
        replication_method="physical",
    )


class AssetApprovalGateTests(unittest.TestCase):
    def test_approved_investable_passes_gate(self) -> None:
        result = check_asset_approval(_asset("approved_investable"))

        self.assertTrue(result.eligible_for_allocation)
        self.assertIn("approved_investable", result.reason)

    def test_candidate_unreviewed_is_blocked(self) -> None:
        result = check_asset_approval(_asset("candidate_unreviewed"))

        self.assertFalse(result.eligible_for_allocation)
        self.assertIn("not approved_investable", result.reason)

    def test_legacy_existing_is_blocked(self) -> None:
        result = check_asset_approval(_asset("legacy_existing"))

        self.assertFalse(result.eligible_for_allocation)
        self.assertIn("legacy_existing", result.reason)

    def test_test_position_is_blocked(self) -> None:
        result = check_asset_approval(_asset("test_position"))

        self.assertFalse(result.eligible_for_allocation)
        self.assertIn("test_position", result.reason)


if __name__ == "__main__":
    unittest.main()
