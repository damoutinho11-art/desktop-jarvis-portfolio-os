from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v38_0_individual_stock_public_universe_engine import STOCK_MISSING_SOURCE, STOCK_READY
from jarvis.jarvis_v39_0_individual_stock_public_ranker import (
    DECISION_STATUS_NOT_APPROVED,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_individual_stock_public_ranker_result,
    format_individual_stock_public_ranker,
)


def _signal(
    stock_id: str,
    *,
    status: str = STOCK_READY,
    close_price: float | None = 100.0,
    priority_score: float = 50.0,
    source_as_of: str = "2026-06-17",
    symbol: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        stock_id=stock_id,
        name=f"{stock_id} Corp",
        ticker=stock_id.upper(),
        exchange="NASDAQ",
        market="USA",
        sector="Technology",
        provider="stooq_csv",
        symbol=symbol or f"{stock_id.lower()}.us",
        currency="USD",
        source_url=f"https://stooq.com/q/l/?s={stock_id.lower()}.us&f=sd2t2ohlcv&h&e=csv",
        source_as_of=source_as_of,
        close_price=close_price,
        priority_score=priority_score,
        source_status=status,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"stock_id": stock_id},
    )


def _upstream(*signals: SimpleNamespace, status: str = "JARVIS_V38_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        stock_universe_path="jarvis/local/individual_stock_public_universe.local.json",
        stock_signals_path="jarvis/local/individual_stock_public_signals.local.json",
        stock_count=len(signals),
        ready_stock_count=sum(1 for signal in signals if signal.source_status == STOCK_READY),
        stock_signals=signals,
        blockers=(),
        warnings=(),
        buy_request_created=False,
        no_trades_executed=True,
        to_dict=lambda: {"status": status},
    )


class JarvisV390IndividualStockPublicRankerTests(unittest.TestCase):
    def test_no_ready_stocks_reviews_without_ranking(self) -> None:
        result = build_individual_stock_public_ranker_result(
            current_date="2026-06-17",
            upstream_stock_universe_result=_upstream(
                _signal("blank", status=STOCK_MISSING_SOURCE, close_price=None)
            ),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.ranked_candidate_count, 0)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)

    def test_ranks_ready_stocks_by_score(self) -> None:
        result = build_individual_stock_public_ranker_result(
            current_date="2026-06-17",
            upstream_stock_universe_result=_upstream(
                _signal("lower", priority_score=10.0, symbol="lower.us"),
                _signal("higher", priority_score=80.0, symbol="higher.us"),
            ),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.ranked_candidate_count, 2)
        self.assertEqual(result.top_ranked_stock_id, "higher")
        self.assertEqual(result.ranked_candidates[0].decision_status, DECISION_STATUS_NOT_APPROVED)
        self.assertFalse(result.approval_ticket_mutation)

    def test_ignores_non_ready_and_invalid_price_signals(self) -> None:
        result = build_individual_stock_public_ranker_result(
            current_date="2026-06-17",
            upstream_stock_universe_result=_upstream(
                _signal("ready", close_price=10.0),
                _signal("missing", status=STOCK_MISSING_SOURCE, close_price=None),
                _signal("bad_price", close_price=0.0),
            ),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.ranked_candidate_count, 1)
        self.assertEqual(result.top_ranked_stock_id, "ready")

    def test_upstream_review_keeps_ranker_review(self) -> None:
        result = build_individual_stock_public_ranker_result(
            current_date="2026-06-17",
            upstream_stock_universe_result=_upstream(
                _signal("ready"),
                status="JARVIS_V38_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_REVIEW_REQUIRED_SAFE",
            ),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertIn("individual stock public universe engine requires review.", result.warnings)

    def test_write_ranked_stocks_under_jarvis_local_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_individual_stock_public_ranker_result(
                current_date="2026-06-17",
                root=root,
                write_ranked_stocks=True,
                upstream_stock_universe_result=_upstream(_signal("ready")),
            )

            self.assertTrue(result.ranked_stocks_written)
            path = root / "jarvis" / "local" / "individual_stock_public_ranked_candidates.local.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["ranked_candidate_count"], 1)
            self.assertFalse(payload["safety"]["buy_request_created"])
            self.assertFalse(payload["safety"]["trades_executed"])

    def test_ranked_path_outside_jarvis_local_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_individual_stock_public_ranker_result(
                current_date="2026-06-17",
                root=Path(tmp),
                ranked_stocks_path="outputs/bad_ranked_stocks.json",
                upstream_stock_universe_result=_upstream(_signal("ready")),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("ranked stocks path must remain under jarvis/local/.", result.blockers)

    def test_console_mentions_ranker_and_safety(self) -> None:
        result = build_individual_stock_public_ranker_result(
            current_date="2026-06-17",
            upstream_stock_universe_result=_upstream(_signal("ready")),
        )
        output = format_individual_stock_public_ranker(result)

        self.assertIn("Individual Stock Public Ranker", output)
        self.assertIn("Ranked individual stock candidates", output)
        self.assertIn("RANKED_STOCK_CANDIDATE_FOR_REVIEW_NOT_APPROVED", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)
        self.assertIn("Upstream individual stock public universe engine", output)
        self.assertNotIn("Upstream dual-lane daily refresh:\nJ.A.R.V.I.S. Autonomous Dual-Lane Daily Refresh", output)


if __name__ == "__main__":
    unittest.main()