import unittest

from jarvis.dynamic_operator_status_dashboard_report import report_dynamic_operator_status


POLICY = "jarvis/data/portfolio_policy.example.json"
REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"
PLAN = "jarvis/data/private/personal_weekly_contribution.local.json"
SNAPSHOT = "jarvis/data/private/personal_snapshot.local.json"


class DynamicOperatorStatusDashboardReportTests(unittest.TestCase):
    def test_report_contains_ready_chain_and_safety_boundary(self) -> None:
        report = report_dynamic_operator_status(
            "20y", PLAN, SNAPSHOT, POLICY, REGISTRY, BINDINGS, MARKET_DATA
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Operator Status Dashboard", report)
        self.assertIn("status: DYNAMIC_OPERATOR_STATUS_BLOCKED_SAFE", report)
        self.assertIn("- market import plan: DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE", report)
        self.assertIn("- market data intake: DYNAMIC_MARKET_DATA_INTAKE_READY_SAFE", report)
        self.assertIn("- source quality: DYNAMIC_MARKET_DATA_SOURCE_QUALITY_BLOCKED_SAFE", report)
        self.assertIn("- portfolio preflight: DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE", report)
        self.assertIn("- optimizer: DYNAMIC_POLICY_READY_SAFE", report)
        self.assertIn("- weekly plan: DYNAMIC_WEEKLY_PLAN_READY_SAFE", report)
        self.assertIn("- import ready rows: 6", report)
        self.assertIn("- intake ready series: 6", report)
        self.assertIn("- weekly draft plan lines: 6", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
