from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.voice_briefing import (
    FORBIDDEN_VOICE_PHRASES,
    STATUS_READY,
    build_voice_briefing_result,
    format_voice_briefing,
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
            },
            "data_readiness": {"data_readiness_ready": True},
            "live_news_context": {"usable_count": 0},
            "blockers": [],
        }
    )


class JarvisV143VoiceBriefingTests(unittest.TestCase):
    def _patch_ready(self):
        return (
            patch("jarvis.runtime.voice_briefing.build_product_api_result", return_value=_product()),
            patch(
                "jarvis.runtime.voice_briefing.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_voice_text_includes_ready_manual_plan_and_safety(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_voice_briefing_result(current_date="2026-06-20")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.voice_briefing_ready)
        self.assertIn("Good evening, Diogo.", result.text)
        self.assertIn("ready for manual use", result.text)
        self.assertIn("crypto 100 euros", result.text)
        self.assertIn("ETF/fund 275 euros", result.text)
        self.assertIn("Manual-only safety is active", result.text)
        self.assertIn("Ready when you are.", result.text)

    def test_voice_text_has_no_execution_phrases(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            text = build_voice_briefing_result(current_date="2026-06-20").text.lower()

        for phrase in FORBIDDEN_VOICE_PHRASES:
            self.assertNotIn(phrase, text)

    def test_missing_tts_is_warning_not_blocker(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_voice_briefing_result(current_date="2026-06-20", audio_requested=True)

        self.assertFalse(result.audio_rendered)
        self.assertFalse(result.tts_available)
        self.assertTrue(result.voice_briefing_ready)
        self.assertEqual(result.blockers, [])
        self.assertTrue(any("audio was requested" in item for item in result.warnings))

    def test_format_text_only_and_operator_route(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_voice_briefing_result(current_date="2026-06-20")
            self.assertEqual(format_voice_briefing(result, text_only=True), result.text)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--voice-briefing-text", "--current-date", "2026-06-20"])

        self.assertEqual(code, 0)
        self.assertIn("Good evening, Diogo.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
