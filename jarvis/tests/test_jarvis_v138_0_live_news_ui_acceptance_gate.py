from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.live_news_ui_acceptance_gate import (
    REQUIRED_UI_MARKERS,
    STATUS_READY,
    build_live_news_ui_acceptance_gate_result,
    format_live_news_ui_acceptance_gate,
)


def _safety_flags(**overrides):
    flags = {
        "trusted_read_only": True,
        "public_free_sources_only": True,
        "credentials_used": False,
        "browser_login": False,
        "auth_scraping": False,
        "recommendation_mutation": False,
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "buy_request_created": False,
        "sell_request_created": False,
        "broker_connection": False,
        "order_created": False,
        "trade_executed": False,
        "auto_approval": False,
        "safety_check_blocked_execution": True,
    }
    flags.update(overrides)
    return flags


def _daily() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V129_0_DAILY_OPERATOR_READY_SAFE",
        daily_operator_ready=True,
        final_acceptance_ready=True,
        blockers=[],
        warnings=[],
        proof={"dashboard_status": "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE"},
    )


def _dashboard() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE",
        dashboard_contract_ready=True,
        blockers=[],
        warnings=[],
        sections={
            "safety": {
                "safety_check_blocked_execution": True,
                "manual_approval_required": True,
                "execution_forbidden": True,
                "broker_connection": False,
                "credentials_used": False,
                "order_created": False,
                "trade_executed": False,
            },
            "manual_holdings": {"title": "Manual Holdings"},
            "news": {"title": "Live News"},
        },
    )


def _post_app() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V134_0_POST_APP_ACCEPTANCE_GATE_READY_SAFE",
        post_app_acceptance_ready=True,
        blockers=[],
        warnings=[],
    )


def _live_news_missing(**overrides) -> SimpleNamespace:
    data = {
        "status": "JARVIS_V135_0_LIVE_NEWS_FETCHER_REVIEW_REQUIRED_SAFE",
        "cache_loaded": False,
        "cache_written": False,
        "blockers": [],
        "warnings": ["live news cache missing; run --live-news-fetch --write-news-cache to create it"],
        "safety_flags": _safety_flags(),
    }
    data.update(overrides)
    return SimpleNamespace(to_dict=lambda: dict(data), **data)


def _html() -> str:
    return "\n".join(
        [
            *REQUIRED_UI_MARKERS,
            "Manual-only safety",
            "No broker connection, credentials, orders, trades, buy/sell requests, or auto-approval",
            "Possible context only",
        ]
    )


