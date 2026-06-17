from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v26_0_manual_buy_outcome_portfolio_state_recorder import (
    CONFIRMATION_PHRASE,
    STATUS_BLOCKED,
    STATUS_READY,
    build_manual_buy_outcome_portfolio_state_recorder_result,
    format_manual_buy_outcome_portfolio_state_recorder,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _ticket() -> dict:
    return {
        "ticket_id": "JARVIS-2026-06-04-daily-dual-lane-manual-approval",
        "as_of": "2026-06-04",
        "generated_at": "2026-06-17",
        "approval_status": "pending_manual_approval",
        "selected_crypto_candidate": "btc",
        "selected_crypto_amount_eur": 41.54,
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "buy_request_created": False,
        "trades_executed": False,
        "broker_connection_forbidden": True,
        "order_creation_forbidden": True,
    }


def _portfolio() -> dict:
    return {
        "as_of": "2026-06-04",
        "currency": "EUR",
        "holdings": {
            "btc": 20.0,
            "hype": 0.0,
            "tao": 0.0,
            "quality_etf": 0.0,
            "growth_nasdaq_etf": 0.0,
            "global_core_etf": 0.0,
            "discovery": 0.0,
            "tactical_reserve": 4.9,
        },
        "legacy_holdings": {},
        "platform_status": {"lhv_crypto_ready": True, "kraken_ready": False},
        "weekly_investment_budget": 103.85,
    }


class JarvisV260ManualBuyOutcomePortfolioStateRecorderTests(unittest.TestCase):
    def test_requires_explicit_manual_buy_confirmation_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="btc",
                lane="crypto",
                amount_eur=41.54,
                execution_date="2026-06-17",
                confirmation_phrase="",
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.portfolio_state_written)
            self.assertIn("confirmation phrase", " ".join(result.blockers))

    def test_records_confirmed_crypto_buy_into_local_portfolio_state_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="btc",
                lane="crypto",
                amount_eur=41.54,
                execution_date="2026-06-17",
                confirmation_phrase=CONFIRMATION_PHRASE,
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=True,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.portfolio_state_written)
            self.assertTrue(result.confirmation_logged)
            self.assertTrue(result.portfolio_state_mutation)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)

            updated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["as_of"], "2026-06-17")
            self.assertEqual(updated["holdings"]["btc"], 61.54)
            self.assertTrue(log_path.exists())

    def test_blocks_duplicate_manual_buy_confirmation_for_same_ticket_asset_amount_and_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                json.dumps(
                    {
                        "record_type": "manual_buy_confirmation",
                        "approval_ticket_id": "JARVIS-2026-06-04-daily-dual-lane-manual-approval",
                        "asset": "btc",
                        "lane": "crypto",
                        "amount_eur": 41.54,
                        "execution_date": "2026-06-17",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="btc",
                lane="crypto",
                amount_eur=41.54,
                execution_date="2026-06-17",
                confirmation_phrase=CONFIRMATION_PHRASE,
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.portfolio_state_written)
            self.assertIn("already recorded", " ".join(result.blockers))
            updated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["holdings"]["btc"], 20.0)


    def test_blocks_amount_that_does_not_match_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="btc",
                lane="crypto",
                amount_eur=10.0,
                execution_date="2026-06-17",
                confirmation_phrase=CONFIRMATION_PHRASE,
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.portfolio_state_written)
            self.assertIn("does not match approval ticket amount", " ".join(result.blockers))

    def test_blocks_asset_that_does_not_match_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="hype",
                lane="crypto",
                amount_eur=41.54,
                execution_date="2026-06-17",
                confirmation_phrase=CONFIRMATION_PHRASE,
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("does not match approval ticket asset", " ".join(result.blockers))

    def test_console_output_preserves_no_execution_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(ticket_path, _ticket())
            _write_json(state_path, _portfolio())

            result = build_manual_buy_outcome_portfolio_state_recorder_result(
                asset="btc",
                lane="crypto",
                amount_eur=41.54,
                execution_date="2026-06-17",
                confirmation_phrase=CONFIRMATION_PHRASE,
                approval_ticket_path=ticket_path,
                portfolio_state_path=state_path,
                confirmation_log_path=log_path,
                write_state=False,
            )
            output = format_manual_buy_outcome_portfolio_state_recorder(result)

            self.assertIn("Manual Buy Outcome Portfolio-State Recorder", output)
            self.assertIn("buy request created: False", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()