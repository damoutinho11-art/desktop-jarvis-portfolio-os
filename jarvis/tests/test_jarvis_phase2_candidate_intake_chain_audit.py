import unittest
from pathlib import Path

from jarvis.jarvis_phase2_candidate_intake_chain_audit import (
    EXPECTED_STAGE_IDS,
    build_phase2_candidate_intake_chain_audit_pack,
    load_phase2_candidate_intake_chain_audit_pack,
)


DEFAULT_AUDIT = "jarvis/data/jarvis_phase2_candidate_intake_chain_audit.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_phase2_candidate_intake_chain_audit.synthetic_complete.example.json"


UNSAFE_FIELDS = (
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_packet_file",
    "executor_created",
    "approved_asset",
    "trusted_asset",
    "investable",
    "evidence_collection_started",
    "evidence_verification_started",
    "promoted_verified_evidence",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "broker_api_used",
    "credentials_used",
    "private_file_ingested",
    "automatic_source_fetching",
    "automatic_download",
)


STAGE_UNSAFE_FIELDS = (
    "writes_files",
    "mutates_registry",
    "creates_executor",
    "approves_asset",
    "trusts_asset",
    "marks_investable",
    "starts_evidence_collection",
    "verifies_evidence",
    "promotes_verified_evidence",
    "recommends_allocation",
    "creates_buy_or_sell_signal",
    "executes_trade",
)


def _complete_data():
    return {
        "version": "v4.55",
        "title": "Inline Complete Audit",
        "audit_mode": "phase2_candidate_intake_chain_integration_audit",
        "report_only": True,
        "phase2_candidate_intake_chain_complete": True,
        "stop_gate_building": True,
        "next_action": "manual_candidate_watchlist_data_entry_only",
        "expected_statuses": [f"{stage}: safe status" for stage in EXPECTED_STAGE_IDS],
        "safety_controls": {field: False for field in UNSAFE_FIELDS},
        "prohibited_actions": ["registry_mutation", "trade_execution"],
        "route_summary": [
            "v4.50 manual watchlist entry",
            "v4.51 manual candidate intake bridge",
            "v4.52 manual candidate intake review decision",
            "v4.53 explicit dry-run packet command contract",
            "v4.54 candidate intake packet dry-run builder",
            "v4.49 candidate intake",
            "v4.27-v4.47 Phase 1 real evidence pipeline",
        ],
        "notes": [
            "VWCE and FTAW were pilot anchors only, not exclusive candidates.",
            "More candidate-intake gates are not currently justified.",
        ],
        "stages": [
            {
                "stage_id": stage_id,
                "stage_name": f"{stage_id} stage",
                "purpose": "Synthetic audit stage.",
                "report_command": f"python -m jarvis.report_{stage_id.replace('.', '_')}",
                "expected_safe_status": "SAFE",
                **{field: False for field in STAGE_UNSAFE_FIELDS},
            }
            for stage_id in EXPECTED_STAGE_IDS
        ],
    }


class Phase2CandidateIntakeChainAuditTests(unittest.TestCase):
    def test_default_blocks_safely_and_complete_passes(self) -> None:
        default = load_phase2_candidate_intake_chain_audit_pack(DEFAULT_AUDIT)
        complete = load_phase2_candidate_intake_chain_audit_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(default.overall_status, "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_BLOCKED_SAFE")
        self.assertEqual(complete.overall_status, "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE")
        self.assertTrue(complete.chain_coherent)

    def test_stage_list_exact_order_required(self) -> None:
        complete = load_phase2_candidate_intake_chain_audit_pack(SYNTHETIC_COMPLETE)
        reversed_data = _complete_data()
        reversed_data["stages"] = list(reversed(reversed_data["stages"]))
        missing_data = _complete_data()
        missing_data["stages"] = missing_data["stages"][:-1]

        self.assertEqual(tuple(stage.stage_id for stage in complete.stages), EXPECTED_STAGE_IDS)
        self.assertNotEqual(
            build_phase2_candidate_intake_chain_audit_pack(reversed_data).overall_status,
            "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE",
        )
        self.assertNotEqual(
            build_phase2_candidate_intake_chain_audit_pack(missing_data).overall_status,
            "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE",
        )

    def test_unsafe_top_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data[field] = True
                data["safety_controls"][field] = True
                pack = build_phase2_candidate_intake_chain_audit_pack(data)
                self.assertNotEqual(pack.overall_status, "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE")

    def test_unsafe_stage_level_claims_are_blocked(self) -> None:
        for field in STAGE_UNSAFE_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["stages"][0][field] = True
                pack = build_phase2_candidate_intake_chain_audit_pack(data)
                self.assertNotEqual(pack.overall_status, "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE")

    def test_next_action_must_be_manual_candidate_entry_only(self) -> None:
        for next_action in ("another_review_gate", "registry_mutation", "evidence_collection", "approval", "trade_execution"):
            with self.subTest(next_action=next_action):
                data = _complete_data()
                data["next_action"] = next_action
                pack = build_phase2_candidate_intake_chain_audit_pack(data)
                self.assertNotEqual(pack.overall_status, "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE")

    def test_complete_writes_no_files_and_outputs_false_safety_fields(self) -> None:
        before = Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8")
        pack = load_phase2_candidate_intake_chain_audit_pack(SYNTHETIC_COMPLETE)

        self.assertEqual(before, Path(SYNTHETIC_COMPLETE).read_text(encoding="utf-8"))
        for field in UNSAFE_FIELDS:
            self.assertFalse(getattr(pack, field))
        self.assertEqual(pack.next_action, "manual_candidate_watchlist_data_entry_only")
        self.assertIn("no more candidate-intake gates recommended now", pack.redundancy_verdict)


if __name__ == "__main__":
    unittest.main()
