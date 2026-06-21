from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.local_server import ROUTES
from jarvis.runtime.portfolio_orbit_view import (
    STATUS_READY,
    build_orbit_assets,
    build_portfolio_orbit_view_result,
    render_portfolio_orbit_view,
)


def _product_fixture() -> dict:
    return {
        "week_plan": {
            "monthly_contribution_eur": 500,
            "emergency_top_up_eur": 75,
            "crypto_eur": 100,
            "etf_fund_eur": 250,
            "individual_stock_eur": 75,
            "selected_instruments": [
                {"lane": "etf_fund", "symbol": "VWCE", "amount_eur": 250},
                {"lane": "crypto", "symbol": "BTC", "amount_eur": 100},
                {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": 75},
            ],
        },
        "manual_holdings": {"holdings_ready": False, "positions": []},
        "data_readiness": {"data_readiness_ready": True, "missing_data": [], "missing_universe": []},
        "live_news_context": {"cache_loaded": False, "source_failures": []},
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


def _finance_fixture() -> dict:
    return {
        "selected_instrument_coverage": [
            {"symbol": "VWCE", "freshness": "ready", "classification": "trusted quote"},
            {"symbol": "BTC", "freshness": "partial_or_unavailable", "classification": "review context"},
            {"symbol": "MSFT", "freshness": "ready", "classification": "trusted quote"},
        ]
    }


class JarvisV163PortfolioOrbitViewTests(unittest.TestCase):
    def test_orbit_assets_normalize_from_manual_plan(self) -> None:
        assets = build_orbit_assets(product_api_result=_product_fixture(), finance_result=_finance_fixture())

        self.assertEqual([asset.symbol for asset in assets], ["VWCE", "BTC", "MSFT"])
        self.assertEqual(assets[0].sleeve, "ETF/Fund Core")
        self.assertEqual(assets[1].sleeve, "Crypto")
        self.assertGreater(assets[0].size, assets[2].size)
        self.assertIn("Prepare Manual Review", assets[0].manual_review_note)

    def test_orbit_view_renders_core_rings_planets_and_detail_panel(self) -> None:
        result = build_portfolio_orbit_view_result(
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
        )
        html = render_portfolio_orbit_view(result)

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.orbit_view_ready)
        for marker in (
            "Portfolio Orbit",
            "orbital-core",
            "orbit-ring",
            "orbit-planet",
            "planet-focus",
            "Selected Instrument",
            "Risk Notes",
            "Manual Review Note",
            "Legend",
            "updateOrbitDetail",
            "portfolio is a solar system",
        ):
            self.assertIn(marker, html)

    def test_orbit_view_uses_safe_language(self) -> None:
        html = render_portfolio_orbit_view(
            build_portfolio_orbit_view_result(
                product_api_result=_product_fixture(),
                finance_result=_finance_fixture(),
            )
        )

        self.assertIn("Prepare Manual Review", html)
        self.assertIn("not instructions", html)
        for forbidden in (
            "Buy now",
            "Sell now",
            "Rebalance Portfolio",
            "Execute trade",
            "Liquidate",
            "order placement",
        ):
            self.assertNotIn(forbidden, html)

    def test_local_server_route_registered(self) -> None:
        self.assertIn("GET /orbit", ROUTES)
        self.assertIn("orbital portfolio visualization", ROUTES["GET /orbit"])

    def test_operator_route_works(self) -> None:
        fixture_result = build_portfolio_orbit_view_result(
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
        )
        with patch("jarvis.runtime.portfolio_orbit_view.build_portfolio_orbit_view_result", return_value=fixture_result):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--portfolio-orbit-view"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V163_0_PORTFOLIO_ORBIT_VIEW_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
