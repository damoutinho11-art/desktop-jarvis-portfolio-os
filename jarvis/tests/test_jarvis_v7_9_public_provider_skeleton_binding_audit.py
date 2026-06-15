import unittest
from dataclasses import replace

from jarvis.jarvis_v7_9_public_provider_skeleton_binding_audit import (
    BINDING_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_9_public_provider_skeleton_binding_audit,
)


class JarvisV79PublicProviderSkeletonBindingAuditTests(unittest.TestCase):
    def test_binding_audit_is_ready_and_points_to_readiness_closeout(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.binding_status, BINDING_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_10_live_public_market_intelligence_readiness_closeout_audit")
        self.assertTrue(result.binding_audit_ready)
        self.assertTrue(result.compatible_with_v7_6_disabled_adapter_skeleton)
        self.assertTrue(result.compatible_with_v7_8_provider_registry)
        self.assertGreaterEqual(result.binding_count, 4)
        self.assertEqual(result.binding_count, result.skeleton_count)
        self.assertEqual(result.unbound_skeleton_count, 0)
        self.assertGreaterEqual(result.selected_candidate_binding_count, 1)
        self.assertEqual(result.live_fetch_enabled_count, 0)
        self.assertEqual(result.network_call_allowed_count, 0)
        self.assertEqual(result.raw_response_storage_allowed_count, 0)
        self.assertEqual(result.live_adapter_record_emission_allowed_count, 0)
        self.assertFalse(result.blockers)

    def test_every_binding_is_ready_and_matches_endpoint_category(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()

        for binding in result.bindings:
            self.assertTrue(binding.binding_ready)
            self.assertTrue(binding.endpoint_category_match)
            self.assertTrue(binding.usable_for_dry_run_plans)
            self.assertTrue(binding.provider_disabled_by_default)
            self.assertTrue(binding.adapter_disabled)

    def test_bindings_are_non_live_non_networked_and_non_executable(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()

        for binding in result.bindings:
            self.assertFalse(binding.live_fetch_enabled)
            self.assertFalse(binding.network_call_allowed)
            self.assertFalse(binding.raw_response_storage_allowed)
            self.assertFalse(binding.live_adapter_record_emission_allowed)
            self.assertFalse(binding.creates_buy_request)
            self.assertFalse(binding.connects_broker)
            self.assertFalse(binding.places_order)
            self.assertFalse(binding.executes_trade)
            self.assertTrue(binding.safe_binding_only())

    def test_selected_candidate_has_provider_binding(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()

        self.assertGreaterEqual(result.selected_candidate_binding_count, 1)
        self.assertTrue(any(binding.candidate_id == result.selected_candidate_id for binding in result.bindings))

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_9_public_provider_skeleton_binding_audit(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Binding override must be" in blocker for blocker in blocked.blockers))

    def test_empty_bindings_block(self) -> None:
        blocked = audit_v7_9_public_provider_skeleton_binding_audit(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public provider skeleton bindings" in blocker for blocker in blocked.blockers))

    def test_duplicate_binding_id_blocks(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        blocked = audit_v7_9_public_provider_skeleton_binding_audit(
            result.bindings + (result.bindings[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_unready_binding_blocks(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        bad = replace(
            result.bindings[0],
            binding_ready=False,
            endpoint_category_match=False,
        )

        blocked = audit_v7_9_public_provider_skeleton_binding_audit(
            (bad,) + result.bindings[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("endpoint category must match" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("binding must be ready" in blocker for blocker in blocked.blockers))

    def test_enabling_provider_or_adapter_blocks(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        bad = replace(
            result.bindings[0],
            provider_disabled_by_default=False,
            adapter_disabled=False,
        )

        blocked = audit_v7_9_public_provider_skeleton_binding_audit(
            (bad,) + result.bindings[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("provider must remain disabled by default" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("adapter skeleton must remain disabled" in blocker for blocker in blocked.blockers))

    def test_live_network_raw_or_emit_blocks(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        bad = replace(
            result.bindings[0],
            live_fetch_enabled=True,
            network_call_allowed=True,
            raw_response_storage_allowed=True,
            live_adapter_record_emission_allowed=True,
        )

        blocked = audit_v7_9_public_provider_skeleton_binding_audit(
            (bad,) + result.bindings[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_execution_fields_block(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        bad = replace(
            result.bindings[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_9_public_provider_skeleton_binding_audit(
            (bad,) + result.bindings[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_9_public_provider_skeleton_binding_audit()
        payload = result.to_dict()

        self.assertTrue(payload["binding_audit_only"])
        self.assertTrue(payload["providers_disabled_by_default"])
        self.assertTrue(payload["adapters_disabled_by_default"])
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
