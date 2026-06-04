"""Regression tests for J.A.R.V.I.S. Portfolio OS v0.1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import allocation_engine
import review_ticket


class JarvisV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.constitution = allocation_engine.load_json("jarvis_constitution.json")
        self.state = allocation_engine.load_json("portfolio_state.json")
        self.result = allocation_engine.allocate_weekly_budget(
            self.constitution, self.state
        )
        self.ticket = self.result["approval_ticket"]

    def test_emergency_fund_is_excluded_from_investable_value(self) -> None:
        holdings = allocation_engine.investable_holdings(self.constitution, self.state)
        investable = sum(holdings.values())
        emergency = allocation_engine.cents(self.state["emergency_fund"]["amount"])

        self.assertEqual(self.result["investable_before_cents"], investable)
        self.assertNotEqual(self.result["investable_before_cents"], investable + emergency)
        self.assertEqual(emergency, allocation_engine.cents(3000.0))

    def test_manual_approval_is_required(self) -> None:
        self.assertEqual(
            self.ticket["approval_notice"],
            "Manual approval required. No trades executed.",
        )
        self.assertEqual(self.ticket["approval_status"], "pending_manual_approval")

    def test_trades_executed_is_false(self) -> None:
        self.assertFalse(self.ticket["trades_executed"])

    def test_ticket_contains_no_broker_api_order_safety_lines(self) -> None:
        safety = self.ticket["safety_checks"]
        self.assertIn("No broker connection.", safety)
        self.assertIn("No API keys.", safety)
        self.assertIn("No orders created.", safety)
        self.assertIn("No automatic selling.", safety)

    def test_lightyear_ready_allows_etf_executable_buy(self) -> None:
        self.assertTrue(self.state["platform_status"]["lightyear_ready"])
        executable = self.result["executable_allocations_cents"]
        self.assertEqual(executable["global_core_etf"], 0)
        self.assertEqual(executable["growth_nasdaq_etf"], 0)
        self.assertEqual(executable["quality_etf"], allocation_engine.cents(103.85))
        self.assertEqual(self.ticket["blocked_actions"], [])

    def test_no_btc_fallback_when_etf_route_is_ready(self) -> None:
        self.assertNotIn("btc", self.ticket["executable_allocation"])
        self.assertEqual(self.ticket["fallback_actions"], [])

    def test_tactical_reserve_not_used_when_etf_route_is_ready(self) -> None:
        self.assertNotIn("tactical_reserve", self.ticket["executable_allocation"])
        self.assertEqual(self.ticket["reserve_actions"], [])

    def test_legacy_holdings_numeric_included_and_null_ignored(self) -> None:
        state = deepcopy(self.state)
        state["legacy_holdings"] = {
            "lhv_growth_sxr8": 50.0,
            "lhv_growth_iemm": 100.0,
            "lhv_growth_xcha": None,
            "lhv_growth_cash_pending_settlement": 25.0,
        }
        holdings = allocation_engine.investable_holdings(self.constitution, state)

        self.assertEqual(holdings["global_core_etf"], allocation_engine.cents(150.0))
        self.assertEqual(holdings["discovery"], 0)
        self.assertEqual(holdings["tactical_reserve"], allocation_engine.cents(29.9))

    def test_review_ticket_test_mode_uses_test_log_only(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reviewed_path = root / "approval_ticket_reviewed_latest.json"
            real_log = root / "approval_decisions.jsonl"
            test_log = root / "approval_decisions_test.jsonl"

            review_ticket.record_decision(
                self.ticket,
                "skipped",
                "regression test",
                test_decision=True,
                reviewed_path=reviewed_path,
                decisions_path=real_log,
                test_decisions_path=test_log,
            )

            self.assertTrue(test_log.exists())
            self.assertFalse(real_log.exists())
            reviewed = allocation_engine.load_json(reviewed_path)
            self.assertTrue(reviewed["test_decision"])
            self.assertFalse(reviewed["trades_executed"])

    def test_sxr8_maps_to_global_core_etf(self) -> None:
        policy = self.constitution["legacy_holding_policy"]["lhv_growth_sxr8"]
        self.assertEqual(policy["maps_to"], "global_core_etf")
        self.assertFalse(policy["new_buys_allowed"])
        self.assertFalse(policy["sell_allowed_without_explicit_user_approval"])


if __name__ == "__main__":
    unittest.main()
