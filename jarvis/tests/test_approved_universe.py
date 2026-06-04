import json
import tempfile
import unittest
from pathlib import Path

from jarvis.approved_universe import build_approved_universe


def _write_registry(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, approval_status: str, **overrides) -> dict:
    asset = {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": "ETF",
        "sleeve": "global_core_etf",
        "ticker": "ETF",
        "isin_or_symbol": "IE00TEST0001",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": approval_status,
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
    }
    asset.update(overrides)
    return asset


class ApprovedUniverseTests(unittest.TestCase):
    def test_empty_approved_universe_handled_safely(self) -> None:
        universe = build_approved_universe(
            _write_registry({"assets": [_asset("candidate", "candidate_unreviewed")]}),
        )

        self.assertEqual(universe.total_approved_assets, 0)
        self.assertIn("no approved assets in universe.", universe.warnings)

    def test_approved_investable_asset_appears_in_universe(self) -> None:
        universe = build_approved_universe(
            _write_registry({"assets": [_asset("approved", "approved_investable")]}),
            crypto_universe_expected=False,
        )

        self.assertEqual(universe.total_approved_assets, 1)
        self.assertEqual(universe.approved_assets[0].asset_id, "approved")

    def test_candidate_unreviewed_test_position_and_rejected_excluded(self) -> None:
        universe = build_approved_universe(
            _write_registry(
                {
                    "assets": [
                        _asset("candidate", "candidate_unreviewed"),
                        _asset("test", "test_position"),
                        _asset("rejected", "rejected"),
                    ]
                }
            )
        )

        self.assertEqual(universe.total_approved_assets, 0)
        self.assertEqual(universe.blocked_non_approved_count, 3)

    def test_assets_grouped_by_sleeve(self) -> None:
        universe = build_approved_universe(
            _write_registry(
                {
                    "assets": [
                        _asset("core", "approved_investable", sleeve="global_core_etf"),
                        _asset("quality", "approved_investable", sleeve="quality_etf"),
                    ]
                }
            ),
            crypto_universe_expected=False,
        )

        self.assertIn("global_core_etf", universe.assets_by_sleeve)
        self.assertIn("quality_etf", universe.assets_by_sleeve)

    def test_missing_global_core_warning(self) -> None:
        universe = build_approved_universe(
            _write_registry({"assets": [_asset("quality", "approved_investable", sleeve="quality_etf")]}),
            crypto_universe_expected=False,
        )

        self.assertIn("missing global_core sleeve while ETF universe is expected.", universe.warnings)

    def test_multiple_assets_same_sleeve_warning_unless_allowed(self) -> None:
        warned = build_approved_universe(
            _write_registry(
                {"assets": [_asset("core_a", "approved_investable"), _asset("core_b", "approved_investable")]}
            ),
            crypto_universe_expected=False,
        )
        allowed = build_approved_universe(
            _write_registry(
                {
                    "assets": [
                        _asset("core_a", "approved_investable", multi_asset_allowed=True),
                        _asset("core_b", "approved_investable", multi_asset_allowed=True),
                    ]
                }
            ),
            crypto_universe_expected=False,
        )

        self.assertTrue(any("multiple approved assets" in warning for warning in warned.warnings))
        self.assertFalse(any("multiple approved assets" in warning for warning in allowed.warnings))

    def test_non_eur_warning(self) -> None:
        universe = build_approved_universe(
            _write_registry({"assets": [_asset("usd_asset", "approved_investable", currency="USD")]}),
            crypto_universe_expected=False,
        )

        self.assertTrue(any("currency is USD" in warning for warning in universe.warnings))


if __name__ == "__main__":
    unittest.main()
