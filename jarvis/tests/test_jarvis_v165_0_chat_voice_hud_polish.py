from __future__ import annotations

import contextlib
import io
import unittest

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.local_server import render_chat_page
from jarvis.runtime.premium_chat_voice_hud import (
    STATUS_READY,
    build_chat_voice_hud_polish_result,
    render_chat_voice_hud_page,
)


class JarvisV165ChatVoiceHudPolishTests(unittest.TestCase):
    def test_premium_chat_hud_contains_design_system_and_legacy_markers(self) -> None:
        html = render_chat_page()

        for marker in (
            "J.A.R.V.I.S. Local Chat",
            "jarvis-shell",
            "app-nav",
            "hud-hero",
            "glass-panel",
            "status-badge",
            "Ask J.A.R.V.I.S.",
            'fetch("/api/chat"',
            "Read-only and manual-only",
            "No broker, credentials, orders, trades",
        ):
            self.assertIn(marker, html)

    def test_voice_controls_and_orb_states_are_preserved(self) -> None:
        html = render_chat_voice_hud_page()

        for marker in (
            "Voice input",
            "Read briefing aloud",
            "Speak reply",
            "Stop voice",
            "Audio unavailable",
            "SpeechRecognition",
            "speechSynthesis",
            "question.value = transcript",
            "Voice draft ready. Press Ask J.A.R.V.I.S. manually.",
            'class="jarvis-orb state-idle"',
            "state-listening",
            "state-thinking",
            "state-speaking",
            "@keyframes orbPulse",
            "@keyframes orbRing",
            'jarvisOrb.className = "jarvis-orb state-" + nextState',
        ):
            self.assertIn(marker, html)

    def test_quick_commands_include_intelligence_flows_without_execution_language(self) -> None:
        html = render_chat_voice_hud_page()

        for marker in (
            "Portfolio Health",
            "Universe Explorer",
            "What changed since last time?",
            "Evidence Summary",
            "manual-only",
            "read-only",
            "no broker",
            "no credentials",
            "no orders",
            "no trades",
            "no auto-approval",
        ):
            self.assertIn(marker, html)

        for forbidden in (
            "Buy now",
            "Sell now",
            "Rebalance Portfolio",
            "Execute trade",
            "Liquidate",
            "Recommendation queued for execution",
        ):
            self.assertNotIn(forbidden, html)

    def test_readiness_result_reports_safe_manual_only_state(self) -> None:
        result = build_chat_voice_hud_polish_result()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.chat_voice_hud_ready)
        self.assertTrue(result.premium_design_system_present)
        self.assertTrue(result.jarvis_orb_present)
        self.assertTrue(result.voice_controls_present)
        self.assertTrue(result.quick_commands_present)
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection_enabled)
        self.assertFalse(result.credentials_required)
        self.assertFalse(result.account_login_enabled)
        self.assertFalse(result.private_account_ingestion_enabled)
        self.assertFalse(result.buy_sell_request_created)
        self.assertFalse(result.order_ticket_created)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_created)
        self.assertFalse(result.auto_approval_enabled)
        self.assertFalse(result.approval_mutation)
        self.assertFalse(result.allocation_mutation)

    def test_operator_route_works(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--chat-voice-hud-polish"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V165_0_CHAT_VOICE_HUD_POLISH_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
