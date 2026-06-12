import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_candidate_intake_report import build_report_from_path


DEFAULT_INTAKE = "jarvis/data/jarvis_candidate_intake.example.json"
SYNTHETIC_MULTI = "jarvis/data/jarvis_candidate_intake.synthetic_multi.example.json"


class JarvisCandidateIntakeReportTests(unittest.TestCase):
    def test_report_includes_route_to_v4_27_through_v4_47_pipeline(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        self.assertIn("v4.27 real evidence intake readiness", report)
        self.assertIn("v4.47 final real pipeline audit report", report)

    def test_report_includes_safety_non_execution_statements(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        for phrase in (
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no registry mutation",
            "no allocation recommendation",
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no automatic fetching/downloads/extraction",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_authorization(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI).lower()

        for forbidden in (
            "approval is authorized",
            "trust is authorized",
            "investability is authorized",
            "allocation is authorized",
            "buy/sell is authorized",
            "trade is authorized",
            "registry mutation is authorized",
            "execution is authorized",
        ):
            self.assertNotIn(forbidden, report)
        self.assertIn("does not claim approval, trust, investability, allocation, buy/sell, trade, registry mutation, or execution authorization", report)

    def test_cli_default_and_input_work(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_candidate_intake_report"],
            [sys.executable, "-m", "jarvis.jarvis_candidate_intake_report", "--input", SYNTHETIC_MULTI],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("J.A.R.V.I.S.", result.stdout)
                self.assertIn("overall status:", result.stdout)

    def test_module_import_is_safe(self) -> None:
        module = importlib.import_module("jarvis.jarvis_candidate_intake_report")

        self.assertTrue(hasattr(module, "build_report_from_path"))

    def test_report_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(SYNTHETIC_MULTI)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("Candidate intake is record-only", report)
        self.assertEqual(before, after)

    def test_report_shows_candidate_statuses(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        self.assertIn("CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE", report)
        self.assertIn("CANDIDATE_INTAKE_BLOCKED_SAFE", report)
        self.assertIn("CANDIDATE_INTAKE_PARTIAL_SAFE", report)


if __name__ == "__main__":
    unittest.main()
