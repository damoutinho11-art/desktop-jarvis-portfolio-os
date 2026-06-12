import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_watchlist_entry_report import build_report_from_path


DEFAULT_WATCHLIST = "jarvis/data/jarvis_manual_candidate_watchlist_entry.example.json"
SYNTHETIC_MULTI = "jarvis/data/jarvis_manual_candidate_watchlist_entry.synthetic_multi.example.json"


class ManualCandidateWatchlistEntryReportTests(unittest.TestCase):
    def test_report_includes_route_chain(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        self.assertIn("v4.50 manual watchlist entry -> v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline", report)

    def test_report_includes_safety_non_execution_statements(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        for phrase in (
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
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
        report = build_report_from_path(SYNTHETIC_MULTI).lower()

        for forbidden in (
            "approval is authorized",
            "trust is authorized",
            "investability is authorized",
            "verification is authorized",
            "promotion is authorized",
            "allocation is authorized",
            "portfolio weight is authorized",
            "buy/sell is authorized",
            "trade is authorized",
            "registry mutation is authorized",
            "broker api use is authorized",
            "credential use is authorized",
            "private ingest is authorized",
            "fetching/downloads are authorized",
            "executor is authorized",
        ):
            self.assertNotIn(forbidden, report)
        self.assertIn("does not claim approval, trust, investability, verification, promotion, allocation, portfolio weight, buy/sell, trade, registry mutation, broker api use, credential use, private ingest, fetching/downloads, or executor authorization", report)

    def test_cli_default_and_input_work(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_manual_candidate_watchlist_entry_report"],
            [sys.executable, "-m", "jarvis.jarvis_manual_candidate_watchlist_entry_report", "--input", SYNTHETIC_MULTI],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("watchlist entry count:", result.stdout)

    def test_module_import_is_safe(self) -> None:
        module = importlib.import_module("jarvis.jarvis_manual_candidate_watchlist_entry_report")

        self.assertTrue(hasattr(module, "build_report_from_path"))

    def test_report_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(SYNTHETIC_MULTI)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("Manual watchlist entry is record-only", report)
        self.assertEqual(before, after)

    def test_report_shows_entry_statuses_and_preview(self) -> None:
        report = build_report_from_path(SYNTHETIC_MULTI)

        self.assertIn("MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE", report)
        self.assertIn("MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE", report)
        self.assertIn("MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE", report)
        self.assertIn("candidate intake preview:", report)


if __name__ == "__main__":
    unittest.main()
