from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.data_readiness_status import (
    STATUS_READY,
    build_data_readiness_status_result,
    format_data_readiness_status,
)


class JarvisV950DataReadinessStatusTests(unittest.TestCase):
    def test_status_aggregates_existing_gates(self) -> None:
        result = build_data_readiness_status_result(current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.data_readiness_ready)
        self.assertTrue(result.product_recommendations_allowed)
        self.assertTrue(result.freshness_ready)
        self.assertTrue(result.universe_ready)
        self.assertTrue(result.preflight_ready)
        self.assertTrue(result.dynamic_allocator_allowed)
        self.assertEqual(result.blockers, [])

    def test_reports_lane_data_and_candidate_counts(self) -> None:
        result = build_data_readiness_status_result(current_date="2026-06-18")

        self.assertTrue(result.crypto_data_ready)
        self.assertTrue(result.etf_fund_data_ready)
        self.assertTrue(result.stock_data_ready)
        self.assertGreaterEqual(result.crypto_candidate_count, result.crypto_candidate_minimum)
        self.assertGreaterEqual(result.etf_candidate_count, result.etf_candidate_minimum)
        self.assertGreaterEqual(result.stock_candidate_count, result.stock_candidate_minimum)

    def test_safety_remains_manual_only(self) -> None:
        result = build_data_readiness_status_result(current_date="2026-06-18")

        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_format_is_dashboard_chat_ready(self) -> None:
        result = build_data_readiness_status_result(current_date="2026-06-18")
        output = format_data_readiness_status(result)

        self.assertIn("J.A.R.V.I.S. DATA READINESS STATUS", output)
        self.assertIn("verdict: READY_FOR_PRODUCT_RECOMMENDATIONS", output)
        self.assertIn("DATA LANES:", output)
        self.assertIn("CANDIDATE UNIVERSE:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_routes_v95_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v95.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "data_readiness_status")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--data-readiness-status", source)
        self.assertIn("_data_readiness_status_main", source)


if __name__ == "__main__":
    unittest.main()
