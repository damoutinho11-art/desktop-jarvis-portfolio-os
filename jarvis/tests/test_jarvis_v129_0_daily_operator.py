import unittest

from jarvis.runtime.daily_operator import build_daily_operator_result, format_daily_operator
from jarvis.runtime.final_product_acceptance_gate import build_final_product_acceptance_gate_result
from jarvis.runtime.product_mode_operator import build_product_mode_result


class TestJarvisV129DailyOperator(unittest.TestCase):
    def test_daily_operator_ready_safe_without_live_refresh(self):
        result = build_daily_operator_result(
            current_date="2026-06-20",
            refresh_quotes=False,
            write_dashboard=False,
        )

        self.assertEqual(result.status, "JARVIS_V129_0_DAILY_OPERATOR_READY_SAFE")
        self.assertTrue(result.daily_operator_ready)
        self.assertFalse(result.quote_refresh_attempted)
        self.assertTrue(result.final_acceptance_ready)
        self.assertTrue(result.product_mode_ready)
        self.assertTrue(result.safety_ready)
        self.assertEqual(result.blockers, [])

    def test_daily_operator_format_is_user_facing_and_no_legacy_import_noise(self):
        result = build_daily_operator_result(
            current_date="2026-06-20",
            refresh_quotes=False,
            write_dashboard=False,
        )
        text = format_daily_operator(result)

        self.assertIn("J.A.R.V.I.S. DAILY OPERATOR", text)
        self.assertIn("daily operator ready: True", text)
        self.assertIn("final acceptance ready: True", text)
        self.assertIn("Open dashboard:", text)
        self.assertNotIn("unresolved local imports", text)

    def test_final_and_product_warnings_do_not_show_legacy_import_noise(self):
        final_gate = build_final_product_acceptance_gate_result(current_date="2026-06-20")
        product = build_product_mode_result(mode="status", current_date="2026-06-20")
        product_data = product.to_dict()

        self.assertTrue(final_gate.final_acceptance_ready)
        self.assertFalse(any("unresolved local imports" in warning for warning in final_gate.warnings))
        self.assertFalse(any("unresolved local imports" in warning for warning in product_data.get("warnings", [])))


if __name__ == "__main__":
    unittest.main()
