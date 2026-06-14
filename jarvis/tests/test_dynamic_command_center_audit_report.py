import unittest

from jarvis.dynamic_command_center_audit_report import report_dynamic_command_center_audit


POLICY = "jarvis/data/portfolio_policy.example.json"
REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"
PLAN = "jarvis/data/private/personal_weekly_contribution.local.json"
SNAPSHOT = "jarvis/data/private/personal_snapshot.local.json"


class DynamicCommandCenterAuditReportTests(unittest.TestCase):
    def test_report_contains_ready_chain_commands_and_safety(self) -> None:
        report = report_dynamic_command_center_audit(
            "20y", PLAN, SNAPSHOT, POLICY, REGISTRY, BINDINGS, MARKET_DATA
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Portfolio Command Center Audit", report)
        self.assertIn("status: DYNAMIC_COMMAND_CENTER_AUDIT_READY_SAFE", report)
        self.assertIn("dashboard status: DYNAMIC_OPERATOR_STATUS_READY_SAFE", report)
        self.assertIn("ready status count: 8", report)
        self.assertIn("python -m jarvis.dynamic_operator_status_dashboard_report", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
