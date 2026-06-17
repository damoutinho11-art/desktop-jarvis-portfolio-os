import unittest

from jarvis.jarvis_v14_0_daily_operator_entrypoint import run_v14_0_daily_operator_entrypoint
from jarvis.jarvis_v14_0_daily_operator_entrypoint_report import (
    build_v14_0_daily_operator_entrypoint_report,
)
from jarvis.tests.test_jarvis_v14_0_daily_operator_entrypoint import _launcher_runner


class JarvisV140DailyOperatorEntrypointReportTests(unittest.TestCase):
    def test_report_contains_daily_use_and_safety(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="daily",
            launcher_runner=_launcher_runner(),
        )
        report = build_v14_0_daily_operator_entrypoint_report(result)

        self.assertIn("J.A.R.V.I.S. v14.0 Daily Operator Entrypoint", report)
        self.assertIn("status: JARVIS_V14_0_DAILY_OPERATOR_ENTRYPOINT_READY_SAFE", report)
        self.assertIn("entrypoint status: DAILY_OPERATOR_ENTRYPOINT_READY", report)
        self.assertIn("short root command available: True", report)
        self.assertIn("daily mode available: True", report)
        self.assertIn("safety check mode available: True", report)
        self.assertIn("no strategy rebuild: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
