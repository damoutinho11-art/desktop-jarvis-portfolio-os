"""Manual approval schema for local proposed actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


ALLOWED_STATUSES = {
    "draft",
    "pending_manual_approval",
    "approved",
    "rejected",
    "cancelled",
    "expired",
    "executed_manually",
}
ALLOWED_ACTION_TYPES = {
    "buy",
    "sell",
    "hold_cash",
    "asset_status_change",
    "rebalance_note",
    "transfer_warning",
}
ALLOWED_DECISIONS = {"approved", "rejected"}


class ApprovalSchemaError(ValueError):
    """Raised when approval fixture data is malformed."""


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    created_at: str
    action_type: str
    rationale: str
    risks: tuple[str, ...]
    required_confirmations: tuple[str, ...]
    status: str
    manual_approval_required: bool
    auto_execute: bool
    asset_id: str | None = None
    amount_eur: float | None = None
    source_account_id: str | None = None
    destination_account_id: str | None = None
    platform: str | None = None
    full_position: bool = False


@dataclass(frozen=True)
class ApprovalDecision:
    request_id: str
    decision: str
    decided_at: str
    decided_by: str
    notes: str = ""

    def __post_init__(self) -> None:
        if self.decision not in ALLOWED_DECISIONS:
            raise ApprovalSchemaError(f"decision {self.decision} is not allowed.")


@dataclass(frozen=True)
class ApprovalValidationResult:
    request: ApprovalRequest
    valid: bool
    effective_status: str
    blockers: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ApprovalSchemaError(f"{field} exists and must be text.")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field)


def _optional_amount(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ApprovalSchemaError(f"{field} must be a number.")
    return float(value)


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ApprovalSchemaError(f"{field} must be true or false.")
    return value


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ApprovalSchemaError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def _validate_timestamp(value: str, field: str) -> str:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApprovalSchemaError(f"{field} must be ISO-like datetime text.") from exc
    return value


def parse_approval_request(raw: dict[str, Any]) -> ApprovalRequest:
    if not isinstance(raw, dict):
        raise ApprovalSchemaError("approval request must be an object.")
    request = ApprovalRequest(
        request_id=_require_text(raw.get("request_id"), "request_id"),
        created_at=_validate_timestamp(_require_text(raw.get("created_at"), "created_at"), "created_at"),
        action_type=_require_text(raw.get("action_type"), "action_type"),
        asset_id=_optional_text(raw.get("asset_id"), "asset_id"),
        amount_eur=_optional_amount(raw.get("amount_eur"), "amount_eur"),
        source_account_id=_optional_text(raw.get("source_account_id"), "source_account_id"),
        destination_account_id=_optional_text(raw.get("destination_account_id"), "destination_account_id"),
        platform=_optional_text(raw.get("platform"), "platform"),
        rationale=_require_text(raw.get("rationale"), "rationale"),
        risks=_require_text_list(raw.get("risks", []), "risks"),
        required_confirmations=_require_text_list(
            raw.get("required_confirmations", []),
            "required_confirmations",
        ),
        status=_require_text(raw.get("status"), "status"),
        manual_approval_required=_require_bool(raw.get("manual_approval_required"), "manual_approval_required"),
        auto_execute=_require_bool(raw.get("auto_execute"), "auto_execute"),
        full_position=bool(raw.get("full_position", False)),
    )
    if request.status not in ALLOWED_STATUSES:
        raise ApprovalSchemaError(f"status {request.status} is not allowed.")
    return request
