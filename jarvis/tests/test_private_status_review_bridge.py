import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.asset_status_workflow import validate_asset_status_request
from jarvis.private_status_review_bridge import (
    build_private_status_review_bridge_from_files,
    write_private_status_request_previews,
)
from jarvis.status_request_audit_pack import audit_status_request


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
CONFIG = "jarvis/data/private_status_review_bridge.example.json"


def _write_intake(records: list[dict]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"records": records}, file)
        return Path(file.name)


def _private_records() -> list[dict]:
    return json.loads(Path(PRIVATE_INTAKE).read_text(encoding="utf-8"))["records"]


class PrivateStatusReviewBridgeTests(unittest.TestCase):
    def test_vwce_complete_verified_fresh_evidence_creates_candidate_reviewed_preview(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertEqual(len(result.request_previews), 1)
        request = result.request_previews[0].status_request
        self.assertEqual(request.asset_id, "vwce_global_core_candidate")
        self.assertEqual(request.current_status, "candidate_unreviewed")
        self.assertEqual(request.requested_status, "candidate_reviewed")

    def test_stale_evidence_blocks_request_preview(self) -> None:
        records = _private_records()
        for record in records:
            if record["evidence_type"] == "market_data":
                record["as_of"] = "2026-01-01"
        path = _write_intake(records)

        result = build_private_status_review_bridge_from_files(REGISTRY, path, POLICY, CONFIG)

        self.assertEqual(result.request_previews, ())
        self.assertTrue(result.blocked_assets)

    def test_incomplete_evidence_blocks_request_preview(self) -> None:
        records = [record for record in _private_records() if record["evidence_type"] != "tax_route"]
        path = _write_intake(records)

        result = build_private_status_review_bridge_from_files(REGISTRY, path, POLICY, CONFIG)

        self.assertEqual(result.request_previews, ())
        self.assertTrue(result.blocked_assets)

    def test_direct_candidate_unreviewed_to_approved_investable_impossible(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertNotEqual(result.request_previews[0].status_request.requested_status, "approved_investable")

    def test_generated_request_validates_through_asset_status_workflow(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertTrue(validate_asset_status_request(result.request_previews[0].status_request).valid)

    def test_generated_request_passes_status_request_audit_pack(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertTrue(audit_status_request(result.request_previews[0].status_request, "global_core").audit_ready)

    def test_auto_execute_always_false(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertFalse(result.request_previews[0].status_request.auto_execute)

    def test_manual_approval_required_always_true(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertTrue(result.request_previews[0].status_request.manual_approval_required)

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "private_status_requests.json"

            build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

            self.assertFalse(target.exists())

    def test_optional_writer_writes_to_explicit_path_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "private_status_requests.json"
            result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

            write_private_status_request_previews(result, target)

            self.assertTrue(target.exists())
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertIn("freshness_summary", payload["requests"][0])

    def test_approval_status_never_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        self.assertEqual(before, after)

    def test_registry_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_created(self) -> None:
        result = build_private_status_review_bridge_from_files(REGISTRY, PRIVATE_INTAKE, POLICY, CONFIG)

        self.assertFalse(result.buy_sell_requests_created)


if __name__ == "__main__":
    unittest.main()
