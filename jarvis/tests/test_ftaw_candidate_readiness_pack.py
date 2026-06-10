import unittest
from pathlib import Path

from jarvis.ftaw_candidate_readiness_pack import build_ftaw_candidate_readiness_pack
from jarvis.ftaw_identity_guarded_verification_queue import FTAWIdentityGuardedVerificationQueueConfig
from jarvis.ftaw_manual_verification_decision_recorder import (
    FTAWManualVerificationDecision,
    FTAWManualVerificationDecisionConfig,
    build_ftaw_manual_verification_decision_pack,
)
from jarvis.ftaw_source_fact_intake import FTAWSourceFactIntakeConfig, FTAWSourceFactRecord
from jarvis.ftaw_source_identity_guard import FTAWSourceIdentityGuardConfig
from jarvis.ftaw_verified_evidence_preview_bridge import build_ftaw_verified_evidence_preview_bridge
from jarvis.ftaw_verified_evidence_promotion_dry_run import build_ftaw_verified_evidence_promotion_dry_run
from jarvis.ftaw_identity_guarded_verification_queue import build_ftaw_identity_guarded_verification_queue


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_complete.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_complete.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
SYNTHETIC_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
SYNTHETIC_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json"
READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.example.json"
SYNTHETIC_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_pass.example.json"
SYNTHETIC_COMPLETE_READINESS_CONFIG = "jarvis/data/ftaw_candidate_readiness_pack.synthetic_complete.example.json"
TARGET = "ftaw_global_core_candidate"
ITEM_ID = f"{TARGET}:fund_metadata"


def _readiness(queue_config=QUEUE_CONFIG, decision_config=DECISION_CONFIG, preview_config=PREVIEW_CONFIG, dry_run_config=DRY_RUN_CONFIG):
    return build_ftaw_candidate_readiness_pack(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        queue_config,
        decision_config,
        preview_config,
        dry_run_config,
        SYNTHETIC_COMPLETE_READINESS_CONFIG if queue_config == SYNTHETIC_COMPLETE_QUEUE_CONFIG else READINESS_CONFIG,
    )


def _record(**overrides):
    data = {
        "asset_id": TARGET,
        "evidence_type": "fund_metadata",
        "source_name": "Synthetic provider page",
        "source_quality": "provider_factsheet",
        "url_reference": "https://provider.example/fund",
        "file_reference": None,
        "as_of": "2026-06-09",
        "extracted_facts": {
            "name": "Synthetic FTAW Fund",
            "ticker": "FTAW",
            "isin_or_symbol": "SYNTHETICISIN",
            "provider": "Synthetic Provider",
            "index_tracked": "Synthetic Index",
            "replication_method": "physical",
        },
        "user_notes": "Synthetic test facts.",
    }
    data.update(overrides)
    return FTAWSourceFactRecord(**data)


def _guard(**overrides):
    data = {
        "asset_id": TARGET,
        "expected_name": "Synthetic FTAW Fund",
        "expected_ticker": "FTAW",
        "expected_isin_or_symbol": "SYNTHETICISIN",
        "expected_provider": "Synthetic Provider",
        "expected_index_tracked": "Synthetic Index",
        "allowed_source_names": ("Synthetic provider page",),
        "allowed_url_domains": ("provider.example",),
    }
    data.update(overrides)
    return FTAWSourceIdentityGuardConfig(**data)


def _manual_pipeline(records, guard, decision):
    fact_config = FTAWSourceFactIntakeConfig(tuple(records))
    queue = build_ftaw_identity_guarded_verification_queue(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        fact_config,
        guard,
        FTAWIdentityGuardedVerificationQueueConfig(TARGET),
    )
    decisions = build_ftaw_manual_verification_decision_pack(
        queue,
        FTAWManualVerificationDecisionConfig(tuple(decision)),
        "inline_queue",
        "inline_decision",
    )
    preview = build_ftaw_verified_evidence_preview_bridge(queue, decisions)
    return build_ftaw_verified_evidence_promotion_dry_run(preview)


