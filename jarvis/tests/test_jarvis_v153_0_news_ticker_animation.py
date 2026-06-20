from __future__ import annotations

import unittest

from jarvis.runtime.dashboard_contract import DashboardContractResult, render_dashboard_html


def _sections(top_headlines: list[dict[str, object]]) -> dict[str, object]:
    return {
        "status": {"dashboard_ready": True, "chat_ready": True, "voice_ready": True, "audit_verdict": "ready", "blockers": []},
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
            "etf_candidates": 1,
            "stock_candidates": 1,
        },
        "news": {
            "cache_loaded": bool(top_headlines),
            "headline_count": len(top_headlines),
            "source_failures": [],
            "top_headlines": top_headlines,
        },
        "finance_intelligence": {
            "data_trust_summary": {"trusted_records": 3, "partial_records": 0},
            "selected_instrument_coverage": [],
            "market_movement_summary": "Fresh public quote context is available.",
            "fx_summary": {"conversion_available": False},
        },
        "manual_holdings": {
            "file_exists": False,
            "holdings_ready": False,
            "positions_count": 0,
            "confirmed_positions_count": 0,
            "total_cost_basis_eur": 0,
            "total_market_value_eur": None,
            "total_market_value_available": False,
            "positions": [],
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
    }


def _result(top_headlines: list[dict[str, object]]) -> DashboardContractResult:
    return DashboardContractResult(
        status="JARVIS_V153_TEST_READY_SAFE",
        current_date="2026-06-21",
        dashboard_contract_ready=True,
        dashboard_html_written=False,
        dashboard_path="outputs/dashboard_latest.html",
        backend_ready=True,
        product_api_ready=True,
        full_audit_ready=True,
        product_recommendations_allowed=True,
        manual_only=True,
        sections=_sections(top_headlines),
        warnings=[],
        blockers=[],
        report_written=False,
        report_path="outputs/dashboard_contract_latest.json",
    )


class JarvisV1530NewsTickerAnimationTests(unittest.TestCase):
    def test_market_headlines_render_as_scrolling_ticker(self) -> None:
        html = render_dashboard_html(
            _result(
                [
                    {
                        "title": "BTC liquidity improves",
                        "source": "public source",
                        "freshness_status": "fresh",
                        "url": "https://example.test/btc",
                        "entity_tags": ["BTC"],
                        "lane_tags": ["crypto"],
                    },
                    {
                        "title": "MSFT cloud revenue watched",
                        "source": "public source",
                        "freshness_status": "fresh",
                        "url": "https://example.test/msft",
                        "entity_tags": ["MSFT"],
                        "lane_tags": ["individual_stock"],
                    },
                ]
            )
        )

        self.assertIn("Market Headlines", html)
        self.assertIn("headline-ticker", html)
        self.assertIn("headline-track", html)
        self.assertIn("headline-chip", html)
        self.assertIn("@keyframes ticker-scroll", html)
        self.assertIn("animation:ticker-scroll", html)
        self.assertEqual(html.count("BTC liquidity improves"), 2)
        self.assertEqual(html.count("MSFT cloud revenue watched"), 2)
        self.assertIn(">BTC<", html)
        self.assertIn(">MSFT<", html)

    def test_empty_news_state_is_calm_and_non_advisory(self) -> None:
        html = render_dashboard_html(_result([]))

        self.assertIn("headline-ticker-empty", html)
        self.assertIn("Headlines are quiet", html)
        self.assertIn("not blocking today's manual plan", html)
        self.assertIn("never an action signal", html)
        self.assertIn("never recommend action from headline alone", html)
        self.assertNotIn("buy because", html.lower())
        self.assertNotIn("sell because", html.lower())


if __name__ == "__main__":
    unittest.main()
