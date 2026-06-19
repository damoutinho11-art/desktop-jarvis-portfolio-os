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


class JarvisV1000DashboardQualityPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_dashboard_contract_result(current_date="2026-06-18")

    def test_dashboard_quality_contract_still_ready(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertTrue(self.result.dashboard_contract_ready)
        self.assertTrue(self.result.backend_ready)
        self.assertTrue(self.result.manual_only)
        self.assertEqual(self.result.blockers, [])

    def test_html_has_action_summary_and_manual_qa(self) -> None:
        page = render_dashboard_html(self.result)

        self.assertIn("Today's Manual Action Summary", page)
        self.assertIn("Crypto checklist", page)
        self.assertIn("ETF/fund checklist", page)
        self.assertIn("Stock checklist", page)
        self.assertIn("Warnings & Manual Review Notes", page)
        self.assertIn("Manual QA Checklist", page)
        self.assertIn("start .\\outputs\\dashboard_latest.html", page)

    def test_html_keeps_core_dashboard_content(self) -> None:
        page = render_dashboard_html(self.result)

        for expected in [
            "J.A.R.V.I.S. Portfolio Dashboard",
            "Weekly Manual Plan",
            "BTC",
            "ETH",
            "VWCE",
            "IS3Q.DE",
            "MSFT",
            "News",
            "Safety",
            "Blockers",
        ]:
            self.assertIn(expected, page)

    def test_format_prints_open_command_and_qa_checklist(self) -> None:
        output = format_dashboard_contract(self.result)

        self.assertIn("OPEN DASHBOARD:", output)
        self.assertIn("start .\\outputs\\dashboard_latest.html", output)
        self.assertIn("QA CHECKLIST:", output)
        self.assertIn("verify Weekly Manual Plan is visible", output)

    def test_write_dashboard_quality_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dashboard_path = Path(tmp) / "dashboard.html"
            result = build_dashboard_contract_result(
                current_date="2026-06-18",
                dashboard_path=dashboard_path,
                write_dashboard=True,
            )
            page = dashboard_path.read_text(encoding="utf-8")

            self.assertTrue(result.dashboard_html_written)
            self.assertIn("Today's Manual Action Summary", page)
            self.assertIn("Manual QA Checklist", page)

    def test_operator_surface_v100(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v100.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "dashboard_quality_pass")


if __name__ == "__main__":
    unittest.main()
