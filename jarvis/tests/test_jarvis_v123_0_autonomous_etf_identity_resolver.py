import unittest

from jarvis.runtime.etf_identity_resolver import resolve_etf_identity
from jarvis.runtime.public_universe_quote_fetcher import build_quote_fetch_targets


class TestJarvisV123AutonomousETFIdentityResolver(unittest.TestCase):
    def test_growth_nasdaq_resolves_to_candidate_set(self):
        result = resolve_etf_identity("GROWTH_NASDAQ_ETF", current_date="2026-06-20")
        self.assertEqual(result.status, "JARVIS_V123_0_AUTONOMOUS_ETF_IDENTITY_RESOLVER_READY_SAFE")
        self.assertGreaterEqual(result.candidate_count, 1)
        self.assertIsNotNone(result.best_candidate)
        self.assertIn(result.best_candidate["symbol"], {"SXRV", "EQAC", "XNAS", "QDVE", "CNDX"})
        self.assertTrue(result.best_candidate.get("isin"))
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_quote_fetcher_resolves_growth_or_treats_it_as_covered(self):
        targets, unresolved = build_quote_fetch_targets(current_date="2026-06-20")
        by_symbol = {target.symbol: target for target in targets}

        self.assertNotIn("GROWTH_NASDAQ_ETF", unresolved)

        if "GROWTH_NASDAQ_ETF" in by_symbol:
            self.assertEqual(by_symbol["GROWTH_NASDAQ_ETF"].provider, "yahoo_chart_read_only")
            self.assertTrue(by_symbol["GROWTH_NASDAQ_ETF"].provider_symbol.endswith(".DE"))
        else:
            # After a successful live v123 quote probe, the symbol is already cached/covered,
            # so it should no longer be a fetch target.
            self.assertIn("BTC", by_symbol)
            self.assertIn("ETH", by_symbol)

    def test_identity_resolution_is_not_execution_approval(self):
        result = resolve_etf_identity("GROWTH_NASDAQ_ETF", current_date="2026-06-20")
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.buy_sell_request_created)
        self.assertFalse(result.auto_approval_enabled)
        self.assertIn("final real-world buy remains manual", " ".join(result.warnings))



    def test_chat_can_answer_growth_nasdaq_lookup(self):
        import jarvis.runtime.chat_interface_contract as chat

        result = chat.build_chat_interface_contract_result(
            query="Tell me about GROWTH_NASDAQ_ETF",
            current_date="2026-06-20",
        )
        self.assertIn("GROWTH_NASDAQ_ETF", result.response)
        self.assertIn("identity", result.response)
        self.assertNotIn("I can answer: what is today", result.response)


if __name__ == "__main__":
    unittest.main()
