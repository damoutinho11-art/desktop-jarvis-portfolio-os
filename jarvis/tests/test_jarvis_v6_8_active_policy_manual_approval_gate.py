import unittest
from dataclasses import replace

from jarvis.jarvis_v6_8_active_policy_manual_approval_gate import (
    DECISION_APPROVE_ACTIVE_POLICY_DRAFT,
    DECISION_REQUEST_CHANGES,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_8_active_policy_manual_approval_gate,
)


class JarvisV68ActivePolicyManualApprovalGateTests(unittest.TestCase):
    def test_manual_approval_gate_is_ready_and_points_to_active_policy_registry(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.9_active_policy_registry")
        self.assertTrue(result.manual_approval_gate_ready)
        self.assertEqual(result.source_draft_count, 1)
        self.assertEqual(result.approval_decision_count, 1)
        self.assertEqual(result.approve_count, 1)
        self.assertEqual(result.active_policy_count, 0)
        self.assertFalse(result.blockers)

    def test_approval_decision_authorizes_next_registry_stage_only(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()
        decision = result.approval_decisions[0]

        self.assertEqual(decision.decision, DECISION_APPROVE_ACTIVE_POLICY_DRAFT)
        self.assertTrue(decision.approval_recorded)
        self.assertTrue(decision.authorizes_active_policy_registry_draft)
        self.assertFalse(decision.creates_active_policy)
        self.assertFalse(decision.mutates_active_policy)
        self.assertFalse(decision.approves_assets)
        self.assertFalse(decision.creates_weekly_buy_ticket)
        self.assertFalse(decision.creates_buy_request)
        self.assertFalse(decision.executes_trade)

    def test_approval_record_is_not_an_active_policy(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()

        self.assertEqual(result.active_policy_count, 0)
        self.assertTrue(result.active_policy_registry_deferred)
        self.assertTrue(result.manual_approval_records_only)

    def test_request_changes_requires_change_details(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()
        bad = replace(
            result.approval_decisions[0],
            decision=DECISION_REQUEST_CHANGES,
            required_changes=(),
            authorizes_active_policy_registry_draft=False,
        )

        blocked = audit_v6_8_active_policy_manual_approval_gate((bad,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("required changes are missing" in blocker for blocker in blocked.blockers))

    def test_unsafe_approval_decision_blocks(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()
        bad = replace(
            result.approval_decisions[0],
            creates_active_policy=True,
            mutates_active_policy=True,
            approves_assets=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )

        blocked = audit_v6_8_active_policy_manual_approval_gate((bad,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("active policy creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("active policy mutation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("asset approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_missing_approval_for_source_draft_blocks(self) -> None:
        blocked = audit_v6_8_active_policy_manual_approval_gate(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Missing manual approval decision" in blocker for blocker in blocked.blockers))

    def test_duplicate_approval_draft_id_blocks(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()
        duplicate = replace(result.approval_decisions[0], approval_id="duplicate_approval")

        blocked = audit_v6_8_active_policy_manual_approval_gate(
            result.approval_decisions + (duplicate,)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_registry_asset_buy_request_and_execution(self) -> None:
        result = audit_v6_8_active_policy_manual_approval_gate()
        payload = result.to_dict()

        self.assertTrue(payload["manual_approval_records_only"])
        self.assertTrue(payload["active_policy_registry_deferred"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
