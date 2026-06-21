from __future__ import annotations

import unittest
from pathlib import Path

from jarvis.runtime.local_app_packaging_polish import (
    STATUS_READY,
    build_local_app_packaging_polish_result,
)


ROOT = Path(__file__).resolve().parents[2]


class JarvisV147LocalAppPackagingPolishTests(unittest.TestCase):
    def _read(self, name: str) -> str:
        return (ROOT / name).read_text(encoding="utf-8")

    def test_launcher_files_contain_safety_markers_and_default_local_app(self) -> None:
        for name in ["Start Jarvis.bat", "Start-Jarvis.ps1"]:
            text = self._read(name)
            self.assertNotIn("JARVIS_OPEN_CHAT", text)
            self.assertIn("--local-server", text)
            self.assertIn("127.0.0.1:8765", text)
            self.assertIn("/dashboard", text)
            self.assertIn("/chat", text)
            self.assertIn("Manual approval required", text)
            self.assertIn("No broker", text)
            self.assertIn("No credentials", text)
            self.assertIn("No orders", text)
            self.assertIn("No trades", text)
            self.assertIn("No auto-approval", text)

    def test_launcher_avoids_forbidden_execution_commands(self) -> None:
        combined = self._read("Start Jarvis.bat") + "\n" + self._read("Start-Jarvis.ps1")
        lowered = combined.lower()
        for phrase in ["place order", "execute trade", "auto rebalance", "connect broker"]:
            self.assertNotIn(phrase, lowered)

    def test_runbook_mentions_daily_use_cannot_do_and_manual_workflow(self) -> None:
        text = self._read("JARVIS_USER_RUNBOOK.md")
        self.assertIn("How Diogo Uses J.A.R.V.I.S. Daily", text)
        self.assertIn("What J.A.R.V.I.S. Cannot Do", text)
        self.assertIn("Manual Buy Workflow", text)
        self.assertIn("Market Headlines", text)
        self.assertIn("--voice-briefing-text", text)
        self.assertIn("--what-changed", text)
        self.assertIn("manual-only", text.lower())

    def test_referenced_commands_exist_in_operator_surface(self) -> None:
        operator = (ROOT / "jarvis/runtime/operator.py").read_text(encoding="utf-8")
        for command in [
            "--daily-operator",
            "--dashboard-contract",
            "--local-server",
            "--voice-briefing-text",
            "--what-changed",
            "--holdings-status",
        ]:
            self.assertIn(command, operator)

    def test_packaging_gate_outputs_ready_safe_status(self) -> None:
        result = build_local_app_packaging_polish_result()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.local_app_packaging_ready)
        self.assertEqual(result.blockers, [])


if __name__ == "__main__":
    unittest.main()
