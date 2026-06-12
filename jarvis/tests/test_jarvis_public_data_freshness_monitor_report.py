import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_public_data_freshness_monitor_report import build_report_from_path


DEFAULT_CONFIG = "jarvis/data/jarvis_public_data_freshness_monitor.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_data_freshness_monitor.synthetic_complete.example.json"


class PublicDataFreshnessMonitorReportTests(unittest.TestCase):
    def test_report_includes_no_network_stale_action_verification_warning_and_safety(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE)

        for phrase in (
            "no network: true",
            "This monitor is report-only: no network calls, no fetching, and no downloading occurred.",
            "run_v4_57_explicit_public_fetch_local_cache_only",
            "Freshness is not verification.",
            "Raw cached data remains unverified",
            "no fetching",
            "no downloading",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no registry file written",
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
            "no automatic private data ingest",
            "no fetched data committed",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_authorization(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE).lower()

        for forbidden in (
            "evidence verification is authorized",
            "approval is authorized",
            "trust is authorized",
            "investability is authorized",
            "allocation is authorized",
            "buy/sell is authorized",
            "trade is authorized",
            "registry mutation is authorized",
            "candidate registry write is authorized",
            "broker api use is authorized",
            "credential use is authorized",
            "private ingest is authorized",
            "automatic evidence extraction is authorized",
            "executor is authorized",
        ):
            self.assertNotIn(forbidden, report)

    def test_cli_default_and_input_work(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_public_data_freshness_monitor_report"],
            [sys.executable, "-m", "jarvis.jarvis_public_data_freshness_monitor_report", "--input", SYNTHETIC_COMPLETE],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("no network", result.stdout)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_public_data_freshness_monitor_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_CONFIG)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("PUBLIC_DATA_FRESHNESS_MONITOR_PARTIAL_SAFE", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
