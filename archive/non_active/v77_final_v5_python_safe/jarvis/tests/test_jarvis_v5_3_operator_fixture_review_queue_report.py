import io
import sys
import unittest
from contextlib import redirect_stdout

from jarvis.jarvis_v5_3_operator_fixture_review_queue_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_3_operator_fixture_review_queue.synthetic_authorized_write.json"


class V53OperatorFixtureReviewQueueReportTests(unittest.TestCase):
    def test_default_report_contains_partial_status_and_safety_lines(self) -> None:
        report = build_report_from_path(DEFAULT_CONFIG)

        self.assertIn("V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_PARTIAL_SAFE", report)
        self.assertIn("no network calls", report)
        self.assertIn("no fetching", report)
        self.assertIn("no OCR", report)
        self.assertIn("no PDF parsing", report)
        self.assertIn("no HTML scraping", report)
        self.assertIn("no evidence verification", report)
        self.assertIn("no trade", report)
        self.assertIn("no executor", report)

    def test_complete_report_contains_required_sections_and_anti_redundancy(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        self.assertIn("V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_SAFE", report)
        self.assertIn("## Import Preview Summary", report)
        self.assertIn("## Review Queue Summary", report)
        self.assertIn("## Review Decision Summary", report)
        self.assertIn("## Review Priority Summary", report)
        self.assertIn("## Operator Runbook Steps", report)
        self.assertIn("## Where We Are", report)
        self.assertIn("## Where We Need To Go", report)
        self.assertIn("## Anti-Redundancy Statement", report)

    def test_problematic_report_prints_blockers_and_warnings(self) -> None:
        report = build_report_from_path(PROBLEMATIC_CONFIG)

        self.assertIn("V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE", report)
        self.assertIn("duplicate fixture_id", report)
        self.assertIn("rejected_duplicate_fixture_id", report)
        self.assertIn("deferred_stale_fixture", report)

    def test_authorized_report_is_ready_to_write_but_says_report_wrote_nothing(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        self.assertIn("V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_TO_WRITE_SAFE", report)
        self.assertIn("report wrote files: false", report)
        self.assertIn("AUTHORIZE_V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE", report)

    def test_report_does_not_claim_forbidden_capabilities(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for text in (
            "does not claim fetching",
            "no evidence verification",
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
                ["jarvis.jarvis_v5_3_operator_fixture_review_queue_report"],
                ["jarvis.jarvis_v5_3_operator_fixture_review_queue_report", "--input", COMPLETE_CONFIG],
            ):
                with self.subTest(argv=argv):
                    sys.argv = argv
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        main()
                    self.assertIn("J.A.R.V.I.S. v5.3", buffer.getvalue())
                    self.assertIn("Safety Statements", buffer.getvalue())
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    unittest.main()
