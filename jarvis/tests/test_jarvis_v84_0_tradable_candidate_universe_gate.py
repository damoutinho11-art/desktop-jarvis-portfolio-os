from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import jarvis.runtime.tradable_candidate_universe_gate as gate


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


class JarvisV840TradableCandidateUniverseGateTests(unittest.TestCase):
    def test_blocks_when_stock_universe_is_too_narrow_and_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data.json"
            _write_json(
                data,
                {
                    "crypto": ["BTC", "ETH", "SOL", "HYPE", "LINK", "AVAX"],
                    "etfs": ["QUALITY_ETF", "GLOBAL_CORE_ETF", "SXR8"],
                    "stocks": ["MSFT", "META"],
                },
            )

            old_paths = gate.DEFAULT_PATHS
            gate.DEFAULT_PATHS = [str(data)]
            try:
                fake_freshness = SimpleNamespace(missing_freshness=["stock_data_freshness_with_as_of"])
                with patch.object(gate, "build_data_freshness_acquisition_gate_result", return_value=fake_freshness):
                    result = gate.build_tradable_candidate_universe_gate_result(current_date="2026-06-18")
            finally:
                gate.DEFAULT_PATHS = old_paths

        self.assertFalse(result.dynamic_allocator_allowed)
        self.assertFalse(result.universe_gate_ready)
        self.assertGreaterEqual(result.crypto_candidate_count, gate.MIN_CRYPTO)
        self.assertGreaterEqual(result.etf_candidate_count, gate.MIN_ETF)
        self.assertLess(result.stock_candidate_count, gate.MIN_STOCK)
        self.assertIn("stock_candidates_2_of_5", result.missing_breadth)
        self.assertIn("stock_data_freshness_with_as_of", result.missing_freshness)
        self.assertIn("stock_candidates_2_of_5", result.blockers)

    def test_allows_dynamic_allocator_when_breadth_and_freshness_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data.json"
            _write_json(
                data,
                {
                    "crypto": ["BTC", "ETH", "SOL", "HYPE", "LINK"],
                    "etfs": ["QUALITY_ETF", "GLOBAL_CORE_ETF", "SXR8"],
                    "stocks": ["MSFT", "META", "AAPL", "NVDA", "GOOGL"],
                },
            )

            old_paths = gate.DEFAULT_PATHS
            gate.DEFAULT_PATHS = [str(data)]
            try:
                fake_freshness = SimpleNamespace(missing_freshness=[])
                with patch.object(gate, "build_data_freshness_acquisition_gate_result", return_value=fake_freshness):
                    result = gate.build_tradable_candidate_universe_gate_result(current_date="2026-06-18")
            finally:
                gate.DEFAULT_PATHS = old_paths

        self.assertTrue(result.universe_gate_ready)
        self.assertTrue(result.dynamic_allocator_allowed)
        self.assertEqual(result.missing_breadth, [])
        self.assertEqual(result.missing_freshness, [])
        self.assertEqual(result.blockers, [])

    def test_safety_flags_remain_manual_only(self) -> None:
        result = gate.build_tradable_candidate_universe_gate_result(current_date="2026-06-18")

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
