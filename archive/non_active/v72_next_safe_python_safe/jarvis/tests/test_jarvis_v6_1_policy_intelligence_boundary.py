import unittest

from jarvis.jarvis_v6_1_policy_intelligence_boundary import (
    POLICY_NEEDS_REVIEW,
    POLICY_RECOMMENDED_FOR_REVIEW,
    STATUS_READY,
    audit_v6_1_policy_intelligence_boundary,
)


class JarvisV61PolicyIntelligenceBoundaryTests(unittest.TestCase):
    def test_boundary_is_ready_and_points_to_private_snapshot_next(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.2_private_portfolio_snapshot_v2")
        self.assertEqual(result.candidate_policy_count, 3)
        self.assertEqual(result.recommended_policy_id, "balanced_aggressive_flexible_bands")
        self.assertFalse(result.blockers)

    def test_recommended_policy_uses_flexible_bands_not_strict_allocations(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()
        recommended = next(
            policy
            for policy in result.candidate_policies
            if policy.policy_id == result.recommended_policy_id
        )

        self.assertEqual(recommended.status, POLICY_RECOMMENDED_FOR_REVIEW)
        self.assertTrue(recommended.uses_flexible_bands())
        self.assertTrue(all(band.min_weight_pct != band.max_weight_pct for band in recommended.bands))

    def test_global_etf_is_core_not_the_whole_etf_universe(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()
        recommended = next(
            policy
            for policy in result.candidate_policies
            if policy.policy_id == result.recommended_policy_id
        )
        all_assets = {
            asset
            for band in recommended.bands
            for asset in band.asset_universe
        }

        self.assertIn("global_all_world_etf", all_assets)
        self.assertIn("quality_factor_etf", all_assets)
        self.assertIn("momentum_factor_etf", all_assets)
        self.assertIn("sp_500_etf", all_assets)
        self.assertIn("single_stock_candidate", all_assets)
        self.assertTrue(recommended.has_broad_etf_universe())

    def test_weekly_crypto_buying_is_allowed_but_bounded(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()
        recommended = next(
            policy
            for policy in result.candidate_policies
            if policy.policy_id == result.recommended_policy_id
        )
        crypto_bands = [band for band in recommended.bands if "crypto" in band.sleeve_id]

        self.assertTrue(recommended.crypto_weekly_buy_allowed())
        self.assertTrue(result.weekly_crypto_buy_allowed_if_within_risk_bands)
        self.assertEqual(len(crypto_bands), 2)
        self.assertLessEqual(recommended.max_crypto_weight_pct(), 30.0)
        self.assertTrue(all(band.weekly_buy_allowed for band in crypto_bands))

    def test_high_crypto_candidate_requires_review_not_default_recommendation(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()
        high_crypto = next(
            policy
            for policy in result.candidate_policies
            if policy.policy_id == "high_crypto_aggressive_review"
        )

        self.assertEqual(high_crypto.status, POLICY_NEEDS_REVIEW)
        self.assertLess(high_crypto.score_total, 80)
        self.assertTrue(
            any("Crypto concentration" in item for item in high_crypto.counterarguments)
        )

    def test_policy_change_tickets_are_review_only(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()

        self.assertEqual(len(result.policy_change_tickets), result.candidate_policy_count)
        for ticket in result.policy_change_tickets:
            self.assertTrue(ticket.manual_approval_required)
            self.assertFalse(ticket.approved)
            self.assertFalse(ticket.active_policy_mutated)
            self.assertFalse(ticket.creates_buy_request)
            self.assertFalse(ticket.executes_trade)

    def test_safety_flags_forbid_auto_policy_change_and_execution(self) -> None:
        result = audit_v6_1_policy_intelligence_boundary()
        payload = result.to_dict()

        self.assertFalse(payload["active_policy_mutated"])
        self.assertTrue(payload["automatic_policy_change_forbidden"])
        self.assertTrue(payload["automatic_approval_forbidden"])
        self.assertTrue(payload["manual_policy_approval_required"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
