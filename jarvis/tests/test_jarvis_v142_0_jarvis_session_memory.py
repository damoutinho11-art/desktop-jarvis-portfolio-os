from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.jarvis_session_memory import (
    DEFAULT_SESSION_MEMORY_PATH,
    FORBIDDEN_MEMORY_KEYS,
    STATUS_READY,
    build_jarvis_session_memory_result,
    build_safe_session_snapshot,
    format_jarvis_session_memory,
)


def _product() -> SimpleNamespace:
    return SimpleNamespace(
        to_dict=lambda: {
            "dashboard_ready": True,
            "week_plan": {
                "emergency_top_up_eur": 75,
                "crypto_eur": 100,
                "etf_fund_eur": 275,
                "individual_stock_eur": 50,
                "selected_instruments": [
                    {"symbol": "BTC", "amount_eur": 75},
                    {"symbol": "MSFT", "amount_eur": 50},
                ],
            },
            "live_news_context": {"top_headlines": [{"title": "Market opens calm"}]},
            "manual_holdings": {"file_exists": False, "positions_count": 0},
            "safety_status": {"safety_check_blocked_execution": True},
            "blockers": [],
            "warnings": ["holdings missing"],
        }
    )


class JarvisV142SessionMemoryTests(unittest.TestCase):
    def _patch_product(self):
        return (
            patch("jarvis.runtime.jarvis_session_memory.build_product_api_result", return_value=_product()),
            patch(
                "jarvis.runtime.jarvis_session_memory.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_missing_memory_is_safe_first_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis_session_memory.local.json"
            with patch(
                "jarvis.runtime.jarvis_session_memory.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ):
                result = build_jarvis_session_memory_result(mode="status", memory_path=path)

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.session_memory_ready)
        self.assertTrue(result.first_run)
        self.assertFalse(result.memory_exists)
        self.assertIn("First run", result.summary_text)
        self.assertEqual(result.blockers, [])

    def test_write_snapshot_creates_local_ignored_file_only(self) -> None:
        self.assertTrue(DEFAULT_SESSION_MEMORY_PATH.startswith("jarvis/local/"))
        self.assertTrue(DEFAULT_SESSION_MEMORY_PATH.endswith(".local.json"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis_session_memory.local.json"
            with contextlib.ExitStack() as stack:
                for item in self._patch_product():
                    stack.enter_context(item)
                result = build_jarvis_session_memory_result(
                    mode="write_snapshot",
                    current_date="2026-06-20",
                    memory_path=path,
                    last_assistant_summary_text="Ready when you are.",
                )
            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertTrue(result.snapshot_written)
        self.assertTrue(path.name.endswith(".local.json"))
        self.assertEqual(data["dashboard_ready_label"], "READY FOR MANUAL USE")
        self.assertIn("crypto EUR 100.00", data["manual_plan_summary"])
        self.assertNotIn("broker_data", json.dumps(data).lower())

    def test_summary_reads_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis_session_memory.local.json"
            snapshot = build_safe_session_snapshot(current_date="2026-06-20", product_api_result=_product())
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            with patch(
                "jarvis.runtime.jarvis_session_memory.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ):
                result = build_jarvis_session_memory_result(mode="summary", memory_path=path)

        self.assertFalse(result.first_run)
        self.assertTrue(result.memory_exists)
        self.assertIn("READY FOR MANUAL USE", result.summary_text)
        self.assertIn("manual plan", result.summary_text)

    def test_no_trading_or_execution_fields_exist(self) -> None:
        snapshot = build_safe_session_snapshot(current_date="2026-06-20", product_api_result=_product())
        keys: list[str] = []

        def collect_keys(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    keys.append(str(key).lower())
                    collect_keys(item)
            elif isinstance(value, list):
                for item in value:
                    collect_keys(item)

        collect_keys(snapshot)

        for forbidden in FORBIDDEN_MEMORY_KEYS:
            self.assertFalse(any(forbidden in key for key in keys), forbidden)
        self.assertTrue(snapshot["safety_status"]["manual_only"])
        self.assertTrue(snapshot["safety_status"]["execution_forbidden"])

    def test_format_and_operator_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis_session_memory.local.json"
            with contextlib.ExitStack() as stack:
                for item in self._patch_product():
                    stack.enter_context(item)
                result = build_jarvis_session_memory_result(mode="write_snapshot", memory_path=path)
                text = format_jarvis_session_memory(result)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = runtime_operator.main(
                        [
                            "--session-memory-summary",
                            "--session-memory-path",
                            str(path),
                        ]
                    )

        self.assertIn("J.A.R.V.I.S. SESSION MEMORY", text)
        self.assertIn("forbidden fields absent: True", text)
        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V142_0_JARVIS_SESSION_MEMORY_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
