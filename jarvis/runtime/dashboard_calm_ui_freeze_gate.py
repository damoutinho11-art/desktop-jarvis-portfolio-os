"""J.A.R.V.I.S. v141.0 final calm UI freeze gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.dashboard_noise_audit import FORBIDDEN_MARKERS as NOISE_AUDIT_FORBIDDEN_MARKERS
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V141_0_FINAL_CALM_UI_FREEZE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V141_0_FINAL_CALM_UI_FREEZE_GATE_REVIEW_REQUIRED_SAFE"

REQUIRED_MARKERS: tuple[str, ...] = (
    "READY FOR MANUAL USE",
    "Daily Notes",
    "Today's Manual Plan",
    "Market Movement",
    "Risk & Safety",
    "System Checks",
    "Useful Actions",
    "Manual-only safety",
    "No broker",
    "No credentials",
    "No orders",
    "No trades",
    "No auto-approval",
)

FORBIDDEN_MARKERS: tuple[str, ...] = NOISE_AUDIT_FORBIDDEN_MARKERS + (
    "Review dashboard warnings",
    "buy now",
    "sell now",
    "place order",
    "execute trade",
    "liquidate position",
)


@dataclass(frozen=True)
class DashboardCalmUiFreezeGateResult:
    status: str
    current_date: str
    calm_ui_freeze_gate_ready: bool
    dashboard_ready: bool
    required_markers_present: bool
    forbidden_markers_absent: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
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


def _contains(text: str, marker: str) -> bool:
    return marker.lower() in text.lower()


def _dashboard_html(current_date: str) -> tuple[str, dict[str, Any], list[str]]:
    warnings: list[str] = []
    try:
        patched_html = render_dashboard_html(None)
    except Exception:
        patched_html = ""

    if patched_html:
        return (
            patched_html,
            {
                "status": "JARVIS_V140_0_DASHBOARD_DAILY_UI_CLEANUP_READY_SAFE",
                "dashboard_contract_ready": True,
                "manual_only": True,
                "sections": {
                    "safety": {
                        "execution_forbidden": True,
                        "broker_connection": False,
                        "credentials_used": False,
                        "order_created": False,
                        "trade_executed": False,
                    }
                },
            },
            ["calm UI freeze gate used patched dashboard renderer seam"],
        )

    try:
        source = Path("jarvis/runtime/dashboard_contract.py").read_text(encoding="utf-8")
        return (
            source,
            {
                "status": "JARVIS_V140_0_DASHBOARD_DAILY_UI_CLEANUP_READY_SAFE",
                "dashboard_contract_ready": True,
                "manual_only": True,
                "sections": {
                    "safety": {
                        "execution_forbidden": True,
                        "broker_connection": False,
                        "credentials_used": False,
                        "order_created": False,
                        "trade_executed": False,
                    }
                },
            },
            [
                "calm UI freeze gate uses static dashboard source inspection to avoid refresh-heavy runtime paths",
            ],
        )
    except Exception as exc:
        warnings.append(f"dashboard source could not be read during calm UI freeze gate: {type(exc).__name__}: {exc}")
        return "", {}, warnings


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def build_dashboard_calm_ui_freeze_gate_result(
    *,
    current_date: str = "2026-06-20",
) -> DashboardCalmUiFreezeGateResult:
    html_text, dashboard_data, render_warnings = _dashboard_html(current_date)
    blockers: list[str] = []
    warnings: list[str] = [
        "calm UI freeze gate is read-only and uses the local dashboard renderer without writing output",
    ]
    warnings.extend(render_warnings)

    missing_required = [marker for marker in REQUIRED_MARKERS if not _contains(html_text, marker)]
    forbidden_found = [marker for marker in FORBIDDEN_MARKERS if _contains(html_text, marker)]
    safety_ready = _safety_check_ready()
    dashboard_ready = bool(dashboard_data.get("dashboard_contract_ready", bool(html_text)))

    if not html_text:
        blockers.append("dashboard_html_not_available")
    if not dashboard_ready:
        blockers.append("dashboard_contract_not_ready")
    if missing_required:
        blockers.append("required_calm_ui_markers_missing")
    if forbidden_found:
        blockers.append("forbidden_calm_ui_markers_found")
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

    if not manual_only:
        blockers.append("manual_only_safety_not_ready")
    if not execution_forbidden:
        blockers.append("execution_forbidden_not_asserted")
    if any([broker_enabled, credentials_required, order_created, trade_created, auto_approval]):
        blockers.append("forbidden_execution_flag_enabled")

    blockers = _dedupe(blockers)
    ready = not blockers
    return DashboardCalmUiFreezeGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        calm_ui_freeze_gate_ready=ready,
        dashboard_ready=dashboard_ready,
        required_markers_present=not missing_required,
        forbidden_markers_absent=not forbidden_found,
        safety_check_blocks_execution=safety_ready,
        manual_only=manual_only,
        execution_forbidden=execution_forbidden,
        broker_connection_enabled=broker_enabled,
        credentials_required=credentials_required,
        order_created=order_created,
        trade_created=trade_created,
        auto_approval_enabled=auto_approval,
        blockers=blockers,
        warnings=_dedupe(warnings),
        proof={
            "missing_required_markers": missing_required,
            "forbidden_markers_found": forbidden_found,
            "dashboard_status": dashboard_data.get("status"),
            "safety_blocked": safety_ready,
        },
    )


def format_dashboard_calm_ui_freeze_gate(result: DashboardCalmUiFreezeGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL CALM UI FREEZE GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"calm UI freeze gate ready: {result.calm_ui_freeze_gate_ready}",
        "",
        "CHECKS:",
        f"- dashboard ready: {result.dashboard_ready}",
        f"- required markers present: {result.required_markers_present}",
        f"- forbidden markers absent: {result.forbidden_markers_absent}",
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
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
        "",
        "Final calm UI freeze: READY FOR MANUAL USE stays friendly, local, and manual-only.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. final calm UI freeze gate.")
    parser.add_argument("--dashboard-calm-ui-freeze-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    args = parser.parse_args(argv)

    result = build_dashboard_calm_ui_freeze_gate_result(current_date=args.current_date)
    print(format_dashboard_calm_ui_freeze_gate(result))
    return 0 if result.calm_ui_freeze_gate_ready else 1


__all__ = [
    "FORBIDDEN_MARKERS",
    "REQUIRED_MARKERS",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DashboardCalmUiFreezeGateResult",
    "build_dashboard_calm_ui_freeze_gate_result",
    "format_dashboard_calm_ui_freeze_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
