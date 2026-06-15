import unittest
from dataclasses import replace

from jarvis.jarvis_v7_7_live_public_market_intelligence_enablement_preflight import (
    CHECK_FAIL,
    PREFLIGHT_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_7_live_public_market_intelligence_enablement_preflight,
)


class JarvisV77LivePublicMarketIntelligenceEnablementPreflightTests(unittest.TestCase):
    def test_enablement_preflight_is_ready_but_does_not_allow_live_fetch(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.preflight_status, PREFLIGHT_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_8_public_provider_configuration_registry")
        self.assertTrue(result.enablement_preflight_ready)
        self.assertTrue(result.compatible_with_v7_6_disabled_adapter_skeleton)
        self.assertGreaterEqual(result.requirement_count, 10)
        self.assertEqual(result.failed_requirement_count, 0)
        self.assertEqual(result.passed_requirement_count, result.requirement_count)
        self.assertFalse(result.live_fetch_enablement_allowed)
        self.assertFalse(result.blockers)

    def test_all_requirements_are_required_before_live_enablement(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()

        self.assertEqual(result.required_before_live_enablement_count, result.requirement_count)
        for requirement in result.requirements:
            self.assertTrue(requirement.required_before_live_enablement)
            self.assertTrue(requirement.passed())

    def test_preflight_requirements_preserve_disabled_non_executable_state(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()

        for requirement in result.requirements:
            self.assertTrue(requirement.adapter_still_disabled)
            self.assertTrue(requirement.live_fetch_still_disabled)
            self.assertTrue(requirement.network_calls_still_disabled)
            self.assertTrue(requirement.raw_response_storage_still_disabled)
            self.assertTrue(requirement.live_adapter_record_emission_still_disabled)
            self.assertFalse(requirement.creates_buy_request)
            self.assertFalse(requirement.connects_broker)
            self.assertFalse(requirement.places_order)
            self.assertFalse(requirement.executes_trade)
            self.assertTrue(requirement.safe_preflight_only())

    def test_expected_preflight_requirements_exist(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        requirement_ids = {requirement.requirement_id for requirement in result.requirements}

        self.assertIn("disabled_adapter_skeleton_ready", requirement_ids)
        self.assertIn("adapter_disabled_by_default", requirement_ids)
        self.assertIn("selected_candidate_coverage", requirement_ids)
        self.assertIn("boundary_dry_run_normalizer_wired", requirement_ids)
        self.assertIn("live_fetch_deferred", requirement_ids)
        self.assertIn("network_calls_deferred", requirement_ids)
        self.assertIn("raw_response_storage_deferred", requirement_ids)
        self.assertIn("live_adapter_record_emission_deferred", requirement_ids)
        self.assertIn("execution_boundary_preserved", requirement_ids)
        self.assertIn("manual_final_buy_boundary_preserved", requirement_ids)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Preflight requirement override must be" in blocker for blocker in blocked.blockers))

    def test_empty_requirements_block(self) -> None:
        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No live public market enablement preflight requirements" in blocker for blocker in blocked.blockers))

    def test_duplicate_requirement_id_blocks(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(
            result.requirements + (result.requirements[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_failed_requirement_blocks(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        bad = replace(
            result.requirements[0],
            status=CHECK_FAIL,
            blocker_if_failed="Synthetic failed preflight requirement.",
        )

        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(
            (bad,) + result.requirements[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Synthetic failed preflight requirement" in blocker for blocker in blocked.blockers))

    def test_non_required_requirement_blocks(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        bad = replace(result.requirements[0], required_before_live_enablement=False)

        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(
            (bad,) + result.requirements[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must be marked required before live enablement" in blocker for blocker in blocked.blockers))

    def test_unsafe_requirement_blocks(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        bad = replace(
            result.requirements[0],
            adapter_still_disabled=False,
            live_fetch_still_disabled=False,
            network_calls_still_disabled=False,
            raw_response_storage_still_disabled=False,
            live_adapter_record_emission_still_disabled=False,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_7_live_public_market_intelligence_enablement_preflight(
            (bad,) + result.requirements[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("adapter must still be disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetch must still be disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls must still be disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage must still be disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission must still be disabled" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_7_live_public_market_intelligence_enablement_preflight()
        payload = result.to_dict()

        self.assertTrue(payload["preflight_only"])
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
        self.assertFalse(payload["live_fetch_enablement_allowed"])


if __name__ == "__main__":
    unittest.main()
