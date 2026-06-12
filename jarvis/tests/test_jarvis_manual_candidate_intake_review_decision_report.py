import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_intake_review_decision_report import build_report_from_path


DEFAULT_DECISION = "jarvis/data/jarvis_manual_candidate_intake_review_decision.example.json"
SYNTHETIC_DEFER = "jarvis/data/jarvis_manual_candidate_intake_review_decision.synthetic_defer.example.json"
SYNTHETIC_ACCEPT = "jarvis/data/jarvis_manual_candidate_intake_review_decision.synthetic_accept.example.json"


class ManualCandidateIntakeReviewDecisionReportTests(unittest.TestCase):
    def test_report_includes_route_chain_no_write_and_safety(self) -> None:
        report = build_report_from_path(SYNTHETIC_ACCEPT)

        self.assertIn(
            "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
            "v4.52 manual candidate intake review decision -> future explicit dry-run candidate intake packet -> "
            "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline",
            report,
        )
        self.assertIn("no candidate intake file was written", report)
        for phrase in (
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence collection started",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic fetching/downloads/extraction",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_authorization(self) -> None:
        report = build_report_from_path(SYNTHETIC_ACCEPT).lower()

        for forbidden in (
            "approval is authorized",
            "trust is authorized",
            "investability is authorized",
            "evidence collection is authorized",
            "verification is authorized",
            "promotion is authorized",
            "allocation is authorized",
            "portfolio weight is authorized",
            "buy/sell is authorized",
            "trade is authorized",
            "registry mutation is authorized",
            "candidate registry write is authorized",
            "broker api use is authorized",
            "credential use is authorized",
            "private ingest is authorized",
            "fetching/downloads are authorized",
            "executor is authorized",
        ):
            self.assertNotIn(forbidden, report)

    def test_cli_default_and_inputs_work(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_manual_candidate_intake_review_decision_report"],
            [
                sys.executable,
                "-m",
                "jarvis.jarvis_manual_candidate_intake_review_decision_report",
                "--input",
                SYNTHETIC_DEFER,
            ],
            [
                sys.executable,
                "-m",
                "jarvis.jarvis_manual_candidate_intake_review_decision_report",
                "--input",
                SYNTHETIC_ACCEPT,
            ],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("no candidate intake file was written", result.stdout)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_manual_candidate_intake_review_decision_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_DECISION)
            after = set(Path(tmpdir).iterdir())
        self.assertIn("Manual Candidate Intake Review Decision", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
