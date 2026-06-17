from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.jarvis_v25_0_daily_approval_ticket_refresh_builder_report import main


class JarvisV250DailyApprovalTicketRefreshBuilderReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution(self) -> None:
        fake_result = SimpleNamespace(
            status="JARVIS_V25_0_DAILY_APPROVAL_TICKET_REFRESH_BUILDER_REVIEW_REQUIRED_SAFE",
            builder_status="DAILY_APPROVAL_TICKET_REFRESH_BUILDER_REVIEW_REQUIRED",
            current_date="2026-06-17",
            output_path="outputs/approval_ticket_latest.json",
            approval_ticket_written=False,
            selected_crypto_candidate="btc",
            selected_crypto_amount_eur=41.54,
            selected_stock_fund_etf_candidate="quality_etf",
            selected_stock_fund_etf_amount_eur=62.31,
            recommendation_quality_current_data=False,
            portfolio_data_stale_review_required=True,
            allocation_mutation=False,
            approval_ticket_mutation=False,
            buy_request_created=False,
            broker_connection_forbidden=True,
            credentials_forbidden=True,
            private_account_data_ingestion_forbidden=True,
            order_creation_forbidden=True,
            no_trades_executed=True,
            blockers=(),
            warnings=("portfolio_state is stale",),
            approval_ticket={"as_of": "2026-06-17", "buy_request_created": False},
            to_dict=lambda: {"status": "fake"},
        )

        with patch(
            "jarvis.jarvis_v25_0_daily_approval_ticket_refresh_builder_report.build_daily_approval_ticket_refresh_builder_result",
            return_value=fake_result,
        ):
            exit_code = main(["--current-date", "2026-06-17"])

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()