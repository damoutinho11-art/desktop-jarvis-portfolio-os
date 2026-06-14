"""Dynamic portfolio command-center audit for J.A.R.V.I.S.

Final report-only audit for the local dynamic portfolio command center.
No fetching, broker integration, registry mutation, approval, buy request, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_operator_status_dashboard import (
    STATUS_READY as DASHBOARD_READY,
    build_dynamic_operator_status,
)


STATUS_READY = "DYNAMIC_COMMAND_CENTER_AUDIT_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_COMMAND_CENTER_AUDIT_BLOCKED_SAFE"


REQUIRED_COMMANDS = (
    "python -m jarvis.dynamic_market_source_binding_report",
    "python -m jarvis.dynamic_market_import_plan_report",
    "python -m jarvis.dynamic_bound_market_coverage_report",
    "python -m jarvis.dynamic_market_coverage_audit_report",
    "python -m jarvis.dynamic_allocation_optimizer_report",
    "python -m jarvis.dynamic_allocation_weekly_plan_report",
    "python -m jarvis.dynamic_portfolio_preflight_report",
    "python -m jarvis.dynamic_operator_status_dashboard_report",
)


@dataclass(frozen=True)
class DynamicCommandCenterAuditResult:
    status: str
    dashboard_status: str
    horizon: str
    required_command_count: int
    ready_status_count: int
    required_commands: tuple[str, ...]
    chain_statuses: dict[str, str]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    fetching_forbidden: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dashboard_status": self.dashboard_status,
            "horizon": self.horizon,
            "required_command_count": self.required_command_count,
            "ready_status_count": self.ready_status_count,
            "required_commands": list(self.required_commands),
            "chain_statuses": dict(self.chain_statuses),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "fetching_forbidden": self.fetching_forbidden,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def audit_dynamic_command_center(
    horizon: str,
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    binding_path: str | Path,
    market_data_path: str | Path,
) -> DynamicCommandCenterAuditResult:
    dashboard = build_dynamic_operator_status(
        horizon=horizon,
        plan_path=plan_path,
        snapshot_path=snapshot_path,
        policy_path=policy_path,
        registry_path=registry_path,
        binding_path=binding_path,
        market_data_path=market_data_path,
    )

    chain_statuses = {
        "market_import_plan": dashboard.import_plan_status,
        "portfolio_preflight": dashboard.preflight_status,
        "bound_market_coverage": dashboard.bound_market_status,
        "source_binding": dashboard.binding_status,
        "market_coverage": dashboard.coverage_status,
        "optimizer": dashboard.optimizer_status,
        "weekly_plan": dashboard.weekly_plan_status,
        "contribution": dashboard.contribution_status,
    }

    ready_statuses = {
        "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE",
        "DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE",
        "DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE",
        "DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE",
        "DYNAMIC_MARKET_COVERAGE_READY_SAFE",
        "DYNAMIC_POLICY_READY_SAFE",
        "DYNAMIC_WEEKLY_PLAN_READY_SAFE",
        "DRAFT_PLAN",
    }

    ready_count = sum(1 for status in chain_statuses.values() if status in ready_statuses)
    blockers = list(dashboard.blockers)

    if dashboard.status != DASHBOARD_READY:
        blockers.append(f"operator dashboard is not ready: {dashboard.status}")
    if ready_count != len(chain_statuses):
        blockers.append("not all command-center chain statuses are ready.")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicCommandCenterAuditResult(
        status=status,
        dashboard_status=dashboard.status,
        horizon=horizon,
        required_command_count=len(REQUIRED_COMMANDS),
        ready_status_count=ready_count,
        required_commands=REQUIRED_COMMANDS,
        chain_statuses=chain_statuses,
        warnings=dashboard.warnings,
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        fetching_forbidden=True,
        execution_forbidden=True,
    )
