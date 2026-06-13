import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jarvis.jarvis_public_research_operator_dashboard_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_research_operator_dashboard.synthetic_authorized_write.json"


class PublicResearchOperatorDashboardReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE"),
            (COMPLETE_CONFIG, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE"),
            (AUTHORIZED_CONFIG, "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertIn(expected, build_report_from_path(path))

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "## Public Universe Pipeline Stage Table",
            "## Public Research Counts",
            "## Queue / Draft Pack Summary",
            "## Blockers / Warnings",
            "## Pipeline Readiness Label",
            "## v5 MVP Readiness Label",
            "## Next Safe Operator Action",
            "## Do Not Build Next",
            "## Where We Are",
            "## Where We Need To Go",
            "## Remaining Timeline To v5.0",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_stage_ids_and_safety_statements(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for stage_id in (
            "v4.61_discovery_plan",
            "v4.62_source_manifest",
            "v4.63_fetch_dry_run_planner",
            "v4.64_local_cache_builder",
            "v4.65_cache_integrity_freshness_audit",
            "v4.66_normalizer",
            "v4.67_classifier",
            "v4.68_research_priority_queue",
            "v4.69_public_evidence_pack_draft_generator",
        ):
            self.assertIn(stage_id, report)
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
        self.assertIn("PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE", output.getvalue())

        output = io.StringIO()
        with patch("sys.argv", ["prog", "--input", COMPLETE_CONFIG]), redirect_stdout(output):
            main()
        report = output.getvalue()
        self.assertIn("stage id | stage name", report)
        self.assertIn("draft pack count: 6", report)

    def test_report_writes_no_files(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE", report)
        self.assertIn("read-only/default-no-write/no-network/no-fetch/no-broker summary: true", report)


if __name__ == "__main__":
    unittest.main()
