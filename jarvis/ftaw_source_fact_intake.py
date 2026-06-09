"""Manual FTAW public source fact intake.

Automated structure. Manual trust.

This module validates user-supplied public facts and converts them into
VerifiedEvidenceIntakeRecord-compatible draft records. It does not verify,
approve, mutate registries, recommend allocations, create orders, or trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import load_asset_registry
from .ftaw_draft_evidence_verification_queue import REQUIRED_FACT_FIELDS
from .ftaw_public_source_research_pack import PUBLIC_RESEARCH_EVIDENCE_TYPES


TARGET_ASSET_ID = "ftaw_global_core_candidate"
MANUAL_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWSourceFactRecord:
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    url_reference: str
    file_reference: str | None
    as_of: str
    extracted_facts: dict[str, object]
    user_notes: str


@dataclass(frozen=True)
class FTAWSourceFactIntakeConfig:
    records: tuple[FTAWSourceFactRecord, ...]


@dataclass(frozen=True)
class FTAWSourceFactIntakeResult:
    asset_id: str
    evidence_type: str
    intake_status: str
    draft_status: str | None
    draft_record: dict[str, object] | None
    missing_facts: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class FTAWSourceFactIntakePack:
    intake_status: str
    processed_fact_records_count: int
    draft_evidence_records: tuple[dict[str, object], ...]
    draft_ready_count: int
    needs_correction_count: int
    skipped_manual_evidence_types: tuple[str, ...]
    missing_facts_by_evidence_type: dict[str, tuple[str, ...]]
    results: tuple[FTAWSourceFactIntakeResult, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
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


def _parse_record(raw: dict[str, Any]) -> FTAWSourceFactRecord:
    item = _require_mapping(raw, "source fact record")
    return FTAWSourceFactRecord(
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        source_name=_require_text(item.get("source_name"), "source_name"),
        source_quality=_require_text(item.get("source_quality"), "source_quality"),
        url_reference=_require_text(item.get("url_reference"), "url_reference"),
        file_reference=_optional_text(item.get("file_reference"), "file_reference"),
        as_of=_require_text(item.get("as_of"), "as_of"),
        extracted_facts=dict(_require_mapping(item.get("extracted_facts"), "extracted_facts")),
        user_notes=_require_text(item.get("user_notes"), "user_notes"),
    )


def load_ftaw_source_fact_intake_config(path: str | Path) -> FTAWSourceFactIntakeConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW source fact intake config")
    records = raw.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be a list.")
    return FTAWSourceFactIntakeConfig(records=tuple(_parse_record(record) for record in records))


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return not stripped or stripped.startswith("<") or stripped.endswith("_to_capture>")
    return False


def _missing_required(evidence_type: str, facts: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        field
        for field in REQUIRED_FACT_FIELDS.get(evidence_type, ())
        if field not in facts or _is_placeholder(facts[field])
    )


def _draft_record(record: FTAWSourceFactRecord, warnings: tuple[str, ...]) -> dict[str, object]:
    return {
        "evidence_id": f"user_fact_draft_{record.evidence_type}",
        "asset_id": record.asset_id,
        "evidence_type": record.evidence_type,
        "source_quality": record.source_quality,
        "source_name": record.source_name,
        "as_of": record.as_of,
        "verified_by_user": False,
        "verification_notes": "User-supplied public source facts. Manual verification required.",
        "file_reference": record.file_reference,
        "url_reference": record.url_reference,
        "extracted_facts": dict(record.extracted_facts),
        "warnings": list(warnings),
    }


def process_fact_record(record: FTAWSourceFactRecord) -> FTAWSourceFactIntakeResult:
    warnings: list[str] = []
    blockers: list[str] = []
    if record.asset_id != TARGET_ASSET_ID:
        return FTAWSourceFactIntakeResult(record.asset_id, record.evidence_type, "skipped", None, None, (), (), ())
    if record.evidence_type in MANUAL_EVIDENCE_TYPES:
        warnings.append(f"{record.evidence_type}: manual evidence type skipped by source fact intake.")
        return FTAWSourceFactIntakeResult(record.asset_id, record.evidence_type, "skipped", None, None, (), tuple(warnings), ())
    if record.evidence_type not in PUBLIC_RESEARCH_EVIDENCE_TYPES:
        blockers.append(f"{record.evidence_type}: unsupported public evidence type.")
        return FTAWSourceFactIntakeResult(record.asset_id, record.evidence_type, "blocked", None, None, (), tuple(warnings), tuple(blockers))
    warnings.append("user_supplied_public_facts_require_manual_verification")
    missing = _missing_required(record.evidence_type, record.extracted_facts)
    blockers.extend(f"{record.evidence_type}: missing required fact {fact}." for fact in missing)
    status = "needs_correction" if missing else "draft_ready_for_manual_verification"
    return FTAWSourceFactIntakeResult(
        asset_id=record.asset_id,
        evidence_type=record.evidence_type,
        intake_status="processed",
        draft_status=status,
        draft_record=_draft_record(record, tuple(warnings)),
        missing_facts=missing,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def build_ftaw_source_fact_intake_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    intake_config: FTAWSourceFactIntakeConfig,
) -> FTAWSourceFactIntakePack:
    registry = load_asset_registry(source_registry_path)
    if TARGET_ASSET_ID not in registry.by_id():
        raise ValueError(f"{TARGET_ASSET_ID} not found in registry.")
    Path(url_fetch_config_path).read_text(encoding="utf-8")
    if reviewed_registry_copy_path is not None and str(reviewed_registry_copy_path).lower() not in {"", "none", "null", "-"}:
        Path(reviewed_registry_copy_path).read_text(encoding="utf-8")

    results = tuple(process_fact_record(record) for record in intake_config.records)
    records = tuple(result.draft_record for result in results if result.draft_record is not None)
    warnings = tuple(dict.fromkeys(warning for result in results for warning in result.warnings))
    blockers = tuple(dict.fromkeys(blocker for result in results for blocker in result.blockers))
    missing_by_type: dict[str, tuple[str, ...]] = {
        result.evidence_type: result.missing_facts for result in results if result.missing_facts
    }
    ready_count = sum(result.draft_status == "draft_ready_for_manual_verification" for result in results)
    correction_count = sum(result.draft_status == "needs_correction" for result in results)
    status = "READY_WITH_CORRECTIONS" if correction_count else "READY" if records else "NO_DRAFTS"
    if any(result.intake_status == "blocked" for result in results):
        status = "BLOCKED"
    return FTAWSourceFactIntakePack(
        intake_status=status,
        processed_fact_records_count=sum(result.intake_status == "processed" for result in results),
        draft_evidence_records=records,
        draft_ready_count=ready_count,
        needs_correction_count=correction_count,
        skipped_manual_evidence_types=tuple(sorted({result.evidence_type for result in results if result.evidence_type in MANUAL_EVIDENCE_TYPES and result.intake_status == "skipped"})),
        missing_facts_by_evidence_type=dict(sorted(missing_by_type.items())),
        results=results,
        warnings=warnings,
        blockers=blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_source_fact_intake_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
) -> FTAWSourceFactIntakePack:
    return build_ftaw_source_fact_intake_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        load_ftaw_source_fact_intake_config(fact_intake_config_path),
    )


def write_improved_draft_evidence(pack: FTAWSourceFactIntakePack, output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "records": list(pack.draft_evidence_records),
        "manual_verification_required": True,
        "verified_by_user_by_default": False,
        "approvals_created": False,
        "registry_mutation_allowed": False,
        "allocation_recommendation_created": False,
        "buy_sell_requests_created": False,
        "trades_executed": False,
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
