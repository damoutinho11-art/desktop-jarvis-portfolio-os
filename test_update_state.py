"""Tests for safe portfolio state updates."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

import update_state


SAMPLE_STATE = {
    "currency": "EUR",
    "as_of": "2026-06-04",
    "monthly_investment_budget": 450.0,
    "weekly_investment_budget": 103.85,
    "holdings": {
        "global_core_etf": 0.0,
        "growth_nasdaq_etf": 0.0,
        "quality_etf": 0.0,
        "btc": 20.0,
        "hype": 0.0,
        "tao": 0.0,
        "discovery": 0.0,
        "tactical_reserve": 4.9,
    },
    "platform_status": {
        "lightyear_ready": False,
        "lhv_crypto_ready": True,
        "kraken_ready": False,
        "trade_republic_ready": True,
    },
    "legacy_holdings": {
        "lhv_growth_sxr8": 635.83,
        "lhv_growth_iemm": 372.24,
        "lhv_growth_xcha": 127.93,
        "lhv_growth_cash_pending_settlement": 1271.57,
    },
}


class UpdateStateTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def read_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def test_backup_is_created_and_holdings_update(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "portfolio_state.json"
            self.write_json(state_path, SAMPLE_STATE)

            _before, after, backup_path = update_state.update_state_file(
                state_path, holdings=["btc=61.54"]
            )

            self.assertTrue(backup_path.exists())
            self.assertEqual(after["holdings"]["btc"], 61.54)
            self.assertEqual(self.read_json(state_path)["holdings"]["btc"], 61.54)
            self.assertEqual(self.read_json(backup_path)["holdings"]["btc"], 20.0)

    def test_legacy_null_works(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "portfolio_state.json"
            self.write_json(state_path, SAMPLE_STATE)

            _before, after, _backup_path = update_state.update_state_file(
                state_path,
                legacy=["lhv_growth_cash_pending_settlement=null"],
            )

            self.assertIsNone(
                after["legacy_holdings"]["lhv_growth_cash_pending_settlement"]
            )

    def test_platform_status_updates(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "portfolio_state.json"
            self.write_json(state_path, SAMPLE_STATE)

            _before, after, _backup_path = update_state.update_state_file(
                state_path, platforms=["lightyear_ready=true"]
            )

            self.assertTrue(after["platform_status"]["lightyear_ready"])

    def test_invalid_keys_are_rejected(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "portfolio_state.json"
            self.write_json(state_path, SAMPLE_STATE)

            with self.assertRaises(ValueError):
                update_state.update_state_file(state_path, holdings=["bad_asset=1"])
            with self.assertRaises(ValueError):
                update_state.update_state_file(state_path, legacy=["bad_legacy=1"])
            with self.assertRaises(ValueError):
                update_state.update_state_file(state_path, platforms=["bad_ready=true"])

    def test_constitution_is_never_modified(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = root / "portfolio_state.json"
            constitution_path = root / "jarvis_constitution.json"
            self.write_json(state_path, SAMPLE_STATE)
            self.write_json(constitution_path, {"sentinel": "unchanged"})

            update_state.update_state_file(
                state_path,
                weekly_budget=200.0,
                monthly_budget=800.0,
                holdings=["btc=61.54"],
            )

            self.assertEqual(self.read_json(constitution_path), {"sentinel": "unchanged"})


if __name__ == "__main__":
    unittest.main()
