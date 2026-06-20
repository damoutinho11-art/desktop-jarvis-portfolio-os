from __future__ import annotations

import contextlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.what_changed_since_last_time import (
    STATUS_READY,
    build_what_changed_since_last_time_result,
    format_what_changed_since_last_time,
)


def _snapshot(**overrides):
    data = {
        "dashboard_ready_label": "READY FOR MANUAL USE",
        "manual_plan_summary": "emergency EUR 75.00, crypto EUR 100.00, ETF/fund EUR 275.00, stock EUR 50.00",
        "selected_instruments_summary": "BTC EUR 75.00, MSFT EUR 50.00",
        "market_movement_summary": "BTC moved up, MSFT moved slightly down",
        "news_headline_summary": "News unavailable - not blocking today's manual plan.",
        "holdings_status_summary": "Holdings not entered yet",
        "safety_status": {"manual_only": True},
        "blockers_count": 0,
        "warnings_count": 2,
    }
    data.update(overrides)
    return data


class JarvisV146WhatChangedTests(unittest.TestCase):
    def _patch_safety(self):
        return patch(
            "jarvis.runtime.what_changed_since_last_time.build_safety_check_console_output",
            return_value="BLOCKED: dry run. No execution action was taken.",
        )

    def test_no_memory_is_safe_first_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.local.json"
            with self._patch_safety():
                result = build_what_changed_since_last_time_result(memory_path=path)

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.what_changed_ready)
        self.assertTrue(result.first_run)
        self.assertFalse(result.comparison_available)
        self.assertIn("first run", result.summary_text.lower())
        self.assertEqual(result.blockers, [])

    def test_comparison_works_with_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.local.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")
            current = _snapshot(manual_plan_summary="emergency EUR 75.00, crypto EUR 90.00, ETF/fund EUR 285.00, stock EUR 50.00")
            with self._patch_safety():
                result = build_what_changed_since_last_time_result(memory_path=path, current_snapshot=current)

        self.assertFalse(result.first_run)
        self.assertTrue(result.comparison_available)
        self.assertIn("manual plan changed", result.summary_text)
        self.assertIn("safety remains manual-only", result.summary_text)
        self.assertTrue(any("dashboard unchanged" in item for item in result.changes))

    def test_output_has_no_trading_claims_and_preserves_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.local.json"
            path.write_text(json.dumps(_snapshot()), encoding="utf-8")
            with self._patch_safety():
                result = build_what_changed_since_last_time_result(memory_path=path, current_snapshot=_snapshot())
                text = format_what_changed_since_last_time(result)

        lowered = text.lower()
        for phrase in ["bought", "sold", "order created: true", "trade created: true", "liquidate"]:
            self.assertNotIn(phrase, lowered)
        self.assertTrue(result.manual_only)
        self.assertFalse(result.broker_connection_enabled)
        self.assertFalse(result.approval_mutation)

    def test_operator_routes_what_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.local.json"
            with self._patch_safety():
                output = []
                import io
                from contextlib import redirect_stdout

                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = runtime_operator.main(["--what-changed", "--session-memory-path", str(path)])
                output.append(buf.getvalue())

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V146_0_WHAT_CHANGED_SINCE_LAST_TIME_READY_SAFE", output[0])


if __name__ == "__main__":
    unittest.main()
