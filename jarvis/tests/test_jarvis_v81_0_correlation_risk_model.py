from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.correlation_risk_model import (
    MODEL_READY,
    STATUS_READY,
    build_correlation_risk_model_result,
)
from jarvis.runtime.product_mode_operator import build_product_mode_result


class JarvisV810CorrelationRiskModelTests(unittest.TestCase):
    def _sample_cost_basis(self, path: Path) -> None:
        payload = {
            "positions": [
                {"symbol": "BTC", "market_value_eur": 20.18},
                {"symbol": "SXR8", "market_value_eur": 633.01},
                {"symbol": "XCHA", "market_value_eur": 128.47},
                {"symbol": "IEMM", "market_value_eur": 373.55},
            ]
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_sample_positions_are_classified_and_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cost_basis = Path(tmp) / "cost_basis.json"
            snapshot = Path(tmp) / "snapshot.json"
            self._sample_cost_basis(cost_basis)
            snapshot.write_text("{}", encoding="utf-8")

            result = build_correlation_risk_model_result(
                current_date="2026-06-17",
                cost_basis_path=cost_basis,
                portfolio_snapshot_path=snapshot,
            )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.model_status, MODEL_READY)
        self.assertTrue(result.correlation_model_ready)
        self.assertEqual(result.position_count, 4)
        self.assertIn("crypto", result.exposure_weights)
        self.assertIn("equity", result.exposure_weights)
        self.assertIn("us_large_cap", result.exposure_weights)
        self.assertIn("emerging_markets", result.exposure_weights)
        self.assertIn("global_developed", result.exposure_weights)
        self.assertEqual(result.remaining_full_allocation_blockers, [])
        self.assertEqual(result.blockers, [])

    def test_safety_flags_remain_manual_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cost_basis = Path(tmp) / "cost_basis.json"
            snapshot = Path(tmp) / "snapshot.json"
            self._sample_cost_basis(cost_basis)
            snapshot.write_text("{}", encoding="utf-8")

            result = build_correlation_risk_model_result(
                cost_basis_path=cost_basis,
                portfolio_snapshot_path=snapshot,
            )

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_product_mode_no_longer_lists_correlation_as_full_allocation_blocker(self) -> None:
        result = build_product_mode_result(mode="status", current_date="2026-06-17")

        self.assertNotIn("correlation_risk_model", result.full_allocation_blockers)
        self.assertIn("stock_specific_public_evidence", result.full_allocation_blockers)
        self.assertTrue(result.product_ready_for_manual_use)


if __name__ == "__main__":
    unittest.main()
