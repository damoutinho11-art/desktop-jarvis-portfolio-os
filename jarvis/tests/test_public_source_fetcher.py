import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.public_source_fetcher import (
    PublicSourceFetchConfig,
    fetch_public_source,
    run_public_source_fetcher,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"


def _config(
    source_id: str = "unit_public_source",
    asset_id: str = "vwce_global_core_candidate",
    source_type: str = "provider_product_page",
    enabled: bool = True,
    allow_network_fetch: bool = False,
    local_fixture_content: str | None = (
        "ticker: VWCE\ncurrency: EUR\nprovider: Vanguard\nplatform_name: public fixture\navailability_status: reference_only"
    ),
) -> PublicSourceFetchConfig:
    return PublicSourceFetchConfig(
        source_id=source_id,
        asset_id=asset_id,
        evidence_type="fund_metadata",
        source_type=source_type,
        source_name="Unit public source",
        url_reference="https://example.invalid/source",
        enabled=enabled,
        allow_network_fetch=allow_network_fetch,
        local_fixture_content=local_fixture_content,
        notes="Unit-test public source.",
    )


def _write_sources(sources: list[dict]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"sources": sources}, file)
        return Path(file.name)


class PublicSourceFetcherTests(unittest.TestCase):
    def test_local_fixture_mode_creates_draft_evidence(self) -> None:
        result = fetch_public_source(_config(), load_asset_registry(REGISTRY).by_id())

        self.assertEqual(result.status, "DRAFT_EVIDENCE_CREATED")
        self.assertIsNotNone(result.draft_evidence_record)

    def test_network_disabled_by_default(self) -> None:
        config = _config()

        self.assertFalse(config.allow_network_fetch)

    def test_allow_network_fetch_false_never_calls_network_fetch(self) -> None:
        called = False

        def network_fetch(url: str, timeout: int, max_bytes: int) -> str:
            nonlocal called
            called = True
            return "ticker: TEST"

        fetch_public_source(_config(allow_network_fetch=False), load_asset_registry(REGISTRY).by_id(), network_fetch=network_fetch)

        self.assertFalse(called)

    def test_forbidden_authenticated_source_blocked(self) -> None:
        result = fetch_public_source(
            _config(source_type="authenticated_broker_session"),
            load_asset_registry(REGISTRY).by_id(),
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(result.blockers)

    def test_unknown_asset_id_blocked(self) -> None:
        result = fetch_public_source(_config(asset_id="unknown_asset"), load_asset_registry(REGISTRY).by_id())

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(result.blockers)

    def test_disabled_source_skipped(self) -> None:
        result = fetch_public_source(_config(enabled=False), load_asset_registry(REGISTRY).by_id())

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("source disabled", result.blockers[0])

    def test_extracted_facts_populate_draft_record(self) -> None:
        result = fetch_public_source(_config(), load_asset_registry(REGISTRY).by_id())

        self.assertEqual(result.draft_evidence_record["extracted_facts"]["ticker"], "VWCE")

    def test_missing_facts_create_warnings(self) -> None:
        result = fetch_public_source(_config(local_fixture_content="ticker: VWCE"), load_asset_registry(REGISTRY).by_id())

        self.assertEqual(result.status, "WARNING")
        self.assertTrue(any("missing extracted fact" in warning for warning in result.warnings))

    def test_draft_evidence_always_has_verified_by_user_false(self) -> None:
        result = fetch_public_source(_config(), load_asset_registry(REGISTRY).by_id())

        self.assertFalse(result.draft_evidence_record["verified_by_user"])

    def test_no_approval_status_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        run_public_source_fetcher(REGISTRY, PUBLIC_SOURCES)

        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        self.assertEqual(before, after)

    def test_no_registry_mutation(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        run_public_source_fetcher(REGISTRY, PUBLIC_SOURCES)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_network_failure_returns_warning_not_crash(self) -> None:
        def failing_fetch(url: str, timeout: int, max_bytes: int) -> str:
            raise OSError("network unavailable")

        result = fetch_public_source(
            _config(allow_network_fetch=True, local_fixture_content="ticker: VWCE"),
            load_asset_registry(REGISTRY).by_id(),
            network_fetch=failing_fetch,
        )

        self.assertEqual(result.status, "WARNING")
        self.assertTrue(any("network fetch failed" in warning for warning in result.warnings))

    def test_example_fixture_creates_drafts(self) -> None:
        result = run_public_source_fetcher(REGISTRY, PUBLIC_SOURCES)
        drafts = [item for item in result.results if item.draft_evidence_record]

        self.assertGreaterEqual(len(drafts), 3)

    def test_malformed_public_source_file_rejected(self) -> None:
        path = _write_sources([{"source_id": "missing required fields"}])

        with self.assertRaises(ValueError):
            run_public_source_fetcher(REGISTRY, path)


if __name__ == "__main__":
    unittest.main()