class JarvisV138LiveNewsUiAcceptanceGateTests(unittest.TestCase):
    def _patch_ready_dependencies(self, *, html: str | None = None, live_news: SimpleNamespace | None = None):
        return (
            patch("jarvis.runtime.live_news_ui_acceptance_gate.build_daily_operator_result", return_value=_daily()),
            patch("jarvis.runtime.live_news_ui_acceptance_gate.build_dashboard_contract_result", return_value=_dashboard()),
            patch("jarvis.runtime.live_news_ui_acceptance_gate.render_dashboard_html", return_value=html or _html()),
            patch("jarvis.runtime.live_news_ui_acceptance_gate.build_live_news_fetcher_result", return_value=live_news or _live_news_missing()),
            patch("jarvis.runtime.live_news_ui_acceptance_gate.build_post_app_acceptance_gate_result", return_value=_post_app()),
            patch(
                "jarvis.runtime.live_news_ui_acceptance_gate.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_live_news_ui_acceptance_gate_ready_safe_when_news_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_holdings = Path(tmp) / "missing_holdings.local.json"
            missing_news = Path(tmp) / "missing_news.local.json"
            with contextlib.ExitStack() as stack:
                for item in self._patch_ready_dependencies():
                    stack.enter_context(item)
                result = build_live_news_ui_acceptance_gate_result(
                    current_date="2026-06-20",
                    manual_holdings_path=Path(tmp) / "manual_holdings.local.json",
                    missing_holdings_probe_path=missing_holdings,
                    missing_news_probe_path=missing_news,
                )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.live_news_ui_acceptance_ready)
        self.assertTrue(result.daily_operator_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.improved_ui_sections_present)
        self.assertTrue(result.holdings_workflow_installed)
        self.assertTrue(result.missing_holdings_handled_safely)
        self.assertTrue(result.live_news_fetcher_installed)
        self.assertTrue(result.live_news_missing_handled_safely)
        self.assertTrue(result.post_app_acceptance_ready)
        self.assertTrue(result.safety_check_blocks_execution)
        self.assertTrue(result.no_broker_credentials_orders_trades_auto_approval)
        self.assertEqual(result.blockers, [])

    def test_format_lists_required_checks_and_safety_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.ExitStack() as stack:
                for item in self._patch_ready_dependencies():
                    stack.enter_context(item)
                result = build_live_news_ui_acceptance_gate_result(
                    current_date="2026-06-20",
                    missing_holdings_probe_path=Path(tmp) / "missing_holdings.local.json",
                    missing_news_probe_path=Path(tmp) / "missing_news.local.json",
                )
        text = format_live_news_ui_acceptance_gate(result)

        self.assertIn("J.A.R.V.I.S. LIVE NEWS + UI ACCEPTANCE GATE", text)
        self.assertIn("live news + UI acceptance ready: True", text)
        self.assertIn("improved UI sections present: True", text)
        self.assertIn("live news missing/failing handled safely: True", text)
        self.assertIn("no broker/credentials/orders/trades/auto-approval: True", text)
        self.assertIn("- none", text)
        self.assertIn("No broker, credential, buy/sell request, order, trade", text)

    def test_operator_routes_live_news_ui_acceptance_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.ExitStack() as stack:
                for item in self._patch_ready_dependencies():
                    stack.enter_context(item)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = runtime_operator.main(
                        [
                            "--live-news-ui-acceptance-gate",
                            "--current-date",
                            "2026-06-20",
                            "--missing-holdings-probe-path",
                            str(Path(tmp) / "missing_holdings.local.json"),
                            "--missing-news-probe-path",
                            str(Path(tmp) / "missing_news.local.json"),
                        ]
                    )

        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn("J.A.R.V.I.S. LIVE NEWS + UI ACCEPTANCE GATE", text)
        self.assertIn("JARVIS_V138_0_LIVE_NEWS_UI_ACCEPTANCE_GATE_READY_SAFE", text)

    def test_missing_ui_sections_block_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.ExitStack() as stack:
                for item in self._patch_ready_dependencies(html="Manual-only safety"):
                    stack.enter_context(item)
                result = build_live_news_ui_acceptance_gate_result(
                    current_date="2026-06-20",
                    missing_holdings_probe_path=Path(tmp) / "missing_holdings.local.json",
                    missing_news_probe_path=Path(tmp) / "missing_news.local.json",
                )

        self.assertFalse(result.live_news_ui_acceptance_ready)
        self.assertIn("improved_ui_sections_missing", result.blockers)

    def test_execution_safety_flag_failure_blocks_gate(self) -> None:
        unsafe_news = _live_news_missing(safety_flags=_safety_flags(order_created=True))
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.ExitStack() as stack:
                for item in self._patch_ready_dependencies(live_news=unsafe_news):
                    stack.enter_context(item)
                result = build_live_news_ui_acceptance_gate_result(
                    current_date="2026-06-20",
                    missing_holdings_probe_path=Path(tmp) / "missing_holdings.local.json",
                    missing_news_probe_path=Path(tmp) / "missing_news.local.json",
                )

        self.assertFalse(result.live_news_ui_acceptance_ready)
        self.assertIn("live_news_missing_not_handled_safely", result.blockers)
        self.assertIn("execution_safety_flags_not_clear", result.blockers)

    def test_runtime_surface_tracks_live_news_ui_gate_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()
        self.assertEqual(
            surface["active_live_news_ui_acceptance_gate_module"],
            "jarvis.runtime.live_news_ui_acceptance_gate",
        )


if __name__ == "__main__":
    unittest.main()
