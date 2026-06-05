import subprocess
import sys
import unittest

from jarvis.verified_evidence_promotion_report import build_verified_evidence_promotion_report


class VerifiedEvidencePromotionReportTests(unittest.TestCase):
    def test_report_contains_required_sections(self) -> None:
        report = build_verified_evidence_promotion_report(
            "jarvis/data/candidate_assets.v2.example.json",
            "jarvis/data/source_evidence_sources.example.json",
            "jarvis/data/verified_evidence_promotion.example.json",
        )

        self.assertIn("promotion pack status", report)
        self.assertIn("total verification tasks:", report)
        self.assertIn("accepted count:", report)
        self.assertIn("verified evidence preview count:", report)
        self.assertIn("assets ready for real status review:", report)
        self.assertIn("no approvals created: true", report)

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.verified_evidence_promotion_report",
                "jarvis/data/candidate_assets.v2.example.json",
                "jarvis/data/source_evidence_sources.example.json",
                "jarvis/data/verified_evidence_promotion.example.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Verified Evidence Promotion Pack Report", result.stdout)
        self.assertIn("no registry mutation: true", result.stdout)
        self.assertIn("no trades executed: true", result.stdout)


if __name__ == "__main__":
    unittest.main()
