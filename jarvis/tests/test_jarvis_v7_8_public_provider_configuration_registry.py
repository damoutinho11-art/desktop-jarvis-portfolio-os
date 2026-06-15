import unittest
from dataclasses import replace

from jarvis.jarvis_v7_8_public_provider_configuration_registry import (
    AUTH_MODE_ENV_API_KEY,
    AUTH_MODE_NONE,
    REGISTRY_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_8_public_provider_configuration_registry,
)


class JarvisV78PublicProviderConfigurationRegistryTests(unittest.TestCase):
    def test_provider_registry_is_ready_and_points_to_binding_audit(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.registry_status, REGISTRY_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_9_public_provider_skeleton_binding_audit")
        self.assertTrue(result.provider_registry_ready)
        self.assertTrue(result.compatible_with_v7_7_enablement_preflight)
        self.assertGreaterEqual(result.provider_count, 4)
        self.assertGreaterEqual(result.selected_candidate_provider_count, 1)
        self.assertEqual(result.enabled_provider_count, 0)
        self.assertEqual(result.live_fetch_enabled_count, 0)
        self.assertEqual(result.network_call_allowed_count, 0)
        self.assertEqual(result.raw_response_storage_allowed_count, 0)
        self.assertEqual(result.live_adapter_record_emit_count, 0)
        self.assertGreaterEqual(result.no_auth_provider_count, 1)
        self.assertGreaterEqual(result.env_api_key_provider_count, 1)
        self.assertFalse(result.blockers)

    def test_provider_registry_covers_required_endpoint_categories(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        categories = {provider.endpoint_category for provider in result.providers}

        self.assertIn("PUBLIC_CRYPTO_MARKET_CONTEXT", categories)
        self.assertIn("PUBLIC_VOLATILITY_CONTEXT", categories)
        self.assertIn("PUBLIC_ETF_MARKET_CONTEXT", categories)
        self.assertIn("PUBLIC_NEWS_RISK_CONTEXT", categories)

    def test_provider_configs_are_disabled_non_networked_and_non_executable(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()

        for provider in result.providers:
            self.assertTrue(provider.usable_for_dry_run_plans)
            self.assertFalse(provider.provider_enabled_by_default)
            self.assertFalse(provider.live_fetch_enabled)
            self.assertFalse(provider.network_call_allowed)
            self.assertFalse(provider.raw_response_storage_allowed)
            self.assertFalse(provider.emits_live_adapter_record)
            self.assertFalse(provider.creates_buy_request)
            self.assertFalse(provider.connects_broker)
            self.assertFalse(provider.places_order)
            self.assertFalse(provider.executes_trade)
            self.assertTrue(provider.safe_configuration_only())

    def test_auth_modes_are_valid(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()

        for provider in result.providers:
            self.assertIn(provider.auth_mode, {AUTH_MODE_NONE, AUTH_MODE_ENV_API_KEY})
            if provider.auth_mode == AUTH_MODE_ENV_API_KEY:
                self.assertTrue(provider.api_key_env_var)
            if provider.auth_mode == AUTH_MODE_NONE:
                self.assertFalse(provider.api_key_env_var)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_8_public_provider_configuration_registry(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Provider override must be" in blocker for blocker in blocked.blockers))

    def test_empty_providers_block(self) -> None:
        blocked = audit_v7_8_public_provider_configuration_registry(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public provider configurations" in blocker for blocker in blocked.blockers))

    def test_duplicate_provider_id_blocks(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        blocked = audit_v7_8_public_provider_configuration_registry(
            result.providers + (result.providers[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_enabling_provider_or_live_fetch_blocks(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        bad = replace(
            result.providers[0],
            provider_enabled_by_default=True,
            live_fetch_enabled=True,
        )

        blocked = audit_v7_8_public_provider_configuration_registry(
            (bad,) + result.providers[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("provider must be disabled by default" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))

    def test_network_or_raw_storage_or_live_emit_blocks(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        bad = replace(
            result.providers[0],
            network_call_allowed=True,
            raw_response_storage_allowed=True,
            emits_live_adapter_record=True,
        )

        blocked = audit_v7_8_public_provider_configuration_registry(
            (bad,) + result.providers[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_execution_fields_block(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        bad = replace(
            result.providers[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_8_public_provider_configuration_registry(
            (bad,) + result.providers[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_8_public_provider_configuration_registry()
        payload = result.to_dict()

        self.assertTrue(payload["registry_only"])
        self.assertTrue(payload["providers_disabled_by_default"])
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
