from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate import CryptoLanePublicSignalSelectionGateResult
from jarvis.jarvis_v24_0_crypto_lane_selection_daily_operator_bridge_report import main


class JarvisV240CryptoLaneSelectionDailyOperatorBridgeReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution(self) -> None:
        daily = SimpleNamespace(
            status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE",
            readiness_status="STALE_REVIEW_REQUIRED",
            stale_data_review_required=True,
            blockers=(),
            warnings=("portfolio_state is stale",),
        )
        selection = CryptoLanePublicSignalSelectionGateResult(
            status="JARVIS_V23_0_CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY_SAFE",
            gate_status="CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY",
            selected_crypto_candidate="btc",
            selected_crypto_amount_eur=41.54,
            crypto_public_signal_universe_ready=True,
            candidate_count=3,
            eligible_candidate_count=1,
            blocked_candidate_count=2,
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

        with patch(
            "jarvis.jarvis_v24_0_crypto_lane_selection_daily_operator_bridge.build_real_daily_readiness_gate",
            return_value=daily,
        ), patch(
            "jarvis.jarvis_v24_0_crypto_lane_selection_daily_operator_bridge.build_crypto_lane_public_signal_selection_gate_result",
            return_value=selection,
        ):
            exit_code = main(["--current-date", "2026-06-17"])

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()