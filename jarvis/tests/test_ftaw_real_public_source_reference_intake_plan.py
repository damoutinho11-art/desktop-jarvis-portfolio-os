import unittest
from pathlib import Path

from jarvis.ftaw_real_public_source_reference_intake_plan import (
    build_ftaw_real_public_source_reference_intake_plan_from_files,
)
from jarvis.tests.test_ftaw_real_evidence_collection_checklist_pack import (
    CHECKLIST_CONFIG,
    COMPLETE_CHECKLIST_CONFIG,
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


PLAN_CONFIG = "jarvis/data/ftaw_real_public_source_reference_intake_plan.example.json"
COMPLETE_PLAN_CONFIG = "jarvis/data/ftaw_real_public_source_reference_intake_plan.synthetic_complete.example.json"


def _plan(
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
    plan_config=PLAN_CONFIG,
):
    return build_ftaw_real_public_source_reference_intake_plan_from_files(
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
        plan_config,
    )


def _partial_plan():
    return _plan(
        PARTIAL_QUEUE_CONFIG,
        PARTIAL_DECISION_CONFIG,
        PARTIAL_PREVIEW_CONFIG,
        PARTIAL_DRY_RUN_CONFIG,
        PARTIAL_READINESS_CONFIG,
    )


def _complete_plan():
    return _plan(
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
        COMPLETE_PLAN_CONFIG,
    )


class FTAWRealPublicSourceReferenceIntakePlanTests(unittest.TestCase):
    def test_default_fixture_is_blocked_not_ready_for_public_source_references(self) -> None:
        plan = _plan()

        self.assertEqual(plan.public_source_reference_plan_status, "BLOCKED_NOT_READY_FOR_PUBLIC_SOURCE_REFERENCES")

    def test_partial_synthetic_fixture_is_not_fully_ready_and_lists_blockers(self) -> None:
        plan = _partial_plan()

        self.assertEqual(plan.public_source_reference_plan_status, "PARTIAL_PUBLIC_SOURCE_REFERENCE_PLAN_READY")
        self.assertTrue(plan.blocked_reasons)

    def test_synthetic_complete_fixture_reaches_public_source_reference_plan_ready(self) -> None:
        plan = _complete_plan()

        self.assertEqual(plan.public_source_reference_plan_status, "PUBLIC_SOURCE_REFERENCE_PLAN_READY")

    def test_synthetic_complete_creates_slots_for_all_seven_evidence_types(self) -> None:
        plan = _complete_plan()

        self.assertEqual(plan.source_reference_slot_count, 7)
        self.assertEqual(
            {slot.evidence_type for slot in plan.source_reference_slots},
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

    def test_public_official_slots_do_not_fetch_download_or_verify_automatically(self) -> None:
        plan = _complete_plan()
        public_slots = [slot for slot in plan.source_reference_slots if slot.expected_public_or_private == "public_official"]

        self.assertTrue(public_slots)
        self.assertTrue(all(not slot.auto_fetch_allowed for slot in public_slots))
        self.assertTrue(all(not slot.auto_download_allowed for slot in public_slots))
        self.assertTrue(all(not slot.auto_verify_allowed for slot in public_slots))

    def test_platform_availability_is_private_manual_reference_and_not_commit_safe(self) -> None:
        plan = _complete_plan()
        slot = next(slot for slot in plan.source_reference_slots if slot.evidence_type == "platform_availability")

        self.assertEqual(slot.expected_public_or_private, "private_manual_reference_required")
        self.assertFalse(slot.auto_fetch_allowed)
        self.assertEqual(slot.expected_commit_safety, "do_not_commit_private_evidence")

    def test_tax_route_is_manual_user_confirmation(self) -> None:
        plan = _complete_plan()
        slot = next(slot for slot in plan.source_reference_slots if slot.evidence_type == "tax_route")

        self.assertEqual(slot.expected_public_or_private, "manual_user_confirmation")
        self.assertFalse(slot.manual_url_required)

    def test_every_slot_starts_uncollected_unverified_and_not_verified_by_default(self) -> None:
        plan = _complete_plan()

        self.assertTrue(all(not slot.collected for slot in plan.source_reference_slots))
        self.assertTrue(all(not slot.verified for slot in plan.source_reference_slots))
        self.assertTrue(all(not slot.verified_by_user_default for slot in plan.source_reference_slots))
        self.assertTrue(all(not slot.buy_signal for slot in plan.source_reference_slots))

    def test_no_source_fact_identity_or_queue_records_are_created(self) -> None:
        plan = _complete_plan()

        self.assertFalse(plan.source_fact_intake_records_created)
        self.assertFalse(plan.identity_guard_pass_records_created)
        self.assertFalse(plan.queue_eligibility_created)

    def test_plan_does_not_approve_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        plan = _complete_plan()

        self.assertFalse(plan.approved_asset)
        self.assertFalse(plan.registry_mutation)
        self.assertFalse(plan.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_plan_does_not_create_recommendations_orders_trades_executor_ingest_or_fetches(self) -> None:
        plan = _complete_plan()

        self.assertFalse(plan.allocation_recommendation_created)
        self.assertFalse(plan.buy_sell_requests_created)
        self.assertFalse(plan.trades_executed)
        self.assertFalse(plan.executor_created)
        self.assertFalse(plan.private_file_auto_ingest)
        self.assertFalse(plan.automatic_source_fetching)
        self.assertFalse(plan.automatic_downloads)
        self.assertEqual(plan.auto_fetch_allowed_count, 0)
        self.assertEqual(plan.auto_download_allowed_count, 0)
        self.assertEqual(plan.auto_verify_allowed_count, 0)


if __name__ == "__main__":
    unittest.main()
