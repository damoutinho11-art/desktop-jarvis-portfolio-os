"""J.A.R.V.I.S. v134.0 post-app acceptance gate.

This gate verifies the local app is complete for manual use after the launcher,
holdings workflow, dashboard/API integration, and user runbook stages.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.daily_operator import build_daily_operator_result
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.manual_holdings_update import (
    DEFAULT_MANUAL_HOLDINGS_PATH,
    MANUAL_SOURCE,
    build_manual_holdings_template,
    build_manual_holdings_update_result,
)
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.user_runbook import build_user_runbook_result

STATUS_READY = "JARVIS_V134_0_POST_APP_ACCEPTANCE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V134_0_POST_APP_ACCEPTANCE_GATE_REVIEW_REQUIRED_SAFE"
MISSING_HOLDINGS_PROBE_PATH = "jarvis/local/__jarvis_v134_missing_holdings_probe.local.json"


@dataclass(frozen=True)
class PostAppAcceptanceGateResult:
    status: str
    current_date: str
    post_app_acceptance_ready: bool
    daily_operator_ready: bool
    launcher_files_exist: bool
    final_product_acceptance_ready: bool
    dashboard_ready: bool
    holdings_workflow_ready: bool
    holdings_missing_handled_safely: bool
    product_api_includes_holdings: bool
    dashboard_includes_holdings: bool
    user_runbook_ready: bool
    safety_check_blocks_execution: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _launcher_files_exist() -> bool:
    return Path("Start Jarvis.bat").exists() and Path("Start-Jarvis.ps1").exists()


def _holdings_workflow_installed(current_date: str) -> tuple[bool, dict[str, Any]]:
    template = build_manual_holdings_template(current_date=current_date)
    symbols = {str(item.get("symbol")) for item in template.get("positions", []) if isinstance(item, Mapping)}
    ready = bool(
        template.get("manual_only") is True
        and template.get("source") == MANUAL_SOURCE
        and template.get("is_template") is True
        and template.get("holdings_confirmed") is False
        and {"BTC", "ETH", "VWCE", "IS3Q.DE", "MSFT"}.issubset(symbols)
    )
    return ready, {"template_symbols": sorted(symbols), "manual_only": template.get("manual_only"), "source": template.get("source")}


def _missing_holdings_safe(current_date: str, missing_probe_path: str | Path) -> tuple[bool, dict[str, Any]]:
    path = Path(missing_probe_path)
    if path.exists():
        return False, {
            "status": "probe_path_exists",
            "file_exists": True,
            "blockers": ["missing_holdings_probe_path_should_not_exist"],
        }
    result = build_manual_holdings_update_result(current_date=current_date, holdings_path=path)
    data = result.to_dict()
    safe = bool(
        result.status == "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE"
        and not result.file_exists
        and not result.holdings_ready
        and result.blockers == []
        and not result.safety_flags.get("order_created")
        and not result.safety_flags.get("trade_executed")
    )
    return safe, data


def _safety_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def build_post_app_acceptance_gate_result(
    *,
    current_date: str = "2026-06-20",
    manual_holdings_path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
    missing_holdings_probe_path: str | Path = MISSING_HOLDINGS_PROBE_PATH,
) -> PostAppAcceptanceGateResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "post-app acceptance is read-only and creates no broker, credential, order, trade, or auto-approval path",
        "missing holdings remain a review note, not a blocker for daily manual use",
    ]

    daily = build_daily_operator_result(
        current_date=current_date,
        refresh_quotes=False,
        write_dashboard=False,
        manual_holdings_path=manual_holdings_path,
    )
    daily_data = _plain(daily)
    daily_ready = bool(daily_data.get("daily_operator_ready"))
    if not daily_ready:
        blockers.append("daily_operator_not_ready")

    launcher_ready = _launcher_files_exist()
    if not launcher_ready:
        blockers.append("launcher_files_missing")

    final_ready = bool(daily_data.get("final_acceptance_ready"))
    if not final_ready:
        blockers.append("final_product_acceptance_not_ready")

    dashboard_status = str((daily_data.get("proof") or {}).get("dashboard_status") or "")
    dashboard_ready_from_daily = "READY_SAFE" in dashboard_status
    if not dashboard_ready_from_daily:
        blockers.append("dashboard_not_ready")

    holdings_workflow_ready, holdings_workflow_proof = _holdings_workflow_installed(current_date)
    if not holdings_workflow_ready:
        blockers.append("holdings_workflow_not_ready")

    holdings_missing_safe, missing_holdings_proof = _missing_holdings_safe(
        current_date, missing_holdings_probe_path
    )
    if not holdings_missing_safe:
        blockers.append("missing_holdings_not_handled_safely")

    product_api = build_product_api_result(
        current_date=current_date,
        manual_holdings_path=manual_holdings_path,
    )
    product_api_data = _plain(product_api)
    product_holdings = product_api_data.get("manual_holdings")
    product_includes_holdings = isinstance(product_holdings, Mapping) and "status" in product_holdings
    if not product_includes_holdings:
        blockers.append("product_api_missing_holdings_status")

    dashboard = build_dashboard_contract_result(
        current_date=current_date,
        manual_holdings_path=manual_holdings_path,
    )
    dashboard_data = _plain(dashboard)
    dashboard_sections = dashboard_data.get("sections") or {}
    dashboard_includes_holdings = isinstance(dashboard_sections, Mapping) and isinstance(
        dashboard_sections.get("manual_holdings"), Mapping
    )
    dashboard_ready = bool(dashboard_data.get("dashboard_contract_ready")) and dashboard_includes_holdings
    if not dashboard_ready:
        blockers.append("dashboard_missing_holdings_status")

    runbook = build_user_runbook_result(current_date=current_date)
    runbook_data = _plain(runbook)
    runbook_ready = bool(runbook_data.get("runbook_ready"))
    if not runbook_ready:
        blockers.append("user_runbook_not_ready")

    safety_ready = _safety_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    blockers = _dedupe(blockers)
    ready = not blockers

    return PostAppAcceptanceGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        post_app_acceptance_ready=ready,
        daily_operator_ready=daily_ready,
        launcher_files_exist=launcher_ready,
        final_product_acceptance_ready=final_ready,
        dashboard_ready=dashboard_ready,
        holdings_workflow_ready=holdings_workflow_ready,
        holdings_missing_handled_safely=holdings_missing_safe,
        product_api_includes_holdings=product_includes_holdings,
        dashboard_includes_holdings=dashboard_includes_holdings,
        user_runbook_ready=runbook_ready,
        safety_check_blocks_execution=safety_ready,
        blockers=blockers,
        warnings=_dedupe(warnings),
        proof={
            "daily_operator_status": daily_data.get("status"),
            "final_acceptance_ready": final_ready,
            "dashboard_status": dashboard_status,
            "daily_holdings_status": (daily_data.get("proof") or {}).get("holdings_status"),
            "holdings_workflow": holdings_workflow_proof,
            "missing_holdings_status": missing_holdings_proof.get("status"),
            "missing_holdings_file_exists": missing_holdings_proof.get("file_exists"),
            "product_api_status": product_api_data.get("status"),
            "product_api_holdings_status": product_holdings.get("status") if isinstance(product_holdings, Mapping) else None,
            "dashboard_contract_status": dashboard_data.get("status"),
            "dashboard_holdings_title": (dashboard_sections.get("manual_holdings") or {}).get("title")
            if isinstance(dashboard_sections, Mapping)
            else None,
            "runbook_status": runbook_data.get("status"),
            "safety_blocked": safety_ready,
        },
    )


def format_post_app_acceptance_gate(result: PostAppAcceptanceGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. POST-APP ACCEPTANCE GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"post-app acceptance ready: {result.post_app_acceptance_ready}",
        "",
        "CHECKS:",
        f"- daily operator ready: {result.daily_operator_ready}",
        f"- launcher files exist: {result.launcher_files_exist}",
        f"- final product acceptance ready: {result.final_product_acceptance_ready}",
        f"- dashboard ready: {result.dashboard_ready}",
        f"- holdings workflow ready: {result.holdings_workflow_ready}",
        f"- holdings missing handled safely: {result.holdings_missing_handled_safely}",
        f"- product API includes holdings: {result.product_api_includes_holdings}",
        f"- dashboard includes holdings: {result.dashboard_includes_holdings}",
        f"- user runbook ready: {result.user_runbook_ready}",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        "",
        "PROOF:",
        f"- daily operator status: {result.proof.get('daily_operator_status')}",
        f"- dashboard status: {result.proof.get('dashboard_status')}",
        f"- daily holdings status: {result.proof.get('daily_holdings_status')}",
        f"- missing holdings status: {result.proof.get('missing_holdings_status')}",
        f"- product API holdings status: {result.proof.get('product_api_holdings_status')}",
        f"- dashboard holdings title: {result.proof.get('dashboard_holdings_title')}",
        f"- runbook status: {result.proof.get('runbook_status')}",
        f"- safety blocked: {result.proof.get('safety_blocked')}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
        "",
        "Safety: read-only and manual-only. Diogo buys outside J.A.R.V.I.S.; no broker, credential, order, trade, or auto-approval path is enabled.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. post-app acceptance gate.")
    parser.add_argument("--post-app-acceptance-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--holdings-path", default=DEFAULT_MANUAL_HOLDINGS_PATH)
    parser.add_argument("--missing-holdings-probe-path", default=MISSING_HOLDINGS_PROBE_PATH)
    args = parser.parse_args(argv)

    result = build_post_app_acceptance_gate_result(
        current_date=args.current_date,
        manual_holdings_path=args.holdings_path,
        missing_holdings_probe_path=args.missing_holdings_probe_path,
    )
    print(format_post_app_acceptance_gate(result))
    return 0 if result.post_app_acceptance_ready else 1


__all__ = [
    "MISSING_HOLDINGS_PROBE_PATH",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "PostAppAcceptanceGateResult",
    "build_post_app_acceptance_gate_result",
    "format_post_app_acceptance_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
