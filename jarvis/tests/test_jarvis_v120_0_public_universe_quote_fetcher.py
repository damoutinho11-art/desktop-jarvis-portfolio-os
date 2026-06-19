import unittest

from jarvis.runtime.public_universe_quote_fetcher import (
    STATUS_READY,
    build_public_universe_quote_fetch_result,
    build_quote_fetch_targets,
)


class TestJarvisV120PublicUniverseQuoteFetcher(unittest.TestCase):
    def test_dry_run_ready_safe(self):
        result = build_public_universe_quote_fetch_result(current_date="2026-06-20", dry_run=True)
        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.buy_sell_request_created)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)
        self.assertFalse(result.auto_approval_enabled)
        self.assertFalse(result.cache_written)

    def test_targets_include_priority_assets(self):
        targets, unresolved = build_quote_fetch_targets(current_date="2026-06-20")
        symbols = {target.symbol for target in targets}

        # These assets were the first missing-priority set before the cache was written.
        # After a successful local cache refresh, they may disappear from the target list
        # because the coverage layer now marks them trusted.
        from jarvis.runtime.public_universe_data_coverage import build_public_universe_data_coverage_result

        coverage = build_public_universe_data_coverage_result(current_date="2026-06-20")
        records = {record["symbol"]: record for record in coverage.records}

        for symbol in ["VWCE", "GLOBAL_CORE_ETF", "IS3Q.DE"]:
            self.assertTrue(
                symbol in symbols or records[symbol]["trusted_quote"],
                f"{symbol} must either be a fetch target or already trusted",
            )

        # These remain valid crypto fetch targets when CoinGecko rate limits left them missing.
        self.assertIn("SOL", symbols)
        self.assertTrue("RENDER" in symbols or records["RENDER"]["trusted_quote"])
        self.assertTrue("TAO" in symbols or records["TAO"]["trusted_quote"])
        self.assertIsInstance(unresolved, list)

    def test_provider_urls_are_public_no_api_key_contract(self):
        result = build_public_universe_quote_fetch_result(current_date="2026-06-20", dry_run=True)
        text = " ".join(result.warnings).lower()
        self.assertIn("no api keys", text)
        self.assertFalse(result.credentials_used)


if __name__ == "__main__":
    unittest.main()
