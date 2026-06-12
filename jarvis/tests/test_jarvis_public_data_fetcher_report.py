import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_public_data_fetcher_report import build_report_from_path


DEFAULT_CONFIG = "jarvis/data/jarvis_public_data_fetcher.example.json"
SYNTHETIC_PLAN = "jarvis/data/jarvis_public_data_fetcher.synthetic_plan.example.json"


class PublicDataFetcherReportTests(unittest.TestCase):
    def test_report_includes_frequency_raw_unverified_route_and_safety(self) -> None:
        report = build_report_from_path(SYNTHETIC_PLAN)

        for phrase in (
            "Daily updates are preferred for market/reference freshness.",
            "Weekly updates are acceptable for low-volatility metadata.",
            "Fetched data is raw/unverified local cache only when explicitly authorized.",
            "No evidence verification occurred.",
            "No broker/authenticated API or credentials are used.",
            "v4.56 manual candidate data entry workspace -> v4.57 public data fetcher local cache control plane",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no verified evidence promotion",
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
            "no automatic evidence extraction",
            "fetched data ignored from git/local cache only when explicitly authorized",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_authorization(self) -> None:
        report = build_report_from_path(SYNTHETIC_PLAN).lower()

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

    def test_cli_default_and_input_work_without_network_write(self) -> None:
        for command in (
            [sys.executable, "-m", "jarvis.jarvis_public_data_fetcher_report"],
            [sys.executable, "-m", "jarvis.jarvis_public_data_fetcher_report", "--input", SYNTHETIC_PLAN],
            [
                sys.executable,
                "-m",
                "jarvis.jarvis_public_data_fetcher_report",
                "--input",
                DEFAULT_CONFIG,
                "--manifest",
                "templates/jarvis_public_data_sources.local.template.json",
            ],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.assertIn("overall status:", result.stdout)
                self.assertIn("Default mode is dry-run/no-network/no-write.", result.stdout)

    def test_module_import_is_safe_and_default_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_public_data_fetcher_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(SYNTHETIC_PLAN)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("PUBLIC_DATA_FETCHER_PLAN_READY_SAFE", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
