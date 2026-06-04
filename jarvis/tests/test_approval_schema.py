import unittest

from jarvis.approval_schema import ApprovalDecision, ApprovalSchemaError, parse_approval_request


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


class ApprovalSchemaTests(unittest.TestCase):
    def test_valid_buy_request_parses(self) -> None:
        request = parse_approval_request(_valid_buy_payload())

        self.assertEqual(request.request_id, "req_valid_buy")
        self.assertTrue(request.manual_approval_required)
        self.assertFalse(request.auto_execute)

    def test_invalid_status_rejected(self) -> None:
        with self.assertRaisesRegex(ApprovalSchemaError, "status blocked is not allowed"):
            parse_approval_request(_valid_buy_payload(status="blocked"))

    def test_decision_accepts_allowed_values(self) -> None:
        decision = ApprovalDecision("req_valid_buy", "approved", "2026-06-04T09:01:00+00:00", "tester")

        self.assertEqual(decision.decision, "approved")

    def test_decision_rejects_unknown_value(self) -> None:
        with self.assertRaisesRegex(ApprovalSchemaError, "decision maybe is not allowed"):
            ApprovalDecision("req_valid_buy", "maybe", "2026-06-04T09:01:00+00:00", "tester")


if __name__ == "__main__":
    unittest.main()
