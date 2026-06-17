from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import (
    MODE_DAILY_CHECK_IN,
    MODE_WEEKLY_BUY_PREP,
    STATUS_BLOCKED,
    STATUS_READY,
    build_free_research_api_router_weekly_policy_result,
    build_research_provider_statuses,
    format_free_research_api_router_weekly_policy,
)


def _action_ready() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_READY_SAFE",
        crypto_candidate="hype",
        crypto_amount_eur=41.54,
        etf_symbol="IS3Q.DE",
        etf_amount_eur=62.31,
        stock_symbol="MSFT",
        stock_manual_amount_required=True,
        stock_approved_for_purchase=False,
        approval_ticket_mutation=True,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": "ready"},
    )


class JarvisV430FreeResearchApiRouterWeeklyPolicyTests(unittest.TestCase):
    def test_daily_mode_ready_but_not_buy_prep(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_three_lane_result=_action_ready(),
            env={},
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.daily_check_in_only)
        self.assertFalse(result.weekly_buy_preparation_allowed)
        self.assertFalse(result.manual_buy_action_today)
        self.assertTrue(result.free_stack_sufficient_for_weekly_investing)
        self.assertEqual(result.source_confidence_grade, "MEDIUM_HIGH_FREE_STACK")
        self.assertLess(result.source_confidence_score, 100)
        self.assertFalse(result.paid_api_required_now)
        self.assertFalse(result.broker_api_required_now)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)

    def test_daily_mode_filters_expected_stock_bridge_not_run_warning(self) -> None:
        upstream = _action_ready()
        upstream.status = "JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_REVIEW_REQUIRED_SAFE"
        upstream.approval_ticket_mutation = False
        upstream.warnings = ("stock bridge was not run.",)

        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_three_lane_result=upstream,
            env={},
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.warnings, ())
        self.assertFalse(result.approval_ticket_mutation)
        self.assertTrue(result.daily_check_in_only)
    def test_weekly_mode_allows_manual_buy_preparation_only(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_three_lane_result=_action_ready(),
            env={},
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.daily_check_in_only)
        self.assertTrue(result.weekly_buy_preparation_allowed)
        self.assertTrue(result.manual_buy_action_today)
        self.assertTrue(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_optional_api_key_detection(self) -> None:
        providers = build_research_provider_statuses(
            {
                "JARVIS_FMP_API_KEY": "fmp-key",
                "JARVIS_COINGECKO_API_KEY": "coin-key",
            }
        )
        provider_map = {provider.provider_id: provider for provider in providers}

        self.assertTrue(provider_map["fmp_free_optional"].api_key_present)
        self.assertEqual(provider_map["fmp_free_optional"].status, "OPTIONAL_KEY_PRESENT_READY")
        self.assertTrue(provider_map["coingecko_free_or_demo"].api_key_present)
        self.assertEqual(provider_map["sec_edgar_official"].status, "NO_KEY_OFFICIAL_READY")
        self.assertEqual(provider_map["ecb_fx_official"].status, "NO_KEY_OFFICIAL_READY")

    def test_optional_keys_raise_confidence_to_high_free_stack(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_three_lane_result=_action_ready(),
            env={
                "JARVIS_FMP_API_KEY": "fmp-key",
                "JARVIS_COINGECKO_API_KEY": "coin-key",
            },
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.source_confidence_grade, "HIGH_FREE_STACK")
        self.assertGreaterEqual(result.source_confidence_score, 85)
        self.assertTrue(result.weekly_buy_preparation_allowed)
    def test_missing_optional_fmp_key_does_not_block_free_stack(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_three_lane_result=_action_ready(),
            env={},
        )

        fmp = next(provider for provider in result.provider_statuses if provider.provider_id == "fmp_free_optional")
        self.assertFalse(fmp.api_key_present)
        self.assertEqual(fmp.status, "OPTIONAL_KEY_MISSING_FALLBACK_ACTIVE")
        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.weekly_buy_preparation_allowed)

    def test_blocked_three_lane_blocks_router(self) -> None:
        upstream = _action_ready()
        upstream.status = "JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_BLOCKED_SAFE"
        upstream.blockers = ("unsafe approval state",)

        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_three_lane_result=upstream,
            env={},
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.weekly_buy_preparation_allowed)
        self.assertIn("unsafe approval state", result.blockers)
        self.assertIn("three-lane daily action brief was blocked.", result.blockers)

    def test_invalid_mode_blocks(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode="daily_buy_every_day",
            upstream_three_lane_result=_action_ready(),
            env={},
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertIn("operating_mode must be daily_check_in or weekly_buy_prep.", result.blockers)

    def test_console_mentions_policy_sources_and_safety(self) -> None:
        result = build_free_research_api_router_weekly_policy_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_three_lane_result=_action_ready(),
            env={},
        )
        output = format_free_research_api_router_weekly_policy(result)

        self.assertIn("weekly mode is for manual buy preparation", output)
        self.assertIn("free APIs/no-key official sources are used first", output)
        self.assertIn("fmp_free_optional", output)
        self.assertIn("sec_edgar_official", output)
        self.assertIn("ecb_fx_official", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()