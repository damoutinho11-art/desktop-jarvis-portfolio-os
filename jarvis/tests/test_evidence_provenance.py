import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_provenance import (
    EvidenceProvenanceRecord,
    build_candidate_evidence_with_provenance,
    build_evidence_provenance_gate,
    classify_evidence_readiness,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
MARKET_V2 = "jarvis/data/market_data.v2.example.json"
EXPOSURE_V2 = "jarvis/data/asset_exposure.v2.example.json"
POLICY = "jarvis/data/portfolio_policy.example.json"


def _record(
    asset_id: str = "vwce_global_core_candidate",
    evidence_type: str = "fund_metadata",
    source_quality: str = "provider_factsheet",
    verified_by_user: bool = True,
) -> EvidenceProvenanceRecord:
    return EvidenceProvenanceRecord(
        asset_id=asset_id,
        evidence_type=evidence_type,
        source_quality=source_quality,
        source_name="test source",
        as_of="2026-06-04",
        verified_by_user=verified_by_user,
        notes="Synthetic unit-test provenance.",
    )


def _write_provenance(records: list[EvidenceProvenanceRecord]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"records": [record.__dict__ for record in records]}, file)
        return Path(file.name)


class EvidenceProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assets = load_asset_registry(REGISTRY).by_id()

    def test_synthetic_fixture_evidence_does_not_allow_real_status_promotion(self) -> None:
        result = classify_evidence_readiness(
            [_record(source_quality="synthetic_fixture", verified_by_user=False)],
            {"vwce_global_core_candidate": self.assets["vwce_global_core_candidate"]},
        )["vwce_global_core_candidate"]

        self.assertTrue(result.has_test_evidence)
        self.assertFalse(result.real_status_promotion_allowed)

    def test_verified_provider_factsheet_counts_as_review_evidence(self) -> None:
        result = classify_evidence_readiness([_record()], {})["vwce_global_core_candidate"]

        self.assertTrue(result.has_review_evidence)

    def test_verified_platform_screenshot_counts_as_review_evidence(self) -> None:
        result = classify_evidence_readiness(
            [_record(evidence_type="platform_availability", source_quality="platform_screenshot")],
            {},
        )["vwce_global_core_candidate"]

        self.assertTrue(result.has_review_evidence)

    def test_unverified_manual_research_does_not_count_as_review_evidence(self) -> None:
        result = classify_evidence_readiness(
            [_record(source_quality="manual_research", verified_by_user=False)],
            {},
        )["vwce_global_core_candidate"]

        self.assertFalse(result.has_review_evidence)
        self.assertTrue(result.warnings)

    def test_etf_missing_exposure_review_evidence_is_blocked(self) -> None:
        records = [
            _record(evidence_type="fund_metadata"),
            _record(evidence_type="market_data"),
            _record(evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(evidence_type="tax_route", source_quality="manual_research"),
        ]
        result = classify_evidence_readiness(
            records,
            {"vwce_global_core_candidate": self.assets["vwce_global_core_candidate"]},
        )["vwce_global_core_candidate"]

        self.assertFalse(result.real_status_promotion_allowed)
        self.assertIn("exposure_data", result.missing_real_evidence)

    def test_crypto_missing_custody_route_review_evidence_is_blocked(self) -> None:
        asset_id = "btc_crypto_core_candidate"
        records = [
            _record(asset_id=asset_id, evidence_type="fund_metadata"),
            _record(asset_id=asset_id, evidence_type="market_data"),
            _record(asset_id=asset_id, evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(asset_id=asset_id, evidence_type="tax_route", source_quality="manual_research"),
        ]
        result = classify_evidence_readiness(records, {asset_id: self.assets[asset_id]})[asset_id]

        self.assertFalse(result.real_status_promotion_allowed)
        self.assertIn("custody_route", result.missing_real_evidence)

    def test_all_required_etf_review_evidence_allows_real_status_promotion_in_fixture(self) -> None:
        records = [
            _record(evidence_type="fund_metadata"),
            _record(evidence_type="market_data"),
            _record(evidence_type="exposure_data"),
            _record(evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(evidence_type="tax_route", source_quality="manual_research"),
        ]
        result = classify_evidence_readiness(
            records,
            {"vwce_global_core_candidate": self.assets["vwce_global_core_candidate"]},
        )["vwce_global_core_candidate"]

        self.assertTrue(result.real_status_promotion_allowed)

    def test_all_required_crypto_review_evidence_allows_real_status_promotion_in_fixture(self) -> None:
        asset_id = "btc_crypto_core_candidate"
        records = [
            _record(asset_id=asset_id, evidence_type="fund_metadata"),
            _record(asset_id=asset_id, evidence_type="market_data"),
            _record(asset_id=asset_id, evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(asset_id=asset_id, evidence_type="custody_route", source_quality="broker_export"),
            _record(asset_id=asset_id, evidence_type="tax_route", source_quality="manual_research"),
        ]
        result = classify_evidence_readiness(records, {asset_id: self.assets[asset_id]})[asset_id]

        self.assertTrue(result.real_status_promotion_allowed)

    def test_approval_status_is_never_changed(self) -> None:
        provenance_path = _write_provenance(
            [
                _record(evidence_type="fund_metadata"),
                _record(evidence_type="market_data"),
                _record(evidence_type="exposure_data"),
                _record(evidence_type="platform_availability", source_quality="platform_screenshot"),
                _record(evidence_type="tax_route", source_quality="manual_research"),
            ]
        )

        build_evidence_provenance_gate(REGISTRY, provenance_path)
        registry = load_asset_registry(REGISTRY)

        self.assertFalse(any(asset.approval_status == "approved_investable" for asset in registry.assets))

    def test_no_registry_mutation_occurs(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_evidence_provenance_gate(REGISTRY, "jarvis/data/evidence_provenance.example.json")

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_candidate_evidence_wrapper_shows_test_and_real_readiness(self) -> None:
        rows = build_candidate_evidence_with_provenance(
            REGISTRY,
            MARKET_V2,
            EXPOSURE_V2,
            POLICY,
            "jarvis/data/evidence_provenance.example.json",
        )

        vwce = next(row for row in rows if row["asset_id"] == "vwce_global_core_candidate")
        self.assertTrue(vwce["eligible_for_manual_review_test_mode"])
        self.assertFalse(vwce["eligible_for_real_status_review"])


if __name__ == "__main__":
    unittest.main()
