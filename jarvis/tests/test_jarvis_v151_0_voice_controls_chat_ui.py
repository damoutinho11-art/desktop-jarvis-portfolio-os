from __future__ import annotations

import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime.local_server import ROUTES, make_handler, render_chat_page


def _request_json(*, host: str, port: int, path: str) -> tuple[int, dict[str, object]]:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw)
    finally:
        conn.close()


class JarvisV1510VoiceControlsChatUiTests(unittest.TestCase):
    def test_chat_page_includes_safe_voice_controls(self) -> None:
        html = render_chat_page()

        self.assertIn("Voice input", html)
        self.assertIn("Read briefing aloud", html)
        self.assertIn("Speak reply", html)
        self.assertIn("Stop voice", html)
        self.assertIn("audioStatus", html)
        self.assertIn("speechSynthesis", html)
        self.assertIn("SpeechRecognition", html)
        self.assertIn("Microphone input unavailable", html)
        self.assertIn("Audio unavailable", html)
        self.assertIn("Press Ask J.A.R.V.I.S. manually", html)
        self.assertIn("/api/voice-briefing", html)

    def test_voice_input_only_drafts_text(self) -> None:
        html = render_chat_page()

        self.assertIn("question.value = transcript", html)
        self.assertIn("Voice draft ready", html)
        self.assertNotIn("recognition.onresult = (event) => { askJarvis", html)
        lowered = html.lower()
        self.assertIn("no broker", lowered)
        self.assertIn("no trades", lowered)

    def test_voice_briefing_endpoint_is_read_only_text_payload(self) -> None:
        fake = SimpleNamespace(
            to_dict=lambda: {
                "voice_briefing_ready": True,
                "text": "Safe local briefing text.",
                "audio_requested": False,
                "audio_rendered": False,
                "manual_only": True,
                "broker_connection_enabled": False,
                "credentials_required": False,
                "order_created": False,
                "trade_created": False,
                "auto_approval_enabled": False,
                "blockers": [],
            }
        )

        host = "127.0.0.1"
        with patch("jarvis.runtime.local_server.build_voice_briefing_result", return_value=fake):
            handler = make_handler(host=host, port=0, current_date="2026-06-21")
            server = ThreadingHTTPServer((host, 0), handler)
            port = int(server.server_address[1])
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                status, payload = _request_json(host=host, port=port, path="/api/voice-briefing")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(status, 200)
        self.assertEqual(payload["text"], "Safe local briefing text.")
        self.assertFalse(payload["audio_requested"])
        self.assertFalse(payload["audio_rendered"])
        self.assertTrue(payload["manual_only"])
        self.assertFalse(payload["broker_connection_enabled"])
        self.assertFalse(payload["credentials_required"])
        self.assertFalse(payload["order_created"])
        self.assertFalse(payload["trade_created"])
        self.assertFalse(payload["auto_approval_enabled"])

    def test_route_registry_lists_voice_briefing_without_execution(self) -> None:
        self.assertIn("GET /api/voice-briefing", ROUTES)
        self.assertIn("read-only", ROUTES["GET /api/voice-briefing"])


if __name__ == "__main__":
    unittest.main()
