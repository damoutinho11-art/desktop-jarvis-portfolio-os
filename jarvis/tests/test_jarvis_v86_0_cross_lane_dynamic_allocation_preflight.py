from __future__ import annotations

import unittest
from unittest.mock import patch

from jarvis.runtime.cross_lane_dynamic_allocation_preflight import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_cross_lane_dynamic_allocation_preflight_result,
)

READY_FRESHNESS = {"status": "X_READY_SAFE", "dynamic_allocator_allowed": True}
READY_UNIVERSE = {
    "status": "X_READY_SAFE",
    "dynamic_allocator_allowed": True,
    "crypto_candidate_count": 10,
    "etf_candidate_count": 13,
    "stock_candidate_count": 25,
}
READY_CONTRIBUTION = {
    "trusted_monthly_contribution_decision_allowed": True,
    "monthly_expenses_confirmed": True,
    "snapshot_ready": True,
    "manual_cost_basis_ready": True,
    "blockers": [],
}
READY_CORRELATION = {"correlation_model_ready": True, "blockers": []}
READY_PRODUCT = {"status": "X_READY_SAFE", "verdict": "READY_FOR_MANUAL_USE"}


class JarvisV860CrossLaneDynamicAllocationPreflightTests(unittest.TestCase):
    def _run_with(self, contribution=READY_CONTRIBUTION):
        with patch("jarvis.runtime.cross_lane_dynamic_allocation_preflight.build_data_freshness_acquisition_gate_result", return_value=READY_FRESHNESS), \
             patch("jarvis.runtime.cross_lane_dynamic_allocation_preflight.build_tradable_candidate_universe_gate_result", return_value=READY_UNIVERSE), \
             patch("jarvis.runtime.cross_lane_dynamic_allocation_preflight.build_personal_finance_contribution_bridge_result", return_value=contribution), \
             patch("jarvis.runtime.cross_lane_dynamic_allocation_preflight.build_correlation_risk_model_result", return_value=READY_CORRELATION), \
             patch("jarvis.runtime.cross_lane_dynamic_allocation_preflight.build_product_mode_result", return_value=READY_PRODUCT):
            return build_cross_lane_dynamic_allocation_preflight_result(current_date="2026-06-18")

    def test_ready_when_all_cross_lane_inputs_are_ready(self) -> None:
        result = self._run_with()
        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.preflight_ready)
        self.assertTrue(result.dynamic_allocator_allowed)
        self.assertEqual(result.blockers, [])

    def test_blocks_when_contribution_is_not_ready(self) -> None:
        bad = dict(READY_CONTRIBUTION)
        bad["trusted_monthly_contribution_decision_allowed"] = False

        result = self._run_with(contribution=bad)

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.dynamic_allocator_allowed)
        self.assertIn("contribution_not_ready", result.blockers)

    def test_safety_flags_remain_manual_only(self) -> None:
        result = self._run_with()
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
