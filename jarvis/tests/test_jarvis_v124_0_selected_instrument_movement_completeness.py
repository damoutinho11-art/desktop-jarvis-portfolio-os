import unittest

from jarvis.runtime.public_universe_quote_fetcher import (
    SELECTED_ETF_MOVEMENT_REFRESH_SYMBOLS,
    build_quote_fetch_targets,
)


class TestJarvisV124SelectedInstrumentMovementCompleteness(unittest.TestCase):
    def test_selected_etf_movement_refresh_symbols_are_declared(self):
        self.assertEqual(
            SELECTED_ETF_MOVEMENT_REFRESH_SYMBOLS,
            ("GLOBAL_CORE_ETF", "IS3Q.DE", "VWCE"),
        )

    def test_selected_etfs_are_quote_fetch_targets_for_movement_completeness(self):
        targets, unresolved = build_quote_fetch_targets(current_date="2026-06-20")
        by_symbol = {target.symbol: target for target in targets}

        self.assertIn("BTC", by_symbol)
        self.assertIn("ETH", by_symbol)
        self.assertIn("GLOBAL_CORE_ETF", by_symbol)
        self.assertIn("IS3Q.DE", by_symbol)
        self.assertIn("VWCE", by_symbol)

        self.assertEqual(by_symbol["IS3Q.DE"].provider, "yahoo_chart_read_only")
        self.assertEqual(by_symbol["IS3Q.DE"].provider_symbol, "IS3Q.DE")
        self.assertNotIn("GROWTH_NASDAQ_ETF", unresolved)

    def test_selected_etf_refresh_is_manual_only(self):
        targets, _unresolved = build_quote_fetch_targets(current_date="2026-06-20")
        by_symbol = {target.symbol: target for target in targets}

        self.assertFalse(by_symbol["IS3Q.DE"].manual_review_required)
        self.assertEqual(by_symbol["GLOBAL_CORE_ETF"].provider, "yahoo_chart_read_only")
        self.assertEqual(by_symbol["VWCE"].provider, "yahoo_chart_read_only")


if __name__ == "__main__":
    unittest.main()
