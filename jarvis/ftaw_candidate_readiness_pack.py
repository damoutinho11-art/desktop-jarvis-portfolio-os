"""Candidate-level readiness pack for the FTAW evidence pipeline.

This report layer summarizes the FTAW source fact, identity guard, verification
queue, manual decision, preview, and promotion dry-run pipeline. It never
promotes evidence, approves assets, mutates registries, recommends allocations,
creates orders, or trades.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_identity_guarded_verification_queue import (
    build_ftaw_identity_guarded_verification_queue,
    load_ftaw_identity_guarded_verification_queue_config,
)
from .ftaw_manual_verification_decision_recorder import (
    build_ftaw_manual_verification_decision_pack,
    load_ftaw_manual_verification_decision_config,
)
from .ftaw_public_source_research_pack import PUBLIC_RESEARCH_EVIDENCE_TYPES
from .ftaw_source_fact_intake import build_ftaw_source_fact_intake_pack, load_ftaw_source_fact_intake_config
from .ftaw_source_identity_guard import build_ftaw_source_identity_guard, load_ftaw_source_identity_guard_config
from .ftaw_verified_evidence_preview_bridge import build_ftaw_verified_evidence_preview_bridge
from .ftaw_verified_evidence_promotion_dry_run import build_ftaw_verified_evidence_promotion_dry_run


READINESS_STATUSES = {
    "BLOCKED",
    "RESEARCH_INCOMPLETE",
    "READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION",
    "READY_FOR_MANUAL_APPROVAL_REVIEW",
}


@dataclass(frozen=True)
class FTAWCandidateReadinessPack:
    target_asset: str
    candidate_readiness_status: str
    source_fact_status: str
    identity_guard_status: str
    verification_queue_status: str
    manual_decision_status: str
    preview_bridge_status: str
    promotion_dry_run_status: str
    required_evidence_types_count: int
    planned_promotion_evidence_types_count: int
    missing_evidence_types_count: int
    planned_promotion_evidence_types: tuple[str, ...]
    missing_evidence_types: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    ready_for_manual_approval_review: bool = False
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _status_from_pipeline(
    source_fact_status: str,
    identity_guard_status: str,
    verification_queue_status: str,
    manual_decision_status: str,
    preview_bridge_status: str,
    promotion_dry_run_status: str,
    planned_count: int,
) -> tuple[str, str, tuple[str, ...]]:
    reasons: list[str] = []
    if identity_guard_status != "identity_guard_passed":
        reasons.append(f"identity guard is {identity_guard_status}.")
        return "BLOCKED", "Confirm source identity before manual evidence promotion.", tuple(reasons)
    if source_fact_status in {"READY_WITH_CORRECTIONS", "BLOCKED"}:
        reasons.append(f"source facts are {source_fact_status}.")
        return "RESEARCH_INCOMPLETE", "Complete missing source facts.", tuple(reasons)
    if verification_queue_status != "READY_FOR_MANUAL_VERIFICATION":
        reasons.append(f"verification queue is {verification_queue_status}.")
        return "BLOCKED", "Resolve verification queue blockers.", tuple(reasons)
    if manual_decision_status != "DECISIONS_RECORDED":
        reasons.append(f"manual decision status is {manual_decision_status}.")
        return "BLOCKED", "Record manual verification decisions.", tuple(reasons)
    if preview_bridge_status != "PREVIEW_READY":
        reasons.append(f"preview bridge status is {preview_bridge_status}.")
        return "BLOCKED", "Create preview-ready evidence records.", tuple(reasons)
    if promotion_dry_run_status != "DRY_RUN_PLANNED" or planned_count == 0:
        reasons.append(f"promotion dry-run status is {promotion_dry_run_status}.")
        return "BLOCKED", "Run promotion dry-run planning.", tuple(reasons)
    return (
        "READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION",
        "Manually review dry-run promotion plan; do not approve asset yet.",
        (),
    )


def build_ftaw_candidate_readiness_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
) -> FTAWCandidateReadinessPack:
    Path(preview_bridge_config_path).read_text(encoding="utf-8")
    Path(promotion_dry_run_config_path).read_text(encoding="utf-8")
    Path(readiness_config_path).read_text(encoding="utf-8")

    queue_config = load_ftaw_identity_guarded_verification_queue_config(queue_config_path)
    fact_intake_config = queue_config.synthetic_fact_intake_config or load_ftaw_source_fact_intake_config(fact_intake_config_path)
    identity_guard_config = queue_config.synthetic_identity_guard_config or load_ftaw_source_identity_guard_config(identity_guard_config_path)

    source_facts = build_ftaw_source_fact_intake_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config,
    )
    identity = build_ftaw_source_identity_guard(
        source_registry_path,
        reviewed_registry_copy_path,
        fact_intake_config,
        identity_guard_config,
    )
    queue = build_ftaw_identity_guarded_verification_queue(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config,
        identity_guard_config,
        queue_config,
    )
    decisions = build_ftaw_manual_verification_decision_pack(
        queue,
        load_ftaw_manual_verification_decision_config(decision_config_path),
        queue_config_path,
        decision_config_path,
    )
    preview = build_ftaw_verified_evidence_preview_bridge(queue, decisions)
    dry_run = build_ftaw_verified_evidence_promotion_dry_run(preview)

    required = tuple(PUBLIC_RESEARCH_EVIDENCE_TYPES)
    planned_types = tuple(
        sorted(
            {
                record.evidence_type
                for record in dry_run.plan_records
                if record.planned_promotion_status == "planned_for_promotion"
                and record.promotion_mode == "dry_run"
            }
        )
    )
    missing_types = tuple(evidence_type for evidence_type in required if evidence_type not in planned_types)
    status, next_action, reasons = _status_from_pipeline(
        source_facts.intake_status,
        identity.identity_guard_status,
        queue.queue_status,
        decisions.decision_pack_status,
        preview.preview_bridge_status,
        dry_run.dry_run_status,
        dry_run.planned_for_promotion_count,
    )
    extra_reasons: list[str] = list(reasons)
    if missing_types:
        extra_reasons.append("not all required evidence types have planned dry-run promotions.")

    return FTAWCandidateReadinessPack(
        target_asset=queue.target_asset_id,
        candidate_readiness_status=status,
        source_fact_status=source_facts.intake_status,
        identity_guard_status=identity.identity_guard_status,
        verification_queue_status=queue.queue_status,
        manual_decision_status=decisions.decision_pack_status,
        preview_bridge_status=preview.preview_bridge_status,
        promotion_dry_run_status=dry_run.dry_run_status,
        required_evidence_types_count=len(required),
        planned_promotion_evidence_types_count=len(planned_types),
        missing_evidence_types_count=len(missing_types),
        planned_promotion_evidence_types=planned_types,
        missing_evidence_types=missing_types,
        blocked_reasons=tuple(dict.fromkeys(extra_reasons)),
        next_manual_action=next_action,
        ready_for_manual_approval_review=False,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )
