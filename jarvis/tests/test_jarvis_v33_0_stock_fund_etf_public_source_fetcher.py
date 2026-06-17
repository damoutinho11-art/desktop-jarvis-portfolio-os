from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v33_0_stock_fund_etf_public_source_fetcher import (
    SOURCE_MISSING,
    SOURCE_READY,
    SOURCE_STALE,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_stock_fund_etf_public_source_fetcher_result,
    format_stock_fund_etf_public_source_fetcher,
)


def _ticket() -> dict:
    return {
        "as_of": "2026-06-04",
        "allocation_basis_as_of": "2026-06-04",
        "generated_at": "2026-06-17",
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "buy_request_created": False,
        "trades_executed": False,
        "etf_scoring_verdict": {
            "selected_ideal_etf": "quality_etf",
            "sleeves": [
                {"candidate_id": "quality_etf", "score": 83.0},
                {"candidate_id": "growth_nasdaq_etf", "score": 79.0},
            ],
        },
    }


def _upstream(status: str = "JARVIS_V32_0_STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        selected_stock_fund_etf_candidate="quality_etf",
        selected_candidate_metadata_status="ETF_SOURCE_METADATA_READY",
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": status},
    )


def _write_ticket(root: Path) -> None:
    path = root / "outputs" / "approval_ticket_latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_ticket()), encoding="utf-8")


def _write_manifest(root: Path, provider: str = "yahoo_chart") -> None:
    path = root / "jarvis" / "local" / "stock_fund_etf_public_sources.local.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "sources": {
                    "quality_etf": {
                        "provider": provider,
                        "symbol": "QUALITY.TEST",
                        "currency": "EUR",
                    },
                    "growth_nasdaq_etf": {
                        "provider": provider,
                        "symbol": "GROWTH.TEST",
                        "currency": "EUR",
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _yahoo_payload(date_epoch: int = 1781654400, close: float = 101.25) -> str:
    return json.dumps(
        {
            "chart": {
                "result": [
                    {
                        "meta": {"currency": "EUR"},
                        "timestamp": [date_epoch],
                        "indicators": {"quote": [{"close": [close]}]},
                    }
                ],
                "error": None,
            }
        }
    )


def _stooq_payload(date_text: str = "2026-06-17", close: float = 101.25) -> str:
    return f"Symbol,Date,Time,Open,High,Low,Close,Volume\nQUALITY.TEST,{date_text},22:00:00,100,102,99,{close},12345\n"


class JarvisV330StockFundEtfPublicSourceFetcherTests(unittest.TestCase):
    def test_missing_manifest_reviews_without_fetching_or_inventing_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            fetch_calls: list[str] = []

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: fetch_calls.append(url) or _yahoo_payload(),
                upstream_freshness_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.source_manifest_loaded)
            self.assertEqual(result.network_fetch_attempted_count, 0)
            self.assertEqual(fetch_calls, [])
            self.assertEqual(result.selected_candidate_source_status, SOURCE_MISSING)

    def test_fetches_fresh_yahoo_chart_source_when_manifest_has_real_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_manifest(root, provider="yahoo_chart")

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _yahoo_payload(),
                upstream_freshness_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.selected_candidate_source_status, SOURCE_READY)
            self.assertEqual(result.source_ready_count, 2)
            self.assertEqual(result.network_fetch_attempted_count, 2)
            self.assertTrue(result.all_selected_sources_fresh)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_fetches_fresh_stooq_csv_source_when_manifest_uses_stooq(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_manifest(root, provider="stooq_csv")

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                upstream_freshness_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.selected_candidate_source_status, SOURCE_READY)
            self.assertEqual(result.source_ready_count, 2)

    def test_stale_fetched_source_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_manifest(root, provider="stooq_csv")

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(date_text="2026-06-01"),
                upstream_freshness_result=_upstream(),
                max_age_days=7,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.selected_candidate_source_status, SOURCE_STALE)
            self.assertEqual(result.source_stale_count, 2)

    def test_write_local_manifest_template_does_not_mark_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                write_local_manifest_template=True,
                upstream_freshness_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.source_manifest_template_written)
            self.assertEqual(result.network_fetch_attempted_count, 0)
            self.assertEqual(result.selected_candidate_source_status, SOURCE_MISSING)
            self.assertTrue((root / "jarvis" / "local" / "stock_fund_etf_public_sources.local.json").exists())

    def test_writes_local_signals_only_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_manifest(root, provider="yahoo_chart")

            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                write_local_signals=True,
                fetch_text=lambda url: _yahoo_payload(),
                upstream_freshness_result=_upstream(),
            )

            self.assertTrue(result.public_signals_written)
            signals = root / "jarvis" / "local" / "stock_fund_etf_public_signals.local.json"
            self.assertTrue(signals.exists())
            self.assertEqual(json.loads(signals.read_text(encoding="utf-8"))["signals"][0]["source_status"], SOURCE_READY)

    def test_console_mentions_public_sources_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root)
            _write_manifest(root, provider="yahoo_chart")
            result = build_stock_fund_etf_public_source_fetcher_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _yahoo_payload(),
                upstream_freshness_result=_upstream(),
            )

            output = format_stock_fund_etf_public_source_fetcher(result)

            self.assertIn("Stock/Fund/ETF Public Source Fetcher", output)
            self.assertIn("selected candidate source status: ETF_PUBLIC_SOURCE_READY", output)
            self.assertIn("network fetch attempted count: 2", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()