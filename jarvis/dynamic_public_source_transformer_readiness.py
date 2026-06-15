"""Public source transformer-readiness plan for J.A.R.V.I.S.

Report-only classifier for public source candidates. This module does not fetch,
call APIs, connect to brokers, approve assets, create buy requests, promote
endpoint packs, mutate registries, or execute trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "DYNAMIC_PUBLIC_SOURCE_TRANSFORMER_READINESS_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_PUBLIC_SOURCE_TRANSFORMER_READINESS_BLOCKED_SAFE"

DEFAULT_CANDIDATE_MATRIX_PATH = "jarvis/data/dynamic_public_source_candidates.template.json"

NORMALIZER_READY_STATUSES = {
    "PARSER_COMPATIBLE_IF_CSV_HAS_DATE_CLOSE_COLUMNS",
    "PARSER_COMPATIBLE_IF_JSON_HAS_DATE_CLOSE_ROWS",
}

TRANSFORMER_REQUIRED_STATUSES = {
    "TRANSFORMER_REQUIRED_NOT_RAW_NORMALIZER_READY",
    "FX_SUPPORT_TRANSFORMER_REQUIRED_NOT_APPROVED_ASSET_ENDPOINT",
}


@dataclass(frozen=True)
class DynamicPublicSourceTransformerReadinessRow:
    source_key: str
    asset_id: str | None
    asset_type: str | None
    provider_candidate: str | None
    source_role: str | None
    parser_compatibility_status: str | None
    readiness_classification: str
    promotion_allowed: bool
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_key": self.source_key,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "provider_candidate": self.provider_candidate,
            "source_role": self.source_role,
            "parser_compatibility_status": self.parser_compatibility_status,
            "readiness_classification": self.readiness_classification,
            "promotion_allowed": self.promotion_allowed,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicPublicSourceTransformerReadinessResult:
    status: str
    candidate_count: int
    normalizer_ready_count: int
    transformer_required_count: int
    support_only_count: int
    promotion_allowed_count: int
    rows: tuple[DynamicPublicSourceTransformerReadinessRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_review_required: bool
    fetching_forbidden: bool
    execution_forbidden: bool
    creates_buy_request: bool
    grants_approval: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidate_count": self.candidate_count,
            "normalizer_ready_count": self.normalizer_ready_count,
            "transformer_required_count": self.transformer_required_count,
            "support_only_count": self.support_only_count,
            "promotion_allowed_count": self.promotion_allowed_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_review_required": self.manual_review_required,
            "fetching_forbidden": self.fetching_forbidden,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "grants_approval": self.grants_approval,
            "no_trades_executed": self.no_trades_executed,
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("public source candidate matrix must be a JSON object.")
    return raw


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _bool(value: Any) -> bool:
    return value is True


def _classify_candidate(candidate: dict[str, Any], index: int) -> DynamicPublicSourceTransformerReadinessRow:
    asset_id = _text(candidate.get("asset_id"))
    support_id = _text(candidate.get("support_id"))
    asset_type = _text(candidate.get("asset_type"))
    provider_candidate = _text(candidate.get("provider_candidate"))
    source_role = _text(candidate.get("source_role"))
    parser_status = _text(candidate.get("parser_compatibility_status"))
    promotion_allowed = _bool(candidate.get("promotion_allowed"))

    source_key = asset_id or support_id or f"candidate_{index}"
    warnings: list[str] = []
    blockers: list[str] = []

    if parser_status in NORMALIZER_READY_STATUSES:
        classification = "NORMALIZER_READY_AFTER_MANUAL_VERIFICATION"
    elif parser_status == "TRANSFORMER_REQUIRED_NOT_RAW_NORMALIZER_READY":
        classification = "TRANSFORMER_REQUIRED_BEFORE_ENDPOINT_PROMOTION"
    elif parser_status == "FX_SUPPORT_TRANSFORMER_REQUIRED_NOT_APPROVED_ASSET_ENDPOINT":
        classification = "SUPPORT_ONLY_TRANSFORMER_REQUIRED"
    else:
        classification = "UNKNOWN_TRANSFORMER_READINESS"
        blockers.append(f"{source_key}: parser_compatibility_status is unknown or missing.")

    if promotion_allowed:
        blockers.append(f"{source_key}: promotion_allowed must remain false in transformer readiness planning.")

    if candidate.get("manual_source_url_verification_status") != "pending_manual_operator_check":
        blockers.append(f"{source_key}: manual source URL verification must remain pending.")

    if asset_type == "crypto" and parser_status != "TRANSFORMER_REQUIRED_NOT_RAW_NORMALIZER_READY":
        blockers.append(f"{source_key}: crypto candidates must remain transformer-required until an adapter exists.")

    if asset_type == "fx_reference_support" and asset_id is not None:
        blockers.append(f"{source_key}: FX support candidates must not be approved asset endpoints.")

    if _bool(candidate.get("requires_authentication")) or _bool(candidate.get("requires_credentials")):
        blockers.append(f"{source_key}: candidate source must not require authentication or credentials.")

    if _bool(candidate.get("broker_or_trading_api")):
        blockers.append(f"{source_key}: candidate source must not be a broker or trading API.")

    if _bool(candidate.get("contains_private_data")):
        blockers.append(f"{source_key}: candidate source must not contain private data.")

    if not _bool(candidate.get("public_source_only")):
        blockers.append(f"{source_key}: candidate source must be public_source_only.")

    if candidate.get("cross_check_required") is False and asset_type != "fx_reference_support":
        warnings.append(f"{source_key}: non-FX candidate has no required cross-check.")

    return DynamicPublicSourceTransformerReadinessRow(
        source_key=source_key,
        asset_id=asset_id,
        asset_type=asset_type,
        provider_candidate=provider_candidate,
        source_role=source_role,
        parser_compatibility_status=parser_status,
        readiness_classification=classification,
        promotion_allowed=promotion_allowed,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def audit_dynamic_public_source_transformer_readiness(
    candidate_matrix_path: str | Path = DEFAULT_CANDIDATE_MATRIX_PATH,
) -> DynamicPublicSourceTransformerReadinessResult:
    matrix = _load_json(candidate_matrix_path)
    candidates = matrix.get("candidates", [])

    blockers: list[str] = []
    warnings: list[str] = []

    if matrix.get("template_only") is not True:
        blockers.append("candidate matrix must remain template_only true.")
    if matrix.get("active_endpoint_pack") is not False:
        blockers.append("candidate matrix must not be an active endpoint pack.")
    if matrix.get("fetching_forbidden") is not True:
        blockers.append("candidate matrix must keep fetching_forbidden true.")
    if matrix.get("manual_review_required") is not True:
        blockers.append("candidate matrix must keep manual_review_required true.")
    if matrix.get("execution_forbidden") is not True:
        blockers.append("candidate matrix must keep execution_forbidden true.")
    if matrix.get("creates_buy_request") is not False:
        blockers.append("candidate matrix must not create buy requests.")
    if matrix.get("grants_approval") is not False:
        blockers.append("candidate matrix must not grant approval.")
    if matrix.get("no_trades_executed") is not True:
        blockers.append("candidate matrix must keep no_trades_executed true.")

    if not isinstance(candidates, list) or not candidates:
        blockers.append("candidate matrix must contain at least one candidate row.")
        candidates = []

    rows = tuple(
        _classify_candidate(candidate, index)
        for index, candidate in enumerate(candidates)
        if isinstance(candidate, dict)
    )

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    normalizer_ready_count = sum(
        1 for row in rows
        if row.readiness_classification == "NORMALIZER_READY_AFTER_MANUAL_VERIFICATION"
    )
    transformer_required_count = sum(
        1 for row in rows
        if row.readiness_classification == "TRANSFORMER_REQUIRED_BEFORE_ENDPOINT_PROMOTION"
    )
    support_only_count = sum(
        1 for row in rows
        if row.readiness_classification == "SUPPORT_ONLY_TRANSFORMER_REQUIRED"
    )
    promotion_allowed_count = sum(1 for row in rows if row.promotion_allowed)

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicPublicSourceTransformerReadinessResult(
        status=status,
        candidate_count=len(rows),
        normalizer_ready_count=normalizer_ready_count,
        transformer_required_count=transformer_required_count,
        support_only_count=support_only_count,
        promotion_allowed_count=promotion_allowed_count,
        rows=rows,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_review_required=True,
        fetching_forbidden=True,
        execution_forbidden=True,
        creates_buy_request=False,
        grants_approval=False,
        no_trades_executed=True,
    )
