import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_verification_queue import build_evidence_verification_queue
from jarvis.verified_evidence_promotion import (
    EvidencePromotionDecisionInput,
    build_verified_evidence_promotion_pack,
    build_verified_evidence_promotion_pack_from_files,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
SOURCES = "jarvis/data/source_evidence_sources.example.json"
PROMOTION = "jarvis/data/verified_evidence_promotion.example.json"


def _decision(task_id: str, decision: str = "accept") -> EvidencePromotionDecisionInput:
    return EvidencePromotionDecisionInput(
        task_id=task_id,
        decision=decision,
        decided_at="2026-06-05T12:00:00+00:00",
        decided_by="Diogo",
        notes=f"Manual {decision} decision.",
    )


def _source(asset_id: str, evidence_type: str, source_type: str = "provider_factsheet_pdf") -> dict:
    return {
        "source_id": f"{asset_id}_{evidence_type}_source",
        "asset_id": asset_id,
        "evidence_type": evidence_type,
        "source_type": source_type,
        "source_name": f"{asset_id} {evidence_type} source",
        "url_reference": "https://example.invalid/source",
        "local_fixture_path": None,
        "enabled": True,
        "notes": "Unit-test source.",
        "static_content": "ticker: TEST\nprovider: Provider\ncurrency: EUR\nplatform_name: Lightyear\navailability_status: available",
    }


def _write_sources(sources: list[dict]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"sources": sources}, file)
        return Path(file.name)


class VerifiedEvidencePromotionTests(unittest.TestCase):
    def test_accepted_decision_creates_verified_evidence_preview(self) -> None:
        pack = build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertEqual(pack.accepted_count, 1)
        self.assertEqual(pack.verified_evidence_preview_count, 1)

    def test_rejected_decision_creates_no_verified_evidence_preview(self) -> None:
        queue = build_evidence_verification_queue(REGISTRY, SOURCES)
        task = queue.tasks[0]
        pack = build_verified_evidence_promotion_pack(REGISTRY, SOURCES, [_decision(task.task_id, "reject")])

        self.assertEqual(pack.rejected_count, 1)
        self.assertEqual(pack.verified_evidence_preview_count, 0)

    def test_needs_correction_creates_no_verified_evidence_preview(self) -> None:
        queue = build_evidence_verification_queue(REGISTRY, SOURCES)
        task = queue.tasks[0]
        pack = build_verified_evidence_promotion_pack(REGISTRY, SOURCES, [_decision(task.task_id, "needs_correction")])

        self.assertEqual(pack.needs_correction_count, 1)
        self.assertEqual(pack.verified_evidence_preview_count, 0)

    def test_verified_evidence_preview_has_verified_by_user_true(self) -> None:
        pack = build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertTrue(pack.verified_evidence_previews[0]["verified_by_user"])

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "preview.json"
            build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

            self.assertFalse(target.exists())

    def test_incomplete_evidence_keeps_asset_not_ready(self) -> None:
        pack = build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertNotIn("vwce_global_core_candidate", pack.assets_ready_for_real_status_review)

    def test_complete_etf_verified_evidence_can_mark_ready_in_fixture_only(self) -> None:
        asset_id = "vwce_global_core_candidate"
        sources = [
            _source(asset_id, "fund_metadata"),
            _source(asset_id, "market_data", "provider_factsheet_pdf"),
            _source(asset_id, "exposure_data"),
            _source(asset_id, "platform_availability", "public_platform_page"),
            _source(asset_id, "tax_route", "manual_url_reference"),
        ]
        sources_path = _write_sources(sources)
        queue = build_evidence_verification_queue(REGISTRY, sources_path)
        decisions = [_decision(task.task_id) for task in queue.tasks]
        pack = build_verified_evidence_promotion_pack(REGISTRY, sources_path, decisions)

        self.assertIn(asset_id, pack.assets_ready_for_real_status_review)

    def test_complete_crypto_verified_evidence_can_mark_ready_in_fixture_only(self) -> None:
        asset_id = "btc_crypto_core_candidate"
        sources = [
            _source(asset_id, "fund_metadata", "manual_url_reference"),
            _source(asset_id, "market_data", "public_crypto_market_api"),
            _source(asset_id, "platform_availability", "public_platform_page"),
            _source(asset_id, "custody_route", "manual_url_reference"),
            _source(asset_id, "tax_route", "manual_url_reference"),
        ]
        sources_path = _write_sources(sources)
        queue = build_evidence_verification_queue(REGISTRY, sources_path)
        decisions = [_decision(task.task_id) for task in queue.tasks]
        pack = build_verified_evidence_promotion_pack(REGISTRY, sources_path, decisions)

        self.assertIn(asset_id, pack.assets_ready_for_real_status_review)

    def test_approval_status_never_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)
        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        self.assertEqual(before, after)

    def test_registry_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_created(self) -> None:
        pack = build_verified_evidence_promotion_pack_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertFalse(pack.buy_sell_requests_created)


if __name__ == "__main__":
    unittest.main()
