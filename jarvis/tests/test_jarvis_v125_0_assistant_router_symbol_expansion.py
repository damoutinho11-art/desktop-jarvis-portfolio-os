import unittest

from jarvis.runtime.assistant_symbol_aliases import normalize_asset_symbol_from_query
from jarvis.runtime.finance_intelligence_core import answer_finance_intelligence_question
from jarvis.runtime.chat_interface_contract import build_chat_interface_contract_result
from jarvis.runtime.assistant_router import classify_assistant_intent, _extract_asset_query


class TestJarvisV125AssistantRouterSymbolExpansion(unittest.TestCase):
    def test_alias_normalizer_maps_real_symbols_to_sleeves(self):
        self.assertEqual(normalize_asset_symbol_from_query("Tell me about SXRV"), "GROWTH_NASDAQ_ETF")
        self.assertEqual(normalize_asset_symbol_from_query("Tell me about SXRV.DE"), "GROWTH_NASDAQ_ETF")
        self.assertEqual(normalize_asset_symbol_from_query("Tell me about EUNL.DE"), "GLOBAL_CORE_ETF")
        self.assertEqual(normalize_asset_symbol_from_query("quality ETF"), "IS3Q.DE")
        self.assertEqual(normalize_asset_symbol_from_query("Microsoft stock"), "MSFT")

    def test_finance_core_answers_growth_and_core_aliases(self):
        growth = answer_finance_intelligence_question("Tell me about SXRV", current_date="2026-06-20")
        self.assertIn("GROWTH_NASDAQ_ETF", growth)
        self.assertIn("SXRV", growth)
        self.assertNotIn("I can answer: what is today", growth)

        core = answer_finance_intelligence_question("Tell me about EUNL.DE", current_date="2026-06-20")
        self.assertIn("GLOBAL_CORE_ETF", core)
        self.assertIn("price=", core)

    def test_chat_contract_routes_aliases_without_help_fallback(self):
        result = build_chat_interface_contract_result(
            query="Tell me about SXRV.DE",
            current_date="2026-06-20",
        )
        self.assertIn("GROWTH_NASDAQ_ETF", result.response)
        self.assertNotIn("I can answer: what is today", result.response)

    def test_assistant_router_extracts_aliases(self):
        self.assertEqual(_extract_asset_query("Tell me about SXRV.DE"), "GROWTH_NASDAQ_ETF")
        self.assertEqual(_extract_asset_query("Tell me about EUNL.DE"), "GLOBAL_CORE_ETF")
        self.assertEqual(classify_assistant_intent("Tell me about quality ETF"), "asset_lookup")


if __name__ == "__main__":
    unittest.main()
