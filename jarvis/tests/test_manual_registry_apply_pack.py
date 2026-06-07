import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.manual_registry_apply_pack import (
    REQUIRED_CONFIRMATIONS,
    ManualRegistryApplyConfig,
    build_manual_registry_apply_pack,
    build_manual_registry_apply_pack_from_files,
    write_registry_copy_from_apply_pack,
)
from jarvis.private_registry_dry_run_bridge import build_private_registry_dry_run_bridge_from_files


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PRIVATE_INTAKE = "jarvis/data/private/vwce_verified_evidence_combined.local.json"
POLICY = "jarvis/data/evidence_freshness_policy.example.json"
PRIVATE_STATUS_CONFIG = "jarvis/data/private_status_review_bridge.example.json"
PRIVATE_DRY_RUN_CONFIG = "jarvis/data/private_registry_dry_run_bridge.example.json"
APPLY_CONFIG = "jarvis/data/manual_registry_apply_pack.example.json"


def _dry_run():
    return build_private_registry_dry_run_bridge_from_files(
        REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG
    )


def _config(output_path: str | None, confirmations: tuple[str, ...] = REQUIRED_CONFIRMATIONS) -> ManualRegistryApplyConfig:
    return ManualRegistryApplyConfig(
        target_asset_id="vwce_global_core_candidate",
        output_path=output_path,
        confirmations=confirmations,
    )


class ManualRegistryApplyPackTests(unittest.TestCase):
    def test_vwce_candidate_reviewed_pack_can_be_apply_allowed_with_all_confirmations(self) -> None:
        pack = build_manual_registry_apply_pack_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG, APPLY_CONFIG
        )

        self.assertTrue(pack.apply_allowed)
        self.assertEqual(pack.current_status, "candidate_unreviewed")
        self.assertEqual(pack.requested_status, "candidate_reviewed")

    def test_missing_confirmation_blocks_apply(self) -> None:
        pack = build_manual_registry_apply_pack(REGISTRY, _dry_run(), _config("copy.json", confirmations=REQUIRED_CONFIRMATIONS[:-1]))

        self.assertFalse(pack.apply_allowed)
        self.assertTrue(any("missing confirmation" in blocker for blocker in pack.blockers))

    def test_approved_investable_transition_impossible(self) -> None:
        pack = build_manual_registry_apply_pack_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG, APPLY_CONFIG
        )

        self.assertNotEqual(pack.requested_status, "approved_investable")

    def test_output_path_equal_to_source_registry_path_is_blocked(self) -> None:
        pack = build_manual_registry_apply_pack(REGISTRY, _dry_run(), _config(REGISTRY))

        self.assertFalse(pack.apply_allowed)
        self.assertTrue(any("output_path must not equal" in blocker for blocker in pack.blockers))

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.copy.json"

            build_manual_registry_apply_pack(REGISTRY, _dry_run(), _config(str(target)))

            self.assertFalse(target.exists())

    def test_optional_helper_writes_only_to_explicit_temp_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.copy.json"
            dry_run = _dry_run()
            pack = build_manual_registry_apply_pack(REGISTRY, dry_run, _config(str(target)))

            write_registry_copy_from_apply_pack(REGISTRY, dry_run, pack, target)

            self.assertTrue(target.exists())

    def test_written_copy_changes_only_vwce_status_to_candidate_reviewed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.copy.json"
            dry_run = _dry_run()
            pack = build_manual_registry_apply_pack(REGISTRY, dry_run, _config(str(target)))

            write_registry_copy_from_apply_pack(REGISTRY, dry_run, pack, target)

            source = json.loads(Path(REGISTRY).read_text(encoding="utf-8"))
            copy = json.loads(target.read_text(encoding="utf-8"))
            source_assets = {asset["asset_id"]: asset for asset in source["assets"]}
            copy_assets = {asset["asset_id"]: asset for asset in copy["assets"]}
            self.assertEqual(copy_assets["vwce_global_core_candidate"]["approval_status"], "candidate_reviewed")
            source_assets["vwce_global_core_candidate"]["approval_status"] = "candidate_reviewed"
            self.assertEqual(source_assets, copy_assets)

    def test_source_registry_file_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_manual_registry_apply_pack_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG, APPLY_CONFIG
        )

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_created(self) -> None:
        pack = build_manual_registry_apply_pack_from_files(
            REGISTRY, PRIVATE_INTAKE, POLICY, PRIVATE_STATUS_CONFIG, PRIVATE_DRY_RUN_CONFIG, APPLY_CONFIG
        )

        self.assertFalse(pack.buy_sell_requests_created)

    def test_blocked_pack_cannot_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.copy.json"
            dry_run = _dry_run()
            pack = replace(build_manual_registry_apply_pack(REGISTRY, dry_run, _config(str(target))), apply_allowed=False)

            with self.assertRaises(ValueError):
                write_registry_copy_from_apply_pack(REGISTRY, dry_run, pack, target)


if __name__ == "__main__":
    unittest.main()
