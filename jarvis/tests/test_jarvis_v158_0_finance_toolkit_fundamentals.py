from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.finance_toolkit_fundamentals import (
    STATUS_READY,
    build_finance_toolkit_fundamentals_result,
    normalize_fixture_fundamentals,
)


FIXTURE_FUNDAMENTALS = {
    "symbols": {
        "MSFT": {
            "profitability": {"gross_margin": 0.69, "return_on_equity": 0.35},
            "solvency": {"debt_to_equity": 0.28, "interest_coverage": 40.1},
            "valuation": {"price_to_earnings": 34.2},
            "growth": {"revenue_growth": 0.12},
            "cash_flow_quality": {"free_cash_flow_margin": 0.31},
            "income_statement_summary": {"revenue": 245000000000},
            "balance_sheet_summary": {"cash": 80000000000},
            "ratio_summary": {"current_ratio": 1.2},
        }
    }
}


class JarvisV158FinanceToolkitFundamentalsTests(unittest.TestCase):
    def test_missing_dependency_returns_safe_warning(self) -> None:
        with patch("jarvis.runtime.finance_toolkit_fundamentals._load_financetoolkit_module", return_value=None):
            result = build_finance_toolkit_fundamentals_result(symbols=["MSFT"])

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.dependency_available)
        self.assertFalse(result.fundamentals_ready)
        self.assertEqual(result.blockers, [])
        self.assertIn("optional dependency not installed", result.warnings)
        self.assertIn("selected symbols have no normalized fundamental context yet", result.risk_notes)

    def test_fixture_fundamentals_normalize(self) -> None:
        result = build_finance_toolkit_fundamentals_result(fixture_fundamentals=FIXTURE_FUNDAMENTALS)

        self.assertTrue(result.dependency_available)
        self.assertTrue(result.fundamentals_ready)
        self.assertEqual(result.selected_symbols, ["MSFT"])
        context = result.fundamental_context["MSFT"]
        self.assertEqual(context["profitability"]["gross_margin"], 0.69)
        self.assertEqual(context["solvency"]["interest_coverage"], 40.1)
        self.assertEqual(context["income_statement_summary"]["revenue"], 245000000000)

    def test_risk_and_fundamental_notes_generated(self) -> None:
        sparse = {"symbols": {"ASML": {"profitability": {"gross_margin": 0.51}}}}
        result = build_finance_toolkit_fundamentals_result(fixture_fundamentals=sparse)

        self.assertIn("ASML: fundamental context available for profitability", result.fundamental_notes)
        self.assertIn("ASML: cash flow quality context missing", result.risk_notes)
        self.assertIn("ASML: solvency context missing", result.risk_notes)

    def test_no_buy_sell_order_trade_fields(self) -> None:
        records = normalize_fixture_fundamentals(FIXTURE_FUNDAMENTALS)
        result = build_finance_toolkit_fundamentals_result(fixture_fundamentals=FIXTURE_FUNDAMENTALS).to_dict()
        text = str(result).lower() + str(records).lower()
        for forbidden in ("buy", "sell", "order", "trade", "broker", "credential", "password", "api_key"):
            self.assertNotIn(forbidden, text)

    def test_operator_route_works(self) -> None:
        fixture_result = build_finance_toolkit_fundamentals_result(fixture_fundamentals=FIXTURE_FUNDAMENTALS)
        with patch(
            "jarvis.runtime.finance_toolkit_fundamentals.build_finance_toolkit_fundamentals_result",
            return_value=fixture_result,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--finance-toolkit-fundamentals", "--symbols", "MSFT"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V158_0_FINANCETOOLKIT_FUNDAMENTAL_ANALYSIS_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
