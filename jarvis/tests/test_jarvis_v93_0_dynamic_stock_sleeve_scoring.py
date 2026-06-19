from __future__ import annotations

import unittest

from jarvis.runtime.dynamic_quality_allocator import (
    STATUS_READY,
    score_dynamic_stock_sleeve,
)


class JarvisV930DynamicStockSleeveScoringTests(unittest.TestCase):
    def test_current_concentration_keeps_stock_conservative(self) -> None:
        score = score_dynamic_stock_sleeve(
            stock_lane_ready=True,
            universe_ready=True,
            freshness_ready=True,
            equity_weight=0.98,
            us_large_cap_weight=0.62,
            investable_eur=425.0,
        )

        self.assertEqual(score.stock_eur_after_rounding, 50.0)
        self.assertAlmostEqual(score.final_stock_pct, 0.115)
        self.assertLess(score.concentration_score, 1.0)

    def test_low_concentration_allows_stock_sleeve_to_rise(self) -> None:
        current = score_dynamic_stock_sleeve(
            stock_lane_ready=True,
            universe_ready=True,
            freshness_ready=True,
            equity_weight=0.98,
            us_large_cap_weight=0.62,
            investable_eur=425.0,
        )
        low_risk = score_dynamic_stock_sleeve(
            stock_lane_ready=True,
            universe_ready=True,
            freshness_ready=True,
            equity_weight=0.55,
            us_large_cap_weight=0.25,
            investable_eur=425.0,
        )

        self.assertGreater(low_risk.final_stock_pct, current.final_stock_pct)
        self.assertGreater(low_risk.stock_eur_after_rounding, current.stock_eur_after_rounding)

    def test_stock_lane_not_ready_forces_zero_stock(self) -> None:
        score = score_dynamic_stock_sleeve(
            stock_lane_ready=False,
            universe_ready=True,
            freshness_ready=True,
            equity_weight=0.55,
            us_large_cap_weight=0.25,
            investable_eur=425.0,
        )

        self.assertEqual(score.stock_quality_score, 0.0)
        self.assertEqual(score.final_stock_pct, 0.0)
        self.assertEqual(score.stock_eur_after_rounding, 0.0)

    def test_missing_universe_or_freshness_reduces_availability_score(self) -> None:
        ready = score_dynamic_stock_sleeve(
            stock_lane_ready=True,
            universe_ready=True,
            freshness_ready=True,
            equity_weight=0.55,
            us_large_cap_weight=0.25,
            investable_eur=425.0,
        )
        weaker = score_dynamic_stock_sleeve(
            stock_lane_ready=True,
            universe_ready=False,
            freshness_ready=False,
            equity_weight=0.55,
            us_large_cap_weight=0.25,
            investable_eur=425.0,
        )

        self.assertLess(weaker.availability_score, ready.availability_score)
        self.assertLess(weaker.final_stock_pct, ready.final_stock_pct)

    def test_status_string_is_v93(self) -> None:
        self.assertEqual(STATUS_READY, "JARVIS_V93_0_DYNAMIC_STOCK_SLEEVE_SCORING_READY_SAFE")


if __name__ == "__main__":
    unittest.main()
