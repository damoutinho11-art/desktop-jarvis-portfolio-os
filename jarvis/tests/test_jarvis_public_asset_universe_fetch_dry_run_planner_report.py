import importlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jarvis.jarvis_public_asset_universe_fetch_dry_run_planner_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_fetch_dry_run_planner.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_asset_universe_fetch_dry_run_planner.synthetic_complete.json"


class PublicAssetUniverseFetchDryRunPlannerReportTests(unittest.TestCase):
    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE)

        for phrase in (
            "## Strategic Correction",
            "no manual one-by-one asset entry as primary workflow",
            "public fetch dry-run planner comes before any universe cache builder",
            "## Authorization Policy",
            "## Source Eligibility Summary",
            "## Per-Source Dry-Run Plan Summary",
            "## Fetch Order",
            "## Planned Local Cache Paths",
            "## Freshness Policy",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "## v5.0 Research OS Target",
            "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE",
        ):
            self.assertIn(phrase, report)

    def test_report_includes_safety_statements(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE)

        for phrase in (
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no writes",
            "no cache creation",
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
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
        ):
            self.assertIn(phrase, report)

    def test_report_does_not_claim_forbidden_authorization(self) -> None:
        report = build_report_from_path(SYNTHETIC_COMPLETE).lower()

        for forbidden in (
            "fetching is authorized",
            "api calls are authorized",
            "scraping is authorized",
            "writing is authorized",
            "cache creation is authorized",
            "scheduling is authorized",
            "broker integration is authorized",
            "lightyear integration is authorized",
            "lhv integration is authorized",
            "crypto exchange integration is authorized",
            "credential use is authorized",
            "evidence verification is authorized",
            "approval is authorized",
            "trust is authorized",
            "investability is authorized",
            "allocation is authorized",
            "buy/sell signal is authorized",
            "trade is authorized",
            "registry mutation is authorized",
            "candidate registry write is authorized",
            "private ingest is authorized",
            "executor is authorized",
        ):
            self.assertNotIn(forbidden, report)

    def test_cli_default_and_input_work_without_subprocess(self) -> None:
        for argv in (
            ["jarvis_public_asset_universe_fetch_dry_run_planner_report"],
            ["jarvis_public_asset_universe_fetch_dry_run_planner_report", "--input", SYNTHETIC_COMPLETE],
        ):
            with self.subTest(argv=argv):
                stream = io.StringIO()
                with patch.object(sys, "argv", argv), redirect_stdout(stream):
                    main()
                output = stream.getvalue()
                self.assertIn("overall status:", output)
                self.assertIn("Authorization Policy", output)

    def test_module_import_is_safe_and_report_writes_no_files(self) -> None:
        module = importlib.import_module("jarvis.jarvis_public_asset_universe_fetch_dry_run_planner_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))

        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(DEFAULT_CONFIG)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("Public Asset Universe Fetch Dry-Run Planner", report)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
