import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_phase2_candidate_intake_chain_audit_report import build_report_from_path


DEFAULT_AUDIT = "jarvis/data/jarvis_phase2_candidate_intake_chain_audit.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_phase2_candidate_intake_chain_audit.synthetic_complete.example.json"


class Phase2CandidateIntakeChainAuditReportTests(unittest.TestCase):
    def test_report_includes_stop_recommendation_next_action_route_and_safety(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE)

        self.assertIn("no more candidate-intake gates recommended now", report)
        self.assertIn("manual_candidate_watchlist_data_entry_only", report)
        self.assertIn(
            "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
            "v4.52 manual candidate intake review decision -> "
            "v4.53 explicit dry-run packet command contract -> "
            "v4.54 candidate intake packet dry-run builder -> "
            "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline",
            report,
        )
        self.assertIn("VWCE and FTAW were pilot anchors only", report)
        for phrase in (
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
        report = build_report_from_path(SYNTHETIC_COMPLETE).lower()

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
            [sys.executable, "-m", "jarvis.jarvis_phase2_candidate_intake_chain_audit_report"],
            [
                sys.executable,
                "-m",
                "jarvis.jarvis_phase2_candidate_intake_chain_audit_report",
                "--input",
                SYNTHETIC_COMPLETE,
            ],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("Phase 2 Candidate-Intake Chain Summary", result.stdout)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_phase2_candidate_intake_chain_audit_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_AUDIT)
            after = set(Path(tmpdir).iterdir())
        self.assertIn("Phase 2 Candidate Intake Chain Audit", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
