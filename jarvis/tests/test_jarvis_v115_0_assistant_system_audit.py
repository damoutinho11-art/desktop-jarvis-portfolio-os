from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_system_audit import (
    STATUS_READY,
    build_assistant_system_audit_result,
    format_assistant_system_audit,
)


class JarvisV1150AssistantSystemAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_assistant_system_audit_result(current_date="2026-06-18")

    def test_audit_ready_when_assistant_layers_ready(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertTrue(self.result.tool_registry_ready)
        self.assertTrue(self.result.data_source_registry_ready)
        self.assertTrue(self.result.asset_lookup_ready)
        self.assertTrue(self.result.router_intent_coverage_ready)
        self.assertTrue(self.result.browser_chat_ready)
        self.assertEqual(self.result.blockers, [])

    def test_no_forbidden_capabilities(self) -> None:
        self.assertTrue(self.result.no_forbidden_capabilities)
        self.assertFalse(any(self.result.forbidden_capabilities.values()))

    def test_supported_intents_include_assistant_toolbelt(self) -> None:
        for intent in ["asset_lookup", "crypto_market_context", "news_context", "safety", "dashboard"]:
            self.assertIn(intent, self.result.supported_intents)

    def test_report_prints_safety_lines(self) -> None:
        output = format_assistant_system_audit(self.result)

        self.assertIn("J.A.R.V.I.S. ASSISTANT SYSTEM AUDIT", output)
        self.assertIn("no broker integration: true", output)
        self.assertIn("no trades: true", output)
        self.assertIn("no execution path: true", output)

    def test_operator_surface_v115_and_route(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v115.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "assistant_system_audit")

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_system_audit_module"], "jarvis.runtime.assistant_system_audit")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-system-audit", source)
        self.assertIn("_assistant_system_audit_main", source)


if __name__ == "__main__":
    unittest.main()
