import tempfile
import unittest
from pathlib import Path

from jarvis.ftaw_manual_verification_decision_recorder import (
    FTAWManualVerificationDecision,
    FTAWManualVerificationDecisionConfig,
    build_ftaw_manual_verification_decision_pack,
)
from jarvis.ftaw_identity_guarded_verification_queue import build_ftaw_identity_guarded_verification_queue_from_files
from jarvis.ftaw_verified_evidence_preview_bridge import build_ftaw_verified_evidence_preview_bridge
from jarvis.ftaw_verified_evidence_promotion_dry_run import (
    build_ftaw_verified_evidence_promotion_dry_run,
    build_ftaw_verified_evidence_promotion_dry_run_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
SYNTHETIC_QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.synthetic_pass.example.json"
DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.example.json"
SYNTHETIC_DECISION_CONFIG = "jarvis/data/ftaw_manual_verification_decision_recorder.synthetic_pass.example.json"
PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.example.json"
SYNTHETIC_PREVIEW_CONFIG = "jarvis/data/ftaw_verified_evidence_preview_bridge.synthetic_pass.example.json"
DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json"
SYNTHETIC_DRY_RUN_CONFIG = "jarvis/data/ftaw_verified_evidence_promotion_dry_run.synthetic_pass.example.json"
ITEM_ID = "ftaw_global_core_candidate:fund_metadata"


def _preview_pack(decision: str):
    queue = build_ftaw_identity_guarded_verification_queue_from_files(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        INTAKE_CONFIG,
        GUARD_CONFIG,
        SYNTHETIC_QUEUE_CONFIG,
    )
    decisions = build_ftaw_manual_verification_decision_pack(
        queue,
        FTAWManualVerificationDecisionConfig(
            decisions=(FTAWManualVerificationDecision(ITEM_ID, decision, "Synthetic manual decision."),)
        ),
        SYNTHETIC_QUEUE_CONFIG,
        "inline_decisions",
    )
    return build_ftaw_verified_evidence_preview_bridge(queue, decisions)


class FTAWVerifiedEvidencePromotionDryRunTests(unittest.TestCase):
    def test_default_blocked_preview_path_produces_zero_planned_promotions(self) -> None:
        pack = build_ftaw_verified_evidence_promotion_dry_run_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
            DECISION_CONFIG,
            PREVIEW_CONFIG,
            DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.planned_for_promotion_count, 0)
        self.assertEqual(pack.blocked_or_excluded_count, 1)

    def test_synthetic_preview_ready_path_produces_exactly_one_planned_promotion(self) -> None:
        pack = build_ftaw_verified_evidence_promotion_dry_run_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            SYNTHETIC_QUEUE_CONFIG,
            SYNTHETIC_DECISION_CONFIG,
            SYNTHETIC_PREVIEW_CONFIG,
            SYNTHETIC_DRY_RUN_CONFIG,
        )

        self.assertEqual(pack.dry_run_status, "DRY_RUN_PLANNED")
        self.assertEqual(pack.planned_for_promotion_count, 1)
        self.assertEqual(pack.plan_records[0].asset_id, "ftaw_global_core_candidate")
        self.assertEqual(pack.plan_records[0].evidence_type, "fund_metadata")

    def test_non_preview_ready_items_are_excluded(self) -> None:
        pack = build_ftaw_verified_evidence_promotion_dry_run(_preview_pack("reject"))

        self.assertEqual(pack.planned_for_promotion_count, 0)
        self.assertEqual(pack.blocked_or_excluded_count, 1)
        self.assertEqual(pack.plan_records[0].planned_promotion_status, "excluded_excluded_rejected")

    def test_planned_record_has_dry_run_mode(self) -> None:
        record = build_ftaw_verified_evidence_promotion_dry_run(_preview_pack("accept_for_verified_evidence_preview")).plan_records[0]

        self.assertEqual(record.promotion_mode, "dry_run")

    def test_planned_promotion_does_not_set_verified_by_user_true(self) -> None:
        record = build_ftaw_verified_evidence_promotion_dry_run(_preview_pack("accept_for_verified_evidence_preview")).plan_records[0]

        self.assertFalse(record.verified_by_user)

    def test_dry_run_does_not_write_verified_evidence_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "verified_evidence.json"

            build_ftaw_verified_evidence_promotion_dry_run(_preview_pack("accept_for_verified_evidence_preview"))

            self.assertFalse(output.exists())

    def test_dry_run_does_not_approve_mutate_recommend_order_or_trade(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        pack = build_ftaw_verified_evidence_promotion_dry_run(_preview_pack("accept_for_verified_evidence_preview"))

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertTrue(pack.no_verified_evidence_promotion)
        self.assertFalse(pack.approvals_created)
        self.assertFalse(pack.registry_mutation_performed)
        self.assertFalse(pack.allocation_recommendation_created)
        self.assertFalse(pack.buy_sell_requests_created)
        self.assertFalse(pack.trades_executed)


if __name__ == "__main__":
    unittest.main()
