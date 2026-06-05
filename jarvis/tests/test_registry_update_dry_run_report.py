import subprocess
import sys
import unittest

from jarvis.registry_update_dry_run_report import build_registry_update_dry_run_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
BRIDGE_CONFIG = "jarvis/data/real_status_review_bridge.example.json"
DRY_RUN_CONFIG = "jarvis/data/registry_update_dry_run.example.json"


class RegistryUpdateDryRunReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_registry_update_dry_run_report(REGISTRY, BRIDGE_CONFIG)

        self.assertIn("dry-run status:", report)
        self.assertIn("total request previews:", report)
        self.assertIn("simulated updates count:", report)
        self.assertIn("blocked requests count:", report)
        self.assertIn("registry mutation performed: false", report)
        self.assertIn("No approvals executed.", report)
        self.assertIn("No buy/sell requests created.", report)
        self.assertIn("No trades executed.", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.registry_update_dry_run_report",
                REGISTRY,
                BRIDGE_CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Registry Update Dry-Run Report", completed.stdout)

    def test_bundled_dry_run_example_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.registry_update_dry_run_report",
                REGISTRY,
                DRY_RUN_CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("total request previews: 0", completed.stdout)
        self.assertIn("simulated updates count: 0", completed.stdout)


if __name__ == "__main__":
    unittest.main()
