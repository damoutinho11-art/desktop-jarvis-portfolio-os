"""Dynamic operator status dashboard for J.A.R.V.I.S. Portfolio OS.

Report-only status index. Aggregates existing dynamic portfolio checks.
No fetching, broker integration, approval, registry mutation, buy request, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_market_data_intake_validator import validate_dynamic_market_data_intake
from .dynamic_market_import_plan import build_dynamic_market_import_plan
from .dynamic_portfolio_preflight import run_dynamic_portfolio_preflight
from .dynamic_public_data_fetcher_adapter import build_dynamic_public_data_fetcher_adapter


STATUS_READY = "DYNAMIC_OPERATOR_STATUS_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_OPERATOR_STATUS_BLOCKED_SAFE"
DEFAULT_ENDPOINT_PATH = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


@dataclass(frozen=True)
class DynamicOperatorStatusResult:
    status: str
    horizon: str
    preflight_status: str
    import_plan_status: str
    public_data_fetcher_adapter_status: str
    market_data_intake_status: str
    bound_market_status: str
    binding_status: str
    coverage_status: str
    optimizer_status: str
    weekly_plan_status: str
    contribution_status: str
    import_ready_rows: int
    adapted_source_count: int
    intake_ready_series_count: int
    weekly_plan_line_count: int
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool
    fetching_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "horizon": self.horizon,
            "preflight_status": self.preflight_status,
            "import_plan_status": self.import_plan_status,
            "public_data_fetcher_adapter_status": self.public_data_fetcher_adapter_status,
            "market_data_intake_status": self.market_data_intake_status,
            "bound_market_status": self.bound_market_status,
            "binding_status": self.binding_status,
            "coverage_status": self.coverage_status,
            "optimizer_status": self.optimizer_status,
            "weekly_plan_status": self.weekly_plan_status,
            "contribution_status": self.contribution_status,
            "import_ready_rows": self.import_ready_rows,
            "adapted_source_count": self.adapted_source_count,
            "intake_ready_series_count": self.intake_ready_series_count,
            "weekly_plan_line_count": self.weekly_plan_line_count,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "fetching_forbidden": self.fetching_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def build_dynamic_operator_status(
    horizon: str,
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    binding_path: str | Path,
    market_data_path: str | Path,
    endpoint_path: str | Path = DEFAULT_ENDPOINT_PATH,
) -> DynamicOperatorStatusResult:
    import_result = build_dynamic_market_import_plan(registry_path, binding_path)
    adapter_result = build_dynamic_public_data_fetcher_adapter(registry_path, binding_path, endpoint_path)
    intake_result = validate_dynamic_market_data_intake(registry_path, binding_path, market_data_path)
    preflight_result = run_dynamic_portfolio_preflight(
        horizon=horizon,
        plan_path=plan_path,
        snapshot_path=snapshot_path,
        policy_path=policy_path,
        registry_path=registry_path,
        binding_path=binding_path,
        market_data_path=market_data_path,
    )

    warnings = tuple(
        dict.fromkeys(
            import_result.warnings
            + adapter_result.warnings
            + intake_result.warnings
            + preflight_result.warnings
        )
    )
    blockers = tuple(
        dict.fromkeys(
            import_result.blockers
            + adapter_result.blockers
            + intake_result.blockers
            + preflight_result.blockers
        )
    )

    if import_result.status != "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE":
        blockers = tuple(dict.fromkeys(blockers + (f"import plan is not ready: {import_result.status}",)))
    if adapter_result.status != "DYNAMIC_PUBLIC_DATA_FETCHER_ADAPTER_READY_SAFE":
        blockers = tuple(dict.fromkeys(blockers + (f"public data fetcher adapter is not ready: {adapter_result.status}",)))
    if intake_result.status != "DYNAMIC_MARKET_DATA_INTAKE_READY_SAFE":
        blockers = tuple(dict.fromkeys(blockers + (f"market data intake is not ready: {intake_result.status}",)))
    if preflight_result.status != "DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE":
        blockers = tuple(dict.fromkeys(blockers + (f"preflight is not ready: {preflight_result.status}",)))

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicOperatorStatusResult(
        status=status,
        horizon=horizon,
        preflight_status=preflight_result.status,
        import_plan_status=import_result.status,
        public_data_fetcher_adapter_status=adapter_result.status,
        market_data_intake_status=intake_result.status,
        bound_market_status=preflight_result.bound_market_status,
        binding_status=preflight_result.binding_status,
        coverage_status=preflight_result.coverage_status,
        optimizer_status=preflight_result.optimizer_status,
        weekly_plan_status=preflight_result.weekly_plan_status,
        contribution_status=preflight_result.contribution_status,
        import_ready_rows=import_result.ready_row_count,
        adapted_source_count=adapter_result.adapted_source_count,
        intake_ready_series_count=intake_result.ready_series_count,
        weekly_plan_line_count=len(preflight_result.weekly_plan_lines),
        warnings=warnings,
        blockers=blockers,
        manual_approval_required=True,
        execution_forbidden=True,
        fetching_forbidden=True,
    )
