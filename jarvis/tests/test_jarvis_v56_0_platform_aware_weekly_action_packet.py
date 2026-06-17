from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.platform_weekly_action_packet import (
    STATUS_REVIEW_REQUIRED,
    build_platform_aware_weekly_action_packet_result,
    format_platform_aware_weekly_action_packet,
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


class JarvisV560PlatformAwareWeeklyActionPacketTests(unittest.TestCase):
    def test_weekly_packet_maps_real_amounts_to_lhv_and_lightyear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_aware_weekly_action_packet_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        actions = {(item.platform, item.lane): item.amount_eur for item in result.weekly_actions}
        self.assertEqual(actions[("LHV", "cash_reserve")], 75.0)
        self.assertEqual(actions[("LHV", "crypto")], 170.0)
        self.assertEqual(actions[("Lightyear", "stock_fund_etf")], 255.0)
        self.assertEqual(actions[("Lightyear", "individual_stock")], 0.0)
        self.assertEqual(actions[("legacy_observed", "legacy_positions")], 0.0)
        self.assertEqual(result.total_manual_action_amount_eur, 500.0)

    def test_legacy_positions_are_observe_only_in_weekly_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_aware_weekly_action_packet_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        legacy = [item for item in result.weekly_actions if item.lane == "legacy_positions"]
        self.assertEqual(len(legacy), 1)
        self.assertEqual(legacy[0].amount_eur, 0.0)
        self.assertTrue(legacy[0].review_only)
        self.assertFalse(legacy[0].action_allowed_by_policy)
        self.assertFalse(result.legacy_sell_allowed)
        self.assertIn("NO_LEGACY_SELL_WITHOUT_MIGRATION_REVIEW", result.policy_flags)

    def test_packet_is_read_only_and_does_not_mutate_tickets_or_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_aware_weekly_action_packet_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.evidence_pack_mutation)
        self.assertFalse(result.local_cache_mutation)
        self.assertFalse(result.portfolio_state_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_missing_expenses_blocks_packet_instead_of_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_aware_weekly_action_packet_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=None,
            )

        self.assertIn("monthly_expenses_required_for_dynamic_target_policy", result.blockers)
        self.assertEqual(result.packet_status, "PLATFORM_AWARE_WEEKLY_ACTION_PACKET_BLOCKED")
        self.assertTrue(result.no_trades_executed)

    def test_format_is_a_clear_weekly_action_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_platform_aware_weekly_action_packet_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        output = format_platform_aware_weekly_action_packet(result)
        self.assertIn("J.A.R.V.I.S. WEEKLY PLATFORM ACTION PACKET", output)
        self.assertIn("LHV / cash_reserve: 75.0 EUR", output)
        self.assertIn("LHV / crypto: 170.0 EUR", output)
        self.assertIn("Lightyear / stock_fund_etf: 255.0 EUR", output)
        self.assertIn("legacy_observed / legacy_positions: 0.0 EUR", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_weekly_platform_action_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = runtime_operator.main(
                    [
                        "--weekly-platform-action-packet",
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
        self.assertIn("WEEKLY PLATFORM ACTION PACKET", stdout.getvalue())
        self.assertIn("LHV / crypto: 170.0 EUR", stdout.getvalue())
        self.assertIn("Lightyear / stock_fund_etf: 255.0 EUR", stdout.getvalue())

    def test_runtime_surface_reports_v56_and_weekly_packet_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v56.0")
        self.assertEqual(
            surface["active_platform_weekly_action_packet_module"],
            "jarvis.runtime.platform_weekly_action_packet",
        )
        self.assertTrue(surface["execution_forbidden"])
        self.assertTrue(surface["manual_approval_required"])


if __name__ == "__main__":
    unittest.main()