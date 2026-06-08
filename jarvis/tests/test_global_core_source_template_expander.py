import unittest
from pathlib import Path

from jarvis.global_core_source_template_expander import build_global_core_source_template_expansion_from_files


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
QUEUE_CONFIG = "jarvis/data/multi_candidate_review_queue.example.json"
BATCH_CONFIG = "jarvis/data/global_core_evidence_batch.example.json"
EXPANDER_CONFIG = "jarvis/data/global_core_source_template_expander.example.json"


class GlobalCoreSourceTemplateExpanderTests(unittest.TestCase):
    def test_vwce_is_skipped_when_private_reviewed_copy_is_supplied(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertIn("vwce_global_core_candidate", expansion.already_reviewed_skipped)
        self.assertNotIn("vwce_global_core_candidate", expansion.target_candidates)

    def test_four_remaining_global_core_etfs_are_included(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertEqual(
            set(expansion.target_candidates),
            {
                "ftaw_global_core_candidate",
                "spyi_imie_global_core_candidate",
                "ssac_iusq_global_core_candidate",
                "webn_global_core_candidate",
            },
        )

    def test_each_candidate_gets_seven_templates(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertEqual(set(expansion.templates_by_candidate.values()), {7})
        self.assertEqual(len(expansion.templates), 28)

    def test_all_templates_are_disabled_and_no_network_fetch(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertTrue(all(template.enabled is False for template in expansion.templates))
        self.assertTrue(all(template.allow_network_fetch is False for template in expansion.templates))
        self.assertEqual(expansion.disabled_templates_count, 28)
        self.assertEqual(expansion.network_fetch_enabled_count, 0)

    def test_no_template_is_auto_verified(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertTrue(all(template.manual_verification_required for template in expansion.templates))
        self.assertTrue(all(not template.auto_verified for template in expansion.templates))

    def test_platform_availability_requires_account_specific_evidence(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )
        platform_templates = [template for template in expansion.templates if template.evidence_type == "platform_availability"]

        self.assertTrue(platform_templates)
        self.assertTrue(all("account-specific" in template.source_guidance for template in platform_templates))

    def test_tax_route_requires_manual_review(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )
        tax_templates = [template for template in expansion.templates if template.evidence_type == "tax_route"]

        self.assertTrue(tax_templates)
        self.assertTrue(all("Manual tax/account route review required" in template.source_guidance for template in tax_templates))

    def test_market_data_requires_price_currency_source_and_as_of_guidance(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )
        market_templates = [template for template in expansion.templates if template.evidence_type == "market_data"]

        self.assertTrue(market_templates)
        for template in market_templates:
            guidance = template.source_guidance.lower()
            self.assertIn("price", guidance)
            self.assertIn("currency", guidance)
            self.assertIn("source", guidance)
            self.assertIn("as_of date", guidance)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(expansion.registry_mutation_performed)
        self.assertFalse(expansion.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        expansion = build_global_core_source_template_expansion_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, QUEUE_CONFIG, BATCH_CONFIG, EXPANDER_CONFIG
        )

        self.assertFalse(expansion.buy_sell_requests_created)
        self.assertFalse(expansion.allocation_recommendation_created)
        self.assertFalse(expansion.trades_executed)


if __name__ == "__main__":
    unittest.main()
