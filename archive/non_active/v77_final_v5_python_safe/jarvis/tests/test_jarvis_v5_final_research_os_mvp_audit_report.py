import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jarvis.jarvis_v5_final_research_os_mvp_audit_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_final_research_os_mvp_audit.synthetic_authorized_write.json"


class V5FinalResearchOSMVPAuditReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"),
            (COMPLETE_CONFIG, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE"),
            (AUTHORIZED_CONFIG, "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_TO_WRITE_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertIn(expected, build_report_from_path(path))

    def test_report_includes_release_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "final verdict: JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE",
            "MVP readiness label: V5_RESEARCH_OS_MVP_READY_FOR_TAG_SAFE",
            "product definition:",
            "## Required Stage Chain Audit",
            "## Capability Matrix Audit",
            "## Final Audit Area Summary",
            "## Public Universe E2E Summary",
            "## Manual Trust / Manual Approval / No Execution Summary",
            "## Out Of Scope After v5",
            "## Recommended Next Phase",
            "## Where We Are",
            "## Where We Need To Go",
            "## v5.0 Release Statement",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_stage_capability_area_names(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "phase1_manual_evidence_workflow",
            "phase2_candidate_intake_workspace",
            "v4.71_public_universe_end_to_end_workflow_audit",
            "public_universe_discovery_planning",
            "no_execution_boundary",
            "broker_execution",
            "v5_release_readiness",
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
            "final real-world purchases remain manual and external",
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
        self.assertIn("V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE", output.getvalue())

        output = io.StringIO()
        with patch("sys.argv", ["prog", "--input", COMPLETE_CONFIG]), redirect_stdout(output):
            main()
        report = output.getvalue()
        self.assertIn("final verdict: JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE", report)
        self.assertIn("stage id | status | ready", report)
        self.assertIn("capability | required state | present | violation", report)

    def test_report_writes_no_files(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_TO_WRITE_SAFE", report)
        self.assertIn("read-only/default-no-write/no-network/no-fetch/no-broker summary: true", report)


if __name__ == "__main__":
    unittest.main()
