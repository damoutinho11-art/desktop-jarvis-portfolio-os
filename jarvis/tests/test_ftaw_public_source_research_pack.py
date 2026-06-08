import unittest
from pathlib import Path

from jarvis.ftaw_public_source_research_pack import build_ftaw_public_source_research_pack_from_files


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"
SOURCE_PACK_CONFIG = "jarvis/data/ftaw_source_collection_pack.example.json"
RESEARCH_CONFIG = "jarvis/data/ftaw_public_source_research_pack.example.json"
TARGET = "ftaw_global_core_candidate"


class FTAWPublicSourceResearchPackTests(unittest.TestCase):
    def test_only_ftaw_is_included(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertEqual(pack.target_asset_id, TARGET)
        self.assertEqual({record["asset_id"] for record in pack.draft_evidence_records}, {TARGET})

    def test_only_public_research_tasks_produce_draft_evidence(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )
        evidence_types = {record["evidence_type"] for record in pack.draft_evidence_records}

        self.assertEqual(
            evidence_types,
            {"fund_metadata", "fee_metadata", "distribution_policy", "exposure_data", "market_data"},
        )

    def test_exactly_five_draft_records_are_produced(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertEqual(pack.public_research_tasks_count, 5)
        self.assertEqual(len(pack.draft_evidence_records), 5)

    def test_platform_availability_and_tax_route_are_skipped(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertEqual(pack.skipped_manual_evidence_types, ("platform_availability", "tax_route"))
        self.assertNotIn("platform_availability", pack.draft_records_by_evidence_type)
        self.assertNotIn("tax_route", pack.draft_records_by_evidence_type)

    def test_all_draft_records_are_unverified(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertTrue(all(record["verified_by_user"] is False for record in pack.draft_evidence_records))

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        pack = build_ftaw_public_source_research_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, SOURCE_PACK_CONFIG, RESEARCH_CONFIG
        )

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
