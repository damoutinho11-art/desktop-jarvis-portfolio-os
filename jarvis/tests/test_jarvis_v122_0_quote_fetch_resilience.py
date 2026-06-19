import unittest

import jarvis.runtime.public_universe_quote_fetcher as fetcher


class TestJarvisV122QuoteFetchResilience(unittest.TestCase):
    def test_coingecko_markets_batch_builds_multiple_records(self):
        original = fetcher._fetch_json

        def fake_fetch_json(url: str, timeout: int = 20):
            self.assertIn("/coins/markets", url)
            self.assertIn("price_change_percentage=24h,7d,30d", url)
            return [
                {
                    "id": "bitcoin",
                    "current_price": 60000.0,
                    "last_updated": "2026-06-20T00:00:00.000Z",
                    "price_change_percentage_24h_in_currency": 1.0,
                    "price_change_percentage_7d_in_currency": 2.0,
                    "price_change_percentage_30d_in_currency": 3.0,
                },
                {
                    "id": "solana",
                    "current_price": 140.0,
                    "last_updated": "2026-06-20T00:00:00.000Z",
                    "price_change_percentage_24h_in_currency": -1.0,
                    "price_change_percentage_7d_in_currency": -2.0,
                    "price_change_percentage_30d_in_currency": -3.0,
                },
            ]

        try:
            fetcher._fetch_json = fake_fetch_json
            records, failures = fetcher.fetch_coingecko_markets_quotes(
                [
                    fetcher.QuoteFetchTarget("BTC", "crypto", "coingecko_read_only", "bitcoin", False, None),
                    fetcher.QuoteFetchTarget("SOL", "crypto", "coingecko_read_only", "solana", False, None),
                ],
                current_date="2026-06-20",
            )
        finally:
            fetcher._fetch_json = original

        self.assertEqual(failures, [])
        by_symbol = {record.symbol: record for record in records}
        self.assertEqual(by_symbol["BTC"].movement_7d_pct, 2.0)
        self.assertEqual(by_symbol["SOL"].movement_30d_pct, -3.0)
        self.assertEqual(by_symbol["BTC"].freshness, "ready")

    def test_core_crypto_refresh_symbols_are_fetch_targets(self):
        targets, unresolved = fetcher.build_quote_fetch_targets(current_date="2026-06-20")
        symbols = {target.symbol for target in targets}
        self.assertIn("BTC", symbols)
        self.assertIn("ETH", symbols)
        self.assertIn("GROWTH_NASDAQ_ETF", unresolved)

    def test_cache_merge_preserves_existing_records(self):
        existing = [{"symbol": "VWCE", "quote_price": 165.44}]
        new = [{"symbol": "BTC", "quote_price": 60000.0}, {"symbol": "VWCE", "quote_price": 166.0}]
        merged = fetcher._merge_cache_records(existing, new)
        by_symbol = {row["symbol"]: row for row in merged}
        self.assertEqual(by_symbol["BTC"]["quote_price"], 60000.0)
        self.assertEqual(by_symbol["VWCE"]["quote_price"], 166.0)


if __name__ == "__main__":
    unittest.main()
