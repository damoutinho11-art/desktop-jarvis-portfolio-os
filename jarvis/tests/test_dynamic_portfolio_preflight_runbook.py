import unittest
from pathlib import Path


RUNBOOK = Path("docs/JARVIS_DYNAMIC_PORTFOLIO_PREFLIGHT_RUNBOOK.md")


class DynamicPortfolioPreflightRunbookTests(unittest.TestCase):
    def test_runbook_documents_main_command_statuses_and_safety_boundary(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("J.A.R.V.I.S. Dynamic Portfolio Preflight Runbook", text)
        self.assertIn("python -m jarvis.dynamic_portfolio_preflight_report", text)
        self.assertIn("DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE", text)
        self.assertIn("DYNAMIC_PORTFOLIO_PREFLIGHT_BLOCKED_SAFE", text)
        self.assertIn("DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE", text)
        self.assertIn("DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE", text)
        self.assertIn("DYNAMIC_MARKET_COVERAGE_READY_SAFE", text)
        self.assertIn("DYNAMIC_WEEKLY_PLAN_READY_SAFE", text)
        self.assertIn("DYNAMIC_POLICY_READY_SAFE", text)
        self.assertIn("manual approval required: True", text)
        self.assertIn("execution forbidden: True", text)

    def test_runbook_preserves_no_execution_boundary(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        required_phrases = [
            "No execution",
            "must not execute",
            "must not:",
            "fetch market data",
            "connect to a broker",
            "place orders",
            "create buy requests",
            "approve assets",
            "mutate the registry",
            "execute trades",
        ]

        for phrase in required_phrases:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
