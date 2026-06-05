"""Audit packs for generated asset status request previews."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .asset_registry import load_asset_registry
from .asset_status_workflow import AssetStatusChangeRequest, validate_asset_status_request
from .universe_status_bridge import UniverseStatusBridgeResult, load_review_and_bridge


@dataclass(frozen=True)
class StatusRequestAuditPack:
    request_id: str
    asset_id: str
    asset_type: str
    sleeve: str
    current_status: str
    requested_status: str
    transition_allowed: bool
    validation_status: str
    evidence_summary: str
    required_confirmations: tuple[str, ...]
    missing_confirmations: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    auto_execute: bool
    registry_mutation_allowed: bool
    audit_ready: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "current_status": self.current_status,
            "requested_status": self.requested_status,
            "transition_allowed": self.transition_allowed,
            "validation_status": self.validation_status,
            "evidence_summary": self.evidence_summary,
            "required_confirmations": list(self.required_confirmations),
            "missing_confirmations": list(self.missing_confirmations),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "auto_execute": self.auto_execute,
            "registry_mutation_allowed": self.registry_mutation_allowed,
            "audit_ready": self.audit_ready,
        }


@dataclass(frozen=True)
class StatusRequestAuditSummary:
    total_status_request_previews: int
    audit_ready_count: int
    blocked_count: int
    by_requested_status: dict[str, int]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    registry_mutation_forbidden: bool = True


@dataclass(frozen=True)
class StatusRequestAuditResult:
    status: str
    audit_packs: tuple[StatusRequestAuditPack, ...]
    summary: StatusRequestAuditSummary
    manual_approval_required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "audit_packs": [pack.to_dict() for pack in self.audit_packs],
            "summary": {
                "total_status_request_previews": self.summary.total_status_request_previews,
                "audit_ready_count": self.summary.audit_ready_count,
                "blocked_count": self.summary.blocked_count,
                "by_requested_status": self.summary.by_requested_status,
                "warnings": list(self.summary.warnings),
                "blockers": list(self.summary.blockers),
                "registry_mutation_forbidden": self.summary.registry_mutation_forbidden,
            },
            "manual_approval_required": self.manual_approval_required,
        }


def _safe_transition_blockers(request: AssetStatusChangeRequest) -> list[str]:
    blockers: list[str] = []
    if request.requested_status == "approved_investable":
        if request.current_status != "approved_watchlist":
            blockers.append(f"{request.current_status} -> approved_investable is not allowed by audit policy.")
        if request.current_status in {"candidate_unreviewed", "test_position", "rejected"}:
            blockers.append(f"direct {request.current_status} -> approved_investable is forbidden.")
    return blockers


def _asset_sleeve_lookup(registry_path: str | Path) -> dict[str, str]:
    registry = load_asset_registry(registry_path)
    return {asset.asset_id: asset.sleeve for asset in registry.assets}


def audit_status_request(
    request: AssetStatusChangeRequest,
    sleeve: str = "unknown",
) -> StatusRequestAuditPack:
    validation = validate_asset_status_request(request)
    blockers = [*validation.blockers, *_safe_transition_blockers(request)]
    if not request.manual_approval_required:
        blockers.append("manual_approval_required must be true.")
    if request.auto_execute:
        blockers.append("auto_execute must always be false.")
    audit_ready = (
        validation.valid
        and request.manual_approval_required
        and not request.auto_execute
        and not validation.missing_confirmations
        and not _safe_transition_blockers(request)
    )
    return StatusRequestAuditPack(
        request_id=request.request_id,
        asset_id=request.asset_id,
        asset_type=request.asset_type,
        sleeve=sleeve,
        current_status=request.current_status,
        requested_status=request.requested_status,
        transition_allowed=validation.allowed_transition,
        validation_status="valid" if audit_ready else "blocked",
        evidence_summary=request.evidence_summary,
        required_confirmations=request.required_confirmations,
        missing_confirmations=validation.missing_confirmations,
        warnings=validation.warnings,
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=request.manual_approval_required,
        auto_execute=request.auto_execute,
        registry_mutation_allowed=False,
        audit_ready=audit_ready,
    )


def audit_status_bridge_result(
    bridge_result: UniverseStatusBridgeResult,
    registry_path: str | Path,
) -> StatusRequestAuditResult:
    sleeve_lookup = _asset_sleeve_lookup(registry_path)
    packs = tuple(
        audit_status_request(request, sleeve_lookup.get(request.asset_id, "unknown"))
        for request in bridge_result.status_requests
    )
    by_requested_status: dict[str, int] = {}
    for pack in packs:
        by_requested_status[pack.requested_status] = by_requested_status.get(pack.requested_status, 0) + 1
    warnings = [*bridge_result.warnings]
    warnings.extend(warning for pack in packs for warning in pack.warnings)
    blockers = [*bridge_result.blockers]
    blockers.extend(blocker for pack in packs for blocker in pack.blockers)
    summary = StatusRequestAuditSummary(
        total_status_request_previews=len(packs),
        audit_ready_count=sum(pack.audit_ready for pack in packs),
        blocked_count=sum(not pack.audit_ready for pack in packs),
        by_requested_status=dict(sorted(by_requested_status.items())),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        registry_mutation_forbidden=True,
    )
    return StatusRequestAuditResult(
        status="AUDIT_READY" if packs and summary.blocked_count == 0 else "BLOCKED",
        audit_packs=packs,
        summary=summary,
        manual_approval_required=True,
    )


def build_status_request_audit(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> StatusRequestAuditResult:
    bridge_result = load_review_and_bridge(registry_path, market_data_path, exposure_path, policy_path)
    return audit_status_bridge_result(bridge_result, registry_path)
