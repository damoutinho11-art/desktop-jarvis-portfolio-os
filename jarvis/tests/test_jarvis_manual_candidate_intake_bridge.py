import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_intake_bridge import (
    build_manual_candidate_intake_bridge_pack,
    load_manual_candidate_intake_bridge_pack,
)
from jarvis.jarvis_manual_candidate_watchlist_entry import INTENDED_ROUTE


DEFAULT_BRIDGE = "jarvis/data/jarvis_manual_candidate_intake_bridge.example.json"
SYNTHETIC_MULTI = "jarvis/data/jarvis_manual_candidate_intake_bridge.synthetic_multi.example.json"


def _entry(**overrides):
    base = {
        "watchlist_entry_id": "bridge_test",
        "candidate_id": "synthetic_candidate",
        "display_name": "Synthetic Candidate",
        "asset_type": "etf",
        "symbol_or_identifier": "SYN",
        "issuer_or_provider": "Synthetic issuer",
        "market_or_region": "EU",
        "currency": "EUR",
        "watchlist_reason": "Manual bridge test.",
        "watchlist_source_context": "synthetic manual entry",
        "manually_entered_by_user": True,
        "manual_entry_timestamp": "2026-06-12T00:00:00Z",
        "intended_route": INTENDED_ROUTE,
        "candidate_intake_required": True,
        "evidence_pipeline_required": True,
        "manual_review_required": True,
        "notes": "No approval.",
    }
    base.update(overrides)
    return base


def _data(entries=None, **overrides):
    base = {
        "version": "v4.51",
        "title": "Test Bridge",
        "source_watchlist_entry_pack": "inline",
        "bridge_mode": "dry_run_candidate_intake_packet_preview",
        "dry_run_only": True,
        "write_candidate_intake_file": False,
        "registry_mutation": False,
        "candidate_registry_write": False,
        "evidence_collection_started": False,
        "evidence_verification_started": False,
        "entries": entries if entries is not None else [_entry()],
    }
    base.update(overrides)
    return base


class ManualCandidateIntakeBridgeTests(unittest.TestCase):
    def test_top_level_controls_are_required(self) -> None:
        for field, value in (
            ("dry_run_only", False),
            ("write_candidate_intake_file", True),
            ("registry_mutation", True),
            ("candidate_registry_write", True),
            ("evidence_collection_started", True),
            ("evidence_verification_started", True),
        ):
            with self.subTest(field=field):
                pack = build_manual_candidate_intake_bridge_pack(_data(**{field: value}))
                self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE")

    def test_entry_unsafe_claims_are_blocked(self) -> None:
        for field in (
            "approved_asset",
            "trusted_asset",
            "investable",
            "verified_evidence",
            "promoted_verified_evidence",
            "allocation_recommendation",
            "portfolio_weight",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "registry_mutation",
            "candidate_registry_write",
            "write_candidate_intake_file",
            "executor_created",
            "broker_api_used",
            "credentials_used",
            "automatic_source_fetching",
            "automatic_download",
            "private_file_ingested",
            "evidence_collection_started",
            "evidence_verification_started",
        ):
            with self.subTest(field=field):
                pack = build_manual_candidate_intake_bridge_pack(_data(entries=[_entry(**{field: True})]))
                self.assertEqual(pack.entries[0].bridge_entry_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE")

    def test_multiple_asset_types_and_non_hardcoded_candidates(self) -> None:
        pack = load_manual_candidate_intake_bridge_pack(SYNTHETIC_MULTI)
        asset_types = {entry.asset_type for entry in pack.entries}
        ready_ids = {entry.candidate_id for entry in pack.entries if entry.candidate_preview_created}

        self.assertIn("etf", asset_types)
        self.assertIn("stock", asset_types)
        self.assertIn("other", asset_types)
        self.assertIn("synthetic_stock_candidate", ready_ids)

    def test_complete_entries_produce_v4_49_compatible_previews(self) -> None:
        pack = build_manual_candidate_intake_bridge_pack(_data())
        preview = pack.candidate_intake_packet_preview

        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW")
        self.assertIsNotNone(preview)
        self.assertTrue(preview["dry_run_only"])
        self.assertFalse(preview["write_candidate_intake_file"])
        self.assertFalse(preview["registry_mutation"])
        self.assertFalse(preview["candidate_registry_write"])
        self.assertEqual(preview["candidate_count"], 1)
        self.assertEqual(preview["candidates"][0]["phase1_route"], "v4.27-v4.47-real-evidence-pipeline")

    def test_partial_and_unsafe_entries_do_not_produce_previews(self) -> None:
        pack = load_manual_candidate_intake_bridge_pack(SYNTHETIC_MULTI)

        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_PARTIAL_SAFE")
        self.assertEqual(pack.preview_candidate_count, 3)
        self.assertFalse(next(entry for entry in pack.entries if entry.watchlist_entry_id == "bridge_other_manual_review").candidate_preview_created)
        self.assertFalse(next(entry for entry in pack.entries if entry.watchlist_entry_id == "bridge_blocked_unsafe").candidate_preview_created)

    def test_default_blocked_and_all_ready_statuses_are_deterministic(self) -> None:
        default = load_manual_candidate_intake_bridge_pack(DEFAULT_BRIDGE)
        ready = build_manual_candidate_intake_bridge_pack(_data(entries=[_entry(), _entry(watchlist_entry_id="bridge_test_2", candidate_id="candidate_2")]))

        self.assertEqual(default.overall_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE")
        self.assertEqual(ready.overall_status, "MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW")

    def test_preview_safety_flags_are_false_and_no_files_written(self) -> None:
        before = Path(SYNTHETIC_MULTI).read_text(encoding="utf-8")
        pack = load_manual_candidate_intake_bridge_pack(SYNTHETIC_MULTI)

        self.assertEqual(before, Path(SYNTHETIC_MULTI).read_text(encoding="utf-8"))
        self.assertFalse(pack.write_candidate_intake_file)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.candidate_registry_write)
        self.assertFalse(pack.evidence_collection_started)
        self.assertFalse(pack.evidence_verification_started)
        self.assertIsNotNone(pack.candidate_intake_packet_preview)
        for candidate in pack.candidate_intake_packet_preview["candidates"]:
            self.assertTrue(all(value is False for value in candidate["safety_flags"].values()))


if __name__ == "__main__":
    unittest.main()
