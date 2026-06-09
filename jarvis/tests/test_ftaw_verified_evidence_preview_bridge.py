import unittest
from pathlib import Path

from jarvis.ftaw_identity_guarded_verification_queue import build_ftaw_identity_guarded_verification_queue_from_files
from jarvis.ftaw_manual_verification_decision_recorder import (
    FTAWManualVerificationDecision,
    FTAWManualVerificationDecisionConfig,
    build_ftaw_manual_verification_decision_pack,
)
from jarvis.ftaw_verified_evidence_preview_bridge import (
    build_ftaw_verified_evidence_preview_bridge,
    build_ftaw_verified_evidence_preview_bridge_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
BRIDGE_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
SYNTHETIC_BRIDGE_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
ITEM_ID = "ftaw_global_core_candidate:fund_metadata"


def _queue():
    return build_ftaw_identity_guarded_verification_queue_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        SYNTHETIC_QUEUE_CONFIG,
    )


def _decision(item_id=ITEM_ID, decision="accept_for_verified_evidence_preview"):
    return FTAWManualVerificationDecision(item_id, decision, "Synthetic manual decision.")


def _pack(decisions):
    queue = _queue()
    decision_pack = build_ftaw_manual_verification_decision_pack(
        queue,
        FTAWManualVerificationDecisionConfig(decisions=tuple(decisions)),
        SYNTHETIC_QUEUE_CONFIG,
        "inline_decisions",
    )
    return build_ftaw_verified_evidence_preview_bridge(queue, decision_pack)


class FTAWVerifiedEvidencePreviewBridgeTests(unittest.TestCase):
    def test_default_path_produces_zero_preview_ready_records(self) -> None:
        pack = build_ftaw_verified_evidence_preview_bridge_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
            DECISION_CONFIG,
            BRIDGE_CONFIG,
        )

        self.assertEqual(pack.preview_bridge_status, "BLOCKED")
        self.assertEqual(pack.preview_ready_count, 0)
        self.assertEqual(pack.blocked_non_eligible_queue_item_count, 1)

    def test_synthetic_accept_produces_exactly_one_preview_ready_record(self) -> None:
        pack = build_ftaw_verified_evidence_preview_bridge_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_QUEUE_CONFIG,
            SYNTHETIC_DECISION_CONFIG,
            SYNTHETIC_BRIDGE_CONFIG,
        )

        self.assertEqual(pack.preview_bridge_status, "PREVIEW_READY")
        self.assertEqual(pack.preview_ready_count, 1)
        record = pack.preview_records[0]
        self.assertEqual(record.asset_id, "ftaw_global_core_candidate")
        self.assertEqual(record.evidence_type, "fund_metadata")
        self.assertEqual(record.preview_status, "preview_ready")
        self.assertEqual(record.queue_item_reference, ITEM_ID)
        self.assertEqual(record.extracted_facts["ticker"], "FTAW")

    def test_preview_ready_record_keeps_verified_by_user_false(self) -> None:
        record = _pack([_decision()]).preview_records[0]

        self.assertFalse(record.verified_by_user)

    def test_preview_ready_record_has_preview_only_marker(self) -> None:
        record = _pack([_decision()]).preview_records[0]

        self.assertTrue(record.verified_evidence_preview)
        self.assertTrue(record.no_verified_evidence_promotion)

    def test_reject_decision_is_excluded(self) -> None:
        pack = _pack([_decision(decision="reject")])

        self.assertEqual(pack.preview_ready_count, 0)
        self.assertEqual(pack.excluded_rejected_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "excluded_rejected")

    def test_needs_correction_decision_is_excluded(self) -> None:
        pack = _pack([_decision(decision="needs_correction")])

        self.assertEqual(pack.preview_ready_count, 0)
        self.assertEqual(pack.excluded_needs_correction_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "excluded_needs_correction")

    def test_invalid_decision_blocks(self) -> None:
        pack = _pack([_decision(decision="approve_now")])

        self.assertEqual(pack.preview_bridge_status, "BLOCKED")
        self.assertEqual(pack.blocked_invalid_manual_decision_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "blocked_invalid_manual_decision")

    def test_unknown_queue_item_blocks(self) -> None:
        pack = _pack([_decision(item_id="ftaw_global_core_candidate:unknown")])

        self.assertEqual(pack.preview_bridge_status, "BLOCKED")
        self.assertEqual(pack.blocked_unknown_queue_item_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "blocked_unknown_queue_item")

    def test_non_eligible_queue_item_blocks(self) -> None:
        pack = _pack([_decision(item_id="ftaw_global_core_candidate:platform_availability")])

        self.assertEqual(pack.preview_bridge_status, "BLOCKED")
        self.assertEqual(pack.blocked_non_eligible_queue_item_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "blocked_non_eligible_queue_item")

    def test_missing_decision_remains_pending(self) -> None:
        pack = _pack([])

        self.assertEqual(pack.preview_bridge_status, "PENDING_MANUAL_DECISION")
        self.assertEqual(pack.pending_manual_decision_count, 1)
        self.assertEqual(pack.preview_records[0].preview_status, "pending_manual_decision")

    def test_preview_builder_does_not_mutate_registry_or_approve(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _pack([_decision()])

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
