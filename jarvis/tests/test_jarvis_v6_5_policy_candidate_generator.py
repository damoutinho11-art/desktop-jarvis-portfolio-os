import unittest
from dataclasses import replace

from jarvis.jarvis_v6_5_policy_candidate_generator import (
    POLICY_STATUS_BLOCKED,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_5_policy_candidate_generator,
)


class JarvisV65PolicyCandidateGeneratorTests(unittest.TestCase):
    def test_policy_generator_is_ready_and_points_to_manual_review_queue(self) -> None:
        result = audit_v6_5_policy_candidate_generator()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.6_manual_policy_review_queue")
        self.assertTrue(result.policy_candidate_generation_ready)
        self.assertEqual(result.policy_candidate_count, 4)
        self.assertEqual(result.manual_review_candidate_count, 4)
        self.assertEqual(result.blocked_policy_candidate_count, 0)
        self.assertFalse(result.blockers)

    def test_policy_candidates_include_expected_strategic_variants(self) -> None:
        result = audit_v6_5_policy_candidate_generator()
        ids = {candidate.policy_id for candidate in result.policy_candidates}

        self.assertEqual(
            ids,
            {
                "balanced_aggressive_manual_review",
                "etf_heavy_with_crypto_allowance",
                "core_etf_btc_accumulation",
                "defensive_cash_bond_aware",
            },
        )

    def test_candidates_use_quality_ready_or_watchlist_assets_only(self) -> None:
        result = audit_v6_5_policy_candidate_generator()

        allowed_quality_statuses = {"QUALITY_READY", "QUALITY_WATCHLIST"}
        for candidate in result.policy_candidates:
            for selection in candidate.selected_assets:
                self.assertIn(selection.quality_status, allowed_quality_statuses)
                self.assertTrue(selection.included_for_policy_generation)

    def test_speculative_crypto_is_explicitly_excluded_until_quality_improves(self) -> None:
        result = audit_v6_5_policy_candidate_generator()

        for candidate in result.policy_candidates:
            exclusions = " ".join(candidate.explicit_exclusions)
            self.assertIn("hype_candidate excluded", exclusions)
            self.assertIn("tao_candidate excluded", exclusions)

    def test_crypto_ceiling_and_defensive_floor_are_enforced(self) -> None:
        result = audit_v6_5_policy_candidate_generator()

        for candidate in result.policy_candidates:
            self.assertLessEqual(candidate.max_crypto_weight_pct(), 35.0)
            self.assertGreaterEqual(candidate.min_cash_or_defensive_pct(), 3.0)
            self.assertTrue(candidate.has_valid_bands())

    def test_no_policy_is_approved_active_buy_ready_or_executable(self) -> None:
        result = audit_v6_5_policy_candidate_generator()

        for candidate in result.policy_candidates:
            self.assertTrue(candidate.manual_review_required)
            self.assertFalse(candidate.operator_approved)
            self.assertFalse(candidate.active_policy_mutated)
            self.assertFalse(candidate.creates_weekly_buy_ticket)
            self.assertFalse(candidate.creates_buy_request)
            self.assertFalse(candidate.executes_trade)

    def test_bad_policy_candidate_blocks(self) -> None:
        result = audit_v6_5_policy_candidate_generator()
        bad = replace(
            result.policy_candidates[0],
            operator_approved=True,
            active_policy_mutated=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )

        blocked = audit_v6_5_policy_candidate_generator((bad,) + result.policy_candidates[1:])

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("operator approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("active policy mutation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_policy_id_blocks(self) -> None:
        result = audit_v6_5_policy_candidate_generator()
        duplicate = replace(result.policy_candidates[0], display_name="Duplicate")

        blocked = audit_v6_5_policy_candidate_generator(result.policy_candidates + (duplicate,))

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_blocked_policy_count_is_reported(self) -> None:
        result = audit_v6_5_policy_candidate_generator()
        blocked_candidate = replace(
            result.policy_candidates[0],
            policy_status=POLICY_STATUS_BLOCKED,
            blockers=("Synthetic blocker.",),
        )

        blocked = audit_v6_5_policy_candidate_generator((blocked_candidate,) + result.policy_candidates[1:])

        self.assertEqual(blocked.blocked_policy_candidate_count, 1)

    def test_safety_flags_defer_approval_buy_request_and_execution(self) -> None:
        result = audit_v6_5_policy_candidate_generator()
        payload = result.to_dict()

        self.assertTrue(payload["manual_review_required"])
        self.assertFalse(payload["active_policy_mutated"])
        self.assertTrue(payload["policy_approval_deferred"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["automatic_approval_forbidden"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
