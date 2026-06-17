from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v42_0_three_lane_daily_action_brief import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_three_lane_daily_action_brief_result,
    format_three_lane_daily_action_brief,
)


def _ticket_payload() -> dict:
    return {
        "selected_crypto_candidate": "hype",
        "selected_crypto_amount_eur": 41.54,
        "selected_stock_fund_etf_sleeve": "quality_etf",
        "stock_fund_etf_source_metadata": {
            "public_source_ready": True,
        },
        "selected_stock_fund_etf_real_instrument": {
            "name": "iShares Edge MSCI World Quality Factor UCITS ETF USD (Acc)",
            "symbol": "IS3Q.DE",
            "isin": "IE00BP3QZ601",
            "amount_eur": 62.31,
            "public_source_ready": True,
        },
        "selected_individual_stock_candidate": {
            "stock_id": "microsoft_msft_us",
            "name": "Microsoft Corporation",
            "symbol": "MSFT",
            "amount_eur": None,
            "manual_amount_required": True,
            "approved_for_purchase": False,
            "decision_status": "RANKED_INDIVIDUAL_STOCK_CANDIDATE_BRIDGED_FOR_REVIEW_NOT_APPROVED",
            "source_as_of": "2026-06-16",
            "close_price": 393.829987,
            "currency": "USD",
        },
    }


def _bridge_ready() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V41_0_RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_READY_SAFE",
        stock_ticket_written=True,
        approval_ticket_mutation=True,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": "ready"},
    )


class JarvisV420ThreeLaneDailyActionBriefTests(unittest.TestCase):
    def test_three_lane_brief_ready_from_ticket_and_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(_ticket_payload()), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                upstream_stock_bridge_result=_bridge_ready(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.crypto_candidate, "hype")
            self.assertEqual(result.etf_symbol, "IS3Q.DE")
            self.assertTrue(result.etf_public_source_ready)
            self.assertEqual(result.stock_symbol, "MSFT")
            self.assertIsNone(result.stock_amount_eur)
            self.assertTrue(result.stock_manual_amount_required)
            self.assertFalse(result.stock_approved_for_purchase)
            self.assertFalse(result.buy_request_created)

    def test_etf_public_source_ready_derived_from_metadata_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _ticket_payload()
            payload["stock_fund_etf_source_metadata"] = {
                "metadata_status": "ETF_SOURCE_METADATA_READY"
            }
            payload["selected_stock_fund_etf_real_instrument"].pop("public_source_ready", None)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(payload), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                upstream_stock_bridge_result=_bridge_ready(),
            )

            self.assertTrue(result.etf_public_source_ready)
    def test_stock_amount_blocks_if_assigned_before_manual_router(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _ticket_payload()
            payload["selected_individual_stock_candidate"]["amount_eur"] = 50.0
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(payload), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                upstream_stock_bridge_result=_bridge_ready(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("individual stock candidate amount_eur must remain null until manual amount routing exists.", result.blockers)

    def test_stock_approval_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _ticket_payload()
            payload["selected_individual_stock_candidate"]["approved_for_purchase"] = True
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(payload), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                upstream_stock_bridge_result=_bridge_ready(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("individual stock candidate must not be approved for purchase.", result.blockers)

    def test_skip_stock_bridge_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(_ticket_payload()), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                run_stock_bridge=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertIn("stock bridge was not run.", result.warnings)

    def test_ticket_missing_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=Path(tmp),
                upstream_stock_bridge_result=_bridge_ready(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("approval ticket path does not exist" in blocker for blocker in result.blockers))

    def test_console_brief_contains_three_lanes_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ticket = root / "outputs" / "approval_ticket_latest.json"
            ticket.parent.mkdir(parents=True)
            ticket.write_text(json.dumps(_ticket_payload()), encoding="utf-8")

            result = build_three_lane_daily_action_brief_result(
                current_date="2026-06-17",
                root=root,
                upstream_stock_bridge_result=_bridge_ready(),
            )
            output = format_three_lane_daily_action_brief(result)

            self.assertIn("Crypto lane", output)
            self.assertIn("Stock/Fund/ETF lane", output)
            self.assertIn("Individual stock lane", output)
            self.assertIn("manual amount required", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()