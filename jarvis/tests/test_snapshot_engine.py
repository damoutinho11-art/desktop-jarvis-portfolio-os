import json
import tempfile
import unittest
from pathlib import Path

from jarvis.decision_logger import append_decision_record
from jarvis.portfolio_schema import Account, Holding, PortfolioSnapshot, Recommendation
from jarvis.portfolio_snapshot_engine import (
    block_recommendation_until_validated,
    load_account_roles,
    load_constitution,
    validate_snapshot,
)


class SnapshotEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.constitution = load_constitution()
        self.roles = load_account_roles()

    def test_emergency_and_daily_spending_cash_are_protected(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            emergency_fund_amount=3000.0,
            accounts=[
                Account("emergency_fund", "Emergency Fund"),
                Account("daily_spending", "Daily Spending"),
            ],
            holdings=[
                Holding("daily_spending", "EUR", 500.0, "cash"),
            ],
        )

        result = validate_snapshot(snapshot, self.constitution, self.roles)
        self.assertTrue(result.validation_passed)
        self.assertEqual(result.snapshot.classified_totals["protected_cash"], 3500.0)
        self.assertEqual(result.snapshot.classified_totals["investable_cash"], 0.0)

    def test_lhv_crypto_is_investment_account_crypto(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            accounts=[Account("lhv_crypto_investments", "LHV Crypto Investments")],
            holdings=[Holding("lhv_crypto_investments", "BTC", 100.0, "crypto")],
        )

        result = validate_snapshot(snapshot, self.constitution, self.roles)
        self.assertTrue(result.validation_passed)
        self.assertEqual(result.snapshot.classified_totals["investment_account_crypto"], 100.0)

    def test_lhv_growth_is_legacy_cleanup(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            accounts=[Account("lhv_growth", "LHV Growth Account")],
            holdings=[Holding("lhv_growth", "lhv_growth_sxr8", 200.0, "legacy_etf")],
        )

        result = validate_snapshot(snapshot, self.constitution, self.roles)
        self.assertTrue(result.validation_passed)
        self.assertEqual(result.snapshot.classified_totals["legacy_holdings"], 200.0)

    def test_unknown_asset_is_candidate_unapproved_and_invalidates_snapshot(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            accounts=[Account("lightyear", "Lightyear")],
            holdings=[Holding("lightyear", "MYSTERY", 50.0, "etf")],
        )

        result = validate_snapshot(snapshot, self.constitution, self.roles)
        self.assertFalse(result.validation_passed)
        self.assertEqual(result.warnings[0].code, "candidate_unapproved")
        self.assertEqual(result.snapshot.classified_totals["unapproved_assets"], 50.0)

    def test_recommendation_is_blocked_until_snapshot_validation_passes(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            accounts=[Account("lightyear", "Lightyear")],
            holdings=[Holding("lightyear", "UNKNOWN", 50.0, "etf")],
        )
        result = validate_snapshot(snapshot, self.constitution, self.roles)
        recommendation = Recommendation("buy", "quality_etf", 100.0, "lightyear")

        blocked = block_recommendation_until_validated(result, recommendation)
        self.assertEqual(blocked.status, "blocked")
        self.assertTrue(blocked.manual_approval_required)

    def test_valid_snapshot_recommendation_still_requires_manual_approval(self) -> None:
        snapshot = PortfolioSnapshot(
            as_of="2026-06-04",
            accounts=[Account("lightyear", "Lightyear")],
            holdings=[Holding("lightyear", "quality_etf", 100.0, "etf")],
        )
        result = validate_snapshot(snapshot, self.constitution, self.roles)
        recommendation = Recommendation("buy", "quality_etf", 100.0, "lightyear")

        pending = block_recommendation_until_validated(result, recommendation)
        self.assertEqual(pending.status, "pending_manual_approval")
        self.assertTrue(pending.manual_approval_required)

    def test_decision_logger_appends_jsonl_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "decision_log.jsonl"
            append_decision_record(
                {
                    "as_of": "2026-06-04",
                    "recommendation_status": "pending_manual_approval",
                    "trades_executed": False,
                },
                log_path,
            )

            lines = log_path.read_text(encoding="utf-8").splitlines()
            payload = json.loads(lines[0])
            self.assertEqual(len(lines), 1)
            self.assertEqual(payload["recommendation_status"], "pending_manual_approval")
            self.assertFalse(payload["trades_executed"])


if __name__ == "__main__":
    unittest.main()
