from __future__ import annotations

import http.client
import json
import threading
import unittest
from contextlib import ExitStack
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from jarvis.runtime import operator
from jarvis.runtime.local_server import make_handler, render_chat_page


class _FixtureChat:
    chat_contract_ready = True
    manual_only = True
    response = "safe fixture response"

    def to_dict(self):
        return {
            "chat_contract_ready": True,
            "manual_only": True,
            "response": "safe fixture response",
            "blockers": [],
            "execution_forbidden": True,
            "broker_connection": False,
            "credentials_used": False,
            "order_created": False,
            "trade_executed": False,
        }


def _fixture_chat_result(*args, **kwargs):
    return _FixtureChat()


def _fixture_chat_reply(result):
    return "Fixture reply from v107 browser chat UX polish. No execution path."


class JarvisV1070BrowserChatUxPolishTests(unittest.TestCase):
    def test_chat_page_contains_preset_buttons(self) -> None:
        html = render_chat_page()

        self.assertIn("What is my plan today?", html)
        self.assertIn("Why these instruments?", html)
        self.assertIn("Is this safe?", html)
        self.assertIn("What are the blockers?", html)
        self.assertIn("Open dashboard", html)
        self.assertIn('class="preset"', html)

    def test_chat_page_contains_safety_badges_and_banner(self) -> None:
        html = render_chat_page()

        self.assertIn("Read-only and manual-only", html)
        self.assertIn("Safety and status badges", html)
        self.assertIn("manual-only", html)
        self.assertIn("read-only", html)
        self.assertIn("no broker", html)
        self.assertIn("no credentials", html)
        self.assertIn("no orders", html)
        self.assertIn("no trades", html)
        self.assertIn("no auto-approval", html)

    def test_chat_page_contains_reply_card_loading_state_and_dashboard_link(self) -> None:
        html = render_chat_page()

        self.assertIn("reply-card", html)
        self.assertIn("Loading...", html)
        self.assertIn("Loading reply...", html)
        self.assertIn('href="/dashboard"', html)
        self.assertIn("fetch(\"/api/chat\"", html)

    def test_root_and_chat_both_return_chat_page_and_api_chat_still_replies(self) -> None:
        with ExitStack() as stack:
            stack.enter_context(
                patch("jarvis.runtime.local_server.build_chat_interface_contract_result", _fixture_chat_result)
            )
            stack.enter_context(patch("jarvis.runtime.local_server.format_chat_reply", _fixture_chat_reply))

            handler = make_handler(host="127.0.0.1", port=0, current_date="2026-06-18")
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            port = int(server.server_address[1])
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/")
                root_response = conn.getresponse()
                root_html = root_response.read().decode("utf-8")
                conn.close()

                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/chat")
                chat_response = conn.getresponse()
                chat_html = chat_response.read().decode("utf-8")
                conn.close()

                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request(
                    "POST",
                    "/api/chat",
                    body=json.dumps({"query": "Is this safe?"}),
                    headers={"Content-Type": "application/json"},
                )
                api_response = conn.getresponse()
                payload = json.loads(api_response.read().decode("utf-8"))
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(root_response.status, 200)
        self.assertEqual(chat_response.status, 200)
        self.assertIn("J.A.R.V.I.S. Local Chat", root_html)
        self.assertIn("J.A.R.V.I.S. Local Chat", chat_html)
        self.assertIn("What is my plan today?", root_html)
        self.assertEqual(api_response.status, 200)
        self.assertIn("Fixture reply from v107", payload.get("reply", ""))

    def test_operator_surface_is_v107_browser_chat_ux_polish(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(operator.CURRENT_OPERATOR_SURFACE, {"browser_chat_ux_polish", "assistant_tool_registry", "assistant_data_source_registry", "assistant_asset_lookup"})

        surface = operator.get_active_runtime_surface()
        self.assertTrue(surface["active_runtime_stage"].startswith("v"))
        self.assertIn(surface["current_operator_surface"], {"browser_chat_ux_polish", "assistant_tool_registry", "assistant_data_source_registry", "assistant_asset_lookup"})

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("active_local_browser_chat_page_module", source)


if __name__ == "__main__":
    unittest.main()
