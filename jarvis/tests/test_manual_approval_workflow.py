import json
import tempfile
import unittest
from pathlib import Path

from jarvis.approval_schema import ApprovalSchemaError, parse_approval_request
from jarvis.manual_approval_workflow import approve_request, reject_request, validate_approval_request


def _valid_buy_payload(**overrides):
    payload = {
        "request_id": "req_valid_buy",
        "created_at": "2026-06-04T09:00:00+00:00",
        "action_type": "buy",
        "asset_id": "quality_etf_candidate",
        "amount_eur": 25.0,
        "platform": "manual_fixture_platform",
        "rationale": "Fixture-only approval request.",
        "risks": ["not a recommendation"],
        "required_confirmations": ["manual_review_completed"],
        "status": "pending_manual_approval",
        "manual_approval_required": True,
        "auto_execute": False,
    }
    payload.update(overrides)
    return payload


def _request(**overrides):
    return parse_approval_request(_valid_buy_payload(**overrides))


class ManualApprovalWorkflowTests(unittest.TestCase):
    def test_valid_buy_request_remains_pending_manual_approval(self) -> None:
        result = validate_approval_request(_request())

        self.assertTrue(result.valid)
        self.assertEqual(result.effective_status, "pending_manual_approval")

    def test_auto_execute_true_is_blocked(self) -> None:
        result = validate_approval_request(_request(auto_execute=True))

        self.assertFalse(result.valid)
        self.assertIn("auto_execute must always be false.", result.blockers)

    def test_missing_manual_approval_requirement_rejected(self) -> None:
        result = validate_approval_request(_request(manual_approval_required=False))

        self.assertFalse(result.valid)
        self.assertIn("manual_approval_required must always be true.", result.blockers)

    def test_buy_missing_asset_id_rejected(self) -> None:
        result = validate_approval_request(_request(asset_id=None))

        self.assertFalse(result.valid)
        self.assertIn("buy action requires asset_id.", result.blockers)

    def test_buy_with_non_positive_amount_rejected(self) -> None:
        result = validate_approval_request(_request(amount_eur=0.0))

        self.assertFalse(result.valid)
        self.assertIn("buy action requires amount_eur > 0.", result.blockers)

    def test_sell_missing_safety_acknowledgement_rejected(self) -> None:
        request = _request(
            action_type="sell",
            amount_eur=10.0,
            required_confirmations=[],
        )

        result = validate_approval_request(request)

        self.assertFalse(result.valid)
        self.assertIn("sell action requires sell_safety_acknowledgement.", result.blockers)

    def test_emergency_fund_action_requires_ack_or_warns_high_risk(self) -> None:
        missing_ack = _request(action_type="hold_cash", source_account_id="emergency_fund")
        blocked = validate_approval_request(missing_ack)
        acknowledged = _request(
            action_type="hold_cash",
            source_account_id="emergency_fund",
            required_confirmations=["emergency_fund_override_acknowledged"],
        )
        warned = validate_approval_request(acknowledged)

        self.assertFalse(blocked.valid)
        self.assertTrue(any("emergency reserve usage" in blocker for blocker in blocked.blockers))
        self.assertTrue(warned.valid)
        self.assertTrue(any("high-risk" in warning for warning in warned.warnings))

    def test_investment_account_withdrawal_without_tax_ack_rejected(self) -> None:
        request = _request(action_type="transfer_warning", source_account_id="lightyear")

        result = validate_approval_request(request)

        self.assertFalse(result.valid)
        self.assertIn(
            "investment-account withdrawal requires investment_account_tax_warning_acknowledged.",
            result.blockers,
        )

    def test_approval_changes_status_but_does_not_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "decisions.jsonl"
            approved, decision = approve_request(_request(), "tester", "looks fine", log_path)

            payload = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(approved.status, "approved")
            self.assertFalse(approved.auto_execute)
            self.assertEqual(decision.decision, "approved")
            self.assertFalse(payload["trades_executed"])

    def test_rejection_changes_status_but_does_not_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "decisions.jsonl"
            rejected, decision = reject_request(_request(), "tester", "no", log_path)

            payload = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(rejected.status, "rejected")
            self.assertEqual(decision.decision, "rejected")
            self.assertFalse(payload["trades_executed"])

    def test_executed_manually_cannot_be_created_directly(self) -> None:
        result = validate_approval_request(_request(status="executed_manually"))

        self.assertFalse(result.valid)
        self.assertIn("executed_manually cannot be created directly without prior approved status.", result.blockers)

    def test_blocked_request_cannot_be_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "decisions.jsonl"
            with self.assertRaisesRegex(ApprovalSchemaError, "blocked requests cannot be approved"):
                approve_request(_request(auto_execute=True), "tester", "", log_path)


if __name__ == "__main__":
    unittest.main()
