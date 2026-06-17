from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.jarvis_v28_0_expanded_crypto_ranking_daily_operator_bridge import (
    DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET,
    DECISION_BLOCKED_BY_PLATFORM,
    DECISION_SELECTED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_expanded_crypto_ranking_daily_operator_bridge,
    build_expanded_crypto_ranking_daily_operator_console_output,
)


def _daily(status: str = "JARVIS_TEST_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(status=status, blockers=(), warnings=(), stale_data_review_required=False)


def _score(
    candidate_id: str,
    *,
    total_score: float,
    platform_ready: bool = True,
    decision_status: str = "RANKED_FOR_CRYPTO_LANE",
) -> SimpleNamespace:
    return SimpleNamespace(
        candidate_id=candidate_id,
        total_score=total_score,
        source_quality_ready=True,
        platform_ready=platform_ready,
        platform_route="lhv_crypto" if platform_ready else "kraken",
        decision_status=decision_status,
        price_eur=10.0,
        market_cap_eur=1_000_000_000.0,
        volume_24h_eur=100_000_000.0,
        change_24h_pct=1.0,
        signal_age_days=0,
        warnings=(),
    )


def _ranking(scores: list[SimpleNamespace], *, ready: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        status=(
            "JARVIS_V27_0_EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_READY_SAFE"
            if ready
            else "JARVIS_V27_0_EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_REVIEW_REQUIRED_SAFE"
        ),
        full_public_data_coverage=ready,
        source_quality_ready_count=len(scores) if ready else max(0, len(scores) - 1),
        source_quality_blocked_count=0 if ready else 1,
        ranked_candidate_count=len([item for item in scores if item.decision_status == "RANKED_FOR_CRYPTO_LANE"]),
        candidate_scores=tuple(scores),
        blockers=(),
        warnings=(),
        to_dict=lambda: {},
    )


class JarvisV280ExpandedCryptoRankingDailyOperatorBridgeTests(unittest.TestCase):
    def test_selects_highest_ranked_candidate_with_executable_amount(self) -> None:
        ranking = _ranking([_score("hype", total_score=90.0), _score("btc", total_score=80.0)])
        allocation = {
            "ideal_allocations_cents": {"hype": 1000, "btc": 2000},
            "executable_allocations_cents": {"hype": 1234, "btc": 2000},
        }

        result = build_expanded_crypto_ranking_daily_operator_bridge(
            daily_readiness_result=_daily(),
            crypto_ranking_result=ranking,
            allocation_result=allocation,
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_crypto_candidate, "hype")
        self.assertEqual(result.selected_crypto_amount_eur, 12.34)
        self.assertEqual(result.candidate_decisions[0].decision_status, DECISION_SELECTED)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.credentials_forbidden)
        self.assertTrue(result.private_account_data_ingestion_forbidden)
        self.assertTrue(result.order_creation_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_blocks_top_quality_candidate_without_executable_amount_and_selects_next(self) -> None:
        ranking = _ranking([_score("hype", total_score=90.0), _score("btc", total_score=80.0)])
        allocation = {
            "ideal_allocations_cents": {"hype": 1000, "btc": 2000},
            "executable_allocations_cents": {"hype": 0, "btc": 4154},
        }

        result = build_expanded_crypto_ranking_daily_operator_bridge(
            daily_readiness_result=_daily(),
            crypto_ranking_result=ranking,
            allocation_result=allocation,
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.selected_crypto_candidate, "btc")
        self.assertEqual(result.selected_crypto_amount_eur, 41.54)
        self.assertEqual(result.candidate_decisions[0].decision_status, DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET)
        self.assertEqual(result.candidate_decisions[1].decision_status, DECISION_SELECTED)

    def test_platform_blocked_candidate_is_not_selected(self) -> None:
        ranking = _ranking([_score("tao", total_score=90.0, platform_ready=False), _score("btc", total_score=80.0)])
        allocation = {
            "ideal_allocations_cents": {"tao": 1000, "btc": 2000},
            "executable_allocations_cents": {"tao": 1000, "btc": 2000},
        }

        result = build_expanded_crypto_ranking_daily_operator_bridge(
            daily_readiness_result=_daily(),
            crypto_ranking_result=ranking,
            allocation_result=allocation,
        )

        self.assertEqual(result.selected_crypto_candidate, "btc")
        self.assertEqual(result.candidate_decisions[0].decision_status, DECISION_BLOCKED_BY_PLATFORM)

    def test_incomplete_expanded_crypto_coverage_requires_review(self) -> None:
        ranking = _ranking([_score("btc", total_score=80.0)], ready=False)
        allocation = {
            "ideal_allocations_cents": {"btc": 2000},
            "executable_allocations_cents": {"btc": 2000},
        }

        result = build_expanded_crypto_ranking_daily_operator_bridge(
            daily_readiness_result=_daily(),
            crypto_ranking_result=ranking,
            allocation_result=allocation,
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertFalse(result.expanded_crypto_ranking_ready)
        self.assertFalse(result.full_public_data_coverage)

    def test_console_output_mentions_expanded_crypto_ranking_and_safety(self) -> None:
        ranking = _ranking([_score("btc", total_score=80.0)])
        allocation = {
            "ideal_allocations_cents": {"btc": 2000},
            "executable_allocations_cents": {"btc": 2000},
        }
        result = build_expanded_crypto_ranking_daily_operator_bridge(
            daily_readiness_result=_daily(),
            crypto_ranking_result=ranking,
            allocation_result=allocation,
        )

        output = build_expanded_crypto_ranking_daily_operator_console_output(result)

        self.assertIn("Daily Operator with Expanded Crypto Ranking", output)
        self.assertIn("full public data coverage: True", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no orders created", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()