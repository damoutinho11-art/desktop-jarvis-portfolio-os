from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.user_runbook import (
    DEFAULT_RUNBOOK_PATH,
    STATUS_READY,
    build_user_runbook_result,
    format_user_runbook,
)


class JarvisV133UserRunbookAppUxTests(unittest.TestCase):
    def test_user_runbook_exists_and_covers_daily_dashboard_holdings_and_safety(self) -> None:
        path = Path(DEFAULT_RUNBOOK_PATH)
        self.assertTrue(path.exists())

        text = path.read_text(encoding="utf-8")
        self.assertIn("Start Jarvis.bat", text)
        self.assertIn("What Start Jarvis.bat Does", text)
        self.assertIn("outputs\\dashboard_latest.html", text)
        self.assertIn("Manual Holdings", text)
        self.assertIn("python .\\jarvis_operator.py --write-holdings-template --current-date 2026-06-20", text)
        self.assertIn("python .\\jarvis_operator.py --holdings-status --current-date 2026-06-20", text)
        self.assertIn('"manual_only": true', text)
        self.assertIn('"source": "diogo_manual_entry"', text)
        self.assertIn("must never connect to a broker", text)
        self.assertIn("Do not commit files from `outputs/` or `jarvis/local/`.", text)

    def test_user_runbook_result_is_ready_and_user_facing(self) -> None:
        result = build_user_runbook_result(current_date="2026-06-20")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.runbook_ready)
        self.assertTrue(result.runbook_exists)
        self.assertEqual(result.blockers, [])
        self.assertEqual(result.missing_required_snippets, [])

        text = format_user_runbook(result)
        self.assertIn("J.A.R.V.I.S. USER RUNBOOK", text)
        self.assertIn("runbook ready: True", text)
        self.assertIn("Start The App", text)
        self.assertIn("--holdings-status", text)
        self.assertIn("no broker", text)

    def test_operator_routes_user_runbook_command(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--user-runbook", "--current-date", "2026-06-20"])

        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn("J.A.R.V.I.S. USER RUNBOOK", text)
        self.assertIn("Start Jarvis.bat", text)
        self.assertIn("--write-holdings-template", text)

    def test_runtime_surface_tracks_user_runbook_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_user_runbook_module"], "jarvis.runtime.user_runbook")


if __name__ == "__main__":
    unittest.main()
