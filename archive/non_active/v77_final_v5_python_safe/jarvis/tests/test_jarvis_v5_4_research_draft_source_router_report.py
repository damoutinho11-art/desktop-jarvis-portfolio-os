import io
import sys
import unittest
from contextlib import redirect_stdout

from jarvis.jarvis_v5_4_research_draft_source_router_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_4_research_draft_source_router.synthetic_authorized_write.json"


class V54ResearchDraftSourceRouterReportTests(unittest.TestCase):
    def test_default_report_contains_partial_status_and_safety_lines(self) -> None:
        report = build_report_from_path(DEFAULT_CONFIG)

        self.assertIn("V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_PARTIAL_SAFE", report)
        self.assertIn("no network calls", report)
        self.assertIn("no fetching", report)
        self.assertIn("no external file read", report)
        self.assertIn("no evidence verification", report)
        self.assertIn("no source truth verification", report)
        self.assertIn("no trade", report)
        self.assertIn("no executor", report)

    def test_complete_report_contains_required_sections_and_anti_redundancy(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        self.assertIn("V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_SAFE", report)
        self.assertIn("## Review Row Summary", report)
        self.assertIn("## Source Route Summary", report)
        self.assertIn("## Routing Decision Summary", report)
        self.assertIn("## Route Priority Summary", report)
        self.assertIn("## Blocked Downstream Use Summary", report)
        self.assertIn("## Operator Runbook Steps", report)
        self.assertIn("## Anti-Redundancy Statement", report)

    def test_problematic_report_prints_blockers_and_warnings(self) -> None:
        report = build_report_from_path(PROBLEMATIC_CONFIG)

        self.assertIn("V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE", report)
        self.assertIn("duplicate review_id", report)
        self.assertIn("block_duplicate_fixture_id", report)
        self.assertIn("defer_stale_fixture", report)

    def test_authorized_report_is_ready_to_write_but_says_report_wrote_nothing(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_TO_WRITE_SAFE", report)
        self.assertIn("report wrote files: false", report)
        self.assertIn("AUTHORIZE_V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE", report)

    def test_report_does_not_claim_forbidden_capabilities(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for text in (
            "does not claim fetching",
            "external file read",
            "no evidence verification",
            "no source truth verification",
            "no recommendation",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no allocation recommendation",
            "no buy/sell signal",
            "no trade",
            "no executor",
        ):
            self.assertIn(text, report)

    def test_cli_runs_with_default_and_explicit_input(self) -> None:
        original_argv = sys.argv[:]
        try:
            for argv in (
                ["jarvis.jarvis_v5_4_research_draft_source_router_report"],
                ["jarvis.jarvis_v5_4_research_draft_source_router_report", "--input", COMPLETE_CONFIG],
            ):
                with self.subTest(argv=argv):
                    sys.argv = argv
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        main()
                    self.assertIn("J.A.R.V.I.S. v5.4", buffer.getvalue())
                    self.assertIn("Safety Statements", buffer.getvalue())
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    unittest.main()
