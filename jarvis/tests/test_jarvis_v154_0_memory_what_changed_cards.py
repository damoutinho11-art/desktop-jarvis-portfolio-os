from __future__ import annotations

import unittest
from unittest.mock import patch

from jarvis.runtime.dashboard_contract import DashboardContractResult, _build_sections, render_dashboard_html
from jarvis.runtime.local_server import render_chat_page


def _product() -> dict[str, object]:
    return {
        "dashboard_ready": True,
        "chat_ready": True,
        "voice_ready": True,
        "week_plan": {
            "monthly_contribution_eur": 500,
            "emergency_top_up_eur": 75,
            "crypto_eur": 100,
            "etf_fund_eur": 275,
            "individual_stock_eur": 50,
            "selected_instruments": [
                {"lane": "crypto", "symbol": "BTC", "amount_eur": 100},
                {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": 50},
            ],
        },
        "data_readiness": {
            "data_readiness_ready": True,
            "missing_data": [],
            "missing_universe": [],
            "crypto_candidate_count": 2,
            "etf_candidate_count": 1,
            "stock_candidate_count": 1,
        },
        "news_coverage": {"news_coverage_ready": True},
        "live_news_context": {
            "cache_loaded": False,
            "usable_count": 0,
            "source_failures": [],
            "top_headlines": [],
        },
        "manual_holdings": {
            "file_exists": False,
            "holdings_ready": False,
            "positions_count": 0,
            "confirmed_positions_count": 0,
            "total_cost_basis_eur": 0,
            "total_market_value_available": False,
            "positions": [],
        },
        "safety_status": {
            "safety_check_blocked_execution": True,
            "manual_approval_required": True,
            "execution_forbidden": True,
            "broker_connection": False,
            "credentials_used": False,
            "order_created": False,
            "trade_executed": False,
        },
        "blockers": [],
        "warnings": [],
    }


def _audit() -> dict[str, object]:
    return {
        "audit_verdict": "ready",
        "blockers": [],
        "formula_invariants_ready": True,
        "data_readiness_ready": True,
        "news_coverage_ready": True,
        "safety_ready": True,
        "speed_ready": True,
        "warnings": [],
    }


def _finance() -> dict[str, object]:
    return {
        "data_trust_summary": {"trusted_records": 3, "partial_records": 0},
        "selected_instrument_coverage": [],
        "market_movement_summary": "Fresh public quote context is available.",
        "fx_summary": {"conversion_available": False},
    }


def _previous_snapshot() -> dict[str, object]:
    return {
        "dashboard_ready_label": "READY FOR MANUAL USE",
        "manual_plan_summary": "emergency EUR 75.00, crypto EUR 90.00, ETF/fund EUR 285.00, stock EUR 50.00",
        "selected_instruments_summary": "BTC EUR 90.00, MSFT EUR 50.00",
        "market_movement_summary": "Use the dashboard Market Movement section; source freshness must be reviewed manually.",
        "news_headline_summary": "News unavailable - not blocking today's manual plan.",
        "holdings_status_summary": "Holdings not entered yet; this is a warning, not a blocker.",
        "safety_status": {"manual_only": True},
        "blockers_count": 0,
        "warnings_count": 0,
    }


def _result(sections: dict[str, object]) -> DashboardContractResult:
    return DashboardContractResult(
        status="JARVIS_V154_TEST_READY_SAFE",
        current_date="2026-06-21",
        dashboard_contract_ready=True,
        dashboard_html_written=False,
        dashboard_path="outputs/dashboard_latest.html",
        backend_ready=True,
        product_api_ready=True,
        full_audit_ready=True,
        product_recommendations_allowed=True,
        manual_only=True,
        sections=sections,
        warnings=[],
        blockers=[],
        report_written=False,
        report_path="outputs/dashboard_contract_latest.json",
    )


class JarvisV1540MemoryWhatChangedCardsTests(unittest.TestCase):
    def _patch_safety(self):
        return patch(
            "jarvis.runtime.what_changed_since_last_time.build_safety_check_console_output",
            return_value="BLOCKED: dry run. No execution action was taken.",
        )

    def test_first_run_memory_cards_are_calm(self) -> None:
        with patch("jarvis.runtime.dashboard_contract.load_session_memory", return_value=None), \
             patch("jarvis.runtime.what_changed_since_last_time.load_session_memory", return_value=None), \
             self._patch_safety():
            sections = _build_sections(_product(), _audit(), _finance(), current_date="2026-06-21")
            html = render_dashboard_html(_result(sections))

        self.assertTrue(sections["session_memory"]["first_run"])
        self.assertTrue(sections["what_changed"]["first_run"])
        self.assertIn("Last Session", html)
        self.assertIn("What Changed Since Last Time", html)
        self.assertIn("First run", html)
        self.assertIn("no previous J.A.R.V.I.S. session memory exists yet", html)
        self.assertIn("No previous safe snapshot exists yet", html)

    def test_dashboard_surfaces_last_session_and_changes(self) -> None:
        previous = _previous_snapshot()
        with patch("jarvis.runtime.dashboard_contract.load_session_memory", return_value=previous), \
             patch("jarvis.runtime.what_changed_since_last_time.load_session_memory", return_value=previous), \
             self._patch_safety():
            sections = _build_sections(_product(), _audit(), _finance(), current_date="2026-06-21")
            html = render_dashboard_html(_result(sections))

        self.assertFalse(sections["session_memory"]["first_run"])
        self.assertFalse(sections["what_changed"]["first_run"])
        self.assertIn("Memory found", html)
        self.assertIn("Comparison ready", html)
        self.assertIn("Last memory: READY FOR MANUAL USE", html)
        self.assertIn("manual plan changed", html)
        self.assertIn("safety remains manual-only", html)
        self.assertIn("Safe derived summaries only", html)

    def test_chat_has_what_changed_preset(self) -> None:
        html = render_chat_page()

        self.assertIn("What changed since last time?", html)
        self.assertIn('data-question="What changed since last time?"', html)

    def test_memory_cards_preserve_safety_invariant(self) -> None:
        previous = _previous_snapshot()
        with patch("jarvis.runtime.dashboard_contract.load_session_memory", return_value=previous), \
             patch("jarvis.runtime.what_changed_since_last_time.load_session_memory", return_value=previous), \
             self._patch_safety():
            html = render_dashboard_html(_result(_build_sections(_product(), _audit(), _finance())))

        lowered = html.lower()
        for phrase in ("broker login", "credentials required", "order ticket", "trade executed: true", "auto-approval enabled"):
            self.assertNotIn(phrase, lowered)
        self.assertIn("no broker", lowered)
        self.assertIn("no credentials", lowered)
        self.assertIn("no orders", lowered)
        self.assertIn("no trades", lowered)


if __name__ == "__main__":
    unittest.main()
