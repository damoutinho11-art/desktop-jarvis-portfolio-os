from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.data_freshness_acquisition_gate import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_data_freshness_acquisition_gate_result,
)
from jarvis.runtime.product_mode_operator import build_product_mode_result


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


class JarvisV830DataFreshnessAcquisitionGateTests(unittest.TestCase):
    def _sample_paths(self, tmp: str, *, stock_as_of: str | None) -> dict[str, Path]:
        root = Path(tmp)
        cache = root / "cache.json"
        evidence = root / "evidence.json"
        ticket = root / "ticket.json"
        cost = root / "cost.json"
        expenses = root / "expenses.json"

        _write_json(
            cache,
            {
                "records": [
                    {"source": "coingecko_free_or_demo", "lane": "crypto", "status": "PUBLIC_CRYPTO_SOURCE_READY", "usable": True},
                    {"source": "ecb_fx_official", "lane": "fx", "status": "OFFICIAL_FREE_SOURCE_READY", "usable": True},
                ]
            },
        )
        _write_json(evidence, {"items": []})

        stock_row = {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "close_price": 378.91,
            "currency": "USD",
            "source": "public_stock_quote",
        }
        if stock_as_of is not None:
            stock_row["as_of"] = stock_as_of

        _write_json(
            ticket,
            {
                "ranked_candidates": [stock_row],
                "selected_etf": {"symbol": "IS3Q.DE", "kind": "ETF", "status": "READY", "price": 10.0, "as_of": "2026-06-18"},
            },
        )
        _write_json(
            cost,
            {
                "positions": [
                    {"symbol": "BTC", "market_value_eur": 20.18},
                    {"symbol": "SXR8", "market_value_eur": 633.01},
                ]
            },
        )
        _write_json(
            expenses,
            {
                "planned_monthly_contribution_eur": 500.0,
                "normal_monthly_expenses_eur": 1048.0,
                "survival_monthly_expenses_eur": 805.0,
            },
        )

        return {
            "cache_path": cache,
            "evidence_pack_path": evidence,
            "approval_ticket_path": ticket,
            "cost_basis_path": cost,
            "expenses_path": expenses,
        }

    def test_blocks_dynamic_allocator_when_stock_as_of_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._sample_paths(tmp, stock_as_of=None)
            result = build_data_freshness_acquisition_gate_result(current_date="2026-06-18", **paths)

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.dynamic_allocator_allowed)
        self.assertTrue(result.crypto_data_fresh)
        self.assertTrue(result.fx_data_fresh)
        self.assertTrue(result.etf_fund_data_fresh)
        self.assertFalse(result.stock_data_fresh)
        self.assertTrue(result.portfolio_data_fresh)
        self.assertTrue(result.monthly_expenses_data_fresh)
        self.assertEqual(result.missing_freshness, ["stock_data_freshness_with_as_of"])

    def test_allows_dynamic_allocator_when_all_freshness_lanes_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._sample_paths(tmp, stock_as_of="2026-06-18")
            result = build_data_freshness_acquisition_gate_result(current_date="2026-06-18", **paths)

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.freshness_gate_ready)
        self.assertTrue(result.dynamic_allocator_allowed)
        self.assertEqual(result.missing_freshness, [])
        self.assertEqual(result.blockers, [])

    def test_safety_flags_remain_manual_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._sample_paths(tmp, stock_as_of=None)
            result = build_data_freshness_acquisition_gate_result(**paths)

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_product_mode_remains_ready_even_when_dynamic_allocator_is_blocked(self) -> None:
        result = build_product_mode_result(mode="status", current_date="2026-06-18")

        self.assertTrue(result.product_ready_for_manual_use)
        self.assertEqual(result.blockers, [])
        self.assertEqual(result.full_allocation_blockers, [])


if __name__ == "__main__":
    unittest.main()
