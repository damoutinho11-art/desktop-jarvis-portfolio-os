import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_collection_pack import build_evidence_collection_pack


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
INTAKE = "jarvis/data/verified_evidence_intake.example.json"


class EvidenceCollectionPackTests(unittest.TestCase):
    def test_collection_pack_generates_tasks_for_missing_etf_evidence(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)

        self.assertTrue(any(task.asset_type == "ETF" for task in pack.tasks))
        self.assertTrue(any(task.asset_id == "vwce_global_core_candidate" for task in pack.tasks))

    def test_collection_pack_generates_tasks_for_missing_crypto_evidence(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)

        self.assertTrue(any(task.asset_type == "crypto" for task in pack.tasks))

    def test_global_core_blocking_evidence_gets_high_priority(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)
        task = next(task for task in pack.tasks if task.asset_id == "spyi_imie_global_core_candidate")

        self.assertEqual(task.priority, "high")

    def test_optional_sleeve_blocking_evidence_gets_medium_priority(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)
        task = next(task for task in pack.tasks if task.asset_id == "sxrv_cndx_growth_candidate")

        self.assertEqual(task.priority, "medium")

    def test_task_contains_valid_intake_record_template_fields(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)
        template = pack.tasks[0].intake_record_template

        self.assertEqual(
            set(template),
            {
                "evidence_id",
                "asset_id",
                "evidence_type",
                "source_quality",
                "source_name",
                "as_of",
                "verified_by_user",
                "verification_notes",
                "file_reference",
                "url_reference",
                "extracted_facts",
                "warnings",
            },
        )

    def test_suggested_source_quality_options_match_evidence_type(self) -> None:
        pack = build_evidence_collection_pack(REGISTRY, INTAKE)
        platform_task = next(
            task for task in pack.tasks if task.asset_type == "ETF" and task.evidence_type == "platform_availability"
        )
        crypto_market_task = next(
            task for task in pack.tasks if task.asset_type == "crypto" and task.evidence_type == "market_data"
        )

        self.assertEqual(platform_task.suggested_source_quality_options, ("platform_screenshot",))
        self.assertEqual(crypto_market_task.suggested_source_quality_options, ("broker_export", "verified_api_snapshot"))

    def test_candidate_approval_status_never_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_evidence_collection_pack(REGISTRY, INTAKE)
        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        self.assertEqual(before, after)

    def test_no_registry_mutation_occurs(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_evidence_collection_pack(REGISTRY, INTAKE)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
