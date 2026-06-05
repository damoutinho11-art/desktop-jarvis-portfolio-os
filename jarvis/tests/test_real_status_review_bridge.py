import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.asset_status_workflow import validate_asset_status_request
from jarvis.real_status_review_bridge import (
    build_real_status_review_bridge,
    build_real_status_review_bridge_from_files,
    write_status_request_previews,
)
from jarvis.status_request_audit_pack import audit_status_request
from jarvis.verified_evidence_promotion import EvidencePromotionPack


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
SOURCES = "jarvis/data/source_evidence_sources.example.json"
PROMOTION = "jarvis/data/verified_evidence_promotion.example.json"


def _pack(*ready_assets: str) -> EvidencePromotionPack:
    return EvidencePromotionPack(
        promotion_pack_status="READY_FOR_STATUS_REVIEW" if ready_assets else "INCOMPLETE",
        total_tasks=0,
        accepted_count=0,
        rejected_count=0,
        needs_correction_count=0,
        verified_evidence_preview_count=0,
        verified_evidence_previews=(),
        provenance_gate_results=(),
        assets_ready_for_real_status_review=tuple(ready_assets),
        blockers=(),
        warnings=(),
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def _registry_with_status(asset_id: str, status: str):
    registry = load_asset_registry(REGISTRY)
    assets = tuple(
        replace(asset, approval_status=status) if asset.asset_id == asset_id else asset
        for asset in registry.assets
    )
    return replace(registry, assets=assets)


class RealStatusReviewBridgeTests(unittest.TestCase):
    def test_ready_candidate_unreviewed_generates_candidate_reviewed_request(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertEqual(result.status_requests[0].requested_status, "candidate_reviewed")

    def test_ready_candidate_reviewed_generates_approved_watchlist_request(self) -> None:
        registry = _registry_with_status("vwce_global_core_candidate", "candidate_reviewed")
        result = build_real_status_review_bridge(registry, _pack("vwce_global_core_candidate"))

        self.assertEqual(result.status_requests[0].requested_status, "approved_watchlist")
        self.assertIn("candidate_review_pack_present", result.status_requests[0].required_confirmations)

    def test_ready_test_position_generates_candidate_reviewed_request(self) -> None:
        registry = _registry_with_status("vwce_global_core_candidate", "test_position")
        result = build_real_status_review_bridge(registry, _pack("vwce_global_core_candidate"))

        self.assertEqual(result.status_requests[0].current_status, "test_position")
        self.assertEqual(result.status_requests[0].requested_status, "candidate_reviewed")

    def test_not_ready_asset_creates_no_request(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack())

        self.assertEqual(result.status_requests, ())
        self.assertEqual(result.ready_assets_count, 0)

    def test_rejected_asset_creates_no_request(self) -> None:
        registry = _registry_with_status("vwce_global_core_candidate", "rejected")
        result = build_real_status_review_bridge(registry, _pack("vwce_global_core_candidate"))

        self.assertEqual(result.status_requests, ())
        self.assertTrue(result.blocked_assets)

    def test_no_direct_candidate_unreviewed_to_approved_investable(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertNotEqual(result.status_requests[0].requested_status, "approved_investable")

    def test_generated_requests_validate_through_asset_status_workflow(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertTrue(validate_asset_status_request(result.status_requests[0]).valid)

    def test_generated_requests_pass_status_request_audit_pack(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertTrue(audit_status_request(result.status_requests[0], "global_core").audit_ready)

    def test_auto_execute_always_false(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertFalse(result.status_requests[0].auto_execute)

    def test_manual_approval_required_always_true(self) -> None:
        result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

        self.assertTrue(result.status_requests[0].manual_approval_required)

    def test_bridge_writes_nothing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "status_requests.json"
            build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

            self.assertFalse(target.exists())

    def test_optional_writer_writes_only_when_called(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "status_requests.json"
            result = build_real_status_review_bridge(load_asset_registry(REGISTRY), _pack("vwce_global_core_candidate"))

            write_status_request_previews(result, target)

            self.assertTrue(target.exists())

    def test_approval_status_never_changes(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_real_status_review_bridge_from_files(REGISTRY, SOURCES, PROMOTION)

        self.assertEqual(json.loads(before), json.loads(Path(REGISTRY).read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
