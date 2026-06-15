import unittest
from dataclasses import replace

from jarvis.jarvis_v6_2_private_portfolio_snapshot_v2 import (
    STATUS_BLOCKED,
    STATUS_READY,
    CASH_EMERGENCY_PROTECTED,
    ACCOUNT_CRYPTO_EXCHANGE,
    ACCOUNT_DAILY_BANK,
    ACCOUNT_EMERGENCY_FUND,
    ACCOUNT_INVESTMENT_BROKERAGE,
    ACCOUNT_CASH_BUFFER,
    build_example_private_portfolio_snapshot_v2,
    audit_v6_2_private_portfolio_snapshot_v2,
)


class JarvisV62PrivatePortfolioSnapshotV2Tests(unittest.TestCase):
    def test_default_snapshot_is_ready_and_points_to_universal_asset_registry(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.3_universal_asset_candidate_registry")
        self.assertTrue(result.private_snapshot_v2_ready)
        self.assertFalse(result.blockers)

    def test_cash_is_separated_between_protected_and_investable(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()

        self.assertEqual(result.protected_cash_eur, 5900.0)
        self.assertEqual(result.investable_cash_eur, 350.0)
        self.assertGreater(result.protected_cash_eur, result.investable_cash_eur)

        emergency_bucket = next(
            bucket
            for bucket in result.snapshot.cash_buckets
            if bucket.bucket_id == CASH_EMERGENCY_PROTECTED
        )
        self.assertTrue(emergency_bucket.protected)
        self.assertFalse(emergency_bucket.investable)

    def test_required_account_roles_are_present(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()

        self.assertEqual(
            set(result.required_account_roles),
            {
                ACCOUNT_DAILY_BANK,
                ACCOUNT_EMERGENCY_FUND,
                ACCOUNT_INVESTMENT_BROKERAGE,
                ACCOUNT_CRYPTO_EXCHANGE,
                ACCOUNT_CASH_BUFFER,
            },
        )
        self.assertEqual(set(result.required_account_roles), set(result.account_roles_present))

    def test_holdings_have_platform_routing_and_fresh_manual_sources(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()

        self.assertEqual(len(result.snapshot.holdings), 4)
        for holding in result.snapshot.holdings:
            self.assertTrue(holding.platform)
            self.assertTrue(holding.account_id)
            self.assertTrue(holding.manually_entered)
            self.assertTrue(holding.source_fresh)
            self.assertGreaterEqual(holding.market_value_eur, 0.0)

    def test_sleeve_weights_include_equity_crypto_and_cash(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()

        self.assertIn("equity_core", result.sleeve_weights_pct)
        self.assertIn("crypto_core_btc", result.sleeve_weights_pct)
        self.assertIn("crypto_speculative", result.sleeve_weights_pct)
        self.assertIn("cash_defensive", result.sleeve_weights_pct)
        self.assertAlmostEqual(sum(result.sleeve_weights_pct.values()), 95.7576, places=4)

    def test_stale_snapshot_blocks(self) -> None:
        snapshot = build_example_private_portfolio_snapshot_v2()
        stale_snapshot = replace(snapshot, snapshot_age_hours=100.0)

        result = audit_v6_2_private_portfolio_snapshot_v2(stale_snapshot)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.private_snapshot_v2_ready)
        self.assertTrue(any("older than the allowed freshness" in blocker for blocker in result.blockers))

    def test_protected_cash_marked_investable_blocks(self) -> None:
        snapshot = build_example_private_portfolio_snapshot_v2()
        bad_bucket = replace(snapshot.cash_buckets[0], investable=True)
        bad_snapshot = replace(snapshot, cash_buckets=(bad_bucket,) + snapshot.cash_buckets[1:])

        result = audit_v6_2_private_portfolio_snapshot_v2(bad_snapshot)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("Protected cash cannot be investable" in blocker for blocker in result.blockers))

    def test_broker_or_execution_access_blocks(self) -> None:
        snapshot = build_example_private_portfolio_snapshot_v2()
        bad_snapshot = replace(
            snapshot,
            broker_api_connected=True,
            broker_execution_enabled=True,
        )

        result = audit_v6_2_private_portfolio_snapshot_v2(bad_snapshot)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("Broker/API connections are forbidden" in blocker for blocker in result.blockers))
        self.assertTrue(any("Broker execution is forbidden" in blocker for blocker in result.blockers))

    def test_safety_flags_forbid_policy_mutation_buy_requests_and_trades(self) -> None:
        result = audit_v6_2_private_portfolio_snapshot_v2()
        payload = result.to_dict()

        self.assertTrue(payload["local_private_data_only"])
        self.assertTrue(payload["operator_confirmation_required"])
        self.assertTrue(payload["automatic_import_forbidden_at_this_stage"])
        self.assertTrue(payload["broker_api_forbidden"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertFalse(payload["active_policy_mutated"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
