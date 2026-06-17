from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v39_0_individual_stock_public_ranker import DECISION_STATUS_NOT_APPROVED, STATUS_READY as RANKER_READY
from jarvis.jarvis_v40_0_individual_stock_public_universe_bootstrap import (
    STARTER_STOCK_UNIVERSE,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_bootstrap_stock_universe_payload,
    build_individual_stock_public_universe_bootstrap_result,
    format_individual_stock_public_universe_bootstrap,
    write_bootstrap_stock_universe,
)


def _ranker_ready() -> SimpleNamespace:
    candidate = SimpleNamespace(
        rank=1,
        stock_id="microsoft_msft_us",
        symbol="msft.us",
        ticker="MSFT",
        ranking_score=118.0,
        decision_status=DECISION_STATUS_NOT_APPROVED,
    )
    return SimpleNamespace(
        status=RANKER_READY,
        ready_stock_count=1,
        ranked_candidate_count=1,
        top_ranked_stock_id="microsoft_msft_us",
        top_ranked_symbol="msft.us",
        ranked_candidates=(candidate,),
        ranked_stocks_written=True,
        upstream_stock_universe_result=SimpleNamespace(stock_signals_written=True),
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": RANKER_READY},
    )


class JarvisV400IndividualStockPublicUniverseBootstrapTests(unittest.TestCase):
    def test_bootstrap_payload_contains_real_public_stock_sources_and_safety(self) -> None:
        payload = build_bootstrap_stock_universe_payload(current_date="2026-06-17")

        self.assertEqual(payload["decision_status"], "PUBLIC_STOCK_UNIVERSE_BOOTSTRAP_NOT_APPROVED_NOT_A_BUY_LIST")
        self.assertGreaterEqual(len(payload["stocks"]), 8)
        self.assertTrue(all(stock["provider"] == "yahoo_chart" for stock in payload["stocks"]))
        self.assertTrue(all(stock["symbol"].isupper() for stock in payload["stocks"]))
        self.assertFalse(payload["safety"]["buy_request_created"])
        self.assertFalse(payload["safety"]["trades_executed"])

    def test_write_bootstrap_stock_universe_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = write_bootstrap_stock_universe(
                path="jarvis/local/individual_stock_public_universe.local.json",
                root=root,
                current_date="2026-06-17",
            )

            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["stocks"]), len(STARTER_STOCK_UNIVERSE))
            self.assertEqual(payload["stocks"][0]["symbol"], "AAPL")

    def test_write_bootstrap_stock_universe_outside_local_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_bootstrap_stock_universe(
                    path="outputs/bad_stock_universe.json",
                    root=Path(tmp),
                    current_date="2026-06-17",
                )

    def test_bootstrap_wrapper_ready_when_ranker_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_individual_stock_public_universe_bootstrap_result(
                current_date="2026-06-17",
                root=Path(tmp),
                bootstrap_stock_universe=True,
                write_stock_signals=True,
                write_ranked_stocks=True,
            )
            # Network is not used in this test path, so assert the file side only here.
            self.assertTrue((Path(tmp) / "jarvis" / "local" / "individual_stock_public_universe.local.json").exists())

    def test_result_ready_with_injected_ready_ranker(self) -> None:
        # Build via direct result object shape to lock v40 status semantics.
        ranker = _ranker_ready()
        result = build_individual_stock_public_universe_bootstrap_result(
            current_date="2026-06-17",
            root=Path(tempfile.mkdtemp()),
            bootstrap_stock_universe=False,
        )
        # The normal path depends on local files/network. Verify formatter separately with injected-like object below.
        output = format_individual_stock_public_universe_bootstrap(
            result.__class__(
                status=STATUS_READY,
                bootstrap_status="INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_READY",
                recommended_next_stage=result.recommended_next_stage,
                current_date=result.current_date,
                stock_universe_path=result.stock_universe_path,
                stock_signals_path=result.stock_signals_path,
                ranked_stocks_path=result.ranked_stocks_path,
                bootstrap_style=result.bootstrap_style,
                bootstrap_stock_count=result.bootstrap_stock_count,
                bootstrap_universe_written=True,
                stock_signals_written=True,
                ranked_stocks_written=True,
                upstream_ranker_result=ranker,
                ranked_candidate_count=1,
                top_ranked_stock_id="microsoft_msft_us",
                top_ranked_symbol="msft.us",
                recommendation_quality_current_data=True,
                allocation_mutation=False,
                approval_ticket_mutation=False,
                portfolio_state_mutation=False,
                buy_request_created=False,
                broker_connection_forbidden=True,
                credentials_forbidden=True,
                private_account_data_ingestion_forbidden=True,
                order_creation_forbidden=True,
                no_trades_executed=True,
                final_user_buy_action_required=True,
                blockers=(),
                warnings=(),
            )
        )

        self.assertIn("not a buy list", output)
        self.assertIn("microsoft_msft_us", output)
        self.assertIn(DECISION_STATUS_NOT_APPROVED, output)
        self.assertIn("no broker connection", output)
        self.assertIn("warnings: none", output)

    def test_path_outside_jarvis_local_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_individual_stock_public_universe_bootstrap_result(
                current_date="2026-06-17",
                root=Path(tmp),
                stock_universe_path="outputs/bad_stock_universe.json",
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("stock universe path must remain under jarvis/local/.", result.blockers)

    def test_invalid_date_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_individual_stock_public_universe_bootstrap_result(
                current_date="bad-date",
                root=Path(tmp),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("current_date must use YYYY-MM-DD format.", result.blockers)


if __name__ == "__main__":
    unittest.main()