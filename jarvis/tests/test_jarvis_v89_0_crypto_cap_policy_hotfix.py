from __future__ import annotations

import unittest

from jarvis.runtime.dynamic_quality_allocator import build_dynamic_quality_allocator_result
from jarvis.runtime.product_mode_operator import build_product_mode_result


class JarvisV890CryptoCapPolicyTests(unittest.TestCase):
    def test_allocator_caps_crypto_at_20_percent_of_contribution(self) -> None:
        result = build_dynamic_quality_allocator_result(current_date="2026-06-18")

        self.assertEqual(result.status, "JARVIS_V89_0_CRYPTO_CAP_POLICY_READY_SAFE")
        self.assertEqual(result.monthly_contribution_eur, 500.0)
        self.assertEqual(result.emergency_top_up_eur, 75.0)
        self.assertEqual(result.crypto_eur, 100.0)
        self.assertEqual(result.etf_fund_eur, 275.0)
        self.assertEqual(result.individual_stock_eur, 50.0)
        self.assertEqual(result.total_allocated_eur, 500.0)
        self.assertFalse(result.approved_for_purchase)
        self.assertFalse(result.trade_executed)

    def test_product_mode_uses_crypto_cap_policy_split(self) -> None:
        result = build_product_mode_result(mode="week", current_date="2026-06-18")

        self.assertEqual(result.status, "JARVIS_V89_0_CRYPTO_CAP_POLICY_READY_SAFE")
        self.assertEqual(result.recommended_crypto_eur, 100.0)
        self.assertEqual(result.recommended_etf_fund_eur, 275.0)
        self.assertEqual(result.recommended_individual_stock_eur, 50.0)
        self.assertEqual(result.blockers, [])


if __name__ == "__main__":
    unittest.main()
