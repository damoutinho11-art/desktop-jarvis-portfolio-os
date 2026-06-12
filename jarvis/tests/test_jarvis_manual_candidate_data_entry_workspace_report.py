import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_data_entry_workspace_report import build_report_from_path


DEFAULT_WORKSPACE = "jarvis/data/jarvis_manual_candidate_data_entry_workspace.example.json"


class ManualCandidateDataEntryWorkspaceReportTests(unittest.TestCase):
    def test_report_includes_next_action_route_warnings_and_safety(self) -> None:
        report = build_report_from_path(DEFAULT_WORKSPACE)

        self.assertIn("No more candidate-intake gates are being added.", report)
        self.assertIn("manual_candidate_watchlist_data_entry_only", report)
        self.assertIn(
            "v4.56 manual candidate data entry workspace -> v4.50 manual watchlist entry -> "
            "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence/manual review pipeline",
            report,
        )
        for phrase in (
            "do not commit local candidate watchlists",
            "do not commit account data",
            "do not commit credentials",
            "do not commit broker data",
            "do not commit private files/screenshots/PDFs",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence collection started",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no packet file persisted",
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
        report = build_report_from_path(DEFAULT_WORKSPACE).lower()

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
            "candidate intake file write is authorized",
            "packet persistence is authorized",
            "broker api use is authorized",
            "credential use is authorized",
            "private ingest is authorized",
            "fetching/downloads are authorized",
            "executor is authorized",
        ):
            self.assertNotIn(forbidden, report)

    def test_cli_default_and_input_work(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_manual_candidate_data_entry_workspace_report"],
            [
                sys.executable,
                "-m",
                "jarvis.jarvis_manual_candidate_data_entry_workspace_report",
                "--input",
                DEFAULT_WORKSPACE,
            ],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("No more candidate-intake gates are being added.", result.stdout)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_manual_candidate_data_entry_workspace_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_WORKSPACE)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("Manual Candidate Data Entry Workspace", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
