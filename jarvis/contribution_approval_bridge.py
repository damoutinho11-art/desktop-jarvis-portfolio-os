"""Bridge draft contribution plans into pending manual approval requests."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .approval_schema import ApprovalRequest
from .asset_registry import CandidateAsset, load_asset_registry
from .contribution_planner import ContributionPlanResult, PlanLine, load_and_plan_contribution
from .manual_approval_workflow import INVESTMENT_ACCOUNT_IDS, validate_approval_request


BASE_CONFIRMATIONS = (
    "manual_trade_execution_required",
    "platform_checked_before_execution",
    "amount_checked_before_execution",
)
CRYPTO_CONFIRMATIONS = (
    "crypto_tax_risk_acknowledged",
    "crypto_volatility_acknowledged",
)
INVESTMENT_ACCOUNT_CONFIRMATION = "investment_account_tax_rules_acknowledged"


@dataclass(frozen=True)
class BridgeLineResult:
    plan_line: PlanLine
    valid: bool
    blockers: tuple[str, ...]
    approval_request: ApprovalRequest | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_line": self.plan_line.to_dict(),
            "valid": self.valid,
            "blockers": list(self.blockers),
            "approval_request": asdict(self.approval_request) if self.approval_request else None,
        }


@dataclass(frozen=True)
class ContributionApprovalBridgeResult:
    status: str
    approval_requests: tuple[ApprovalRequest, ...]
    blocked_lines: tuple[BridgeLineResult, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "approval_requests": [asdict(request) for request in self.approval_requests],
            "blocked_lines": [line.to_dict() for line in self.blocked_lines],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _asset_lookup(registry_path: str | Path) -> dict[str, CandidateAsset]:
    registry = load_asset_registry(registry_path)
    return {asset.asset_id: asset for asset in registry.assets}


def _required_confirmations_for_line(
    line: PlanLine,
    asset: CandidateAsset | None,
    source_account_id: str | None,
    destination_account_id: str | None,
) -> tuple[str, ...]:
    confirmations = list(BASE_CONFIRMATIONS)
    if asset is not None and asset.asset_type == "crypto":
        confirmations.extend(CRYPTO_CONFIRMATIONS)
    if source_account_id in INVESTMENT_ACCOUNT_IDS or destination_account_id in INVESTMENT_ACCOUNT_IDS:
        confirmations.append(INVESTMENT_ACCOUNT_CONFIRMATION)
    return tuple(dict.fromkeys(confirmations))


def build_approval_request_from_plan_line(
    line: PlanLine,
    asset: CandidateAsset | None = None,
    source_account_id: str | None = None,
    destination_account_id: str | None = None,
    created_at: str | None = None,
) -> ApprovalRequest:
    return ApprovalRequest(
        request_id=f"contribution_{line.sleeve_id}_{line.asset_id}",
        created_at=created_at or _now_iso(),
        action_type="buy",
        asset_id=line.asset_id,
        amount_eur=line.amount_eur,
        source_account_id=source_account_id,
        destination_account_id=destination_account_id,
        platform=line.platform,
        rationale=f"Draft contribution bridge for sleeve {line.sleeve_id}: {line.reason}",
        risks=(
            "draft contribution plan only",
            "manual execution required",
            "no broker connection",
        ),
        required_confirmations=_required_confirmations_for_line(
            line,
            asset,
            source_account_id,
            destination_account_id,
        ),
        status="pending_manual_approval",
        manual_approval_required=True,
        auto_execute=False,
    )


def bridge_contribution_plan(
    plan_result: ContributionPlanResult,
    registry_path: str | Path,
    source_account_id: str | None = None,
    destination_account_id: str | None = None,
) -> ContributionApprovalBridgeResult:
    if plan_result.status == "BLOCKED":
        return ContributionApprovalBridgeResult(
            status="BLOCKED",
            approval_requests=(),
            blocked_lines=(),
            warnings=plan_result.warnings,
            blockers=plan_result.blockers,
            manual_approval_required=plan_result.manual_approval_required,
            execution_forbidden=True,
        )

    assets = _asset_lookup(registry_path)
    valid_requests: list[ApprovalRequest] = []
    blocked_lines: list[BridgeLineResult] = []
    for line in plan_result.plan_lines:
        request = build_approval_request_from_plan_line(
            line,
            assets.get(line.asset_id),
            source_account_id,
            destination_account_id,
        )
        validation = validate_approval_request(request)
        if validation.valid:
            valid_requests.append(request)
        else:
            blocked_lines.append(BridgeLineResult(line, False, validation.blockers, None))

    status = "PENDING_MANUAL_APPROVAL" if valid_requests and not blocked_lines else "BLOCKED"
    return ContributionApprovalBridgeResult(
        status=status,
        approval_requests=tuple(valid_requests),
        blocked_lines=tuple(blocked_lines),
        warnings=plan_result.warnings,
        blockers=tuple(line_blocker for line in blocked_lines for line_blocker in line.blockers),
        manual_approval_required=True,
        execution_forbidden=True,
    )


def load_plan_and_bridge(
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> ContributionApprovalBridgeResult:
    plan_result = load_and_plan_contribution(plan_path, snapshot_path, policy_path, registry_path)
    return bridge_contribution_plan(plan_result, registry_path)


def write_approval_requests(
    bridge_result: ContributionApprovalBridgeResult,
    path: str | Path,
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"requests": [asdict(request) for request in bridge_result.approval_requests]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
