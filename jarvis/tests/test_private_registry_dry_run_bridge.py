import json
import tempfile
import unittest
from pathlib import Path

from jarvis.private_registry_dry_run_bridge import (
    build_private_registry_dry_run_bridge_from_files,
    write_private_registry_copy_from_dry_run,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
PRIVATE_STATUS_CONFIG = "jarvis/data/private_status_review_bridge.example.json"
PRIVATE_DRY_RUN_CONFIG = "jarvis/data/private_registry_dry_run_bridge.example.json"


def _private_records() -> list[dict]:
    return json.loads(Path(PRIVATE_INTAKE).read_text(encoding="utf-8"))["records"]


def _write_intake(records: list[dict]) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"records": records}, file)
        return Path(file.name)


class PrivateRegistryDryRunBridgeTests(unittest.TestCase):
    def test_vwce_private_evidence_produces_candidate_reviewed_dry_run_update(self) -> None:
        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertEqual(len(result.dry_run.simulated_changes), 1)
        change = result.dry_run.simulated_changes[0]
        self.assertEqual(change.current_status, "candidate_unreviewed")
        self.assertEqual(change.requested_status, "candidate_reviewed")
        self.assertTrue(change.would_update)

    def test_after_record_changes_only_approval_status(self) -> None:
        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )
        change = result.dry_run.simulated_changes[0]
        before = dict(change.before_record)
        after = dict(change.after_record)
        before.pop("approval_status")
        after.pop("approval_status")

        self.assertEqual(before, after)

    def test_direct_candidate_unreviewed_to_approved_investable_impossible(self) -> None:
        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertNotEqual(result.dry_run.simulated_changes[0].requested_status, "approved_investable")

    def test_stale_evidence_produces_no_dry_run_update(self) -> None:
        records = _private_records()
        for record in records:
            if record["evidence_type"] == "market_data":
                record["as_of"] = "2026-01-01"
        path = _write_intake(records)

        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, path, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertEqual(result.dry_run.simulated_changes, ())

    def test_incomplete_evidence_produces_no_dry_run_update(self) -> None:
        records = [record for record in _private_records() if record["evidence_type"] != "tax_route"]
        path = _write_intake(records)

        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, path, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertEqual(result.dry_run.simulated_changes, ())

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.updated.json"

            build_private_registry_dry_run_bridge_from_files(
                REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
            )

            self.assertFalse(target.exists())

    def test_optional_writer_only_writes_to_explicit_temp_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.updated.json"
            result = build_private_registry_dry_run_bridge_from_files(
                REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
            )

            write_private_registry_copy_from_dry_run(REGISTRY, result, target)

            self.assertTrue(target.exists())
            self.assertIn('"approval_status": "candidate_reviewed"', target.read_text(encoding="utf-8"))

    def test_registry_source_file_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_private_registry_dry_run_bridge_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_created(self) -> None:
        result = build_private_registry_dry_run_bridge_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
        )

        self.assertFalse(result.buy_sell_requests_created)


if __name__ == "__main__":
    unittest.main()
