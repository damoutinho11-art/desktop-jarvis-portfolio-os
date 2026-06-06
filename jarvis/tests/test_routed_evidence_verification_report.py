import subprocess
import sys
import unittest

from jarvis.routed_evidence_verification_report import build_routed_evidence_verification_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"
CONFIG = "jarvis/data/routed_evidence_verification_pack.example.json"


class RoutedEvidenceVerificationReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_routed_evidence_verification_report(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertIn("verification pack status:", report)
        self.assertIn("target asset: vwce_global_core_candidate", report)
        self.assertIn("required evidence types:", report)
        self.assertIn("pending verification tasks count:", report)
        self.assertIn("missing evidence types:", report)
        self.assertIn("selected source per evidence type:", report)
        self.assertIn("recommended decision per evidence type:", report)
        self.assertIn("accepted preview count:", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.routed_evidence_verification_report",
                REGISTRY,
                PUBLIC_SOURCES,
                CONFIG,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Routed Evidence Verification Pack Report", completed.stdout)

    def test_report_prints_vwce_strictness_recommendations(self) -> None:
        report = build_routed_evidence_verification_report(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertIn("- platform_availability: needs_correction", report)
        self.assertIn("- market_data: needs_correction", report)
        self.assertIn("- fund_metadata: accept", report)


if __name__ == "__main__":
    unittest.main()
