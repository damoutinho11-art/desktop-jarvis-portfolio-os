from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v33_0_stock_fund_etf_public_source_fetcher import SOURCE_READY
from jarvis.jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver import (
    INSTRUMENT_MISSING_SOURCE,
    INSTRUMENT_SELECTED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_stock_fund_etf_sleeve_to_instrument_resolver_result,
    format_stock_fund_etf_sleeve_to_instrument_resolver,
)


def _ticket() -> dict:
    return {
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "etf_scoring_verdict": {
            "selected_ideal_etf": "quality_etf",
            "sleeves": [
                {"candidate_id": "quality_etf", "score": 83.0},
                {"candidate_id": "growth_nasdaq_etf", "score": 79.0},
                {"candidate_id": "global_core_etf", "score": 50.0},
            ],
        },
        "buy_request_created": False,
        "trades_executed": False,
    }


def _write_ticket(root: Path) -> None:
    path = root / "outputs" / "approval_ticket_latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_ticket()), encoding="utf-8")


def _write_universe(root: Path, *, blank: bool = False) -> None:
    path = root / "jarvis" / "local" / "stock_fund_etf_instrument_universe.local.json"
    path.parent.mkdir(parents=True)
    provider = "" if blank else "stooq_csv"
    symbol = "" if blank else "quality.test"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "sleeves": {
                    "quality_etf": {
                        "sleeve_id": "quality_etf",
                        "instruments": [
                            {
                                "instrument_id": "quality_real_etf",
                                "name": "Quality Real ETF",
                                "isin": "IE00TESTQUALITY",
                                "ticker": "QUALITY",
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


def _stooq_payload(date_text: str = "2026-06-17", close: float = 101.25) -> str:
    return f"Symbol,Date,Time,Open,High,Low,Close,Volume\nQUALITY.TEST,{date_text},22:00:00,100,102,99,{close},12345\n"


def _upstream(status: str = "JARVIS_V33_0_STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        selected_stock_fund_etf_candidate="quality_etf",
        selected_candidate_source_status=SOURCE_READY,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": status},
    )


class JarvisV340StockFundEtfSleeveToInstrumentResolverTests(unittest.TestCase):
    def test_missing_universe_reviews_without_inventing_instrument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                upstream_public_source_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.instrument_universe_loaded)
            self.assertEqual(result.selected_sleeve, "quality_etf")
            self.assertIsNone(result.selected_instrument_id)
            self.assertEqual(result.network_fetch_attempted_count, 0)

    def test_template_write_does_not_select_blank_instrument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                write_local_instrument_template=True,
                upstream_public_source_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.instrument_universe_template_written)
            self.assertIsNone(result.selected_instrument_id)
            self.assertTrue((root / "jarvis" / "local" / "stock_fund_etf_instrument_universe.local.json").exists())

    def test_blank_instrument_source_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root, blank=True)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                upstream_public_source_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.instrument_decisions[0].decision_status, INSTRUMENT_MISSING_SOURCE)
            self.assertIsNone(result.selected_instrument_id)

    def test_selects_real_instrument_only_with_fresh_public_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                upstream_public_source_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.selected_instrument_id, "quality_real_etf")
            self.assertEqual(result.selected_instrument_isin, "IE00TESTQUALITY")
            self.assertEqual(result.selected_instrument_ticker, "QUALITY")
            self.assertEqual(result.selected_instrument_symbol, "quality.test")
            self.assertTrue(result.selected_instrument_public_source_ready)
            self.assertEqual(result.instrument_decisions[0].decision_status, INSTRUMENT_SELECTED)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_stale_public_source_does_not_select_instrument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(date_text="2026-06-01"),
                upstream_public_source_result=_upstream(),
                max_age_days=7,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertIsNone(result.selected_instrument_id)
            self.assertFalse(result.selected_instrument_public_source_ready)

    def test_writes_local_resolution_only_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)

            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                write_local_resolution=True,
                upstream_public_source_result=_upstream(),
            )

            self.assertTrue(result.instrument_resolution_written)
            path = root / "jarvis" / "local" / "stock_fund_etf_selected_instrument.local.json"
            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_instrument"]["instrument_id"], "quality_real_etf")
            self.assertFalse(payload["safety"]["buy_request_created"])
            self.assertFalse(payload["safety"]["trades_executed"])

    def test_console_mentions_sleeve_instrument_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_universe(root)
            result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                upstream_public_source_result=_upstream(),
            )

            output = format_stock_fund_etf_sleeve_to_instrument_resolver(result)

            self.assertIn("Sleeve-to-Instrument Resolver", output)
            self.assertIn("selected sleeve: quality_etf", output)
            self.assertIn("selected instrument id: quality_real_etf", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()