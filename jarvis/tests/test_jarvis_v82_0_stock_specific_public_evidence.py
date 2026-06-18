from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.stock_specific_public_evidence import (
    EVIDENCE_READY,
    STATUS_READY,
    build_stock_specific_public_evidence_result,
)
from jarvis.runtime.product_mode_operator import build_product_mode_result


class JarvisV820StockSpecificPublicEvidenceTests(unittest.TestCase):
    def test_sample_msft_public_evidence_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ranked = Path(tmp) / "ranked.json"
            signals = Path(tmp) / "signals.json"
            ticket = Path(tmp) / "ticket.json"

            ranked.write_text(
                json.dumps(
                    {
                        "ranked_candidates": [
                            {
                                "symbol": "MSFT",
                                "name": "Microsoft Corporation",
                                "close_price": 393.83,
                                "currency": "USD",
                                "source": "public_stock_quote",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            signals.write_text("{}", encoding="utf-8")
            ticket.write_text("{}", encoding="utf-8")

            result = build_stock_specific_public_evidence_result(
                current_date="2026-06-17",
                ranked_candidates_path=ranked,
                stock_signals_path=signals,
                approval_ticket_path=ticket,
            )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.evidence_status, EVIDENCE_READY)
        self.assertTrue(result.stock_specific_public_evidence_ready)
        self.assertEqual(result.top_stock_symbol, "MSFT")
        self.assertEqual(result.public_price, 393.83)
        self.assertTrue(result.stock_review_allowed)
        self.assertFalse(result.approved_for_purchase)
        self.assertTrue(result.manual_amount_required)
        self.assertEqual(result.remaining_full_allocation_blockers, [])
        self.assertEqual(result.blockers, [])

    def test_safety_flags_remain_manual_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ranked = Path(tmp) / "ranked.json"
            signals = Path(tmp) / "signals.json"
            ticket = Path(tmp) / "ticket.json"

            ranked.write_text(
                json.dumps({"ranked_candidates": [{"symbol": "MSFT", "close_price": 393.83}]}),
                encoding="utf-8",
            )
            signals.write_text("{}", encoding="utf-8")
            ticket.write_text("{}", encoding="utf-8")

            result = build_stock_specific_public_evidence_result(
                ranked_candidates_path=ranked,
                stock_signals_path=signals,
                approval_ticket_path=ticket,
            )

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_product_mode_has_no_full_allocation_blockers_after_stock_evidence(self) -> None:
        result = build_product_mode_result(mode="status", current_date="2026-06-17")

        self.assertTrue(result.product_ready_for_manual_use)
        self.assertEqual(result.full_allocation_blockers, [])
        self.assertEqual(result.blockers, [])
        self.assertEqual(result.unresolved_local_import_count, 0)

    def test_stock_lane_is_still_not_auto_approved_or_allocated(self) -> None:
        result = build_product_mode_result(mode="week", current_date="2026-06-17")

        self.assertTrue(result.product_ready_for_manual_use)
        self.assertEqual(result.recommended_individual_stock_eur, 50.0)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)


if __name__ == "__main__":
    unittest.main()
