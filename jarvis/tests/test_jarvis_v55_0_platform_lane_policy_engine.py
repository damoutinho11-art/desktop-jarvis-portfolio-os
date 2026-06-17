from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.platform_lane_policy import (
    DEFAULT_LEGACY_MODE,
    STATUS_REVIEW_REQUIRED,
    build_platform_lane_policy_result,
    format_platform_lane_policy,
)


def _snapshot() -> dict:
    return {
        "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
        "snapshot_date": "2026-06-17",
        "is_template": False,
        "brokerless_manual_snapshot": True,
        "cash_eur": 717.42,
        "emergency_fund_reserved_eur": 3600.00,
        "totals": {
            "visible_liquid_cash_excluding_emergency_eur": 717.42,
            "visible_invested_assets_excluding_cash_eur": 1156.38,
            "visible_portfolio_excluding_emergency_eur": 1873.80,
            "visible_total_including_emergency_eur": 5473.80,
        },
        "holdings": [
            {"lane": "cash", "asset_name": "EUR current-account cash", "instrument_id": "eur_current_account_cash", "market_value_eur": 712.51},
            {"lane": "cash", "asset_name": "Other visible cash", "instrument_id": "other_cash", "market_value_eur": 4.90},
            {"lane": "cash_reserve", "asset_name": "Emergency fund", "instrument_id": "emergency_fund_reserved_cash", "market_value_eur": 3600.00},
            {"lane": "crypto", "asset_name": "Bitcoin", "instrument_id": "bitcoin_btc", "market_value_eur": 19.78},
            {"lane": "stock_fund_etf", "asset_name": "iShares MSCI Emerging Markets", "instrument_id": "em", "market_value_eur": 373.55},
            {"lane": "stock_fund_etf", "asset_name": "LHV Euro Bond Fund", "instrument_id": "bond", "market_value_eur": 0.15},
            {"lane": "stock_fund_etf", "asset_name": "LHV World Equities Fund", "instrument_id": "world", "market_value_eur": 1.54},
            {"lane": "stock_fund_etf", "asset_name": "db x-trackers China CSI300 ETF", "instrument_id": "china", "market_value_eur": 128.41},
            {"lane": "stock_fund_etf", "asset_name": "iShares Core S&P 500 UCITS ETF", "instrument_id": "sp500", "market_value_eur": 632.95},
        ],
        "cost_basis": {"sp500": 573.79, "em": 318.59, "bitcoin_btc": 20.03},
    }


def _write_snapshot(path: Path) -> None:
    path.write_text(json.dumps(_snapshot()), encoding="utf-8")


class JarvisV550PlatformLanePolicyEngineTests(unittest.TestCase):
    def test_platform_policy_routes_crypto_to_lhv_and_core_to_lightyear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_lane_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        actions = {(item.platform, item.lane): item.amount_eur for item in result.platform_actions}
        self.assertEqual(actions[("LHV", "cash_reserve")], 75.0)
        self.assertEqual(actions[("LHV", "crypto")], 170.0)
        self.assertEqual(actions[("Lightyear", "stock_fund_etf")], 255.0)
        self.assertEqual(actions[("Lightyear", "individual_stock")], 0.0)
        self.assertIn("ETF_STOCK_FUND_NEW_MONEY_TO_LIGHTYEAR", result.platform_policy_flags)
        self.assertIn("CRYPTO_NEW_MONEY_TO_LHV", result.platform_policy_flags)

    def test_legacy_positions_are_observed_only_and_selling_is_blocked_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_lane_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        self.assertEqual(result.legacy_positions_mode, DEFAULT_LEGACY_MODE)
        self.assertFalse(result.legacy_sell_allowed)
        legacy = [item for item in result.platform_actions if item.lane == "legacy_positions"]
        self.assertEqual(len(legacy), 1)
        self.assertEqual(legacy[0].amount_eur, 0.0)
        self.assertTrue(legacy[0].review_only)
        self.assertIn("LEGACY_SELL_BLOCKED_BY_DEFAULT", result.platform_policy_flags)

    def test_legacy_sell_allowed_blocks_until_migration_review_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_lane_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
                legacy_sell_allowed=True,
            )

        self.assertIn("legacy_sell_requires_separate_manual_migration_review", result.blockers)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_missing_expenses_blocks_platform_policy_instead_of_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_lane_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=None,
            )

        self.assertIn("monthly_expenses_required_for_dynamic_target_policy", result.blockers)
        self.assertFalse(result.allocation_mutation)
        self.assertTrue(result.no_trades_executed)

    def test_format_shows_platform_map_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_lane_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        output = format_platform_lane_policy(result)
        self.assertIn("J.A.R.V.I.S. PLATFORM LANE POLICY ENGINE", output)
        self.assertIn("crypto platform: LHV", output)
        self.assertIn("ETF/stock/fund new investing platform: Lightyear", output)
        self.assertIn("LHV / crypto: 170.0 EUR", output)
        self.assertIn("Lightyear / stock_fund_etf: 255.0 EUR", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_platform_lane_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = runtime_operator.main(
                    [
                        "--platform-lane-policy",
                        "--current-date",
                        "2026-06-17",
                        "--manual-portfolio-snapshot-path",
                        str(snapshot_path),
                        "--monthly-contribution-eur",
                        "500",
                        "--monthly-expenses-eur",
                        "1200",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("PLATFORM LANE POLICY ENGINE", stdout.getvalue())
        self.assertIn("LHV / crypto: 170.0 EUR", stdout.getvalue())
        self.assertIn("Lightyear / stock_fund_etf: 255.0 EUR", stdout.getvalue())

    def test_runtime_surface_reports_v55_and_platform_lane_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v55.0")
        self.assertEqual(
            surface["active_platform_lane_policy_module"],
            "jarvis.runtime.platform_lane_policy",
        )
        self.assertTrue(surface["execution_forbidden"])
        self.assertTrue(surface["manual_approval_required"])


if __name__ == "__main__":
    unittest.main()