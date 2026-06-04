import subprocess
import sys
import unittest

from jarvis.asset_status_audit import build_asset_status_audit_report


class AssetStatusAuditTests(unittest.TestCase):
    def test_audit_report_contains_status_summary(self) -> None:
        report = build_asset_status_audit_report("jarvis/data/asset_status_requests.example.json")

        self.assertIn("J.A.R.V.I.S. Asset Status Change Audit", report)
        self.assertIn("valid requests: 2", report)
        self.assertIn("blocked requests: 1", report)
        self.assertIn("No registry files modified.", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.asset_status_audit", "jarvis/data/asset_status_requests.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("allowed_transition", result.stdout)
        self.assertIn("manual_approval_required", result.stdout)


if __name__ == "__main__":
    unittest.main()
