from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate import CryptoLanePublicSignalSelectionGateResult
from jarvis.jarvis_v24_0_crypto_lane_selection_daily_operator_bridge import (
    STATUS_REVIEW_REQUIRED,
    build_crypto_lane_selection_daily_operator_bridge,
    build_crypto_lane_selection_daily_operator_console_output,
)


def _daily_readiness() -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE",
        readiness_status="STALE_REVIEW_REQUIRED",
        stale_data_review_required=True,
        blockers=(),
        warnings=("portfolio_state is stale",),
    )


def _selection_result(selected: str | None = "btc") -> CryptoLanePublicSignalSelectionGateResult:
    return CryptoLanePublicSignalSelectionGateResult(
        status="JARVIS_V23_0_CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY_SAFE" if selected else "JARVIS_V23_0_CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_REVIEW_REQUIRED_SAFE",
        gate_status="CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY" if selected else "CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_REVIEW_REQUIRED",
        selected_crypto_candidate=selected,
        selected_crypto_amount_eur=41.54 if selected else 0.0,
        crypto_public_signal_universe_ready=True,
        candidate_count=3,
        eligible_candidate_count=1 if selected else 0,
        blocked_candidate_count=2 if selected else 3,
        current_date="2026-06-17",
        recommended_next_stage="crypto_lane_public_signal_scoring_integration",
        candidate_decisions=tuple(),
        blockers=tuple(),
        warnings=tuple(),
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


class JarvisV240CryptoLaneSelectionDailyOperatorBridgeTests(unittest.TestCase):
    def test_daily_operator_surfaces_v23_selected_crypto_without_mutation(self) -> None:
        result = build_crypto_lane_selection_daily_operator_bridge(
            daily_readiness_result=_daily_readiness(),
            crypto_selection_result=_selection_result("btc"),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.selected_crypto_candidate, "btc")
        self.assertEqual(result.selected_crypto_amount_eur, 41.54)
        self.assertTrue(result.crypto_selection_ready)
        self.assertFalse(result.recommendation_quality_current_data)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.credentials_forbidden)
        self.assertTrue(result.private_account_data_ingestion_forbidden)
        self.assertTrue(result.order_creation_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_daily_operator_warns_when_no_crypto_selection(self) -> None:
        result = build_crypto_lane_selection_daily_operator_bridge(
            daily_readiness_result=_daily_readiness(),
            crypto_selection_result=_selection_result(None),
        )

        self.assertFalse(result.crypto_selection_ready)
        self.assertIn("No crypto candidate was selected", " ".join(result.warnings))

    def test_console_output_uses_crypto_lane_selection_not_btc_only_label(self) -> None:
        result = build_crypto_lane_selection_daily_operator_bridge(
            daily_readiness_result=_daily_readiness(),
            crypto_selection_result=_selection_result("btc"),
        )
        output = build_crypto_lane_selection_daily_operator_console_output(result)

        self.assertIn("Daily Operator with Crypto-Lane Selection", output)
        self.assertIn("selected crypto candidate: btc", output)
        self.assertIn("Crypto-lane selection:", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)
        self.assertNotIn("BTC signal:", output)


if __name__ == "__main__":
    unittest.main()