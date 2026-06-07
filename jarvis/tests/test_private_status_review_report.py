import subprocess
import sys
import unittest

from jarvis.private_status_review_report import build_private_status_review_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
CONFIG = "jarvis/data/private_status_review_bridge.example.json"


class PrivateStatusReviewReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_private_status_review_report(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertIn("private status review bridge status:", report)
        self.assertIn("verified eligible assets count:", report)
        self.assertIn("freshness-passing assets count:", report)
        self.assertIn("generated request previews count:", report)
        self.assertIn("requested transitions:", report)
        self.assertIn("blocked assets:", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.private_status_review_report",
                REGISTRY,
                PRIVATE_INTAKE,
                POLICY,
                CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Private Status Review Bridge Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
