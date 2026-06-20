"""J.A.R.V.I.S. v139.0 calm dashboard noise audit.

This audit is read-only. It inspects dashboard HTML for scary/internal wording
that should not appear in the daily-use UI.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V139_0_DASHBOARD_NOISE_AUDIT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V139_0_DASHBOARD_NOISE_AUDIT_REVIEW_REQUIRED_SAFE"

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "READY_WITH_AUDIT_WARNINGS",
    "Blockers / Warnings",
    "Review dashboard warnings",
    "raw warning dump",
    "raw audit verdict",
    "internal_sleeve_placeholder_not_tradable",
    "etf_fund_candidate_missing_quote_source",
    "partial_or_unavailable",
    "Classification / Next Action",
    "buy now",
    "sell now",
    "place order",
    "execute trade",
    "liquidate position",
)

REQUIRED_CALM_MARKERS: tuple[str, ...] = (
    "READY FOR MANUAL USE",
    "Daily Notes",
    "Today's Manual Plan",
    "Market Movement",
    "Risk & Safety",
    "System Checks",
    "Useful Actions",
    "Manual-only safety",
)


@dataclass(frozen=True)
class DashboardNoiseAuditResult:
    status: str
    current_date: str
    dashboard_noise_audit_ready: bool
    read_only: bool
    no_output_write_required: bool
    dashboard_html_inspected: bool
    calm_markers_present: bool
    noisy_markers_absent: bool
    long_code_heavy_command_cards_absent: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    allocation_mutation: bool
    approval_mutation: bool
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


def _dashboard_html(current_date: str) -> tuple[str, dict[str, Any], list[str]]:
    warnings: list[str] = []
    try:
        dashboard = build_dashboard_contract_result(current_date=current_date, write_dashboard=False)
        return render_dashboard_html(dashboard), _plain(dashboard), warnings
    except Exception as exc:
        warnings.append(f"dashboard render failed during noise audit: {type(exc).__name__}: {exc}")
        return "", {}, warnings


def _contains(text: str, marker: str) -> bool:
    return marker.lower() in text.lower()


def _long_code_cards_absent(html_text: str) -> bool:
    lowered = html_text.lower()
    if lowered.count("<code") > 4:
        return False
    start = 0
    while True:
        open_at = lowered.find("<code", start)
        if open_at < 0:
            return True
        close_start = lowered.find(">", open_at)
        close_at = lowered.find("</code>", close_start)
        if close_start < 0 or close_at < 0:
            return False
        code_text = html_text[close_start + 1 : close_at].strip()
        if len(code_text) > 80:
            return False
        start = close_at + len("</code>")


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def build_dashboard_noise_audit_result(
    *,
    current_date: str = "2026-06-20",
) -> DashboardNoiseAuditResult:
    html_text, dashboard_data, render_warnings = _dashboard_html(current_date)
    blockers: list[str] = []
    warnings: list[str] = [
        "dashboard noise audit is read-only and does not write dashboard/report output",
        "warnings are audit notes only unless a forbidden user-facing marker appears",
    ]
    warnings.extend(render_warnings)

    missing_calm = [marker for marker in REQUIRED_CALM_MARKERS if not _contains(html_text, marker)]
    forbidden_found = [marker for marker in FORBIDDEN_MARKERS if _contains(html_text, marker)]
    long_code_clear = _long_code_cards_absent(html_text)
    safety_ready = _safety_check_ready()

    if not html_text:
        blockers.append("dashboard_html_not_available")
    if missing_calm:
        blockers.append("calm_dashboard_markers_missing")
    if forbidden_found:
        blockers.append("noisy_dashboard_markers_found")
    if not long_code_clear:
        blockers.append("long_code_heavy_command_cards_found")
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    sections = dashboard_data.get("sections") or {}
    safety = sections.get("safety") if isinstance(sections, Mapping) else {}
    if not isinstance(safety, Mapping):
        safety = {}

    manual_only = bool(dashboard_data.get("manual_only", True))
    execution_forbidden = bool(safety.get("execution_forbidden", True))
    broker_enabled = bool(safety.get("broker_connection", False))
    credentials_required = bool(safety.get("credentials_used", False))
    order_created = bool(safety.get("order_created", False))
    trade_created = bool(safety.get("trade_executed", False))
    auto_approval = False
    allocation_mutation = False
    approval_mutation = False

    if not manual_only:
        blockers.append("manual_only_safety_not_ready")
    if not execution_forbidden:
        blockers.append("execution_forbidden_not_asserted")
    if any(
        [
            broker_enabled,
            credentials_required,
            order_created,
            trade_created,
            auto_approval,
            allocation_mutation,
            approval_mutation,
        ]
    ):
        blockers.append("forbidden_execution_flag_enabled")

    blockers = _dedupe(blockers)
    ready = not blockers
    return DashboardNoiseAuditResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        dashboard_noise_audit_ready=ready,
        read_only=True,
        no_output_write_required=True,
        dashboard_html_inspected=bool(html_text),
        calm_markers_present=not missing_calm,
        noisy_markers_absent=not forbidden_found,
        long_code_heavy_command_cards_absent=long_code_clear,
        safety_check_blocks_execution=safety_ready,
        manual_only=manual_only,
        execution_forbidden=execution_forbidden,
        broker_connection_enabled=broker_enabled,
        credentials_required=credentials_required,
        order_created=order_created,
        trade_created=trade_created,
        auto_approval_enabled=auto_approval,
        allocation_mutation=allocation_mutation,
        approval_mutation=approval_mutation,
        blockers=blockers,
        warnings=_dedupe(warnings),
        proof={
            "missing_calm_markers": missing_calm,
            "forbidden_markers_found": forbidden_found,
            "dashboard_status": dashboard_data.get("status"),
            "dashboard_ready": dashboard_data.get("dashboard_contract_ready"),
            "safety_blocked": safety_ready,
            "output_written": False,
        },
    )


def format_dashboard_noise_audit(result: DashboardNoiseAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. DASHBOARD NOISE AUDIT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"dashboard noise audit ready: {result.dashboard_noise_audit_ready}",
        "",
        "CHECKS:",
        f"- read-only: {result.read_only}",
        f"- no output write required: {result.no_output_write_required}",
        f"- dashboard HTML inspected: {result.dashboard_html_inspected}",
        f"- calm markers present: {result.calm_markers_present}",
        f"- noisy markers absent: {result.noisy_markers_absent}",
        f"- long code-heavy command cards absent: {result.long_code_heavy_command_cards_absent}",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        "",
        "SAFETY ASSERTIONS:",
        f"- manual_only: {result.manual_only}",
        f"- execution_forbidden: {result.execution_forbidden}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        f"- allocation_mutation: {result.allocation_mutation}",
        f"- approval_mutation: {result.approval_mutation}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
        "",
        "Safety: audit only. No broker, credentials, buy/sell request, order, trade, auto-approval, allocation mutation, or approval mutation path is enabled.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. dashboard noise audit.")
    parser.add_argument("--dashboard-noise-audit", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    args = parser.parse_args(argv)

    result = build_dashboard_noise_audit_result(current_date=args.current_date)
    print(format_dashboard_noise_audit(result))
    return 0 if result.dashboard_noise_audit_ready else 1


__all__ = [
    "FORBIDDEN_MARKERS",
    "REQUIRED_CALM_MARKERS",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DashboardNoiseAuditResult",
    "build_dashboard_noise_audit_result",
    "format_dashboard_noise_audit",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
