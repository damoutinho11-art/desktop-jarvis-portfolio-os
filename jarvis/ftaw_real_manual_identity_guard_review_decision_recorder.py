"""FTAW real manual identity guard review decision recorder.

This read-only recorder captures human decisions over the v4.32 identity guard
bridge packet. It records intent for future dry-run submission review only. It
does not confirm identity, verify evidence, create identity guard pass records,
create queue eligibility, approve assets, mutate registries, promote evidence,
recommend allocations, create orders, trade, or create an executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_manual_source_fact_entry_pack import (
    FTAWManualSourceFactEntryPack,
    build_ftaw_manual_source_fact_entry_pack_from_files,
)
from .ftaw_real_manual_source_fact_identity_guard_bridge import (
    FTAWRealManualSourceFactIdentityGuardBridgePack,
    build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files,
)


ALLOWED_DECISIONS = ("accept_for_identity_guard_review", "reject_for_identity_guard_review", "needs_correction")
PUBLIC_EVIDENCE_TYPES = ("fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data")
MANUAL_PRIVATE_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWManualIdentityGuardReviewDecisionRecord:
    evidence_type: str
    source_reference_id: str
    reviewer_decision: str
    reviewer_notes: str
    decision_status: str
    reason: str
    reviewed_by_user: bool
    manual_review: bool
    evidence_verified: bool = False
    identity_guard_pass_created: bool = False
    queue_eligibility_created: bool = False
    approved_asset: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRejectedManualIdentityGuardDecisionEntry:
    evidence_type: str
    source_reference_id: str
    reason: str


@dataclass(frozen=True)
class FTAWManualIdentityGuardReviewDecisionRecorderPack:
    target_asset: str
    recorder_status: str
    upstream_bridge_status: str
    decisions_provided_count: int
    accepted_decision_count: int
    rejected_needs_correction_count: int
    missing_decision_count: int
    manual_private_outstanding_count: int
    decision_records: tuple[FTAWManualIdentityGuardReviewDecisionRecord, ...]
    rejected_entries: tuple[FTAWRejectedManualIdentityGuardDecisionEntry, ...]
    manual_private_outstanding: tuple
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
    verified_evidence_promotion: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _load_decision_entries(path: str | Path) -> tuple[dict[str, Any], ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = raw.get("manual_identity_guard_review_decisions", [])
    if not isinstance(entries, list):
        raise ValueError("manual_identity_guard_review_decisions must be a list")
    return tuple(dict(entry) for entry in entries)


def _entry_assertions_ok(entry: dict[str, Any]) -> bool:
    return (
        entry.get("reviewed_by_user") is True
        and entry.get("user_asserted_manual_review") is True
        and entry.get("user_asserted_no_auto_verification") is True
        and entry.get("user_asserted_no_identity_pass_creation") is True
    )


def build_ftaw_real_manual_identity_guard_review_decision_recorder(
    bridge: FTAWRealManualSourceFactIdentityGuardBridgePack,
    fact_pack: FTAWManualSourceFactEntryPack,
    decision_entries: tuple[dict[str, Any], ...],
) -> FTAWManualIdentityGuardReviewDecisionRecorderPack:
    eligible_records = {
        record.source_reference_id: record
        for record in fact_pack.accepted_source_fact_records
        if record.evidence_type in PUBLIC_EVIDENCE_TYPES
    }
    decisions_by_id: dict[str, FTAWManualIdentityGuardReviewDecisionRecord] = {}
    rejected_entries: list[FTAWRejectedManualIdentityGuardDecisionEntry] = []

    for entry in decision_entries:
        source_reference_id = str(entry.get("source_reference_id", "")).strip()
        evidence_type = str(entry.get("evidence_type", "")).strip()
        reviewer_decision = str(entry.get("reviewer_decision", "")).strip()
        reviewer_notes = str(entry.get("reviewer_notes", "")).strip()
        eligible = eligible_records.get(source_reference_id)
        if evidence_type in MANUAL_PRIVATE_EVIDENCE_TYPES:
            rejected_entries.append(
                FTAWRejectedManualIdentityGuardDecisionEntry(
                    evidence_type=evidence_type,
                    source_reference_id=source_reference_id,
                    reason="manual/private evidence type is not decision-recorded here",
                )
            )
            continue
        if eligible is None:
            rejected_entries.append(
                FTAWRejectedManualIdentityGuardDecisionEntry(
                    evidence_type=evidence_type,
                    source_reference_id=source_reference_id,
                    reason="unknown or ineligible identity guard review source reference",
                )
            )
            continue
        if eligible.evidence_type != evidence_type:
            rejected_entries.append(
                FTAWRejectedManualIdentityGuardDecisionEntry(
                    evidence_type=evidence_type,
                    source_reference_id=source_reference_id,
                    reason="evidence_type does not match eligible source fact record",
                )
            )
            continue
        if reviewer_decision not in ALLOWED_DECISIONS:
            rejected_entries.append(
                FTAWRejectedManualIdentityGuardDecisionEntry(
                    evidence_type=evidence_type,
                    source_reference_id=source_reference_id,
                    reason="invalid reviewer_decision",
                )
            )
            continue
        if not _entry_assertions_ok(entry):
            rejected_entries.append(
                FTAWRejectedManualIdentityGuardDecisionEntry(
                    evidence_type=evidence_type,
                    source_reference_id=source_reference_id,
                    reason="manual review assertions are incomplete",
                )
            )
            continue
        if reviewer_decision == "accept_for_identity_guard_review":
            decision_status = "accepted_for_future_identity_guard_submission_review"
            reason = "accepted for future identity guard submission review; not identity confirmation"
        elif reviewer_decision == "reject_for_identity_guard_review":
            decision_status = "rejected_for_identity_guard_review"
            reason = "human reviewer rejected this item for identity guard review"
        else:
            decision_status = "needs_correction"
            reason = "human reviewer marked this item as needing correction"
        decisions_by_id[source_reference_id] = FTAWManualIdentityGuardReviewDecisionRecord(
            evidence_type=evidence_type,
            source_reference_id=source_reference_id,
            reviewer_decision=reviewer_decision,
            reviewer_notes=reviewer_notes,
            decision_status=decision_status,
            reason=reason,
            reviewed_by_user=True,
            manual_review=True,
            evidence_verified=False,
            identity_guard_pass_created=False,
            queue_eligibility_created=False,
            approved_asset=False,
            buy_signal=False,
        )

    decision_records = tuple(sorted(decisions_by_id.values(), key=lambda item: (item.evidence_type, item.source_reference_id)))
    eligible_ids = set(eligible_records)
    missing_ids = sorted(eligible_ids - set(decisions_by_id))
    rejected_or_correction = tuple(
        record for record in decision_records if record.reviewer_decision in {"reject_for_identity_guard_review", "needs_correction"}
    )
    blocked = list(bridge.blocked_reasons)
    blocked.extend(f"missing manual identity guard decision for {eligible_records[source_id].evidence_type}" for source_id in missing_ids)
    blocked.extend(record.reason for record in rejected_or_correction)

    if bridge.bridge_status != "READY_FOR_MANUAL_IDENTITY_GUARD_REVIEW" or not bridge.identity_review_packet_preview.review_packet_created:
        status = "BLOCKED_NO_IDENTITY_GUARD_REVIEW_PACKET"
        next_action = "Resolve identity guard bridge blockers before recording review decisions."
    elif not decision_records:
        status = "NO_MANUAL_IDENTITY_GUARD_DECISIONS"
        next_action = "Record human decisions for every public identity guard review item."
    elif missing_ids or rejected_or_correction:
        status = "PARTIAL_MANUAL_IDENTITY_GUARD_DECISIONS_RECORDED"
        next_action = "Resolve missing, rejected, or correction-needed decisions before dry-run submission review."
    else:
        status = "MANUAL_IDENTITY_GUARD_DECISIONS_RECORDED_FOR_DRY_RUN_SUBMISSION_REVIEW"
        next_action = "Prepare a future dry-run identity guard submission review; do not create pass records."

    return FTAWManualIdentityGuardReviewDecisionRecorderPack(
        target_asset=bridge.target_asset,
        recorder_status=status,
        upstream_bridge_status=bridge.bridge_status,
        decisions_provided_count=len(decision_entries),
        accepted_decision_count=sum(1 for record in decision_records if record.reviewer_decision == "accept_for_identity_guard_review"),
        rejected_needs_correction_count=len(rejected_or_correction),
        missing_decision_count=len(missing_ids),
        manual_private_outstanding_count=bridge.manual_private_outstanding_count,
        decision_records=decision_records,
        rejected_entries=tuple(rejected_entries),
        manual_private_outstanding=bridge.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
        verified_evidence_promotion=False,
        approved_asset=False,
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


def build_ftaw_real_manual_identity_guard_review_decision_recorder_from_files(
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
) -> FTAWManualIdentityGuardReviewDecisionRecorderPack:
    entries = _load_decision_entries(identity_guard_review_decision_config_path)
    bridge = build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files(
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
    )
    fact_pack = build_ftaw_manual_source_fact_entry_pack_from_files(
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
    )
    return build_ftaw_real_manual_identity_guard_review_decision_recorder(bridge, fact_pack, entries)
