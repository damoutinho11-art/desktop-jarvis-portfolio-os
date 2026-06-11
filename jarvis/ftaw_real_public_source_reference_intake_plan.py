"""FTAW real public source reference intake plan.

This read-only plan creates structured slots for manually entering real source
references later. It does not fetch webpages, download PDFs, ingest private
files, verify evidence, approve assets, mutate registries, promote evidence,
recommend allocations, create orders, trade, or create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_evidence_collection_checklist_pack import (
    FTAWRealEvidenceCollectionChecklistPack,
    build_ftaw_real_evidence_collection_checklist_pack_from_files,
)


@dataclass(frozen=True)
class FTAWRealPublicSourceReferenceSlot:
    evidence_type: str
    source_reference_id: str
    source_category: str
    expected_public_or_private: str
    expected_commit_safety: str
    expected_source_identity_fields: tuple[str, ...]
    expected_source_fact_fields: tuple[str, ...]
    manual_url_required: bool
    private_file_allowed: bool = False
    auto_fetch_allowed: bool = False
    auto_download_allowed: bool = False
    auto_verify_allowed: bool = False
    verified_by_user_default: bool = False
    collected: bool = False
    verified: bool = False
    approval_impact: str = "none"
    buy_signal: bool = False
    manual_action: str = ""


@dataclass(frozen=True)
class FTAWRealPublicSourceReferenceIntakePlan:
    target_asset: str
    public_source_reference_plan_status: str
    upstream_checklist_status: str
    source_reference_slot_count: int
    public_official_slot_count: int
    public_market_slot_count: int
    private_manual_slot_count: int
    manual_confirmation_slot_count: int
    auto_fetch_allowed_count: int
    auto_download_allowed_count: int
    auto_verify_allowed_count: int
    source_reference_slots: tuple[FTAWRealPublicSourceReferenceSlot, ...]
    blocked_reasons: tuple[str, ...]
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


def _slot_from_checklist_item(item) -> FTAWRealPublicSourceReferenceSlot:
    if item.evidence_type == "platform_availability":
        expected_public_or_private = "private_manual_reference_required"
        manual_url_required = False
        manual_action = "Enter a manual account-specific availability summary later; do not enter or commit private screenshots/files."
    elif item.evidence_type == "tax_route":
        expected_public_or_private = "manual_user_confirmation"
        manual_url_required = False
        manual_action = "Enter a manual tax-route confirmation summary later; do not auto-fetch or auto-verify."
    else:
        expected_public_or_private = item.public_or_private
        manual_url_required = True
        manual_action = "Enter the public URL/text reference manually later; do not fetch or download it automatically."

    return FTAWRealPublicSourceReferenceSlot(
        evidence_type=item.evidence_type,
        source_reference_id=f"ftaw_{item.evidence_type}_reference_slot",
        source_category=item.source_category,
        expected_public_or_private=expected_public_or_private,
        expected_commit_safety=item.commit_safety,
        expected_source_identity_fields=item.source_identity_requirements,
        expected_source_fact_fields=item.required_source_fact_fields,
        manual_url_required=manual_url_required,
        private_file_allowed=False,
        auto_fetch_allowed=False,
        auto_download_allowed=False,
        auto_verify_allowed=False,
        verified_by_user_default=False,
        collected=False,
        verified=False,
        approval_impact="none",
        buy_signal=False,
        manual_action=manual_action,
    )


def build_ftaw_real_public_source_reference_intake_plan(
    checklist: FTAWRealEvidenceCollectionChecklistPack,
) -> FTAWRealPublicSourceReferenceIntakePlan:
    slots = tuple(_slot_from_checklist_item(item) for item in checklist.checklist_items)
    blocked = list(checklist.blocked_reasons)
    if checklist.checklist_status == "REAL_EVIDENCE_COLLECTION_PLAN_READY":
        status = "PUBLIC_SOURCE_REFERENCE_PLAN_READY"
        next_action = "Manually enter public source references later; do not fetch or download sources automatically."
    elif checklist.checklist_status == "PARTIAL_COLLECTION_PLAN_READY":
        status = "PARTIAL_PUBLIC_SOURCE_REFERENCE_PLAN_READY"
        if not blocked:
            blocked.append("upstream collection checklist is partial.")
        next_action = "Resolve partial checklist blockers before treating public source reference planning as complete."
    else:
        status = "BLOCKED_NOT_READY_FOR_PUBLIC_SOURCE_REFERENCES"
        if not blocked:
            blocked.append(f"upstream checklist status is {checklist.checklist_status}.")
        next_action = "Resolve upstream checklist blockers before creating public source reference intake."

    return FTAWRealPublicSourceReferenceIntakePlan(
        target_asset=checklist.target_asset,
        public_source_reference_plan_status=status,
        upstream_checklist_status=checklist.checklist_status,
        source_reference_slot_count=len(slots),
        public_official_slot_count=sum(1 for slot in slots if slot.expected_public_or_private == "public_official"),
        public_market_slot_count=sum(1 for slot in slots if slot.expected_public_or_private == "public_market"),
        private_manual_slot_count=sum(1 for slot in slots if slot.expected_public_or_private == "private_manual_reference_required"),
        manual_confirmation_slot_count=sum(1 for slot in slots if slot.expected_public_or_private == "manual_user_confirmation"),
        auto_fetch_allowed_count=sum(1 for slot in slots if slot.auto_fetch_allowed),
        auto_download_allowed_count=sum(1 for slot in slots if slot.auto_download_allowed),
        auto_verify_allowed_count=sum(1 for slot in slots if slot.auto_verify_allowed),
        source_reference_slots=slots,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
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


def build_ftaw_real_public_source_reference_intake_plan_from_files(
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
) -> FTAWRealPublicSourceReferenceIntakePlan:
    Path(public_source_reference_plan_config_path).read_text(encoding="utf-8")
    checklist = build_ftaw_real_evidence_collection_checklist_pack_from_files(
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
    )
    return build_ftaw_real_public_source_reference_intake_plan(checklist)
