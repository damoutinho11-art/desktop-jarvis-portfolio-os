import subprocess
import sys
import unittest

from jarvis.evidence_freshness_report import build_evidence_freshness_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"


class EvidenceFreshnessReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_evidence_freshness_report(REGISTRY, PRIVATE_INTAKE, POLICY)

        self.assertIn("freshness report status:", report)
        self.assertIn("target assets checked:", report)
        self.assertIn("fresh count:", report)
        self.assertIn("stale count:", report)
        self.assertIn("missing count:", report)
        self.assertIn("auto-refresh available count:", report)
        self.assertIn("manual refresh required count:", report)
        self.assertIn("account-specific refresh required count:", report)
        self.assertIn("recommended actions by evidence type:", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.evidence_freshness_report",
                REGISTRY,
                PRIVATE_INTAKE,
                POLICY,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Evidence Freshness Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
