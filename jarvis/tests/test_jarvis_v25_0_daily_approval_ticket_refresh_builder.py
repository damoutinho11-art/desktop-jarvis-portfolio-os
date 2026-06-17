from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v25_0_daily_approval_ticket_refresh_builder import (
    STATUS_BLOCKED,
    STATUS_REVIEW_REQUIRED,
    build_daily_approval_ticket_refresh_builder_result,
)


def _fake_bridge() -> SimpleNamespace:
    daily = SimpleNamespace(
        status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE",
        readiness_status="STALE_REVIEW_REQUIRED",
        recommendation_trust="refresh_required_before_manual_action",
        stale_data_review_required=True,
        manual_action_guidance="Refresh local portfolio data before any manual buy.",
        blockers=(),
        warnings=("portfolio_state is stale",),
        allocation_result={
            "portfolio_mode": "transition_mode",
            "weekly_budget": 103.85,
            "selected_ideal_sleeve": "quality_etf",
            "ideal_allocation": {"btc": 41.54, "quality_etf": 62.31},
            "executable_allocation": {"btc": 41.54, "quality_etf": 62.31},
            "weekly_dual_lane_mandate": {
                "crypto_lane": {"asset": "btc", "amount": 41.54, "status": "READY_FOR_MANUAL_BUY"},
                "stock_fund_etf_lane": {"asset": "quality_etf", "amount": 62.31, "status": "READY_FOR_MANUAL_BUY"},
            },
            "ranked_candidates": [
                {"sleeve": "quality_etf", "rank": 1, "selected": True, "score": 83.0},
            ],
        },
        freshness_checks=[
            {"name": "portfolio_state", "status": "STALE", "age_days": 13},
        ],
    )
    crypto = SimpleNamespace(
        to_dict=lambda: {
            "selected_crypto_candidate": "btc",
            "selected_crypto_amount_eur": 41.54,
            "candidate_count": 3,
            "eligible_candidate_count": 1,
            "blocked_candidate_count": 2,
        }
    )
    return SimpleNamespace(
        status="JARVIS_V24_0_CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED_SAFE",
        bridge_status="CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED",
        daily_readiness_result=daily,
        crypto_selection_result=crypto,
        selected_crypto_candidate="btc",
        selected_crypto_amount_eur=41.54,
        blockers=(),
        warnings=("portfolio_state is stale",),
        to_dict=lambda: {"status": "fake", "selected_crypto_candidate": "btc"},
    )


class JarvisV250DailyApprovalTicketRefreshBuilderTests(unittest.TestCase):
    def test_builds_current_dual_lane_approval_ticket_without_execution(self) -> None:
        result = build_daily_approval_ticket_refresh_builder_result(
            current_date="2026-06-17",
            bridge_result=_fake_bridge(),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.approval_ticket_written)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.credentials_forbidden)
        self.assertTrue(result.private_account_data_ingestion_forbidden)
        self.assertTrue(result.order_creation_forbidden)
        self.assertTrue(result.no_trades_executed)
        self.assertEqual(result.approval_ticket["as_of"], "2026-06-17")
        self.assertEqual(result.approval_ticket["selected_crypto_candidate"], "btc")
        self.assertEqual(result.approval_ticket["selected_stock_fund_etf_candidate"], "quality_etf")

    def test_write_ticket_updates_outputs_path_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_daily_approval_ticket_refresh_builder_result(
                current_date="2026-06-17",
                root=root,
                output_path="outputs/approval_ticket_latest.json",
                write_ticket=True,
                bridge_result=_fake_bridge(),
            )

            output = root / "outputs" / "approval_ticket_latest.json"
            self.assertTrue(result.approval_ticket_written)
            self.assertTrue(result.approval_ticket_mutation)
            self.assertTrue(output.exists())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["ticket_id"], "JARVIS-2026-06-17-daily-dual-lane-manual-approval")
            self.assertFalse(payload["buy_request_created"])

    def test_blocks_output_outside_outputs_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_daily_approval_ticket_refresh_builder_result(
                current_date="2026-06-17",
                root=root,
                output_path="approval_ticket_latest.json",
                write_ticket=True,
                bridge_result=_fake_bridge(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.approval_ticket_written)
            self.assertIn("output_path must remain under outputs", " ".join(result.blockers))


if __name__ == "__main__":
    unittest.main()