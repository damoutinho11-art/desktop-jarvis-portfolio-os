import unittest
from pathlib import Path

from jarvis.asset_registry import load_asset_registry
from jarvis.evidence_verification_queue import (
    EvidenceVerificationDecision,
    apply_verification_decision,
    build_evidence_verification_queue,
)


REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
SOURCES = "jarvis/data/source_evidence_sources.example.json"


def _decision(task_id: str, decision: str) -> EvidenceVerificationDecision:
    return EvidenceVerificationDecision(
        task_id=task_id,
        decision=decision,
        decided_at="2026-06-05T12:00:00+00:00",
        decided_by="Diogo",
        notes=f"Manual decision: {decision}.",
    )


class EvidenceVerificationQueueTests(unittest.TestCase):
    def test_draft_evidence_creates_pending_verification_tasks(self) -> None:
        queue = build_evidence_verification_queue(REGISTRY, SOURCES)

        self.assertGreater(len(queue.tasks), 0)
        self.assertEqual(queue.tasks[0].verification_status, "pending_user_verification")

    def test_all_generated_tasks_start_pending_user_verification(self) -> None:
        queue = build_evidence_verification_queue(REGISTRY, SOURCES)

        self.assertTrue(all(task.verification_status == "pending_user_verification" for task in queue.tasks))

    def test_accept_decision_can_produce_verified_evidence_preview_only(self) -> None:
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]
        result = apply_verification_decision(task, _decision(task.task_id, "accept"))

        self.assertEqual(result.status, "ACCEPTED_PREVIEW_CREATED")
        self.assertTrue(result.verified_evidence_preview["verified_by_user"])
        self.assertFalse(result.files_written)
        self.assertFalse(result.registry_mutation_allowed)

    def test_reject_decision_produces_no_verified_evidence(self) -> None:
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]
        result = apply_verification_decision(task, _decision(task.task_id, "reject"))

        self.assertEqual(result.status, "REJECTED")
        self.assertIsNone(result.verified_evidence_preview)

    def test_needs_correction_decision_produces_no_verified_evidence(self) -> None:
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]
        result = apply_verification_decision(task, _decision(task.task_id, "needs_correction"))

        self.assertEqual(result.status, "NEEDS_CORRECTION")
        self.assertIsNone(result.verified_evidence_preview)
        self.assertIsNotNone(result.correction_notes)

    def test_applying_decision_does_not_mutate_registry(self) -> None:
        before = Path(REGISTRY).read_text(encoding="utf-8")
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]

        apply_verification_decision(task, _decision(task.task_id, "accept"))

        self.assertEqual(before, Path(REGISTRY).read_text(encoding="utf-8"))

    def test_applying_decision_does_not_mutate_source_file(self) -> None:
        before = Path(SOURCES).read_text(encoding="utf-8")
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]

        apply_verification_decision(task, _decision(task.task_id, "accept"))

        self.assertEqual(before, Path(SOURCES).read_text(encoding="utf-8"))

    def test_no_approval_status_changes(self) -> None:
        before = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}
        task = build_evidence_verification_queue(REGISTRY, SOURCES).tasks[0]

        apply_verification_decision(task, _decision(task.task_id, "accept"))
        after = {asset.asset_id: asset.approval_status for asset in load_asset_registry(REGISTRY).assets}

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
