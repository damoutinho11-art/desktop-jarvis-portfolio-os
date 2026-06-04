import json
import tempfile
import unittest
from pathlib import Path

from jarvis.portfolio_drift import analyze_portfolio_drift


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _snapshot(accounts: list[dict]) -> Path:
    return _write_json({"snapshot_date": "2026-06-04", "base_currency": "EUR", "accounts": accounts})


def _account(account_id: str, role: str, cash: float = 0.0, holdings: list[dict] | None = None) -> dict:
    return {
        "account_id": account_id,
        "platform": "manual_test",
        "role": role,
        "cash_eur": cash,
        "holdings": holdings or [],
    }


def _holding(symbol: str, value: float, asset_class: str = "etf", classification: str | None = None) -> dict:
    payload = {"asset_symbol": symbol, "asset_class": asset_class, "market_value_eur": value}
    if classification:
        payload["classification"] = classification
    return payload


def _asset(asset_id: str, sleeve: str, status: str = "approved_investable", asset_type: str = "ETF") -> dict:
    asset = {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": asset_type,
        "sleeve": sleeve,
        "ticker": asset_id,
        "isin_or_symbol": asset_id,
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": status,
        "risk_level": "medium",
    }
    if asset_type == "ETF":
        asset.update({"provider": "Provider", "index_tracked": "Index", "replication_method": "physical"})
    if asset_type == "crypto":
        asset.update(
            {
                "network_or_protocol": "Bitcoin",
                "custody_platforms": ["LHV Crypto Investments"],
                "transferable": False,
                "mica_route_possible": True,
            }
        )
    return asset


def _registry(*assets: dict) -> Path:
    return _write_json({"assets": list(assets)})


POLICY = "jarvis/data/portfolio_policy.example.json"


class PortfolioDriftTests(unittest.TestCase):
    def test_protected_emergency_cash_excluded_from_investable_weights(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot(
                [
                    _account("emergency_fund", "protected_cash", cash=3000.0),
                    _account("lightyear", "ETF_engine", holdings=[_holding("CORE", 100.0)]),
                ]
            ),
            POLICY,
            _registry(_asset("CORE", "global_core")),
        )

        self.assertEqual(result.protected_cash_eur, 3000.0)
        self.assertEqual(result.total_investable_value_eur, 100.0)

    def test_daily_banking_cash_excluded_by_default(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot(
                [
                    _account("daily_spending", "daily_spending", cash=250.0),
                    _account("lightyear", "ETF_engine", holdings=[_holding("CORE", 100.0)]),
                ]
            ),
            POLICY,
            _registry(_asset("CORE", "global_core")),
        )

        self.assertEqual(result.protected_cash_eur, 250.0)
        self.assertEqual(result.total_investable_value_eur, 100.0)

    def test_legacy_holdings_tracked_separately(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lhv_growth", "legacy_cleanup", holdings=[_holding("OLD", 123.0, "legacy_etf", "legacy_existing")])]),
            POLICY,
            _registry(),
        )

        self.assertEqual(result.legacy_value_eur, 123.0)

    def test_test_positions_tracked_separately(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("TEST", 12.0)])]),
            POLICY,
            _registry(_asset("TEST", "global_core", status="test_position")),
        )

        self.assertEqual(result.test_position_value_eur, 12.0)

    def test_approved_asset_maps_to_sleeve(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("CORE", 100.0)])]),
            POLICY,
            _registry(_asset("CORE", "global_core")),
        )

        self.assertEqual(result.sleeve_current_weights["global_core"], 1.0)

    def test_unknown_asset_becomes_unknown_unapproved(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("MYSTERY", 10.0)])]),
            POLICY,
            _registry(),
        )

        self.assertEqual(result.unapproved_value_eur, 10.0)
        self.assertTrue(any("unknown_unapproved" in warning for warning in result.warnings))

    def test_sleeve_below_min_detected(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot(
                [
                    _account(
                        "lightyear",
                        "ETF_engine",
                        holdings=[_holding("CORE", 10.0), _holding("CASH", 90.0, "cash")],
                    )
                ]
            ),
            POLICY,
            _registry(_asset("CORE", "global_core"), _asset("CASH", "tactical_cash", asset_type="cash")),
        )

        self.assertEqual(result.sleeve_band_status["global_core"], "below_min")

    def test_sleeve_above_max_detected(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("CORE", 100.0)])]),
            POLICY,
            _registry(_asset("CORE", "global_core")),
        )

        self.assertEqual(result.sleeve_band_status["global_core"], "above_max")

    def test_empty_approved_universe_blocks_allocation_ready(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("MYSTERY", 10.0)])]),
            POLICY,
            _registry(),
        )

        self.assertFalse(result.allocation_ready)
        self.assertIn("approved universe is empty.", result.blockers)

    def test_required_sleeve_with_no_approved_asset_blocks_allocation_ready(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("CASH", 10.0, "cash")])]),
            POLICY,
            _registry(_asset("CASH", "tactical_cash", asset_type="cash")),
        )

        self.assertFalse(result.allocation_ready)
        self.assertTrue(any("required sleeve global_core" in blocker for blocker in result.blockers))

    def test_strict_mode_blocks_unknown_unapproved_holdings(self) -> None:
        result = analyze_portfolio_drift(
            _snapshot([_account("lightyear", "ETF_engine", holdings=[_holding("MYSTERY", 10.0)])]),
            POLICY,
            _registry(_asset("CORE", "global_core")),
            strict_mode=True,
        )

        self.assertIn("strict_mode blocks unknown/unapproved holdings.", result.blockers)


if __name__ == "__main__":
    unittest.main()
