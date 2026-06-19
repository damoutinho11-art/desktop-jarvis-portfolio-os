from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.assistant_asset_lookup import (
    STATUS_NOT_FOUND,
    STATUS_READY,
    build_assistant_asset_lookup_result,
    build_etf_comparison_result,
    format_assistant_asset_lookup,
    format_etf_comparison,
)
from jarvis.runtime.chat_interface_contract import build_chat_interface_contract_result, format_chat_reply


class JarvisV1100AssistantAssetLookupTests(unittest.TestCase):
    def test_btc_lookup(self) -> None:
        result = build_assistant_asset_lookup_result(asset="BTC", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.matched_symbol, "BTC")
        self.assertEqual(result.lane, "crypto")
        self.assertTrue(result.selected_in_plan)
        self.assertGreater(result.recommended_amount_eur or 0, 0)
        self.assertIn("source", result.to_dict())
        self.assertFalse(result.trade_executed)

    def test_eth_lookup(self) -> None:
        result = build_assistant_asset_lookup_result(asset="ETH", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.matched_symbol, "ETH")
        self.assertEqual(result.lane, "crypto")
        self.assertTrue(result.selected_in_plan)

    def test_vwce_lookup(self) -> None:
        result = build_assistant_asset_lookup_result(asset="VWCE", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.matched_symbol, "VWCE")
        self.assertEqual(result.lane, "etf_fund")
        self.assertTrue(result.selected_in_plan)

    def test_is3q_lookup_accepts_dot_de(self) -> None:
        result = build_assistant_asset_lookup_result(asset="IS3Q.DE", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.matched_symbol, "IS3Q.DE")
        self.assertEqual(result.lane, "etf_fund")

    def test_msft_lookup(self) -> None:
        result = build_assistant_asset_lookup_result(asset="MSFT", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.matched_symbol, "MSFT")
        self.assertEqual(result.lane, "individual_stock")
        self.assertTrue(result.selected_in_plan)
        self.assertEqual(result.recommended_amount_eur, 50.0)

    def test_unknown_symbol_is_honest(self) -> None:
        result = build_assistant_asset_lookup_result(asset="XYZ_UNKNOWN", current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_NOT_FOUND)
        self.assertIn("unknown asset", result.blockers[0])
        self.assertTrue(result.available_assets)
        reply = format_assistant_asset_lookup(result)
        self.assertIn("I could not find", reply)
        self.assertIn("Available assets include", reply)

    def test_etf_comparison(self) -> None:
        results = build_etf_comparison_result(current_date="2026-06-18")
        output = format_etf_comparison(results)

        self.assertGreaterEqual(len(results), 2)
        self.assertIn("VWCE", output)
        self.assertIn("IS3Q.DE", output)
        self.assertIn("not a buy/sell request", output)

    def test_lookup_reply_has_no_execution_language(self) -> None:
        result = build_assistant_asset_lookup_result(asset="VWCE", current_date="2026-06-18")
        reply = format_assistant_asset_lookup(result)

        self.assertIn("Data / Source / Freshness", reply)
        self.assertIn("live fetch enabled=False", reply)
        self.assertIn("No broker, order, trade", reply)
        self.assertNotIn("I placed", reply)
        self.assertNotIn("buy now", reply.lower())

    def test_chat_routes_asset_lookup_and_etf_compare(self) -> None:
        asset = build_chat_interface_contract_result(query="Tell me about VWCE", current_date="2026-06-18")
        compare = build_chat_interface_contract_result(query="Compare my ETFs", current_date="2026-06-18")

        self.assertEqual(asset.detected_intent, "asset_lookup")
        self.assertIn("VWCE", format_chat_reply(asset))
        self.assertEqual(compare.detected_intent, "etf_compare")
        self.assertIn("ETF/fund comparison", format_chat_reply(compare))

    def test_operator_surface_v110_and_route(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v110.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "assistant_asset_lookup")

        surface = operator.get_active_runtime_surface()
        self.assertEqual(surface["active_assistant_asset_lookup_module"], "jarvis.runtime.assistant_asset_lookup")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--assistant-asset-lookup", source)
        self.assertIn("_assistant_asset_lookup_main", source)


if __name__ == "__main__":
    unittest.main()
