import unittest
from pathlib import Path

from jarvis.jarvis_candidate_intake_dry_run_command_contract import (
    REQUIRED_EXACT_PHRASE,
    build_candidate_intake_dry_run_command_contract_pack,
    load_candidate_intake_dry_run_command_contract_pack,
)


DEFAULT_CONTRACT = "jarvis/data/jarvis_candidate_intake_dry_run_command_contract.example.json"
SYNTHETIC_PARTIAL = "jarvis/data/jarvis_candidate_intake_dry_run_command_contract.synthetic_partial.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_candidate_intake_dry_run_command_contract.synthetic_complete.example.json"


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
    "create_candidate_intake_packet",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
    "evidence_collection_started",
    "evidence_verification_started",
)


def _contract(**overrides):
    base = {
        "command_id": "test-command",
        "commander": "manual_commander",
        "command_timestamp": "2026-06-12T00:00:00Z",
        "explicit_command": REQUIRED_EXACT_PHRASE,
        "required_exact_phrase": REQUIRED_EXACT_PHRASE,
        "command_scope": "test dry-run contract",
        "candidate_ids_in_scope": ["candidate_a"],
        "next_allowed_step": "future_candidate_intake_packet_dry_run_only",
        "manual_review_required": True,
        "safety_acknowledgement": "No write, mutation, approval, trade, or execution.",
        "contract_notes": "Synthetic test.",
    }
    base.update(overrides)
    return base


def _data(**overrides):
    base = {
        "version": "v4.53",
        "title": "Test Contract",
        "source_review_decision_version": "v4.52",
        "source_review_decision_status": "MANUAL_CANDIDATE_INTAKE_REVIEW_ACCEPTED_FOR_DRY_RUN_SAFE",
        "source_decision_id": "synthetic-accept-v4-52",
        "source_decision": "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN",
        "reviewed_candidate_ids": ["candidate_a", "candidate_b"],
        "command_contract_mode": "explicit_candidate_intake_packet_dry_run_command_contract_only",
        "dry_run_only": True,
        "write_candidate_intake_file": False,
        "create_candidate_intake_packet": False,
        "registry_mutation": False,
        "registry_file_written": False,
        "candidate_registry_write": False,
        "evidence_collection_started": False,
        "evidence_verification_started": False,
        "command_contract": _contract(),
    }
    base.update(overrides)
    return base


class CandidateIntakeDryRunCommandContractTests(unittest.TestCase):
    def test_top_level_controls_are_enforced(self) -> None:
        for field, value in (
            ("dry_run_only", False),
            ("write_candidate_intake_file", True),
            ("create_candidate_intake_packet", True),
            ("registry_mutation", True),
            ("registry_file_written", True),
            ("candidate_registry_write", True),
            ("evidence_collection_started", True),
            ("evidence_verification_started", True),
        ):
            with self.subTest(field=field):
                pack = build_candidate_intake_dry_run_command_contract_pack(_data(**{field: value}))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_unsafe_top_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_candidate_intake_dry_run_command_contract_pack(_data(**{field: True}))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_unsafe_contract_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_candidate_intake_dry_run_command_contract_pack(_data(command_contract=_contract(**{field: True})))
                self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_default_partial_and_complete_statuses(self) -> None:
        default = load_candidate_intake_dry_run_command_contract_pack(DEFAULT_CONTRACT)
        partial = load_candidate_intake_dry_run_command_contract_pack(SYNTHETIC_PARTIAL)
        complete = load_candidate_intake_dry_run_command_contract_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(default.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_BLOCKED_SAFE")
        self.assertEqual(partial.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_PARTIAL_SAFE")
        self.assertEqual(complete.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_complete_blocks_if_source_status_or_decision_is_wrong(self) -> None:
        wrong_status = build_candidate_intake_dry_run_command_contract_pack(_data(source_review_decision_status="MANUAL_CANDIDATE_INTAKE_REVIEW_DEFERRED_SAFE"))
        wrong_decision = build_candidate_intake_dry_run_command_contract_pack(_data(source_decision="DEFER"))

        self.assertNotEqual(wrong_status.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")
        self.assertNotEqual(wrong_decision.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_complete_blocks_if_phrase_scope_or_next_step_is_invalid(self) -> None:
        missing_phrase = build_candidate_intake_dry_run_command_contract_pack(
            _data(command_contract=_contract(explicit_command="NOPE", required_exact_phrase="NOPE"))
        )
        empty_scope = build_candidate_intake_dry_run_command_contract_pack(_data(command_contract=_contract(candidate_ids_in_scope=[])))
        outside_scope = build_candidate_intake_dry_run_command_contract_pack(_data(command_contract=_contract(candidate_ids_in_scope=["candidate_z"])))
        wrong_next = build_candidate_intake_dry_run_command_contract_pack(_data(command_contract=_contract(next_allowed_step="write_candidate_intake_file")))

        for pack in (missing_phrase, empty_scope, outside_scope, wrong_next):
            self.assertNotEqual(pack.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")

    def test_complete_keeps_all_safety_outputs_false_and_writes_no_files(self) -> None:
        before = Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8")
        pack = load_candidate_intake_dry_run_command_contract_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(before, Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8"))
        self.assertEqual(pack.overall_status, "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE")
        for field in (
            "write_candidate_intake_file",
            "create_candidate_intake_packet",
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
