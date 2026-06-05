import unittest

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_collection_checklist import build_evidence_collection_checklist


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"


def _record(asset_id: str = "vwce_global_core_candidate", evidence_type: str = "fund_metadata", **overrides) -> dict:
    record = {
        "evidence_id": f"{asset_id}_{evidence_type}",
        "asset_id": asset_id,
        "evidence_type": evidence_type,
        "source_quality": "provider_factsheet",
        "source_name": "Verified source",
        "as_of": "2026-06-01",
        "verified_by_user": True,
        "verification_notes": "User verified evidence.",
        "file_reference": "manual_evidence/test.pdf",
        "url_reference": None,
        "extracted_facts": {"field": "value"},
        "warnings": [],
    }
    record.update(overrides)
    return record


def _item(result, asset_id: str, evidence_type: str):
    checklist = next(checklist for checklist in result.checklists if checklist.asset_id == asset_id)
    return next(item for item in checklist.items if item.evidence_type == evidence_type)


class EvidenceCollectionChecklistTests(unittest.TestCase):
    def test_etf_checklist_includes_required_etf_evidence(self) -> None:
        result = build_evidence_collection_checklist(REGISTRY, [])
        checklist = next(item for item in result.checklists if item.asset_id == "vwce_global_core_candidate")
        evidence_types = {item.evidence_type for item in checklist.items}

        self.assertEqual(
            evidence_types,
            {
                "provider_factsheet",
                "fund_metadata",
                "fee_metadata",
                "distribution_policy",
                "platform_availability",
                "tax_route",
                "exposure_data",
                "market_data",
            },
        )

    def test_crypto_checklist_includes_required_crypto_evidence(self) -> None:
        result = build_evidence_collection_checklist(REGISTRY, [])
        checklist = next(item for item in result.checklists if item.asset_id == "btc_crypto_core_candidate")
        evidence_types = {item.evidence_type for item in checklist.items}

        self.assertEqual(
            evidence_types,
            {
                "protocol_metadata",
                "market_data",
                "platform_availability",
                "custody_route",
                "tax_route",
                "crypto_risk_notes",
            },
        )

    def test_verified_evidence_marks_present_verified(self) -> None:
        result = build_evidence_collection_checklist(REGISTRY, [_record(evidence_type="market_data", source_quality="broker_export")])

        self.assertEqual(_item(result, "vwce_global_core_candidate", "market_data").current_status, "present_verified")

    def test_unverified_evidence_marks_present_unverified_and_blocking(self) -> None:
        result = build_evidence_collection_checklist(
            REGISTRY,
            [_record(evidence_type="market_data", source_quality="broker_export", verified_by_user=False, verification_notes="")],
        )
        item = _item(result, "vwce_global_core_candidate", "market_data")

        self.assertEqual(item.current_status, "present_unverified")
        self.assertTrue(item.blocking_for_real_review)

    def test_stale_evidence_marks_stale_and_blocking(self) -> None:
        result = build_evidence_collection_checklist(
            REGISTRY,
            [_record(evidence_type="market_data", source_quality="broker_export", as_of="2025-01-01")],
        )
        item = _item(result, "vwce_global_core_candidate", "market_data")

        self.assertEqual(item.current_status, "stale")
        self.assertTrue(item.blocking_for_real_review)

    def test_synthetic_evidence_does_not_satisfy_real_checklist(self) -> None:
        result = build_evidence_collection_checklist(
            REGISTRY,
            [_record(evidence_type="market_data", source_quality="synthetic_fixture")],
        )
        item = _item(result, "vwce_global_core_candidate", "market_data")

        self.assertEqual(item.current_status, "present_unverified")
        self.assertTrue(item.blocking_for_real_review)

    def test_complete_etf_checklist_possible_in_test_fixture(self) -> None:
        records = [
            _record(evidence_type="fund_metadata"),
            _record(evidence_type="fee_metadata", source_quality="provider_factsheet"),
            _record(evidence_type="distribution_policy", source_quality="provider_factsheet"),
            _record(evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(evidence_type="tax_route", source_quality="manual_research"),
            _record(evidence_type="exposure_data", source_quality="provider_factsheet"),
            _record(evidence_type="market_data", source_quality="broker_export"),
        ]
        result = build_evidence_collection_checklist(REGISTRY, records)
        checklist = next(checklist for checklist in result.checklists if checklist.asset_id == "vwce_global_core_candidate")

        self.assertTrue(checklist.collection_complete)

    def test_incomplete_etf_checklist_blocked(self) -> None:
        result = build_evidence_collection_checklist(REGISTRY, [_record(evidence_type="fund_metadata")])
        checklist = next(checklist for checklist in result.checklists if checklist.asset_id == "vwce_global_core_candidate")

        self.assertFalse(checklist.collection_complete)

    def test_complete_crypto_checklist_possible_in_test_fixture(self) -> None:
        asset_id = "btc_crypto_core_candidate"
        records = [
            _record(asset_id=asset_id, evidence_type="protocol_metadata", source_quality="manual_research"),
            _record(asset_id=asset_id, evidence_type="market_data", source_quality="broker_export"),
            _record(asset_id=asset_id, evidence_type="platform_availability", source_quality="platform_screenshot"),
            _record(asset_id=asset_id, evidence_type="custody_route", source_quality="broker_export"),
            _record(asset_id=asset_id, evidence_type="tax_route", source_quality="manual_research"),
        ]
        result = build_evidence_collection_checklist(REGISTRY, records)
        checklist = next(checklist for checklist in result.checklists if checklist.asset_id == asset_id)

        self.assertTrue(checklist.collection_complete)

    def test_approval_status_never_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_evidence_collection_checklist(REGISTRY, [_record(evidence_type="fund_metadata")])
        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
