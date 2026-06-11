import unittest
from dataclasses import replace
from pathlib import Path

from jarvis.ftaw_real_manual_source_fact_identity_guard_bridge import (
    build_ftaw_real_manual_source_fact_identity_guard_bridge,
    build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files,
)
from jarvis.tests.test_ftaw_manual_public_source_reference_entry_recorder import (
    COMPLETE_RECORDER_CONFIG,
    PARTIAL_RECORDER_CONFIG,
    RECORDER_CONFIG,
)
from jarvis.tests.test_ftaw_manual_source_fact_entry_pack import (
    COMPLETE_FACT_CONFIG,
    FACT_CONFIG,
    PARTIAL_FACT_CONFIG,
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


BRIDGE_CONFIG = "jarvis/data/ftaw_real_manual_source_fact_identity_guard_bridge.example.json"
PARTIAL_BRIDGE_CONFIG = "jarvis/data/ftaw_real_manual_source_fact_identity_guard_bridge.synthetic_partial.example.json"
COMPLETE_BRIDGE_CONFIG = "jarvis/data/ftaw_real_manual_source_fact_identity_guard_bridge.synthetic_complete.example.json"


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
    bridge_config=BRIDGE_CONFIG,
):
    return build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files(
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
        bridge_config,
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
        bridge_config=PARTIAL_BRIDGE_CONFIG,
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
        COMPLETE_BRIDGE_CONFIG,
    )


class FTAWRealManualSourceFactIdentityGuardBridgeTests(unittest.TestCase):
    def test_default_fixture_is_blocked_no_manual_source_facts(self) -> None:
        pack = _pack()

        self.assertEqual(pack.bridge_status, "BLOCKED_NO_MANUAL_SOURCE_FACTS")

    def test_partial_synthetic_is_not_fully_ready_and_lists_blockers(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.bridge_status, "PARTIAL_IDENTITY_GUARD_BRIDGE_READY")
        self.assertTrue(pack.blocked_reasons)

    def test_synthetic_complete_reaches_ready_for_manual_identity_guard_review(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.bridge_status, "READY_FOR_MANUAL_IDENTITY_GUARD_REVIEW")
        self.assertTrue(pack.identity_review_packet_preview.review_packet_created)

    def test_synthetic_complete_includes_all_five_public_fact_types(self) -> None:
        pack = _complete_pack()

        self.assertEqual(
            set(pack.present_public_fact_types),
            {"fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data"},
        )

    def test_identity_field_coverage_includes_required_identity_fields(self) -> None:
        pack = _complete_pack()
        coverage = {item.field_name: item.present for item in pack.identity_field_coverage}

        self.assertTrue(coverage["provider"])
        self.assertTrue(coverage["fund_name"])
        self.assertTrue(coverage["isin"])
        self.assertTrue(coverage["ticker_or_symbol_or_market_ticker"])

    def test_missing_identity_fields_block_readiness(self) -> None:
        complete = _complete_pack()
        fact_pack = _load_complete_fact_pack_for_direct_tests()
        fund_record = next(record for record in fact_pack.accepted_source_fact_records if record.evidence_type == "fund_metadata")
        edited_facts = dict(fund_record.facts)
        edited_facts["provider"] = ""
        edited_records = tuple(
            replace(record, facts=edited_facts) if record.evidence_type == "fund_metadata" else record
            for record in fact_pack.accepted_source_fact_records
        )
        edited_pack = replace(fact_pack, accepted_source_fact_records=edited_records)

        pack = build_ftaw_real_manual_source_fact_identity_guard_bridge(edited_pack)

        self.assertEqual(pack.bridge_status, "PARTIAL_IDENTITY_GUARD_BRIDGE_READY")
        self.assertTrue(any("missing identity field provider" in reason for reason in pack.blocked_reasons))
        self.assertEqual(complete.bridge_status, "READY_FOR_MANUAL_IDENTITY_GUARD_REVIEW")

    def test_inconsistent_identity_fields_block_readiness(self) -> None:
        fact_pack = _load_complete_fact_pack_for_direct_tests()
        market_record = next(record for record in fact_pack.accepted_source_fact_records if record.evidence_type == "market_data")
        edited_facts = dict(market_record.facts)
        edited_facts["market_ticker"] = "DIFFERENT"
        edited_records = tuple(
            replace(record, facts=edited_facts) if record.evidence_type == "market_data" else record
            for record in fact_pack.accepted_source_fact_records
        )
        edited_pack = replace(fact_pack, accepted_source_fact_records=edited_records)

        pack = build_ftaw_real_manual_source_fact_identity_guard_bridge(edited_pack)

        self.assertEqual(pack.bridge_status, "PARTIAL_IDENTITY_GUARD_BRIDGE_READY")
        self.assertEqual(pack.identity_consistency_status, "inconsistent")

    def test_manual_private_items_remain_outstanding(self) -> None:
        pack = _complete_pack()
        outstanding = {item.evidence_type: item.reason for item in pack.manual_private_outstanding}

        self.assertIn("platform_availability", outstanding)
        self.assertIn("tax_route", outstanding)

    def test_no_evidence_identity_pass_or_queue_eligibility_is_created(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.identity_guard_pass_records_created)
        self.assertFalse(pack.queue_eligibility_created)
        self.assertFalse(pack.identity_review_packet_preview.identity_guard_pass_created)
        self.assertFalse(pack.identity_review_packet_preview.queue_eligibility_created)

    def test_bridge_does_not_approve_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_bridge_does_not_create_recommendations_orders_trades_executor_ingest_fetch_download_or_extract(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)
        self.assertFalse(pack.private_file_auto_ingest)
        self.assertFalse(pack.automatic_source_fetching)
        self.assertFalse(pack.automatic_downloads)
        self.assertFalse(pack.automatic_fact_extraction)


def _load_complete_fact_pack_for_direct_tests():
    from jarvis.tests.test_ftaw_manual_source_fact_entry_pack import _complete_pack as load_fact_pack

    return load_fact_pack()


if __name__ == "__main__":
    unittest.main()
