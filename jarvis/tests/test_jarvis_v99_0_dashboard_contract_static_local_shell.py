from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from jarvis.runtime import operator
from jarvis.runtime.dashboard_contract import (
    STATUS_READY,
    build_dashboard_contract_result,
    format_dashboard_contract,
    render_dashboard_html,
)


class JarvisV990DashboardContractStaticLocalShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_dashboard_contract_result(current_date="2026-06-18")

    def test_dashboard_contract_ready(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertTrue(self.result.dashboard_contract_ready)
        self.assertTrue(self.result.backend_ready)
        self.assertTrue(self.result.product_api_ready)
        self.assertTrue(self.result.full_audit_ready)
        self.assertTrue(self.result.product_recommendations_allowed)
        self.assertTrue(self.result.manual_only)
        self.assertEqual(self.result.blockers, [])

    def test_sections_are_dashboard_ready(self) -> None:
        sections = self.result.sections
        for key in ["status", "week_plan", "data", "news", "safety", "audit"]:
            self.assertIn(key, sections)

        self.assertTrue(sections["status"]["dashboard_ready"])
        self.assertTrue(sections["status"]["chat_ready"])
        self.assertTrue(sections["status"]["voice_ready"])
        self.assertEqual(sections["week_plan"]["monthly_contribution_eur"], 500.0)
        self.assertGreater(len(sections["week_plan"]["selected_instruments"]), 0)
        self.assertTrue(sections["news"]["news_coverage_ready"])
        self.assertFalse(sections["news"]["live_news_fetch_enabled"])
        self.assertTrue(sections["safety"]["safety_check_blocked_execution"])
        self.assertFalse(sections["safety"]["trade_executed"])

    def test_static_html_renders_core_content(self) -> None:
        page = render_dashboard_html(self.result)
        self.assertIn("<!doctype html>", page)
        self.assertIn("J.A.R.V.I.S. Portfolio Dashboard", page)
        self.assertIn("Weekly Manual Plan", page)
        self.assertIn("BTC", page)
        self.assertIn("ETH", page)
        self.assertIn("MSFT", page)
        self.assertIn("News", page)
        self.assertIn("Safety", page)

    def test_write_dashboard_outputs_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dashboard_path = Path(tmp) / "dashboard.html"
            result = build_dashboard_contract_result(
                current_date="2026-06-18",
                dashboard_path=dashboard_path,
                write_dashboard=True,
            )
            self.assertTrue(result.dashboard_html_written)
            self.assertTrue(dashboard_path.exists())
            self.assertIn("J.A.R.V.I.S. Portfolio Dashboard", dashboard_path.read_text(encoding="utf-8"))

    def test_format_is_operator_readable(self) -> None:
        output = format_dashboard_contract(self.result)
        self.assertIn("J.A.R.V.I.S. DASHBOARD CONTRACT", output)
        self.assertIn("dashboard contract ready: True", output)
        self.assertIn("manual-only safety: True", output)
        self.assertIn("dashboard path:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_routes_v99_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v99.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "dashboard_contract_static_local_shell")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--dashboard-contract", source)
        self.assertIn("_dashboard_contract_main", source)


if __name__ == "__main__":
    unittest.main()
