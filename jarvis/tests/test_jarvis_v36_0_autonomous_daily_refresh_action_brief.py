from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v36_0_autonomous_daily_refresh_action_brief import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_autonomous_daily_refresh_action_brief_result,
    format_autonomous_daily_refresh_action_brief,
)


def _ticket() -> dict:
    return {
        "selected_crypto_candidate": "hype",
        "selected_crypto_amount_eur": 41.54,
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "buy_request_created": False,
        "trades_executed": False,
    }


def _write_ticket(root: Path) -> None:
    path = root / "outputs" / "approval_ticket_latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_ticket()), encoding="utf-8")


def _write_universe(root: Path, *, provider: str = "stooq_csv", symbol: str = "quality.test") -> None:
    path = root / "jarvis" / "local" / "stock_fund_etf_instrument_universe.local.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "sleeves": {
                    "quality_etf": {
                        "sleeve_id": "quality_etf",
                        "instruments": [
                            {
                                "instrument_id": "ishares_world_quality_is3q_de",
                                "name": "iShares Edge MSCI World Quality Factor UCITS ETF USD (Acc)",
                                "isin": "IE00BP3QZ601",
                                "ticker": "IS3Q",
                                "exchange": "XETRA",
                                "currency": "EUR",
                                "provider": provider,
                                "symbol": symbol,
                                "expense_ratio": 0.25,
                                "priority_score": 90.0,
                            }
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )


def _stooq_payload(date_text: str = "2026-06-17", close: float = 75.90) -> str:
    return f"Symbol,Date,Time,Open,High,Low,Close,Volume\nQUALITY.TEST,{date_text},22:00:00,75,76,74,{close},12345\n"


class JarvisV360AutonomousDailyRefreshActionBriefTests(unittest.TestCase):
    def test_autonomous_daily_refresh_writes_resolution_ticket_and_clean_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_autonomous_daily_refresh_action_brief_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.local_resolution_written)
            self.assertTrue(result.approval_ticket_written)
            self.assertEqual(result.crypto_candidate, "hype")
            self.assertEqual(result.crypto_amount_eur, 41.54)
            self.assertEqual(result.stock_fund_etf_sleeve, "quality_etf")
            self.assertEqual(result.real_instrument_symbol, "quality.test")
            self.assertEqual(result.real_instrument_isin, "IE00BP3QZ601")
            self.assertTrue(result.real_instrument_public_source_ready)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_no_write_flags_review_but_do_not_mutate_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_autonomous_daily_refresh_action_brief_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                write_local_resolution=True,
                write_ticket=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.local_resolution_written)
            self.assertFalse(result.approval_ticket_written)
            self.assertIsNone(result.real_instrument_symbol)

    def test_missing_instrument_universe_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)

            result = build_autonomous_daily_refresh_action_brief_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.real_instrument_public_source_ready)
            self.assertFalse(result.approval_ticket_written)

    def test_stale_quote_requires_review_and_no_ticket_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_autonomous_daily_refresh_action_brief_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(date_text="2026-05-01"),
                max_age_days=7,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.approval_ticket_written)
            self.assertFalse(result.real_instrument_public_source_ready)

    def test_console_mentions_clean_crypto_etf_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_autonomous_daily_refresh_action_brief_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
            )
            output = format_autonomous_daily_refresh_action_brief(result)

            self.assertIn("Autonomous Daily Refresh Action Brief", output)
            self.assertIn("Crypto lane:", output)
            self.assertIn("Candidate: hype", output)
            self.assertIn("Stock/Fund/ETF lane:", output)
            self.assertIn("IE00BP3QZ601", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()