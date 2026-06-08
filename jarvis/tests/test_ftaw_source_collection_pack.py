import unittest
from pathlib import Path

from jarvis.ftaw_source_collection_pack import build_ftaw_source_collection_pack_from_files


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"
PACK_CONFIG = "jarvis/data/ftaw_source_collection_pack.example.json"
TARGET = "ftaw_global_core_candidate"


class FTAWSourceCollectionPackTests(unittest.TestCase):
    def test_only_ftaw_is_included(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )

        self.assertEqual(pack.target_asset_id, TARGET)
        self.assertEqual({item.asset_id for item in pack.collection_items}, {TARGET})

    def test_exactly_seven_collection_items_are_produced(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )

        self.assertEqual(len(pack.collection_items), 7)
        self.assertEqual(set(pack.items_by_evidence_type.values()), {1})

    def test_all_templates_verified_by_user_false(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )

        self.assertTrue(
            all(item.ready_to_fill_intake_template["verified_by_user"] is False for item in pack.collection_items)
        )

    def test_platform_availability_uses_account_specific_manual(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )
        item = next(item for item in pack.collection_items if item.evidence_type == "platform_availability")

        self.assertEqual(item.collection_mode, "account_specific_manual")

    def test_tax_route_uses_manual_tax_review(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )
        item = next(item for item in pack.collection_items if item.evidence_type == "tax_route")

        self.assertEqual(item.collection_mode, "manual_tax_review")

    def test_market_data_requires_price_currency_source_and_as_of(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )
        item = next(item for item in pack.collection_items if item.evidence_type == "market_data")
        fields = {field.lower() for field in item.fields_to_capture}

        self.assertTrue({"price", "currency", "source"}.issubset(fields))
        self.assertTrue("as_of_date" in fields or "market_date" in fields)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        pack = build_ftaw_source_collection_pack_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG, PACK_CONFIG
        )

        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