class FTAWCandidateReadinessPackTests(unittest.TestCase):
    def test_default_placeholder_fixture_is_blocked(self) -> None:
        pack = _readiness()

        self.assertEqual(pack.candidate_readiness_status, "BLOCKED")
        self.assertEqual(pack.identity_guard_status, "needs_identity_confirmation")

    def test_synthetic_pass_reaches_ready_for_manual_verified_evidence_promotion(self) -> None:
        pack = _readiness(SYNTHETIC_QUEUE_CONFIG, SYNTHETIC_DECISION_CONFIG, SYNTHETIC_PREVIEW_CONFIG, SYNTHETIC_DRY_RUN_CONFIG)

        self.assertEqual(pack.candidate_readiness_status, "READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION")
        self.assertEqual(pack.planned_promotion_evidence_types, ("fund_metadata",))
        self.assertEqual(pack.planned_promotion_evidence_types_count, 1)
        self.assertEqual(pack.missing_evidence_types_count, 4)

    def test_synthetic_pass_does_not_reach_asset_approval_or_buy_signal(self) -> None:
        pack = _readiness(SYNTHETIC_QUEUE_CONFIG, SYNTHETIC_DECISION_CONFIG, SYNTHETIC_PREVIEW_CONFIG, SYNTHETIC_DRY_RUN_CONFIG)

        self.assertFalse(pack.ready_for_manual_approval_review)
        self.assertNotEqual(pack.candidate_readiness_status, "READY_FOR_MANUAL_APPROVAL_REVIEW")
        self.assertFalse(pack.buy_sell_requests_created)

    def test_synthetic_complete_reaches_full_planned_coverage(self) -> None:
        pack = _readiness(
            SYNTHETIC_COMPLETE_QUEUE_CONFIG,
            SYNTHETIC_COMPLETE_DECISION_CONFIG,
            SYNTHETIC_COMPLETE_PREVIEW_CONFIG,
            SYNTHETIC_COMPLETE_DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.planned_promotion_evidence_types_count, 5)
        self.assertEqual(pack.missing_evidence_types_count, 0)
        self.assertEqual(pack.missing_evidence_types, ())

    def test_synthetic_complete_manual_approval_review_is_not_approval_or_buy_signal(self) -> None:
        pack = _readiness(
            SYNTHETIC_COMPLETE_QUEUE_CONFIG,
            SYNTHETIC_COMPLETE_DECISION_CONFIG,
            SYNTHETIC_COMPLETE_PREVIEW_CONFIG,
            SYNTHETIC_COMPLETE_DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.candidate_readiness_status, "READY_FOR_MANUAL_APPROVAL_REVIEW")
        self.assertTrue(pack.ready_for_manual_approval_review)
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.buy_sell_requests_created)

    def test_missing_source_facts_block_or_mark_research_incomplete(self) -> None:
        facts = dict(_record().extracted_facts)
        facts["replication_method"] = "<missing>"
        dry_run = _manual_pipeline([_record(extracted_facts=facts)], _guard(), [FTAWManualVerificationDecision(ITEM_ID, "accept_for_verified_evidence_preview", "note")])

        self.assertEqual(dry_run.planned_for_promotion_count, 0)

    def test_identity_mismatch_blocks(self) -> None:
        pack = _manual_pipeline([_record(extracted_facts={**_record().extracted_facts, "ticker": "WRONG"})], _guard(), [FTAWManualVerificationDecision(ITEM_ID, "accept_for_verified_evidence_preview", "note")])

        self.assertEqual(pack.planned_for_promotion_count, 0)

    def test_missing_manual_decision_blocks_advancement(self) -> None:
        pack = _manual_pipeline([_record()], _guard(), [])

        self.assertEqual(pack.planned_for_promotion_count, 0)
        self.assertEqual(pack.dry_run_status, "NO_PROMOTIONS_PLANNED")

    def test_no_preview_ready_records_blocks_advancement(self) -> None:
        pack = _manual_pipeline([_record()], _guard(), [FTAWManualVerificationDecision(ITEM_ID, "reject", "note")])

        self.assertEqual(pack.planned_for_promotion_count, 0)

    def test_no_planned_promotion_records_blocks_approval_review(self) -> None:
        pack = _readiness()

        self.assertNotEqual(pack.candidate_readiness_status, "READY_FOR_MANUAL_APPROVAL_REVIEW")

    def test_planned_promotion_records_are_dry_run_only(self) -> None:
        dry_run = _manual_pipeline([_record()], _guard(), [FTAWManualVerificationDecision(ITEM_ID, "accept_for_verified_evidence_preview", "note")])

        self.assertEqual(dry_run.plan_records[0].promotion_mode, "dry_run")

    def test_no_verified_evidence_promotion_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = _readiness(SYNTHETIC_QUEUE_CONFIG, SYNTHETIC_DECISION_CONFIG, SYNTHETIC_PREVIEW_CONFIG, SYNTHETIC_DRY_RUN_CONFIG)

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)

    def test_manual_only_evidence_types_are_not_required_for_completion(self) -> None:
        pack = _readiness(
            SYNTHETIC_COMPLETE_QUEUE_CONFIG,
            SYNTHETIC_COMPLETE_DECISION_CONFIG,
            SYNTHETIC_COMPLETE_PREVIEW_CONFIG,
            SYNTHETIC_COMPLETE_DRY_RUN_CONFIG,
        )

        self.assertNotIn("platform_availability", pack.missing_evidence_types)
        self.assertNotIn("tax_route", pack.missing_evidence_types)


if __name__ == "__main__":
    unittest.main()
