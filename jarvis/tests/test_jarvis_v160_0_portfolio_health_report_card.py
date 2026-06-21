from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.portfolio_health_report_card import (
    STATUS_READY,
    build_portfolio_health_report_card_result,
    format_portfolio_health_report_card,
)


def _product_fixture(*, holdings_ready: bool = True) -> dict:
    holdings = {
        "holdings_ready": holdings_ready,
        "positions": [
            {"symbol": "MSFT", "confirmed": True, "cost_basis_eur": 1000, "market_value_eur": 1200},
            {"symbol": "VWCE", "confirmed": True, "cost_basis_eur": 900, "market_value_eur": 950},
            {"symbol": "BTC", "confirmed": True, "cost_basis_eur": 300, "market_value_eur": 400},
            {"symbol": "ETH", "confirmed": True, "cost_basis_eur": 200, "market_value_eur": 250},
        ] if holdings_ready else [],
    }
    return {
        "week_plan": {
            "monthly_contribution_eur": 500,
            "emergency_top_up_eur": 0,
            "crypto_eur": 100,
            "etf_fund_eur": 250,
            "individual_stock_eur": 150,
            "selected_instruments": [
                {"lane": "crypto", "symbol": "BTC"},
                {"lane": "etf_fund", "symbol": "VWCE"},
                {"lane": "individual_stock", "symbol": "MSFT"},
            ],
        },
        "manual_holdings": holdings,
        "data_readiness": {
            "data_readiness_ready": True,
            "missing_data": [],
            "missing_universe": [],
        },
        "live_news_context": {"cache_loaded": True, "source_failures": []},
        "product_recommendations_allowed": True,
        "safety_status": {
            "safety_check_blocked_execution": True,
            "manual_approval_required": True,
            "execution_forbidden": True,
            "allocation_mutation": False,
            "approval_ticket_mutation": False,
            "buy_request_created": False,
            "broker_connection": False,
            "credentials_used": False,
            "private_account_data_ingestion": False,
            "order_created": False,
            "trade_executed": False,
        },
        "warnings": [],
        "blockers": [],
    }


class JarvisV160PortfolioHealthReportCardTests(unittest.TestCase):
    def test_report_card_returns_ready_when_existing_system_ready(self) -> None:
        result = build_portfolio_health_report_card_result(product_api_result=_product_fixture())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.report_card_ready)
        self.assertEqual(result.overall_status, "ready")
        self.assertGreaterEqual(result.readiness_score, 75)

    def test_missing_holdings_warning_not_blocker(self) -> None:
        result = build_portfolio_health_report_card_result(product_api_result=_product_fixture(holdings_ready=False))

        self.assertTrue(result.report_card_ready)
        self.assertEqual(result.blockers, [])
        self.assertIn("manual holdings missing or not confirmed; this is a warning, not a blocker", result.warnings)
        self.assertIn("enter or confirm manual holdings when available", result.review_notes)

    def test_score_components_are_explainable(self) -> None:
        result = build_portfolio_health_report_card_result(product_api_result=_product_fixture())

        self.assertIn("diversification_score", result.score_components)
        self.assertIn("data_freshness_score", result.score_components)
        for item in result.score_components.values():
            self.assertIn("score", item)
            self.assertIn("weight", item)
            self.assertIn("basis", item)

    def test_no_recommendation_trading_language_in_notes(self) -> None:
        result = build_portfolio_health_report_card_result(product_api_result=_product_fixture(holdings_ready=False))
        text = " ".join(result.top_strengths + result.review_notes).lower()
        for forbidden in ("buy", "sell", "order", "trade", "broker", "credential", "api_key"):
            self.assertNotIn(forbidden, text)

    def test_safety_invariants_true(self) -> None:
        result = build_portfolio_health_report_card_result(product_api_result=_product_fixture())
        safety = result.safety_status

        self.assertTrue(safety["safety_ready"])
        self.assertTrue(safety["manual_only"])
        self.assertTrue(safety["execution_forbidden"])
        self.assertFalse(safety["broker_connection_enabled"])
        self.assertFalse(safety["credentials_required"])
        self.assertFalse(safety["request_creation_enabled"])
        self.assertFalse(safety["external_instruction_created"])
        self.assertFalse(safety["external_completion_recorded"])
        self.assertFalse(safety["auto_approval_enabled"])
        self.assertFalse(safety["allocation_mutation"])
        self.assertFalse(safety["approval_mutation"])

    def test_format_lists_sections(self) -> None:
        text = format_portfolio_health_report_card(build_portfolio_health_report_card_result(product_api_result=_product_fixture()))

        self.assertIn("J.A.R.V.I.S. PORTFOLIO HEALTH REPORT CARD", text)
        self.assertIn("readiness score:", text)
        self.assertIn("SCORE COMPONENTS:", text)
        self.assertIn("SAFETY STATUS:", text)

    def test_operator_route_works(self) -> None:
        fixture_result = build_portfolio_health_report_card_result(product_api_result=_product_fixture())
        with patch(
            "jarvis.runtime.portfolio_health_report_card.build_portfolio_health_report_card_result",
            return_value=fixture_result,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--portfolio-health-report-card"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V160_0_PORTFOLIO_HEALTH_REPORT_CARD_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
