from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.jarvis_experience_parity_gate import (
    FINAL_VERDICT_READY,
    STATUS_READY,
    build_jarvis_experience_parity_gate_result,
    format_jarvis_experience_parity_gate,
)


def _dashboard_html() -> str:
    return """
    <html>
      <nav><a href="/dashboard">Dashboard</a><a href="/chat">Chat</a><a href="/briefing">Briefing</a><a href="/memory">Memory</a><a href="/safety">Safety</a></nav>
      <h1>J.A.R.V.I.S. Portfolio Dashboard</h1>
      <section>Today's Manual Plan</section>
      <section>Market Headlines <div class="headline-ticker"><div class="headline-track"><article class="headline-chip">BTC</article></div></div> never recommend action from headline alone</section>
      <section>Last Session Safe derived summaries only</section>
      <section>What Changed Since Last Time Since last time: first run.</section>
      <style>@keyframes ticker-scroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }</style>
    </html>
    """


def _chat_html() -> str:
    return """
    <html>
      <nav><a href="/dashboard">Dashboard</a><a href="/chat">Chat</a><a href="/briefing">Briefing</a><a href="/memory">Memory</a><a href="/safety">Safety</a></nav>
      <h1>J.A.R.V.I.S. Local Chat</h1>
      <button>Ask J.A.R.V.I.S.</button>
      <button>What changed since last time?</button>
      <button>Read briefing aloud</button>
      <button>Speak reply</button>
      <button>Stop voice</button>
      <button>Voice input</button>
      <span>Audio unavailable</span>
      <div class="jarvis-orb state-idle state-listening state-thinking state-speaking"></div>
      <style>@keyframes orbPulse {}</style>
      <script>fetch("/api/chat")</script>
    </html>
    """


class JarvisV1560ExperienceParityGateTests(unittest.TestCase):
    def _patch_ready(self):
        return (
            patch("jarvis.runtime.jarvis_experience_parity_gate._launch_ready", return_value=(True, {"missing": [], "forbidden_found": []})),
            patch("jarvis.runtime.jarvis_experience_parity_gate.build_dashboard_contract_result", return_value=SimpleNamespace(status="JARVIS_DASHBOARD_READY")),
            patch("jarvis.runtime.jarvis_experience_parity_gate.render_dashboard_html", return_value=_dashboard_html()),
            patch("jarvis.runtime.jarvis_experience_parity_gate.render_chat_page", return_value=_chat_html()),
            patch(
                "jarvis.runtime.jarvis_experience_parity_gate.build_voice_briefing_result",
                return_value=SimpleNamespace(
                    status="JARVIS_V143_0_VOICE_DAILY_BRIEFING_SHELL_READY_SAFE",
                    voice_briefing_ready=True,
                    text="Good evening, Diogo. Safe briefing.",
                    audio_requested=False,
                    audio_rendered=False,
                    tts_backend="text_only",
                    warnings=[],
                ),
            ),
            patch(
                "jarvis.runtime.jarvis_experience_parity_gate.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
            patch("jarvis.runtime.jarvis_experience_parity_gate._forbidden_source_markers_absent", return_value=(True, [])),
        )

    def test_parity_gate_ready_for_safe_jarvis_experience(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_jarvis_experience_parity_gate_result(current_date="2026-06-21")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.jarvis_experience_parity_ready)
        self.assertTrue(result.local_app_launch_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.chat_ready)
        self.assertTrue(result.voice_briefing_text_ready)
        self.assertTrue(result.voice_playback_ready_or_safe_fallback)
        self.assertTrue(result.chat_voice_buttons_ready)
        self.assertTrue(result.animated_orb_ready)
        self.assertTrue(result.news_ticker_ready)
        self.assertTrue(result.session_memory_visible)
        self.assertTrue(result.what_changed_visible)
        self.assertTrue(result.navigation_ready)
        self.assertEqual(result.blockers, [])

    def test_format_lists_final_verdict_and_safety_assertions(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            text = format_jarvis_experience_parity_gate(
                build_jarvis_experience_parity_gate_result(current_date="2026-06-21")
            )

        self.assertIn("J.A.R.V.I.S. EXPERIENCE PARITY GATE", text)
        self.assertIn("final verdict: READY_FOR_SAFE_JARVIS_EXPERIENCE", text)
        self.assertIn("animated orb ready: True", text)
        self.assertIn("news ticker ready: True", text)
        self.assertIn("broker_connection_enabled: False", text)
        self.assertIn("approval_mutation: False", text)

    def test_forbidden_source_marker_blocks_gate(self) -> None:
        patches = list(self._patch_ready())
        patches[-1] = patch(
            "jarvis.runtime.jarvis_experience_parity_gate._forbidden_source_markers_absent",
            return_value=(False, ["create_order"]),
        )
        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)
            result = build_jarvis_experience_parity_gate_result(current_date="2026-06-21")

        self.assertFalse(result.jarvis_experience_parity_ready)
        self.assertIn("forbidden_execution_marker_found", result.blockers)

    def test_operator_routes_experience_parity_gate(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--jarvis-experience-parity-gate", "--current-date", "2026-06-21"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V156_0_JARVIS_EXPERIENCE_PARITY_GATE_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
