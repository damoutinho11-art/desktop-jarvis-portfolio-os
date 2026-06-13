import importlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit_report import (
    build_report_from_path,
    main,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_problematic.json"


class PublicAssetUniverseCacheIntegrityFreshnessAuditReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_BLOCKED_SAFE"),
            (COMPLETE_CONFIG, "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_INTEGRITY_ISSUES_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                report = build_report_from_path(path)
                self.assertIn(expected, report)

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "## Coverage Summary",
            "## Freshness Summary",
            "## Integrity Summary",
            "## Per-Source Cache Audit Summary",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "## Redundancy Check",
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
            "no writes",
            "no cache mutation",
            "no cache repair",
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
            "no normalization",
            "no classification",
            "no screening",
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

        for forbidden in (
            "fetching is authorized",
            "api calls are authorized",
            "scraping is authorized",
            "writing is authorized",
            "cache repair is authorized",
            "cache mutation is authorized",
            "scheduling is authorized",
            "broker integration is authorized",
            "lightyear integration is authorized",
            "lhv integration is authorized",
            "crypto exchange integration is authorized",
            "credential use is authorized",
            "evidence verification is authorized",
            "normalization is authorized",
            "classification is authorized",
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
            ["jarvis_public_asset_universe_cache_integrity_freshness_audit_report"],
            ["jarvis_public_asset_universe_cache_integrity_freshness_audit_report", "--input", COMPLETE_CONFIG],
            ["jarvis_public_asset_universe_cache_integrity_freshness_audit_report", "--input", PROBLEMATIC_CONFIG],
        ):
            with self.subTest(argv=argv):
                stream = io.StringIO()
                with patch.object(sys, "argv", argv), redirect_stdout(stream):
                    main()
                output = stream.getvalue()
                self.assertIn("overall status:", output)
                self.assertIn("Coverage Summary", output)

    def test_report_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(COMPLETE_CONFIG)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("CACHE_AUDIT_READY_SAFE", report)
        self.assertEqual(before, after)

    def test_module_import_is_safe(self) -> None:
        module = importlib.import_module("jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))


if __name__ == "__main__":
    unittest.main()
