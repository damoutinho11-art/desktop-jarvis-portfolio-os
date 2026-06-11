import unittest
from pathlib import Path

from jarvis.ftaw_real_evidence_collection_checklist_pack import (
    build_ftaw_real_evidence_collection_checklist_pack_from_files,
)
from jarvis.tests.test_ftaw_real_evidence_intake_readiness_bridge import (
    APPLY_GATE_CONFIG,
    AUDIT_CONFIG,
    COMMAND_CONFIG,
    COMPLETE_APPLY_GATE_CONFIG,
    COMPLETE_AUDIT_CONFIG,
    COMPLETE_COMMAND_CONFIG,
    COMPLETE_DECISION_CONFIG,
    COMPLETE_DRY_RUN_CONFIG,
    COMPLETE_EXECUTION_REVIEW_CONFIG,
    COMPLETE_GATE_CONFIG,
    COMPLETE_HUMAN_DECISION_CONFIG,
    COMPLETE_PREVIEW_CONFIG,
    COMPLETE_QUEUE_CONFIG,
    COMPLETE_READINESS_CONFIG,
    COMPLETE_REAL_INTAKE_CONFIG,
    COMPLETE_REGISTRY_DRY_RUN_CONFIG,
    DECISION_CONFIG,
    DRY_RUN_CONFIG,
    EXECUTION_REVIEW_CONFIG,
    GATE_CONFIG,
    GUARD_CONFIG,
    HUMAN_DECISION_CONFIG,
    INTAKE_CONFIG,
    PARTIAL_DECISION_CONFIG,
    PARTIAL_DRY_RUN_CONFIG,
    PARTIAL_PREVIEW_CONFIG,
    PARTIAL_QUEUE_CONFIG,
    PARTIAL_READINESS_CONFIG,
    PREVIEW_CONFIG,
    QUEUE_CONFIG,
    READINESS_CONFIG,
    REAL_INTAKE_CONFIG,
    REGISTRY_DRY_RUN_CONFIG,
    SOURCE_REGISTRY,
    URL_FETCH_CONFIG,
)


CHECKLIST_CONFIG = "jarvis/data/ftaw_real_evidence_collection_checklist_pack.example.json"
COMPLETE_CHECKLIST_CONFIG = "jarvis/data/ftaw_real_evidence_collection_checklist_pack.synthetic_complete.example.json"


def _pack(
    queue_config=QUEUE_CONFIG,
    decision_config=DECISION_CONFIG,
    preview_config=PREVIEW_CONFIG,
    dry_run_config=DRY_RUN_CONFIG,
    readiness_config=READINESS_CONFIG,
    approval_gate_config=GATE_CONFIG,
    human_decision_config=HUMAN_DECISION_CONFIG,
    registry_dry_run_config=REGISTRY_DRY_RUN_CONFIG,
    apply_gate_config=APPLY_GATE_CONFIG,
    command_config=COMMAND_CONFIG,
    execution_review_config=EXECUTION_REVIEW_CONFIG,
    audit_config=AUDIT_CONFIG,
    real_intake_config=REAL_INTAKE_CONFIG,
    checklist_config=CHECKLIST_CONFIG,
):
    return build_ftaw_real_evidence_collection_checklist_pack_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        queue_config,
        decision_config,
        preview_config,
        dry_run_config,
        readiness_config,
        approval_gate_config,
        human_decision_config,
        registry_dry_run_config,
        apply_gate_config,
        command_config,
        execution_review_config,
        audit_config,
        real_intake_config,
        checklist_config,
    )


def _partial_pack():
    return _pack(
        PARTIAL_QUEUE_CONFIG,
        PARTIAL_DECISION_CONFIG,
        PARTIAL_PREVIEW_CONFIG,
        PARTIAL_DRY_RUN_CONFIG,
        PARTIAL_READINESS_CONFIG,
    )


def _complete_pack():
    return _pack(
        COMPLETE_QUEUE_CONFIG,
        COMPLETE_DECISION_CONFIG,
        COMPLETE_PREVIEW_CONFIG,
        COMPLETE_DRY_RUN_CONFIG,
        COMPLETE_READINESS_CONFIG,
        COMPLETE_GATE_CONFIG,
        COMPLETE_HUMAN_DECISION_CONFIG,
        COMPLETE_REGISTRY_DRY_RUN_CONFIG,
        COMPLETE_APPLY_GATE_CONFIG,
        COMPLETE_COMMAND_CONFIG,
        COMPLETE_EXECUTION_REVIEW_CONFIG,
        COMPLETE_AUDIT_CONFIG,
        COMPLETE_REAL_INTAKE_CONFIG,
        COMPLETE_CHECKLIST_CONFIG,
    )


class FTAWRealEvidenceCollectionChecklistPackTests(unittest.TestCase):
    def test_default_fixture_is_blocked_not_ready_for_collection(self) -> None:
        pack = _pack()

        self.assertEqual(pack.checklist_status, "BLOCKED_NOT_READY_FOR_COLLECTION")

    def test_partial_synthetic_fixture_is_not_fully_ready_and_lists_blockers(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.checklist_status, "PARTIAL_COLLECTION_PLAN_READY")
        self.assertTrue(pack.blocked_reasons)

    def test_synthetic_complete_fixture_reaches_collection_plan_ready(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.checklist_status, "REAL_EVIDENCE_COLLECTION_PLAN_READY")

    def test_synthetic_complete_creates_all_seven_required_items(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.checklist_item_count, 7)
        self.assertEqual(
            {item.evidence_type for item in pack.checklist_items},
            {
                "fund_metadata",
                "fee_metadata",
                "distribution_policy",
                "platform_availability",
                "market_data",
                "exposure_data",
                "tax_route",
            },
        )

    def test_every_item_disallows_auto_ingest_auto_verify_and_default_verification(self) -> None:
        pack = _complete_pack()

        self.assertTrue(all(not item.auto_ingest_allowed for item in pack.checklist_items))
        self.assertTrue(all(not item.auto_verify_allowed for item in pack.checklist_items))
        self.assertTrue(all(not item.verified_by_user_default for item in pack.checklist_items))

    def test_platform_availability_is_private_account_specific_and_not_commit_safe(self) -> None:
        pack = _complete_pack()
        item = next(item for item in pack.checklist_items if item.evidence_type == "platform_availability")

        self.assertEqual(item.public_or_private, "private_account_specific")
        self.assertEqual(item.commit_safety, "do_not_commit_private_evidence")

    def test_tax_route_is_manual_user_confirmation_or_summary_only(self) -> None:
        pack = _complete_pack()
        item = next(item for item in pack.checklist_items if item.evidence_type == "tax_route")

        self.assertEqual(item.public_or_private, "manual_user_confirmation")
        self.assertEqual(item.commit_safety, "manual_summary_only")

    def test_public_official_items_are_commit_safe_public_references(self) -> None:
        pack = _complete_pack()
        public_items = [item for item in pack.checklist_items if item.public_or_private == "public_official"]

        self.assertTrue(public_items)
        self.assertTrue(all(item.commit_safety == "commit_safe_public_reference" for item in public_items))

    def test_checklist_does_not_mark_evidence_collected_verified_or_queue_eligible(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.evidence_collected)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.queue_eligibility_created)

    def test_checklist_does_not_approve_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_checklist_does_not_create_recommendations_orders_trades_executor_or_private_ingest(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)


if __name__ == "__main__":
    unittest.main()
