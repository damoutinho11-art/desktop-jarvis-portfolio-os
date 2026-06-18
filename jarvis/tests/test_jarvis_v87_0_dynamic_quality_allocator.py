from __future__ import annotations

import unittest
from unittest.mock import patch

from jarvis.runtime.dynamic_quality_allocator import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_dynamic_quality_allocator_result,
)

READY_PREFLIGHT = {"dynamic_allocator_allowed": True, "stock_lane_ready": True, "universe_ready": True, "freshness_ready": True}
BAD_PREFLIGHT = {"dynamic_allocator_allowed": False}

CONTRIBUTION = {
    "monthly_contribution_eur": 500.0,
    "suggested_monthly_emergency_top_up_eur": 75.0,
    "crypto_amount_eur": 170.0,
}

HIGH_EQUITY = {
    "exposure_weights": {
        "equity": 0.9804,
        "us_large_cap": 0.6154,
    }
}


class JarvisV870DynamicQualityAllocatorTests(unittest.TestCase):
    def _run(self, preflight=READY_PREFLIGHT):
        with patch("jarvis.runtime.dynamic_quality_allocator.build_cross_lane_dynamic_allocation_preflight_result", return_value=preflight), \
             patch("jarvis.runtime.dynamic_quality_allocator.build_personal_finance_contribution_bridge_result", return_value=CONTRIBUTION), \
             patch("jarvis.runtime.dynamic_quality_allocator.build_correlation_risk_model_result", return_value=HIGH_EQUITY):
            return build_dynamic_quality_allocator_result(current_date="2026-06-18")

    def test_recommends_conservative_split(self) -> None:
        result = self._run()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.allocator_ready)
        self.assertEqual(result.emergency_top_up_eur, 75.0)
        self.assertEqual(result.crypto_eur, 100.0)
        self.assertEqual(result.etf_fund_eur, 275.0)
        self.assertEqual(result.individual_stock_eur, 50.0)
        self.assertEqual(result.total_allocated_eur, 500.0)
        self.assertFalse(result.approved_for_purchase)
        self.assertEqual(result.blockers, [])

    def test_blocks_when_preflight_not_ready(self) -> None:
        result = self._run(BAD_PREFLIGHT)

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.allocator_ready)
        self.assertIn("cross_lane_preflight_not_ready", result.blockers)

    def test_safety_flags_remain_recommendation_only(self) -> None:
        result = self._run()

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.approved_for_purchase)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)


if __name__ == "__main__":
    unittest.main()
