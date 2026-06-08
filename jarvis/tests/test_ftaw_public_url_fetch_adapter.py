import unittest
from pathlib import Path

from jarvis.ftaw_public_url_fetch_adapter import (
    FTAWPublicURLFetchSource,
    build_ftaw_public_url_fetch_pack_from_files,
    process_url_fetch_source,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
AUTO_CONFIG = "jarvis/data/ftaw_public_source_auto_draft.example.json"
FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
TARGET = "ftaw_global_core_candidate"


def _complete_market_source(**overrides):
    data = {
        "source_id": "complete_market",
        "asset_id": TARGET,
        "evidence_type": "market_data",
        "source_type": "public_market_data_page",
        "source_name": "Complete market fixture",
        "url_reference": "https://example.invalid/ftaw-market",
        "enabled": True,
        "allow_network_fetch": False,
        "local_fixture_text": "price: 100.00\ncurrency: EUR\nsource: public page\nmarket_date: 2026-06-08",
        "extraction_rules": {
            "price": ("price",),
            "currency": ("currency",),
            "source": ("source",),
            "market_date": ("market_date",),
        },
    }
    data.update(overrides)
    return FTAWPublicURLFetchSource(**data)


class FTAWPublicURLFetchAdapterTests(unittest.TestCase):
    def test_default_config_performs_no_network_fetch(self) -> None:
        pack = build_ftaw_public_url_fetch_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, AUTO_CONFIG, FETCH_CONFIG)

        self.assertFalse(pack.global_network_fetch_enabled)
        self.assertEqual(pack.network_fetch_attempted_count, 0)

    def test_local_fixture_text_can_create_draft_evidence(self) -> None:
        result = process_url_fetch_source(_complete_market_source(), enable_network_fetch=False)

        self.assertEqual(result.source_status, "processed")
        self.assertIsNotNone(result.draft_record)
        self.assertEqual(result.mode, "local_fixture")

    def test_fetched_or_local_evidence_remains_unverified(self) -> None:
        result = process_url_fetch_source(_complete_market_source(), enable_network_fetch=False)

        self.assertFalse(result.draft_record["verified_by_user"])

    def test_disabled_sources_are_skipped(self) -> None:
        result = process_url_fetch_source(_complete_market_source(enabled=False), enable_network_fetch=False)

        self.assertEqual(result.source_status, "skipped")

    def test_forbidden_source_types_are_blocked(self) -> None:
        result = process_url_fetch_source(_complete_market_source(source_type="authenticated_broker"), enable_network_fetch=False)

        self.assertEqual(result.source_status, "blocked")
        self.assertTrue(result.blockers)

    def test_http_urls_are_blocked_when_network_would_be_used(self) -> None:
        source = _complete_market_source(local_fixture_text=None, allow_network_fetch=True, url_reference="http://example.invalid/ftaw")
        result = process_url_fetch_source(source, enable_network_fetch=True)

        self.assertEqual(result.source_status, "blocked")
        self.assertTrue(any("https" in blocker for blocker in result.blockers))

    def test_blocked_url_patterns_are_blocked(self) -> None:
        source = _complete_market_source(local_fixture_text=None, allow_network_fetch=True, url_reference="https://example.invalid/account/ftaw")
        result = process_url_fetch_source(source, enable_network_fetch=True)

        self.assertEqual(result.source_status, "blocked")
        self.assertTrue(any("account" in blocker for blocker in result.blockers))

    def test_platform_and_tax_route_are_skipped(self) -> None:
        platform = process_url_fetch_source(_complete_market_source(evidence_type="platform_availability"), enable_network_fetch=False)
        tax = process_url_fetch_source(_complete_market_source(evidence_type="tax_route"), enable_network_fetch=False)

        self.assertEqual(platform.source_status, "skipped")
        self.assertEqual(tax.source_status, "skipped")

    def test_missing_facts_produce_needs_correction(self) -> None:
        source = _complete_market_source(local_fixture_text="price: 100.00\ncurrency: EUR")
        result = process_url_fetch_source(source, enable_network_fetch=False)

        self.assertEqual(result.draft_status, "needs_correction")
        self.assertTrue(result.blockers)

    def test_complete_fixture_facts_produce_draft_ready(self) -> None:
        result = process_url_fetch_source(_complete_market_source(), enable_network_fetch=False)

        self.assertEqual(result.draft_status, "draft_ready_for_manual_verification")

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_public_url_fetch_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, AUTO_CONFIG, FETCH_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        pack = build_ftaw_public_url_fetch_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, AUTO_CONFIG, FETCH_CONFIG)

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
