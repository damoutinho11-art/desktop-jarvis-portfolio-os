import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jarvis.jarvis_public_evidence_pack_draft_generator_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_authorized_write.json"


class PublicEvidencePackDraftGeneratorReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE"),
            (COMPLETE_CONFIG, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_PARTIAL_SAFE"),
            (AUTHORIZED_CONFIG, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_TO_WRITE_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertIn(expected, build_report_from_path(path))

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "## Draft Pack Summary",
            "## Required Evidence Section Summary",
            "## Required Public Source Category Summary",
            "## Manual Verification Checklist Summary",
            "## Skipped / Blocked Item Summary",
            "## Duplicate Draft ID Summary",
            "## Output / Write Authorization Summary",
            "## Sample Draft Packs",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "## v5.0 Research OS Target",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_safety_statements(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no browser automation",
            "no subprocess execution",
            "no scheduler creation",
            "no broker integration",
            "no Lightyear integration",
            "no LHV integration",
            "no crypto exchange integration",
            "no credentials",
            "no private/account data ingest",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no investment screening",
            "no research scoring based on expected returns",
            "no ranking by investment merit",
            "no recommendation",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_forbidden_authorization(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG).lower()

        for phrase in (
            "approved asset: true",
            "investable: true",
            "buy signal: true",
            "trade executed: true",
            "registry mutation: true",
            "executor authorized",
        ):
            self.assertNotIn(phrase, report)

    def test_cli_default_and_input_work(self) -> None:
        output = io.StringIO()
        with patch("sys.argv", ["prog"]), redirect_stdout(output):
            main()
        self.assertIn("PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE", output.getvalue())

        output = io.StringIO()
        with patch("sys.argv", ["prog", "--input", COMPLETE_CONFIG]), redirect_stdout(output):
            main()
        report = output.getvalue()
        self.assertIn("draft pack count: 6", report)
        self.assertIn("identity_and_identifier_check", report)

    def test_report_writes_no_files(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("report writes files: false", report)
        self.assertIn("PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_TO_WRITE_SAFE", report)


if __name__ == "__main__":
    unittest.main()
