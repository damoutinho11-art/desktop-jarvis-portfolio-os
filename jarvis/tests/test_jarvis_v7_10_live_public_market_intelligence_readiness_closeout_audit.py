import unittest
from dataclasses import replace

from jarvis.jarvis_v7_10_live_public_market_intelligence_readiness_closeout_audit import (
    CHECK_FAIL,
    CLOSEOUT_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_10_live_public_market_intelligence_readiness_closeout_audit,
)


class JarvisV710LivePublicMarketIntelligenceReadinessCloseoutAuditTests(unittest.TestCase):
    def test_readiness_closeout_is_ready_and_points_to_v8_dashboard(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.closeout_status, CLOSEOUT_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v8_0_public_market_intelligence_operator_dashboard")
        self.assertTrue(result.readiness_closeout_ready)
        self.assertTrue(result.v7_chain_closeout_complete)
        self.assertEqual(result.failed_check_count, 0)
        self.assertEqual(result.passed_check_count, result.check_count)
        self.assertGreaterEqual(result.chain_stage_count, 10)
        self.assertGreaterEqual(result.ready_chain_stage_count, 10)
        self.assertFalse(result.live_fetch_enablement_allowed)
        self.assertFalse(result.blockers)

    def test_closeout_covers_every_v7_stage(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        stage_ids = {check.stage_id for check in result.checks}

        self.assertIn("v7.0", stage_ids)
        self.assertIn("v7.1", stage_ids)
        self.assertIn("v7.2", stage_ids)
        self.assertIn("v7.3", stage_ids)
        self.assertIn("v7.4", stage_ids)
        self.assertIn("v7.5", stage_ids)
        self.assertIn("v7.6", stage_ids)
        self.assertIn("v7.7", stage_ids)
        self.assertIn("v7.8", stage_ids)
        self.assertIn("v7.9", stage_ids)

    def test_closeout_checks_are_required_and_non_executable(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()

        for check in result.checks:
            self.assertTrue(check.required_for_closeout)
            self.assertTrue(check.passed())
            self.assertFalse(check.live_fetch_enabled)
            self.assertFalse(check.network_call_attempted)
            self.assertFalse(check.raw_response_stored)
            self.assertFalse(check.live_adapter_record_emitted)
            self.assertFalse(check.creates_buy_request)
            self.assertFalse(check.connects_broker)
            self.assertFalse(check.places_order)
            self.assertFalse(check.executes_trade)
            self.assertTrue(check.safe_closeout_check_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Closeout check override must be" in blocker for blocker in blocked.blockers))

    def test_empty_checks_block(self) -> None:
        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No live public market readiness closeout checks" in blocker for blocker in blocked.blockers))

    def test_duplicate_check_id_blocks(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(
            result.checks + (result.checks[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_failed_check_blocks(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        bad = replace(result.checks[0], status=CHECK_FAIL)

        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(
            (bad,) + result.checks[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("closeout check failed" in blocker for blocker in blocked.blockers))

    def test_non_required_check_blocks(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        bad = replace(result.checks[0], required_for_closeout=False)

        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(
            (bad,) + result.checks[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("check must be required for closeout" in blocker for blocker in blocked.blockers))

    def test_unsafe_check_blocks(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        bad = replace(
            result.checks[0],
            live_fetch_enabled=True,
            network_call_attempted=True,
            raw_response_stored=True,
            live_adapter_record_emitted=True,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(
            (bad,) + result.checks[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
        payload = result.to_dict()

        self.assertTrue(payload["closeout_audit_only"])
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
        self.assertFalse(payload["live_fetch_enablement_allowed"])


if __name__ == "__main__":
    unittest.main()
