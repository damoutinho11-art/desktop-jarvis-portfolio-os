"""FTAW manual public source reference entry recorder.

This read-only recorder normalizes manually entered public source references
for later source-fact entry. It does not fetch URLs, download files, scrape
content, ingest private files, verify evidence, claim facts, approve assets,
mutate registries, promote evidence, recommend allocations, create orders,
trade, or create an executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_real_public_source_reference_intake_plan import (
    FTAWRealPublicSourceReferenceIntakePlan,
    FTAWRealPublicSourceReferenceSlot,
    build_ftaw_real_public_source_reference_intake_plan_from_files,
)


PUBLIC_REFERENCE_EVIDENCE_TYPES = ("fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data")
MANUAL_PRIVATE_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWManualPublicSourceReferenceRecord:
    evidence_type: str
    source_reference_id: str
    source_category: str
    manual_reference: str
    manual_entry: bool = True
    reference_recorded: bool = True
    fetched: bool = False
    downloaded: bool = False
    parsed: bool = False
    facts_extracted: bool = False
    collected: bool = False
    verified: bool = False
    verified_by_user_default: bool = False
    approval_impact: str = "none"
    buy_signal: bool = False
    manual_action: str = "Use this reference later for manual source-fact entry; do not fetch or verify automatically."


@dataclass(frozen=True)
class FTAWRejectedManualPublicSourceReferenceEntry:
    source_reference_id: str
    evidence_type: str
    reason: str


@dataclass(frozen=True)
class FTAWManualPrivateOutstandingRequirement:
    evidence_type: str
    reason: str
    next_manual_action: str


@dataclass(frozen=True)
class FTAWManualPublicSourceReferenceEntryRecorderPack:
    target_asset: str
    recorder_status: str
    upstream_public_source_reference_plan_status: str
    manual_public_reference_entries_provided_count: int
    public_references_recorded_count: int
    required_public_reference_count: int
    missing_public_reference_count: int
    manual_private_outstanding_count: int
    skipped_rejected_entry_count: int
    recorded_references: tuple[FTAWManualPublicSourceReferenceRecord, ...]
    manual_private_outstanding: tuple[FTAWManualPrivateOutstandingRequirement, ...]
    blocked_reasons: tuple[str, ...]
    rejected_reasons: tuple[str, ...]
    next_manual_action: str
    source_fact_intake_records_created: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    verified_evidence_promotion: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False


def _load_entries(path: str | Path) -> tuple[dict[str, Any], ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = raw.get("manual_public_source_references", [])
    if not isinstance(entries, list):
        raise ValueError("manual_public_source_references must be a list")
    return tuple(dict(entry) for entry in entries)


def _is_public_slot(slot: FTAWRealPublicSourceReferenceSlot) -> bool:
    return slot.evidence_type in PUBLIC_REFERENCE_EVIDENCE_TYPES and slot.expected_public_or_private in {"public_official", "public_market"}


def _entry_is_asserted_reference_only(entry: dict[str, Any]) -> bool:
    return (
        entry.get("entered_by_user") is True
        and entry.get("user_asserted_public_reference") is True
        and entry.get("user_asserted_no_private_file") is True
        and entry.get("user_asserted_no_download_required") is True
        and entry.get("user_asserted_reference_only") is True
    )


def _manual_outstanding_from_slots(slots: tuple[FTAWRealPublicSourceReferenceSlot, ...]) -> tuple[FTAWManualPrivateOutstandingRequirement, ...]:
    requirements: list[FTAWManualPrivateOutstandingRequirement] = []
    for slot in slots:
        if slot.evidence_type == "platform_availability":
            requirements.append(
                FTAWManualPrivateOutstandingRequirement(
                    evidence_type=slot.evidence_type,
                    reason="platform availability is private/account-specific and not a public source reference",
                    next_manual_action="Confirm availability manually inside the account; do not commit private evidence.",
                )
            )
        elif slot.evidence_type == "tax_route":
            requirements.append(
                FTAWManualPrivateOutstandingRequirement(
                    evidence_type=slot.evidence_type,
                    reason="tax route remains manual user confirmation and not public-fetchable",
                    next_manual_action="Record a manual tax-route summary later; do not auto-verify.",
                )
            )
    return tuple(requirements)


def build_ftaw_manual_public_source_reference_entry_recorder(
    plan: FTAWRealPublicSourceReferenceIntakePlan,
    manual_entries: tuple[dict[str, Any], ...],
) -> FTAWManualPublicSourceReferenceEntryRecorderPack:
    slots_by_id = {slot.source_reference_id: slot for slot in plan.source_reference_slots}
    public_slots = tuple(slot for slot in plan.source_reference_slots if _is_public_slot(slot))
    public_slot_ids = {slot.source_reference_id for slot in public_slots}
    records_by_id: dict[str, FTAWManualPublicSourceReferenceRecord] = {}
    rejected: list[FTAWRejectedManualPublicSourceReferenceEntry] = []

    for entry in manual_entries:
        source_reference_id = str(entry.get("source_reference_id", "")).strip()
        evidence_type = str(entry.get("evidence_type", "")).strip()
        manual_reference = str(entry.get("manual_reference", "")).strip()
        slot = slots_by_id.get(source_reference_id)
        if slot is None:
            rejected.append(
                FTAWRejectedManualPublicSourceReferenceEntry(
                    source_reference_id=source_reference_id,
                    evidence_type=evidence_type,
                    reason="unknown source reference slot",
                )
            )
            continue
        if slot.evidence_type != evidence_type:
            rejected.append(
                FTAWRejectedManualPublicSourceReferenceEntry(
                    source_reference_id=source_reference_id,
                    evidence_type=evidence_type,
                    reason="evidence_type does not match source reference slot",
                )
            )
            continue
        if evidence_type in MANUAL_PRIVATE_EVIDENCE_TYPES or source_reference_id not in public_slot_ids:
            rejected.append(
                FTAWRejectedManualPublicSourceReferenceEntry(
                    source_reference_id=source_reference_id,
                    evidence_type=evidence_type,
                    reason="manual-only/private evidence type cannot be recorded as a public source reference",
                )
            )
            continue
        if not manual_reference:
            rejected.append(
                FTAWRejectedManualPublicSourceReferenceEntry(
                    source_reference_id=source_reference_id,
                    evidence_type=evidence_type,
                    reason="manual_reference is required",
                )
            )
            continue
        if not _entry_is_asserted_reference_only(entry):
            rejected.append(
                FTAWRejectedManualPublicSourceReferenceEntry(
                    source_reference_id=source_reference_id,
                    evidence_type=evidence_type,
                    reason="manual public reference assertions are incomplete",
                )
            )
            continue
        records_by_id[source_reference_id] = FTAWManualPublicSourceReferenceRecord(
            evidence_type=evidence_type,
            source_reference_id=source_reference_id,
            source_category=slot.source_category,
            manual_reference=manual_reference,
            manual_entry=True,
            reference_recorded=True,
            fetched=False,
            downloaded=False,
            parsed=False,
            facts_extracted=False,
            collected=False,
            verified=False,
            verified_by_user_default=False,
            approval_impact="none",
            buy_signal=False,
        )

    recorded = tuple(sorted(records_by_id.values(), key=lambda record: (record.evidence_type, record.source_reference_id)))
    missing_public_ids = sorted(public_slot_ids - set(records_by_id))
    blocked = list(plan.blocked_reasons)
    blocked.extend(f"missing public source reference for {slots_by_id[source_id].evidence_type}" for source_id in missing_public_ids)

    if plan.public_source_reference_plan_status == "BLOCKED_NOT_READY_FOR_PUBLIC_SOURCE_REFERENCES":
        status = "BLOCKED_NO_PUBLIC_SOURCE_REFERENCE_PLAN"
        next_action = "Resolve upstream public source reference plan blockers before recording manual references."
    elif not recorded:
        status = "NO_PUBLIC_SOURCE_REFERENCES_RECORDED"
        next_action = "Manually enter public source references for public evidence types."
    elif missing_public_ids or plan.public_source_reference_plan_status != "PUBLIC_SOURCE_REFERENCE_PLAN_READY":
        status = "PARTIAL_PUBLIC_SOURCE_REFERENCES_RECORDED"
        next_action = "Enter the remaining public source references before manual source-fact entry."
    else:
        status = "PUBLIC_SOURCE_REFERENCES_RECORDED_FOR_MANUAL_FACT_ENTRY"
        next_action = "Proceed later to manual source-fact entry; do not fetch, parse, or verify automatically."

    rejected_reasons = tuple(
        f"{item.source_reference_id or 'unknown'}:{item.evidence_type or 'unknown'}: {item.reason}" for item in rejected
    )
    return FTAWManualPublicSourceReferenceEntryRecorderPack(
        target_asset=plan.target_asset,
        recorder_status=status,
        upstream_public_source_reference_plan_status=plan.public_source_reference_plan_status,
        manual_public_reference_entries_provided_count=len(manual_entries),
        public_references_recorded_count=len(recorded),
        required_public_reference_count=len(public_slots),
        missing_public_reference_count=len(missing_public_ids),
        manual_private_outstanding_count=len(_manual_outstanding_from_slots(plan.source_reference_slots)),
        skipped_rejected_entry_count=len(rejected),
        recorded_references=recorded,
        manual_private_outstanding=_manual_outstanding_from_slots(plan.source_reference_slots),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        rejected_reasons=rejected_reasons,
        next_manual_action=next_action,
        source_fact_intake_records_created=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
        approved_asset=False,
        registry_mutation=False,
        verified_evidence_promotion=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
    )


def build_ftaw_manual_public_source_reference_entry_recorder_from_files(
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
) -> FTAWManualPublicSourceReferenceEntryRecorderPack:
    entries = _load_entries(manual_public_source_reference_entry_config_path)
    plan = build_ftaw_real_public_source_reference_intake_plan_from_files(
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
    )
    return build_ftaw_manual_public_source_reference_entry_recorder(plan, entries)
