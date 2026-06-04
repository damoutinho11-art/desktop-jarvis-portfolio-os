import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from jarvis.manual_snapshot_loader import ManualSnapshotError, load_manual_snapshot
from jarvis.portfolio_snapshot_engine import load_account_roles


def _write_snapshot(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _valid_payload() -> dict:
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
                "cash_eur": 200.0,
                "holdings": [],
            },
            {
                "account_id": "lhv_growth",
                "platform": "LHV",
                "role": "legacy_cleanup",
                "cash_eur": 0.0,
                "holdings": [
                    {
                        "asset_symbol": "lhv_growth_sxr8",
                        "asset_class": "legacy_etf",
                        "market_value_eur": 150.0,
                        "classification": "legacy_existing",
                    }
                ],
            },
        ],
    }


class ManualSnapshotLoaderTests(unittest.TestCase):
    def test_valid_snapshot_loads_into_schema(self) -> None:
        snapshot, warnings = load_manual_snapshot(_write_snapshot(_valid_payload()), today=date(2026, 6, 4))

        self.assertEqual(snapshot.as_of, "2026-06-04")
        self.assertEqual(len(snapshot.accounts), 3)
        self.assertEqual(len(snapshot.holdings), 3)
        self.assertEqual(warnings, [])

    def test_invalid_role_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["accounts"][0]["role"] = "broker_execution"

        with self.assertRaisesRegex(ManualSnapshotError, "role broker_execution is not known"):
            load_manual_snapshot(_write_snapshot(payload))

    def test_negative_cash_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["accounts"][0]["cash_eur"] = -1.0

        with self.assertRaisesRegex(ManualSnapshotError, "cash_eur must be non-negative"):
            load_manual_snapshot(_write_snapshot(payload))

    def test_top_level_holding_with_unknown_account_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["holdings"] = [
            {
                "account_id": "missing_account",
                "asset_symbol": "BTC",
                "asset_class": "crypto",
                "market_value_eur": 10.0,
            }
        ]

        with self.assertRaisesRegex(ManualSnapshotError, "unknown account_id missing_account"):
            load_manual_snapshot(_write_snapshot(payload))

    def test_stale_snapshot_adds_warning(self) -> None:
        payload = _valid_payload()
        payload["snapshot_date"] = "2026-05-20"

        _, warnings = load_manual_snapshot(_write_snapshot(payload), today=date(2026, 6, 4))

        self.assertEqual(warnings[0].code, "stale_snapshot")

    def test_roles_are_loaded_from_account_roles_config(self) -> None:
        roles = load_account_roles()

        self.assertEqual(roles["lhv_growth"]["role"], "legacy_cleanup")
        self.assertEqual(roles["lhv_crypto_investments"]["role"], "investment_account_crypto")


if __name__ == "__main__":
    unittest.main()
