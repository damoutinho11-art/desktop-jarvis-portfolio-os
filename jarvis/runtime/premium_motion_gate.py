"""J.A.R.V.I.S. v166.0 final premium motion and safety gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.finance_database_universe import build_finance_database_universe_result
from jarvis.runtime.finance_toolkit_fundamentals import build_finance_toolkit_fundamentals_result
from jarvis.runtime.jarvis_experience_parity_gate import build_jarvis_experience_parity_gate_result
from jarvis.runtime.local_server import ROUTES, render_chat_page, render_portfolio_health_page, render_settings_page, render_universe_page
from jarvis.runtime.orbital_instrument_detail_panel import (
    build_orbital_instrument_detail_result,
    render_orbital_instrument_detail_panel,
)
from jarvis.runtime.portfolio_health_report_card import build_portfolio_health_report_card_result
from jarvis.runtime.portfolio_orbit_view import build_portfolio_orbit_view_result, render_portfolio_orbit_view
from jarvis.runtime.premium_chat_voice_hud import build_chat_voice_hud_polish_result
from jarvis.runtime.premium_command_center_dashboard import build_command_center_dashboard_result
from jarvis.runtime.premium_orbital_design_system import build_premium_orbital_design_system_result, render_nav
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.universe_explorer import build_universe_explorer_result

STATUS_READY = "JARVIS_V166_0_FINAL_PREMIUM_MOTION_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V166_0_FINAL_PREMIUM_MOTION_GATE_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_SAFE_JARVIS_OS"

FORBIDDEN_CAPABILITY_MARKERS: tuple[str, ...] = (
    "broker_login(",
    "connect_broker(",
    "create_order(",
    "execute_trade(",
    "place_order(",
    "submit_order(",
    "rebalance_portfolio(",
    "auto_approval_enabled = True",
    "private_account_ingestion_enabled = True",
    "allocation_mutation = True",
    "approval_mutation = True",
    "buy_sell_request_created = True",
    "order_ticket_created = True",
)


@dataclass(frozen=True)
class PremiumMotionGateResult:
    status: str
    final_verdict: str
    premium_motion_gate_ready: bool
    premium_design_system_present: bool
    command_center_dashboard_present: bool
    portfolio_orbit_view_present: bool
    orbital_instrument_detail_present: bool
    chat_voice_hud_polish_present: bool
    jarvis_orb_present: bool
    ticker_present: bool
    session_memory_visible: bool
    what_changed_visible: bool
    top_navigation_ready: bool
    local_server_routes_ready: bool
    intelligence_routes_ready: bool
    v156_experience_gate_ready: bool
    safety_check_blocks_execution: bool
    forbidden_capabilities_absent: bool
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


def _markers(text: str, required: list[str]) -> tuple[bool, list[str]]:
    missing = [marker for marker in required if marker not in text]
    return not missing, missing


def _source_text(paths: list[str]) -> str:
    parts = []
    for path in paths:
        parts.append(Path(path).read_text(encoding="utf-8"))
    return "\n".join(parts)


def _forbidden_capabilities_absent() -> tuple[bool, list[str]]:
    paths = [
        "jarvis/runtime/local_server.py",
        "jarvis/runtime/premium_orbital_design_system.py",
        "jarvis/runtime/premium_command_center_dashboard.py",
        "jarvis/runtime/portfolio_orbit_view.py",
        "jarvis/runtime/orbital_instrument_detail_panel.py",
        "jarvis/runtime/premium_chat_voice_hud.py",
    ]
    lowered = _source_text(paths).lower()
    found = [marker for marker in FORBIDDEN_CAPABILITY_MARKERS if marker.lower() in lowered]
    return not found, found


def build_premium_motion_gate_result(*, current_date: str = "2026-06-21") -> PremiumMotionGateResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "premium motion gate validates local UI/runtime markers only and does not write output, local memory, approval, allocation, broker, order, or trade files",
        "optional FinanceDatabase and FinanceToolkit dependencies may safely fall back to fixtures or warnings",
    ]
    proof: dict[str, Any] = {}

    design = build_premium_orbital_design_system_result()
    premium_design_system_present = bool(design.design_system_ready and "orbital-core" in design.reusable_components)
    proof["design_status"] = design.status
    if not premium_design_system_present:
        blockers.append("premium_design_system_not_present")

    dashboard_result = build_dashboard_contract_result(current_date=current_date)
    dashboard_html = render_dashboard_html(dashboard_result)
    command_center = build_command_center_dashboard_result(dashboard_html)
    command_center_dashboard_present = bool(command_center.command_center_ready)
    proof["command_center_status"] = command_center.status
    if not command_center_dashboard_present:
        blockers.append("command_center_dashboard_not_present")

    orbit_result = build_portfolio_orbit_view_result()
    orbit_html = render_portfolio_orbit_view(orbit_result)
    orbit_ready, orbit_missing = _markers(
        orbit_html,
        ["Portfolio Orbit", "orbital-core", "orbit-ring", "planet-focus", "Open Detail Panel", "Manual Review"],
    )
    portfolio_orbit_view_present = bool(orbit_result.orbit_view_ready and orbit_ready)
    proof["orbit_status"] = orbit_result.status
    proof["orbit_missing"] = orbit_missing
    if not portfolio_orbit_view_present:
        blockers.append("portfolio_orbit_view_not_present")

    detail_result = build_orbital_instrument_detail_result(current_date=current_date, symbol="MSFT")
    detail_html = render_orbital_instrument_detail_panel(detail_result)
    detail_ready, detail_missing = _markers(
        detail_html,
        [
            "Instrument Detail",
            "Identity and Metadata",
            "Price / Movement / Freshness",
            "Fundamental Context",
            "Manual Checklist",
            "Evidence Summary",
        ],
    )
    orbital_instrument_detail_present = bool(detail_result.detail_panel_ready and detail_ready)
    proof["instrument_detail_status"] = detail_result.status
    proof["instrument_detail_missing"] = detail_missing
    if not orbital_instrument_detail_present:
        blockers.append("orbital_instrument_detail_not_present")

    chat_html = render_chat_page()
    chat_hud = build_chat_voice_hud_polish_result(rendered_html=chat_html)
    chat_voice_hud_polish_present = bool(chat_hud.chat_voice_hud_ready)
    jarvis_orb_present = bool(chat_hud.jarvis_orb_present)
    proof["chat_voice_hud_status"] = chat_hud.status
    if not chat_voice_hud_polish_present:
        blockers.append("chat_voice_hud_polish_not_present")
    if not jarvis_orb_present:
        blockers.append("jarvis_orb_not_present")

    ticker_present = all(marker in dashboard_html for marker in ("headline-ticker", "ticker-scroll", "Market Headlines"))
    if not ticker_present:
        blockers.append("headline_ticker_not_present")

    session_memory_visible = "Last Session" in dashboard_html and "Safe derived summaries only" in dashboard_html
    what_changed_visible = "What Changed Since Last Time" in dashboard_html and "Since last time:" in dashboard_html
    if not session_memory_visible:
        blockers.append("session_memory_not_visible")
    if not what_changed_visible:
        blockers.append("what_changed_not_visible")

    nav_html = render_nav("dashboard")
    top_navigation_ready = all(
        marker in nav_html
        for marker in (
            "Dashboard",
            "Chat",
            "Orbit",
            "Universe",
            "Instruments",
            "Portfolio Health",
            "Memory",
            "Safety",
            "Settings",
        )
    )
    if not top_navigation_ready:
        blockers.append("top_navigation_not_ready")

    required_routes = (
        "GET /health",
        "GET /dashboard",
        "GET /chat",
        "POST /api/chat",
        "GET /api/status",
        "GET /orbit",
        "GET /universe",
        "GET /instruments",
        "GET /portfolio-health",
        "GET /settings",
    )
    local_server_routes_ready = all(route in ROUTES for route in required_routes)
    proof["missing_routes"] = [route for route in required_routes if route not in ROUTES]
    if not local_server_routes_ready:
        blockers.append("local_server_routes_not_ready")

    universe_page = render_universe_page()
    health_page = render_portfolio_health_page(current_date=current_date)
    settings_page = render_settings_page()
    proof["supporting_pages_ready"] = all(
        marker in universe_page + health_page + settings_page
        for marker in ("Universe Explorer", "Portfolio Health", "Manual-Only Settings")
    )

    finance_database = build_finance_database_universe_result()
    finance_toolkit = build_finance_toolkit_fundamentals_result(symbols=["MSFT"])
    universe = build_universe_explorer_result(query="find European accumulating global ETFs")
    health = build_portfolio_health_report_card_result(current_date=current_date)
    intelligence_routes_ready = all(
        [
            finance_database.status.startswith("JARVIS_V157_0"),
            finance_toolkit.status.startswith("JARVIS_V158_0"),
            universe.status.startswith("JARVIS_V159_0"),
            health.status.startswith("JARVIS_V160_0"),
            universe.manual_review_required,
            health.report_card_ready,
        ]
    )
    proof["finance_database_status"] = finance_database.status
    proof["finance_toolkit_status"] = finance_toolkit.status
    proof["universe_status"] = universe.status
    proof["portfolio_health_status"] = health.status
    if not intelligence_routes_ready:
        blockers.append("v160_intelligence_routes_not_ready")

    experience = build_jarvis_experience_parity_gate_result(current_date=current_date)
    v156_experience_gate_ready = bool(experience.jarvis_experience_parity_ready)
    proof["v156_experience_status"] = experience.status
    if not v156_experience_gate_ready:
        blockers.append("v156_experience_gate_not_ready")

    safety_text = build_safety_check_console_output()
    safety_check_blocks_execution = "BLOCKED:" in safety_text and "No execution action was taken" in safety_text
    if not safety_check_blocks_execution:
        blockers.append("safety_check_did_not_block_execution")

    forbidden_capabilities_absent, forbidden_found = _forbidden_capabilities_absent()
    proof["forbidden_capability_markers_found"] = forbidden_found
    if not forbidden_capabilities_absent:
        blockers.append("forbidden_capability_marker_found")

    ready = not blockers
    return PremiumMotionGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if ready else "REVIEW_REQUIRED_BEFORE_PREMIUM_SAFE_JARVIS_OS",
        premium_motion_gate_ready=ready,
        premium_design_system_present=premium_design_system_present,
        command_center_dashboard_present=command_center_dashboard_present,
        portfolio_orbit_view_present=portfolio_orbit_view_present,
        orbital_instrument_detail_present=orbital_instrument_detail_present,
        chat_voice_hud_polish_present=chat_voice_hud_polish_present,
        jarvis_orb_present=jarvis_orb_present,
        ticker_present=ticker_present,
        session_memory_visible=session_memory_visible,
        what_changed_visible=what_changed_visible,
        top_navigation_ready=top_navigation_ready,
        local_server_routes_ready=local_server_routes_ready,
        intelligence_routes_ready=intelligence_routes_ready,
        v156_experience_gate_ready=v156_experience_gate_ready,
        safety_check_blocks_execution=safety_check_blocks_execution,
        forbidden_capabilities_absent=forbidden_capabilities_absent,
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
        warnings=warnings,
        proof=proof,
    )


def format_premium_motion_gate(result: PremiumMotionGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL PREMIUM MOTION GATE",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"premium motion gate ready: {result.premium_motion_gate_ready}",
        "",
        "CHECKS:",
        f"- premium design system present: {result.premium_design_system_present}",
        f"- command center dashboard present: {result.command_center_dashboard_present}",
        f"- portfolio orbit view present: {result.portfolio_orbit_view_present}",
        f"- orbital instrument detail present: {result.orbital_instrument_detail_present}",
        f"- chat/voice HUD polish present: {result.chat_voice_hud_polish_present}",
        f"- J.A.R.V.I.S. orb present: {result.jarvis_orb_present}",
        f"- ticker present: {result.ticker_present}",
        f"- session memory visible: {result.session_memory_visible}",
        f"- what-changed visible: {result.what_changed_visible}",
        f"- top navigation ready: {result.top_navigation_ready}",
        f"- local server routes ready: {result.local_server_routes_ready}",
        f"- v157-v160 intelligence routes ready: {result.intelligence_routes_ready}",
        f"- v156 experience gate ready: {result.v156_experience_gate_ready}",
        f"- safety-check blocks execution: {result.safety_check_blocks_execution}",
        f"- forbidden capabilities absent: {result.forbidden_capabilities_absent}",
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
    parser = argparse.ArgumentParser(description="Validate the final premium safe J.A.R.V.I.S. OS UI/motion gate.")
    parser.add_argument("--premium-motion-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args, _ = parser.parse_known_args(argv)

    result = build_premium_motion_gate_result(current_date=args.current_date)
    print(format_premium_motion_gate(result))
    return 0 if result.premium_motion_gate_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "FORBIDDEN_CAPABILITY_MARKERS",
    "PremiumMotionGateResult",
    "build_premium_motion_gate_result",
    "format_premium_motion_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
