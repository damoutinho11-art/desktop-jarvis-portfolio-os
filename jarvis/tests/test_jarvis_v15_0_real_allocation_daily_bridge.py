import unittest

from jarvis.jarvis_v15_0_real_allocation_daily_bridge import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_real_allocation_daily_bridge,
    build_real_allocation_daily_console_output,
    build_safety_check_console_output,
)


def _ticket(selected_sleeve: str, *, trades_executed: bool = False, safety_checks=None):
    ranked = [
        ("quality_etf", 83.0),
        ("growth_nasdaq_etf", 79.0),
        ("global_core_etf", 50.34),
    ]
    if selected_sleeve == "growth_nasdaq_etf":
        ranked = [
            ("growth_nasdaq_etf", 91.0),
            ("quality_etf", 83.0),
            ("global_core_etf", 50.34),
        ]
    if selected_sleeve == "global_core_etf":
        ranked = [
            ("global_core_etf", 92.0),
            ("quality_etf", 83.0),
            ("growth_nasdaq_etf", 79.0),
        ]

    return {
        "approval_notice": "Manual approval required. No trades executed.",
        "approval_status": "pending_manual_approval",
        "as_of": "2026-06-04",
        "portfolio_mode": "transition_mode",
        "weekly_budget": 103.85,
        "ideal_allocation": {selected_sleeve: 103.85},
        "executable_allocation": {selected_sleeve: 103.85},
        "etf_scoring_verdict": {
            "selected_ideal_etf": selected_sleeve,
            "selected_label": f"Selected ideal ETF sleeve: {selected_sleeve}",
            "sleeves": [
                {
                    "sleeve": sleeve,
                    "final_score": score,
                    "rank": index,
                    "main_positive_drivers": ["allocation gap"],
                    "main_penalties": ["no major scoring penalty"],
                    "selected": sleeve == selected_sleeve,
                    "reason": (
                        f"Selected ideal ETF sleeve: {sleeve}."
                        if sleeve == selected_sleeve
                        else f"Not selected: lower score than {selected_sleeve}."
                    ),
                }
                for index, (sleeve, score) in enumerate(ranked, start=1)
            ],
        },
        "safety_checks": safety_checks
        if safety_checks is not None
        else [
            "Manual approval required. No trades executed.",
            "No broker connection.",
            "No API keys.",
            "No orders created.",
            "No automatic selling.",
        ],
        "trades_executed": trades_executed,
        "warnings": [],
    }


class JarvisV150RealAllocationDailyBridgeTests(unittest.TestCase):
    def test_daily_selected_sleeve_is_read_from_weekly_result_ticket(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={"approval_ticket": _ticket("quality_etf")}
        )
        output = build_real_allocation_daily_console_output(result)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_ideal_sleeve, "quality_etf")
        self.assertEqual(result.executable_allocation, {"quality_etf": 103.85})
        self.assertIn("best current executable allocation: quality_etf â‚¬103.85", output)

    def test_growth_nasdaq_fixture_selects_growth_nasdaq_dynamically(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={"approval_ticket": _ticket("growth_nasdaq_etf")}
        )
        output = build_real_allocation_daily_console_output(result)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_ideal_sleeve, "growth_nasdaq_etf")
        self.assertEqual(result.executable_allocation, {"growth_nasdaq_etf": 103.85})
        self.assertIn("best current executable allocation: growth_nasdaq_etf â‚¬103.85", output)
        self.assertNotIn("selected ideal sleeve: quality_etf", output)

    def test_global_core_fixture_selects_global_core_dynamically(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={"approval_ticket": _ticket("global_core_etf")}
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_ideal_sleeve, "global_core_etf")
        self.assertEqual(result.executable_allocation, {"global_core_etf": 103.85})

    def test_trades_executed_true_blocks_bridge(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={"approval_ticket": _ticket("quality_etf", trades_executed=True)}
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.no_trades_executed)
        self.assertTrue(any("no trades" in blocker.lower() for blocker in result.blockers))

    def test_safety_checks_require_broker_order_and_trade_blocks(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={
                "approval_ticket": _ticket(
                    "quality_etf",
                    safety_checks=[
                        "Manual approval required. No trades executed.",
                        "No API keys.",
                    ],
                )
            }
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.broker_connection_forbidden)
        self.assertFalse(result.order_creation_forbidden)
        self.assertTrue(any("broker" in blocker.lower() for blocker in result.blockers))
        self.assertTrue(any("order" in blocker.lower() for blocker in result.blockers))

    def test_safety_check_blocks_buy_command_without_execution(self) -> None:
        output = build_safety_check_console_output()

        self.assertIn("Jarvis, buy BTC now.", output)
        self.assertIn("BLOCKED:", output)
        self.assertIn("No execution action was taken", output)

    def test_current_real_daily_output_does_not_show_old_demo_candidate(self) -> None:
        result = build_real_allocation_daily_bridge()
        output = build_real_allocation_daily_console_output(result)

        self.assertEqual(result.status, STATUS_READY)
        self.assertNotIn("btc_candidate", output)
        self.assertNotIn("crypto_core_btc", output)


if __name__ == "__main__":
    unittest.main()

