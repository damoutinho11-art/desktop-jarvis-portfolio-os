import unittest
from dataclasses import replace

from jarvis.jarvis_v9_0_public_market_data_enablement_decision_layer import (
    DECISION_LAYER_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v9_0_public_market_data_enablement_decision_layer,
)


class JarvisV90PublicMarketDataEnablementDecisionLayerTests(unittest.TestCase):
    def test_decision_layer_is_ready_without_live_mode(self) -> None:
        result = audit_v9_0_public_market_data_enablement_decision_layer()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.decision_layer_status, DECISION_LAYER_READY)
        self.assertEqual(result.recommended_next_stage, "v9_1_controlled_public_data_dry_run_enablement_plan")
        self.assertTrue(result.enablement_decision_layer_ready)
        self.assertTrue(result.source_selection_not_repeated)
        self.assertTrue(result.dry_run_planning_allowed)
        self.assertTrue(result.live_mode_blocked)
        self.assertTrue(result.explicit_operator_authorization_required)
        self.assertEqual(result.live_allowed_decision_count, 0)
        self.assertGreaterEqual(result.decision_count, 6)
        self.assertFalse(result.blockers)

    def test_required_decisions_exist(self) -> None:
        result = audit_v9_0_public_market_data_enablement_decision_layer()
        ids = {decision.decision_id for decision in result.decisions}

        self.assertIn("existing_readiness_chain_accepted", ids)
        self.assertIn("source_selection_not_repeated", ids)
        self.assertIn("dry_run_public_data_path_allowed", ids)
        self.assertIn("live_public_fetch_blocked", ids)
        self.assertIn("live_adapter_emission_blocked", ids)
        self.assertIn("execution_boundary_preserved", ids)

    def test_decisions_are_visible_non_live_and_non_executable(self) -> None:
        result = audit_v9_0_public_market_data_enablement_decision_layer()

        for decision in result.decisions:
            self.assertTrue(decision.user_visible)
            self.assertFalse(decision.live_mode_allowed)
            self.assertFalse(decision.creates_buy_request)
            self.assertFalse(decision.connects_broker)
            self.assertFalse(decision.places_order)
            self.assertFalse(decision.executes_trade)
            self.assertFalse(decision.network_call_enabled)
            self.assertFalse(decision.raw_response_storage_enabled)
            self.assertFalse(decision.live_adapter_record_emission_enabled)
            self.assertTrue(decision.safe_decision_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v9_0_public_market_data_enablement_decision_layer(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Decision override must be" in blocker for blocker in blocked.blockers))

    def test_duplicate_or_missing_decision_blocks(self) -> None:
        result = audit_v9_0_public_market_data_enablement_decision_layer()

        duplicate = audit_v9_0_public_market_data_enablement_decision_layer(
            result.decisions + (result.decisions[0],)
        )
        self.assertEqual(duplicate.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in duplicate.blockers))

        missing = audit_v9_0_public_market_data_enablement_decision_layer(result.decisions[:-1])
        self.assertEqual(missing.status, STATUS_BLOCKED)
        self.assertTrue(any("must include all required" in blocker for blocker in missing.blockers))

    def test_live_or_executable_decision_blocks(self) -> None:
        result = audit_v9_0_public_market_data_enablement_decision_layer()
        bad = replace(
            result.decisions[0],
            live_mode_allowed=True,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
            network_call_enabled=True,
            raw_response_storage_enabled=True,
            live_adapter_record_emission_enabled=True,
        )

        blocked = audit_v9_0_public_market_data_enablement_decision_layer(
            (bad,) + result.decisions[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live mode must not be allowed" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_hold(self) -> None:
        payload = audit_v9_0_public_market_data_enablement_decision_layer().to_dict()

        self.assertTrue(payload["source_selection_not_repeated"])
        self.assertTrue(payload["dry_run_planning_allowed"])
        self.assertTrue(payload["live_mode_blocked"])
        self.assertTrue(payload["explicit_operator_authorization_required"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])


if __name__ == "__main__":
    unittest.main()
