import json
import tempfile
import unittest
from pathlib import Path

from jarvis.ftaw_source_fact_intake import (
    FTAWSourceFactIntakeConfig,
    FTAWSourceFactRecord,
    build_ftaw_source_fact_intake_pack,
    build_ftaw_source_fact_intake_pack_from_files,
    write_improved_draft_evidence,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
TARGET = "ftaw_global_core_candidate"


def _complete_market_record(**overrides):
    data = {
        "asset_id": TARGET,
        "evidence_type": "market_data",
        "source_name": "User supplied market facts",
        "source_quality": "manual_research",
        "url_reference": "https://example.invalid/ftaw-market",
        "file_reference": None,
        "as_of": "2026-06-09",
        "extracted_facts": {
            "price": "100.00",
            "currency": "EUR",
            "source": "public market page",
            "market_date": "2026-06-09",
        },
        "user_notes": "Manually collected public facts.",
    }
    data.update(overrides)
    return FTAWSourceFactRecord(**data)


class FTAWSourceFactIntakeTests(unittest.TestCase):
    def test_only_ftaw_is_processed(self) -> None:
        other = _complete_market_record(asset_id="webn_global_core_candidate")
        pack = build_ftaw_source_fact_intake_pack(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            URL_FETCH_CONFIG,
            FTAWSourceFactIntakeConfig(records=(_complete_market_record(), other)),
        )

        self.assertEqual(pack.processed_fact_records_count, 1)
        self.assertEqual({record["asset_id"] for record in pack.draft_evidence_records}, {TARGET})

    def test_manual_evidence_types_are_skipped(self) -> None:
        platform = _complete_market_record(evidence_type="platform_availability")
        tax = _complete_market_record(evidence_type="tax_route")
        pack = build_ftaw_source_fact_intake_pack(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            URL_FETCH_CONFIG,
            FTAWSourceFactIntakeConfig(records=(platform, tax)),
        )

        self.assertEqual(pack.skipped_manual_evidence_types, ("platform_availability", "tax_route"))
        self.assertEqual(pack.draft_evidence_records, ())

    def test_complete_fact_record_creates_draft_ready(self) -> None:
        pack = build_ftaw_source_fact_intake_pack(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            URL_FETCH_CONFIG,
            FTAWSourceFactIntakeConfig(records=(_complete_market_record(),)),
        )

        self.assertEqual(pack.draft_ready_count, 1)
        self.assertEqual(pack.needs_correction_count, 0)

    def test_missing_or_placeholder_facts_create_needs_correction(self) -> None:
        pack = build_ftaw_source_fact_intake_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, URL_FETCH_CONFIG, INTAKE_CONFIG)

        self.assertEqual(pack.processed_fact_records_count, 5)
        self.assertEqual(len(pack.draft_evidence_records), 5)
        self.assertEqual(pack.draft_ready_count, 0)
        self.assertEqual(pack.needs_correction_count, 5)
        self.assertEqual(
            pack.missing_facts_by_evidence_type,
            {
                "distribution_policy": ("distribution_policy", "accumulating_or_distributing", "as_of_date"),
                "exposure_data": ("top_holdings_source", "country_exposure_source", "sector_exposure_source", "as_of_date"),
                "fee_metadata": ("ter_or_fee", "fee_source", "as_of_date"),
                "fund_metadata": ("name", "ticker", "isin_or_symbol", "provider", "index_tracked", "replication_method"),
                "market_data": ("price", "currency", "source", "market_date"),
            },
        )

    def test_all_draft_records_are_unverified(self) -> None:
        pack = build_ftaw_source_fact_intake_pack(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            URL_FETCH_CONFIG,
            FTAWSourceFactIntakeConfig(records=(_complete_market_record(),)),
        )

        self.assertTrue(all(record["verified_by_user"] is False for record in pack.draft_evidence_records))

    def test_optional_writer_writes_only_to_explicit_output_path(self) -> None:
        pack = build_ftaw_source_fact_intake_pack(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            URL_FETCH_CONFIG,
            FTAWSourceFactIntakeConfig(records=(_complete_market_record(),)),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "improved_drafts.json"

            write_improved_draft_evidence(pack, output)

            self.assertTrue(output.exists())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["records"]), 1)
            self.assertFalse(payload["records"][0]["verified_by_user"])

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "improved_drafts.json"

            build_ftaw_source_fact_intake_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, URL_FETCH_CONFIG, INTAKE_CONFIG)

            self.assertFalse(output.exists())

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_source_fact_intake_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, URL_FETCH_CONFIG, INTAKE_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        pack = build_ftaw_source_fact_intake_pack_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, URL_FETCH_CONFIG, INTAKE_CONFIG)

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
