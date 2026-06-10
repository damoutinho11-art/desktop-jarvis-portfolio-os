"""Manual approval review gate for FTAW candidate readiness.

This layer creates a human review packet only when candidate readiness is
READY_FOR_MANUAL_APPROVAL_REVIEW. It does not approve assets, promote evidence,
mutate registries, recommend allocations, create orders, or trade.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_candidate_readiness_pack import FTAWCandidateReadinessPack, build_ftaw_candidate_readiness_pack


@dataclass(frozen=True)
class FTAWManualApprovalReviewPacket:
    asset_id: str
    candidate_readiness_status: str
    required_evidence_types_count: int
    planned_promotion_evidence_types_count: int
    missing_evidence_types: tuple[str, ...]
    evidence_coverage_summary: str
    dry_run_promotion_references: tuple[str, ...]
    manual_warnings: tuple[str, ...]
    approval_review_only: bool = True
    approved: bool = False
    approval_status_change: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWManualApprovalReviewGatePack:
    approval_review_gate_status: str
    target_asset: str
    candidate_readiness_status: str
    ready_for_manual_approval_review: bool
    required_evidence_types_count: int
    planned_promotion_evidence_types_count: int
    missing_evidence_types_count: int
    missing_evidence_types: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    review_packet_created: bool
    next_manual_action: str
    review_packet: FTAWManualApprovalReviewPacket | None
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def build_ftaw_manual_approval_review_gate(
    readiness: FTAWCandidateReadinessPack,
    promotion_modes: tuple[str, ...] | None = None,
) -> FTAWManualApprovalReviewGatePack:
    modes = promotion_modes or tuple("dry_run" for _ in readiness.planned_promotion_evidence_types)
    blocked: list[str] = []
    if readiness.candidate_readiness_status != "READY_FOR_MANUAL_APPROVAL_REVIEW":
        blocked.append(f"candidate readiness status is {readiness.candidate_readiness_status}.")
    if not readiness.ready_for_manual_approval_review:
        blocked.append("ready_for_manual_approval_review is false.")
    if readiness.missing_evidence_types:
        blocked.append("missing evidence types remain.")
    if readiness.planned_promotion_evidence_types_count != readiness.required_evidence_types_count:
        blocked.append("planned promotion evidence coverage is incomplete.")
    if any(mode != "dry_run" for mode in modes):
        blocked.append("all planned promotions must remain dry_run.")

    if blocked:
        return FTAWManualApprovalReviewGatePack(
            approval_review_gate_status="BLOCKED",
            target_asset=readiness.target_asset,
            candidate_readiness_status=readiness.candidate_readiness_status,
            ready_for_manual_approval_review=readiness.ready_for_manual_approval_review,
            required_evidence_types_count=readiness.required_evidence_types_count,
            planned_promotion_evidence_types_count=readiness.planned_promotion_evidence_types_count,
            missing_evidence_types_count=readiness.missing_evidence_types_count,
            missing_evidence_types=readiness.missing_evidence_types,
            blocked_reasons=tuple(dict.fromkeys(blocked)),
            review_packet_created=False,
            next_manual_action="Resolve readiness blockers before human approval review.",
            review_packet=None,
            no_verified_evidence_promotion=True,
            approvals_created=False,
            registry_mutation_performed=False,
            allocation_recommendation_created=False,
            buy_sell_requests_created=False,
            trades_executed=False,
        )

    references = tuple(f"{readiness.target_asset}:{evidence_type}:dry_run" for evidence_type in readiness.planned_promotion_evidence_types)
    warnings = (
        "approval review packet is not asset approval",
        "approval review packet is not verified evidence promotion",
        "approval review packet is not registry mutation",
        "approval review packet is not allocation advice",
        "approval review packet is not a buy/sell request",
        "approval review packet is not trade execution",
    )
    packet = FTAWManualApprovalReviewPacket(
        asset_id=readiness.target_asset,
        candidate_readiness_status=readiness.candidate_readiness_status,
        required_evidence_types_count=readiness.required_evidence_types_count,
        planned_promotion_evidence_types_count=readiness.planned_promotion_evidence_types_count,
        missing_evidence_types=readiness.missing_evidence_types,
        evidence_coverage_summary=(
            f"{readiness.planned_promotion_evidence_types_count} of "
            f"{readiness.required_evidence_types_count} required evidence types have dry-run planned promotions."
        ),
        dry_run_promotion_references=references,
        manual_warnings=warnings,
        approval_review_only=True,
        approved=False,
        approval_status_change=False,
        buy_signal=False,
    )
    return FTAWManualApprovalReviewGatePack(
        approval_review_gate_status="READY_FOR_HUMAN_APPROVAL_REVIEW",
        target_asset=readiness.target_asset,
        candidate_readiness_status=readiness.candidate_readiness_status,
        ready_for_manual_approval_review=True,
        required_evidence_types_count=readiness.required_evidence_types_count,
        planned_promotion_evidence_types_count=readiness.planned_promotion_evidence_types_count,
        missing_evidence_types_count=readiness.missing_evidence_types_count,
        missing_evidence_types=readiness.missing_evidence_types,
        blocked_reasons=(),
        review_packet_created=True,
        next_manual_action="Human may review the approval packet; this is not approval.",
        review_packet=packet,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_manual_approval_review_gate_from_files(
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
    approval_review_gate_config_path: str | Path,
) -> FTAWManualApprovalReviewGatePack:
    Path(approval_review_gate_config_path).read_text(encoding="utf-8")
    readiness = build_ftaw_candidate_readiness_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
    )
    return build_ftaw_manual_approval_review_gate(readiness)
