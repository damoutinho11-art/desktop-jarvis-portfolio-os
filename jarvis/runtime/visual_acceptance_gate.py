"""J.A.R.V.I.S. v168.0 final visual acceptance gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any

from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.finance_database_universe import build_finance_database_universe_result
from jarvis.runtime.finance_toolkit_fundamentals import build_finance_toolkit_fundamentals_result
from jarvis.runtime.jarvis_experience_parity_gate import build_jarvis_experience_parity_gate_result
from jarvis.runtime.local_server import (
    ROUTES,
    render_chat_page,
    render_instruments_page,
    render_memory_page,
    render_orbit_page,
    render_portfolio_health_page,
    render_safety_page,
    render_settings_page,
    render_universe_page,
)
from jarvis.runtime.portfolio_health_report_card import build_portfolio_health_report_card_result
from jarvis.runtime.premium_motion_gate import build_premium_motion_gate_result
from jarvis.runtime.premium_visual_parity_pass import (
    DASHBOARD_REQUIRED_MARKERS,
    FORBIDDEN_DASHBOARD_LABELS,
    build_premium_visual_parity_pass_result,
)
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.universe_explorer import build_universe_explorer_result

STATUS_READY = "JARVIS_V168_0_FINAL_VISUAL_ACCEPTANCE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V168_0_FINAL_VISUAL_ACCEPTANCE_GATE_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_VISUAL_ACCEPTANCE"

REQUIRED_ROUTE_KEYS: tuple[str, ...] = (
    "GET /health",
    "GET /dashboard",
    "GET /chat",
    "GET /orbit",
    "GET /instruments",
    "GET /universe",
    "GET /portfolio-health",
    "GET /memory",
    "GET /safety",
    "GET /settings",
    "GET /api/status",
    "POST /api/chat",
)


@dataclass(frozen=True)
class VisualAcceptanceGateResult:
    status: str
    final_verdict: str
    visual_acceptance_ready: bool
    dashboard_markers_present: bool
    dashboard_forbidden_labels_absent: bool
    route_registry_ready: bool
    route_render_surfaces_ready: bool
    api_status_ready: bool
    api_chat_ready: bool
    v156_experience_gate_ready: bool
    v166_premium_motion_gate_ready: bool
    v167_visual_parity_ready: bool
    v157_v160_intelligence_ready: bool
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


def _missing(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def _forbidden_found(text: str, labels: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [label for label in labels if label in lowered]


def build_visual_acceptance_gate_result(*, current_date: str = "2026-06-21") -> VisualAcceptanceGateResult:
    blockers: list[str] = []
    proof: dict[str, Any] = {}

    dashboard_html = render_dashboard_html(build_dashboard_contract_result(current_date=current_date))
    dashboard_missing = _missing(dashboard_html, DASHBOARD_REQUIRED_MARKERS)
    dashboard_markers_present = not dashboard_missing
    proof["dashboard_missing_markers"] = dashboard_missing
    if dashboard_missing:
        blockers.append("dashboard_visual_markers_missing")

    forbidden_found = _forbidden_found(dashboard_html, FORBIDDEN_DASHBOARD_LABELS)
    dashboard_forbidden_labels_absent = not forbidden_found
    proof["dashboard_forbidden_labels_found"] = forbidden_found
    if forbidden_found:
        blockers.append("dashboard_forbidden_labels_found")

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
    required_render_markers = {
        "/dashboard": "visual-command-center",
        "/chat": "J.A.R.V.I.S. Local Chat",
        "/orbit": "Portfolio Orbit",
        "/instruments?symbol=MSFT": "Instrument Detail",
        "/universe": "Universe Explorer",
        "/portfolio-health": "Portfolio Health",
        "/memory": "What Changed Since Last Time",
        "/safety": "Safety",
        "/settings": "Manual-Only Settings",
    }
    render_missing = [
        path for path, marker in required_render_markers.items() if marker not in rendered_pages.get(path, "")
    ]
    route_render_surfaces_ready = not render_missing
    proof["render_missing_routes"] = render_missing
    if render_missing:
        blockers.append("route_render_surfaces_not_ready")

    product = build_product_api_result(current_date=current_date)
    product_payload = product.to_dict()
    product_safety = product_payload.get("safety_status") or {}
    api_status_ready = bool(
        product_payload.get("api_ready")
        and product_safety.get("manual_approval_required")
        and product_safety.get("execution_forbidden")
        and not product_safety.get("broker_connection")
        and not product_safety.get("credentials_used")
        and not product_safety.get("order_created")
        and not product_safety.get("trade_executed")
    )
    if not api_status_ready:
        blockers.append("api_status_not_ready")

    chat = build_assistant_router_result(query="Is this safe?", current_date=current_date)
    chat_payload = chat.to_dict()
    api_chat_ready = bool(chat_payload.get("reply") and not chat_payload.get("trade_executed") and not chat_payload.get("order_created"))
    if not api_chat_ready:
        blockers.append("api_chat_not_ready")

    experience = build_jarvis_experience_parity_gate_result(current_date=current_date)
    v156_experience_gate_ready = bool(experience.jarvis_experience_parity_ready)
    proof["v156_status"] = experience.status
    if not v156_experience_gate_ready:
        blockers.append("v156_experience_gate_not_ready")

    motion = build_premium_motion_gate_result(current_date=current_date)
    v166_premium_motion_gate_ready = bool(motion.premium_motion_gate_ready)
    proof["v166_status"] = motion.status
    if not v166_premium_motion_gate_ready:
        blockers.append("v166_premium_motion_gate_not_ready")

    visual_parity = build_premium_visual_parity_pass_result(current_date=current_date)
    v167_visual_parity_ready = bool(visual_parity.visual_parity_ready)
    proof["v167_status"] = visual_parity.status
    if not v167_visual_parity_ready:
        blockers.append("v167_visual_parity_not_ready")

    finance_database = build_finance_database_universe_result()
    finance_toolkit = build_finance_toolkit_fundamentals_result(symbols=["MSFT"])
    universe = build_universe_explorer_result(query="find European accumulating global ETFs")
    portfolio_health = build_portfolio_health_report_card_result(current_date=current_date)
    v157_v160_intelligence_ready = all(
        [
            finance_database.status.startswith("JARVIS_V157_0"),
            finance_toolkit.status.startswith("JARVIS_V158_0"),
            universe.status.startswith("JARVIS_V159_0"),
            portfolio_health.status.startswith("JARVIS_V160_0"),
        ]
    )
    proof["v157_status"] = finance_database.status
    proof["v158_status"] = finance_toolkit.status
    proof["v159_status"] = universe.status
    proof["v160_status"] = portfolio_health.status
    if not v157_v160_intelligence_ready:
        blockers.append("v157_v160_intelligence_not_ready")

    safety_text = build_safety_check_console_output()
    safety_check_blocks_execution = "BLOCKED:" in safety_text and "No execution action was taken" in safety_text
    if not safety_check_blocks_execution:
        blockers.append("safety_check_did_not_block_execution")

    ready = not blockers
    return VisualAcceptanceGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if ready else "REVIEW_REQUIRED_BEFORE_PREMIUM_VISUAL_ACCEPTANCE",
        visual_acceptance_ready=ready,
        dashboard_markers_present=dashboard_markers_present,
        dashboard_forbidden_labels_absent=dashboard_forbidden_labels_absent,
        route_registry_ready=route_registry_ready,
        route_render_surfaces_ready=route_render_surfaces_ready,
        api_status_ready=api_status_ready,
        api_chat_ready=api_chat_ready,
        v156_experience_gate_ready=v156_experience_gate_ready,
        v166_premium_motion_gate_ready=v166_premium_motion_gate_ready,
        v167_visual_parity_ready=v167_visual_parity_ready,
        v157_v160_intelligence_ready=v157_v160_intelligence_ready,
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
            "visual acceptance gate is read-only and does not write output, local memory, approval, allocation, broker, order, or trade files",
            "dashboard and supporting routes remain manual review context only",
        ],
        proof=proof,
    )


def format_visual_acceptance_gate(result: VisualAcceptanceGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL VISUAL ACCEPTANCE GATE",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"visual acceptance ready: {result.visual_acceptance_ready}",
        "",
        "CHECKS:",
        f"- dashboard markers present: {result.dashboard_markers_present}",
        f"- dashboard forbidden labels absent: {result.dashboard_forbidden_labels_absent}",
        f"- route registry ready: {result.route_registry_ready}",
        f"- route render surfaces ready: {result.route_render_surfaces_ready}",
        f"- api status ready: {result.api_status_ready}",
        f"- api chat ready: {result.api_chat_ready}",
        f"- v156 experience gate ready: {result.v156_experience_gate_ready}",
        f"- v166 premium motion gate ready: {result.v166_premium_motion_gate_ready}",
        f"- v167 visual parity ready: {result.v167_visual_parity_ready}",
        f"- v157-v160 intelligence ready: {result.v157_v160_intelligence_ready}",
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
    parser = argparse.ArgumentParser(description="Validate final premium visual acceptance.")
    parser.add_argument("--visual-acceptance-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args, _ = parser.parse_known_args(argv)

    result = build_visual_acceptance_gate_result(current_date=args.current_date)
    print(format_visual_acceptance_gate(result))
    return 0 if result.visual_acceptance_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "REQUIRED_ROUTE_KEYS",
    "VisualAcceptanceGateResult",
    "build_visual_acceptance_gate_result",
    "format_visual_acceptance_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
