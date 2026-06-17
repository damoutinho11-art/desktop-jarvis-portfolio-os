from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v26_0_manual_buy_outcome_portfolio_state_recorder import CONFIRMATION_PHRASE
from jarvis.jarvis_v26_0_manual_buy_outcome_portfolio_state_recorder_report import main


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class JarvisV260ManualBuyOutcomePortfolioStateRecorderReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_broker_or_trade_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            state_path = root / "portfolio_state.json"
            log_path = root / "outputs" / "manual_buy_confirmations.jsonl"
            _write_json(
                ticket_path,
                {
                    "ticket_id": "JARVIS-2026-06-04-daily-dual-lane-manual-approval",
                    "selected_crypto_candidate": "btc",
                    "selected_crypto_amount_eur": 41.54,
                    "buy_request_created": False,
                    "trades_executed": False,
                    "broker_connection_forbidden": True,
                    "order_creation_forbidden": True,
                },
            )
            _write_json(
                state_path,
                {
                    "as_of": "2026-06-04",
                    "currency": "EUR",
                    "holdings": {"btc": 20.0},
                },
            )

            exit_code = main(
                [
                    "--asset",
                    "btc",
                    "--lane",
                    "crypto",
                    "--amount-eur",
                    "41.54",
                    "--execution-date",
                    "2026-06-17",
                    "--confirmation-phrase",
                    CONFIRMATION_PHRASE,
                    "--approval-ticket-path",
                    str(ticket_path),
                    "--portfolio-state-path",
                    str(state_path),
                    "--confirmation-log-path",
                    str(log_path),
                ]
            )

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()