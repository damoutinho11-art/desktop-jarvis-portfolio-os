import tempfile
import unittest
from pathlib import Path

from jarvis.asset_status_workflow import AssetStatusChangeRequest
from jarvis.registry_update_dry_run import (
    simulate_registry_update,
    simulate_registry_update_from_files,
    write_registry_copy_from_dry_run,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
BRIDGE_CONFIG = "jarvis/data/real_status_review_bridge.example.json"


def _request(
    asset_id: str = "vwce_global_core_candidate",
    current_status: str = "candidate_unreviewed",
    requested_status: str = "candidate_reviewed",
    asset_type: str = "ETF",
    confirmations: tuple[str, ...] = (
        "verified_evidence_reviewed",
        "provenance_gate_passed",
        "no_registry_mutation_without_manual_action",
        "manual_status_change_required",
    ),
) -> AssetStatusChangeRequest:
    return AssetStatusChangeRequest(
        request_id=f"dry_run_test_{asset_id}_{requested_status}",
        created_at="2026-06-05T12:00:00+00:00",
        asset_id=asset_id,
        asset_type=asset_type,
        current_status=current_status,
        requested_status=requested_status,
        rationale="Unit-test manual status review preview.",
        evidence_summary="Verified evidence reviewed in unit-test fixture.",
        required_confirmations=confirmations,
        manual_approval_required=True,
        auto_execute=False,
    )


class RegistryUpdateDryRunTests(unittest.TestCase):
    def test_valid_candidate_unreviewed_to_candidate_reviewed_request_simulates_update(self) -> None:
        result = simulate_registry_update(REGISTRY, [_request()])

        self.assertEqual(len(result.simulated_changes), 1)
        self.assertTrue(result.simulated_changes[0].would_update)
        self.assertEqual(result.simulated_changes[0].requested_status, "candidate_reviewed")

    def test_invalid_direct_candidate_unreviewed_to_approved_investable_blocked(self) -> None:
        result = simulate_registry_update(REGISTRY, [_request(requested_status="approved_investable")])

        self.assertEqual(result.simulated_changes, ())
        self.assertTrue(result.blocked_changes)

    def test_test_position_to_approved_investable_blocked(self) -> None:
        result = simulate_registry_update(
            REGISTRY,
            [
                _request(
                    asset_id="btc_crypto_core_candidate",
                    asset_type="crypto",
                    current_status="test_position",
                    requested_status="approved_investable",
                )
            ],
        )

        self.assertEqual(result.simulated_changes, ())
        self.assertTrue(result.blocked_changes)

    def test_rejected_to_approved_investable_blocked(self) -> None:
        result = simulate_registry_update(REGISTRY, [_request(current_status="rejected", requested_status="approved_investable")])

        self.assertEqual(result.simulated_changes, ())
        self.assertTrue(result.blocked_changes)

    def test_blocked_audit_request_produces_no_simulated_update(self) -> None:
        bad_request = _request(requested_status="approved_watchlist", confirmations=())
        result = simulate_registry_update(REGISTRY, [bad_request])

        self.assertEqual(result.simulated_changes, ())
        self.assertTrue(result.blocked_changes)

    def test_after_record_changes_only_approval_status(self) -> None:
        result = simulate_registry_update(REGISTRY, [_request()])
        change = result.simulated_changes[0]

        before = dict(change.before_record)
        after = dict(change.after_record)
        before.pop("approval_status")
        after.pop("approval_status")

        self.assertEqual(before, after)

    def test_original_registry_file_is_not_mutated(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")

        simulate_registry_update(REGISTRY, [_request()])

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_default_flow_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.updated.json"

            simulate_registry_update(REGISTRY, [_request()])

            self.assertFalse(target.exists())

    def test_optional_helper_writes_only_to_explicit_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "candidate_assets.updated.json"
            result = simulate_registry_update(REGISTRY, [_request()])

            write_registry_copy_from_dry_run(REGISTRY, result, target)

            self.assertTrue(target.exists())
            self.assertIn('"approval_status": "candidate_reviewed"', target.read_text(encoding="utf-8"))

    def test_no_buy_sell_requests_created(self) -> None:
        result = simulate_registry_update(REGISTRY, [_request()])

        self.assertFalse(result.buy_sell_requests_created)

    def test_config_default_loads_without_writing(self) -> None:
        result = simulate_registry_update_from_files(REGISTRY, BRIDGE_CONFIG)

        self.assertFalse(result.registry_mutation_performed)


if __name__ == "__main__":
    unittest.main()
