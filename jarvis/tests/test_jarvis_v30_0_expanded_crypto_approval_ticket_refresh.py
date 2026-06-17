from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v29_0_expanded_crypto_allocation_eligibility_bridge import (
    CryptoAllocationEligibilityDecision,
)
from jarvis.jarvis_v30_0_expanded_crypto_approval_ticket_refresh import (
    STATUS_REVIEW_REQUIRED,
    build_expanded_crypto_approval_ticket_refresh_result,
    format_expanded_crypto_approval_ticket_refresh,
)


def _decision(candidate_id: str, *, selected: bool, proposed_amount_eur: float) -> CryptoAllocationEligibilityDecision:
    return CryptoAllocationEligibilityDecision(
        candidate_id=candidate_id,
        rank=1 if selected else 2,
        score=86.49 if selected else 83.33,
        eligible=True,
        selected=selected,
        proposed_amount_eur=proposed_amount_eur,
        allocation_basis_amount_eur=0.0 if selected else 41.54,
        source_quality_ready=True,
        platform_ready=True,
        platform_route="lhv_crypto",
        prior_daily_decision_status="ELIGIBLE",
        decision_status="SELECTED_FOR_CRYPTO_LANE_MANUAL_BUY" if selected else "ELIGIBLE_NOT_SELECTED",
        blockers=(),
        warnings=(),
    )


def _allocation_result() -> dict:
    return {
        "as_of": "2026-06-04",
        "portfolio_mode": "transition_mode",
        "weekly_budget": 103.85,
        "weekly_dual_lane_mandate": {
            "stock_fund_etf_lane": {
                "asset": "quality_etf",
                "amount": 62.31,
            }
        },
        "ideal_allocation": {"quality_etf": 62.31},
        "executable_allocation": {"btc": 41.54, "quality_etf": 62.31},
        "selected_ideal_sleeve": "quality_etf",
        "ranked_candidates": [{"candidate_id": "quality_etf", "score": 83.0}],
    }


def _v29_result(status: str = "JARVIS_V29_0_EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_REVIEW_REQUIRED_SAFE") -> SimpleNamespace:
    daily_readiness = SimpleNamespace(
        allocation_result=_allocation_result(),
        readiness_status="STALE_REVIEW_REQUIRED",
        recommendation_trust="refresh_required_before_manual_action",
        manual_action_guidance="Refresh local portfolio data and approval ticket before any manual buy.",
        stale_data_review_required=True,
        freshness_checks=[],
        blockers=(),
        warnings=("portfolio_state is 13 days old; refresh required before manual action.",),
        to_dict=lambda: {
            "allocation_result": _allocation_result(),
            "readiness_status": "STALE_REVIEW_REQUIRED",
            "recommendation_trust": "refresh_required_before_manual_action",
            "manual_action_guidance": "Refresh local portfolio data and approval ticket before any manual buy.",
            "stale_data_review_required": True,
            "freshness_checks": [],
            "blockers": [],
            "warnings": ["portfolio_state is 13 days old; refresh required before manual action."],
        },
    )
    upstream = SimpleNamespace(
        daily_readiness_result=daily_readiness,
        to_dict=lambda: {"daily_readiness_result": daily_readiness.to_dict()},
    )
    return SimpleNamespace(
        status=status,
        bridge_status="EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_REVIEW_REQUIRED",
        upstream_daily_result=upstream,
        allocation_basis_candidate="btc",
        allocation_basis_amount_eur=41.54,
        selected_crypto_candidate="hype",
        selected_crypto_amount_eur=41.54,
        selected_crypto_rank=1,
        selected_crypto_score=86.49,
        reassigned_from_allocation_basis=True,
        approval_ticket_refresh_required=True,
        full_public_data_coverage=True,
        expanded_crypto_ranking_ready=True,
        candidate_decisions=(_decision("hype", selected=True, proposed_amount_eur=41.54), _decision("btc", selected=False, proposed_amount_eur=0.0)),
        blockers=(),
        warnings=("Crypto-lane candidate changed from allocation basis btc to hype; approval ticket refresh is required before manual action.",),
        to_dict=lambda: {
            "status": status,
            "bridge_status": "EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_REVIEW_REQUIRED",
            "upstream_daily_result": upstream.to_dict(),
            "allocation_basis_candidate": "btc",
            "allocation_basis_amount_eur": 41.54,
            "selected_crypto_candidate": "hype",
            "selected_crypto_amount_eur": 41.54,
            "selected_crypto_rank": 1,
            "selected_crypto_score": 86.49,
            "reassigned_from_allocation_basis": True,
            "approval_ticket_refresh_required": True,
            "full_public_data_coverage": True,
            "expanded_crypto_ranking_ready": True,
            "candidate_decisions": [_decision("hype", selected=True, proposed_amount_eur=41.54).to_dict()],
            "blockers": [],
            "warnings": ["Crypto-lane candidate changed from allocation basis btc to hype; approval ticket refresh is required before manual action."],
        },
    )


