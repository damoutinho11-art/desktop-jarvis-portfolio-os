"""Regression tests for J.A.R.V.I.S. Portfolio OS v0.2 ETF scoring."""

from __future__ import annotations

from copy import deepcopy
import subprocess
import sys
import unittest

import allocation_engine
import etf_scoring


class JarvisV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.constitution = allocation_engine.load_json("jarvis_constitution.json")
        self.state = allocation_engine.load_json("portfolio_state.json")
        self.universe = etf_scoring.load_etf_universe("etf_universe.json")
        self.result = allocation_engine.allocate_weekly_budget(
            self.constitution, self.state
        )

    def test_etf_scoring_formula_works(self) -> None:
        score = etf_scoring.score_etf_sleeve(
            "quality_etf", self.universe["quality_etf"], current_weight=0.0
        )
        expected = (0.45 * 100) + (0.25 * 60) + (0.15 * 75) + (0.10 * 75) + (0.05 * 85)
        self.assertAlmostEqual(score["final_score"], expected, places=4)

    def test_above_max_sleeve_gets_score_zero(self) -> None:
        score = etf_scoring.score_etf_sleeve(
            "global_core_etf", self.universe["global_core_etf"], current_weight=0.70
        )
        self.assertEqual(score["final_score"], 0.0)
        self.assertTrue(score["warnings"])

    def test_disabled_etf_sleeve_gets_score_zero(self) -> None:
        config = deepcopy(self.universe["quality_etf"])
        config["enabled"] = False
        score = etf_scoring.score_etf_sleeve("quality_etf", config, current_weight=0.0)
        self.assertEqual(score["final_score"], 0.0)
        self.assertFalse(score["enabled"])

    def test_etf_scoring_does_not_affect_crypto_safety_rules(self) -> None:
        ticket = self.result["approval_ticket"]
        self.assertEqual(ticket["executable_allocation"]["btc"], 41.54)
        self.assertEqual(ticket["executable_allocation"]["tactical_reserve"], 62.31)
        self.assertLessEqual(
            self.result["crypto_risk_status"]["btc_weight"],
            self.result["crypto_risk_status"]["btc_max"],
        )
        self.assertEqual(
            self.result["crypto_risk_status"]["btc_fallback_weekly_cap_cents"],
            allocation_engine.cents(41.54),
        )

    def test_ideal_etf_allocation_uses_highest_eligible_score(self) -> None:
        scores = self.result["etf_scores"]
        ranked = etf_scoring.rank_eligible_etfs(scores)
        top_sleeve = ranked[0]["sleeve"]

        self.assertEqual(top_sleeve, "quality_etf")
        self.assertEqual(self.result["approval_ticket"]["ideal_allocation"][top_sleeve], 103.85)
        self.assertEqual(self.result["approval_ticket"]["blocked_actions"][0]["asset"], top_sleeve)

    def test_etf_scoring_verdict_is_in_ticket(self) -> None:
        verdict = self.result["approval_ticket"]["etf_scoring_verdict"]
        self.assertEqual(verdict["selected_ideal_etf"], "quality_etf")
        self.assertEqual(verdict["selected_label"], "Selected ideal ETF sleeve: quality_etf")
        self.assertEqual(len(verdict["sleeves"]), 3)

    def test_etf_score_ranks_and_reasoning_are_present(self) -> None:
        verdict = self.result["approval_ticket"]["etf_scoring_verdict"]
        by_sleeve = {item["sleeve"]: item for item in verdict["sleeves"]}

        self.assertEqual(by_sleeve["quality_etf"]["rank"], 1)
        self.assertEqual(by_sleeve["growth_nasdaq_etf"]["rank"], 2)
        self.assertEqual(by_sleeve["global_core_etf"]["rank"], 3)
        self.assertTrue(by_sleeve["quality_etf"]["main_positive_drivers"])
        self.assertTrue(by_sleeve["quality_etf"]["main_penalties"])
        self.assertIn("strongest eligible ETF score", by_sleeve["quality_etf"]["reason"])
        self.assertIn("lower score", by_sleeve["growth_nasdaq_etf"]["reason"])

    def test_safety_lines_remain_present(self) -> None:
        safety = self.result["approval_ticket"]["safety_checks"]
        self.assertIn("Manual approval required. No trades executed.", safety)
        self.assertIn("No broker connection.", safety)
        self.assertIn("No API keys.", safety)
        self.assertIn("No orders created.", safety)
        self.assertIn("No automatic selling.", safety)

    def test_v01_regression_tests_still_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "test_jarvis_v01.py"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=completed.stdout + completed.stderr,
        )


if __name__ == "__main__":
    unittest.main()
