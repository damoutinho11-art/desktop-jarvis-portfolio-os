"""Real evidence collection checklist for candidate status-review readiness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .verified_evidence_intake import (
    REFERENCE_DATE,
    STALE_DAYS,
    VerifiedEvidenceIntakeRecord,
    build_verified_evidence_pack,
    load_verified_evidence_intake,
)


ETF_CHECKLIST = (
    "provider_factsheet",
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "platform_availability",
    "tax_route",
    "exposure_data",
    "market_data",
)
CRYPTO_CHECKLIST = (
    "protocol_metadata",
    "market_data",
    "platform_availability",
    "custody_route",
    "tax_route",
    "crypto_risk_notes",
)
SOURCE_OPTIONS = {
    "provider_factsheet": ("provider_factsheet",),
    "fund_metadata": ("provider_factsheet", "manual_research", "verified_api_snapshot"),
    "fee_metadata": ("provider_factsheet", "manual_research", "broker_export", "verified_api_snapshot"),
    "distribution_policy": ("provider_factsheet", "manual_research", "verified_api_snapshot"),
    "platform_availability": ("platform_screenshot", "broker_export", "verified_api_snapshot"),
    "tax_route": ("manual_research", "broker_export", "verified_api_snapshot"),
    "exposure_data": ("provider_factsheet", "broker_export", "verified_api_snapshot"),
    "market_data": ("broker_export", "verified_api_snapshot"),
    "protocol_metadata": ("manual_research", "provider_factsheet", "verified_api_snapshot"),
    "custody_route": ("platform_screenshot", "broker_export", "verified_api_snapshot"),
    "crypto_risk_notes": ("manual_research", "provider_factsheet", "verified_api_snapshot"),
}


@dataclass(frozen=True)
class EvidenceChecklistItem:
    evidence_type: str
    required_source_quality_options: tuple[str, ...]
    current_status: str
    blocking_for_real_review: bool
    notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_type": self.evidence_type,
            "required_source_quality_options": list(self.required_source_quality_options),
            "current_status": self.current_status,
            "blocking_for_real_review": self.blocking_for_real_review,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CandidateEvidenceChecklist:
    asset_id: str
    asset_type: str
    sleeve: str
    approval_status: str
    items: tuple[EvidenceChecklistItem, ...]
    collection_complete: bool
    manual_approval_required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "approval_status": self.approval_status,
            "items": [item.to_dict() for item in self.items],
            "collection_complete": self.collection_complete,
            "manual_approval_required": self.manual_approval_required,
        }


@dataclass(frozen=True)
class EvidenceCollectionSummary:
    total_candidates: int
    complete_checklists: int
    incomplete_checklists: int
    stale_evidence_count: int
    missing_evidence_count: int
    by_asset_type: dict[str, int]
    by_sleeve: dict[str, int]


@dataclass(frozen=True)
class EvidenceCollectionChecklistResult:
    checklist_status: str
    checklists: tuple[CandidateEvidenceChecklist, ...]
    summary: EvidenceCollectionSummary
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _checklist_for_asset(asset: CandidateAsset) -> tuple[str, ...]:
    if asset.asset_type == "ETF":
        return ETF_CHECKLIST
    if asset.asset_type == "crypto":
        return CRYPTO_CHECKLIST
    return ("fund_metadata", "platform_availability")


def _record_matches(record: VerifiedEvidenceIntakeRecord, evidence_type: str) -> bool:
    if evidence_type == "provider_factsheet":
        return record.source_quality == "provider_factsheet"
    if evidence_type == "crypto_risk_notes":
        return record.evidence_type == "protocol_metadata" and bool(record.extracted_facts)
    return record.evidence_type == evidence_type


def _record_is_stale(record: VerifiedEvidenceIntakeRecord, reference_date: date) -> bool:
    return (reference_date - _parse_date(record.as_of)).days > STALE_DAYS


def _status_for_item(
    asset_id: str,
    evidence_type: str,
    records: tuple[VerifiedEvidenceIntakeRecord, ...],
    reference_date: date,
) -> EvidenceChecklistItem:
    matching = tuple(record for record in records if record.asset_id == asset_id and _record_matches(record, evidence_type))
    options = SOURCE_OPTIONS[evidence_type]
    status = "missing"
    notes = "No matching evidence collected."
    if matching:
        verified_real = tuple(
            record
            for record in matching
            if record.verified_by_user
            and record.source_quality != "synthetic_fixture"
            and record.source_quality in options
            and not _record_is_stale(record, reference_date)
        )
        stale = tuple(
            record
            for record in matching
            if record.verified_by_user
            and record.source_quality != "synthetic_fixture"
            and record.source_quality in options
            and _record_is_stale(record, reference_date)
        )
        if verified_real:
            status = "present_verified"
            notes = f"Verified evidence present: {verified_real[0].evidence_id}."
        elif stale:
            status = "stale"
            notes = f"Evidence is older than {STALE_DAYS} days: {stale[0].evidence_id}."
        else:
            status = "present_unverified"
            notes = "Evidence exists but is unverified, synthetic, or from the wrong source quality."
    return EvidenceChecklistItem(
        evidence_type=evidence_type,
        required_source_quality_options=options,
        current_status=status,
        blocking_for_real_review=status != "present_verified",
        notes=notes,
    )


def build_evidence_collection_checklist(
    candidate_registry: str | Path | AssetRegistry,
    intake_records: list[dict[str, object]],
    reference_date: date = REFERENCE_DATE,
) -> EvidenceCollectionChecklistResult:
    registry = load_asset_registry(candidate_registry) if not isinstance(candidate_registry, AssetRegistry) else candidate_registry
    pack = build_verified_evidence_pack(registry, intake_records)
    records = tuple(result.record for result in pack.validation_results if result.record is not None)
    checklists: list[CandidateEvidenceChecklist] = []
    for asset in registry.assets:
        items = tuple(
            _status_for_item(asset.asset_id, evidence_type, records, reference_date)
            for evidence_type in _checklist_for_asset(asset)
        )
        checklists.append(
            CandidateEvidenceChecklist(
                asset_id=asset.asset_id,
                asset_type=asset.asset_type,
                sleeve=asset.sleeve,
                approval_status=asset.approval_status,
                items=items,
                collection_complete=not any(item.blocking_for_real_review for item in items),
                manual_approval_required=True,
            )
        )
    by_type: dict[str, int] = {}
    by_sleeve: dict[str, int] = {}
    for checklist in checklists:
        by_type[checklist.asset_type] = by_type.get(checklist.asset_type, 0) + 1
        by_sleeve[checklist.sleeve] = by_sleeve.get(checklist.sleeve, 0) + 1
    summary = EvidenceCollectionSummary(
        total_candidates=len(checklists),
        complete_checklists=sum(checklist.collection_complete for checklist in checklists),
        incomplete_checklists=sum(not checklist.collection_complete for checklist in checklists),
        stale_evidence_count=sum(item.current_status == "stale" for checklist in checklists for item in checklist.items),
        missing_evidence_count=sum(item.current_status == "missing" for checklist in checklists for item in checklist.items),
        by_asset_type=dict(sorted(by_type.items())),
        by_sleeve=dict(sorted(by_sleeve.items())),
    )
    return EvidenceCollectionChecklistResult(
        checklist_status="COLLECTION_COMPLETE" if summary.complete_checklists else "COLLECTION_INCOMPLETE",
        checklists=tuple(checklists),
        summary=summary,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_evidence_collection_checklist_from_files(
    registry_path: str | Path,
    intake_path: str | Path,
) -> EvidenceCollectionChecklistResult:
    return build_evidence_collection_checklist(registry_path, load_verified_evidence_intake(intake_path))
