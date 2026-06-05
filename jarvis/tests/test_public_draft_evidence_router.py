import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.public_draft_evidence_router import (
    build_public_draft_evidence_router_pack,
    routed_records_to_verification_tasks,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"


def _records_for(asset_id: str, evidence_type: str):
    pack = build_public_draft_evidence_router_pack(REGISTRY, PUBLIC_SOURCES)
    return [
        record
        for route in pack.route_results
        for record in route.routed_evidence_records
        if record["asset_id"] == asset_id and record["evidence_type"] == evidence_type
    ]


def _write_sources(content: str) -> Path:
    source = {
        "source_id": "insufficient_public_source",
        "asset_id": "vwce_global_core_candidate",
        "evidence_type": "fund_metadata",
        "source_type": "provider_product_page",
        "source_name": "Insufficient public source",
        "url_reference": "https://example.invalid/insufficient",
        "enabled": True,
        "allow_network_fetch": False,
        "local_fixture_content": content,
        "notes": "Unit-test insufficient fixture.",
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"sources": [source]}, file)
        return Path(file.name)


class PublicDraftEvidenceRouterTests(unittest.TestCase):
    def test_vwce_provider_factsheet_source_routes_to_fund_metadata(self) -> None:
        records = _records_for("vwce_global_core_candidate", "fund_metadata")

        self.assertTrue(records)
        self.assertIn("fund_name", records[0]["extracted_facts"])

    def test_ter_fact_routes_to_fee_metadata(self) -> None:
        records = _records_for("vwce_global_core_candidate", "fee_metadata")

        self.assertTrue(records)
        self.assertIn("ter_or_fee", records[0]["extracted_facts"])

    def test_distribution_policy_fact_routes_to_distribution_policy(self) -> None:
        records = _records_for("vwce_global_core_candidate", "distribution_policy")

        self.assertTrue(records)
        self.assertIn("distribution_policy", records[0]["extracted_facts"])

    def test_platform_facts_route_to_platform_availability(self) -> None:
        records = _records_for("vwce_global_core_candidate", "platform_availability")

        self.assertTrue(records)
        self.assertIn("platform_name", records[0]["extracted_facts"])
        self.assertIn("availability_status", records[0]["extracted_facts"])

    def test_insufficient_facts_create_missing_route_warning(self) -> None:
        path = _write_sources("ticker: VWCE")
        pack = build_public_draft_evidence_router_pack(REGISTRY, path)

        self.assertGreater(pack.summary.missing_routes_count, 0)
        self.assertTrue(any("missing route" in warning for warning in pack.summary.warnings))

    def test_no_routed_record_has_verified_by_user_true(self) -> None:
        pack = build_public_draft_evidence_router_pack(REGISTRY, PUBLIC_SOURCES)
        records = [record for route in pack.route_results for record in route.routed_evidence_records]

        self.assertTrue(records)
        self.assertTrue(all(record["verified_by_user"] is False for record in records))

    def test_no_approval_status_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_public_draft_evidence_router_pack(REGISTRY, PUBLIC_SOURCES)

        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        self.assertEqual(before, after)

    def test_no_registry_mutation(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_public_draft_evidence_router_pack(REGISTRY, PUBLIC_SOURCES)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_optional_verification_task_conversion_creates_pending_tasks_only(self) -> None:
        pack = build_public_draft_evidence_router_pack(REGISTRY, PUBLIC_SOURCES)
        records = [record for route in pack.route_results for record in route.routed_evidence_records]
        tasks = routed_records_to_verification_tasks(records)

        self.assertTrue(tasks)
        self.assertTrue(all(task.verification_status == "pending_user_verification" for task in tasks))

    def test_crypto_market_source_routes_to_market_data(self) -> None:
        records = _records_for("btc_crypto_core_candidate", "market_data")

        self.assertTrue(records)
        self.assertIn("ticker", records[0]["extracted_facts"])


if __name__ == "__main__":
    unittest.main()
