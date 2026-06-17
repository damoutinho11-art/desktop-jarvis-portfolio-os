from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from jarvis.runtime.product_mode_operator import (
    STATUS_READY,
    build_product_mode_result,
    main,
)


class JarvisV800ProductOutputQualityTests(unittest.TestCase):
    def test_today_output_has_real_numbers_and_manual_plan(self) -> None:
        result = build_product_mode_result(mode="today", current_date="2026-06-17")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.product_ready_for_manual_use)
        text = "\n".join(result.today_lines)

        self.assertIn("EUR 3600.00", text)
        self.assertIn("EUR 3144.00", text)
        self.assertIn("EUR 6288.00", text)
        self.assertIn("EUR 75.00", text)
        self.assertIn("EUR 170.00", text)
        self.assertIn("EUR 255.00", text)
        self.assertIn("manual", text.lower())
        self.assertNotIn("unknown", text.lower())

    def test_week_output_is_clear_manual_buy_plan(self) -> None:
        result = build_product_mode_result(mode="week", current_date="2026-06-17")

        text = "\n".join(result.week_lines)

        self.assertIn("Manual buy plan", text)
        self.assertIn("Emergency top-up: EUR 75.00", text)
        self.assertIn("Crypto lane: EUR 170.00", text)
        self.assertIn("ETF/fund lane: EUR 255.00", text)
        self.assertIn("Individual stock lane: EUR 0.00", text)
        self.assertIn("creates no orders", text)
        self.assertNotIn("unknown", text.lower())

    def test_status_output_filters_noisy_internal_component_blockers(self) -> None:
        result = build_product_mode_result(mode="status", current_date="2026-06-17")

        text = "\n".join(result.status_lines)

        self.assertIn("Product readiness: READY_FOR_MANUAL_USE", text)
        self.assertIn("Unresolved local imports: 0", text)
        self.assertIn("Legacy module archive candidates: 0", text)
        self.assertIn("Full allocation blockers: stock_specific_public_evidence", text)
        self.assertIn("Product-mode blockers: none", text)
        self.assertNotIn("monthly_expenses_required_for_dynamic_target_policy", text)
        self.assertNotIn("monthly_contribution_required_for_dynamic_target_policy", text)

    def test_cli_week_is_human_readable(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["--week", "--current-date", "2026-06-17"])

        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("J.A.R.V.I.S. WEEK", output)
        self.assertIn("Manual buy plan", output)
        self.assertIn("EUR 75.00", output)
        self.assertIn("EUR 170.00", output)
        self.assertIn("EUR 255.00", output)
        self.assertNotIn("unknown", output.lower())

    def test_safety_flags_remain_manual_only(self) -> None:
        result = build_product_mode_result(mode="today", current_date="2026-06-17")

        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)


if __name__ == "__main__":
    unittest.main()
