"""FTAW manual source fact entry pack.

This read-only pack accepts user-entered source facts tied to recorded public
source references. It does not fetch, download, scrape, inspect web content,
auto-extract facts, ingest private files, verify evidence, create identity
guard pass records, create queue eligibility, approve assets, mutate
registries, promote evidence, recommend allocations, create orders, trade, or
create an executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_manual_public_source_reference_entry_recorder import (
    FTAWManualPrivateOutstandingRequirement,
    FTAWManualPublicSourceReferenceEntryRecorderPack,
    build_ftaw_manual_public_source_reference_entry_recorder_from_files,
)


REQUIRED_FACT_FIELDS_BY_EVIDENCE_TYPE = {
    "fund_metadata": ("provider", "fund_name", "isin", "ticker_or_symbol"),
    "fee_metadata": ("fee_metric_name", "fee_metric_value", "fee_as_of"),
    "distribution_policy": ("distribution_policy", "policy_as_of"),
    "market_data": ("market_ticker", "quote_currency", "quote_source_label", "quote_as_of"),
    "exposure_data": ("exposure_source_label", "exposure_as_of", "exposure_summary_reference"),
}
PUBLIC_FACT_EVIDENCE_TYPES = tuple(REQUIRED_FACT_FIELDS_BY_EVIDENCE_TYPE)
MANUAL_PRIVATE_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWManualSourceFactRecord:
    evidence_type: str
    source_reference_id: str
    facts: dict[str, Any]
    required_fields_present: tuple[str, ...]
    required_fields_missing: tuple[str, ...]
    extra_fields: tuple[str, ...]
    manual_entry: bool = True
    facts_entered: bool = True
    auto_extracted: bool = False
    fetched: bool = False
    downloaded: bool = False
    parsed: bool = False
    verified: bool = False
    identity_guard_pass_created: bool = False
    queue_eligibility_created: bool = False
    approval_impact: str = "none"
    buy_signal: bool = False
    manual_action: str = "Use these manually entered facts later for identity review; do not verify automatically."


@dataclass(frozen=True)
class FTAWRejectedManualSourceFactEntry:
    evidence_type: str
    source_reference_id: str
    reason: str


@dataclass(frozen=True)
class FTAWManualSourceFactEntryPack:
    target_asset: str
    source_fact_entry_status: str
    upstream_manual_public_source_reference_recorder_status: str
    public_references_recorded_count: int
    manual_source_fact_entries_provided_count: int
    accepted_source_fact_record_count: int
    required_public_fact_record_count: int
    missing_public_fact_record_count: int
    missing_required_field_count: int
    rejected_entry_count: int
    manual_private_outstanding_count: int
    accepted_source_fact_records: tuple[FTAWManualSourceFactRecord, ...]
    rejected_entries: tuple[FTAWRejectedManualSourceFactEntry, ...]
    manual_private_outstanding: tuple[FTAWManualPrivateOutstandingRequirement, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    automatic_fact_extraction: bool = False
    evidence_verified: bool = False
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


def _load_fact_entries(path: str | Path) -> tuple[dict[str, Any], ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = raw.get("manual_source_fact_entries", [])
    if not isinstance(entries, list):
        raise ValueError("manual_source_fact_entries must be a list")
    return tuple(dict(entry) for entry in entries)


def _entry_has_manual_assertions(entry: dict[str, Any]) -> bool:
    return (
        entry.get("entered_by_user") is True
        and entry.get("user_asserted_reference_reviewed_manually") is True
        and entry.get("user_asserted_no_auto_extraction") is True
        and entry.get("user_asserted_no_private_file") is True
    )


def _is_non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def build_ftaw_manual_source_fact_entry_pack(
    recorder: FTAWManualPublicSourceReferenceEntryRecorderPack,
    manual_fact_entries: tuple[dict[str, Any], ...],
) -> FTAWManualSourceFactEntryPack:
    recorded_by_id = {record.source_reference_id: record for record in recorder.recorded_references}
    accepted_by_id: dict[str, FTAWManualSourceFactRecord] = {}
    rejected: list[FTAWRejectedManualSourceFactEntry] = []

    for entry in manual_fact_entries:
        source_reference_id = str(entry.get("source_reference_id", "")).strip()
        evidence_type = str(entry.get("evidence_type", "")).strip()
        facts = entry.get("facts", {})
        if not isinstance(facts, dict):
            facts = {}
        recorded_reference = recorded_by_id.get(source_reference_id)
        if recorded_reference is None:
            rejected.append(FTAWRejectedManualSourceFactEntry(evidence_type, source_reference_id, "unknown or unrecorded public source reference"))
            continue
        if recorded_reference.evidence_type != evidence_type:
            rejected.append(FTAWRejectedManualSourceFactEntry(evidence_type, source_reference_id, "evidence_type does not match recorded public reference"))
            continue
        if evidence_type in MANUAL_PRIVATE_EVIDENCE_TYPES or evidence_type not in PUBLIC_FACT_EVIDENCE_TYPES:
            rejected.append(FTAWRejectedManualSourceFactEntry(evidence_type, source_reference_id, "manual/private evidence type cannot receive public source facts here"))
            continue
        if not _entry_has_manual_assertions(entry):
            rejected.append(FTAWRejectedManualSourceFactEntry(evidence_type, source_reference_id, "manual source fact assertions are incomplete"))
            continue
        required_fields = REQUIRED_FACT_FIELDS_BY_EVIDENCE_TYPE[evidence_type]
        present = tuple(field for field in required_fields if _is_non_empty(facts.get(field)))
        missing = tuple(field for field in required_fields if field not in present)
        extra = tuple(sorted(field for field in facts if field not in required_fields))
        accepted_by_id[source_reference_id] = FTAWManualSourceFactRecord(
            evidence_type=evidence_type,
            source_reference_id=source_reference_id,
            facts=dict(facts),
            required_fields_present=present,
            required_fields_missing=missing,
            extra_fields=extra,
            manual_entry=True,
            facts_entered=True,
            auto_extracted=False,
            fetched=False,
            downloaded=False,
            parsed=False,
            verified=False,
            identity_guard_pass_created=False,
            queue_eligibility_created=False,
            approval_impact="none",
            buy_signal=False,
        )

    accepted = tuple(sorted(accepted_by_id.values(), key=lambda record: (record.evidence_type, record.source_reference_id)))
    required_public_ids = {record.source_reference_id for record in recorder.recorded_references}
    missing_public_ids = sorted(required_public_ids - set(accepted_by_id))
    missing_field_count = sum(len(record.required_fields_missing) for record in accepted)
    blocked = list(recorder.blocked_reasons)
    blocked.extend(f"missing manual source facts for {recorded_by_id[source_id].evidence_type}" for source_id in missing_public_ids)
    for record in accepted:
        for field in record.required_fields_missing:
            blocked.append(f"missing required field {field} for {record.evidence_type}")

    if recorder.recorder_status == "BLOCKED_NO_PUBLIC_SOURCE_REFERENCE_PLAN" or recorder.public_references_recorded_count == 0:
        status = "BLOCKED_NO_PUBLIC_SOURCE_REFERENCES"
        next_action = "Record manual public source references before entering source facts."
    elif not accepted:
        status = "NO_SOURCE_FACTS_ENTERED"
        next_action = "Manually enter source facts for recorded public references."
    elif missing_public_ids or missing_field_count or recorder.recorder_status != "PUBLIC_SOURCE_REFERENCES_RECORDED_FOR_MANUAL_FACT_ENTRY":
        status = "PARTIAL_SOURCE_FACTS_ENTERED"
        next_action = "Complete missing source fact records and required fields before identity review."
    else:
        status = "MANUAL_SOURCE_FACTS_ENTERED_FOR_IDENTITY_REVIEW"
        next_action = "Proceed later to source identity review; do not verify or create queue eligibility automatically."

    return FTAWManualSourceFactEntryPack(
        target_asset=recorder.target_asset,
        source_fact_entry_status=status,
        upstream_manual_public_source_reference_recorder_status=recorder.recorder_status,
        public_references_recorded_count=recorder.public_references_recorded_count,
        manual_source_fact_entries_provided_count=len(manual_fact_entries),
        accepted_source_fact_record_count=len(accepted),
        required_public_fact_record_count=len(recorder.recorded_references),
        missing_public_fact_record_count=len(missing_public_ids),
        missing_required_field_count=missing_field_count,
        rejected_entry_count=len(rejected),
        manual_private_outstanding_count=recorder.manual_private_outstanding_count,
        accepted_source_fact_records=accepted,
        rejected_entries=tuple(rejected),
        manual_private_outstanding=recorder.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        automatic_fact_extraction=False,
        evidence_verified=False,
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


def build_ftaw_manual_source_fact_entry_pack_from_files(
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
) -> FTAWManualSourceFactEntryPack:
    entries = _load_fact_entries(manual_source_fact_entry_config_path)
    recorder = build_ftaw_manual_public_source_reference_entry_recorder_from_files(
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
    )
    return build_ftaw_manual_source_fact_entry_pack(recorder, entries)
