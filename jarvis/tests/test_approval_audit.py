import subprocess
import sys
import unittest

from jarvis.approval_audit import build_approval_audit_report


class ApprovalAuditTests(unittest.TestCase):
    def test_audit_report_contains_summary(self) -> None:
        report = build_approval_audit_report("jarvis/data/approval_requests.example.json")

        self.assertIn("J.A.R.V.I.S. Manual Approval Audit", report)
        self.assertIn("total requests: 3", report)
        self.assertIn("blocked requests: 1", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.approval_audit", "jarvis/data/approval_requests.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("valid pending requests", result.stdout)
        self.assertIn("req_valid_buy_example", result.stdout)


if __name__ == "__main__":
    unittest.main()
