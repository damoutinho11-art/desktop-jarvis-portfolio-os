from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.portfolio_exposure_audit import (
    STATUS_REVIEW_REQUIRED,
    build_portfolio_exposure_dynamic_emergency_fund_audit_result,
    format_portfolio_exposure_dynamic_emergency_fund_audit,
)


def _snapshot() -> dict:
    return {
        "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
        "snapshot_date": "2026-06-17",
        "is_template": False,
        "brokerless_manual_snapshot": True,
        "cash_eur": 1054.35,
        "emergency_fund_reserved_eur": 3263.07,
        "totals": {
            "visible_portfolio_excluding_emergency_eur": 2210.73,
            "visible_total_including_emergency_eur": 5473.80,
        },
        "holdings": [
            {"lane": "cash", "asset_name": "EUR cash", "instrument_id": "eur_cash", "market_value_eur": 1054.35},
            {"lane": "cash_reserve", "asset_name": "Emergency fund", "instrument_id": "emergency", "market_value_eur": 3263.07},
            {"lane": "crypto", "asset_name": "Bitcoin", "instrument_id": "bitcoin_btc", "market_value_eur": 19.78},
            {"lane": "stock_fund_etf", "asset_name": "ISHARES MSCI EMERGING MKTS", "instrument_id": "em", "market_value_eur": 373.55},
            {"lane": "stock_fund_etf", "asset_name": "LHV Euro Bond Fund", "instrument_id": "bond", "market_value_eur": 0.15},
            {"lane": "stock_fund_etf", "asset_name": "LHV World Equities Fund", "instrument_id": "world", "market_value_eur": 1.54},
            {"lane": "stock_fund_etf", "asset_name": "db x-trackers China CSI300 ETF", "instrument_id": "china", "market_value_eur": 128.41},
            {"lane": "stock_fund_etf", "asset_name": "iShares Core S&P 500 UCITS ETF", "instrument_id": "sp500", "market_value_eur": 632.95},
        ],
        "cost_basis": {"sp500": 573.79},
    }


class JarvisV530PortfolioExposureDynamicEmergencyFundAuditTests(unittest.TestCase):
    def test_without_expenses_jarvis_refuses_to_decide_emergency_vs_invest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
                monthly_contribution_eur=400.0,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.emergency_fund_decision, "EXPENSES_REQUIRED_FOR_DYNAMIC_EMERGENCY_POLICY")
            self.assertIsNone(result.suggested_monthly_emergency_top_up_eur)
            self.assertIsNone(result.suggested_monthly_investment_after_emergency_eur)
            self.assertFalse(result.buy_request_created)

    def test_expenses_drive_dynamic_targets_not_fixed_5000(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
                monthly_contribution_eur=400.0,
                monthly_expenses_eur=1000.0,
                minimum_emergency_months=3.0,
                ideal_emergency_months=6.0,
            )

            self.assertEqual(result.minimum_emergency_target_eur, 3000.0)
            self.assertEqual(result.ideal_emergency_target_eur, 6000.0)
            self.assertEqual(result.emergency_months_covered, 3.26)
            self.assertEqual(result.emergency_fund_decision, "MINIMUM_EMERGENCY_FUND_MET_IDEAL_NOT_MET")
            self.assertEqual(result.suggested_monthly_emergency_top_up_eur, 75.0)
            self.assertEqual(result.suggested_monthly_investment_after_emergency_eur, 325.0)
            self.assertTrue(result.no_trades_executed)

    def test_low_emergency_months_prioritizes_minimum_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = _snapshot()
            snapshot["emergency_fund_reserved_eur"] = 500.0
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
                monthly_contribution_eur=400.0,
                monthly_expenses_eur=1000.0,
            )

            self.assertEqual(result.emergency_fund_decision, "BELOW_MINIMUM_EMERGENCY_FUND")
            self.assertEqual(result.suggested_monthly_emergency_top_up_eur, 400.0)
            self.assertEqual(result.suggested_monthly_investment_after_emergency_eur, 0.0)

    def test_lane_exposures_and_position_flags_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
                monthly_contribution_eur=400.0,
                monthly_expenses_eur=1000.0,
            )

            lanes = {lane.lane: lane for lane in result.lane_exposures}
            self.assertIn("cash_reserve", lanes)
            self.assertIn("crypto", lanes)
            self.assertIn("stock_fund_etf", lanes)
            flag_types = {flag.flag_type for flag in result.position_flags}
            self.assertIn("TINY_RESIDUAL_POSITION", flag_types)
            self.assertIn("TOP_HOLDING_CONCENTRATION_REVIEW", flag_types)

    def test_missing_snapshot_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
            )

            self.assertIn("manual portfolio snapshot missing or unreadable.", result.blockers)
            self.assertFalse(result.snapshot_ready)

    def test_format_contains_dynamic_emergency_and_safety_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")

            result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
                current_date="2026-06-17",
                snapshot_path=path,
                monthly_contribution_eur=400.0,
                monthly_expenses_eur=1000.0,
            )
            output = format_portfolio_exposure_dynamic_emergency_fund_audit(result)

            self.assertIn("DYNAMIC EMERGENCY FUND AUDIT", output)
            self.assertIn("target basis: monthly expenses, not fixed EUR", output)
            self.assertIn("suggested monthly emergency top-up EUR", output)
            self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_portfolio_exposure_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = runtime_operator.main(
                    [
                        "--portfolio-exposure-audit",
                        "--manual-portfolio-snapshot-path",
                        str(path),
                        "--current-date",
                        "2026-06-17",
                        "--monthly-contribution-eur",
                        "400",
                        "--monthly-expenses-eur",
                        "1000",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn("DYNAMIC EMERGENCY FUND AUDIT", buffer.getvalue())

    def test_runtime_surface_reports_v53_and_exposure_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v53.0")
        self.assertEqual(
            surface["active_portfolio_exposure_audit_module"],
            "jarvis.runtime.portfolio_exposure_audit",
        )


if __name__ == "__main__":
    unittest.main()