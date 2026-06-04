"""Tests for v0.3 voice briefing behavior."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import subprocess
import sys
import unittest

import allocation_engine
import run_weekly_allocation
import status


ROOT = Path(__file__).resolve().parent


class VoiceBriefingTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def copy_runtime_json(self, root: Path) -> None:
        for filename in ["portfolio_state.json", "jarvis_constitution.json", "etf_universe.json"]:
            self.write_json(root / filename, allocation_engine.load_json(ROOT / filename))

    def forced_voice_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["JARVIS_VOICE_FORCE_FALLBACK"] = "1"
        return env

    def test_weekly_voice_text_contains_required_safety_line(self) -> None:
        result = allocation_engine.build_weekly_result()
        briefing = run_weekly_allocation.build_weekly_voice_briefing(result)

        self.assertIn("Sir, portfolio mode is transition.", briefing)
        self.assertIn("€103.85 to Quality ETF", briefing)
        self.assertIn("€41.54 to Bitcoin", briefing)
        self.assertIn("€62.31 to tactical reserve", briefing)
        self.assertIn("Lightyear is not ready.", briefing)
        self.assertIn("No trades executed.", briefing)

    def test_status_speak_is_read_only_and_prints_fallback(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.copy_runtime_json(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "status.py"),
                    "--state-path",
                    str(root / "portfolio_state.json"),
                    "--constitution-path",
                    str(root / "jarvis_constitution.json"),
                    "--speak",
                ],
                cwd=root,
                env=self.forced_voice_env(),
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("J.A.R.V.I.S. voice fallback:", completed.stdout)
            self.assertIn("Sir, portfolio mode is transition.", completed.stdout)
            self.assertIn("Lightyear and Kraken are not ready.", completed.stdout)
            self.assertIn("No trades executed.", completed.stdout)
            self.assertFalse((root / "outputs" / "approval_ticket_latest.json").exists())
            self.assertFalse((root / "outputs" / "decision_log.jsonl").exists())

    def test_run_weekly_speak_keeps_ticket_content_same(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.copy_runtime_json(root)

            normal = subprocess.run(
                [sys.executable, str(ROOT / "run_weekly_allocation.py")],
                cwd=root,
                env=self.forced_voice_env(),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(normal.returncode, 0, normal.stderr)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            normal_ticket = allocation_engine.load_json(ticket_path)

            spoken = subprocess.run(
                [sys.executable, str(ROOT / "run_weekly_allocation.py"), "--speak"],
                cwd=root,
                env=self.forced_voice_env(),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(spoken.returncode, 0, spoken.stderr)
            spoken_ticket = allocation_engine.load_json(ticket_path)

            self.assertEqual(spoken_ticket, normal_ticket)
            self.assertIn("J.A.R.V.I.S. voice fallback:", spoken.stdout)
            self.assertIn("€41.54 to Bitcoin", spoken.stdout)
            self.assertIn("€62.31 to tactical reserve", spoken.stdout)
            self.assertIn("No trades executed.", spoken.stdout)

    def test_status_voice_text_contains_required_safety_line(self) -> None:
        briefing = status.build_status_voice_briefing()
        self.assertIn("Sir, portfolio mode is transition.", briefing)
        self.assertIn("Lightyear and Kraken are not ready.", briefing)
        self.assertIn("Emergency funds remain excluded.", briefing)
        self.assertIn("Status only.", briefing)
        self.assertIn("No trades executed.", briefing)


if __name__ == "__main__":
    unittest.main()
