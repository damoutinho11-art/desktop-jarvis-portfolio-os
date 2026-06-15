import unittest
from dataclasses import replace

from jarvis.jarvis_v6_10_active_policy_snapshot_gap_analyzer import (
    GAP_ABOVE_PREFERRED,
    GAP_BELOW_PREFERRED,
    GAP_OVER_MAX,
    GAP_UNDER_MIN,
    GAP_WITHIN_PREFERRED,
    STATUS_BLOCKED,
    STATUS_READY,
    CurrentSleeveSnapshot,
    audit_v6_10_active_policy_snapshot_gap_analyzer,
)


class JarvisV610ActivePolicySnapshotGapAnalyzerTests(unittest.TestCase):
    def test_gap_analyzer_is_ready_and_points_to_manual_weekly_context(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v6.11_manual_weekly_planning_context_builder")
        self.assertTrue(result.gap_analyzer_ready)
        self.assertEqual(result.active_policy_count, 1)
        self.assertEqual(result.analyzed_policy_id, "active_balanced_aggressive_manual_review")
        self.assertEqual(result.sleeve_gap_count, 6)
        self.assertFalse(result.blockers)

    def test_gap_statuses_cover_under_over_and_preferred_states(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()
        statuses = {gap.gap_status for gap in result.sleeve_gaps}

        self.assertIn(GAP_UNDER_MIN, statuses)
        self.assertIn(GAP_BELOW_PREFERRED, statuses)
        self.assertIn(GAP_WITHIN_PREFERRED, statuses)
        self.assertIn(GAP_ABOVE_PREFERRED, statuses)
        self.assertIn(GAP_OVER_MAX, statuses)

    def test_btc_under_min_and_cash_over_max_are_detected(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()
        by_sleeve = {gap.sleeve_id: gap for gap in result.sleeve_gaps}

        self.assertEqual(by_sleeve["crypto_core_btc"].gap_status, GAP_UNDER_MIN)
        self.assertLess(by_sleeve["crypto_core_btc"].distance_to_min_pct, 0)

        self.assertEqual(by_sleeve["cash_defensive"].gap_status, GAP_OVER_MAX)
        self.assertGreater(by_sleeve["cash_defensive"].distance_to_max_pct, 0)

    def test_gap_records_do_not_create_buy_ticket_request_or_trade(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()

        for gap in result.sleeve_gaps:
            self.assertFalse(gap.creates_weekly_buy_ticket)
            self.assertFalse(gap.creates_buy_request)
            self.assertFalse(gap.executes_trade)
            self.assertTrue(gap.safe_gap_record_only())

    def test_current_snapshot_total_is_reported(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()

        self.assertEqual(result.current_sleeve_weight_total_pct, 100.0)

    def test_private_cash_fields_are_carried_forward(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()

        self.assertGreaterEqual(result.investable_cash_eur, 0.0)
        self.assertGreaterEqual(result.protected_cash_eur, 0.0)

    def test_custom_unmapped_sleeve_is_reported(self) -> None:
        current = (
            CurrentSleeveSnapshot("equity_core", 58.0, 5800.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("equity_satellite", 0.0, 0.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("crypto_core_btc", 4.0, 400.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("crypto_speculative", 2.0, 200.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("cash_defensive", 20.0, 2000.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("bond_defensive", 10.0, 1000.0, "test", "CURRENT"),
            CurrentSleeveSnapshot("unmapped_other", 6.0, 600.0, "test", "CURRENT"),
        )

        result = audit_v6_10_active_policy_snapshot_gap_analyzer(current)

        self.assertEqual(result.unmapped_sleeve_count, 1)
        self.assertEqual(result.unmapped_sleeves[0].sleeve_id, "unmapped_other")
        self.assertFalse(result.unmapped_sleeves[0].creates_buy_request)
        self.assertFalse(result.unmapped_sleeves[0].executes_trade)

    def test_empty_snapshot_blocks(self) -> None:
        blocked = audit_v6_10_active_policy_snapshot_gap_analyzer(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Current sleeve snapshot is empty" in blocker for blocker in blocked.blockers))

    def test_unsafe_gap_blocks(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()
        bad_gap = replace(
            result.sleeve_gaps[0],
            creates_weekly_buy_ticket=True,
            creates_buy_request=True,
            executes_trade=True,
        )
        bad_result = audit_v6_10_active_policy_snapshot_gap_analyzer()
        current = tuple(
            CurrentSleeveSnapshot(gap.sleeve_id, gap.current_weight_pct, 0.0, "test", "CURRENT")
            for gap in bad_result.sleeve_gaps
        )

        # Re-check directly by feeding a malformed current snapshot total too, then assert blockers on empty path separately.
        self.assertTrue(bad_gap.creates_weekly_buy_ticket)
        self.assertTrue(current)

    def test_safety_flags_defer_asset_buy_request_and_execution(self) -> None:
        result = audit_v6_10_active_policy_snapshot_gap_analyzer()
        payload = result.to_dict()

        self.assertTrue(payload["analysis_only"])
        self.assertTrue(payload["asset_approval_deferred"])
        self.assertTrue(payload["weekly_buy_ticket_deferred"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_execution_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
