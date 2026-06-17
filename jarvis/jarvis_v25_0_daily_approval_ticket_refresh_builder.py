"""J.A.R.V.I.S. v25.0 daily approval ticket refresh builder.

v25 creates a current manual-approval ticket from the active v24 daily operator,
including the v23 crypto-lane selection and the current stock/fund/ETF lane from
the allocation engine.

This intentionally writes a local approval-ticket artifact when requested. It
does not create a buy request, does not connect to brokers, does not place
orders, and does not execute trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .jarvis_v24_0_crypto_lane_selection_daily_operator_bridge import (
    CryptoLaneSelectionDailyOperatorBridgeResult,
    build_crypto_lane_selection_daily_operator_bridge,
)

STATUS_READY = "JARVIS_V25_0_DAILY_APPROVAL_TICKET_REFRESH_BUILDER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V25_0_DAILY_APPROVAL_TICKET_REFRESH_BUILDER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V25_0_DAILY_APPROVAL_TICKET_REFRESH_BUILDER_BLOCKED_SAFE"

BUILDER_READY = "DAILY_APPROVAL_TICKET_REFRESH_BUILDER_READY"
BUILDER_REVIEW_REQUIRED = "DAILY_APPROVAL_TICKET_REFRESH_BUILDER_REVIEW_REQUIRED"
BUILDER_BLOCKED = "DAILY_APPROVAL_TICKET_REFRESH_BUILDER_BLOCKED"

DEFAULT_OUTPUT_PATH = "outputs/approval_ticket_latest.json"
APPROVAL_NOTICE = "Manual approval required. No trades executed."


@dataclass(frozen=True)
class DailyApprovalTicketRefreshBuilderResult:
    status: str
    builder_status: str
    current_date: str
    output_path: str
    approval_ticket_written: bool
    approval_ticket: dict[str, Any]
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    selected_stock_fund_etf_candidate: str | None
    selected_stock_fund_etf_amount_eur: float
    recommendation_quality_current_data: bool
    portfolio_data_stale_review_required: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "builder_status": self.builder_status,
            "current_date": self.current_date,
            "output_path": self.output_path,
            "approval_ticket_written": self.approval_ticket_written,
            "approval_ticket": self.approval_ticket,
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "selected_stock_fund_etf_candidate": self.selected_stock_fund_etf_candidate,
            "selected_stock_fund_etf_amount_eur": self.selected_stock_fund_etf_amount_eur,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "portfolio_data_stale_review_required": self.portfolio_data_stale_review_required,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return dict(converted) if isinstance(converted, dict) else {}
    return dict(getattr(value, "__dict__", {}))


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _resolve_output_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under_outputs(path: Path, root: str | Path) -> bool:
    resolved = path.resolve()
    output_root = (Path(root) / "outputs").resolve()
    try:
        resolved.relative_to(output_root)
        return True
    except ValueError:
        return False


def _weekly_dual_lane(allocation_result: dict[str, Any]) -> dict[str, Any]:
    return dict(allocation_result.get("weekly_dual_lane_mandate") or {})


def _stock_fund_etf_selection(weekly_dual_lane: dict[str, Any]) -> tuple[str | None, float]:
    lane = dict(weekly_dual_lane.get("stock_fund_etf_lane") or {})
    return lane.get("asset"), float(lane.get("amount") or 0.0)


def _ranked_etf_candidates(allocation_result: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = allocation_result.get("ranked_candidates") or []
    return [dict(item) for item in ranked if isinstance(item, dict)]


def build_daily_approval_ticket(
    *,
    current_date: str,
    bridge_result: CryptoLaneSelectionDailyOperatorBridgeResult,
) -> dict[str, Any]:
    bridge_dict = bridge_result.to_dict()
    daily = _to_dict(getattr(bridge_result, "daily_readiness_result", None))
    allocation_result = _to_dict(daily.get("allocation_result"))
    weekly_dual_lane = _weekly_dual_lane(allocation_result)
    crypto_selection = _to_dict(getattr(bridge_result, "crypto_selection_result", None))
    stock_asset, stock_amount = _stock_fund_etf_selection(weekly_dual_lane)

    warnings = _dedupe(list(getattr(bridge_result, "warnings", ())) + list(daily.get("warnings") or []))
    blockers = _dedupe(list(getattr(bridge_result, "blockers", ())) + list(daily.get("blockers") or []))
    stale_review_required = bool(daily.get("stale_data_review_required"))
    allocation_basis_as_of = str(allocation_result.get("as_of") or current_date)

    return {
        "ticket_id": f"JARVIS-{allocation_basis_as_of}-daily-dual-lane-manual-approval",
        "as_of": allocation_basis_as_of,
        "allocation_basis_as_of": allocation_basis_as_of,
        "generated_at": current_date,
        "ticket_generated_at": current_date,
        "timestamp": current_date,
        "approval_notice": APPROVAL_NOTICE,
        "approval_status": "pending_manual_approval",
        "manual_approval_required": True,
        "final_user_buy_action_required": True,
        "manual_action_guidance": daily.get(
            "manual_action_guidance",
            "Review the recommendation manually before any real-world buy.",
        ),
        "recommendation_quality_current_data": False,
        "portfolio_data_stale_review_required": stale_review_required,
        "data_readiness": daily.get("readiness_status", "unknown"),
        "recommendation_trust": daily.get("recommendation_trust", "review_required"),
        "portfolio_mode": allocation_result.get("portfolio_mode", "unknown"),
        "weekly_budget": allocation_result.get("weekly_budget", 0.0),
        "selected_crypto_candidate": bridge_result.selected_crypto_candidate,
        "selected_crypto_amount_eur": bridge_result.selected_crypto_amount_eur,
        "selected_stock_fund_etf_candidate": stock_asset,
        "selected_stock_fund_etf_amount_eur": stock_amount,
        "crypto_lane_selection": crypto_selection,
        "weekly_dual_lane_mandate": weekly_dual_lane,
        "ideal_allocation": allocation_result.get("ideal_allocation", {}),
        "executable_allocation": allocation_result.get("executable_allocation", {}),
        "etf_scoring_verdict": {
            "selected_ideal_etf": allocation_result.get("selected_ideal_sleeve"),
            "sleeves": _ranked_etf_candidates(allocation_result),
        },
        "freshness_checks": daily.get("freshness_checks", []),
        "bridge_status": bridge_result.bridge_status,
        "daily_operator_status": bridge_result.status,
        "blocked_actions": list(blockers),
        "warnings": list(warnings),
        "safety_checks": [
            APPROVAL_NOTICE,
            "No broker connection.",
            "No credentials.",
            "No private account data ingestion.",
            "No orders created.",
            "No trades executed.",
            "No automatic selling.",
        ],
        "allocation_mutation": False,
        "approval_ticket_written_by_v25": True,
        "buy_request_created": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "trades_executed": False,
        "source_bridge_result": bridge_dict,
    }


def build_daily_approval_ticket_refresh_builder_result(
    *,
    current_date: str | None = None,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    root: str | Path = ".",
    write_ticket: bool = False,
    bridge_result: CryptoLaneSelectionDailyOperatorBridgeResult | None = None,
) -> DailyApprovalTicketRefreshBuilderResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_output = _resolve_output_path(output_path, root)
    if not _is_under_outputs(resolved_output, root):
        blockers.append("approval ticket output_path must remain under outputs/.")

    bridge = bridge_result
    if bridge is None and not blockers:
        bridge = build_crypto_lane_selection_daily_operator_bridge(current_date=current_date_text)

    if bridge is None:
        ticket: dict[str, Any] = {}
    else:
        blockers.extend(getattr(bridge, "blockers", ()) or ())
        warnings.extend(getattr(bridge, "warnings", ()) or ())
        ticket = build_daily_approval_ticket(current_date=current_date_text, bridge_result=bridge)

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)
    wrote = False

    if write_ticket and not unique_blockers:
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(ticket, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        wrote = True

    stale_review_required = bool(ticket.get("portfolio_data_stale_review_required")) if ticket else False
    selected_stock, selected_stock_amount = (
        ticket.get("selected_stock_fund_etf_candidate") if ticket else None,
        float(ticket.get("selected_stock_fund_etf_amount_eur") or 0.0) if ticket else 0.0,
    )

    if unique_blockers:
        status = STATUS_BLOCKED
        builder_status = BUILDER_BLOCKED
    elif stale_review_required:
        status = STATUS_REVIEW_REQUIRED
        builder_status = BUILDER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        builder_status = BUILDER_READY

    return DailyApprovalTicketRefreshBuilderResult(
        status=status,
        builder_status=builder_status,
        current_date=current_date_text,
        output_path=str(resolved_output),
        approval_ticket_written=wrote,
        approval_ticket=ticket,
        selected_crypto_candidate=ticket.get("selected_crypto_candidate") if ticket else None,
        selected_crypto_amount_eur=float(ticket.get("selected_crypto_amount_eur") or 0.0) if ticket else 0.0,
        selected_stock_fund_etf_candidate=selected_stock,
        selected_stock_fund_etf_amount_eur=selected_stock_amount,
        recommendation_quality_current_data=False,
        portfolio_data_stale_review_required=stale_review_required,
        allocation_mutation=False,
        approval_ticket_mutation=wrote,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def format_daily_approval_ticket_refresh_builder(
    result: DailyApprovalTicketRefreshBuilderResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Approval Ticket Refresh Builder",
        f"status: {result.status}",
        f"builder status: {result.builder_status}",
        f"current date: {result.current_date}",
        f"ticket as_of: {result.approval_ticket.get('as_of', 'none') if result.approval_ticket else 'none'}",
        f"ticket generated_at: {result.approval_ticket.get('generated_at', 'none') if result.approval_ticket else 'none'}",
        f"output path: {result.output_path}",
        f"approval ticket written: {result.approval_ticket_written}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"selected stock/fund/ETF candidate: {result.selected_stock_fund_etf_candidate or 'none'}",
        f"selected stock/fund/ETF amount: EUR {result.selected_stock_fund_etf_amount_eur:,.2f}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"portfolio data stale review required: {result.portfolio_data_stale_review_required}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
    ]

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the local manual approval ticket from daily selection.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--write-ticket", action="store_true")
    args = parser.parse_args(argv)

    result = build_daily_approval_ticket_refresh_builder_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_ticket=args.write_ticket,
    )
    print(format_daily_approval_ticket_refresh_builder(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())