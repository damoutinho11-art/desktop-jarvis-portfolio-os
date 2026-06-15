import unittest
from dataclasses import replace

from jarvis.jarvis_v6_15_autonomous_command_center_closeout_audit import (
    CHECK_FAIL,
    CHECK_PASS,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_15_autonomous_command_center_closeout_audit,
)


class JarvisV615AutonomousCommandCenterCloseoutAuditTests(unittest.TestCase):
    def test_closeout_audit_is_ready_and_points_to_market_intelligence(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_0_autonomous_market_intelligence_expansion")
        self.assertTrue(result.closeout_audit_ready)
        self.assertTrue(result.v6_chain_complete)
        self.assertTrue(result.autonomous_intelligence_ready)
        self.assertTrue(result.command_center_ready)
        self.assertEqual(result.failed_check_count, 0)
        self.assertFalse(result.blockers)

    def test_all_expected_closeout_checks_pass(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()
        check_ids = {check.check_id for check in result.checks}

        self.assertIn("active_policy_gap_analysis_ready", check_ids)
        self.assertIn("weekly_planning_context_ready", check_ids)
        self.assertIn("weekly_shortlist_ready", check_ids)
        self.assertIn("autonomous_recommendation_ready", check_ids)
        self.assertIn("dashboard_integration_ready", check_ids)
        self.assertIn("only_final_buy_is_manual", check_ids)
        self.assertIn("no_execution_path_exists", check_ids)

        for check in result.checks:
            self.assertEqual(check.status, CHECK_PASS)
            self.assertTrue(check.passed())

    def test_selected_recommendation_is_carried_forward(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()

        self.assertTrue(result.selected_candidate_id)
        self.assertTrue(result.selected_sleeve_id)
        self.assertEqual(result.analyzed_policy_id, "active_balanced_aggressive_manual_review")

    def test_no_manual_review_queue_is_added(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()

        self.assertTrue(result.no_manual_review_queue_added)
        self.assertTrue(any("not another manual review queue" in warning for warning in result.warnings))

    def test_only_final_user_buy_action_remains_manual(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()

        self.assertTrue(result.final_user_buy_action_required)
        only_manual_check = next(check for check in result.checks if check.check_id == "only_final_buy_is_manual")
        self.assertEqual(only_manual_check.status, CHECK_PASS)

    def test_no_execution_path_exists(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()

        self.assertTrue(result.no_buy_request_created)
        self.assertTrue(result.no_broker_connection_created)
        self.assertTrue(result.no_order_placement_created)
        self.assertTrue(result.no_trades_executed)

        execution_check = next(check for check in result.checks if check.check_id == "no_execution_path_exists")
        self.assertEqual(execution_check.status, CHECK_PASS)

    def test_failed_check_blocks(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()
        bad_check = replace(
            result.checks[0],
            status=CHECK_FAIL,
            blocker_if_failed="Synthetic failed closeout check.",
        )

        blocked = audit_v6_15_autonomous_command_center_closeout_audit(
            (bad_check,) + result.checks[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Synthetic failed closeout check" in blocker for blocker in blocked.blockers))

    def test_unsafe_check_blocks(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()
        bad_check = replace(
            result.checks[0],
            no_buy_request=False,
            no_broker_connection=False,
            no_order_placement=False,
            no_trade_execution=False,
        )

        blocked = audit_v6_15_autonomous_command_center_closeout_audit(
            (bad_check,) + result.checks[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request path is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection path is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement path is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution path is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_check_id_blocks(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()
        duplicate = result.checks[0]

        blocked = audit_v6_15_autonomous_command_center_closeout_audit(
            result.checks + (duplicate,)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_payload_preserves_safety_flags(self) -> None:
        result = audit_v6_15_autonomous_command_center_closeout_audit()
        payload = result.to_dict()

        self.assertTrue(payload["no_manual_review_queue_added"])
        self.assertTrue(payload["no_buy_request_created"])
        self.assertTrue(payload["no_broker_connection_created"])
        self.assertTrue(payload["no_order_placement_created"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
