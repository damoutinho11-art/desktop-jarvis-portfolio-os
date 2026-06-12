import importlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jarvis.jarvis_local_operator_bootstrap_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_local_operator_bootstrap.example.json"
SYNTHETIC_READY = "jarvis/data/jarvis_local_operator_bootstrap.synthetic_ready.example.json"


class LocalOperatorBootstrapReportTests(unittest.TestCase):
    def test_report_includes_commands_sections_and_safety(self) -> None:
        report = build_report_from_path(SYNTHETIC_READY)

        for phrase in (
            "Commands are documented only and were not executed.",
            "Code did not create local files or directories.",
            "New-Item -ItemType Directory -Force -Path jarvis\\local",
            "Copy-Item templates\\jarvis_manual_candidate_watchlist_entry.local.template.json",
            "Copy-Item templates\\jarvis_public_data_sources.local.template.json",
            "python -m jarvis.jarvis_manual_candidate_data_entry_workspace_report",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "no network calls",
            "no fetching",
            "no downloading",
            "no writes",
            "no directory creation",
            "no template copying by code",
            "no subprocess execution",
            "no scheduler creation",
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
        report = build_report_from_path(SYNTHETIC_READY).lower()

        for forbidden in (
            "fetching is authorized",
            "writing is authorized",
            "scheduling is authorized",
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

    def test_cli_default_and_input_work_without_subprocess(self) -> None:
        for argv in (
            ["jarvis_local_operator_bootstrap_report"],
            ["jarvis_local_operator_bootstrap_report", "--input", SYNTHETIC_READY],
        ):
            with self.subTest(argv=argv):
                stream = io.StringIO()
                with patch.object(sys, "argv", argv), redirect_stdout(stream):
                    main()
                output = stream.getvalue()
                self.assertIn("overall status:", output)
                self.assertIn("Commands are documented only", output)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_local_operator_bootstrap_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_CONFIG)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("Local Operator Bootstrap", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
