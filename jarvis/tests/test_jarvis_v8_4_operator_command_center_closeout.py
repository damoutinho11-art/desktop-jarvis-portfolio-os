import unittest
from dataclasses import replace

from jarvis.jarvis_v8_4_operator_command_center_closeout import (
    CLOSEOUT_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v8_4_operator_command_center_closeout,
)


class JarvisV84OperatorCommandCenterCloseoutTests(unittest.TestCase):
    def test_v8_product_layer_closeout_is_ready(self) -> None:
        result = audit_v8_4_operator_command_center_closeout()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.closeout_status, CLOSEOUT_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v9_0_public_market_data_enablement_decision_layer")
        self.assertTrue(result.v8_product_layer_complete)
        self.assertTrue(result.v8_0_ready)
        self.assertTrue(result.v8_1_ready)
        self.assertTrue(result.v8_2_ready)
        self.assertTrue(result.v8_3_ready)
        self.assertEqual(result.capability_count, 5)
        self.assertEqual(result.ready_capability_count, 5)
        self.assertEqual(result.user_visible_capability_count, 5)
        self.assertEqual(result.unsafe_capability_count, 0)
        self.assertFalse(result.blockers)

    def test_required_capabilities_exist(self) -> None:
        result = audit_v8_4_operator_command_center_closeout()
        ids = {capability.capability_id for capability in result.capabilities}

        self.assertIn("public_market_intelligence_operator_dashboard", ids)
        self.assertIn("autonomous_research_cycle_status_panel", ids)
        self.assertIn("weekly_recommendation_evidence_pack_integration", ids)
        self.assertIn("portfolio_action_brief_generator", ids)
        self.assertIn("execution_boundary_preservation", ids)

    def test_capabilities_are_visible_safe_and_non_executable(self) -> None:
        result = audit_v8_4_operator_command_center_closeout()

        for capability in result.capabilities:
            self.assertTrue(capability.ready)
            self.assertTrue(capability.user_visible)
            self.assertFalse(capability.creates_buy_request)
            self.assertFalse(capability.connects_broker)
            self.assertFalse(capability.places_order)
            self.assertFalse(capability.executes_trade)
            self.assertFalse(capability.live_fetch_enabled)
            self.assertFalse(capability.network_call_enabled)
            self.assertFalse(capability.raw_response_storage_enabled)
            self.assertFalse(capability.live_adapter_record_emission_enabled)
            self.assertTrue(capability.safe_capability_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v8_4_operator_command_center_closeout(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Capability override must be" in blocker for blocker in blocked.blockers))

    def test_duplicate_or_missing_capability_blocks(self) -> None:
        result = audit_v8_4_operator_command_center_closeout()

        duplicate = audit_v8_4_operator_command_center_closeout(
            result.capabilities + (result.capabilities[0],)
        )
        self.assertEqual(duplicate.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in duplicate.blockers))

        missing = audit_v8_4_operator_command_center_closeout(result.capabilities[:-1])
        self.assertEqual(missing.status, STATUS_BLOCKED)
        self.assertTrue(any("must include all required" in blocker for blocker in missing.blockers))

    def test_unsafe_capability_blocks(self) -> None:
        result = audit_v8_4_operator_command_center_closeout()
        bad = replace(
            result.capabilities[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
            live_fetch_enabled=True,
            network_call_enabled=True,
        )

        blocked = audit_v8_4_operator_command_center_closeout((bad,) + result.capabilities[1:])

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))

    def test_closeout_safety_flags_hold(self) -> None:
        payload = audit_v8_4_operator_command_center_closeout().to_dict()

        self.assertTrue(payload["product_value_not_redundant"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])


if __name__ == "__main__":
    unittest.main()

