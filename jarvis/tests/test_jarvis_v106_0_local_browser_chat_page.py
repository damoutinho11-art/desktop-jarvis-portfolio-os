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
from jarvis.runtime.local_server import ROUTES, make_handler, render_chat_page


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
        }


def _fixture_chat_result(*args, **kwargs):
    return _FixtureChat()


def _fixture_chat_reply(result):
    return "Fixture reply from local browser chat page. Safety: read-only and manual-only."


class JarvisV1060LocalBrowserChatPageTests(unittest.TestCase):
    def test_chat_route_registered(self) -> None:
        self.assertIn("GET /chat", ROUTES)
        self.assertEqual(ROUTES["GET /chat"], "local browser chat page backed by POST /api/chat")

    def test_render_chat_page_contains_ui_and_safety(self) -> None:
        html = render_chat_page()

        self.assertIn("J.A.R.V.I.S. Local Chat", html)
        self.assertIn("Ask J.A.R.V.I.S.", html)
        self.assertIn("fetch(\"/api/chat\"", html)
        self.assertIn("Read-only and manual-only", html)
        self.assertIn("No broker, credentials, orders, trades", html)

    def test_live_chat_page_and_api_chat_endpoint(self) -> None:
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
                conn.request("GET", "/chat")
                response = conn.getresponse()
                chat_html = response.read().decode("utf-8")
                conn.close()

                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/")
                root_response = conn.getresponse()
                root_html = root_response.read().decode("utf-8")
                conn.close()

                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request(
                    "POST",
                    "/api/chat",
                    body=json.dumps({"query": "what is my plan today?"}),
                    headers={"Content-Type": "application/json"},
                )
                api_response = conn.getresponse()
                payload = json.loads(api_response.read().decode("utf-8"))
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertIn("J.A.R.V.I.S. Local Chat", chat_html)
        self.assertEqual(root_response.status, 200)
        self.assertIn("J.A.R.V.I.S. Local Chat", root_html)
        self.assertEqual(api_response.status, 200)
        self.assertIn("Fixture reply", payload.get("reply", ""))

    def test_operator_surface_v106(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(
            operator.CURRENT_OPERATOR_SURFACE,
            {"local_browser_chat_page", "browser_chat_ux_polish", "assistant_tool_registry", "assistant_data_source_registry"},
        )

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("active_local_browser_chat_page_module", source)


if __name__ == "__main__":
    unittest.main()
