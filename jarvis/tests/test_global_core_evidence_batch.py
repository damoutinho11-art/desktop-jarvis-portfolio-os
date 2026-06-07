import unittest
from pathlib import Path

from jarvis.global_core_evidence_batch import (
    GLOBAL_CORE_EVIDENCE_TYPES,
    build_global_core_evidence_batch_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"


class GlobalCoreEvidenceBatchTests(unittest.TestCase):
    def test_vwce_is_skipped_when_private_reviewed_copy_is_supplied(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertIn("vwce_global_core_candidate", batch.already_reviewed_skipped)
        self.assertNotIn("vwce_global_core_candidate", batch.target_candidates)

    def test_remaining_global_core_etfs_are_included(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertEqual(
            set(batch.target_candidates),
            {
                "ftaw_global_core_candidate",
                "spyi_imie_global_core_candidate",
                "ssac_iusq_global_core_candidate",
                "webn_global_core_candidate",
            },
        )

    def test_each_included_candidate_gets_seven_evidence_tasks(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        for asset_id in batch.target_candidates:
            tasks = [task for task in batch.tasks if task.asset_id == asset_id]
            self.assertEqual(len(tasks), 7)
            self.assertEqual({task.evidence_type for task in tasks}, set(GLOBAL_CORE_EVIDENCE_TYPES))

    def test_no_task_is_auto_verified(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertTrue(batch.tasks)
        self.assertTrue(all(task.manual_verification_required for task in batch.tasks))
        self.assertTrue(all(not task.auto_verified for task in batch.tasks))

    def test_platform_availability_requires_account_specific_manual_evidence(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)
        platform_tasks = [task for task in batch.tasks if task.evidence_type == "platform_availability"]

        self.assertTrue(platform_tasks)
        self.assertTrue(all("account-specific" in task.source_guidance for task in platform_tasks))

    def test_source_config_templates_default_to_no_network_fetch(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertTrue(batch.source_config_templates)
        self.assertTrue(all(template["allow_network_fetch"] is False for template in batch.source_config_templates))
        self.assertTrue(all(template["enabled"] is False for template in batch.source_config_templates))

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(batch.registry_mutation_performed)
        self.assertFalse(batch.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        batch = build_global_core_evidence_batch_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG)

        self.assertFalse(batch.buy_sell_requests_created)
        self.assertFalse(batch.allocation_recommendation_created)
        self.assertFalse(batch.trades_executed)


if __name__ == "__main__":
    unittest.main()
