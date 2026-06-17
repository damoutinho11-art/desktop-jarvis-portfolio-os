from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v39_0_individual_stock_public_ranker import DECISION_STATUS_NOT_APPROVED
from jarvis.jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import (
    STOCK_TICKET_DECISION_STATUS,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    bridge_stock_candidate_into_ticket,
    build_ranked_individual_stock_candidate_ticket_bridge_result,
    build_stock_ticket_payload,
    format_ranked_individual_stock_candidate_ticket_bridge,
)


def _candidate() -> SimpleNamespace:
    return SimpleNamespace(
        rank=1,
        stock_id="microsoft_msft_us",
        name="Microsoft Corporation",
        ticker="MSFT",
        symbol="MSFT",
        exchange="NASDAQ",
        market="USA",
        sector="Technology",
        provider="yahoo_chart",
        currency="USD",
        source_url="https://query1.finance.yahoo.com/v8/finance/chart/MSFT?range=5d&interval=1d",
        source_as_of="2026-06-17",
        close_price=450.0,
        priority_score=78.0,
        ranking_score=117.0,
        source_status="STOCK_PUBLIC_SOURCE_READY",
        decision_status=DECISION_STATUS_NOT_APPROVED,
    )


def _upstream_ready(
    *,
    candidate: SimpleNamespace | None = None,
    status: str = "JARVIS_V40_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_READY_SAFE",
    warnings: tuple[str, ...] = (),
) -> SimpleNamespace:
    ranker = SimpleNamespace(ranked_candidates=tuple([candidate] if candidate is not None else []))
    return SimpleNamespace(
        status=status,
        bootstrap_universe_written=True,
        stock_signals_written=True,
        ranked_stocks_written=True,
        ranked_candidate_count=1 if candidate is not None else 0,
        top_ranked_stock_id=candidate.stock_id if candidate is not None else None,
        top_ranked_symbol=candidate.symbol if candidate is not None else None,
        upstream_ranker_result=ranker,
        blockers=(),
        warnings=warnings,
        to_dict=lambda: {"status": "ready"},
    )


class JarvisV410RankedIndividualStockCandidateTicketBridgeTests(unittest.TestCase):
    def test_build_stock_ticket_payload_is_review_only(self) -> None:
        payload = build_stock_ticket_payload(candidate=_candidate(), current_date="2026-06-17")

        self.assertEqual(payload["decision_status"], STOCK_TICKET_DECISION_STATUS)
        self.assertEqual(payload["stock_id"], "microsoft_msft_us")
        self.assertIsNone(payload["amount_eur"])
        self.assertTrue(payload["manual_amount_required"])
        self.assertFalse(payload["approved_for_purchase"])
        self.assertFalse(payload["buy_request_created"])
        self.assertFalse(payload["order_created"])
        self.assertFalse(payload["trade_executed"])

    def test_available_candidate_without_ticket_write_reviews(self) -> None:
        result = build_ranked_individual_stock_candidate_ticket_bridge_result(
            current_date="2026-06-17",
            upstream_bootstrap_result=_upstream_ready(candidate=_candidate()),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertTrue(result.stock_candidate_available)
        self.assertFalse(result.stock_ticket_written)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertIn("ranked stock candidate is available but stock ticket bridge was not written.", result.warnings)

    def test_write_stock_ticket_updates_existing_approval_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps({"existing": "kept"}), encoding="utf-8")

            result = build_ranked_individual_stock_candidate_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_stock_ticket=True,
                upstream_bootstrap_result=_upstream_ready(candidate=_candidate()),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.stock_ticket_written)
            self.assertTrue(result.approval_ticket_mutation)
            payload = json.loads(ticket.read_text(encoding="utf-8"))
            self.assertEqual(payload["existing"], "kept")
            self.assertEqual(payload["selected_individual_stock_candidate"]["symbol"], "MSFT")
            self.assertEqual(payload["selected_individual_stock_candidate"]["decision_status"], STOCK_TICKET_DECISION_STATUS)
            self.assertFalse(payload["selected_individual_stock_candidate"]["approved_for_purchase"])

    def test_write_stock_ticket_with_available_candidate_ignores_nonblocking_upstream_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps({"existing": "kept"}), encoding="utf-8")

            result = build_ranked_individual_stock_candidate_ticket_bridge_result(
                current_date="2026-06-17",
                root=root,
                write_stock_ticket=True,
                upstream_bootstrap_result=_upstream_ready(
                    candidate=_candidate(),
                    status="JARVIS_V40_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_REVIEW_REQUIRED_SAFE",
                    warnings=("non-top bootstrap quote failed",),
                ),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.stock_ticket_written)
            self.assertEqual(result.warnings, ())
    def test_write_stock_ticket_missing_ticket_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_ranked_individual_stock_candidate_ticket_bridge_result(
                current_date="2026-06-17",
                root=Path(tmp),
                write_stock_ticket=True,
                upstream_bootstrap_result=_upstream_ready(candidate=_candidate()),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("approval ticket path does not exist" in blocker for blocker in result.blockers))

    def test_no_candidate_reviews(self) -> None:
        result = build_ranked_individual_stock_candidate_ticket_bridge_result(
            current_date="2026-06-17",
            upstream_bootstrap_result=_upstream_ready(candidate=None),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.stock_candidate_available)
        self.assertIn("no ranked individual stock candidate is available to bridge.", result.warnings)

    def test_ticket_path_outside_outputs_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_ranked_individual_stock_candidate_ticket_bridge_result(
                current_date="2026-06-17",
                root=Path(tmp),
                approval_ticket_path="jarvis/local/bad_ticket.json",
                upstream_bootstrap_result=_upstream_ready(candidate=_candidate()),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("approval ticket path must remain under outputs/.", result.blockers)

    def test_direct_bridge_path_outside_outputs_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                bridge_stock_candidate_into_ticket(
                    approval_ticket_path="jarvis/local/bad_ticket.json",
                    root=Path(tmp),
                    current_date="2026-06-17",
                    candidate=_candidate(),
                )

    def test_console_mentions_review_only_and_safety(self) -> None:
        result = build_ranked_individual_stock_candidate_ticket_bridge_result(
            current_date="2026-06-17",
            upstream_bootstrap_result=_upstream_ready(candidate=_candidate()),
        )
        output = format_ranked_individual_stock_candidate_ticket_bridge(result)

        self.assertIn("Ranked Individual Stock Candidate Ticket Bridge", output)
        self.assertIn("review-only", output)
        self.assertIn("no stock is approved", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()