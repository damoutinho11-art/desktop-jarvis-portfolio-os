import unittest
from pathlib import Path

from jarvis.ftaw_public_source_auto_draft import (
    FTAWAutoDraftSourceRecord,
    build_ftaw_public_source_auto_draft_pack_from_files,
    process_auto_draft_source,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
RESEARCH_CONFIG = "jarvis/data/ftaw_public_source_research_pack.example.json"
VERIFICATION_CONFIG = "jarvis/data/ftaw_draft_evidence_verification_queue.example.json"
AUTO_CONFIG = "jarvis/data/ftaw_public_source_auto_draft.example.json"
TARGET = "ftaw_global_core_candidate"


def _complete_market_source() -> FTAWAutoDraftSourceRecord:
    return FTAWAutoDraftSourceRecord(
        source_id="complete_market",
        asset_id=TARGET,
        evidence_type="market_data",
        source_type="public_market_data_page",
        source_name="Complete market source",
        url_reference="https://example.invalid/ftaw-market",
        local_text_content="price: 100.00\ncurrency: EUR\nsource: public page\nmarket_date: 2026-06-08",
        local_file_reference=None,
        enabled=True,
        allow_network_fetch=False,
        extraction_rules={
            "price": ("price",),
            "currency": ("currency",),
            "source": ("source",),
            "market_date": ("market_date",),
        },
    )


class FTAWPublicSourceAutoDraftTests(unittest.TestCase):
    def test_only_ftaw_is_processed(self) -> None:
        source = _complete_market_source()
        other = FTAWAutoDraftSourceRecord(
            **{**source.__dict__, "source_id": "other_asset", "asset_id": "webn_global_core_candidate"}
        )

        self.assertEqual(process_auto_draft_source(source).source_status, "processed")
        self.assertEqual(process_auto_draft_source(other).source_status, "skipped")

    def test_disabled_sources_are_skipped(self) -> None:
        source = FTAWAutoDraftSourceRecord(**{**_complete_market_source().__dict__, "enabled": False})

        self.assertEqual(process_auto_draft_source(source).source_status, "skipped")

    def test_forbidden_source_types_are_blocked(self) -> None:
        source = FTAWAutoDraftSourceRecord(**{**_complete_market_source().__dict__, "source_type": "credentialed_api"})
        result = process_auto_draft_source(source)

        self.assertEqual(result.source_status, "blocked")
        self.assertTrue(result.blockers)

    def test_platform_and_tax_route_are_skipped(self) -> None:
        source = _complete_market_source()
        platform = FTAWAutoDraftSourceRecord(**{**source.__dict__, "evidence_type": "platform_availability"})
        tax = FTAWAutoDraftSourceRecord(**{**source.__dict__, "evidence_type": "tax_route"})

        self.assertEqual(process_auto_draft_source(platform).source_status, "skipped")
        self.assertEqual(process_auto_draft_source(tax).source_status, "skipped")

    def test_complete_local_source_content_produces_draft_ready(self) -> None:
        result = process_auto_draft_source(_complete_market_source())

        self.assertEqual(result.draft_status, "draft_ready_for_manual_verification")
        self.assertIsNotNone(result.draft_record)
        self.assertFalse(result.draft_record["verified_by_user"])

    def test_incomplete_content_produces_needs_correction(self) -> None:
        source = FTAWAutoDraftSourceRecord(
            **{**_complete_market_source().__dict__, "local_text_content": "price: 100.00\ncurrency: EUR"}
        )
        result = process_auto_draft_source(source)

        self.assertEqual(result.draft_status, "needs_correction")
        self.assertTrue(result.blockers)

    def test_all_example_draft_records_are_unverified_and_network_disabled(self) -> None:
        pack = build_ftaw_public_source_auto_draft_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, RESEARCH_CONFIG, VERIFICATION_CONFIG, AUTO_CONFIG
        )

        self.assertTrue(pack.draft_evidence_records)
        self.assertTrue(all(record["verified_by_user"] is False for record in pack.draft_evidence_records))
        self.assertEqual(pack.network_fetch_enabled_count, 0)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_public_source_auto_draft_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, RESEARCH_CONFIG, VERIFICATION_CONFIG, AUTO_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        pack = build_ftaw_public_source_auto_draft_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, RESEARCH_CONFIG, VERIFICATION_CONFIG, AUTO_CONFIG
        )

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
