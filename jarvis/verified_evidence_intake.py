"""Manual verified evidence intake pack for candidate review provenance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .evidence_provenance import (
    ALLOWED_SOURCE_QUALITIES,
    EvidenceProvenanceRecord,
    EvidenceProvenanceReportResult,
    classify_evidence_readiness,
)


ALLOWED_INTAKE_EVIDENCE_TYPES = {
    "market_data",
    "exposure_data",
    "platform_availability",
    "tax_route",
    "custody_route",
    "fund_metadata",
    "protocol_metadata",
    "fee_metadata",
    "distribution_policy",
}
PROVENANCE_EVIDENCE_TYPE_MAP = {
    "protocol_metadata": "fund_metadata",
    "fee_metadata": "fund_metadata",
    "distribution_policy": "tax_route",
}
STALE_DAYS = 180
REFERENCE_DATE = date(2026, 6, 5)


@dataclass(frozen=True)
class VerifiedEvidenceIntakeRecord:
    evidence_id: str
    asset_id: str
    evidence_type: str
    source_quality: str
    source_name: str
    as_of: str
    verified_by_user: bool
    verification_notes: str
    file_reference: str | None
    url_reference: str | None
    extracted_facts: dict[str, object]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class IntakeValidationResult:
    valid: bool
    record: VerifiedEvidenceIntakeRecord | None
    provenance_record: EvidenceProvenanceRecord | None
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    evidence_id: str | None = None
    asset_id: str | None = None


@dataclass(frozen=True)
class VerifiedEvidencePackSummary:
    total_intake_records: int
    valid_records: int
    invalid_records: int
    verified_records: int
    unverified_records: int
    records_by_evidence_type: dict[str, int]
    records_by_source_quality: dict[str, int]
    affected_assets: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedEvidencePack:
    intake_status: str
    validation_results: tuple[IntakeValidationResult, ...]
    provenance_records: tuple[EvidenceProvenanceRecord, ...]
    provenance_gate: EvidenceProvenanceReportResult
    assets_with_real_status_promotion_allowed: tuple[str, ...]
    summary: VerifiedEvidencePackSummary
    manual_approval_required: bool = True
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field)


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be true or false.")
    return value


def _parse_iso_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("as_of must be an ISO date.") from exc


def _provenance_type(evidence_type: str) -> str:
    return PROVENANCE_EVIDENCE_TYPE_MAP.get(evidence_type, evidence_type)


def validate_intake_record(
    raw: dict[str, Any],
    known_assets: dict[str, CandidateAsset],
    reference_date: date = REFERENCE_DATE,
) -> IntakeValidationResult:
    evidence_id = raw.get("evidence_id") if isinstance(raw, dict) else None
    asset_id = raw.get("asset_id") if isinstance(raw, dict) else None
    warnings: list[str] = []
    blockers: list[str] = []
    try:
        item = _require_mapping(raw, "intake record")
        evidence_id_text = _require_text(item.get("evidence_id"), "evidence_id")
        asset_id_text = _require_text(item.get("asset_id"), "asset_id")
        if asset_id_text not in known_assets:
            raise ValueError(f"unknown asset_id {asset_id_text}.")
        evidence_type = _require_text(item.get("evidence_type"), "evidence_type")
        if evidence_type not in ALLOWED_INTAKE_EVIDENCE_TYPES:
            raise ValueError(f"unsupported evidence_type {evidence_type}.")
        source_quality = _require_text(item.get("source_quality"), "source_quality")
        if source_quality not in ALLOWED_SOURCE_QUALITIES:
            raise ValueError(f"unsupported source_quality {source_quality}.")
        source_name = _require_text(item.get("source_name"), "source_name")
        as_of = _require_text(item.get("as_of"), "as_of")
        as_of_date = _parse_iso_date(as_of)
        verified_by_user = _require_bool(item.get("verified_by_user"), "verified_by_user")
        verification_notes = item.get("verification_notes", "")
        if verified_by_user:
            verification_notes = _require_text(verification_notes, "verification_notes")
        elif not isinstance(verification_notes, str):
            raise ValueError("verification_notes must be text.")
        file_reference = _optional_text(item.get("file_reference"), "file_reference")
        url_reference = _optional_text(item.get("url_reference"), "url_reference")
        extracted_facts = item.get("extracted_facts", {})
        if not isinstance(extracted_facts, dict):
            raise ValueError("extracted_facts must be an object when provided.")
        record_warnings = item.get("warnings", [])
        if not isinstance(record_warnings, list):
            raise ValueError("warnings must be a list.")
        warnings.extend(str(warning) for warning in record_warnings)
        if not verified_by_user:
            warnings.append(f"{evidence_id_text}: evidence is unverified and will not count as review evidence.")
        if (reference_date - as_of_date).days > STALE_DAYS:
            warnings.append(f"{evidence_id_text}: evidence is older than {STALE_DAYS} days.")
        if not file_reference and not url_reference:
            warnings.append(f"{evidence_id_text}: file_reference and url_reference are both missing.")

        record = VerifiedEvidenceIntakeRecord(
            evidence_id=evidence_id_text,
            asset_id=asset_id_text,
            evidence_type=evidence_type,
            source_quality=source_quality,
            source_name=source_name,
            as_of=as_of,
            verified_by_user=verified_by_user,
            verification_notes=verification_notes,
            file_reference=file_reference,
            url_reference=url_reference,
            extracted_facts=extracted_facts,
            warnings=tuple(warnings),
        )
        provenance = EvidenceProvenanceRecord(
            asset_id=record.asset_id,
            evidence_type=_provenance_type(record.evidence_type),
            source_quality=record.source_quality,
            source_name=record.source_name,
            as_of=record.as_of,
            verified_by_user=record.verified_by_user,
            notes=record.verification_notes or "Unverified intake record.",
        )
        return IntakeValidationResult(
            valid=True,
            record=record,
            provenance_record=provenance,
            warnings=tuple(warnings),
            blockers=(),
            evidence_id=evidence_id_text,
            asset_id=asset_id_text,
        )
    except ValueError as exc:
        blockers.append(str(exc))
        return IntakeValidationResult(
            valid=False,
            record=None,
            provenance_record=None,
            warnings=tuple(warnings),
            blockers=tuple(blockers),
            evidence_id=str(evidence_id) if evidence_id is not None else None,
            asset_id=str(asset_id) if asset_id is not None else None,
        )


def load_verified_evidence_intake(path: str | Path) -> list[dict[str, Any]]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "verified evidence intake")
    records = raw.get("records")
    if not isinstance(records, list):
        raise ValueError("verified evidence intake must contain a records list.")
    return [_require_mapping(record, "intake record") for record in records]


def build_verified_evidence_pack(
    candidate_registry: str | Path | AssetRegistry,
    intake_records: list[dict[str, Any]],
) -> VerifiedEvidencePack:
    registry = load_asset_registry(candidate_registry) if not isinstance(candidate_registry, AssetRegistry) else candidate_registry
    assets_by_id = registry.by_id()
    validation_results = tuple(validate_intake_record(record, assets_by_id) for record in intake_records)
    provenance_records = tuple(result.provenance_record for result in validation_results if result.provenance_record)
    gate_results_by_id = classify_evidence_readiness(provenance_records, assets_by_id)
    gate_results = tuple(gate_results_by_id[asset.asset_id] for asset in registry.assets)
    assets_allowed = tuple(
        result.asset_id for result in gate_results if result.real_status_promotion_allowed
    )
    warnings = tuple(
        dict.fromkeys(
            [warning for result in validation_results for warning in result.warnings]
            + [warning for result in gate_results for warning in result.warnings]
        )
    )
    blockers = tuple(
        dict.fromkeys(
            [blocker for result in validation_results for blocker in result.blockers]
            + [blocker for result in gate_results for blocker in result.blockers]
        )
    )
    by_type: dict[str, int] = {}
    by_quality: dict[str, int] = {}
    affected_assets: set[str] = set()
    for result in validation_results:
        if result.record is None:
            continue
        by_type[result.record.evidence_type] = by_type.get(result.record.evidence_type, 0) + 1
        by_quality[result.record.source_quality] = by_quality.get(result.record.source_quality, 0) + 1
        affected_assets.add(result.record.asset_id)

    from .evidence_provenance import EvidenceProvenanceReportResult, EvidenceProvenanceSummary

    gate_summary = EvidenceProvenanceSummary(
        total_candidates=len(registry.assets),
        only_synthetic_or_test_evidence_count=sum(
            result.has_test_evidence and not result.has_review_evidence for result in gate_results
        ),
        verified_review_evidence_count=sum(result.has_review_evidence for result in gate_results),
        real_status_promotion_allowed_count=len(assets_allowed),
        warnings=tuple(warning for result in gate_results for warning in result.warnings),
        blockers=tuple(blocker for result in gate_results for blocker in result.blockers),
    )
    gate = EvidenceProvenanceReportResult(gate_results, gate_summary)
    summary = VerifiedEvidencePackSummary(
        total_intake_records=len(intake_records),
        valid_records=sum(result.valid for result in validation_results),
        invalid_records=sum(not result.valid for result in validation_results),
        verified_records=sum(bool(result.record and result.record.verified_by_user) for result in validation_results),
        unverified_records=sum(bool(result.record and not result.record.verified_by_user) for result in validation_results),
        records_by_evidence_type=dict(sorted(by_type.items())),
        records_by_source_quality=dict(sorted(by_quality.items())),
        affected_assets=tuple(sorted(affected_assets)),
        warnings=warnings,
        blockers=blockers,
    )
    return VerifiedEvidencePack(
        intake_status="VALID_WITH_WARNINGS" if summary.valid_records and warnings else ("VALID" if summary.valid_records else "BLOCKED"),
        validation_results=validation_results,
        provenance_records=provenance_records,
        provenance_gate=gate,
        assets_with_real_status_promotion_allowed=assets_allowed,
        summary=summary,
    )


def build_verified_evidence_pack_from_files(registry_path: str | Path, intake_path: str | Path) -> VerifiedEvidencePack:
    return build_verified_evidence_pack(registry_path, load_verified_evidence_intake(intake_path))
