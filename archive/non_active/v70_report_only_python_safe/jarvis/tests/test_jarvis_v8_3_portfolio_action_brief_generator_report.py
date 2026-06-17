import unittest

from jarvis.jarvis_v8_3_portfolio_action_brief_generator_report import (
    report_v8_3_portfolio_action_brief_generator,
)


class JarvisV83PortfolioActionBriefGeneratorReportTests(unittest.TestCase):
    def test_report_contains_brief_and_safety(self) -> None:
        report = report_v8_3_portfolio_action_brief_generator()

        self.assertIn("J.A.R.V.I.S. v8.3 Portfolio Action Brief Generator", report)
        self.assertIn("status: JARVIS_V8_3_PORTFOLIO_ACTION_BRIEF_GENERATOR_READY_SAFE", report)
        self.assertIn("brief status: PORTFOLIO_ACTION_BRIEF_READY", report)
        self.assertIn("recommended next stage: v8_4_operator_command_center_closeout", report)
        self.assertIn("Portfolio Action Brief", report)
        self.assertIn("creates buy request: False", report)
        self.assertIn("connects broker: False", report)
        self.assertIn("places order: False", report)
        self.assertIn("executes trade: False", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
