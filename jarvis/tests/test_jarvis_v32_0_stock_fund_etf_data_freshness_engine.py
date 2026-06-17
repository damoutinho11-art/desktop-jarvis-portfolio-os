from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v32_0_stock_fund_etf_data_freshness_engine import (
    ITEM_MISSING,
    ITEM_READY,
    ITEM_STALE,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_stock_fund_etf_data_freshness_engine_result,
    format_stock_fund_etf_data_freshness_engine,
)


def _manual(status: str = "JARVIS_V31_0_APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(status=status, blockers=(), warnings=(), to_dict=lambda: {"status": status})


def _ticket(*, metadata: str | None = None, unsafe: bool = False) -> dict:
    sleeve = {"candidate_id": "quality_etf", "score": 83.0}
    if metadata is not None:
        sleeve["as_of"] = metadata

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
        "buy_request_created": unsafe,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "trades_executed": False,
        "etf_scoring_verdict": {
            "selected_ideal_etf": "quality_etf",
            "sleeves": [sleeve],
        },
    }


def _write_ticket(root: Path, ticket: dict) -> None:
    path = root / "outputs" / "approval_ticket_latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(ticket), encoding="utf-8")


class JarvisV320StockFundEtfDataFreshnessEngineTests(unittest.TestCase):
    def test_ready_when_selected_etf_has_fresh_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root, _ticket(metadata="2026-06-17"))

            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                manual_action_result=_manual(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.selected_stock_fund_etf_candidate, "quality_etf")
            self.assertEqual(result.selected_candidate_metadata_status, ITEM_READY)
            self.assertTrue(result.stock_fund_etf_metadata_ready)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_missing_metadata_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root, _ticket(metadata=None))

            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                manual_action_result=_manual(),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.selected_candidate_metadata_status, ITEM_MISSING)
            self.assertTrue(result.stock_fund_etf_metadata_missing_or_stale)

    def test_stale_metadata_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root, _ticket(metadata="2026-06-01"))

            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                manual_action_result=_manual(),
                max_age_days=7,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.selected_candidate_metadata_status, ITEM_STALE)
            self.assertEqual(result.metadata_stale_count, 1)

    def test_manual_action_review_status_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root, _ticket(metadata="2026-06-17"))

            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                manual_action_result=_manual("JARVIS_V31_0_APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_REVIEW_REQUIRED_SAFE"),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)

    def test_blocks_unsafe_ticket_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=Path(tmp),
                ticket_path="approval_ticket_latest.json",
                manual_action_result=_manual(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("approval ticket path must remain under outputs/.", result.blockers)

    def test_console_mentions_freshness_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ticket(root, _ticket(metadata=None))
            result = build_stock_fund_etf_data_freshness_engine_result(
                current_date="2026-06-17",
                root=root,
                ticket_path="outputs/approval_ticket_latest.json",
                manual_action_result=_manual(),
            )

            output = format_stock_fund_etf_data_freshness_engine(result)

            self.assertIn("Stock/Fund/ETF Data Freshness Engine", output)
            self.assertIn("selected stock/fund/ETF candidate: quality_etf", output)
            self.assertIn("selected candidate metadata status: ETF_SOURCE_METADATA_MISSING", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()