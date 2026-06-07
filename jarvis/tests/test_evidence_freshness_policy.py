import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_freshness_policy import (
    EvidenceFreshnessConfig,
    EvidenceFreshnessRule,
    build_evidence_freshness_pack,
    build_evidence_freshness_pack_from_files,
    load_evidence_freshness_config,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"


def _record(evidence_type: str, as_of: str) -> dict:
    return {
        "evidence_id": f"unit_{evidence_type}",
        "asset_id": "vwce_global_core_candidate",
        "evidence_type": evidence_type,
        "source_quality": "manual_research",
        "source_name": f"Unit {evidence_type}",
        "as_of": as_of,
        "verified_by_user": True,
        "verification_notes": "Unit-test verified evidence.",
        "url_reference": "https://example.invalid/unit",
        "extracted_facts": {"ticker": "VWCE"},
        "warnings": [],
    }


def _write_intake(records: list[dict]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"records": records}, file)
        return Path(file.name)


def _config(rule: EvidenceFreshnessRule) -> EvidenceFreshnessConfig:
    return EvidenceFreshnessConfig(
        target_asset_ids=("vwce_global_core_candidate",),
        rules=(rule,),
        public_source_fetch_path=PUBLIC_SOURCES,
    )


class EvidenceFreshnessPolicyTests(unittest.TestCase):
    def test_fresh_vwce_evidence_remains_usable(self) -> None:
        pack = build_evidence_freshness_pack_from_files(REGISTRY, PRIVATE_INTAKE, POLICY)
        result = next(item for item in pack.results if item.evidence_type == "fund_metadata")

        self.assertEqual(result.freshness_status, "fresh")
        self.assertEqual(result.recommended_action, "keep_current_evidence")

    def test_default_vwce_policy_has_no_missing_etf_evidence(self) -> None:
        pack = build_evidence_freshness_pack_from_files(REGISTRY, PRIVATE_INTAKE, POLICY)

        self.assertEqual(pack.summary.missing_count, 0)

    def test_stale_market_data_recommends_public_refresh_draft(self) -> None:
        rule = EvidenceFreshnessRule("market_data", 7, "public_auto_refresh_allowed", ("public_market_data_page",), "Market.")
        path = _write_intake([_record("market_data", "2026-05-01")])
        pack = build_evidence_freshness_pack(REGISTRY, path, _config(rule))
        result = pack.results[0]

        self.assertEqual(result.freshness_status, "stale")
        self.assertEqual(result.recommended_action, "public_refresh_draft")

    def test_stale_platform_availability_recommends_manual_account_reverification(self) -> None:
        rule = EvidenceFreshnessRule("platform_availability", 90, "account_specific_manual_required", ("public_platform_page",), "Platform.")
        path = _write_intake([_record("platform_availability", "2026-01-01")])
        result = build_evidence_freshness_pack(REGISTRY, path, _config(rule)).results[0]

        self.assertEqual(result.recommended_action, "manual_account_reverification")
        self.assertTrue(result.account_specific_required)

    def test_stale_tax_route_recommends_manual_review(self) -> None:
        rule = EvidenceFreshnessRule("tax_route", 180, "manual_refresh_required", ("manual_url_reference",), "Tax.")
        path = _write_intake([_record("tax_route", "2025-01-01")])
        result = build_evidence_freshness_pack(REGISTRY, path, _config(rule)).results[0]

        self.assertEqual(result.recommended_action, "manual_review")
        self.assertTrue(result.manual_refresh_required)

    def test_missing_evidence_reports_missing(self) -> None:
        rule = EvidenceFreshnessRule("exposure_data", 90, "public_auto_refresh_allowed", ("provider_factsheet_pdf",), "Exposure.")
        path = _write_intake([])
        result = build_evidence_freshness_pack(REGISTRY, path, _config(rule)).results[0]

        self.assertEqual(result.freshness_status, "missing")

    def test_public_auto_refresh_creates_draft_only_with_verified_false(self) -> None:
        rule = EvidenceFreshnessRule("market_data", 7, "public_auto_refresh_allowed", ("public_market_data_page",), "Market.")
        path = _write_intake([_record("market_data", "2026-05-01")])
        pack = build_evidence_freshness_pack(REGISTRY, path, _config(rule))

        self.assertTrue(pack.draft_refresh_records)
        self.assertTrue(all(record["verified_by_user"] is False for record in pack.draft_refresh_records))

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "refresh.json"

            build_evidence_freshness_pack_from_files(REGISTRY, PRIVATE_INTAKE, POLICY)

            self.assertFalse(target.exists())

    def test_no_approval_status_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_evidence_freshness_pack_from_files(REGISTRY, PRIVATE_INTAKE, POLICY)

        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        self.assertEqual(before, after)

    def test_registry_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_evidence_freshness_pack_from_files(REGISTRY, PRIVATE_INTAKE, POLICY)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_policy_config_loads_default_rules(self) -> None:
        config = load_evidence_freshness_config(POLICY)

        self.assertIn("market_data", {rule.evidence_type for rule in config.rules})


if __name__ == "__main__":
    unittest.main()
