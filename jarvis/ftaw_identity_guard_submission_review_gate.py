"""FTAW identity guard submission review gate.

This read-only gate reviews the v4.34 identity guard submission dry-run packet
and decides whether a future explicit manual submission command could be
prepared. It never runs identity guard, creates pass records, creates queue
eligibility, verifies evidence, approves assets, mutates registries, promotes
evidence, recommends allocations, creates orders, trades, or creates an
executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_identity_guard_submission_dry_run_pack import (
    FTAWIdentityGuardSubmissionDryRunPack,
    build_ftaw_identity_guard_submission_dry_run_pack_from_files,
)
from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES


@dataclass(frozen=True)
class FTAWIdentityGuardSubmissionReviewCheck:
    evidence_type: str
    present: bool
    source_reference_id: str | None
    ready: bool
    reason: str
    identity_guard_executed: bool = False
    identity_guard_pass_created: bool = False
    queue_eligibility_created: bool = False
    evidence_verified: bool = False
    approved_asset: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWIdentityGuardSubmissionReviewGatePack:
    target_asset: str
    gate_status: str
    upstream_v4_34_status: str
    required_packet_item_count: int
    present_packet_item_count: int
    missing_packet_item_count: int
    manual_private_outstanding_count: int
    readiness_checks: tuple[FTAWIdentityGuardSubmissionReviewCheck, ...]
    manual_private_outstanding: tuple
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    identity_guard_executed: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
    verified_evidence_promotion: bool = False
    approvals_created: bool = False
    registry_mutation: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _packet_item_safe(item) -> bool:
    return not (
        item.identity_guard_executed
        or item.identity_guard_pass_created
        or item.queue_eligibility_created
        or item.evidence_verified
        or item.approved_asset
        or item.buy_signal
    )


def build_ftaw_identity_guard_submission_review_gate(
    dry_run_pack: FTAWIdentityGuardSubmissionDryRunPack,
) -> FTAWIdentityGuardSubmissionReviewGatePack:
    items_by_type = {item.evidence_type: item for item in dry_run_pack.packet_items}
    blocked: list[str] = []

    if dry_run_pack.dry_run_status != "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY":
        blocked.append(f"identity guard submission dry-run status is {dry_run_pack.dry_run_status}.")

    if dry_run_pack.dry_run_packet_item_count != len(PUBLIC_EVIDENCE_TYPES):
        blocked.append(f"dry-run packet must contain exactly {len(PUBLIC_EVIDENCE_TYPES)} public evidence items.")

    readiness_checks: list[FTAWIdentityGuardSubmissionReviewCheck] = []
    for evidence_type in PUBLIC_EVIDENCE_TYPES:
        item = items_by_type.get(evidence_type)
        if item is None:
            reason = f"missing dry-run packet item for {evidence_type}"
            blocked.append(reason)
            readiness_checks.append(
                FTAWIdentityGuardSubmissionReviewCheck(
                    evidence_type=evidence_type,
                    present=False,
                    source_reference_id=None,
                    ready=False,
                    reason=reason,
                )
            )
            continue

        item_blockers = []
        if not _packet_item_safe(item):
            item_blockers.append(f"dry-run packet item for {evidence_type} has forbidden safety side-effect flags.")
        if item.evidence_type in {"platform_availability", "tax_route"}:
            item_blockers.append(f"{item.evidence_type} must remain excluded/manual/private outstanding.")

        blocked.extend(item_blockers)
        readiness_checks.append(
            FTAWIdentityGuardSubmissionReviewCheck(
                evidence_type=evidence_type,
                present=True,
                source_reference_id=item.source_reference_id,
                ready=not item_blockers,
                reason="ready for future explicit manual identity guard submission command"
                if not item_blockers
                else "; ".join(item_blockers),
                identity_guard_executed=item.identity_guard_executed,
                identity_guard_pass_created=item.identity_guard_pass_created,
                queue_eligibility_created=item.queue_eligibility_created,
                evidence_verified=item.evidence_verified,
                approved_asset=item.approved_asset,
                buy_signal=item.buy_signal,
            )
        )

    packet_types = {item.evidence_type for item in dry_run_pack.packet_items}
    for excluded_type in ("platform_availability", "tax_route"):
        if excluded_type in packet_types:
            blocked.append(f"{excluded_type} must not be included in the public identity guard submission packet.")

    blocked.extend(dry_run_pack.blocked_reasons)
    missing_count = sum(1 for check in readiness_checks if not check.present)

    if dry_run_pack.dry_run_packet_item_count == 0:
        status = "BLOCKED_NO_IDENTITY_GUARD_DRY_RUN_PACKET"
        next_action = "Create a complete accepted v4.34 identity guard submission dry-run packet first."
    elif blocked:
        status = "PARTIAL_IDENTITY_GUARD_SUBMISSION_REVIEW_READY"
        next_action = "Resolve dry-run packet blockers before preparing an explicit manual identity guard submission command."
    else:
        status = "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND"
        next_action = "A future explicit manual identity guard submission command may be prepared; no identity guard was executed."

    return FTAWIdentityGuardSubmissionReviewGatePack(
        target_asset=dry_run_pack.target_asset,
        gate_status=status,
        upstream_v4_34_status=dry_run_pack.dry_run_status,
        required_packet_item_count=len(PUBLIC_EVIDENCE_TYPES),
        present_packet_item_count=len(packet_types & set(PUBLIC_EVIDENCE_TYPES)),
        missing_packet_item_count=missing_count,
        manual_private_outstanding_count=dry_run_pack.manual_private_outstanding_count,
        readiness_checks=tuple(readiness_checks),
        manual_private_outstanding=dry_run_pack.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        identity_guard_executed=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
        verified_evidence_promotion=False,
        approvals_created=False,
        registry_mutation=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
        automatic_fact_extraction=False,
    )


def build_ftaw_identity_guard_submission_review_gate_from_files(
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
    human_decision_config_path: str | Path,
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
    real_evidence_intake_readiness_config_path: str | Path,
    collection_checklist_config_path: str | Path,
    public_source_reference_plan_config_path: str | Path,
    manual_public_source_reference_entry_config_path: str | Path,
    manual_source_fact_entry_config_path: str | Path,
    identity_guard_bridge_config_path: str | Path,
    identity_guard_review_decision_config_path: str | Path,
    identity_guard_submission_dry_run_config_path: str | Path,
    identity_guard_submission_review_gate_config_path: str | Path,
) -> FTAWIdentityGuardSubmissionReviewGatePack:
    Path(identity_guard_submission_review_gate_config_path).read_text(encoding="utf-8")
    dry_run_pack = build_ftaw_identity_guard_submission_dry_run_pack_from_files(
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
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
        full_pipeline_audit_config_path,
        real_evidence_intake_readiness_config_path,
        collection_checklist_config_path,
        public_source_reference_plan_config_path,
        manual_public_source_reference_entry_config_path,
        manual_source_fact_entry_config_path,
        identity_guard_bridge_config_path,
        identity_guard_review_decision_config_path,
        identity_guard_submission_dry_run_config_path,
    )
    return build_ftaw_identity_guard_submission_review_gate(dry_run_pack)
