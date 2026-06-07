import json
import tempfile
import unittest
from pathlib import Path

from jarvis.reviewed_candidate_snapshot import (
    FUTURE_GATES_REQUIRED,
    ReviewedCandidateSnapshotConfig,
    build_reviewed_candidate_snapshot,
    build_reviewed_candidate_snapshot_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
FRESHNESS_POLICY = "jarvis/data/evidence_freshness_policy.example.json"
SNAPSHOT_CONFIG = "jarvis/data/reviewed_candidate_snapshot.example.json"
TARGET = "vwce_global_core_candidate"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        return Path(file.name)


def _reviewed_registry_payload() -> dict:
    return json.loads(Path(REVIEWED_REGISTRY).read_text(encoding="utf-8"))


def _private_intake_payload() -> dict:
    return json.loads(Path(PRIVATE_INTAKE).read_text(encoding="utf-8"))


class ReviewedCandidateSnapshotTests(unittest.TestCase):
    def test_vwce_reviewed_copy_produces_ready_snapshot(self) -> None:
        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(snapshot.snapshot_status, "READY")
        self.assertEqual(snapshot.asset_id, TARGET)
        self.assertEqual(snapshot.previous_status, "candidate_unreviewed")
        self.assertEqual(snapshot.current_status, "candidate_reviewed")
        self.assertEqual(snapshot.status_transition, "candidate_unreviewed -> candidate_reviewed")
        self.assertEqual(snapshot.verified_evidence_count, 7)
        self.assertEqual(snapshot.freshness_status, "fresh")
        self.assertTrue(snapshot.private_evidence_present)

    def test_source_registry_is_not_mutated(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_approved_investable_status_blocks(self) -> None:
        payload = _reviewed_registry_payload()
        for asset in payload["assets"]:
            if asset["asset_id"] == TARGET:
                asset["approval_status"] = "approved_investable"
        reviewed_path = _write_json(payload)

        snapshot = build_reviewed_candidate_snapshot(
            SOURCE_REGISTRY,
            reviewed_path,
            PRIVATE_INTAKE,
            FRESHNESS_POLICY,
            ReviewedCandidateSnapshotConfig(TARGET),
        )

        self.assertEqual(snapshot.snapshot_status, "BLOCKED")
        self.assertFalse(snapshot.not_approved_investable)
        self.assertTrue(any("approved_investable" in blocker for blocker in snapshot.blockers))

    def test_unexpected_extra_registry_diff_blocks(self) -> None:
        payload = _reviewed_registry_payload()
        for asset in payload["assets"]:
            if asset["asset_id"] != TARGET:
                asset["notes"] = asset["notes"] + " unexpected mutation"
                break
        reviewed_path = _write_json(payload)

        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, reviewed_path, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(snapshot.snapshot_status, "BLOCKED")
        self.assertTrue(any("unexpected reviewed registry diff" in blocker for blocker in snapshot.blockers))

    def test_stale_evidence_blocks(self) -> None:
        payload = _private_intake_payload()
        for record in payload["records"]:
            if record["evidence_type"] == "market_data":
                record["as_of"] = "2026-01-01"
        intake_path = _write_json(payload)

        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, intake_path, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(snapshot.snapshot_status, "BLOCKED")
        self.assertEqual(snapshot.freshness_status, "blocked")

    def test_missing_evidence_blocks(self) -> None:
        payload = _private_intake_payload()
        payload["records"] = [record for record in payload["records"] if record["evidence_type"] != "tax_route"]
        intake_path = _write_json(payload)

        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, intake_path, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(snapshot.snapshot_status, "BLOCKED")
        self.assertTrue(any("missing" in blocker or "provenance" in blocker for blocker in snapshot.blockers))

    def test_future_gates_present(self) -> None:
        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertEqual(snapshot.future_gates_required, FUTURE_GATES_REQUIRED)

    def test_no_buy_sell_requests_are_created(self) -> None:
        snapshot = build_reviewed_candidate_snapshot_from_files(
            SOURCE_REGISTRY, REVIEWED_REGISTRY, PRIVATE_INTAKE, FRESHNESS_POLICY, SNAPSHOT_CONFIG
        )

        self.assertFalse(snapshot.buy_sell_requests_created)
        self.assertFalse(snapshot.allocation_recommendation_created)
        self.assertFalse(snapshot.trades_executed)


if __name__ == "__main__":
    unittest.main()