class JarvisV300ExpandedCryptoApprovalTicketRefreshTests(unittest.TestCase):
    def test_builds_ticket_with_expanded_crypto_selection_and_allocation_basis_asof(self) -> None:
        result = build_expanded_crypto_approval_ticket_refresh_result(
            current_date="2026-06-17",
            v29_result=_v29_result(),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.approval_ticket_written)
        self.assertEqual(result.selected_crypto_candidate, "hype")
        self.assertEqual(result.selected_crypto_amount_eur, 41.54)
        self.assertEqual(result.selected_stock_fund_etf_candidate, "quality_etf")
        self.assertEqual(result.selected_stock_fund_etf_amount_eur, 62.31)
        self.assertEqual(result.allocation_basis_as_of, "2026-06-04")
        self.assertEqual(result.ticket_generated_at, "2026-06-17")
        self.assertTrue(result.expanded_crypto_candidate_reassigned)
        self.assertTrue(result.approval_ticket_refresh_required)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_write_ticket_is_limited_to_outputs_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_expanded_crypto_approval_ticket_refresh_result(
                current_date="2026-06-17",
                root=root,
                output_path="outputs/approval_ticket_latest.json",
                write_ticket=True,
                v29_result=_v29_result(),
            )

            ticket_path = root / "outputs" / "approval_ticket_latest.json"
            self.assertTrue(result.approval_ticket_written)
            self.assertTrue(ticket_path.exists())
            ticket = json.loads(ticket_path.read_text(encoding="utf-8"))
            self.assertEqual(ticket["selected_crypto_candidate"], "hype")
            self.assertEqual(ticket["selected_crypto_amount_eur"], 41.54)
            self.assertNotIn("source_bridge_result", ticket)
            self.assertEqual(ticket["source_bridge_summary"]["selected_expanded_crypto_candidate"], "hype")
            self.assertEqual(ticket["source_bridge_summary"]["allocation_basis_candidate"], "btc")
            self.assertEqual(ticket["as_of"], "2026-06-04")
            self.assertEqual(ticket["generated_at"], "2026-06-17")
            self.assertTrue(ticket["manual_approval_required"])
            self.assertFalse(ticket["buy_request_created"])
            self.assertTrue(ticket["broker_connection_forbidden"])
            self.assertFalse(ticket["trades_executed"])

    def test_rejects_output_path_outside_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_expanded_crypto_approval_ticket_refresh_result(
                current_date="2026-06-17",
                root=Path(tmp),
                output_path="approval_ticket_latest.json",
                write_ticket=True,
                v29_result=_v29_result(),
            )

            self.assertIn("BLOCKED", result.status)
            self.assertIn("approval ticket output_path must remain under outputs/.", result.blockers)

    def test_console_output_mentions_ticket_refresh_and_safety(self) -> None:
        result = build_expanded_crypto_approval_ticket_refresh_result(
            current_date="2026-06-17",
            v29_result=_v29_result(),
        )

        output = format_expanded_crypto_approval_ticket_refresh(result)

        self.assertIn("Expanded Crypto Approval Ticket Refresh", output)
        self.assertIn("selected crypto candidate: hype", output)
        self.assertIn("selected stock/fund/ETF candidate: quality_etf", output)
        self.assertIn("approval ticket refresh required: True", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()