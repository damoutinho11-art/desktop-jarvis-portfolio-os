import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jarvis.jarvis_public_asset_universe_normalizer_report import build_report_from_path, main


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_normalizer.synthetic_authorized_write.json"


class PublicAssetUniverseNormalizerReportTests(unittest.TestCase):
    def test_reports_include_expected_statuses(self) -> None:
        cases = (
            (DEFAULT_CONFIG, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE"),
            (COMPLETE_CONFIG, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE"),
            (PROBLEMATIC_CONFIG, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_PARTIAL_SAFE"),
            (AUTHORIZED_CONFIG, "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_TO_WRITE_SAFE"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertIn(expected, build_report_from_path(path))

    def test_report_includes_required_sections(self) -> None:
        report = build_report_from_path(COMPLETE_CONFIG)

        for phrase in (
            "## Normalized Record Summary",
            "## Skipped / Blocked Input Summary",
            "## Duplicate Asset ID Summary",
            "## Output / Write Authorization Summary",
            "## Sample Normalized Records",
            "## Where We Are",
            "## Where We Need To Go",
            "## Do Not Build Next",
            "## Redundancy Check",
            "## Next Efficient Action",
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
            "no classification",
            "no screening",
            "no research scoring",
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
        report = build_report_from_path(COMPLETE_CONFIG)

        forbidden = (
            "approved asset: true",
            "investable: true",
            "buy signal: true",
            "trade executed: true",
            "registry mutation: true",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, report.lower())

    def test_cli_runs_with_default_input(self) -> None:
        output = io.StringIO()
        with patch("sys.argv", ["prog"]), redirect_stdout(output):
            main()

        self.assertIn("PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE", output.getvalue())

    def test_cli_runs_with_synthetic_complete_input(self) -> None:
        output = io.StringIO()
        with patch("sys.argv", ["prog", "--input", COMPLETE_CONFIG]), redirect_stdout(output):
            main()

        report = output.getvalue()
        self.assertIn("normalized record count: 3", report)
        self.assertIn("etf_vwce_xetra", report)


if __name__ == "__main__":
    unittest.main()
