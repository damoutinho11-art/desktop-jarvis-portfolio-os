import unittest
from pathlib import Path

from jarvis.ftaw_real_evidence_intake_readiness_bridge import (
    build_ftaw_real_evidence_intake_readiness_bridge_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
PARTIAL_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
COMPLETE_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_complete.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
PARTIAL_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
COMPLETE_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_complete.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
PARTIAL_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
COMPLETE_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
PARTIAL_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
COMPLETE_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json"
READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.example.json"
PARTIAL_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_pass.example.json"
COMPLETE_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_complete.example.json"
GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.example.json"
COMPLETE_GATE_CONFIG = "jarvis/data/ftaw_manual_approval_review_gate.synthetic_complete.example.json"
HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.example.json"
COMPLETE_HUMAN_DECISION_CONFIG = "jarvis/data/ftaw_human_approval_review_decision_recorder.synthetic_complete.example.json"
REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.example.json"
COMPLETE_REGISTRY_DRY_RUN_CONFIG = "jarvis/data/ftaw_registry_update_dry_run_pack.synthetic_complete.example.json"
APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.example.json"
COMPLETE_APPLY_GATE_CONFIG = "jarvis/data/ftaw_registry_update_apply_gate.synthetic_complete.example.json"
COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json"
COMPLETE_COMMAND_CONFIG = "jarvis/data/ftaw_explicit_manual_apply_command_contract.synthetic_complete.example.json"
EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.example.json"
COMPLETE_EXECUTION_REVIEW_CONFIG = "jarvis/data/ftaw_registry_apply_execution_review_pack.synthetic_complete.example.json"
AUDIT_CONFIG = "jarvis/data/ftaw_full_pipeline_audit_report.example.json"
COMPLETE_AUDIT_CONFIG = "jarvis/data/ftaw_full_pipeline_audit_report.synthetic_complete.example.json"
REAL_INTAKE_CONFIG = "jarvis/data/ftaw_real_evidence_intake_readiness_bridge.example.json"
COMPLETE_REAL_INTAKE_CONFIG = "jarvis/data/ftaw_real_evidence_intake_readiness_bridge.synthetic_complete.example.json"


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
):
    return build_ftaw_real_evidence_intake_readiness_bridge_from_files(
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
    )


class FTAWRealEvidenceIntakeReadinessBridgeTests(unittest.TestCase):
    def test_default_fixture_is_not_ready_for_real_evidence_intake(self) -> None:
        pack = _pack()

        self.assertEqual(pack.real_evidence_intake_readiness_status, "NOT_READY_FOR_REAL_EVIDENCE_INTAKE")

    def test_partial_synthetic_fixture_is_not_fully_ready_and_lists_blockers(self) -> None:
        pack = _partial_pack()

        self.assertEqual(pack.real_evidence_intake_readiness_status, "PARTIAL_READY_FOR_REAL_EVIDENCE_INTAKE")
        self.assertTrue(pack.blocked_reasons)

    def test_synthetic_complete_fixture_is_ready_for_real_evidence_intake_planning(self) -> None:
        pack = _complete_pack()

        self.assertEqual(pack.real_evidence_intake_readiness_status, "READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING")
        self.assertTrue(pack.final_preflight_ready)

    def test_required_real_evidence_types_are_complete(self) -> None:
        pack = _complete_pack()

        self.assertEqual(
            set(pack.required_real_evidence_types),
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
        self.assertEqual(pack.required_real_evidence_types_count, 7)

    def test_platform_availability_requires_account_specific_confirmation(self) -> None:
        pack = _complete_pack()

        self.assertIn(
            "platform_availability requires account-specific confirmation, not public visibility",
            pack.account_specific_evidence_requirements,
        )

    def test_broker_account_specific_evidence_is_private_manual_and_not_commit_safe(self) -> None:
        pack = _complete_pack()

        joined = " ".join(pack.private_manual_evidence_requirements)
        self.assertIn("private/manual", joined)
        self.assertIn("never be committed", joined)

    def test_manual_only_evidence_types_are_not_auto_verified(self) -> None:
        pack = _complete_pack()

        self.assertIn("platform_availability", pack.manual_only_evidence_types)
        self.assertIn("tax_route", pack.manual_only_evidence_types)
        self.assertFalse(pack.evidence_verified)

    def test_bridge_does_not_mark_real_evidence_collected_or_queue_eligible(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.real_evidence_collected)
        self.assertFalse(pack.evidence_verified)
        self.assertFalse(pack.real_evidence_queue_eligibility_created)

    def test_bridge_does_not_approve_or_mutate_or_promote(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _complete_pack()

        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.verified_evidence_promotion)
        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))

    def test_bridge_does_not_create_recommendations_orders_trades_or_executor(self) -> None:
        pack = _complete_pack()

        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)
        self.assertFalse(pack.executor_created)


if __name__ == "__main__":
    unittest.main()
