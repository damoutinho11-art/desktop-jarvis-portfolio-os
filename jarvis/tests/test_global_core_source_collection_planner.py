import unittest
from pathlib import Path

from jarvis.global_core_source_collection_planner import build_global_core_source_collection_plan_from_files


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"
PLANNER_CONFIG = "jarvis/data/global_core_source_collection_planner.example.json"


class GlobalCoreSourceCollectionPlannerTests(unittest.TestCase):
    def test_vwce_is_skipped_when_private_reviewed_copy_is_supplied(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertIn("vwce_global_core_candidate", plan.already_reviewed_skipped)
        self.assertNotIn("vwce_global_core_candidate", plan.target_candidates)

    def test_four_remaining_global_core_etfs_are_included_by_default(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertEqual(
            set(plan.target_candidates),
            {
                "ftaw_global_core_candidate",
                "spyi_imie_global_core_candidate",
                "ssac_iusq_global_core_candidate",
                "webn_global_core_candidate",
            },
        )

    def test_twenty_eight_collection_tasks_are_generated(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertEqual(len(plan.tasks), 28)
        self.assertEqual(set(plan.tasks_by_candidate.values()), {7})

    def test_platform_availability_tasks_use_account_specific_manual(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )
        tasks = [task for task in plan.tasks if task.evidence_type == "platform_availability"]

        self.assertTrue(tasks)
        self.assertTrue(all(task.collection_mode == "account_specific_manual" for task in tasks))

    def test_tax_route_tasks_use_manual_tax_review(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )
        tasks = [task for task in plan.tasks if task.evidence_type == "tax_route"]

        self.assertTrue(tasks)
        self.assertTrue(all(task.collection_mode == "manual_tax_review" for task in tasks))

    def test_public_evidence_tasks_use_public_research(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )
        public_tasks = [
            task
            for task in plan.tasks
            if task.evidence_type in {"fund_metadata", "fee_metadata", "distribution_policy", "exposure_data", "market_data"}
        ]

        self.assertTrue(public_tasks)
        self.assertTrue(all(task.collection_mode == "public_research" for task in public_tasks))

    def test_auto_fetch_auto_verified_and_manual_verification_flags(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertTrue(all(task.auto_fetch_allowed is False for task in plan.tasks))
        self.assertTrue(all(task.auto_verified is False for task in plan.tasks))
        self.assertTrue(all(task.manual_verification_required for task in plan.tasks))
        self.assertEqual(plan.auto_fetch_allowed_count, 0)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(plan.registry_mutation_performed)
        self.assertFalse(plan.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        plan = build_global_core_source_collection_plan_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG, PLANNER_CONFIG
        )

        self.assertFalse(plan.buy_sell_requests_created)
        self.assertFalse(plan.allocation_recommendation_created)
        self.assertFalse(plan.trades_executed)


if __name__ == "__main__":
    unittest.main()
