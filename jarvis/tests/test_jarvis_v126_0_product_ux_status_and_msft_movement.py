import unittest

from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.public_universe_quote_fetcher import (
    SELECTED_STOCK_MOVEMENT_REFRESH_SYMBOLS,
    build_quote_fetch_targets,
)


class TestJarvisV126ProductUXStatusAndMSFTMovement(unittest.TestCase):
    def test_product_mode_unresolved_import_note_is_not_manual_use_blocker(self):
        result = build_product_mode_result(mode="status", current_date="2026-06-20")
        data = result.to_dict()

        self.assertEqual(data["status"], "JARVIS_V126_0_PRODUCT_UX_STATUS_AND_MSFT_MOVEMENT_READY_SAFE")
        self.assertEqual(data.get("blockers") or [], [])
        self.assertNotIn("unresolved local imports: 1", data.get("blockers") or [])
        self.assertTrue(data["safety_check_blocked_execution"])
        self.assertFalse(data["broker_connection"])
        self.assertFalse(data["order_created"])
        self.assertFalse(data["trade_executed"])

    def test_msft_is_declared_for_selected_stock_movement_refresh(self):
        self.assertEqual(SELECTED_STOCK_MOVEMENT_REFRESH_SYMBOLS, ("MSFT",))

    def test_msft_is_quote_fetch_target_for_movement_completeness(self):
        targets, unresolved = build_quote_fetch_targets(current_date="2026-06-20")
        by_symbol = {target.symbol: target for target in targets}

        self.assertIn("MSFT", by_symbol)
        self.assertEqual(by_symbol["MSFT"].provider, "yahoo_chart_read_only")
        self.assertEqual(by_symbol["MSFT"].provider_symbol, "MSFT")
        self.assertNotIn("MSFT", unresolved)


if __name__ == "__main__":
    unittest.main()
