import unittest
from dataclasses import replace

from jarvis.jarvis_v6_3_universal_asset_candidate_registry import (
    ASSET_TYPE_BOND_ETF,
    ASSET_TYPE_CASH_LIKE,
    ASSET_TYPE_COMMODITY_ETF,
    ASSET_TYPE_CRYPTO,
    ASSET_TYPE_ETF,
    ASSET_TYPE_FUND,
    ASSET_TYPE_STOCK,
    STATE_BLOCKED,
    STATE_POLICY_CANDIDATE,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v6_3_universal_asset_candidate_registry,
    build_example_universal_asset_candidates,
)


class JarvisV63UniversalAssetCandidateRegistryTests(unittest.TestCase):
    def test_registry_is_ready_and_points_to_quality_scoring_next(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.4_asset_quality_scoring_gate")
        self.assertTrue(result.broad_universe_registry_ready)
        self.assertEqual(result.candidate_count, 12)
        self.assertFalse(result.blockers)

    def test_registry_covers_required_asset_types(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()

        self.assertEqual(
            set(result.asset_types_covered),
            {
                ASSET_TYPE_ETF,
                ASSET_TYPE_FUND,
                ASSET_TYPE_STOCK,
                ASSET_TYPE_CRYPTO,
                ASSET_TYPE_CASH_LIKE,
                ASSET_TYPE_BOND_ETF,
                ASSET_TYPE_COMMODITY_ETF,
            },
        )

    def test_registry_includes_broad_etf_stock_crypto_cash_bond_and_commodity_candidates(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()
        candidate_ids = {candidate.candidate_id for candidate in result.candidates}

        self.assertIn("global_all_world_etf_candidate", candidate_ids)
        self.assertIn("sp_500_etf_candidate", candidate_ids)
        self.assertIn("quality_factor_etf_candidate", candidate_ids)
        self.assertIn("global_equity_fund_candidate", candidate_ids)
        self.assertIn("single_stock_candidate_large_cap", candidate_ids)
        self.assertIn("btc_candidate", candidate_ids)
        self.assertIn("hype_candidate", candidate_ids)
        self.assertIn("tao_candidate", candidate_ids)
        self.assertIn("money_market_candidate", candidate_ids)
        self.assertIn("short_duration_bond_etf_candidate", candidate_ids)
        self.assertIn("gold_or_commodity_etf_candidate", candidate_ids)

    def test_registry_is_candidate_only_not_approval_or_buy_list(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()

        self.assertEqual(result.approved_policy_asset_count, 0)
        self.assertEqual(result.weekly_buy_candidate_count, 0)
        self.assertTrue(result.candidates_only)
        self.assertTrue(result.policy_approval_deferred)
        self.assertTrue(result.weekly_buy_ticket_deferred)

        for candidate in result.candidates:
            self.assertFalse(candidate.operator_approved)
            self.assertFalse(candidate.policy_asset_approved)
            self.assertFalse(candidate.weekly_buy_candidate)
            self.assertFalse(candidate.creates_buy_request)
            self.assertFalse(candidate.executes_trade)

    def test_policy_candidates_can_enter_quality_scoring_without_being_approved(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()
        quality_ready = [
            candidate
            for candidate in result.candidates
            if candidate.can_enter_quality_scoring_next()
        ]

        self.assertGreaterEqual(result.quality_scoring_ready_count, 8)
        self.assertTrue(any(candidate.candidate_state == STATE_POLICY_CANDIDATE for candidate in quality_ready))
        self.assertTrue(all(not candidate.policy_asset_approved for candidate in quality_ready))

    def test_blocked_candidate_is_not_quality_scoring_ready(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()
        blocked = next(
            candidate
            for candidate in result.candidates
            if candidate.candidate_id == "unverified_microcap_crypto_blocked"
        )

        self.assertEqual(blocked.candidate_state, STATE_BLOCKED)
        self.assertFalse(blocked.required_data_ready())
        self.assertFalse(blocked.blocker_free())
        self.assertFalse(blocked.can_enter_quality_scoring_next())

    def test_missing_required_asset_type_blocks(self) -> None:
        candidates = tuple(
            candidate
            for candidate in build_example_universal_asset_candidates()
            if candidate.asset_type != ASSET_TYPE_FUND
        )

        result = audit_v6_3_universal_asset_candidate_registry(candidates)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any(ASSET_TYPE_FUND in blocker for blocker in result.blockers))

    def test_duplicate_candidate_id_blocks(self) -> None:
        candidates = build_example_universal_asset_candidates()
        duplicate = replace(candidates[0], display_name="Duplicate candidate")
        result = audit_v6_3_universal_asset_candidate_registry(candidates + (duplicate,))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in result.blockers))

    def test_approved_or_weekly_buy_candidate_blocks(self) -> None:
        candidates = build_example_universal_asset_candidates()
        bad_candidate = replace(
            candidates[0],
            operator_approved=True,
            policy_asset_approved=True,
            weekly_buy_candidate=True,
        )

        result = audit_v6_3_universal_asset_candidate_registry((bad_candidate,) + candidates[1:])

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("operator approval is forbidden" in blocker for blocker in result.blockers))
        self.assertTrue(any("policy asset approval is forbidden" in blocker for blocker in result.blockers))
        self.assertTrue(any("weekly buy candidacy is forbidden" in blocker for blocker in result.blockers))

    def test_safety_flags_defer_scoring_approval_buy_tickets_and_execution(self) -> None:
        result = audit_v6_3_universal_asset_candidate_registry()
        payload = result.to_dict()

        self.assertTrue(payload["exact_asset_scoring_deferred"])
        self.assertTrue(payload["policy_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertFalse(payload["active_policy_mutated"])
        self.assertTrue(payload["automatic_approval_forbidden"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
