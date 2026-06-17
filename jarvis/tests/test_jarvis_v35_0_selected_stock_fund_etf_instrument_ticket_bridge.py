from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v35_0_selected_stock_fund_etf_instrument_ticket_bridge import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_selected_stock_fund_etf_instrument_ticket_bridge_result,
    format_selected_stock_fund_etf_instrument_ticket_bridge,
)


def _ticket() -> dict:
    return {
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "selected_crypto_candidate": "hype",
        "buy_request_created": False,
        "trades_executed": False,
    }


def _instrument(source_as_of: str = "2026-06-16") -> dict:
    return {
        "sleeve_id": "quality_etf",
        "instrument_id": "ishares_world_quality_is3q_de",
        "name": "iShares Edge MSCI World Quality Factor UCITS ETF USD (Acc)",
        "isin": "IE00BP3QZ601",
        "ticker": "IS3Q",
        "exchange": "XETRA",
        "currency": "EUR",
        "provider": "yahoo_chart",
        "symbol": "IS3Q.DE",
        "source_as_of": source_as_of,
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/IS3Q.DE?range=5d&interval=1d&includeAdjustedClose=true",
        "close_price": 75.900002,
        "expense_ratio": 0.25,
        "priority_score": 90.0,
        "public_source_status": "ETF_PUBLIC_SOURCE_READY",
        "decision_status": "SELECTED_REAL_INSTRUMENT_FOR_SLEEVE",
        "selected": True,
    }


def _resolution(source_as_of: str = "2026-06-16") -> dict:
    return {
        "version": 1,
        "current_date": "2026-06-17",
        "selected_sleeve": "quality_etf",
        "selected_sleeve_amount_eur": 62.31,
        "selected_instrument": _instrument(source_as_of),
        "instrument_decisions": [_instrument(source_as_of)],
    }


def _write_ticket(root: Path) -> Path:
    path = root / "outputs" / "approval_ticket_latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_ticket()), encoding="utf-8")
    return path


def _write_resolution(root: Path, source_as_of: str = "2026-06-16") -> Path:
    path = root / "jarvis" / "local" / "stock_fund_etf_selected_instrument.local.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_resolution(source_as_of)), encoding="utf-8")
    return path


class JarvisV350SelectedStockFundEtfInstrumentTicketBridgeTests(unittest.TestCase):
    def test_missing_resolution_reviews_without_writing_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=True,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.resolution_loaded)
            self.assertFalse(result.ticket_written)
            self.assertFalse(result.approval_ticket_now_has_real_instrument)

    def test_fresh_resolution_reviews_until_write_ticket_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_resolution(root)

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.selected_instrument_public_source_ready)
            self.assertFalse(result.ticket_written)
            self.assertFalse(result.approval_ticket_now_has_real_instrument)

    def test_write_ticket_adds_real_instrument_without_changing_sleeve_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = _write_ticket(root)
            _write_resolution(root)

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=True,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.ticket_written)
            self.assertTrue(result.approval_ticket_now_has_real_instrument)
            updated = json.loads(ticket_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["selected_stock_fund_etf_candidate"], "quality_etf")
            self.assertEqual(updated["selected_stock_fund_etf_sleeve"], "quality_etf")
            self.assertEqual(updated["selected_stock_fund_etf_real_instrument"]["instrument_id"], "ishares_world_quality_is3q_de")
            self.assertEqual(updated["selected_stock_fund_etf_real_instrument_symbol"], "IS3Q.DE")
            self.assertEqual(updated["stock_fund_etf_source_metadata"]["metadata_status"], "ETF_SOURCE_METADATA_READY")
            self.assertFalse(updated["buy_request_created"])
            self.assertFalse(updated["trades_executed"])

    def test_stale_resolution_does_not_write_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_resolution(root, source_as_of="2026-05-01")

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=True,
                max_age_days=7,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.ticket_written)
            self.assertFalse(result.selected_instrument_public_source_ready)

    def test_existing_ticket_with_same_real_instrument_can_be_ready_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = _write_ticket(root)
            _write_resolution(root)
            build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=True,
            )

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=False,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertFalse(result.ticket_written)
            self.assertTrue(result.approval_ticket_now_has_real_instrument)
            self.assertEqual(json.loads(ticket_path.read_text(encoding="utf-8"))["selected_stock_fund_etf_candidate"], "quality_etf")

    def test_console_mentions_real_instrument_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_resolution(root)

            result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_ticket=True,
            )
            output = format_selected_stock_fund_etf_instrument_ticket_bridge(result)

            self.assertIn("Selected Stock/Fund/ETF Instrument Ticket Bridge", output)
            self.assertIn("selected real instrument symbol: IS3Q.DE", output)
            self.assertIn("approval ticket now has real instrument: True", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()