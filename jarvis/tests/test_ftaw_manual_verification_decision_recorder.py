import unittest
from pathlib import Path

from jarvis.ftaw_identity_guarded_verification_queue import build_ftaw_identity_guarded_verification_queue_from_files
from jarvis.ftaw_manual_verification_decision_recorder import (
    FTAWManualVerificationDecision,
    FTAWManualVerificationDecisionConfig,
    build_ftaw_manual_verification_decision_pack,
    build_ftaw_manual_verification_decision_pack_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
ITEM_ID = "ftaw_global_core_candidate:fund_metadata"


def _synthetic_queue():
    return build_ftaw_identity_guarded_verification_queue_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        SYNTHETIC_QUEUE_CONFIG,
    )


def _pack(decisions):
    return build_ftaw_manual_verification_decision_pack(
        _synthetic_queue(),
        FTAWManualVerificationDecisionConfig(decisions=tuple(decisions)),
        SYNTHETIC_QUEUE_CONFIG,
        "inline_decisions",
    )


def _decision(item_id=ITEM_ID, decision="accept_for_verified_evidence_preview"):
    return FTAWManualVerificationDecision(
        queue_item_id=item_id,
        manual_decision=decision,
        reviewer_notes="Synthetic manual decision.",
    )


class FTAWManualVerificationDecisionRecorderTests(unittest.TestCase):
    def test_default_blocked_queue_cannot_be_accepted(self) -> None:
        pack = build_ftaw_manual_verification_decision_pack_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
            DECISION_CONFIG,
        )

        self.assertEqual(pack.decision_pack_status, "BLOCKED")
        self.assertEqual(pack.blocked_non_eligible_queue_item_count, 1)
        self.assertEqual(pack.accepted_for_verified_evidence_preview_count, 0)

    def test_synthetic_eligible_item_can_receive_accept(self) -> None:
        pack = build_ftaw_manual_verification_decision_pack_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_QUEUE_CONFIG,
            SYNTHETIC_DECISION_CONFIG,
        )

        self.assertEqual(pack.decision_pack_status, "DECISIONS_RECORDED")
        self.assertEqual(pack.accepted_for_verified_evidence_preview_count, 1)
        self.assertEqual(pack.preview_ready_item_ids, (ITEM_ID,))

    def test_accepted_decision_does_not_set_verified_by_user_true(self) -> None:
        pack = _pack([_decision()])

        self.assertTrue(all(result.verified_by_user is False for result in pack.decision_results))

    def test_accepted_decision_does_not_approve_or_mutate_or_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _pack([_decision()])

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)

    def test_reject_decision_is_recorded_without_mutating_source_facts(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _pack([_decision(decision="reject")])

        self.assertEqual(pack.rejected_count, 1)
        self.assertEqual(pack.preview_ready_item_ids, ())
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_needs_correction_is_recorded_and_kept_out_of_preview_ready(self) -> None:
        pack = _pack([_decision(decision="needs_correction")])

        self.assertEqual(pack.needs_correction_count, 1)
        self.assertEqual(pack.preview_ready_item_ids, ())

    def test_invalid_manual_decision_blocks(self) -> None:
        pack = _pack([_decision(decision="approve_now")])

        self.assertEqual(pack.decision_pack_status, "BLOCKED")
        self.assertEqual(pack.blocked_invalid_manual_decision_count, 1)

    def test_unknown_queue_item_blocks(self) -> None:
        pack = _pack([_decision(item_id="ftaw_global_core_candidate:unknown")])

        self.assertEqual(pack.decision_pack_status, "BLOCKED")
        self.assertEqual(pack.blocked_unknown_queue_item_count, 1)

    def test_non_eligible_queue_item_blocks(self) -> None:
        pack = _pack([_decision(item_id="ftaw_global_core_candidate:platform_availability")])

        self.assertEqual(pack.decision_pack_status, "BLOCKED")
        self.assertEqual(pack.blocked_non_eligible_queue_item_count, 1)

    def test_missing_decision_for_eligible_item_remains_pending(self) -> None:
        pack = _pack([])

        self.assertEqual(pack.decision_pack_status, "PENDING_MANUAL_DECISION")
        self.assertEqual(pack.pending_manual_decision_count, 1)
        self.assertEqual(pack.preview_ready_item_ids, ())


if __name__ == "__main__":
    unittest.main()
