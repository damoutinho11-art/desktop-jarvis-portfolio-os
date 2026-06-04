"""Manual approval workflow for local proposed actions only."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .approval_schema import (
    ALLOWED_ACTION_TYPES,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalSchemaError,
    ApprovalValidationResult,
    parse_approval_request,
)
from .decision_logger import append_decision_record


INVESTMENT_ACCOUNT_IDS = {
    "lhv_crypto_investments",
    "lhv_growth",
    "lightyear",
    "kraken",
}
EMERGENCY_ACCOUNT_IDS = {"emergency_fund", "emergency_reserve"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_approval_requests(path: str | Path) -> list[ApprovalRequest]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ApprovalSchemaError("approval requests fixture must be an object.")
    requests = raw.get("requests")
    if not isinstance(requests, list):
        raise ApprovalSchemaError("approval requests fixture must contain a requests list.")
    parsed = [parse_approval_request(item) for item in requests]
    seen_ids: set[str] = set()
    for request in parsed:
        if request.request_id in seen_ids:
            raise ApprovalSchemaError(f"duplicate request_id {request.request_id}.")
        seen_ids.add(request.request_id)
    return parsed


def validate_approval_request(request: ApprovalRequest) -> ApprovalValidationResult:
    blockers: list[str] = []
    warnings: list[str] = []
    confirmations = set(request.required_confirmations)

    if request.action_type not in ALLOWED_ACTION_TYPES:
        blockers.append(f"action_type {request.action_type} is not allowed.")
    if request.auto_execute:
        blockers.append("auto_execute must always be false.")
    if not request.manual_approval_required:
        blockers.append("manual_approval_required must always be true.")
    if request.status == "executed_manually":
        blockers.append("executed_manually cannot be created directly without prior approved status.")

    if request.action_type == "buy":
        if not request.asset_id:
            blockers.append("buy action requires asset_id.")
        if request.amount_eur is None or request.amount_eur <= 0:
            blockers.append("buy action requires amount_eur > 0.")
        if not request.platform:
            blockers.append("buy action requires platform.")
        if not request.rationale:
            blockers.append("buy action requires rationale.")

    if request.action_type == "sell":
        if not request.asset_id:
            blockers.append("sell action requires asset_id.")
        if (request.amount_eur is None or request.amount_eur <= 0) and not request.full_position:
            blockers.append("sell action requires amount_eur > 0 or full_position.")
        if not request.platform:
            blockers.append("sell action requires platform.")
        if not request.rationale:
            blockers.append("sell action requires rationale.")
        if "sell_safety_acknowledgement" not in confirmations:
            blockers.append("sell action requires sell_safety_acknowledgement.")

    if (
        request.action_type == "transfer_warning"
        and request.source_account_id in INVESTMENT_ACCOUNT_IDS
        and "investment_account_tax_warning_acknowledged" not in confirmations
    ):
        blockers.append("investment-account withdrawal requires investment_account_tax_warning_acknowledged.")

    emergency_involved = (
        request.source_account_id in EMERGENCY_ACCOUNT_IDS
        or request.destination_account_id in EMERGENCY_ACCOUNT_IDS
        or request.asset_id in EMERGENCY_ACCOUNT_IDS
    )
    if emergency_involved:
        if "emergency_fund_override_acknowledged" not in confirmations:
            blockers.append("emergency reserve usage requires emergency_fund_override_acknowledged.")
        else:
            warnings.append("high-risk warning: emergency reserve usage was explicitly acknowledged.")

    if request.action_type in {"buy", "sell"} and (
        "crypto_swap_pair" in confirmations or "swap" in request.rationale.lower()
    ):
        warnings.append("crypto_tax_event_possible.")

    valid = not blockers
    return ApprovalValidationResult(
        request=request,
        valid=valid,
        effective_status=request.status if valid else "blocked",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def validate_approval_requests(requests: list[ApprovalRequest]) -> list[ApprovalValidationResult]:
    return [validate_approval_request(request) for request in requests]


def approve_request(
    request: ApprovalRequest,
    decided_by: str,
    notes: str = "",
    log_path: str | Path | None = None,
) -> tuple[ApprovalRequest, ApprovalDecision]:
    validation = validate_approval_request(request)
    if request.status != "pending_manual_approval":
        raise ApprovalSchemaError("only pending_manual_approval requests can be approved.")
    if not validation.valid:
        raise ApprovalSchemaError("blocked requests cannot be approved.")
    approved_request = replace(request, status="approved", auto_execute=False, manual_approval_required=True)
    decision = ApprovalDecision(request.request_id, "approved", _now_iso(), decided_by, notes)
    record = {
        "request_id": decision.request_id,
        "decision": decision.decision,
        "decided_at": decision.decided_at,
        "decided_by": decision.decided_by,
        "notes": decision.notes,
        "status": approved_request.status,
        "auto_execute": approved_request.auto_execute,
        "trades_executed": False,
    }
    append_decision_record(record, log_path) if log_path else append_decision_record(record)
    return approved_request, decision


def reject_request(
    request: ApprovalRequest,
    decided_by: str,
    notes: str = "",
    log_path: str | Path | None = None,
) -> tuple[ApprovalRequest, ApprovalDecision]:
    if request.status != "pending_manual_approval":
        raise ApprovalSchemaError("only pending_manual_approval requests can be rejected.")
    rejected_request = replace(request, status="rejected", auto_execute=False, manual_approval_required=True)
    decision = ApprovalDecision(request.request_id, "rejected", _now_iso(), decided_by, notes)
    record = {
        "request_id": decision.request_id,
        "decision": decision.decision,
        "decided_at": decision.decided_at,
        "decided_by": decision.decided_by,
        "notes": decision.notes,
        "status": rejected_request.status,
        "auto_execute": rejected_request.auto_execute,
        "trades_executed": False,
    }
    append_decision_record(record, log_path) if log_path else append_decision_record(record)
    return rejected_request, decision
