from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis.runtime.stock_candidate_universe_expansion import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_stock_candidate_universe_expansion_result,
)


def fake_quote(symbol: str):
    return {
        "symbol": symbol,
        "name": symbol,
        "close_price": 100.0,
        "currency": "USD",
        "as_of": "2026-06-17",
        "source": "yahoo_chart_public",
        "asset_type": "stock",
        "public_source_ready": True,
        "approved_for_purchase": False,
        "buy_request_created": False,
        "order_created": False,
        "trade_executed": False,
    }


class JarvisV850StockCandidateUniverseExpansionTests(unittest.TestCase):
    def test_expands_stock_universe_with_five_fresh_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "stocks.json"
            with patch(
                "jarvis.runtime.stock_candidate_universe_expansion.fetch_yahoo_chart_quote",
                side_effect=fake_quote,
            ):
                result = build_stock_candidate_universe_expansion_result(
                    current_date="2026-06-18",
                    symbols=["MSFT", "META", "AAPL", "NVDA", "GOOGL"],
                    write_candidates=True,
                    output_path=str(output),
                )

            self.assertTrue(output.exists())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.stock_universe_ready)
        self.assertEqual(result.fresh_candidate_count, 5)
        self.assertTrue(result.output_written)
        self.assertEqual(result.blockers, [])

    def test_blocks_when_stock_universe_is_too_small(self) -> None:
        with patch(
            "jarvis.runtime.stock_candidate_universe_expansion.fetch_yahoo_chart_quote",
            side_effect=fake_quote,
        ):
            result = build_stock_candidate_universe_expansion_result(
                current_date="2026-06-18",
                symbols=["MSFT", "META"],
                min_required_candidates=5,
            )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.stock_universe_ready)
        self.assertIn("fresh_stock_candidates_2_of_5", result.blockers)

    def test_safety_flags_remain_manual_only(self) -> None:
        with patch(
            "jarvis.runtime.stock_candidate_universe_expansion.fetch_yahoo_chart_quote",
            side_effect=fake_quote,
        ):
            result = build_stock_candidate_universe_expansion_result(
                symbols=["MSFT", "META", "AAPL", "NVDA", "GOOGL"],
            )

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)


if __name__ == "__main__":
    unittest.main()
