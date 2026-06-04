import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from jarvis.manual_snapshot_loader import load_manual_snapshot
from jarvis.portfolio_snapshot_engine import load_account_roles, load_constitution, validate_snapshot
from jarvis.snapshot_audit import build_snapshot_audit_report


def _write_snapshot(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _payload_with_asset(asset_symbol: str, classification: str | None = None) -> dict:
    holding = {
        "asset_symbol": asset_symbol,
        "asset_class": "etf",
        "market_value_eur": 50.0,
    }
    if classification:
        holding["classification"] = classification
    return {
        "snapshot_date": "2026-06-04",
        "base_currency": "EUR",
        "accounts": [
            {
                "account_id": "emergency_fund",
                "platform": "bank",
                "role": "protected_cash",
                "cash_eur": 3000.0,
                "holdings": [],
            },
            {
                "account_id": "daily_spending",
                "platform": "bank",
                "role": "daily_spending",
                "cash_eur": 250.0,
                "holdings": [],
            },
            {
                "account_id": "lightyear",
                "platform": "Lightyear",
                "role": "ETF_engine",
                "cash_eur": 100.0,
                "holdings": [holding],
            },
        ],
    }


class SnapshotAuditTests(unittest.TestCase):
    def _result_for_payload(self, payload: dict):
        snapshot, intake_warnings = load_manual_snapshot(_write_snapshot(payload), today=date(2026, 6, 4))
        result = validate_snapshot(snapshot, load_constitution(), load_account_roles())
        return result, intake_warnings

    def test_protected_emergency_and_daily_cash_are_reported_non_investable(self) -> None:
        result, warnings = self._result_for_payload(_payload_with_asset("quality_etf"))
        report = build_snapshot_audit_report(result, warnings)

        self.assertIn("status: valid", report)
        self.assertIn("total cash: EUR 3350.00", report)
        self.assertIn("protected cash: EUR 3250.00", report)
        self.assertIn("investable cash: EUR 0.00", report)
        self.assertIn("recommendations blocked: no", report)

    def test_unknown_asset_is_candidate_unapproved_and_blocks_recommendations(self) -> None:
        result, warnings = self._result_for_payload(_payload_with_asset("MYSTERY_ASSET"))
        report = build_snapshot_audit_report(result, warnings)

        self.assertFalse(result.validation_passed)
        self.assertIn("candidate_unapproved", report)
        self.assertIn("unapproved assets: EUR 50.00", report)
        self.assertIn("recommendations blocked: yes", report)

    def test_legacy_existing_unknown_asset_is_not_candidate_unapproved(self) -> None:
        result, warnings = self._result_for_payload(_payload_with_asset("OLD_LEGACY_ETF", "legacy_existing"))
        report = build_snapshot_audit_report(result, warnings)

        self.assertTrue(result.validation_passed)
        self.assertNotIn("candidate_unapproved", report)
        self.assertIn("legacy holdings: EUR 50.00", report)

    def test_test_position_unknown_asset_is_warned_without_candidate_label(self) -> None:
        result, warnings = self._result_for_payload(_payload_with_asset("SANDBOX_ASSET", "test_position"))
        report = build_snapshot_audit_report(result, warnings)

        self.assertTrue(result.validation_passed)
        self.assertIn("test_position", report)
        self.assertNotIn("candidate_unapproved", report)


if __name__ == "__main__":
    unittest.main()
