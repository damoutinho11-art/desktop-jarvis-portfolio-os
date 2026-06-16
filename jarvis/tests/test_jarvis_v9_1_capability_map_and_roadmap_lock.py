import unittest

from jarvis.jarvis_v9_1_capability_map_and_roadmap_lock import (
    ROADMAP_LOCK_READY,
    STATUS_READY,
    audit_v9_1_capability_map_and_roadmap_lock,
)


class JarvisV91CapabilityMapAndRoadmapLockTests(unittest.TestCase):
    def test_roadmap_lock_is_ready_and_has_no_stale_references(self) -> None:
        result = audit_v9_1_capability_map_and_roadmap_lock()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.roadmap_lock_status, ROADMAP_LOCK_READY)
        self.assertEqual(result.recommended_next_stage, "v10_0_autonomous_public_data_refresh_runtime")
        self.assertTrue(result.capability_map_ready)
        self.assertTrue(result.roadmap_lock_ready)
        self.assertEqual(result.missing_capability_count, 0)
        self.assertEqual(result.stale_roadmap_reference_count, 0)
        self.assertEqual(result.active_roadmap_reference_count, 4)
        self.assertFalse(result.blockers)

    def test_existing_capability_map_prevents_redundant_planner_and_source_stages(self) -> None:
        result = audit_v9_1_capability_map_and_roadmap_lock()
        ids = {entry.capability_id for entry in result.capability_map_entries}

        self.assertIn("v7_4_live_public_dry_run_planner", ids)
        self.assertIn("v7_7_enablement_preflight", ids)
        self.assertIn("v7_8_provider_configuration_registry", ids)
        self.assertIn("dynamic_market_source_binding", ids)
        self.assertIn("dynamic_market_import_plan", ids)
        self.assertIn("v9_0_enablement_decision_layer", ids)
        self.assertTrue(result.source_selection_not_repeated)
        self.assertTrue(result.dry_run_planner_not_rebuilt)
        self.assertTrue(result.provider_registry_not_rebuilt)

    def test_safety_flags_hold(self) -> None:
        payload = audit_v9_1_capability_map_and_roadmap_lock().to_dict()

        self.assertTrue(payload["public_data_enablement_decision_preserved"])
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

