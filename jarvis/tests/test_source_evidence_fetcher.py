import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.source_evidence_fetcher import (
    SourceEvidenceConfig,
    fetch_source_evidence,
    load_source_evidence_configs,
    run_source_evidence_fetcher,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
SOURCES = "jarvis/data/source_evidence_sources.example.json"


def _config(**overrides) -> SourceEvidenceConfig:
    config = SourceEvidenceConfig(
        source_id="source_test",
        asset_id="vwce_global_core_candidate",
        evidence_type="fund_metadata",
        source_type="provider_factsheet_pdf",
        source_name="Static test source",
        url_reference="https://example.invalid/test",
        local_fixture_path=None,
        enabled=True,
        notes="Test static source.",
        static_content="ticker: VWCE\nprovider: Vanguard\ncurrency: EUR\nplatform_name: Lightyear\navailability_status: available",
    )
    return SourceEvidenceConfig(**{**config.__dict__, **overrides})


class SourceEvidenceFetcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assets = load_asset_registry(REGISTRY).by_id()

    def test_valid_source_config_loads(self) -> None:
        configs = load_source_evidence_configs(SOURCES)

        self.assertGreaterEqual(len(configs), 3)
        self.assertEqual(configs[0].source_id, "vwce_provider_factsheet_static")

    def test_forbidden_authenticated_source_is_blocked(self) -> None:
        result = fetch_source_evidence(_config(source_type="authenticated_broker_session"), self.assets)

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("forbidden source_type" in blocker for blocker in result.blockers))

    def test_unknown_asset_id_blocked(self) -> None:
        result = fetch_source_evidence(_config(asset_id="unknown_asset"), self.assets)

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("unknown asset_id" in blocker for blocker in result.blockers))

    def test_disabled_source_skipped(self) -> None:
        result = fetch_source_evidence(_config(enabled=False), self.assets)

        self.assertEqual(result.status, "BLOCKED")
        self.assertIsNone(result.draft_evidence_record)
        self.assertTrue(any("source disabled" in blocker for blocker in result.blockers))

    def test_local_static_source_creates_draft_evidence(self) -> None:
        result = fetch_source_evidence(_config(), self.assets)

        self.assertIn(result.status, {"DRAFT_EVIDENCE_CREATED", "WARNING"})
        self.assertIsNotNone(result.draft_evidence_record)

    def test_draft_evidence_always_unverified(self) -> None:
        result = fetch_source_evidence(_config(source_type="public_crypto_market_api"), self.assets)

        self.assertFalse(result.draft_evidence_record["verified_by_user"])

    def test_extracted_facts_appear_in_draft_record(self) -> None:
        result = fetch_source_evidence(_config(), self.assets)

        self.assertEqual(result.draft_evidence_record["extracted_facts"]["ticker"], "VWCE")

    def test_missing_extracted_facts_create_warnings(self) -> None:
        result = fetch_source_evidence(_config(static_content="ticker: VWCE"), self.assets)

        self.assertEqual(result.status, "WARNING")
        self.assertTrue(any("missing extracted fact" in warning for warning in result.warnings))

    def test_source_quality_mapping_works(self) -> None:
        platform = fetch_source_evidence(_config(source_type="public_platform_page"), self.assets)
        api = fetch_source_evidence(_config(source_type="public_crypto_market_api"), self.assets)

        self.assertEqual(platform.draft_evidence_record["source_quality"], "platform_screenshot")
        self.assertEqual(api.draft_evidence_record["source_quality"], "verified_api_snapshot")
        self.assertFalse(api.draft_evidence_record["verified_by_user"])

    def test_no_approval_status_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        run_source_evidence_fetcher(REGISTRY, SOURCES)
        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        self.assertEqual(before, after)

    def test_no_registry_mutation(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        run_source_evidence_fetcher(REGISTRY, SOURCES)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
