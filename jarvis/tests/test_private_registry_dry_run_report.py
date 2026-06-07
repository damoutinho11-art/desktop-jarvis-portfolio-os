import subprocess
import sys
import unittest

from jarvis.private_registry_dry_run_report import build_private_registry_dry_run_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
PRIVATE_STATUS_CONFIG = "jarvis/data/private_status_review_bridge.example.json"
PRIVATE_DRY_RUN_CONFIG = "jarvis/data/private_registry_dry_run_bridge.example.json"


class PrivateRegistryDryRunReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_private_registry_dry_run_report(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertIn("private registry dry-run bridge status:", report)
        self.assertIn("request previews count:", report)
        self.assertIn("simulated updates count:", report)
        self.assertIn("blocked requests count:", report)
        self.assertIn("requested transitions:", report)
        self.assertIn("diff summary:", report)
        self.assertIn("registry mutation performed: false", report)
        self.assertIn("No approvals executed.", report)
        self.assertIn("No buy/sell requests created.", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.private_registry_dry_run_report",
                REGISTRY,
                PRIVATE_INTAKE,
                POLICY,
                PRIVATE_STATUS_CONFIG,
                PRIVATE_DRY_RUN_CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Private Registry Dry-Run Bridge Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
