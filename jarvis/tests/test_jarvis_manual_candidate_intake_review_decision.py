import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_intake_review_decision import (
    build_manual_candidate_intake_review_decision_pack,
    load_manual_candidate_intake_review_decision_pack,
)


DEFAULT_DECISION = "jarvis/data/jarvis_manual_candidate_intake_review_decision.example.json"
SYNTHETIC_DEFER = "jarvis/data/jarvis_manual_candidate_intake_review_decision.synthetic_defer.example.json"
SYNTHETIC_ACCEPT = "jarvis/data/jarvis_manual_candidate_intake_review_decision.synthetic_accept.example.json"


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
)


def _record(**overrides):
    base = {
        "decision_id": "test-decision",
        "reviewer": "manual_reviewer",
        "review_timestamp": "2026-06-12T00:00:00Z",
        "decision": "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN",
        "decision_scope": "test preview packet",
        "reviewed_candidate_ids": ["candidate_a"],
        "rationale": "Synthetic test decision.",
        "required_followups": ["Future dry-run packet command review only."],
        "manual_review_required": True,
        "next_allowed_step": "future_explicit_dry_run_candidate_intake_packet_command_review",
        "safety_acknowledgement": "No approval, writing, mutation, or execution.",
    }
    base.update(overrides)
    return base


def _data(**overrides):
    base = {
        "version": "v4.52",
        "title": "Test Decision",
        "source_bridge_version": "v4.51",
        "source_bridge_status": "MANUAL_CANDIDATE_INTAKE_BRIDGE_PARTIAL_SAFE",
        "source_preview_candidate_count": 1,
        "decision_mode": "manual_candidate_intake_review_decision_record_only",
        "dry_run_only": True,
        "write_candidate_intake_file": False,
        "registry_mutation": False,
        "candidate_registry_write": False,
        "evidence_collection_started": False,
        "evidence_verification_started": False,
        "decision_record": _record(),
    }
    base.update(overrides)
    return base


class ManualCandidateIntakeReviewDecisionTests(unittest.TestCase):
    def test_top_level_controls_are_enforced(self) -> None:
        for field, value in (
            ("dry_run_only", False),
            ("write_candidate_intake_file", True),
            ("registry_mutation", True),
            ("candidate_registry_write", True),
            ("evidence_collection_started", True),
            ("evidence_verification_started", True),
        ):
            with self.subTest(field=field):
                pack = build_manual_candidate_intake_review_decision_pack(_data(**{field: value}))
                self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")

    def test_unsafe_top_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_manual_candidate_intake_review_decision_pack(_data(**{field: True}))
                self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")

    def test_unsafe_decision_level_claims_are_blocked(self) -> None:
        for field in UNSAFE_FIELDS:
            with self.subTest(field=field):
                pack = build_manual_candidate_intake_review_decision_pack(_data(decision_record=_record(**{field: True})))
                self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")

    def test_default_example_blocks_safely(self) -> None:
        pack = load_manual_candidate_intake_review_decision_pack(DEFAULT_DECISION)

        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")
        self.assertFalse(pack.write_candidate_intake_file)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.candidate_registry_write)

    def test_defer_decision_status(self) -> None:
        pack = load_manual_candidate_intake_review_decision_pack(SYNTHETIC_DEFER)

        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_DEFERRED_SAFE")
        self.assertEqual(pack.decision_record.decision, "DEFER")
        self.assertEqual(pack.decision_record.next_allowed_step, "manual_followup_or_more_review_only")

    def test_reject_decision_status(self) -> None:
        pack = build_manual_candidate_intake_review_decision_pack(
            _data(
                source_bridge_status="MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW",
                decision_record=_record(
                    decision="REJECT",
                    next_allowed_step="candidate_intake_rejected_no_action",
                    reviewed_candidate_ids=["candidate_a"],
                ),
            )
        )

        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_REJECTED_SAFE")

    def test_accept_requires_preview_count_and_reviewed_candidates(self) -> None:
        accepted = load_manual_candidate_intake_review_decision_pack(SYNTHETIC_ACCEPT)
        no_preview = build_manual_candidate_intake_review_decision_pack(_data(source_preview_candidate_count=0))
        no_candidates = build_manual_candidate_intake_review_decision_pack(_data(decision_record=_record(reviewed_candidate_ids=[])))

        self.assertEqual(accepted.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_ACCEPTED_FOR_DRY_RUN_SAFE")
        self.assertEqual(no_preview.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")
        self.assertEqual(no_candidates.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE")

    def test_accept_keeps_all_safety_outputs_false_and_writes_no_files(self) -> None:
        before = Path(SYNTHETIC_ACCEPT).read_text(encoding="utf-8")
        pack = load_manual_candidate_intake_review_decision_pack(SYNTHETIC_ACCEPT)

        self.assertEqual(before, Path(SYNTHETIC_ACCEPT).read_text(encoding="utf-8"))
        self.assertEqual(pack.overall_status, "MANUAL_CANDIDATE_INTAKE_REVIEW_ACCEPTED_FOR_DRY_RUN_SAFE")
        for field in (
            "write_candidate_intake_file",
            "registry_mutation",
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
