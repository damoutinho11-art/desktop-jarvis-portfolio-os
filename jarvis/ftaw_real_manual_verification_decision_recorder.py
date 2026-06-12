"""FTAW real manual verification decision recorder.

This read-only recorder consumes v4.39 verification queue dry-run preview items
and records human/manual verification decisions for a later verified evidence
preview review. It does not verify evidence, promote evidence, approve assets,
mutate registries, recommend allocations, create orders, trade, create an
executor, ingest private files, fetch sources, download sources, or extract
facts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_identity_guarded_verification_queue_dry_run_bridge import (
    FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack,
    build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files,
)
from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES


ALLOWED_MANUAL_VERIFICATION_DECISIONS = (
    "accept_for_verified_evidence_preview",
    "reject",
    "needs_correction",
)


@dataclass(frozen=True)
class FTAWRealManualVerificationDecisionRecord:
    evidence_type: str
    source_reference_id: str
    manual_verification_decision: str
    reviewed_by_user: bool
    user_asserted_manual_verification_decision_completed: bool
    user_asserted_no_evidence_verification: bool
    user_asserted_no_queue_eligibility: bool
    user_asserted_no_promotion: bool
    reviewer_notes: str
    decision_status: str
    decision_recorded: bool
    verified_evidence_preview_ready: bool
    evidence_verified: bool = False
    verified_evidence_promoted: bool = False
    queue_eligibility_created: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRealManualVerificationDecisionRecorderPack:
    target_asset: str
    decision_recorder_status: str
    upstream_v4_39_status: str
    manual_decision_count: int
    accepted_for_preview_count: int
    rejected_needs_correction_count: int
    missing_decision_count: int
    dry_run_preview_item_count: int
    manual_private_outstanding_count: int
    decision_records: tuple[FTAWRealManualVerificationDecisionRecord, ...]
    manual_private_outstanding: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    real_queue_item_created: bool = False
    queue_eligibility_created: bool = False
    evidence_verified: bool = False
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


def _load_manual_decisions(path: str | Path) -> tuple[dict, ...]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = data.get("manual_verification_decisions", ())
    if entries is None:
        return ()
    if not isinstance(entries, list):
        raise ValueError("manual_verification_decisions must be a list when present")
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("manual verification decision entries must be objects")
    return tuple(entries)


def _record_from_entry(entry: dict, eligible_preview_types: set[str]) -> FTAWRealManualVerificationDecisionRecord:
    evidence_type = str(entry.get("evidence_type", ""))
    source_reference_id = str(entry.get("source_reference_id", ""))
    decision = str(entry.get("manual_verification_decision", ""))
    assertions = (
        entry.get("reviewed_by_user") is True,
        entry.get("user_asserted_manual_verification_decision_completed") is True,
        entry.get("user_asserted_no_evidence_verification") is True,
        entry.get("user_asserted_no_queue_eligibility") is True,
        entry.get("user_asserted_no_promotion") is True,
    )

    if evidence_type not in PUBLIC_EVIDENCE_TYPES:
        status = "blocked_unsupported_evidence_type"
    elif evidence_type not in eligible_preview_types:
        status = "blocked_no_matching_dry_run_preview_item"
    elif decision not in ALLOWED_MANUAL_VERIFICATION_DECISIONS:
        status = "blocked_invalid_manual_verification_decision"
    elif not all(assertions):
        status = "blocked_missing_user_assertion"
    elif decision == "accept_for_verified_evidence_preview":
        status = "accepted_for_verified_evidence_preview_review"
    elif decision == "reject":
        status = "manual_verification_rejected"
    else:
        status = "manual_verification_needs_correction"

    return FTAWRealManualVerificationDecisionRecord(
        evidence_type=evidence_type,
        source_reference_id=source_reference_id,
        manual_verification_decision=decision,
        reviewed_by_user=entry.get("reviewed_by_user") is True,
        user_asserted_manual_verification_decision_completed=entry.get("user_asserted_manual_verification_decision_completed") is True,
        user_asserted_no_evidence_verification=entry.get("user_asserted_no_evidence_verification") is True,
        user_asserted_no_queue_eligibility=entry.get("user_asserted_no_queue_eligibility") is True,
        user_asserted_no_promotion=entry.get("user_asserted_no_promotion") is True,
        reviewer_notes=str(entry.get("reviewer_notes", "")),
        decision_status=status,
        decision_recorded=status in {
            "accepted_for_verified_evidence_preview_review",
            "manual_verification_rejected",
            "manual_verification_needs_correction",
        },
        verified_evidence_preview_ready=status == "accepted_for_verified_evidence_preview_review",
        evidence_verified=False,
        verified_evidence_promoted=False,
        queue_eligibility_created=False,
        approved_asset=False,
        registry_mutation=False,
        buy_signal=False,
    )


def build_ftaw_real_manual_verification_decision_recorder(
    queue_dry_run: FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack,
    manual_decision_entries: tuple[dict, ...],
) -> FTAWRealManualVerificationDecisionRecorderPack:
    eligible_preview_types = {item.evidence_type for item in queue_dry_run.preview_items if item.dry_run_queue_preview}
    records = tuple(
        sorted(
            (_record_from_entry(entry, eligible_preview_types) for entry in manual_decision_entries),
            key=lambda item: (item.evidence_type, item.source_reference_id),
        )
    )
    public_records = tuple(record for record in records if record.evidence_type in PUBLIC_EVIDENCE_TYPES)
    accepted_types = {
        record.evidence_type
        for record in public_records
        if record.decision_status == "accepted_for_verified_evidence_preview_review"
    }
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in accepted_types)
    rejected_or_correction = tuple(
        record
        for record in public_records
        if record.decision_status in {"manual_verification_rejected", "manual_verification_needs_correction"}
    )

    blocked: list[str] = []
    if queue_dry_run.queue_dry_run_bridge_status != "VERIFICATION_QUEUE_DRY_RUN_READY_FOR_MANUAL_REVIEW":
        blocked.append(f"verification queue dry-run bridge status is {queue_dry_run.queue_dry_run_bridge_status}.")
    for record in records:
        if record.decision_status.startswith("blocked_"):
            blocked.append(f"{record.evidence_type or 'unknown'} decision blocked: {record.decision_status}.")
        elif record.decision_status == "manual_verification_rejected":
            blocked.append(f"{record.evidence_type} manual verification decision is reject.")
        elif record.decision_status == "manual_verification_needs_correction":
            blocked.append(f"{record.evidence_type} manual verification decision needs correction.")
    blocked.extend(f"missing accepted manual verification decision for {evidence_type}" for evidence_type in missing_types)
    blocked.extend(queue_dry_run.blocked_reasons)

    if queue_dry_run.queue_dry_run_bridge_status == "BLOCKED_NO_MANUAL_IDENTITY_GUARD_RESULTS" and not records:
        status = "BLOCKED_NO_VERIFICATION_QUEUE_DRY_RUN"
        next_action = "Resolve v4.39 verification queue dry-run readiness before recording manual verification decisions."
    elif not records:
        status = "NO_MANUAL_VERIFICATION_DECISIONS_RECORDED"
        next_action = "Record manual verification decisions for all dry-run preview items."
    elif blocked:
        status = "PARTIAL_MANUAL_VERIFICATION_DECISIONS_RECORDED"
        next_action = "Resolve missing, rejected, or needs-correction manual verification decisions before verified evidence preview review."
    else:
        status = "MANUAL_VERIFICATION_DECISIONS_RECORDED_FOR_VERIFIED_EVIDENCE_PREVIEW_REVIEW"
        next_action = "A future verified evidence preview review may inspect these manual decisions; no evidence was verified."

    return FTAWRealManualVerificationDecisionRecorderPack(
        target_asset=queue_dry_run.target_asset,
        decision_recorder_status=status,
        upstream_v4_39_status=queue_dry_run.queue_dry_run_bridge_status,
        manual_decision_count=len(public_records),
        accepted_for_preview_count=len(accepted_types),
        rejected_needs_correction_count=len(rejected_or_correction),
        missing_decision_count=len(missing_types),
        dry_run_preview_item_count=queue_dry_run.dry_run_preview_item_count,
        manual_private_outstanding_count=queue_dry_run.manual_private_outstanding_count,
        decision_records=public_records,
        manual_private_outstanding=queue_dry_run.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        real_queue_item_created=False,
        queue_eligibility_created=False,
        evidence_verified=False,
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


def build_ftaw_real_manual_verification_decision_recorder_from_files(
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
    explicit_manual_identity_guard_submission_command_config_path: str | Path,
    identity_guard_submission_execution_review_config_path: str | Path,
    manual_identity_guard_result_recorder_config_path: str | Path,
    real_identity_guarded_verification_queue_dry_run_bridge_config_path: str | Path,
    real_manual_verification_decision_recorder_config_path: str | Path,
) -> FTAWRealManualVerificationDecisionRecorderPack:
    queue_dry_run = build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files(
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
        identity_guard_submission_review_gate_config_path,
        explicit_manual_identity_guard_submission_command_config_path,
        identity_guard_submission_execution_review_config_path,
        manual_identity_guard_result_recorder_config_path,
        real_identity_guarded_verification_queue_dry_run_bridge_config_path,
    )
    return build_ftaw_real_manual_verification_decision_recorder(
        queue_dry_run,
        _load_manual_decisions(real_manual_verification_decision_recorder_config_path),
    )
