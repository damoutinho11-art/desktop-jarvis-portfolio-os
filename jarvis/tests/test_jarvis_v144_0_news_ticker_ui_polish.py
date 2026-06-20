from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.runtime.dashboard_calm_ui_freeze_gate import REQUIRED_MARKERS
from jarvis.runtime.dashboard_contract import render_dashboard_html


def _dashboard(headlines=None) -> SimpleNamespace:
    return SimpleNamespace(
        current_date="2026-06-20",
        dashboard_contract_ready=True,
        blockers=[],
        sections={
            "status": {"dashboard_ready": True},
            "week_plan": {
                "monthly_contribution_eur": 500,
                "emergency_top_up_eur": 75,
                "crypto_eur": 100,
                "etf_fund_eur": 275,
                "individual_stock_eur": 50,
                "selected_instruments": [],
            },
            "data": {
                "data_readiness_ready": True,
                "missing_data": [],
                "missing_universe": [],
                "crypto_candidates": 2,
                "etf_candidates": 2,
                "stock_candidates": 1,
            },
            "news": {
                "cache_loaded": bool(headlines),
                "headline_count": len(headlines or []),
                "source_failures": [],
                "top_headlines": headlines or [],
            },
            "finance_intelligence": {
                "data_trust_summary": {"trusted_records": 2, "partial_records": 0},
                "selected_instrument_coverage": [],
                "market_movement_summary": "Known local movement from cache.",
                "fx_summary": {"conversion_available": False},
            },
            "manual_holdings": {
                "file_exists": False,
                "holdings_ready": False,
                "positions_count": 0,
                "confirmed_positions_count": 0,
                "positions": [],
                "total_cost_basis_eur": 0,
                "total_market_value_available": False,
            },
            "safety": {
                "safety_check_blocked_execution": True,
                "manual_approval_required": True,
                "execution_forbidden": True,
                "broker_connection": False,
                "credentials_used": False,
                "order_created": False,
                "trade_executed": False,
            },
            "audit": {
                "formula_invariants_ready": True,
                "data_readiness_ready": True,
                "news_coverage_ready": True,
                "safety_ready": True,
                "speed_ready": True,
            },
        },
    )


class JarvisV144NewsTickerUiPolishTests(unittest.TestCase):
    def test_market_headlines_ribbon_shows_tagged_headline_chips(self) -> None:
        page = render_dashboard_html(
            _dashboard(
                [
                    {
                        "title": "Bitcoin headline context for crypto market",
                        "source": "Fixture public RSS",
                        "freshness_status": "fresh",
                        "entity_tags": ["BTC"],
                        "lane_tags": ["crypto"],
                        "url": "https://example.test/btc",
                    },
                    {
                        "title": "Microsoft headline context",
                        "source": "Microsoft public blog",
                        "freshness_status": "recent",
                        "entity_tags": ["MSFT"],
                        "lane_tags": ["individual_stock"],
                        "url": "https://example.test/msft",
                    },
                ]
            )
        )

        self.assertIn("Market Headlines", page)
        self.assertIn("headline-tag", page)
        self.assertIn(">BTC<", page)
        self.assertIn(">MSFT<", page)
        self.assertIn("Bitcoin headline context", page)
        self.assertIn("Microsoft headline context", page)
        self.assertIn("never recommend action from headline alone", page)
        self.assertNotIn("buy because news", page.lower())
        self.assertNotIn("sell because news", page.lower())

    def test_missing_news_message_is_calm_and_non_blocking(self) -> None:
        page = render_dashboard_html(_dashboard())

        self.assertIn("Market Headlines", page)
        self.assertIn("News unavailable &mdash; not blocking today's manual plan.", page)
        self.assertIn("Public headlines are optional context", page)
        self.assertNotIn("stack trace", page.lower())
        self.assertNotIn("{&quot;", page)

    def test_calm_ui_freeze_gate_requires_market_headlines_marker(self) -> None:
        self.assertIn("Market Headlines", REQUIRED_MARKERS)


if __name__ == "__main__":
    unittest.main()
