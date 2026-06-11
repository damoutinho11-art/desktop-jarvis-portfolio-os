import unittest
from pathlib import Path

from jarvis.ftaw_manual_source_fact_entry_pack import build_ftaw_manual_source_fact_entry_pack_from_files
from jarvis.tests.test_ftaw_manual_public_source_reference_entry_recorder import (
    COMPLETE_RECORDER_CONFIG,
    PARTIAL_RECORDER_CONFIG,
    RECORDER_CONFIG,
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
from jarvis.tests.test_ftaw_real_public_source_reference_intake_plan import (
    COMPLETE_PLAN_CONFIG,
    PLAN_CONFIG,
)


FACT_CONFIG = "jarvis/data/ftaw_manual_source_fact_entry_pack.example.json"
PARTIAL_FACT_CONFIG = "jarvis/data/ftaw_manual_source_fact_entry_pack.synthetic_partial.example.json"
COMPLETE_FACT_CONFIG = "jarvis/data/ftaw_manual_source_fact_entry_pack.synthetic_complete.example.json"


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
    plan_config=PLAN_CONFIG,
    recorder_config=RECORDER_CONFIG,
    fact_config=FACT_CONFIG,
):
    return build_ftaw_manual_source_fact_entry_pack_from_files(
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
        recorder_config,
        fact_config,
    )


def _partial_pack():
    return _pack(
        PARTIAL_QUEUE_CONFIG,
        PARTIAL_DECISION_CONFIG,
        PARTIAL_PREVIEW_CONFIG,
        PARTIAL_DRY_RUN_CONFIG,
        PARTIAL_READINESS_CONFIG,
        recorder_config=PARTIAL_RECORDER_CONFIG,
        fact_config=PARTIAL_FACT_CONFIG,
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
        COMPLETE_PLAN_CONFIG,
        COMPLETE_RECORDER_CONFIG,
        COMPLETE_FACT_CONFIG,
    )


class FTAWManualSourceFactEntryPackTests(unittest.TestCase):
    def test_default_fixture_does_not_accept_source_facts_without_ready_public_references(self) -> None:
        pack = _pack()

        self.assertEqual(pack.source_fact_entry_status, "BLOCKED_NO_PUBLIC_SOURCE_REFERENCES")
        self.assertEqual(pack.accepted_source_fact_record_count, 0)

    def test_partial_synthetic_accepts_valid_provided_facts_and_lists_missing(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.source_fact_entry_status, "PARTIAL_SOURCE_FACTS_ENTERED")
        self.assertEqual(pack.accepted_source_fact_record_count, 2)
        self.assertGreater(pack.missing_required_field_count, 0)
        self.assertTrue(pack.blocked_reasons)

    def test_synthetic_complete_reaches_manual_source_facts_entered_for_identity_review(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.source_fact_entry_status, "MANUAL_SOURCE_FACTS_ENTERED_FOR_IDENTITY_REVIEW")

    def test_synthetic_complete_accepts_exactly_five_public_reference_evidence_types(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.accepted_source_fact_record_count, 5)
        self.assertEqual(
            {record.evidence_type for record in pack.accepted_source_fact_records},
            {"fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data"},
        )
        self.assertNotIn("platform_availability", {record.evidence_type for record in pack.accepted_source_fact_records})
        self.assertNotIn("tax_route", {record.evidence_type for record in pack.accepted_source_fact_records})

    def test_manual_private_items_remain_outstanding(self) -> None:
        pack = _complete_pack()
        outstanding = {item.evidence_type: item.reason for item in pack.manual_private_outstanding}

        self.assertIn("platform_availability", outstanding)
        self.assertIn("private/account-specific", outstanding["platform_availability"])
        self.assertIn("tax_route", outstanding)
        self.assertIn("manual user confirmation", outstanding["tax_route"])

    def test_every_accepted_fact_record_has_safe_manual_flags(self) -> None:
        pack = _complete_pack()

        self.assertTrue(all(record.manual_entry for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.auto_extracted for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.fetched for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.downloaded for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.parsed for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.verified for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.identity_guard_pass_created for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.queue_eligibility_created for record in pack.accepted_source_fact_records))
        self.assertTrue(all(not record.buy_signal for record in pack.accepted_source_fact_records))

    def test_missing_required_fields_create_blocked_reasons(self) -> None:
        pack = _partial_pack()

        self.assertTrue(any("missing required field" in reason for reason in pack.blocked_reasons))

    def test_invalid_source_reference_and_private_manual_entries_are_rejected(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.rejected_entry_count, 3)
        self.assertTrue(any("unknown_reference_slot" == entry.source_reference_id for entry in pack.rejected_entries))
        self.assertTrue(any(entry.evidence_type == "platform_availability" for entry in pack.rejected_entries))
        self.assertTrue(any(entry.evidence_type == "tax_route" for entry in pack.rejected_entries))

    def test_no_auto_extraction_verification_identity_or_queue_records_are_created(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.automatic_fact_extraction)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.identity_guard_pass_records_created)
        self.assertFalse(pack.queue_eligibility_created)

    def test_pack_does_not_approve_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_pack_does_not_create_recommendations_orders_trades_executor_ingest_or_fetches(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)


if __name__ == "__main__":
    unittest.main()
