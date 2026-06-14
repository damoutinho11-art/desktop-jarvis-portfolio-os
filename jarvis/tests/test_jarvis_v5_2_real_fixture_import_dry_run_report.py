import io
import sys
import unittest
from contextlib import redirect_stdout

from jarvis.jarvis_v5_2_real_fixture_import_dry_run_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_authorized_write.json"


class V52RealFixtureImportDryRunReportTests(unittest.TestCase):
    def test_default_report_contains_partial_status_and_safety_lines(self) -> None:
        report = build_report_from_path(DEFAULT_CONFIG)

        self.assertIn("V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_PARTIAL_SAFE", report)
        self.assertIn("no network calls", report)
        self.assertIn("no fetching", report)
        self.assertIn("no OCR", report)
        self.assertIn("no PDF parsing", report)
        self.assertIn("no HTML scraping", report)
        self.assertIn("no evidence verification", report)
        self.assertIn("no trade", report)
        self.assertIn("no executor", report)

    def test_complete_report_contains_fixture_import_and_pipeline_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        self.assertIn("V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_SAFE", report)
        self.assertIn("## Fixture Summary", report)
        self.assertIn("## Local File Inspection Summary", report)
        self.assertIn("## Import Preview Summary", report)
        self.assertIn("## Pipeline Mapping Summary", report)
        self.assertIn("etf_universe_csv", report)
        self.assertIn("public_document_pdf_reference", report)

    def test_problematic_report_prints_blockers_and_warnings(self) -> None:
        report = build_report_from_path(PROBLEMATIC_CONFIG)

        self.assertIn("V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE", report)
        self.assertIn("duplicate fixture_id", report)
        self.assertIn("unsupported fixture_format", report)
        self.assertIn("local fixture file is missing", report)

    def test_authorized_report_is_ready_to_write_but_says_report_wrote_nothing(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_TO_WRITE_SAFE", report)
        self.assertIn("report wrote files: false", report)
        self.assertIn("AUTHORIZE_V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE", report)

    def test_cli_runs_with_default_and_explicit_input(self) -> None:
        original_argv = sys.argv[:]
        try:
            for argv in (
                ["jarvis.jarvis_v5_2_real_fixture_import_dry_run_report"],
                ["jarvis.jarvis_v5_2_real_fixture_import_dry_run_report", "--input", COMPLETE_CONFIG],
            ):
                with self.subTest(argv=argv):
                    sys.argv = argv
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        main()
                    self.assertIn("J.A.R.V.I.S. v5.2", buffer.getvalue())
                    self.assertIn("Safety Statements", buffer.getvalue())
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    unittest.main()
