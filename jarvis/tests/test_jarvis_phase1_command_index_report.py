import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_phase1_command_index_report import build_report_from_path, load_command_index


COMMAND_INDEX = "jarvis/data/jarvis_phase1_command_index.example.json"
STAGE_IDS = [f"v4.{version}" for version in range(27, 48)]


class JarvisPhase1CommandIndexReportTests(unittest.TestCase):
    def test_static_data_includes_v4_27_through_v4_47_stages(self) -> None:
        data = load_command_index(COMMAND_INDEX)
        stage_ids = [stage["id"] for stage in data["stages"]]

        self.assertEqual(stage_ids, STAGE_IDS)

    def test_report_includes_every_stage_and_v4_47_final_audit_command(self) -> None:
        report = build_report_from_path(COMMAND_INDEX)

        for stage_id in STAGE_IDS:
            self.assertIn(stage_id, report)
        self.assertIn("python -m jarvis.ftaw_final_real_pipeline_audit_report", report)

    def test_report_includes_phase_1_complete_and_final_audit_statuses(self) -> None:
        report = build_report_from_path(COMMAND_INDEX)

        self.assertIn("Phase 1 backend gate chain is complete.", report)
        for status in (
            "FINAL_REAL_PIPELINE_BLOCKED_SAFE",
            "FINAL_REAL_PIPELINE_PARTIAL_SAFE",
            "FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE",
        ):
            self.assertIn(status, report)

    def test_report_includes_safety_non_execution_statements(self) -> None:
        report = build_report_from_path(COMMAND_INDEX)

        for phrase in (
            "no executor",
            "no mutation",
            "no registry mutation",
            "no approved asset automatically",
            "no allocation recommendation",
            "no buy signal",
            "no trade executed",
            "no broker/authenticated APIs",
            "no credentials",
            "no private file auto-ingest",
            "no automatic source fetching/downloads/extraction",
        ):
            self.assertIn(phrase, report)

    def test_helper_is_import_safe(self) -> None:
        module = importlib.import_module("jarvis.jarvis_phase1_command_index_report")

        self.assertTrue(hasattr(module, "build_report_from_path"))

    def test_helper_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(COMMAND_INDEX)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("J.A.R.V.I.S. Phase 1 Command Index", report)
        self.assertEqual(before, after)

    def test_helper_does_not_claim_authorization(self) -> None:
        report = build_report_from_path(COMMAND_INDEX).lower()

        for forbidden in (
            "promotion is authorized",
            "approval is authorized",
            "execution is authorized",
            "allocation is authorized",
            "buy/sell is authorized",
            "trading is authorized",
        ):
            self.assertNotIn(forbidden, report)
        self.assertIn("does not claim promotion, approval, execution, allocation, buy/sell, or trading authorization", report)

    def test_cli_default_and_explicit_input_run(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_phase1_command_index_report"],
            [sys.executable, "-m", "jarvis.jarvis_phase1_command_index_report", "--input", COMMAND_INDEX],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("Phase 1 backend gate chain is complete.", result.stdout)
                self.assertIn("v4.47", result.stdout)


if __name__ == "__main__":
    unittest.main()
