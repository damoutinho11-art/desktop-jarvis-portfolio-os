import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_provenance import EvidenceProvenanceRecord
from jarvis.verified_evidence_intake import (
    build_verified_evidence_pack,
    build_verified_evidence_pack_from_files,
    validate_intake_record,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"


def _record(**overrides) -> dict:
    record = {
        "evidence_id": "evidence_valid",
        "asset_id": "vwce_global_core_candidate",
        "evidence_type": "fund_metadata",
        "source_quality": "provider_factsheet",
        "source_name": "Provider factsheet",
        "as_of": "2026-06-01",
        "verified_by_user": True,
        "verification_notes": "User verified this evidence.",
        "file_reference": "manual_evidence/test.pdf",
        "url_reference": None,
        "extracted_facts": {"field": "value"},
        "warnings": [],
    }
    record.update(overrides)
    return record


class VerifiedEvidenceIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_asset_registry(REGISTRY)
        cls.assets = cls.registry.by_id()

    def test_valid_intake_record_accepted(self) -> None:
        result = validate_intake_record(_record(), self.assets)

        self.assertTrue(result.valid)
        self.assertIsNotNone(result.record)

    def test_unknown_asset_id_rejected(self) -> None:
        result = validate_intake_record(_record(asset_id="unknown_asset"), self.assets)

        self.assertFalse(result.valid)
        self.assertIn("unknown asset_id unknown_asset.", result.blockers)

    def test_unsupported_evidence_type_rejected(self) -> None:
        result = validate_intake_record(_record(evidence_type="rumor"), self.assets)

        self.assertFalse(result.valid)
        self.assertIn("unsupported evidence_type rumor.", result.blockers)

    def test_unsupported_source_quality_rejected(self) -> None:
        result = validate_intake_record(_record(source_quality="chat_room"), self.assets)

        self.assertFalse(result.valid)
        self.assertIn("unsupported source_quality chat_room.", result.blockers)

    def test_verified_by_user_true_requires_verification_notes(self) -> None:
        result = validate_intake_record(_record(verification_notes=""), self.assets)

        self.assertFalse(result.valid)
        self.assertIn("verification_notes must be non-empty text.", result.blockers)

    def test_unverified_record_does_not_count_as_review_evidence(self) -> None:
        pack = build_verified_evidence_pack(self.registry, [_record(verified_by_user=False, verification_notes="")])
        result = next(row for row in pack.provenance_gate.gate_results if row.asset_id == "vwce_global_core_candidate")

        self.assertFalse(result.has_review_evidence)

    def test_stale_evidence_warning(self) -> None:
        result = validate_intake_record(_record(as_of="2025-01-01"), self.assets)

        self.assertTrue(any("older than 180 days" in warning for warning in result.warnings))

    def test_missing_file_url_warning(self) -> None:
        result = validate_intake_record(_record(file_reference=None, url_reference=None), self.assets)

        self.assertTrue(any("file_reference and url_reference are both missing" in warning for warning in result.warnings))

    def test_conversion_to_evidence_provenance_record(self) -> None:
        result = validate_intake_record(_record(evidence_type="protocol_metadata"), self.assets)

        self.assertIsInstance(result.provenance_record, EvidenceProvenanceRecord)
        self.assertEqual(result.provenance_record.evidence_type, "fund_metadata")

    def test_verified_etf_evidence_allows_real_status_only_when_complete(self) -> None:
        complete = [
            _record(evidence_id="fund", evidence_type="fund_metadata"),
            _record(evidence_id="market", evidence_type="market_data", source_quality="broker_export"),
            _record(evidence_id="exposure", evidence_type="exposure_data"),
            _record(evidence_id="platform", evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(evidence_id="tax", evidence_type="tax_route", source_quality="manual_research"),
        ]
        pack = build_verified_evidence_pack(self.registry, complete)

        self.assertIn("vwce_global_core_candidate", pack.assets_with_real_status_promotion_allowed)

    def test_incomplete_etf_evidence_remains_blocked(self) -> None:
        incomplete = [
            _record(evidence_id="fund", evidence_type="fund_metadata"),
            _record(evidence_id="market", evidence_type="market_data", source_quality="broker_export"),
        ]
        pack = build_verified_evidence_pack(self.registry, incomplete)

        self.assertNotIn("vwce_global_core_candidate", pack.assets_with_real_status_promotion_allowed)

    def test_verified_crypto_custody_evidence_contributes_to_crypto_readiness(self) -> None:
        crypto = [
            _record(
                evidence_id="btc_fund",
                asset_id="btc_crypto_core_candidate",
                evidence_type="protocol_metadata",
                source_quality="manual_research",
            ),
            _record(
                evidence_id="btc_market",
                asset_id="btc_crypto_core_candidate",
                evidence_type="market_data",
                source_quality="broker_export",
            ),
            _record(
                evidence_id="btc_platform",
                asset_id="btc_crypto_core_candidate",
                evidence_type="platform_availability",
                source_quality="platform_screenshot",
            ),
            _record(
                evidence_id="btc_custody",
                asset_id="btc_crypto_core_candidate",
                evidence_type="custody_route",
                source_quality="broker_export",
            ),
            _record(
                evidence_id="btc_tax",
                asset_id="btc_crypto_core_candidate",
                evidence_type="tax_route",
                source_quality="manual_research",
            ),
        ]
        pack = build_verified_evidence_pack(self.registry, crypto)

        self.assertIn("btc_crypto_core_candidate", pack.assets_with_real_status_promotion_allowed)

    def test_approval_status_never_changes(self) -> None:
        build_verified_evidence_pack_from_files(REGISTRY, "jarvis/data/verified_evidence_intake.example.json")
        registry = load_asset_registry(REGISTRY)

        self.assertFalse(any(asset.approval_status == "approved_investable" for asset in registry.assets))

    def test_no_registry_mutation_occurs(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_verified_evidence_pack_from_files(REGISTRY, "jarvis/data/verified_evidence_intake.example.json")

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
