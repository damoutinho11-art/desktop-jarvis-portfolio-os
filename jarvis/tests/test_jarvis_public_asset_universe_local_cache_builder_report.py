import importlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jarvis.jarvis_public_asset_universe_local_cache_builder_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.example.json"
UNAUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.synthetic_unauthorized.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.synthetic_authorized.json"


class PublicAssetUniverseLocalCacheBuilderReportTests(unittest.TestCase):
    def test_report_default_and_inputs_work_without_execution(self) -> None:
        for path, expected in (
            (DEFAULT_CONFIG, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE"),
            (UNAUTHORIZED_CONFIG, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE"),
            (AUTHORIZED_CONFIG, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_READY_TO_FETCH_SAFE"),
        ):
            with self.subTest(path=path):
                report = build_report_from_path(path)
                self.assertIn(expected, report)
                self.assertIn("default no fetching", report)
                self.assertIn("default no writes", report)

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        for phrase in (
            "## Default-Off Summary",
            "## Source Plan Summary",
            "## Source Plans",
            "## Planned vs Written Path Summary",
            "## Skipped / Manual Reference Sources",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "## Redundancy Check",
            "## Next Efficient Action",
            "## v5.0 Research OS Target",
        ):
            self.assertIn(phrase, report)

    def test_report_prints_safety_lines(self) -> None:
        report = build_report_from_path(AUTHORIZED_CONFIG)

        for phrase in (
            "default no network calls",
            "default no fetching",
            "default no downloading",
            "default no writes",
            "authorized path local-cache-only",
            "no scraping",
            "no API calls without explicit authorization",
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
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
        ):
            self.assertIn(phrase, report)

    def test_cli_default_and_input_work_without_subprocess(self) -> None:
        for argv in (
            ["jarvis_public_asset_universe_local_cache_builder_report"],
            ["jarvis_public_asset_universe_local_cache_builder_report", "--input", UNAUTHORIZED_CONFIG],
            ["jarvis_public_asset_universe_local_cache_builder_report", "--input", AUTHORIZED_CONFIG],
        ):
            with self.subTest(argv=argv):
                stream = io.StringIO()
                with patch.object(sys, "argv", argv), redirect_stdout(stream):
                    main()
                output = stream.getvalue()
                self.assertIn("overall status:", output)
                self.assertIn("Safety Statements", output)

    def test_report_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            before = set(Path(tmpdir).iterdir())
            report = build_report_from_path(AUTHORIZED_CONFIG)
            after = set(Path(tmpdir).iterdir())

        self.assertIn("READY_TO_FETCH_SAFE", report)
        self.assertEqual(before, after)

    def test_module_import_is_safe(self) -> None:
        module = importlib.import_module("jarvis.jarvis_public_asset_universe_local_cache_builder_report")
        self.assertTrue(hasattr(module, "build_report_from_path"))


if __name__ == "__main__":
    unittest.main()
