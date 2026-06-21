"""J.A.R.V.I.S. v169.0 cockpit dashboard hard rebuild gate."""

from __future__ import annotations

import argparse
import re
from dataclasses import asdict, dataclass
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html

STATUS_READY = "JARVIS_V169_0_COCKPIT_DASHBOARD_HARD_REBUILD_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V169_0_COCKPIT_DASHBOARD_HARD_REBUILD_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_COCKPIT_DASHBOARD_HARD_REBUILD"

COCKPIT_STRUCTURAL_CLASSES: tuple[str, ...] = (
    "jarvis-cockpit",
    "cockpit-topbar",
    "cockpit-sidebar",
    "cockpit-orbit",
    "cockpit-telemetry",
    "cockpit-plan",
    "cockpit-health",
    "cockpit-changes",
    "cockpit-checks",
    "cockpit-market",
    "cockpit-ticker",
    "cockpit-assistant",
)

COCKPIT_LAYOUT_MARKERS: tuple[str, ...] = (
    "display:grid",
    "grid-template-columns:72px",
    "minmax(620px,1fr)",
    "minmax(360px,430px)",
    "grid-template-rows:78px",
    "minmax(320px,1fr)",
    "158px40px72px",
)

COCKPIT_TEXT_MARKERS: tuple[str, ...] = (
    "J.A.R.V.I.S.",
    "Portfolio OS",
    "READY FOR MANUAL USE",
    "Manual-only",
    "No broker",
    "No credentials",
    "No orders",
    "No trades",
    "Data Feed",
    "Local Cache",
    "System",
    "Nominal",
    "Security",
    "Locked",
    "Portfolio Core",
    "BTC",
    "ETH",
    "VWCE",
    "IS3Q.DE",
    "MSFT",
    "Selected",
    "J.A.R.V.I.S. Note",
    "Today's Manual Plan",
    "Portfolio Health",
    "What Changed",
    "System Checks",
    "Market Movement",
    "Market Headlines",
    "assistant/chat/voice marker",
)

FORBIDDEN_DASHBOARD_LABELS: tuple[str, ...] = (
    "internal_sleeve_placeholder_not_tradable",
    "etf_fund_candidate_missing_quote_source",
    "tradable_instrument_trusted_quote",
    "partial_or_unavailable",
    "fixture universe",
    "fixture context",
    "raw internal cache",
    "buy now",
    "sell now",
    "place order",
    "execute trade",
    "liquidate",
    "rebalance portfolio",
    "connect broker",
    "broker login",
    "order ticket",
)


@dataclass(frozen=True)
class CockpitDashboardHardRebuildResult:
    status: str
    final_verdict: str
    cockpit_dashboard_ready: bool
    structural_classes_present: bool
    compact_grid_contract_present: bool
    target_viewport_sections_present: bool
    forbidden_labels_absent: bool
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


def _missing_raw(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def _visible_text(html_text: str) -> str:
    stripped = re.sub(r"<[^>]+>", " ", html_text)
    return re.sub(r"\s+", " ", stripped).strip()


def _missing_text(html_text: str, markers: tuple[str, ...]) -> list[str]:
    searchable = f"{_visible_text(html_text)} {html_text}".lower()
    return [marker for marker in markers if marker.lower() not in searchable]


def _forbidden_found(text: str, labels: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [label for label in labels if label in lowered]


def build_cockpit_dashboard_hard_rebuild_result(
    *,
    current_date: str = "2026-06-21",
    dashboard_html: str | None = None,
) -> CockpitDashboardHardRebuildResult:
    blockers: list[str] = []
    proof: dict[str, Any] = {}

    html_text = dashboard_html
    if html_text is None:
        html_text = render_dashboard_html(build_dashboard_contract_result(current_date=current_date))

    missing_classes = _missing_raw(html_text, COCKPIT_STRUCTURAL_CLASSES)
    structural_classes_present = not missing_classes
    proof["missing_structural_classes"] = missing_classes
    if missing_classes:
        blockers.append("cockpit_structural_classes_missing")

    compact_html = re.sub(r"\s+", "", html_text)
    compact_grid_missing = _missing_raw(compact_html, COCKPIT_LAYOUT_MARKERS)
    compact_grid_contract_present = not compact_grid_missing
    proof["missing_grid_markers"] = compact_grid_missing
    if compact_grid_missing:
        blockers.append("compact_grid_contract_missing")

    missing_text = _missing_text(html_text, COCKPIT_TEXT_MARKERS)
    target_viewport_sections_present = not missing_text
    proof["missing_text_markers"] = missing_text
    if missing_text:
        blockers.append("target_viewport_sections_missing")

    forbidden = _forbidden_found(html_text, FORBIDDEN_DASHBOARD_LABELS)
    forbidden_labels_absent = not forbidden
    proof["forbidden_labels_found"] = forbidden
    if forbidden:
        blockers.append("forbidden_dashboard_labels_found")

    ready = not blockers
    return CockpitDashboardHardRebuildResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if ready else "REVIEW_REQUIRED_FOR_COCKPIT_DASHBOARD_HARD_REBUILD",
        cockpit_dashboard_ready=ready,
        structural_classes_present=structural_classes_present,
        compact_grid_contract_present=compact_grid_contract_present,
        target_viewport_sections_present=target_viewport_sections_present,
        forbidden_labels_absent=forbidden_labels_absent,
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
            "cockpit dashboard hard rebuild validates local read-only HTML only",
            "market, universe, and instrument context remain manual review context only",
        ],
        proof=proof,
    )


def format_cockpit_dashboard_hard_rebuild(result: CockpitDashboardHardRebuildResult) -> str:
    lines = [
        "J.A.R.V.I.S. COCKPIT DASHBOARD HARD REBUILD",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"cockpit dashboard ready: {result.cockpit_dashboard_ready}",
        "",
        "CHECKS:",
        f"- structural classes present: {result.structural_classes_present}",
        f"- compact grid contract present: {result.compact_grid_contract_present}",
        f"- target viewport sections present: {result.target_viewport_sections_present}",
        f"- forbidden labels absent: {result.forbidden_labels_absent}",
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
    parser = argparse.ArgumentParser(description="Validate the v169 cockpit dashboard hard rebuild.")
    parser.add_argument("--cockpit-dashboard-hard-rebuild", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args, _ = parser.parse_known_args(argv)

    result = build_cockpit_dashboard_hard_rebuild_result(current_date=args.current_date)
    print(format_cockpit_dashboard_hard_rebuild(result))
    return 0 if result.cockpit_dashboard_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "COCKPIT_STRUCTURAL_CLASSES",
    "COCKPIT_LAYOUT_MARKERS",
    "COCKPIT_TEXT_MARKERS",
    "FORBIDDEN_DASHBOARD_LABELS",
    "CockpitDashboardHardRebuildResult",
    "build_cockpit_dashboard_hard_rebuild_result",
    "format_cockpit_dashboard_hard_rebuild",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
