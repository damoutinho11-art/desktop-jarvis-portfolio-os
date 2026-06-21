from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.local_server import ROUTES
from jarvis.runtime.orbital_instrument_detail_panel import (
    STATUS_READY,
    build_orbital_instrument_detail_result,
    render_orbital_instrument_detail_panel,
)
from jarvis.runtime.portfolio_orbit_view import build_portfolio_orbit_view_result, render_portfolio_orbit_view


def _product_fixture() -> dict:
    return {
        "week_plan": {
            "selected_instruments": [
                {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": 75},
            ]
        },
        "live_news_context": {
            "top_headlines": [
                {
                    "title": "MSFT cloud context update",
                    "source": "fixture",
                    "freshness_status": "fresh",
                    "entity_tags": ["MSFT"],
                    "url": "https://example.test/msft",
                }
            ]
        },
        "manual_holdings": {"holdings_ready": False, "positions": []},
        "data_readiness": {"data_readiness_ready": True, "missing_data": [], "missing_universe": []},
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
            {
                "symbol": "MSFT",
                "freshness": "ready",
                "classification": "trusted quote",
                "source": "fixture finance core",
                "source_as_of": "2026-06-21",
            }
        ]
    }


def _universe_fixture() -> dict:
    return {
        "equities": [
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "asset_type": "equity",
                "exchange": "NASDAQ",
                "country": "United States",
                "currency": "USD",
                "sector": "Software",
            }
        ]
    }


def _fundamentals_fixture() -> dict:
    return {
        "symbols": {
            "MSFT": {
                "profitability": {"gross_margin": 0.69},
                "solvency": {"debt_to_equity": 0.28},
                "valuation": {"price_to_earnings": 34.2},
                "cash_flow_quality": {"free_cash_flow_margin": 0.31},
            }
        }
    }


class JarvisV164OrbitalInstrumentDetailPanelTests(unittest.TestCase):
    def test_detail_result_integrates_metadata_fundamentals_and_role(self) -> None:
        result = build_orbital_instrument_detail_result(
            symbol="MSFT",
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
            universe_fixture=_universe_fixture(),
            fundamentals_fixture=_fundamentals_fixture(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.detail_panel_ready)
        self.assertEqual(result.identity_metadata["name"], "Microsoft Corporation")
        self.assertEqual(result.identity_metadata["exchange"], "NASDAQ")
        self.assertEqual(result.fundamental_context["profitability"]["gross_margin"], 0.69)
        self.assertTrue(result.portfolio_role["appears_in_plan"])
        self.assertEqual(result.news_context[0]["title"], "MSFT cloud context update")
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)

    def test_rendered_panel_contains_target_sections(self) -> None:
        result = build_orbital_instrument_detail_result(
            symbol="MSFT",
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
            universe_fixture=_universe_fixture(),
            fundamentals_fixture=_fundamentals_fixture(),
        )
        html = render_orbital_instrument_detail_panel(result)

        for marker in (
            "Instrument Detail",
            "Identity and Metadata",
            "Price / Movement / Freshness",
            "Fundamental Context",
            "Risk Notes",
            "News Context",
            "Why It Appears",
            "Manual Checklist",
            "Evidence Summary",
            "manual review only",
        ):
            self.assertIn(marker, html)

    def test_orbit_view_links_to_detail_panel(self) -> None:
        orbit = build_portfolio_orbit_view_result(
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
        )
        html = render_portfolio_orbit_view(orbit)

        self.assertIn("Open Detail Panel", html)
        self.assertIn("/instruments?symbol=", html)
        self.assertIn("detailLink", html)

    def test_safe_language_and_route_registration(self) -> None:
        result = build_orbital_instrument_detail_result(
            symbol="MSFT",
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
            universe_fixture=_universe_fixture(),
            fundamentals_fixture=_fundamentals_fixture(),
        )
        html = render_orbital_instrument_detail_panel(result)

        self.assertIn("GET /instruments", ROUTES)
        self.assertIn("instrument detail panel", ROUTES["GET /instruments"])
        self.assertIn("Manual Checklist", html)
        for forbidden in (
            "Buy now",
            "Sell now",
            "Rebalance Portfolio",
            "Execute trade",
            "Liquidate",
            "Recommendation queued for execution",
        ):
            self.assertNotIn(forbidden, html)

    def test_operator_route_works(self) -> None:
        fixture_result = build_orbital_instrument_detail_result(
            symbol="MSFT",
            product_api_result=_product_fixture(),
            finance_result=_finance_fixture(),
            universe_fixture=_universe_fixture(),
            fundamentals_fixture=_fundamentals_fixture(),
        )
        with patch(
            "jarvis.runtime.orbital_instrument_detail_panel.build_orbital_instrument_detail_result",
            return_value=fixture_result,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--orbital-instrument-detail", "--symbol", "MSFT"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V164_0_ORBITAL_INSTRUMENT_DETAIL_PANEL_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
