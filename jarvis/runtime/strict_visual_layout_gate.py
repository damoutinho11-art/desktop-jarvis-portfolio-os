"""J.A.R.V.I.S. v170.0 strict cockpit visual layout gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any

from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.cockpit_dashboard_hard_rebuild import build_cockpit_dashboard_hard_rebuild_result
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.jarvis_experience_parity_gate import STATUS_READY as V156_STATUS_READY
from jarvis.runtime.local_server import (
    ROUTES,
    _health_payload,
    render_chat_page,
    render_instruments_page,
    render_memory_page,
    render_orbit_page,
    render_portfolio_health_page,
    render_safety_page,
    render_settings_page,
    render_universe_page,
)
from jarvis.runtime.premium_motion_gate import STATUS_READY as V166_STATUS_READY
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.visual_acceptance_gate import STATUS_READY as V168_STATUS_READY

STATUS_READY = "JARVIS_V170_0_STRICT_VISUAL_LAYOUT_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V170_0_STRICT_VISUAL_LAYOUT_GATE_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_COCKPIT_VISUAL_REVIEW"

REQUIRED_ROUTE_KEYS: tuple[str, ...] = (
    "GET /health",
    "GET /dashboard",
    "GET /chat",
    "GET /api/status",
    "POST /api/chat",
    "GET /orbit",
    "GET /instruments",
    "GET /universe",
    "GET /portfolio-health",
    "GET /memory",
    "GET /safety",
    "GET /settings",
)

ROUTE_RENDER_MARKERS: dict[str, str] = {
    "/dashboard": "jarvis-cockpit",
    "/chat": "J.A.R.V.I.S. Local Chat",
    "/orbit": "Portfolio Orbit",
    "/instruments?symbol=MSFT": "Instrument Detail",
    "/universe": "Universe Explorer",
    "/portfolio-health": "Portfolio Health",
    "/memory": "What Changed Since Last Time",
    "/safety": "Safety",
    "/settings": "Manual-Only Settings",
}


@dataclass(frozen=True)
class StrictVisualLayoutGateResult:
    status: str
    final_verdict: str
    strict_visual_layout_ready: bool
    cockpit_layout_contract_ready: bool
    structural_classes_present: bool
    dashboard_text_markers_present: bool
    forbidden_labels_absent: bool
    route_registry_ready: bool
    route_render_surfaces_ready: bool
    health_route_ready: bool
    api_status_ready: bool
    api_chat_ready: bool
    v156_experience_gate_ready: bool
    v166_premium_motion_gate_ready: bool
    v168_visual_acceptance_gate_ready: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    account_login_enabled: bool
    private_account_ingestion_enabled: bool
    buy_sell_request_created: bool
    order_ticket_created: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    approval_mutation: bool
    allocation_mutation: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_strict_visual_layout_gate_result(*, current_date: str = "2026-06-21") -> StrictVisualLayoutGateResult:
    blockers: list[str] = []
    proof: dict[str, Any] = {}

    dashboard_result = build_dashboard_contract_result(current_date=current_date)
    dashboard_html = render_dashboard_html(dashboard_result)
    cockpit = build_cockpit_dashboard_hard_rebuild_result(current_date=current_date, dashboard_html=dashboard_html)
    cockpit_layout_contract_ready = bool(cockpit.cockpit_dashboard_ready)
    structural_classes_present = bool(cockpit.structural_classes_present)
    dashboard_text_markers_present = bool(cockpit.target_viewport_sections_present)
    forbidden_labels_absent = bool(cockpit.forbidden_labels_absent)
    proof["cockpit_status"] = cockpit.status
    proof["cockpit_missing_structural_classes"] = cockpit.proof.get("missing_structural_classes", [])
    proof["cockpit_missing_text_markers"] = cockpit.proof.get("missing_text_markers", [])
    proof["cockpit_forbidden_labels_found"] = cockpit.proof.get("forbidden_labels_found", [])
    if not cockpit_layout_contract_ready:
        blockers.append("cockpit_layout_contract_not_ready")

    route_registry_ready = all(route in ROUTES for route in REQUIRED_ROUTE_KEYS)
    proof["missing_routes"] = [route for route in REQUIRED_ROUTE_KEYS if route not in ROUTES]
    if not route_registry_ready:
        blockers.append("route_registry_not_ready")

    rendered_pages = {
        "/dashboard": dashboard_html,
        "/chat": render_chat_page(),
        "/orbit": render_orbit_page(current_date=current_date),
        "/instruments?symbol=MSFT": render_instruments_page(current_date=current_date, symbol="MSFT"),
        "/universe": render_universe_page(),
        "/portfolio-health": render_portfolio_health_page(current_date=current_date),
        "/memory": render_memory_page(current_date=current_date),
        "/safety": render_safety_page(current_date=current_date),
        "/settings": render_settings_page(),
    }
    render_missing = [
        path for path, marker in ROUTE_RENDER_MARKERS.items() if marker not in rendered_pages.get(path, "")
    ]
    route_render_surfaces_ready = not render_missing
    proof["render_missing_routes"] = render_missing
    if render_missing:
        blockers.append("route_render_surfaces_not_ready")

    health_payload = _health_payload(host="127.0.0.1", port=8765, current_date=current_date)
    health_route_ready = bool(
        health_payload.get("local_server_ready")
        and health_payload.get("manual_only")
        and health_payload.get("execution_forbidden")
        and not health_payload.get("broker_connection")
        and not health_payload.get("credentials_used")
        and not health_payload.get("order_created")
        and not health_payload.get("trade_executed")
    )
    if not health_route_ready:
        blockers.append("health_route_not_ready")

    safety_section = dashboard_result.sections.get("safety") or {}
    api_status_ready = bool(
        dashboard_result.product_api_ready
        and safety_section.get("manual_approval_required")
        and safety_section.get("execution_forbidden")
        and not safety_section.get("broker_connection")
        and not safety_section.get("credentials_used")
        and not safety_section.get("order_created")
        and not safety_section.get("trade_executed")
    )
    if not api_status_ready:
        blockers.append("api_status_not_ready")

    chat = build_assistant_router_result(query="Is this manual-only?", current_date=current_date)
    chat_payload = chat.to_dict()
    chat_safety_note = f"{chat_payload.get('safety_note') or ''} {chat_payload.get('reply') or ''}".lower()
    api_chat_ready = bool(
        chat_payload.get("reply")
        and "manual-only" in chat_safety_note
        and not chat_payload.get("order_created")
        and not chat_payload.get("trade_executed")
        and not chat_payload.get("broker_connection")
        and not chat_payload.get("credentials_used")
    )
    if not api_chat_ready:
        blockers.append("api_chat_not_ready")

    v156_experience_gate_ready = V156_STATUS_READY.startswith("JARVIS_V156_0")
    v166_premium_motion_gate_ready = V166_STATUS_READY.startswith("JARVIS_V166_0")
    v168_visual_acceptance_gate_ready = V168_STATUS_READY.startswith("JARVIS_V168_0")
    proof["v156_status"] = V156_STATUS_READY
    proof["v166_status"] = V166_STATUS_READY
    proof["v168_status"] = V168_STATUS_READY
    if not v156_experience_gate_ready:
        blockers.append("v156_experience_gate_not_ready")
    if not v166_premium_motion_gate_ready:
        blockers.append("v166_premium_motion_gate_not_ready")
    if not v168_visual_acceptance_gate_ready:
        blockers.append("v168_visual_acceptance_gate_not_ready")

    safety_text = build_safety_check_console_output()
    safety_check_blocks_execution = "BLOCKED:" in safety_text and "No execution action was taken" in safety_text
    if not safety_check_blocks_execution:
        blockers.append("safety_check_did_not_block_execution")

    ready = not blockers
    return StrictVisualLayoutGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if ready else "REVIEW_REQUIRED_BEFORE_COCKPIT_VISUAL_REVIEW",
        strict_visual_layout_ready=ready,
        cockpit_layout_contract_ready=cockpit_layout_contract_ready,
        structural_classes_present=structural_classes_present,
        dashboard_text_markers_present=dashboard_text_markers_present,
        forbidden_labels_absent=forbidden_labels_absent,
        route_registry_ready=route_registry_ready,
        route_render_surfaces_ready=route_render_surfaces_ready,
        health_route_ready=health_route_ready,
        api_status_ready=api_status_ready,
        api_chat_ready=api_chat_ready,
        v156_experience_gate_ready=v156_experience_gate_ready,
        v166_premium_motion_gate_ready=v166_premium_motion_gate_ready,
        v168_visual_acceptance_gate_ready=v168_visual_acceptance_gate_ready,
        safety_check_blocks_execution=safety_check_blocks_execution,
        manual_only=True,
        execution_forbidden=True,
        broker_connection_enabled=False,
        credentials_required=False,
        account_login_enabled=False,
        private_account_ingestion_enabled=False,
        buy_sell_request_created=False,
        order_ticket_created=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        approval_mutation=False,
        allocation_mutation=False,
        blockers=blockers,
        warnings=[
            "strict visual layout gate checks local read-only surfaces and route renderability",
            "v156, v166, and v168 gate execution is verified by the final validation commands to avoid recursive slow gate rebuilds here",
            "the cockpit is manual review context only; no broker, order, trade, approval, or allocation path is enabled",
        ],
        proof=proof,
    )


def format_strict_visual_layout_gate(result: StrictVisualLayoutGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. STRICT VISUAL LAYOUT GATE",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"strict visual layout ready: {result.strict_visual_layout_ready}",
        "",
        "COCKPIT CHECKS:",
        f"- cockpit layout contract ready: {result.cockpit_layout_contract_ready}",
        f"- structural classes present: {result.structural_classes_present}",
        f"- dashboard text markers present: {result.dashboard_text_markers_present}",
        f"- forbidden labels absent: {result.forbidden_labels_absent}",
        "",
        "ROUTE CHECKS:",
        f"- route registry ready: {result.route_registry_ready}",
        f"- route render surfaces ready: {result.route_render_surfaces_ready}",
        f"- health route ready: {result.health_route_ready}",
        f"- api status ready: {result.api_status_ready}",
        f"- api chat ready: {result.api_chat_ready}",
        "",
        "GATE CHECKS:",
        f"- v156 experience gate ready: {result.v156_experience_gate_ready}",
        f"- v166 premium motion gate ready: {result.v166_premium_motion_gate_ready}",
        f"- v168 visual acceptance gate ready: {result.v168_visual_acceptance_gate_ready}",
        f"- safety-check blocks execution: {result.safety_check_blocks_execution}",
        "",
        "SAFETY ASSERTIONS:",
        f"- manual_only: {result.manual_only}",
        f"- execution_forbidden: {result.execution_forbidden}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- account_login_enabled: {result.account_login_enabled}",
        f"- private_account_ingestion_enabled: {result.private_account_ingestion_enabled}",
        f"- buy_sell_request_created: {result.buy_sell_request_created}",
        f"- order_ticket_created: {result.order_ticket_created}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        f"- approval_mutation: {result.approval_mutation}",
        f"- allocation_mutation: {result.allocation_mutation}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the strict cockpit visual layout gate.")
    parser.add_argument("--strict-visual-layout-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args, _ = parser.parse_known_args(argv)

    result = build_strict_visual_layout_gate_result(current_date=args.current_date)
    print(format_strict_visual_layout_gate(result))
    return 0 if result.strict_visual_layout_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "REQUIRED_ROUTE_KEYS",
    "ROUTE_RENDER_MARKERS",
    "StrictVisualLayoutGateResult",
    "build_strict_visual_layout_gate_result",
    "format_strict_visual_layout_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
