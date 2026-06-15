import unittest
from dataclasses import replace

from jarvis.jarvis_v6_4_asset_quality_scoring_gate import (
    QUALITY_BLOCKED,
    QUALITY_NEEDS_MORE_DATA,
    QUALITY_READY,
    QUALITY_WATCHLIST,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_4_asset_quality_scoring_gate,
    build_example_asset_quality_assessments,
)


class JarvisV64AssetQualityScoringGateTests(unittest.TestCase):
    def test_quality_gate_is_ready_and_points_to_policy_generator_next(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.5_policy_candidate_generator")
        self.assertTrue(result.quality_scoring_ready)
        self.assertEqual(result.assessment_count, 12)
        self.assertGreaterEqual(result.quality_ready_count, 3)
        self.assertGreaterEqual(result.blocked_count, 1)
        self.assertFalse(result.blockers)

    def test_core_etf_and_btc_are_quality_ready(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()
        by_id = {assessment.candidate_id: assessment for assessment in result.assessments}

        self.assertEqual(by_id["global_all_world_etf_candidate"].quality_status, QUALITY_READY)
        self.assertEqual(by_id["btc_candidate"].quality_status, QUALITY_READY)
        self.assertTrue(by_id["global_all_world_etf_candidate"].can_enter_policy_generation_next)
        self.assertTrue(by_id["btc_candidate"].can_enter_policy_generation_next)

    def test_satellites_and_speculative_crypto_are_not_auto_approved(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()
        by_id = {assessment.candidate_id: assessment for assessment in result.assessments}

        self.assertIn(
            by_id["quality_factor_etf_candidate"].quality_status,
            {QUALITY_READY, QUALITY_WATCHLIST},
        )
        self.assertIn(
            by_id["hype_candidate"].quality_status,
            {QUALITY_NEEDS_MORE_DATA, QUALITY_WATCHLIST},
        )
        self.assertIn(
            by_id["tao_candidate"].quality_status,
            {QUALITY_NEEDS_MORE_DATA, QUALITY_WATCHLIST},
        )

        for assessment in result.assessments:
            self.assertFalse(assessment.operator_approved)
            self.assertFalse(assessment.policy_asset_approved)
            self.assertFalse(assessment.weekly_buy_candidate)

    def test_blocked_microcap_crypto_does_not_advance(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()
        blocked = next(
            assessment
            for assessment in result.assessments
            if assessment.candidate_id == "unverified_microcap_crypto_blocked"
        )

        self.assertEqual(blocked.quality_status, QUALITY_BLOCKED)
        self.assertFalse(blocked.can_enter_policy_generation_next)
        self.assertTrue(blocked.blockers)

    def test_quality_statuses_include_ready_watchlist_needs_more_data_and_blocked(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()
        statuses = {assessment.quality_status for assessment in result.assessments}

        self.assertIn(QUALITY_READY, statuses)
        self.assertIn(QUALITY_WATCHLIST, statuses)
        self.assertIn(QUALITY_NEEDS_MORE_DATA, statuses)
        self.assertIn(QUALITY_BLOCKED, statuses)

    def test_approved_or_buy_ready_assessment_blocks(self) -> None:
        assessments = build_example_asset_quality_assessments()
        bad = replace(
            assessments[0],
            operator_approved=True,
            policy_asset_approved=True,
            weekly_buy_candidate=True,
        )

        result = audit_v6_4_asset_quality_scoring_gate((bad,) + assessments[1:])

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("operator approval is forbidden" in blocker for blocker in result.blockers))
        self.assertTrue(any("policy asset approval is forbidden" in blocker for blocker in result.blockers))
        self.assertTrue(any("weekly buy candidacy is forbidden" in blocker for blocker in result.blockers))

    def test_duplicate_assessment_id_blocks(self) -> None:
        assessments = build_example_asset_quality_assessments()
        duplicate = replace(assessments[0], display_name="Duplicate")

        result = audit_v6_4_asset_quality_scoring_gate(assessments + (duplicate,))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in result.blockers))

    def test_safety_flags_defer_policy_approval_buy_tickets_and_execution(self) -> None:
        result = audit_v6_4_asset_quality_scoring_gate()
        payload = result.to_dict()

        self.assertTrue(payload["exact_policy_generation_deferred"])
        self.assertTrue(payload["policy_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertFalse(payload["active_policy_mutated"])
        self.assertTrue(payload["automatic_approval_forbidden"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
