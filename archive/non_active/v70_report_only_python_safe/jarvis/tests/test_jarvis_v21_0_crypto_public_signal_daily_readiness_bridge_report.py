import unittest

from jarvis.jarvis_v21_0_crypto_public_signal_daily_readiness_bridge_report import build_report_markdown


class JarvisV210CryptoPublicSignalDailyReadinessBridgeReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution(self):
        markdown = build_report_markdown(current_date="2026-06-17")

        self.assertIn("J.A.R.V.I.S. v21.0 Crypto Public Signal Daily Readiness Bridge", markdown)
        self.assertIn("crypto public signal ready:", markdown)
        self.assertIn("allocation mutation: False", markdown)
        self.assertIn("buy request created: False", markdown)
        self.assertIn("no trades executed", markdown)


if __name__ == "__main__":
    unittest.main()