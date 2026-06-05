import subprocess
import sys
import unittest

from jarvis.public_draft_evidence_router_report import build_public_draft_evidence_router_report


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"


class PublicDraftEvidenceRouterReportTests(unittest.TestCase):
    def test_report_contains_required_safety_lines(self) -> None:
        report = build_public_draft_evidence_router_report(REGISTRY, PUBLIC_SOURCES)

        self.assertIn("router status:", report)
        self.assertIn("total public source results:", report)
        self.assertIn("routed draft evidence count:", report)
        self.assertIn("routed evidence by asset:", report)
        self.assertIn("routed evidence by evidence type:", report)
        self.assertIn("missing routes:", report)
        self.assertIn("user verification required: true", report)
        self.assertIn("no approvals created: true", report)
        self.assertIn("no registry mutation: true", report)
        self.assertIn("no buy/sell requests: true", report)
        self.assertIn("no trades executed: true", report)

    def test_cli_runs_without_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "jarvis.public_draft_evidence_router_report",
                REGISTRY,
                PUBLIC_SOURCES,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("J.A.R.V.I.S. Public Draft Evidence Router Report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
