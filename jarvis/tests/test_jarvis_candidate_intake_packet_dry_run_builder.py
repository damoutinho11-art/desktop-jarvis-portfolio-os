import unittest
from pathlib import Path

from jarvis.jarvis_candidate_intake_dry_run_command_contract import REQUIRED_EXACT_PHRASE
from jarvis.jarvis_candidate_intake_packet_dry_run_builder import (
    build_candidate_intake_packet_dry_run_builder_pack,
    load_candidate_intake_packet_dry_run_builder_pack,
)


DEFAULT_BUILDER = "jarvis/data/jarvis_candidate_intake_packet_dry_run_builder.example.json"
SYNTHETIC_PARTIAL = "jarvis/data/jarvis_candidate_intake_packet_dry_run_builder.synthetic_partial.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_candidate_intake_packet_dry_run_builder.synthetic_complete.example.json"


UNSAFE_FIELDS = (
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
    "registry_file_written",
    "candidate_registry_write",
    "write_candidate_intake_file",
    "persist_packet_file",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
    "evidence_collection_started",
    "evidence_verification_started",
)


def _candidate(**overrides):
    base = {
        "candidate_id": "candidate_a",
        "display_name": "Candidate A",
        "asset_type": "etf",
        "symbol_or_identifier": "CAND",
        "issuer_or_provider": "Synthetic provider",
        "market_or_region": "global",
        "currency": "EUR",
        "source_context": "synthetic preview",
        "user_rationale": "Synthetic test.",
        "intake_status": "candidate_intake_packet_preview_pending_manual_review",
        "created_by_manual_entry": True,
        "manual_entry_required": True,
        "evidence_pipeline_required": True,
        "phase1_route": "v4.27-v4.47-real-evidence-pipeline",
        "notes": "Dry-run only.",
        "safety_flags": {
            "approved_asset": False,
            "trusted_asset": False,
            "investable": False,
            "allocation_recommendation": False,
            "buy_signal": False,
            "sell_signal": False,
            "trade_executed": False,
            "registry_mutation": False,
            "executor_created": False,
        },
    }
    base.update(overrides)
    return base


def _data(**overrides):
    base = {
        "version": "v4.54",
        "title": "Test Builder",
        "source_command_contract_version": "v4.53",
        "source_command_contract_status": "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE",
        "source_command_id": "command_a",
        "source_explicit_command": REQUIRED_EXACT_PHRASE,
        "command_candidate_ids_in_scope": ["candidate_a"],
        "builder_mode": "candidate_intake_packet_preview_dry_run_only",
        "dry_run_only": True,
        "write_candidate_intake_file": False,
        "persist_packet_file": False,
        "registry_mutation": False,
        "registry_file_written": False,
        "candidate_registry_write": False,
        "evidence_collection_started": False,
        "evidence_verification_started": False,
        "source_candidate_previews": [_candidate()],
    }
    base.update(overrides)
    return base


class CandidateIntakePacketDryRunBuilderTests(unittest.TestCase):
    def test_top_level_controls_are_enforced(self) -> None:
        for field, value in (
            ("dry_run_only", False),
            ("write_candidate_intake_file", True),
            ("persist_packet_file", True),
            ("registry_mutation", True),
            ("registry_file_written", True),
            ("candidate_registry_write", True),
            ("evidence_collection_started", True),
            ("evidence_verification_started", True),
        ):
            with self.subTest(field=field):
                pack = build_candidate_intake_packet_dry_run_builder_pack(_data(**{field: value}))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE")

    def test_unsafe_top_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_candidate_intake_packet_dry_run_builder_pack(_data(**{field: True}))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE")

    def test_unsafe_candidate_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_candidate_intake_packet_dry_run_builder_pack(_data(source_candidate_previews=[_candidate(**{field: True})]))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE")

    def test_default_partial_and_complete_statuses(self) -> None:
        default = load_candidate_intake_packet_dry_run_builder_pack(DEFAULT_BUILDER)
        partial = load_candidate_intake_packet_dry_run_builder_pack(SYNTHETIC_PARTIAL)
        complete = load_candidate_intake_packet_dry_run_builder_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(default.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_BLOCKED_SAFE")
        self.assertEqual(partial.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_PARTIAL_SAFE")
        self.assertEqual(complete.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE")

    def test_complete_blocks_if_source_status_phrase_or_scope_invalid(self) -> None:
        wrong_status = build_candidate_intake_packet_dry_run_builder_pack(_data(source_command_contract_status="BLOCKED"))
        missing_phrase = build_candidate_intake_packet_dry_run_builder_pack(_data(source_explicit_command="NOPE"))
        empty_scope = build_candidate_intake_packet_dry_run_builder_pack(_data(command_candidate_ids_in_scope=[]))
        outside = build_candidate_intake_packet_dry_run_builder_pack(_data(source_candidate_previews=[_candidate(candidate_id="candidate_z")]))

        self.assertEqual(wrong_status.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_BLOCKED_SAFE")
        self.assertEqual(missing_phrase.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_BLOCKED_SAFE")
        self.assertEqual(empty_scope.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_BLOCKED_SAFE")
        self.assertNotEqual(outside.overall_status, "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE")

    def test_packet_preview_is_v4_49_compatible_and_safe(self) -> None:
        pack = load_candidate_intake_packet_dry_run_builder_pack(SYNTHETIC_COMPLETE)
        packet = pack.candidate_intake_packet_preview

        self.assertIsNotNone(packet)
        self.assertTrue(packet["dry_run_only"])
        self.assertFalse(packet["write_candidate_intake_file"])
        self.assertFalse(packet["persist_packet_file"])
        self.assertFalse(packet["registry_mutation"])
        self.assertFalse(packet["registry_file_written"])
        self.assertEqual(packet["candidate_count"], 2)
        for candidate in packet["candidates"]:
            for field in (
                "candidate_id",
                "display_name",
                "asset_type",
                "symbol_or_identifier",
                "issuer_or_provider",
                "market_or_region",
                "currency",
                "source_context",
                "user_rationale",
                "intake_status",
                "created_by_manual_entry",
                "manual_entry_required",
                "evidence_pipeline_required",
                "phase1_route",
                "notes",
                "required_evidence_categories",
                "safety_flags",
            ):
                self.assertIn(field, candidate)
            self.assertEqual(candidate["phase1_route"], "v4.27-v4.47-real-evidence-pipeline")
            self.assertTrue(all(value is False for value in candidate["safety_flags"].values()))

    def test_complete_writes_no_files_and_outputs_false_safety_fields(self) -> None:
        before = Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8")
        pack = load_candidate_intake_packet_dry_run_builder_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(before, Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8"))
        for field in (
            "write_candidate_intake_file",
            "persist_packet_file",
            "registry_mutation",
            "registry_file_written",
            "candidate_registry_write",
            "evidence_collection_started",
            "evidence_verification_started",
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
            "executor_created",
        ):
            self.assertFalse(getattr(pack, field))


if __name__ == "__main__":
    unittest.main()
