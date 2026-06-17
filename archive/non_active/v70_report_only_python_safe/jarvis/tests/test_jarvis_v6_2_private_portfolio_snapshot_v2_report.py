import unittest

from jarvis.jarvis_v6_2_private_portfolio_snapshot_v2_report import (
    report_v6_2_private_portfolio_snapshot_v2,
)


class JarvisV62PrivatePortfolioSnapshotV2ReportTests(unittest.TestCase):
    def test_report_contains_snapshot_cash_roles_and_safety(self) -> None:
        report = report_v6_2_private_portfolio_snapshot_v2()

        self.assertIn("J.A.R.V.I.S. v6.2 Private Portfolio Snapshot v2", report)
        self.assertIn("status: JARVIS_V6_2_PRIVATE_PORTFOLIO_SNAPSHOT_V2_READY_SAFE", report)
        self.assertIn("recommended next stage: v6.3_universal_asset_candidate_registry", report)
        self.assertIn("investable cash EUR: 350.0", report)
        self.assertIn("protected cash EUR: 5900.0", report)
        self.assertIn("daily_bank", report)
        self.assertIn("emergency_fund", report)
        self.assertIn("investment_brokerage", report)
        self.assertIn("crypto_exchange", report)
        self.assertIn("cash_buffer", report)
        self.assertIn("global_all_world_etf_placeholder", report)
        self.assertIn("btc", report)
        self.assertIn("hype", report)
        self.assertIn("tao", report)
        self.assertIn("local private data only: True", report)
        self.assertIn("broker API forbidden: True", report)
        self.assertIn("broker execution forbidden: True", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
