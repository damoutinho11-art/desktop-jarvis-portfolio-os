import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.routed_evidence_verification_pack import (
    RoutedEvidenceVerificationConfig,
    VerificationDecisionOverride,
    build_routed_evidence_verification_pack,
    build_routed_evidence_verification_pack_from_files,
    write_accepted_previews,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
PUBLIC_SOURCES = "jarvis/data/public_source_fetch.example.json"
CONFIG = "jarvis/data/routed_evidence_verification_pack.example.json"
REQUIRED = (
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "platform_availability",
    "market_data",
    "exposure_data",
    "tax_route",
)


def _config(
    required: tuple[str, ...] = REQUIRED,
    overrides: tuple[VerificationDecisionOverride, ...] = (),
) -> RoutedEvidenceVerificationConfig:
    return RoutedEvidenceVerificationConfig(
        target_asset_id="vwce_global_core_candidate",
        required_evidence_types=required,
        decision_overrides=overrides,
    )


def _override(evidence_type: str, decision: str) -> VerificationDecisionOverride:
    return VerificationDecisionOverride(
        evidence_type=evidence_type,
        decision=decision,
        decided_at="2026-06-06T12:00:00+00:00",
        decided_by="Diogo",
        notes=f"Manual {decision} preview for {evidence_type}.",
    )


class RoutedEvidenceVerificationPackTests(unittest.TestCase):
    def test_vwce_produces_one_task_per_required_evidence_type(self) -> None:
        pack = build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertEqual(len(pack.pending_tasks), len(REQUIRED))
        self.assertEqual(set(task.evidence_type for task in pack.pending_tasks), set(REQUIRED))

    def test_tasks_are_deduplicated_by_evidence_type(self) -> None:
        pack = build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)
        evidence_types = [task.evidence_type for task in pack.pending_tasks]

        self.assertEqual(len(evidence_types), len(set(evidence_types)))

    def test_all_tasks_start_pending_user_verification(self) -> None:
        pack = build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertTrue(all(task.verification_status == "pending_user_verification" for task in pack.pending_tasks))

    def test_missing_evidence_type_reported_when_no_routed_record_exists(self) -> None:
        pack = build_routed_evidence_verification_pack(REGISTRY, PUBLIC_SOURCES, _config(required=("nonexistent_evidence",)))

        self.assertEqual(pack.missing_evidence_types, ("nonexistent_evidence",))
        self.assertEqual(pack.pending_tasks, ())

    def test_accept_decision_produces_verified_preview_only(self) -> None:
        pack = build_routed_evidence_verification_pack(
            REGISTRY,
            PUBLIC_SOURCES,
            _config(overrides=(_override("fund_metadata", "accept"),)),
        )

        self.assertEqual(len(pack.accepted_previews), 1)
        self.assertTrue(pack.accepted_previews[0]["verified_by_user"])
        self.assertFalse(pack.registry_mutation_allowed)

    def test_reject_decision_produces_no_verified_preview(self) -> None:
        pack = build_routed_evidence_verification_pack(
            REGISTRY,
            PUBLIC_SOURCES,
            _config(overrides=(_override("fund_metadata", "reject"),)),
        )

        self.assertEqual(pack.accepted_previews, ())

    def test_needs_correction_decision_produces_no_verified_preview(self) -> None:
        pack = build_routed_evidence_verification_pack(
            REGISTRY,
            PUBLIC_SOURCES,
            _config(overrides=(_override("fund_metadata", "needs_correction"),)),
        )

        self.assertEqual(pack.accepted_previews, ())

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted_preview.json"

            build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

            self.assertFalse(target.exists())

    def test_optional_helper_writes_accepted_preview_to_explicit_path_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted_preview.json"
            pack = build_routed_evidence_verification_pack(
                REGISTRY,
                PUBLIC_SOURCES,
                _config(overrides=(_override("fund_metadata", "accept"),)),
            )

            write_accepted_previews(pack, target)

            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertTrue(payload["records"][0]["verified_by_user"])

    def test_approval_status_never_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        self.assertEqual(before, after)

    def test_registry_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_are_created(self) -> None:
        pack = build_routed_evidence_verification_pack_from_files(REGISTRY, PUBLIC_SOURCES, CONFIG)

        self.assertFalse(pack.buy_sell_requests_created)


if __name__ == "__main__":
    unittest.main()
