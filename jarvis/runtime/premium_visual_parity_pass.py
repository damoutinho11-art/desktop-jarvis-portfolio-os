"""J.A.R.V.I.S. v167.0 premium visual parity pass."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.local_server import (
    render_chat_page,
    render_instruments_page,
    render_portfolio_health_page,
    render_universe_page,
)
from jarvis.runtime.portfolio_orbit_view import build_portfolio_orbit_view_result, render_portfolio_orbit_view

STATUS_READY = "JARVIS_V167_0_PREMIUM_VISUAL_PARITY_PASS_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V167_0_PREMIUM_VISUAL_PARITY_PASS_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_VISUAL_PARITY_PASS"

DASHBOARD_REQUIRED_MARKERS: tuple[str, ...] = (
    "J.A.R.V.I.S.",
    "PORTFOLIO OS",
    "READY FOR MANUAL USE",
    "Manual-only",
    "No broker",
    "No credentials",
    "No orders",
    "No trades",
    "Data Feed",
    "System",
    "Security",
    "left-nav-rail",
    "Portfolio Orbit",
    "dashboard-orbit",
    "dashboard-core",
    "dashboard-planet",
    "selected-asset-telemetry",
    "Selected asset telemetry",
    "Today's Manual Plan",
    "Portfolio Health",
    "What Changed",
    "System Checks",
    "Market Movement",
    "Market Headlines",
    "assistant chat voice panel",
    "Prepare Manual Review",
    "Evidence Summary",
    "No Action Taken",
)

FORBIDDEN_DASHBOARD_LABELS: tuple[str, ...] = (
    "internal_sleeve_placeholder_not_tradable",
    "etf_fund_candidate_missing_quote_source",
    "tradable_instrument_trusted_quote",
    "partial_or_unavailable",
    "buy now",
    "sell now",
    "place order",
    "execute trade",
    "liquidate",
    "rebalance portfolio",
    "connect broker",
    "order ready",
    "trade ready",
)


@dataclass(frozen=True)
class PremiumVisualParityPassResult:
    status: str
    final_verdict: str
    visual_parity_ready: bool
    dashboard_target_structure_ready: bool
    dashboard_forbidden_labels_absent: bool
    orbit_visual_polish_ready: bool
    chat_hud_consistent: bool
    universe_surface_consistent: bool
    instruments_surface_consistent: bool
    portfolio_health_surface_consistent: bool
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


def build_premium_visual_parity_pass_result(*, current_date: str = "2026-06-21") -> PremiumVisualParityPassResult:
    blockers: list[str] = []
    proof: dict[str, Any] = {}
    dashboard_html = render_dashboard_html(build_dashboard_contract_result(current_date=current_date))
    orbit_html = render_portfolio_orbit_view(build_portfolio_orbit_view_result(current_date=current_date))
    chat_html = render_chat_page()
    universe_html = render_universe_page()
    instruments_html = render_instruments_page(current_date=current_date, symbol="MSFT")
    health_html = render_portfolio_health_page(current_date=current_date)

    missing_dashboard = _missing(dashboard_html, DASHBOARD_REQUIRED_MARKERS)
    dashboard_target_structure_ready = not missing_dashboard
    proof["dashboard_missing_markers"] = missing_dashboard
    if missing_dashboard:
        blockers.append("dashboard_target_structure_not_ready")

    forbidden_dashboard = _forbidden_found(dashboard_html, FORBIDDEN_DASHBOARD_LABELS)
    dashboard_forbidden_labels_absent = not forbidden_dashboard
    proof["dashboard_forbidden_labels_found"] = forbidden_dashboard
    if forbidden_dashboard:
        blockers.append("dashboard_forbidden_labels_found")

    orbit_markers = (
        "Portfolio Orbit",
        "orbit-map",
        "orbit-ring",
        "needs-review selected",
        "Selected Instrument",
        "Manual Review Note",
        "Fresh trusted quote context",
    )
    orbit_missing = _missing(orbit_html, orbit_markers)
    orbit_forbidden = _forbidden_found(orbit_html, FORBIDDEN_DASHBOARD_LABELS)
    orbit_visual_polish_ready = not orbit_missing and not orbit_forbidden
    proof["orbit_missing_markers"] = orbit_missing
    proof["orbit_forbidden_labels_found"] = orbit_forbidden
    if not orbit_visual_polish_ready:
        blockers.append("orbit_visual_polish_not_ready")

    chat_hud_consistent = all(
        marker in chat_html
        for marker in ("J.A.R.V.I.S. Local Chat", "jarvis-orb", "Portfolio Health", "Universe Explorer", "Open Orbit")
    )
    if not chat_hud_consistent:
        blockers.append("chat_hud_not_consistent")

    universe_surface_consistent = all(marker in universe_html for marker in ("Universe Explorer", "Manual Review Required", "data-table"))
    if not universe_surface_consistent:
        blockers.append("universe_surface_not_consistent")

    instruments_surface_consistent = all(
        marker in instruments_html
        for marker in ("Instrument Detail", "Identity and Metadata", "Price / Movement / Freshness", "Manual Checklist")
    )
    if not instruments_surface_consistent:
        blockers.append("instruments_surface_not_consistent")

    portfolio_health_surface_consistent = all(marker in health_html for marker in ("Portfolio Health", "Readiness", "Review Notes"))
    if not portfolio_health_surface_consistent:
        blockers.append("portfolio_health_surface_not_consistent")

    ready = not blockers
    return PremiumVisualParityPassResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if ready else "REVIEW_REQUIRED_FOR_PREMIUM_VISUAL_PARITY_PASS",
        visual_parity_ready=ready,
        dashboard_target_structure_ready=dashboard_target_structure_ready,
        dashboard_forbidden_labels_absent=dashboard_forbidden_labels_absent,
        orbit_visual_polish_ready=orbit_visual_polish_ready,
        chat_hud_consistent=chat_hud_consistent,
        universe_surface_consistent=universe_surface_consistent,
        instruments_surface_consistent=instruments_surface_consistent,
        portfolio_health_surface_consistent=portfolio_health_surface_consistent,
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
            "visual parity pass is local UI only and does not add broker, credential, account, order, trade, approval, or allocation paths",
            "dashboard market and news panels remain read-only context for manual review",
        ],
        proof=proof,
    )


def format_premium_visual_parity_pass(result: PremiumVisualParityPassResult) -> str:
    return "\n".join(
        [
            "J.A.R.V.I.S. PREMIUM VISUAL PARITY PASS",
            f"status: {result.status}",
            f"final verdict: {result.final_verdict}",
            f"visual parity ready: {result.visual_parity_ready}",
            "",
            "CHECKS:",
            f"- dashboard target structure ready: {result.dashboard_target_structure_ready}",
            f"- dashboard forbidden labels absent: {result.dashboard_forbidden_labels_absent}",
            f"- orbit visual polish ready: {result.orbit_visual_polish_ready}",
            f"- chat HUD consistent: {result.chat_hud_consistent}",
            f"- universe surface consistent: {result.universe_surface_consistent}",
            f"- instruments surface consistent: {result.instruments_surface_consistent}",
            f"- portfolio health surface consistent: {result.portfolio_health_surface_consistent}",
            "",
            "SAFETY:",
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
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the premium visual parity pass.")
    parser.add_argument("--premium-visual-parity-pass", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args, _ = parser.parse_known_args(argv)

    result = build_premium_visual_parity_pass_result(current_date=args.current_date)
    print(format_premium_visual_parity_pass(result))
    return 0 if result.visual_parity_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "DASHBOARD_REQUIRED_MARKERS",
    "FORBIDDEN_DASHBOARD_LABELS",
    "PremiumVisualParityPassResult",
    "build_premium_visual_parity_pass_result",
    "format_premium_visual_parity_pass",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
