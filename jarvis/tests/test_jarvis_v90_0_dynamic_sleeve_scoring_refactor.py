from __future__ import annotations

import unittest

from jarvis.runtime.dynamic_quality_allocator import build_dynamic_quality_allocator_result
from jarvis.runtime.product_mode_operator import build_product_mode_result


class JarvisV900DynamicSleeveScoringTests(unittest.TestCase):
    def test_allocator_keeps_only_crypto_cap_static_and_scores_stock(self) -> None:
        result = build_dynamic_quality_allocator_result(current_date="2026-06-18")

        self.assertEqual(result.status, "JARVIS_V90_0_DYNAMIC_SLEEVE_SCORING_READY_SAFE")
        self.assertEqual(result.crypto_eur, 100.0)
        self.assertEqual(result.etf_fund_eur, 275.0)
        self.assertEqual(result.individual_stock_eur, 50.0)
        self.assertTrue(any("score-based" in line for line in result.rationale))
        self.assertFalse(result.approved_for_purchase)
        self.assertFalse(result.trade_executed)

    def test_product_mode_shows_score_based_stock_note(self) -> None:
        result = build_product_mode_result(mode="week", current_date="2026-06-18")
        text = "\n".join(result.week_lines)

        self.assertEqual(result.status, "JARVIS_V90_0_DYNAMIC_SLEEVE_SCORING_READY_SAFE")
        self.assertIn("Crypto lane: EUR 100.00", text)
        self.assertIn("ETF/fund lane: EUR 275.00", text)
        self.assertIn("Individual stock lane: EUR 50.00", text)
        self.assertIn("stock sleeve is score-based", text)
        self.assertEqual(result.blockers, [])


if __name__ == "__main__":
    unittest.main()
