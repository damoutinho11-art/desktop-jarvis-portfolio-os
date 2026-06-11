"""FTAW manual identity guard result recorder.

This read-only recorder captures human-entered identity guard review results
after v4.37 final preflight. It does not run identity guard, create queue
eligibility, verify evidence, approve assets, mutate registries, promote
evidence, recommend allocations, create orders, trade, or create an executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .ftaw_identity_guard_submission_execution_review_pack import (
    FTAWIdentityGuardSubmissionExecutionReviewPack,
    build_ftaw_identity_guard_submission_execution_review_pack_from_files,
)
from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES


ALLOWED_MANUAL_RESULTS = ("pass", "fail", "needs_correction")
MANUAL_PRIVATE_OUTSTANDING_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWManualIdentityGuardResultRecord:
    evidence_type: str
    source_reference_id: str
    manual_identity_guard_result: str
    reviewed_by_user: bool
    user_asserted_manual_identity_review_completed: bool
    user_asserted_no_auto_execution: bool
    user_asserted_no_evidence_verification: bool
    user_asserted_no_queue_eligibility: bool
    reviewer_notes: str
    result_status: str
    manual_result_recorded: bool
    identity_guard_executed_by_system: bool = False
    evidence_verified: bool = False
    queue_eligibility_created: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWManualIdentityGuardResultRecorderPack:
    target_asset: str
    result_recorder_status: str
    upstream_v4_37_status: str
    manual_result_count: int
    pass_count: int
    fail_needs_correction_count: int
    missing_result_count: int
    manual_private_outstanding_count: int
    result_records: tuple[FTAWManualIdentityGuardResultRecord, ...]
    manual_private_outstanding: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    system_identity_guard_execution: bool = False
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


def _load_manual_results(path: str | Path) -> tuple[dict, ...]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = data.get("manual_identity_guard_results", ())
    if entries is None:
        return ()
    if not isinstance(entries, list):
        raise ValueError("manual_identity_guard_results must be a list when present")
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("manual identity guard result entries must be objects")
    return tuple(entries)


def _record_from_entry(entry: dict) -> FTAWManualIdentityGuardResultRecord:
    result = entry.get("manual_identity_guard_result")
    required_assertions = (
        entry.get("reviewed_by_user") is True,
        entry.get("user_asserted_manual_identity_review_completed") is True,
        entry.get("user_asserted_no_auto_execution") is True,
        entry.get("user_asserted_no_evidence_verification") is True,
        entry.get("user_asserted_no_queue_eligibility") is True,
    )
    evidence_type = str(entry.get("evidence_type", ""))
    source_reference_id = str(entry.get("source_reference_id", ""))
    if evidence_type not in PUBLIC_EVIDENCE_TYPES:
        status = "blocked_unsupported_evidence_type"
    elif result not in ALLOWED_MANUAL_RESULTS:
        status = "blocked_invalid_manual_result"
    elif not all(required_assertions):
        status = "blocked_missing_user_assertion"
    elif result == "pass":
        status = "manual_identity_guard_pass_recorded"
    elif result == "fail":
        status = "manual_identity_guard_fail_recorded"
    else:
        status = "manual_identity_guard_needs_correction_recorded"

    return FTAWManualIdentityGuardResultRecord(
        evidence_type=evidence_type,
        source_reference_id=source_reference_id,
        manual_identity_guard_result=str(result),
        reviewed_by_user=entry.get("reviewed_by_user") is True,
        user_asserted_manual_identity_review_completed=entry.get("user_asserted_manual_identity_review_completed") is True,
        user_asserted_no_auto_execution=entry.get("user_asserted_no_auto_execution") is True,
        user_asserted_no_evidence_verification=entry.get("user_asserted_no_evidence_verification") is True,
        user_asserted_no_queue_eligibility=entry.get("user_asserted_no_queue_eligibility") is True,
        reviewer_notes=str(entry.get("reviewer_notes", "")),
        result_status=status,
        manual_result_recorded=status in {
            "manual_identity_guard_pass_recorded",
            "manual_identity_guard_fail_recorded",
            "manual_identity_guard_needs_correction_recorded",
        },
        identity_guard_executed_by_system=False,
        evidence_verified=False,
        queue_eligibility_created=False,
        approved_asset=False,
        registry_mutation=False,
        buy_signal=False,
    )


def build_ftaw_manual_identity_guard_result_recorder(
    execution_review: FTAWIdentityGuardSubmissionExecutionReviewPack,
    manual_result_entries: tuple[dict, ...],
) -> FTAWManualIdentityGuardResultRecorderPack:
    records = tuple(sorted((_record_from_entry(entry) for entry in manual_result_entries), key=lambda item: (item.evidence_type, item.source_reference_id)))
    public_records = tuple(record for record in records if record.evidence_type in PUBLIC_EVIDENCE_TYPES)
    pass_types = {record.evidence_type for record in public_records if record.result_status == "manual_identity_guard_pass_recorded"}
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in pass_types)
    fail_or_needs = tuple(
        record
        for record in public_records
        if record.result_status in {"manual_identity_guard_fail_recorded", "manual_identity_guard_needs_correction_recorded"}
    )

    blocked: list[str] = []
    if execution_review.execution_review_status != "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT":
        blocked.append(f"v4.37 execution review status is {execution_review.execution_review_status}.")
    for record in records:
        if record.result_status.startswith("blocked_"):
            blocked.append(f"{record.evidence_type or 'unknown'} result blocked: {record.result_status}.")
        elif record.result_status == "manual_identity_guard_fail_recorded":
            blocked.append(f"{record.evidence_type} manual identity guard result is fail.")
        elif record.result_status == "manual_identity_guard_needs_correction_recorded":
            blocked.append(f"{record.evidence_type} manual identity guard result needs correction.")
    blocked.extend(f"missing manual identity guard pass result for {evidence_type}" for evidence_type in missing_types)
    blocked.extend(execution_review.blocked_reasons)

    if execution_review.execution_review_status != "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT" and not records:
        status = "BLOCKED_NO_FINAL_MANUAL_IDENTITY_GUARD_PREFLIGHT"
        next_action = "Resolve v4.37 final preflight before recording manual identity guard results."
    elif not records:
        status = "NO_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED"
        next_action = "Record manual identity guard results for all required public evidence types."
    elif blocked:
        status = "PARTIAL_MANUAL_IDENTITY_GUARD_RESULTS_RECORDED"
        next_action = "Resolve missing, failed, or needs-correction manual identity guard results before queue dry-run review."
    else:
        status = "MANUAL_IDENTITY_GUARD_RESULTS_RECORDED_FOR_QUEUE_DRY_RUN_REVIEW"
        next_action = "A future queue dry-run review may inspect these manual results; no queue eligibility was created."

    return FTAWManualIdentityGuardResultRecorderPack(
        target_asset=execution_review.target_asset,
        result_recorder_status=status,
        upstream_v4_37_status=execution_review.execution_review_status,
        manual_result_count=len(public_records),
        pass_count=len(pass_types),
        fail_needs_correction_count=len(fail_or_needs),
        missing_result_count=len(missing_types),
        manual_private_outstanding_count=len(MANUAL_PRIVATE_OUTSTANDING_TYPES),
        result_records=public_records,
        manual_private_outstanding=MANUAL_PRIVATE_OUTSTANDING_TYPES,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        system_identity_guard_execution=False,
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


def build_ftaw_manual_identity_guard_result_recorder_from_files(
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
) -> FTAWManualIdentityGuardResultRecorderPack:
    execution_review = build_ftaw_identity_guard_submission_execution_review_pack_from_files(
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
    )
    return build_ftaw_manual_identity_guard_result_recorder(
        execution_review,
        _load_manual_results(manual_identity_guard_result_recorder_config_path),
    )
