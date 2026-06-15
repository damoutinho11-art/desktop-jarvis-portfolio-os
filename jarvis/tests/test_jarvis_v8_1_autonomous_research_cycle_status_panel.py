import unittest
from dataclasses import replace

from jarvis.jarvis_v8_1_autonomous_research_cycle_status_panel import (
    ITEM_STATE_BLOCKED,
    ITEM_STATE_WATCH,
    PANEL_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v8_1_autonomous_research_cycle_status_panel,
)


class JarvisV81AutonomousResearchCycleStatusPanelTests(unittest.TestCase):
    def test_research_cycle_panel_is_ready_and_points_to_evidence_pack(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.panel_status, PANEL_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v8_2_weekly_recommendation_evidence_pack_integration")
        self.assertTrue(result.research_cycle_panel_ready)
        self.assertTrue(result.compatible_with_v8_0_operator_dashboard)
        self.assertGreaterEqual(result.item_count, 6)
        self.assertEqual(result.reviewed_item_count, result.item_count)
        self.assertGreaterEqual(result.ready_item_count, 4)
        self.assertGreaterEqual(result.watch_item_count, 1)
        self.assertEqual(result.blocked_item_count, 0)
        self.assertGreaterEqual(result.recommendation_pack_ready_item_count, 4)
        self.assertEqual(result.user_visible_item_count, result.item_count)
        self.assertEqual(result.live_fetch_enabled_item_count, 0)
        self.assertEqual(result.network_call_enabled_item_count, 0)
        self.assertEqual(result.raw_response_storage_enabled_item_count, 0)
        self.assertEqual(result.live_adapter_record_emission_enabled_item_count, 0)
        self.assertFalse(result.blockers)

    def test_required_status_items_exist(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        item_ids = {item.item_id for item in result.items}

        self.assertIn("public_intelligence_readiness_review", item_ids)
        self.assertIn("selected_candidate_coverage_review", item_ids)
        self.assertIn("provider_and_binding_review", item_ids)
        self.assertIn("live_data_freshness_review", item_ids)
        self.assertIn("weekly_recommendation_pack_readiness", item_ids)
        self.assertIn("execution_boundary_review", item_ids)

    def test_status_items_are_visible_reviewed_and_non_executable(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()

        for item in result.items:
            self.assertTrue(item.user_visible)
            self.assertTrue(item.reviewed_by_jarvis)
            self.assertFalse(item.live_fetch_enabled)
            self.assertFalse(item.network_call_enabled)
            self.assertFalse(item.raw_response_storage_enabled)
            self.assertFalse(item.live_adapter_record_emission_enabled)
            self.assertFalse(item.creates_buy_request)
            self.assertFalse(item.connects_broker)
            self.assertFalse(item.places_order)
            self.assertFalse(item.executes_trade)
            self.assertTrue(item.safe_panel_item_only())

    def test_panel_exposes_product_visibility_fields(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()

        self.assertTrue(result.product_visibility_stage)
        self.assertTrue(result.public_intelligence_review_visible)
        self.assertTrue(result.candidate_coverage_visible)
        self.assertTrue(result.freshness_status_visible)
        self.assertTrue(result.recommendation_pack_readiness_visible)
        self.assertTrue(result.next_watch_focus_visible)

    def test_live_data_freshness_is_watch_only_not_failure(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        live_data_items = [
            item for item in result.items if item.item_id == "live_data_freshness_review"
        ]

        self.assertEqual(len(live_data_items), 1)
        self.assertEqual(live_data_items[0].state, ITEM_STATE_WATCH)
        self.assertFalse(live_data_items[0].ready_for_recommendation_pack)
        self.assertIn("disabled", live_data_items[0].blocked_reason.lower())
        self.assertTrue(live_data_items[0].watch_focus)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v8_1_autonomous_research_cycle_status_panel(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Status item override must be" in blocker for blocker in blocked.blockers))

    def test_empty_items_block(self) -> None:
        blocked = audit_v8_1_autonomous_research_cycle_status_panel(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No autonomous research cycle status items" in blocker for blocker in blocked.blockers))

    def test_duplicate_item_id_blocks(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        blocked = audit_v8_1_autonomous_research_cycle_status_panel(
            result.items + (result.items[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_missing_required_item_blocks(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        items = tuple(item for item in result.items if item.item_id != "execution_boundary_review")

        blocked = audit_v8_1_autonomous_research_cycle_status_panel(items)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must include all required" in blocker for blocker in blocked.blockers))

    def test_blocked_item_requires_reason(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        bad = replace(result.items[0], state=ITEM_STATE_BLOCKED, blocked_reason="")

        blocked = audit_v8_1_autonomous_research_cycle_status_panel(
            (bad,) + result.items[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("blocked items require" in blocker for blocker in blocked.blockers))

    def test_watch_item_requires_watch_focus(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        bad = replace(result.items[0], state=ITEM_STATE_WATCH, watch_focus="")

        blocked = audit_v8_1_autonomous_research_cycle_status_panel(
            (bad,) + result.items[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("watch items require" in blocker for blocker in blocked.blockers))

    def test_hidden_or_unsafe_item_blocks(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        bad = replace(
            result.items[0],
            user_visible=False,
            reviewed_by_jarvis=False,
            live_fetch_enabled=True,
            network_call_enabled=True,
            raw_response_storage_enabled=True,
            live_adapter_record_emission_enabled=True,
        )

        blocked = audit_v8_1_autonomous_research_cycle_status_panel(
            (bad,) + result.items[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must be user-visible" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("must be reviewed" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_execution_fields_block(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        bad = replace(
            result.items[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v8_1_autonomous_research_cycle_status_panel(
            (bad,) + result.items[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v8_1_autonomous_research_cycle_status_panel()
        payload = result.to_dict()

        self.assertTrue(payload["product_visibility_stage"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
