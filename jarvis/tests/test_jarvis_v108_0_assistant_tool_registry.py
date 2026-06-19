from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_tool_registry import (
    REQUIRED_TOOL_IDS,
    STATUS_READY,
    build_assistant_tool_registry_result,
    format_assistant_tool_registry,
)


class JarvisV1080AssistantToolRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_assistant_tool_registry_result(current_date="2026-06-18")

    def test_all_required_tools_are_listed(self) -> None:
        ids = {tool.tool_id for tool in self.result.tools}
        self.assertEqual(set(REQUIRED_TOOL_IDS), ids)
        self.assertEqual(self.result.tool_count, len(REQUIRED_TOOL_IDS))

    def test_all_tools_declare_readiness_and_safety(self) -> None:
        for tool in self.result.tools:
            self.assertIn(tool.readiness, {"ready", "partial", "missing"})
            self.assertEqual(tool.safety_level, "read_only_manual_only_no_execution")
            self.assertIsInstance(tool.data_sources_used, list)
            self.assertIsInstance(tool.live_fetch_required, bool)
            self.assertIsInstance(tool.local_cache_supported, bool)
            self.assertIsInstance(tool.freshness_required, bool)

    def test_partial_or_missing_tools_are_honest(self) -> None:
        partial_or_missing = [tool for tool in self.result.tools if tool.readiness != "ready"]
        self.assertTrue(partial_or_missing)
        self.assertTrue(
            any(tool.blockers or tool.warnings for tool in partial_or_missing),
            "partial or missing assistant tools must explain limitations",
        )

    def test_no_execution_broker_order_or_trade_tools_exist(self) -> None:
        forbidden_terms = ("broker", "credential", "order", "trade", "execution", "buy_request", "sell_request")
        for tool in self.result.tools:
            lowered = tool.tool_id.lower()
            self.assertFalse(any(term in lowered for term in forbidden_terms), tool.tool_id)
        self.assertFalse(self.result.forbidden_tools_present)
        self.assertTrue(self.result.manual_only)
        self.assertTrue(self.result.execution_forbidden)
        self.assertFalse(self.result.broker_connection)
        self.assertFalse(self.result.credentials_used)
        self.assertFalse(self.result.order_created)
        self.assertFalse(self.result.trade_executed)

    def test_registry_is_ready_but_discloses_partial_tools(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertTrue(self.result.registry_ready)
        self.assertGreater(self.result.partial_tool_count + self.result.missing_tool_count, 0)

    def test_report_contains_tool_and_safety_summary(self) -> None:
        output = format_assistant_tool_registry(self.result)

        self.assertIn("J.A.R.V.I.S. ASSISTANT TOOL REGISTRY", output)
        self.assertIn("portfolio_overview", output)
        self.assertIn("asset_lookup", output)
        self.assertIn("manual-only: True", output)
        self.assertIn("trade executed: False", output)
        self.assertIn("forbidden tools present: False", output)

    def test_operator_surface_v108_and_route(self) -> None:
        self.assertTrue(operator.ACTIVE_RUNTIME_STAGE.startswith("v"))
        self.assertIn(operator.CURRENT_OPERATOR_SURFACE, {"assistant_tool_registry", "assistant_data_source_registry", "assistant_asset_lookup", "assistant_market_context", "assistant_news_context", "assistant_router", "assistant_answer_style_polish"})

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_tool_registry_module"], "jarvis.runtime.assistant_tool_registry")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-tool-registry", source)
        self.assertIn("_assistant_tool_registry_main", source)


if __name__ == "__main__":
    unittest.main()
