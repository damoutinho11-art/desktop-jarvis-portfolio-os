from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.allocation_strategy_audit import build_allocation_strategy_data_coverage_audit_result
from jarvis.runtime.dynamic_target_policy import (
    STATUS_REVIEW_REQUIRED,
    build_dynamic_target_policy_result,
    format_dynamic_target_policy,
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


class JarvisV540DynamicTargetPolicyEngineTests(unittest.TestCase):
    def test_dynamic_target_policy_uses_real_expenses_and_500_monthly_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_dynamic_target_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.minimum_emergency_target_eur, 3600.0)
        self.assertEqual(result.ideal_emergency_target_eur, 7200.0)
        self.assertEqual(result.suggested_monthly_emergency_top_up_eur, 75.0)
        self.assertEqual(result.suggested_monthly_investment_after_emergency_eur, 425.0)
        self.assertTrue(result.target_policy_data_gate_covered)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_current_crypto_under_target_floor_routes_capped_catch_up_contribution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_dynamic_target_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        targets = {item.lane: item.amount_eur for item in result.proposed_contribution_targets}
        self.assertEqual(targets["crypto"], 170.0)
        self.assertEqual(targets["stock_fund_etf"], 255.0)
        self.assertEqual(targets["individual_stock"], 0.0)
        self.assertIn("CRYPTO_UNDER_TARGET_FLOOR_BUT_CAPPED", result.policy_flags)

    def test_missing_expenses_blocks_policy_instead_of_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_dynamic_target_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=None,
            )

        self.assertIn("monthly_expenses_required_for_dynamic_target_policy", result.blockers)
        self.assertFalse(result.allocation_mutation)
        self.assertTrue(result.no_trades_executed)

    def test_format_shows_targets_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_dynamic_target_policy_result(
                current_date="2026-06-17",
                snapshot_path=snapshot_path,
                monthly_contribution_eur=500,
                monthly_expenses_eur=1200,
            )

        output = format_dynamic_target_policy(result)
        self.assertIn("J.A.R.V.I.S. DYNAMIC TARGET POLICY ENGINE", output)
        self.assertIn("suggested monthly investment after emergency EUR: 425.0", output)
        self.assertIn("crypto: 170.0 EUR", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_dynamic_target_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = runtime_operator.main(
                    [
                        "--dynamic-target-policy",
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
        self.assertIn("DYNAMIC TARGET POLICY ENGINE", stdout.getvalue())
        self.assertIn("crypto: 170.0 EUR", stdout.getvalue())

    def test_runtime_surface_reports_v54_and_dynamic_target_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v54.0")
        self.assertEqual(
            surface["active_dynamic_target_policy_module"],
            "jarvis.runtime.dynamic_target_policy",
        )
        self.assertTrue(surface["execution_forbidden"])
        self.assertTrue(surface["manual_approval_required"])

    def test_allocation_audit_now_marks_dynamic_target_policy_covered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            _write_snapshot(snapshot_path)

            result = build_allocation_strategy_data_coverage_audit_result(
                current_date="2026-06-17",
                manual_portfolio_snapshot_path=snapshot_path,
                upstream_result=None,
            )

        coverage = {item.key: item.available for item in result.coverage_items}
        self.assertTrue(coverage["dynamic_target_policy"])
        self.assertNotIn("dynamic_target_policy", result.missing_full_allocation_required_keys)
        self.assertIn("correlation_risk_model", result.missing_full_allocation_required_keys)


if __name__ == "__main__":
    unittest.main()