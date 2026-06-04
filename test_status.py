"""Tests for read-only status command."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

import allocation_engine


class StatusCommandTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def test_status_runs_and_is_read_only(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state = allocation_engine.load_json("portfolio_state.json")
            constitution = allocation_engine.load_json("jarvis_constitution.json")
            state_path = root / "portfolio_state.json"
            constitution_path = root / "jarvis_constitution.json"
            self.write_json(state_path, state)
            self.write_json(constitution_path, constitution)

            completed = subprocess.run(
                [
                    sys.executable,
                    "status.py",
                    "--state-path",
                    str(state_path),
                    "--constitution-path",
                    str(constitution_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Status only. No trades executed.", completed.stdout)
            self.assertIn("lightyear_ready: True", completed.stdout)
            self.assertIn("lhv_crypto_ready: True", completed.stdout)
            self.assertFalse((root / "approval_ticket_latest.json").exists())
            self.assertFalse((root / "approval_ticket_2026-06-04.json").exists())
            self.assertFalse((root / "decision_log.jsonl").exists())
            self.assertEqual(allocation_engine.load_json(state_path), state)
            self.assertEqual(allocation_engine.load_json(constitution_path), constitution)


if __name__ == "__main__":
    unittest.main()
