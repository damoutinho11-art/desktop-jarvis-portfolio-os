from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v38_0_individual_stock_public_universe_engine import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    STOCK_MISSING_SOURCE,
    STOCK_READY,
    build_individual_stock_public_universe_engine_result,
    format_individual_stock_public_universe_engine,
)


def _upstream_ready() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V37_0_AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_READY_SAFE",
        daily_status="AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_READY",
        blockers=(),
        warnings=(),
        approval_ticket_mutation=True,
        buy_request_created=False,
        no_trades_executed=True,
        to_dict=lambda: {"status": "ready"},
    )


def _write_universe(root: Path, *, blank: bool = False) -> None:
    path = root / "jarvis" / "local" / "individual_stock_public_universe.local.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "stocks": [
                    {
                        "stock_id": "sample_stock",
                        "name": "Sample Stock Inc.",
                        "ticker": "" if blank else "SAMPLE",
                        "exchange": "NASDAQ",
                        "market": "USA",
                        "sector": "Technology",
                        "currency": "USD",
                        "provider": "" if blank else "stooq_csv",
                        "symbol": "" if blank else "sample.us",
                        "priority_score": 75.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _stooq_payload(date_text: str = "2026-06-17", close: float = 123.45) -> str:
    return f"Symbol,Date,Time,Open,High,Low,Close,Volume\nSAMPLE.US,{date_text},22:00:00,120,124,119,{close},12345\n"


class JarvisV380IndividualStockPublicUniverseEngineTests(unittest.TestCase):
    def test_missing_stock_universe_reviews_but_keeps_dual_lane_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=Path(tmp),
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.stock_universe_loaded)
            self.assertEqual(result.stock_count, 0)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)

    def test_template_write_creates_blank_universe_that_does_not_count_as_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                write_stock_template=True,
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertTrue(result.stock_universe_template_written)
            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue((root / "jarvis" / "local" / "individual_stock_public_universe.local.json").exists())

    def test_blank_stock_source_reviews_without_network_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_universe(root, blank=True)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.network_fetch_attempted_count, 0)
            self.assertEqual(result.stock_signals[0].source_status, STOCK_MISSING_SOURCE)
            self.assertIn("individual stock provider and symbol", result.stock_signals[0].warnings[0])

    def test_real_stock_public_quote_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_universe(root)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.ready_stock_count, 1)
            self.assertEqual(result.network_fetch_attempted_count, 1)
            self.assertEqual(result.stock_signals[0].source_status, STOCK_READY)
            self.assertEqual(result.stock_signals[0].close_price, 123.45)

    def test_stale_stock_public_quote_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_universe(root)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(date_text="2026-05-01"),
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.ready_stock_count, 0)
            self.assertEqual(result.stale_or_failed_stock_count, 1)

    def test_write_stock_signals_under_jarvis_local_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_universe(root)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                write_stock_signals=True,
                upstream_dual_lane_result=_upstream_ready(),
            )

            self.assertTrue(result.stock_signals_written)
            path = root / "jarvis" / "local" / "individual_stock_public_signals.local.json"
            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["ready_stock_count"], 1)
            self.assertFalse(payload["safety"]["buy_request_created"])
            self.assertFalse(payload["safety"]["trades_executed"])

    def test_console_mentions_stock_engine_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_universe(root)
            result = build_individual_stock_public_universe_engine_result(
                current_date="2026-06-17",
                root=root,
                fetch_text=lambda url: _stooq_payload(),
                upstream_dual_lane_result=_upstream_ready(),
            )
            output = format_individual_stock_public_universe_engine(result)

            self.assertIn("Individual Stock Public Universe Engine", output)
            self.assertIn("sample_stock", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()