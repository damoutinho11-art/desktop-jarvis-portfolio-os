import unittest

from jarvis.asset_status_workflow import parse_asset_status_request, validate_asset_status_request


WATCHLIST_CONFIRMATIONS = [
    "candidate_review_pack_present",
    "scorecard_reviewed",
    "risk_metrics_reviewed",
]
ETF_INVESTABLE_CONFIRMATIONS = [
    *WATCHLIST_CONFIRMATIONS,
    "concentration_reviewed",
    "platform_tax_fit_reviewed",
    "manual_asset_approval_confirmed",
    "expense_ratio_reviewed",
    "overlap_concentration_reviewed",
    "accumulating_distribution_reviewed",
    "platform_availability_reviewed",
]
CRYPTO_INVESTABLE_CONFIRMATIONS = [
    *WATCHLIST_CONFIRMATIONS,
    "platform_tax_fit_reviewed",
    "manual_asset_approval_confirmed",
    "custody_risk_reviewed",
    "crypto_tax_risk_reviewed",
    "position_size_limit_acknowledged",
]


def _request(**overrides):
    payload = {
        "request_id": "status_req",
        "created_at": "2026-06-04T10:00:00+00:00",
        "asset_id": "asset_candidate",
        "asset_type": "ETF",
        "current_status": "candidate_unreviewed",
        "requested_status": "candidate_reviewed",
        "rationale": "Fixture-only status change.",
        "evidence_summary": "Synthetic evidence.",
        "required_confirmations": ["manual_review_completed"],
        "manual_approval_required": True,
        "auto_execute": False,
    }
    payload.update(overrides)
    return parse_asset_status_request(payload)


class AssetStatusWorkflowTests(unittest.TestCase):
    def test_candidate_unreviewed_to_candidate_reviewed_allowed(self) -> None:
        result = validate_asset_status_request(_request())

        self.assertTrue(result.valid)
        self.assertTrue(result.allowed_transition)

    def test_candidate_reviewed_to_approved_watchlist_allowed_with_confirmations(self) -> None:
        result = validate_asset_status_request(
            _request(
                current_status="candidate_reviewed",
                requested_status="approved_watchlist",
                required_confirmations=WATCHLIST_CONFIRMATIONS,
            )
        )

        self.assertTrue(result.valid)

    def test_approved_watchlist_to_approved_investable_allowed_with_confirmations(self) -> None:
        result = validate_asset_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                required_confirmations=ETF_INVESTABLE_CONFIRMATIONS,
            )
        )

        self.assertTrue(result.valid)

    def test_candidate_unreviewed_to_approved_investable_blocked(self) -> None:
        result = validate_asset_status_request(
            _request(current_status="candidate_unreviewed", requested_status="approved_investable")
        )

        self.assertFalse(result.valid)
        self.assertFalse(result.allowed_transition)

    def test_test_position_to_approved_investable_blocked(self) -> None:
        result = validate_asset_status_request(
            _request(current_status="test_position", requested_status="approved_investable")
        )

        self.assertFalse(result.valid)
        self.assertFalse(result.allowed_transition)

    def test_rejected_to_approved_investable_blocked(self) -> None:
        result = validate_asset_status_request(
            _request(current_status="rejected", requested_status="approved_investable")
        )

        self.assertFalse(result.valid)
        self.assertFalse(result.allowed_transition)

    def test_missing_confirmations_blocked(self) -> None:
        result = validate_asset_status_request(
            _request(current_status="candidate_reviewed", requested_status="approved_watchlist", required_confirmations=[])
        )

        self.assertFalse(result.valid)
        self.assertIn("candidate_review_pack_present", result.missing_confirmations)

    def test_auto_execute_true_blocked(self) -> None:
        result = validate_asset_status_request(_request(auto_execute=True))

        self.assertFalse(result.valid)
        self.assertIn("auto_execute must always be false.", result.blockers)

    def test_manual_approval_required_false_blocked(self) -> None:
        result = validate_asset_status_request(_request(manual_approval_required=False))

        self.assertFalse(result.valid)
        self.assertIn("manual_approval_required must always be true.", result.blockers)

    def test_etf_investable_promotion_requires_etf_specific_confirmations(self) -> None:
        result = validate_asset_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                asset_type="ETF",
                required_confirmations=WATCHLIST_CONFIRMATIONS,
            )
        )

        self.assertFalse(result.valid)
        self.assertIn("expense_ratio_reviewed", result.missing_confirmations)
        self.assertIn("overlap_concentration_reviewed", result.missing_confirmations)

    def test_crypto_investable_promotion_requires_crypto_specific_confirmations(self) -> None:
        result = validate_asset_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                asset_type="crypto",
                required_confirmations=WATCHLIST_CONFIRMATIONS,
            )
        )

        self.assertFalse(result.valid)
        self.assertIn("custody_risk_reviewed", result.missing_confirmations)
        self.assertIn("crypto_tax_risk_reviewed", result.missing_confirmations)

    def test_crypto_investable_promotion_allowed_with_crypto_confirmations(self) -> None:
        result = validate_asset_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                asset_type="crypto",
                required_confirmations=CRYPTO_INVESTABLE_CONFIRMATIONS,
            )
        )

        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()
