from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.jarvis_v29_0_expanded_crypto_allocation_eligibility_bridge import (
    DECISION_BLOCKED_BY_PLATFORM_ROUTE,
    DECISION_SELECTED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_expanded_crypto_allocation_eligibility_bridge,
    build_expanded_crypto_allocation_eligibility_console_output,
)


def _candidate(
    candidate_id: str,
    *,
    rank: int,
    score: float,
    source_ready: bool = True,
    platform_ready: bool = True,
    prior_status: str = "BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET",
    executable_amount_eur: float = 0.0,
) -> SimpleNamespace:
    return SimpleNamespace(
        candidate_id=candidate_id,
        rank=rank,
        score=score,
        source_quality_ready=source_ready,
        platform_ready=platform_ready,
        platform_route="lhv_crypto" if platform_ready else "kraken",
        decision_status=prior_status,
        executable_amount_eur=executable_amount_eur,
        warnings=(),
    )


def _upstream(
    candidates: list[SimpleNamespace],
    *,
    basis_candidate: str = "btc",
    basis_amount: float = 41.54,
    status: str = "JARVIS_V28_0_EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_READY_SAFE",
    ranking_ready: bool = True,
    full_coverage: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        selected_crypto_candidate=basis_candidate,
        selected_crypto_amount_eur=basis_amount,
        full_public_data_coverage=full_coverage,
        expanded_crypto_ranking_ready=ranking_ready,
        candidate_decisions=tuple(candidates),
        blockers=(),
        warnings=(),
        to_dict=lambda: {},
    )


class JarvisV290ExpandedCryptoAllocationEligibilityBridgeTests(unittest.TestCase):
    def test_reassigns_crypto_lane_budget_to_top_ranked_eligible_asset(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [
                    _candidate("hype", rank=1, score=86.49),
                    _candidate("btc", rank=2, score=83.33, prior_status="SELECTED_FOR_WEEKLY_CRYPTO_MANUAL_BUY", executable_amount_eur=41.54),
                ]
            )
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.allocation_basis_candidate, "btc")
        self.assertEqual(result.selected_crypto_candidate, "hype")
        self.assertEqual(result.selected_crypto_amount_eur, 41.54)
        self.assertTrue(result.reassigned_from_allocation_basis)
        self.assertTrue(result.approval_ticket_refresh_required)
        self.assertEqual(result.candidate_decisions[0].decision_status, DECISION_SELECTED)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_keeps_allocation_basis_when_it_is_top_eligible_asset(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [
                    _candidate("btc", rank=1, score=83.33, prior_status="SELECTED_FOR_WEEKLY_CRYPTO_MANUAL_BUY", executable_amount_eur=41.54),
                    _candidate("hype", rank=2, score=80.0),
                ],
                basis_candidate="btc",
            )
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_crypto_candidate, "btc")
        self.assertFalse(result.reassigned_from_allocation_basis)

    def test_platform_blocked_top_asset_is_skipped(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [
                    _candidate("tao", rank=1, score=90.0, platform_ready=False, prior_status="BLOCKED_BY_PLATFORM"),
                    _candidate("btc", rank=2, score=83.33, prior_status="SELECTED_FOR_WEEKLY_CRYPTO_MANUAL_BUY", executable_amount_eur=41.54),
                ],
                basis_candidate="btc",
            )
        )

        self.assertEqual(result.selected_crypto_candidate, "btc")
        self.assertEqual(result.candidate_decisions[0].decision_status, DECISION_BLOCKED_BY_PLATFORM_ROUTE)

    def test_no_crypto_lane_budget_requires_review(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [_candidate("hype", rank=1, score=86.49)],
                basis_candidate=None,
                basis_amount=0.0,
            )
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertIsNone(result.selected_crypto_candidate)
        self.assertIn("No executable crypto-lane budget", " ".join(result.warnings))

    def test_upstream_review_required_preserved(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [_candidate("hype", rank=1, score=86.49)],
                status="JARVIS_V28_0_EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED_SAFE",
            )
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.selected_crypto_candidate, "hype")
        self.assertTrue(result.approval_ticket_refresh_required)

    def test_console_output_mentions_reassignment_and_safety(self) -> None:
        result = build_expanded_crypto_allocation_eligibility_bridge(
            upstream_daily_result=_upstream(
                [
                    _candidate("hype", rank=1, score=86.49),
                    _candidate("btc", rank=2, score=83.33, prior_status="SELECTED_FOR_WEEKLY_CRYPTO_MANUAL_BUY", executable_amount_eur=41.54),
                ]
            )
        )

        output = build_expanded_crypto_allocation_eligibility_console_output(result)

        self.assertIn("Daily Operator with Expanded Crypto Allocation Eligibility", output)
        self.assertIn("selected crypto candidate: hype", output)
        self.assertIn("reassigned from allocation basis: True", output)
        self.assertIn("approval ticket refresh required: True", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()