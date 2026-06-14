import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jarvis.jarvis_v5_1_public_source_fixture_wiring_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_1_public_source_fixture_wiring.synthetic_authorized_write.json"


class V51PublicSourceFixtureWiringReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE"),
            (COMPLETE_CONFIG, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE"),
            (AUTHORIZED_CONFIG, "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_TO_WRITE_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertIn(expected, build_report_from_path(path))

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "## Fixture Summary",
            "## Supported Format Summary",
            "## Pipeline Mapping Summary",
            "## Operator Runbook Steps",
            "## Blockers / Warnings",
            "## Next Safe Operator Action",
            "## Do Not Build Next",
            "## Where We Are",
            "## Where We Need To Go",
            "## Post-v5.0 Phase Statement",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_fixture_and_mapping_tables(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "fixture id | category | format | status | path | mapped | blockers | warnings",
            "fixture id | category | mapped | pipeline stages | blocked reason",
            "etf_universe_csv",
            "source_manifest",
            "draft_evidence_pack_generator",
            "e2e_audit",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_runbook_and_safety_lines(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "Copy the local template",
            "fixture import dry-run",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no broker integration",
            "no source parsing as verified evidence",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no recommendation",
            "no approval",
            "no investable asset",
            "no registry mutation",
            "no allocation recommendation",
            "no buy/sell signal",
            "no trade",
            "no executor",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_forbidden_authorization(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG).lower()

        for phrase in (
            "fetch executed: true",
            "download executed: true",
            "evidence verified: true",
            "approved asset: true",
            "investable: true",
            "buy signal: true",
            "trade executed: true",
            "executor authorized",
        ):
            self.assertNotIn(phrase, report)

    def test_cli_default_and_input_work(self) -> None:
        output = io.StringIO()
        with patch("sys.argv", ["prog"]), redirect_stdout(output):
            main()
        self.assertIn("V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE", output.getvalue())

        output = io.StringIO()
        with patch("sys.argv", ["prog", "--input", COMPLETE_CONFIG]), redirect_stdout(output):
            main()
        report = output.getvalue()
        self.assertIn("V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_SAFE", report)
        self.assertIn("Pipeline Mapping Summary", report)

    def test_report_writes_no_files(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_TO_WRITE_SAFE", report)
        self.assertIn("read-only/default-no-write/no-network/no-fetch/no-broker summary: true", report)


if __name__ == "__main__":
    unittest.main()
