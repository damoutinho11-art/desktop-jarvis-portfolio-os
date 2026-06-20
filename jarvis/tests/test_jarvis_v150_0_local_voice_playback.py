from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.voice_briefing import (
    LocalTTSPlaybackResult,
    build_voice_briefing_result,
    speak_text_locally,
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
            "live_news_context": {"usable_count": 2},
            "blockers": [],
        }
    )


def _patch_ready():
    return (
        patch("jarvis.runtime.voice_briefing.build_product_api_result", return_value=_product()),
        patch(
            "jarvis.runtime.voice_briefing.build_safety_check_console_output",
            return_value="BLOCKED: dry run. No execution action was taken.",
        ),
    )


class JarvisV1500LocalVoicePlaybackTests(unittest.TestCase):
    def test_windows_sapi_success_marks_audio_rendered(self) -> None:
        completed = SimpleNamespace(returncode=0, stdout="", stderr="")

        with patch("jarvis.runtime.voice_briefing.platform.system", return_value="Windows"), \
             patch("jarvis.runtime.voice_briefing.subprocess.run", return_value=completed) as run:
            result = speak_text_locally("Safe local briefing text.")

        self.assertTrue(result.audio_requested)
        self.assertTrue(result.audio_rendered)
        self.assertTrue(result.tts_available)
        self.assertEqual(result.tts_backend, "windows_sapi")
        self.assertIsNone(result.warning)
        self.assertIn("powershell", run.call_args.args[0][0])
        self.assertEqual(run.call_args.kwargs["input"], "Safe local briefing text.")

    def test_audio_unavailable_is_warning_not_blocker(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _patch_ready():
                stack.enter_context(item)
            stack.enter_context(patch("jarvis.runtime.voice_briefing.platform.system", return_value="Linux"))
            result = build_voice_briefing_result(
                current_date="2026-06-21",
                audio_requested=True,
                play_audio=True,
            )

        self.assertTrue(result.voice_briefing_ready)
        self.assertEqual(result.blockers, [])
        self.assertFalse(result.audio_rendered)
        self.assertFalse(result.tts_available)
        self.assertEqual(result.tts_backend, "text_only")
        self.assertTrue(any("showing text only" in item for item in result.warnings))

    def test_powershell_missing_is_safe_fallback(self) -> None:
        with patch("jarvis.runtime.voice_briefing.platform.system", return_value="Windows"), \
             patch("jarvis.runtime.voice_briefing.subprocess.run", side_effect=FileNotFoundError("powershell")):
            result = speak_text_locally("Safe local briefing text.")

        self.assertFalse(result.audio_rendered)
        self.assertFalse(result.tts_available)
        self.assertEqual(result.tts_backend, "windows_sapi")
        self.assertIn("unavailable", result.warning or "")

    def test_voice_briefing_speak_cli_uses_output_only_tts(self) -> None:
        playback = LocalTTSPlaybackResult(
            audio_requested=True,
            audio_rendered=True,
            tts_available=True,
            tts_backend="windows_sapi",
            warning=None,
        )

        with contextlib.ExitStack() as stack:
            for item in _patch_ready():
                stack.enter_context(item)
            stack.enter_context(patch("jarvis.runtime.voice_briefing.speak_text_locally", return_value=playback))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--voice-briefing-speak", "--current-date", "2026-06-21"])

        text = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("audio requested: True", text)
        self.assertIn("audio rendered: True", text)
        self.assertIn("tts backend: windows_sapi", text)
        self.assertIn("no speech commands added: True", text)

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--voice-briefing-speak", source)

    def test_voice_playback_does_not_add_execution_language(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _patch_ready():
                stack.enter_context(item)
            stack.enter_context(
                patch(
                    "jarvis.runtime.voice_briefing.speak_text_locally",
                    return_value=LocalTTSPlaybackResult(True, False, False, "text_only", "showing text only"),
                )
            )
            result = build_voice_briefing_result(
                current_date="2026-06-21",
                audio_requested=True,
                play_audio=True,
            )

        self.assertTrue(result.no_speech_commands_added)
        self.assertFalse(result.broker_connection_enabled)
        self.assertFalse(result.credentials_required)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_created)
        self.assertFalse(result.auto_approval_enabled)


if __name__ == "__main__":
    unittest.main()
