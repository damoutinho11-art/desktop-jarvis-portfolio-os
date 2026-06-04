"""Manual asset status change workflow for local registry governance."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from .asset_registry import APPROVAL_STATUSES


ALLOWED_TRANSITIONS = {
    ("candidate_unreviewed", "candidate_reviewed"),
    ("candidate_reviewed", "approved_watchlist"),
    ("approved_watchlist", "approved_investable"),
    ("approved_investable", "approved_watchlist"),
    ("approved_watchlist", "rejected"),
    ("candidate_reviewed", "rejected"),
    ("candidate_unreviewed", "rejected"),
    ("test_position", "candidate_reviewed"),
    ("legacy_existing", "candidate_reviewed"),
}
WATCHLIST_CONFIRMATIONS = {
    "candidate_review_pack_present",
    "scorecard_reviewed",
    "risk_metrics_reviewed",
}
INVESTABLE_BASE_CONFIRMATIONS = {
    "candidate_review_pack_present",
    "scorecard_reviewed",
    "risk_metrics_reviewed",
    "platform_tax_fit_reviewed",
    "manual_asset_approval_confirmed",
}
ETF_INVESTABLE_CONFIRMATIONS = {
    "concentration_reviewed",
    "expense_ratio_reviewed",
    "overlap_concentration_reviewed",
    "accumulating_distribution_reviewed",
    "platform_availability_reviewed",
}
CRYPTO_INVESTABLE_CONFIRMATIONS = {
    "custody_risk_reviewed",
    "crypto_tax_risk_reviewed",
    "position_size_limit_acknowledged",
}


class AssetStatusWorkflowError(ValueError):
    """Raised when asset status request data is malformed."""


@dataclass(frozen=True)
class AssetStatusChangeRequest:
    request_id: str
    created_at: str
    asset_id: str
    asset_type: str
    current_status: str
    requested_status: str
    rationale: str
    evidence_summary: str
    required_confirmations: tuple[str, ...]
    manual_approval_required: bool
    auto_execute: bool


@dataclass(frozen=True)
class AssetStatusValidationResult:
    request: AssetStatusChangeRequest
    valid: bool
    allowed_transition: bool
    missing_confirmations: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...] = ()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssetStatusWorkflowError(f"{field} exists and must be text.")
    return value.strip()


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise AssetStatusWorkflowError(f"{field} must be true or false.")
    return value


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise AssetStatusWorkflowError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def _validate_iso_datetime(value: str) -> str:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AssetStatusWorkflowError("created_at must be ISO-like datetime text.") from exc
    return value


def parse_asset_status_request(raw: dict[str, Any]) -> AssetStatusChangeRequest:
    if not isinstance(raw, dict):
        raise AssetStatusWorkflowError("asset status request must be an object.")
    request = AssetStatusChangeRequest(
        request_id=_require_text(raw.get("request_id"), "request_id"),
        created_at=_validate_iso_datetime(_require_text(raw.get("created_at"), "created_at")),
        asset_id=_require_text(raw.get("asset_id"), "asset_id"),
        asset_type=_require_text(raw.get("asset_type"), "asset_type"),
        current_status=_require_text(raw.get("current_status"), "current_status"),
        requested_status=_require_text(raw.get("requested_status"), "requested_status"),
        rationale=_require_text(raw.get("rationale"), "rationale"),
        evidence_summary=_require_text(raw.get("evidence_summary"), "evidence_summary"),
        required_confirmations=_require_text_list(raw.get("required_confirmations"), "required_confirmations"),
        manual_approval_required=_require_bool(raw.get("manual_approval_required"), "manual_approval_required"),
        auto_execute=_require_bool(raw.get("auto_execute"), "auto_execute"),
    )
    if request.current_status not in APPROVAL_STATUSES:
        raise AssetStatusWorkflowError(f"current_status {request.current_status} is not allowed.")
    if request.requested_status not in APPROVAL_STATUSES:
        raise AssetStatusWorkflowError(f"requested_status {request.requested_status} is not allowed.")
    return request


def load_asset_status_requests(path: str | Path) -> list[AssetStatusChangeRequest]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssetStatusWorkflowError("asset status requests fixture must be an object.")
    requests = raw.get("requests")
    if not isinstance(requests, list):
        raise AssetStatusWorkflowError("asset status requests fixture must contain a requests list.")
    parsed = [parse_asset_status_request(item) for item in requests]
    seen_ids: set[str] = set()
    for request in parsed:
        if request.request_id in seen_ids:
            raise AssetStatusWorkflowError(f"duplicate request_id {request.request_id}.")
        seen_ids.add(request.request_id)
    return parsed


def required_confirmations_for_transition(request: AssetStatusChangeRequest) -> set[str]:
    if request.requested_status == "approved_watchlist":
        return set(WATCHLIST_CONFIRMATIONS)
    if request.requested_status == "approved_investable":
        required = set(INVESTABLE_BASE_CONFIRMATIONS)
        if request.asset_type == "ETF":
            required.update(ETF_INVESTABLE_CONFIRMATIONS)
        elif request.asset_type == "crypto":
            required.update(CRYPTO_INVESTABLE_CONFIRMATIONS)
        return required
    return set()


def validate_asset_status_request(request: AssetStatusChangeRequest) -> AssetStatusValidationResult:
    blockers: list[str] = []
    warnings: list[str] = []
    transition = (request.current_status, request.requested_status)
    allowed_transition = transition in ALLOWED_TRANSITIONS
    if not allowed_transition:
        blockers.append(f"transition {request.current_status} -> {request.requested_status} is not allowed.")
    if request.auto_execute:
        blockers.append("auto_execute must always be false.")
    if not request.manual_approval_required:
        blockers.append("manual_approval_required must always be true.")

    required = required_confirmations_for_transition(request)
    missing = tuple(sorted(required.difference(request.required_confirmations)))
    for confirmation in missing:
        blockers.append(f"missing confirmation: {confirmation}.")

    if request.requested_status == "approved_investable":
        warnings.append("manual approval required before any local registry copy may be updated.")

    return AssetStatusValidationResult(
        request=request,
        valid=not blockers,
        allowed_transition=allowed_transition,
        missing_confirmations=missing,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def validate_asset_status_requests(
    requests: list[AssetStatusChangeRequest],
) -> list[AssetStatusValidationResult]:
    return [validate_asset_status_request(request) for request in requests]


def write_updated_registry_copy(
    registry_path: str | Path,
    request: AssetStatusChangeRequest,
    output_path: str | Path,
) -> Path:
    """Write a local registry copy with one status change after explicit caller request."""
    result = validate_asset_status_request(request)
    if not result.valid:
        raise AssetStatusWorkflowError("invalid asset status request cannot update a registry copy.")
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or not isinstance(registry.get("assets"), list):
        raise AssetStatusWorkflowError("registry must contain an assets list.")
    updated = False
    for asset in registry["assets"]:
        if isinstance(asset, dict) and asset.get("asset_id") == request.asset_id:
            if asset.get("approval_status") != request.current_status:
                raise AssetStatusWorkflowError("registry current status does not match request current_status.")
            asset["approval_status"] = request.requested_status
            updated = True
            break
    if not updated:
        raise AssetStatusWorkflowError(f"asset_id {request.asset_id} not found in registry.")
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    return target
