import unittest
from dataclasses import replace

from jarvis.jarvis_v6_12_manual_weekly_candidate_shortlist_builder import (
    REASON_CRYPTO_CEILING_GUARD_ACTIVE,
    REASON_INVESTABLE_CASH_AVAILABLE,
    SHORTLIST_STATUS_MANUAL_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_12_manual_weekly_candidate_shortlist_builder,
)


class JarvisV612ManualWeeklyCandidateShortlistBuilderTests(unittest.TestCase):
    def test_shortlist_builder_is_ready_and_points_to_review_queue(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.13_manual_weekly_shortlist_review_queue")
        self.assertTrue(result.manual_weekly_shortlist_ready)
        self.assertEqual(result.analyzed_policy_id, "active_balanced_aggressive_manual_review")
        self.assertEqual(result.source_planning_context_item_count, 6)
        self.assertGreaterEqual(result.shortlist_candidate_count, 2)
        self.assertFalse(result.blockers)

    def test_shortlist_contains_core_assets_from_under_or_below_context(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        candidate_ids = {candidate.candidate_id for candidate in result.shortlist_candidates}

        self.assertIn("global_all_world_etf_candidate", candidate_ids)
        self.assertIn("btc_candidate", candidate_ids)
        self.assertIn("quality_factor_etf_candidate", candidate_ids)

    def test_shortlist_ranks_are_contiguous(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        ranks = [candidate.rank for candidate in result.shortlist_candidates]

        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))

    def test_crypto_shortlist_candidate_carries_crypto_ceiling_guard(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        crypto_candidates = [
            candidate for candidate in result.shortlist_candidates if candidate.is_crypto_candidate()
        ]

        self.assertTrue(crypto_candidates)
        for candidate in crypto_candidates:
            self.assertIn(REASON_CRYPTO_CEILING_GUARD_ACTIVE, candidate.reason_codes)

    def test_shortlist_candidates_consider_investable_cash_but_not_protected_cash(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()

        self.assertGreaterEqual(result.investable_cash_eur, 0.0)
        self.assertGreaterEqual(result.protected_cash_eur, 0.0)
        for candidate in result.shortlist_candidates:
            self.assertIn(REASON_INVESTABLE_CASH_AVAILABLE, candidate.reason_codes)
            self.assertTrue(any("Protected cash" in constraint for constraint in candidate.constraints))

    def test_shortlist_does_not_create_recommendation_buy_request_broker_or_trade(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()

        for candidate in result.shortlist_candidates:
            self.assertEqual(candidate.shortlist_status, SHORTLIST_STATUS_MANUAL_REVIEW_REQUIRED)
            self.assertTrue(candidate.manual_review_required)
            self.assertFalse(candidate.final_recommendation_created)
            self.assertFalse(candidate.asset_approved)
            self.assertFalse(candidate.creates_weekly_buy_ticket)
            self.assertFalse(candidate.creates_buy_request)
            self.assertFalse(candidate.connects_broker)
            self.assertFalse(candidate.executes_trade)
            self.assertTrue(candidate.safe_shortlist_only())

    def test_empty_shortlist_blocks(self) -> None:
        blocked = audit_v6_12_manual_weekly_candidate_shortlist_builder(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No manual weekly shortlist candidates" in blocker for blocker in blocked.blockers))

    def test_unsafe_shortlist_candidate_blocks(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        bad = replace(
            result.shortlist_candidates[0],
            final_recommendation_created=True,
            asset_approved=True,
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            connects_broker=True,
            executes_trade=True,
        )

        blocked = audit_v6_12_manual_weekly_candidate_shortlist_builder(
            (bad,) + result.shortlist_candidates[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("final recommendation creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("asset approval is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("weekly buy ticket creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_duplicate_shortlist_id_blocks(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        duplicate = replace(result.shortlist_candidates[0], rank=len(result.shortlist_candidates) + 1)

        blocked = audit_v6_12_manual_weekly_candidate_shortlist_builder(
            result.shortlist_candidates + (duplicate,)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_safety_flags_defer_recommendation_asset_buy_request_and_execution(self) -> None:
        result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
        payload = result.to_dict()

        self.assertTrue(payload["shortlist_only"])
        self.assertTrue(payload["final_recommendation_deferred"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
