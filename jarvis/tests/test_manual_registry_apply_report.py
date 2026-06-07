import subprocess
import sys
import unittest

from jarvis.manual_registry_apply_report import build_manual_registry_apply_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
PRIVATE_STATUS_CONFIG = "jarvis/data/private_status_review_bridge.example.json"
PRIVATE_DRY_RUN_CONFIG = "jarvis/data/private_registry_dry_run_bridge.example.json"
APPLY_CONFIG = "jarvis/data/manual_registry_apply_pack.example.json"


class ManualRegistryApplyReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_manual_registry_apply_report(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG, APPLY_CONFIG
        )

        self.assertIn("manual registry apply pack status:", report)
        self.assertIn("target asset:", report)
        self.assertIn("current_status:", report)
        self.assertIn("requested_status:", report)
        self.assertIn("apply_allowed:", report)
        self.assertIn("output_path:", report)
        self.assertIn("required confirmations:", report)
        self.assertIn("diff summary:", report)
        self.assertIn("default write performed: false", report)
        self.assertIn("no approved_investable: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.manual_registry_apply_report",
                REGISTRY,
                PRIVATE_INTAKE,
                POLICY,
                PRIVATE_STATUS_CONFIG,
                PRIVATE_DRY_RUN_CONFIG,
                APPLY_CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Manual Registry Apply Approval Pack Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
