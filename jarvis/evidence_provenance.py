"""Evidence provenance gate for candidate status-review readiness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .asset_registry import CandidateAsset, load_asset_registry
from .candidate_evidence_matrix import build_candidate_evidence_matrix


ALLOWED_SOURCE_QUALITIES = {
    "synthetic_fixture",
    "manual_research",
    "platform_screenshot",
    "provider_factsheet",
    "broker_export",
    "verified_api_snapshot",
}
ALLOWED_EVIDENCE_TYPES = {
    "market_data",
    "exposure_data",
    "platform_availability",
    "tax_route",
    "custody_route",
    "fund_metadata",
}
REVIEW_SOURCE_QUALITIES = ALLOWED_SOURCE_QUALITIES.difference({"synthetic_fixture"})


class EvidenceProvenanceError(ValueError):
    """Raised when evidence provenance fixture data is malformed."""


@dataclass(frozen=True)
class EvidenceProvenanceRecord:
    asset_id: str
    evidence_type: str
    source_quality: str
    source_name: str
    as_of: str
    verified_by_user: bool
    notes: str


@dataclass(frozen=True)
class EvidenceProvenanceGateResult:
    asset_id: str
    has_test_evidence: bool
    has_review_evidence: bool
    real_status_promotion_allowed: bool
    missing_real_evidence: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "has_test_evidence": self.has_test_evidence,
            "has_review_evidence": self.has_review_evidence,
            "real_status_promotion_allowed": self.real_status_promotion_allowed,
            "missing_real_evidence": list(self.missing_real_evidence),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class EvidenceProvenanceSummary:
    total_candidates: int
    only_synthetic_or_test_evidence_count: int
    verified_review_evidence_count: int
    real_status_promotion_allowed_count: int
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceProvenanceReportResult:
    gate_results: tuple[EvidenceProvenanceGateResult, ...]
    summary: EvidenceProvenanceSummary
    manual_approval_required: bool = True
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "gate_results": [result.to_dict() for result in self.gate_results],
            "summary": {
                "total_candidates": self.summary.total_candidates,
                "only_synthetic_or_test_evidence_count": self.summary.only_synthetic_or_test_evidence_count,
                "verified_review_evidence_count": self.summary.verified_review_evidence_count,
                "real_status_promotion_allowed_count": self.summary.real_status_promotion_allowed_count,
                "warnings": list(self.summary.warnings),
                "blockers": list(self.summary.blockers),
            },
            "manual_approval_required": self.manual_approval_required,
            "approvals_created": self.approvals_created,
            "registry_mutation_allowed": self.registry_mutation_allowed,
            "buy_sell_requests_created": self.buy_sell_requests_created,
            "trades_executed": self.trades_executed,
        }


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceProvenanceError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceProvenanceError(f"{field} must be non-empty text.")
    return value.strip()


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise EvidenceProvenanceError(f"{field} must be true or false.")
    return value


def _validate_iso_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise EvidenceProvenanceError("as_of must be an ISO date.") from exc
    return value


def parse_evidence_record(raw: dict[str, Any]) -> EvidenceProvenanceRecord:
    item = _require_mapping(raw, "evidence record")
    evidence_type = _require_text(item.get("evidence_type"), "evidence_type")
    if evidence_type not in ALLOWED_EVIDENCE_TYPES:
        raise EvidenceProvenanceError(f"evidence_type {evidence_type} is not allowed.")
    source_quality = _require_text(item.get("source_quality"), "source_quality")
    if source_quality not in ALLOWED_SOURCE_QUALITIES:
        raise EvidenceProvenanceError(f"source_quality {source_quality} is not allowed.")
    return EvidenceProvenanceRecord(
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=evidence_type,
        source_quality=source_quality,
        source_name=_require_text(item.get("source_name"), "source_name"),
        as_of=_validate_iso_date(_require_text(item.get("as_of"), "as_of")),
        verified_by_user=_require_bool(item.get("verified_by_user"), "verified_by_user"),
        notes=_require_text(item.get("notes"), "notes"),
    )


def load_evidence_provenance(path: str | Path) -> tuple[EvidenceProvenanceRecord, ...]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "evidence provenance")
    records = raw.get("records")
    if not isinstance(records, list):
        raise EvidenceProvenanceError("evidence provenance must contain a records list.")
    return tuple(parse_evidence_record(record) for record in records)


def required_review_evidence_for_asset(asset: CandidateAsset) -> tuple[str, ...]:
    if asset.asset_type == "ETF":
        return ("fund_metadata", "market_data", "exposure_data", "platform_availability", "tax_route")
    if asset.asset_type == "crypto":
        return ("fund_metadata", "market_data", "platform_availability", "custody_route", "tax_route")
    return ("fund_metadata", "platform_availability")


def _record_is_review_evidence(record: EvidenceProvenanceRecord) -> bool:
    return record.source_quality in REVIEW_SOURCE_QUALITIES and record.verified_by_user


def classify_evidence_readiness(
    records: tuple[EvidenceProvenanceRecord, ...] | list[EvidenceProvenanceRecord],
    assets_by_id: dict[str, CandidateAsset] | None = None,
) -> dict[str, EvidenceProvenanceGateResult]:
    grouped: dict[str, list[EvidenceProvenanceRecord]] = {}
    for record in records:
        grouped.setdefault(record.asset_id, []).append(record)

    asset_ids = sorted(set(grouped) | set(assets_by_id or {}))
    results: dict[str, EvidenceProvenanceGateResult] = {}
    for asset_id in asset_ids:
        asset_records = grouped.get(asset_id, [])
        test_types = {record.evidence_type for record in asset_records if record.source_quality == "synthetic_fixture"}
        review_types = {record.evidence_type for record in asset_records if _record_is_review_evidence(record)}
        warnings = [
            f"{asset_id}: {record.evidence_type} {record.source_quality} evidence is unverified and does not count for real review."
            for record in asset_records
            if record.source_quality in REVIEW_SOURCE_QUALITIES and not record.verified_by_user
        ]

        asset = assets_by_id.get(asset_id) if assets_by_id else None
        required = required_review_evidence_for_asset(asset) if asset else tuple(sorted(review_types or test_types))
        missing = tuple(evidence_type for evidence_type in required if evidence_type not in review_types)
        blockers: list[str] = []
        if asset_records and test_types and not review_types:
            blockers.append(f"{asset_id}: only synthetic_fixture evidence is present.")
        for evidence_type in missing:
            blockers.append(f"{asset_id}: missing verified {evidence_type} evidence.")
        if not asset_records:
            blockers.append(f"{asset_id}: no evidence provenance records found.")

        results[asset_id] = EvidenceProvenanceGateResult(
            asset_id=asset_id,
            has_test_evidence=bool(test_types),
            has_review_evidence=bool(review_types),
            real_status_promotion_allowed=bool(review_types) and not missing,
            missing_real_evidence=missing,
            warnings=tuple(dict.fromkeys(warnings)),
            blockers=tuple(dict.fromkeys(blockers)),
        )
    return results


def build_evidence_provenance_gate(
    registry_path: str | Path,
    provenance_path: str | Path,
) -> EvidenceProvenanceReportResult:
    registry = load_asset_registry(registry_path)
    assets_by_id = registry.by_id()
    results_by_id = classify_evidence_readiness(load_evidence_provenance(provenance_path), assets_by_id)
    results = tuple(results_by_id[asset.asset_id] for asset in registry.assets)
    warnings = tuple(dict.fromkeys(warning for result in results for warning in result.warnings))
    blockers = tuple(dict.fromkeys(blocker for result in results for blocker in result.blockers))
    summary = EvidenceProvenanceSummary(
        total_candidates=len(registry.assets),
        only_synthetic_or_test_evidence_count=sum(
            result.has_test_evidence and not result.has_review_evidence for result in results
        ),
        verified_review_evidence_count=sum(result.has_review_evidence for result in results),
        real_status_promotion_allowed_count=sum(result.real_status_promotion_allowed for result in results),
        warnings=warnings,
        blockers=blockers,
    )
    return EvidenceProvenanceReportResult(results, summary)


def build_candidate_evidence_with_provenance(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
    provenance_path: str | Path,
) -> list[dict[str, object]]:
    matrix = build_candidate_evidence_matrix(registry_path, market_data_path, exposure_path, policy_path)
    provenance = build_evidence_provenance_gate(registry_path, provenance_path)
    gates = {result.asset_id: result for result in provenance.gate_results}
    rows: list[dict[str, object]] = []
    for row in matrix.rows:
        gate = gates[row.asset_id]
        payload = row.to_dict()
        payload["eligible_for_manual_review_test_mode"] = row.eligible_for_manual_review
        payload["eligible_for_real_status_review"] = gate.real_status_promotion_allowed
        payload["real_status_review_blockers"] = list(gate.blockers)
        rows.append(payload)
    return rows
