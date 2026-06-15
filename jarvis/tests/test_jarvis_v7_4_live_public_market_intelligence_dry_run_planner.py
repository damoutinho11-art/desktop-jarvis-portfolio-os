import unittest
from dataclasses import replace

from jarvis.jarvis_v7_4_live_public_market_intelligence_dry_run_planner import (
    DRY_RUN_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_4_live_public_market_intelligence_dry_run_planner,
)


class JarvisV74LivePublicMarketIntelligenceDryRunPlannerTests(unittest.TestCase):
    def test_dry_run_planner_is_ready_and_points_to_response_normalizer_contract(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.dry_run_status, DRY_RUN_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_5_live_public_market_intelligence_response_normalizer_contract")
        self.assertTrue(result.dry_run_planner_ready)
        self.assertTrue(result.compatible_with_v7_3_fetch_boundary)
        self.assertGreaterEqual(result.dry_run_plan_count, 4)
        self.assertGreaterEqual(result.selected_candidate_plan_count, 1)
        self.assertEqual(result.planned_network_call_count, 0)
        self.assertEqual(result.planned_live_fetch_count, 0)
        self.assertEqual(result.raw_response_storage_plan_count, 0)
        self.assertFalse(result.blockers)

    def test_dry_run_plans_are_non_executable_and_non_networked(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()

        for plan in result.dry_run_fetch_plans:
            self.assertTrue(plan.dry_run_only)
            self.assertFalse(plan.live_fetch_allowed)
            self.assertFalse(plan.network_call_allowed)
            self.assertFalse(plan.raw_response_storage_allowed)
            self.assertFalse(plan.creates_buy_request)
            self.assertFalse(plan.connects_broker)
            self.assertFalse(plan.places_order)
            self.assertFalse(plan.executes_trade)
            self.assertTrue(plan.safe_dry_run_plan_only())

    def test_planned_urls_are_https_placeholders_with_candidate_resolved(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()

        for plan in result.dry_run_fetch_plans:
            self.assertTrue(plan.planned_url.startswith("https://"))
            self.assertIn("example.invalid", plan.planned_url)
            self.assertNotIn("{candidate_id}", plan.planned_url)
            self.assertIn(plan.candidate_id, plan.planned_url)

    def test_selected_candidate_has_dry_run_plan(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()

        self.assertGreaterEqual(result.selected_candidate_plan_count, 1)
        self.assertTrue(
            any(plan.candidate_id == result.selected_candidate_id for plan in result.dry_run_fetch_plans)
        )

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_4_live_public_market_intelligence_dry_run_planner(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Dry-run plan override must be" in blocker for blocker in blocked.blockers))

    def test_empty_plans_block(self) -> None:
        blocked = audit_v7_4_live_public_market_intelligence_dry_run_planner(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No live public market dry-run fetch plans" in blocker for blocker in blocked.blockers))

    def test_duplicate_plan_id_blocks(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
        blocked = audit_v7_4_live_public_market_intelligence_dry_run_planner(
            result.dry_run_fetch_plans + (result.dry_run_fetch_plans[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_live_fetch_or_network_plan_blocks(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
        bad = replace(
            result.dry_run_fetch_plans[0],
            live_fetch_allowed=True,
            network_call_allowed=True,
            raw_response_storage_allowed=True,
        )

        blocked = audit_v7_4_live_public_market_intelligence_dry_run_planner(
            (bad,) + result.dry_run_fetch_plans[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_dry_run_plan_blocks(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
        bad = replace(
            result.dry_run_fetch_plans[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_4_live_public_market_intelligence_dry_run_planner(
            (bad,) + result.dry_run_fetch_plans[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
        payload = result.to_dict()

        self.assertTrue(payload["dry_run_only"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
