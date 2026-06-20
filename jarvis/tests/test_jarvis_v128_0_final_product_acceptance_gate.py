import unittest

from jarvis.runtime.final_product_acceptance_gate import (
    build_final_product_acceptance_gate_result,
    format_final_product_acceptance_gate,
)


class TestJarvisV128FinalProductAcceptanceGate(unittest.TestCase):
    def test_final_product_acceptance_gate_is_ready_safe(self):
        result = build_final_product_acceptance_gate_result(current_date="2026-06-20")

        self.assertEqual(result.status, "JARVIS_V128_0_FINAL_PRODUCT_ACCEPTANCE_GATE_READY_SAFE")
        self.assertTrue(result.final_acceptance_ready)
        self.assertTrue(result.product_mode_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.assistant_aliases_ready)
        self.assertTrue(result.assistant_answers_ready)
        self.assertTrue(result.msft_movement_ready)
        self.assertTrue(result.quote_targets_ready)
        self.assertTrue(result.safety_ready)
        self.assertEqual(result.blockers, [])

    def test_final_product_acceptance_format_is_user_facing(self):
        result = build_final_product_acceptance_gate_result(current_date="2026-06-20")
        text = format_final_product_acceptance_gate(result)

        self.assertIn("J.A.R.V.I.S. FINAL PRODUCT ACCEPTANCE GATE", text)
        self.assertIn("final acceptance ready: True", text)
        self.assertIn("product mode ready: True", text)
        self.assertIn("dashboard ready: True", text)
        self.assertIn("MSFT movement ready: True", text)
        self.assertIn("BLOCKERS:", text)
        self.assertIn("- none", text)
        self.assertIn("No broker, credential, order, trade, or auto-approval", text)


if __name__ == "__main__":
    unittest.main()
