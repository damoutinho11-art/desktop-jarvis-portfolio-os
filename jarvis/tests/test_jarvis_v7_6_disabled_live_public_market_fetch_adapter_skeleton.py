import unittest
from dataclasses import replace

from jarvis.jarvis_v7_6_disabled_live_public_market_fetch_adapter_skeleton import (
    SKELETON_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)


class JarvisV76DisabledLivePublicMarketFetchAdapterSkeletonTests(unittest.TestCase):
    def test_disabled_adapter_skeleton_is_ready_and_points_to_enablement_preflight(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.skeleton_status, SKELETON_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_7_live_public_market_intelligence_enablement_preflight")
        self.assertTrue(result.disabled_adapter_skeleton_ready)
        self.assertTrue(result.compatible_with_v7_3_fetch_boundary)
        self.assertTrue(result.compatible_with_v7_4_dry_run_planner)
        self.assertTrue(result.compatible_with_v7_5_response_normalizer)
        self.assertGreaterEqual(result.skeleton_count, 4)
        self.assertGreaterEqual(result.selected_candidate_skeleton_count, 1)
        self.assertEqual(result.enabled_adapter_count, 0)
        self.assertEqual(result.live_fetch_enabled_count, 0)
        self.assertEqual(result.network_call_allowed_count, 0)
        self.assertEqual(result.network_call_attempt_count, 0)
        self.assertEqual(result.raw_response_storage_allowed_count, 0)
        self.assertEqual(result.raw_response_storage_count, 0)
        self.assertEqual(result.live_adapter_record_emit_count, 0)
        self.assertFalse(result.blockers)

    def test_skeletons_wire_boundary_dry_run_and_normalizer(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

        for skeleton in result.adapter_skeletons:
            self.assertTrue(skeleton.boundary_available)
            self.assertTrue(skeleton.dry_run_plan_available)
            self.assertTrue(skeleton.normalizer_contract_available)
            self.assertTrue(skeleton.linked_boundary_request_id)
            self.assertTrue(skeleton.linked_dry_run_plan_id)
            self.assertTrue(skeleton.linked_normalization_input_id)

    def test_skeletons_are_disabled_non_networked_and_non_executable(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

        for skeleton in result.adapter_skeletons:
            self.assertFalse(skeleton.adapter_enabled)
            self.assertFalse(skeleton.live_fetch_enabled)
            self.assertFalse(skeleton.network_call_allowed)
            self.assertFalse(skeleton.network_call_attempted)
            self.assertFalse(skeleton.raw_response_storage_allowed)
            self.assertFalse(skeleton.raw_response_stored)
            self.assertFalse(skeleton.emits_live_adapter_record)
            self.assertFalse(skeleton.creates_buy_request)
            self.assertFalse(skeleton.connects_broker)
            self.assertFalse(skeleton.places_order)
            self.assertFalse(skeleton.executes_trade)
            self.assertTrue(skeleton.safe_disabled_skeleton_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Adapter skeleton override must be" in blocker for blocker in blocked.blockers))

    def test_empty_skeletons_block(self) -> None:
        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No disabled live public market fetch adapter skeletons" in blocker for blocker in blocked.blockers))

    def test_duplicate_skeleton_id_blocks(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
            result.adapter_skeletons + (result.adapter_skeletons[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_enabling_adapter_or_live_fetch_blocks(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        bad = replace(
            result.adapter_skeletons[0],
            adapter_enabled=True,
            live_fetch_enabled=True,
        )

        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
            (bad,) + result.adapter_skeletons[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("adapter must remain disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))

    def test_network_or_raw_storage_blocks(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        bad = replace(
            result.adapter_skeletons[0],
            network_call_allowed=True,
            network_call_attempted=True,
            raw_response_storage_allowed=True,
            raw_response_stored=True,
        )

        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
            (bad,) + result.adapter_skeletons[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network call attempt is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage attempt is forbidden" in blocker for blocker in blocked.blockers))

    def test_live_adapter_record_emission_blocks(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        bad = replace(result.adapter_skeletons[0], emits_live_adapter_record=True)

        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
            (bad,) + result.adapter_skeletons[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_execution_fields_block(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        bad = replace(
            result.adapter_skeletons[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
            (bad,) + result.adapter_skeletons[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
        payload = result.to_dict()

        self.assertTrue(payload["skeleton_only"])
        self.assertTrue(payload["adapter_disabled_by_default"])
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
