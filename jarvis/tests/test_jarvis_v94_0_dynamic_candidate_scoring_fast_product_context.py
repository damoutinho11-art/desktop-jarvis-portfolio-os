from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime.multi_candidate_instrument_selector import (
    build_fast_product_instrument_summary,
    score_lane_candidates,
)
from jarvis.runtime import product_mode_operator


class JarvisV940DynamicCandidateScoringFastProductContextTests(unittest.TestCase):
    def test_current_product_summary_uses_dynamic_counts(self) -> None:
        summary = build_fast_product_instrument_summary(
            crypto_lane_eur=100.0,
            etf_fund_lane_eur=275.0,
            individual_stock_lane_eur=50.0,
            current_date="2026-06-18",
        )

        crypto = [item for item in summary.selections if item.lane == "crypto"]
        etf = [item for item in summary.selections if item.lane == "etf_fund"]
        stock = [item for item in summary.selections if item.lane == "individual_stock"]

        self.assertEqual(len(crypto), 2)
        self.assertEqual(len(etf), 3)
        self.assertEqual(len(stock), 1)

        self.assertEqual([item.symbol for item in crypto], ["BTC", "ETH"])
        self.assertIn("IS3Q.DE", [item.symbol for item in etf])
        self.assertEqual(stock[0].symbol, "MSFT")

        self.assertAlmostEqual(summary.lane_totals["crypto"], 100.0)
        self.assertAlmostEqual(summary.lane_totals["etf_fund"], 275.0)
        self.assertAlmostEqual(summary.lane_totals["individual_stock"], 50.0)

    def test_small_etf_lane_stays_concentrated_when_split_is_not_practical(self) -> None:
        summary = build_fast_product_instrument_summary(
            crypto_lane_eur=100.0,
            etf_fund_lane_eur=100.0,
            individual_stock_lane_eur=50.0,
            current_date="2026-06-18",
        )

        etf = [item for item in summary.selections if item.lane == "etf_fund"]

        self.assertEqual(len(etf), 1)
        self.assertAlmostEqual(summary.lane_totals["etf_fund"], 100.0)

    def test_larger_stock_lane_can_select_more_than_one_stock(self) -> None:
        summary = build_fast_product_instrument_summary(
            crypto_lane_eur=100.0,
            etf_fund_lane_eur=275.0,
            individual_stock_lane_eur=200.0,
            current_date="2026-06-18",
        )

        stock = [item for item in summary.selections if item.lane == "individual_stock"]

        self.assertGreater(len(stock), 1)
        self.assertAlmostEqual(summary.lane_totals["individual_stock"], 200.0)

    def test_candidate_scores_are_sorted_by_quality_not_input_position_only(self) -> None:
        scored = score_lane_candidates(
            "crypto",
            ["HYPE", "BTC", "ETH"],
            100.0,
        )

        self.assertEqual(scored[0].symbol, "BTC")
        self.assertEqual(scored[1].symbol, "ETH")
        self.assertEqual(scored[2].symbol, "HYPE")
        self.assertGreater(scored[0].score, scored[-1].score)

    def test_fast_summary_does_not_create_execution_path(self) -> None:
        summary = build_fast_product_instrument_summary(
            crypto_lane_eur=100.0,
            etf_fund_lane_eur=275.0,
            individual_stock_lane_eur=50.0,
            current_date="2026-06-18",
        )

        self.assertIn(
            "manual approval remains required; no order or trade is created",
            summary.warnings,
        )

    def test_product_mode_uses_fast_summary_not_full_selector_rebuild(self) -> None:
        source = Path("jarvis/runtime/product_mode_operator.py").read_text(encoding="utf-8")

        self.assertIn("build_fast_product_instrument_summary", source)
        self.assertNotIn("build_multi_candidate_instrument_selector_result(current_date=current_date)", source)

    def test_product_status_is_v94(self) -> None:
        self.assertEqual(
            product_mode_operator.STATUS_READY,
            "JARVIS_V94_0_DYNAMIC_CANDIDATE_SCORING_FAST_PRODUCT_CONTEXT_READY_SAFE",
        )


if __name__ == "__main__":
    unittest.main()
