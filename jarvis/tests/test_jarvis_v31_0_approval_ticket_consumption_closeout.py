from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v31_0_approval_ticket_consumption_closeout import (
    STATUS_BLOCKED,
    STATUS_REVIEW_REQUIRED,
    build_approval_ticket_consumption_closeout_result,
    format_approval_ticket_consumption_closeout,
)


def _ticket() -> dict:
    return {
        "as_of": "2026-06-04",
        "allocation_basis_as_of": "2026-06-04",
        "generated_at": "2026-06-17",
        "selected_crypto_candidate": "hype",
        "selected_crypto_amount_eur": 41.54,
        "selected_stock_fund_etf_candidate": "quality_etf",
        "selected_stock_fund_etf_amount_eur": 62.31,
        "approval_status": "pending_manual_approval",
        "manual_approval_required": True,
        "final_user_buy_action_required": True,
        "portfolio_data_stale_review_required": True,
        "buy_request_created": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "trades_executed": False,
        "source_bridge_summary": {
            "allocation_basis_candidate": "btc",
            "selected_expanded_crypto_candidate": "hype",
        },
    }


def _preview() -> SimpleNamespace:
    return SimpleNamespace(
        selected_crypto_candidate="hype",
        selected_crypto_amount_eur=41.54,
        selected_stock_fund_etf_candidate="quality_etf",
        selected_stock_fund_etf_amount_eur=62.31,
        allocation_basis_as_of="2026-06-04",
        ticket_generated_at="2026-06-17",
        portfolio_data_stale_review_required=True,
        blockers=(),
        warnings=("portfolio_state is 13 days old; refresh required before manual action.",),
    )


class JarvisV310ApprovalTicketConsumptionCloseoutTests(unittest.TestCase):
    def test_consumes_refreshed_ticket_as_manual_action_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            ticket_path.parent.mkdir(parents=True)
            ticket_path.write_text(json.dumps(_ticket()), encoding="utf-8")

            result = build_approval_ticket_consumption_closeout_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                preview_result=_preview(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.ticket_loaded)
            self.assertTrue(result.ticket_matches_current_preview)
            self.assertEqual(result.selected_crypto_candidate, "hype")
            self.assertEqual(result.selected_crypto_amount_eur, 41.54)
            self.assertEqual(result.selected_stock_fund_etf_candidate, "quality_etf")
            self.assertEqual(result.selected_stock_fund_etf_amount_eur, 62.31)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.portfolio_state_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_blocks_ambiguous_nested_source_bridge_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = _ticket()
            ticket["source_bridge_result"] = {"selected_crypto_candidate": "btc"}
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            ticket_path.parent.mkdir(parents=True)
            ticket_path.write_text(json.dumps(ticket), encoding="utf-8")

            result = build_approval_ticket_consumption_closeout_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                preview_result=_preview(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(result.ticket_has_ambiguous_nested_source_bridge_result)

    def test_blocks_ticket_with_execution_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = _ticket()
            ticket["trades_executed"] = True
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            ticket_path.parent.mkdir(parents=True)
            ticket_path.write_text(json.dumps(ticket), encoding="utf-8")

            result = build_approval_ticket_consumption_closeout_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                preview_result=_preview(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("approval ticket must not execute trades.", result.blockers)

    def test_missing_ticket_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_approval_ticket_consumption_closeout_result(
                current_date="2026-06-17",
                root=Path(tmp),
                ticket_path="outputs/approval_ticket_latest.json",
                preview_result=_preview(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.ticket_loaded)

    def test_console_output_is_clean_manual_action_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            ticket_path.parent.mkdir(parents=True)
            ticket_path.write_text(json.dumps(_ticket()), encoding="utf-8")
            result = build_approval_ticket_consumption_closeout_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                preview_result=_preview(),
            )

            output = format_approval_ticket_consumption_closeout(result)

            self.assertIn("Daily Manual Action Brief", output)
            self.assertIn("Crypto lane manual buy candidate: hype EUR 41.54", output)
            self.assertIn("Stock/Fund/ETF lane manual buy candidate: quality_etf EUR 62.31", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()