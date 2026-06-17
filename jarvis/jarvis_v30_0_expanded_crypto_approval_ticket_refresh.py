"""J.A.R.V.I.S. v30.0 expanded crypto approval ticket refresh.

v30 writes a local manual-approval ticket from the v29 expanded crypto
allocation eligibility bridge when explicitly requested.

It refreshes the local approval-ticket artifact so the crypto lane can reflect
the best eligible expanded-ranked crypto candidate, while preserving the stock /
fund / ETF lane from the allocation engine and all no-execution safety boundaries.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v29_0_expanded_crypto_allocation_eligibility_bridge import (
    ExpandedCryptoAllocationEligibilityBridgeResult,
    build_expanded_crypto_allocation_eligibility_bridge,
    build_expanded_crypto_allocation_eligibility_console_output,
)

STATUS_READY = "JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_BLOCKED_SAFE"

BUILDER_READY = "EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_READY"
BUILDER_REVIEW_REQUIRED = "EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_REVIEW_REQUIRED"
BUILDER_BLOCKED = "EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_BLOCKED"

NEXT_STAGE = "expanded_crypto_manual_buy_brief_refresh"

DEFAULT_OUTPUT_PATH = "outputs/approval_ticket_latest.json"
APPROVAL_NOTICE = "Manual approval required. No trades executed."


@dataclass(frozen=True)
class ExpandedCryptoApprovalTicketRefreshResult:
    status: str
    builder_status: str
    recommended_next_stage: str
    current_date: str
    output_path: str
    approval_ticket_written: bool
    approval_ticket: dict[str, Any]
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    selected_stock_fund_etf_candidate: str | None
    selected_stock_fund_etf_amount_eur: float
    allocation_basis_as_of: str
    ticket_generated_at: str
    expanded_crypto_candidate_reassigned: bool
    approval_ticket_refresh_required: bool
    recommendation_quality_current_data: bool
    portfolio_data_stale_review_required: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    portfolio_state_mutation: bool
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
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "output_path": self.output_path,
            "approval_ticket_written": self.approval_ticket_written,
            "approval_ticket": self.approval_ticket,
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "selected_stock_fund_etf_candidate": self.selected_stock_fund_etf_candidate,
            "selected_stock_fund_etf_amount_eur": self.selected_stock_fund_etf_amount_eur,
            "allocation_basis_as_of": self.allocation_basis_as_of,
            "ticket_generated_at": self.ticket_generated_at,
            "expanded_crypto_candidate_reassigned": self.expanded_crypto_candidate_reassigned,
            "approval_ticket_refresh_required": self.approval_ticket_refresh_required,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "portfolio_data_stale_review_required": self.portfolio_data_stale_review_required,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
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
    outputs_root = (Path(root) / "outputs").resolve()
    try:
        resolved.relative_to(outputs_root)
        return True
    except ValueError:
        return False


def _nested_allocation_result(v29_result: Any) -> dict[str, Any]:
    v29 = _to_dict(v29_result)
    upstream = _to_dict(v29.get("upstream_daily_result"))
    daily = _to_dict(upstream.get("daily_readiness_result"))
    return _to_dict(daily.get("allocation_result"))


def _nested_daily_readiness(v29_result: Any) -> dict[str, Any]:
    v29 = _to_dict(v29_result)
    upstream = _to_dict(v29.get("upstream_daily_result"))
    return _to_dict(upstream.get("daily_readiness_result"))


def _stock_fund_etf_selection(allocation_result: dict[str, Any]) -> tuple[str | None, float]:
    weekly_dual_lane = dict(allocation_result.get("weekly_dual_lane_mandate") or {})
    lane = dict(weekly_dual_lane.get("stock_fund_etf_lane") or {})
    return lane.get("asset"), round(float(lane.get("amount") or 0.0), 2)


def _ranked_etf_candidates(allocation_result: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = allocation_result.get("ranked_candidates") or []
    return [dict(item) for item in ranked if isinstance(item, dict)]


def _existing_ticket_asof_mismatch_blocker(message: str) -> bool:
    return "Approval ticket file as_of does not match current allocation engine result" in str(message)


def _filter_resolved_ticket_blockers(
    blockers: list[str],
    *,
    ticket: dict[str, Any],
    write_ticket: bool,
) -> list[str]:
    if not write_ticket:
        return blockers
    if str(ticket.get("as_of") or "") != str(ticket.get("allocation_basis_as_of") or ""):
        return blockers
    return [item for item in blockers if not _existing_ticket_asof_mismatch_blocker(item)]


def build_expanded_crypto_approval_ticket(
    *,
    current_date: str,
    v29_result: ExpandedCryptoAllocationEligibilityBridgeResult,
) -> dict[str, Any]:
    v29_dict = v29_result.to_dict() if hasattr(v29_result, "to_dict") else _to_dict(v29_result)
    allocation_result = _nested_allocation_result(v29_result)
    daily = _nested_daily_readiness(v29_result)
    allocation_basis_as_of = str(allocation_result.get("as_of") or current_date)
    stock_asset, stock_amount = _stock_fund_etf_selection(allocation_result)

    warnings = _dedupe(
        list(getattr(v29_result, "warnings", ()) or [])
        + list(daily.get("warnings") or [])
    )
    blockers = _dedupe(
        list(getattr(v29_result, "blockers", ()) or [])
        + list(daily.get("blockers") or [])
    )

    stale_review_required = bool(
        daily.get("stale_data_review_required")
        or "STALE" in str(daily.get("readiness_status", ""))
        or "REVIEW_REQUIRED" in str(getattr(v29_result, "status", ""))
    )

    return {
        "ticket_id": f"JARVIS-{allocation_basis_as_of}-expanded-crypto-daily-dual-lane-manual-approval",
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
            "Review the refreshed ticket manually before any real-world buy.",
        ),
        "recommendation_quality_current_data": False,
        "portfolio_data_stale_review_required": stale_review_required,
        "data_readiness": daily.get("readiness_status", "review_required"),
        "recommendation_trust": daily.get("recommendation_trust", "review_required"),
        "portfolio_mode": allocation_result.get("portfolio_mode", "unknown"),
        "weekly_budget": allocation_result.get("weekly_budget", 0.0),
        "selected_crypto_candidate": v29_result.selected_crypto_candidate,
        "selected_crypto_amount_eur": v29_result.selected_crypto_amount_eur,
        "selected_stock_fund_etf_candidate": stock_asset,
        "selected_stock_fund_etf_amount_eur": stock_amount,
        "expanded_crypto_candidate_reassigned": v29_result.reassigned_from_allocation_basis,
        "allocation_basis_crypto_candidate": v29_result.allocation_basis_candidate,
        "allocation_basis_crypto_amount_eur": v29_result.allocation_basis_amount_eur,
        "approval_ticket_refresh_required": v29_result.approval_ticket_refresh_required,
        "expanded_crypto_allocation_eligibility": {
            "selected_crypto_candidate": v29_result.selected_crypto_candidate,
            "selected_crypto_amount_eur": v29_result.selected_crypto_amount_eur,
            "selected_crypto_rank": v29_result.selected_crypto_rank,
            "selected_crypto_score": v29_result.selected_crypto_score,
            "reassigned_from_allocation_basis": v29_result.reassigned_from_allocation_basis,
            "full_public_data_coverage": v29_result.full_public_data_coverage,
            "expanded_crypto_ranking_ready": v29_result.expanded_crypto_ranking_ready,
            "candidate_decisions": [item.to_dict() for item in v29_result.candidate_decisions],
        },
        "weekly_dual_lane_mandate": allocation_result.get("weekly_dual_lane_mandate", {}),
        "ideal_allocation": allocation_result.get("ideal_allocation", {}),
        "executable_allocation": {
            **dict(allocation_result.get("executable_allocation") or {}),
            str(v29_result.selected_crypto_candidate or "crypto"): v29_result.selected_crypto_amount_eur,
        },
        "etf_scoring_verdict": {
            "selected_ideal_etf": allocation_result.get("selected_ideal_sleeve"),
            "sleeves": _ranked_etf_candidates(allocation_result),
        },
        "freshness_checks": daily.get("freshness_checks", []),
        "bridge_status": v29_result.bridge_status,
        "daily_operator_status": v29_result.status,
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
        "approval_ticket_written_by_v30": True,
        "portfolio_state_mutation": False,
        "buy_request_created": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "trades_executed": False,
        "source_bridge_summary": {
            "status": v29_dict.get("status"),
            "bridge_status": v29_dict.get("bridge_status"),
            "allocation_basis_candidate": v29_result.allocation_basis_candidate,
            "allocation_basis_amount_eur": v29_result.allocation_basis_amount_eur,
            "selected_expanded_crypto_candidate": v29_result.selected_crypto_candidate,
            "selected_expanded_crypto_amount_eur": v29_result.selected_crypto_amount_eur,
            "selected_expanded_crypto_rank": v29_result.selected_crypto_rank,
            "selected_expanded_crypto_score": v29_result.selected_crypto_score,
            "reassigned_from_allocation_basis": v29_result.reassigned_from_allocation_basis,
            "approval_ticket_refresh_required": v29_result.approval_ticket_refresh_required,
            "full_public_data_coverage": v29_result.full_public_data_coverage,
            "expanded_crypto_ranking_ready": v29_result.expanded_crypto_ranking_ready,
            "candidate_decisions": [item.to_dict() for item in v29_result.candidate_decisions],
        },
    }


def build_expanded_crypto_approval_ticket_refresh_result(
    *,
    current_date: str | None = None,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    root: str | Path = ".",
    write_ticket: bool = False,
    v29_result: ExpandedCryptoAllocationEligibilityBridgeResult | None = None,
    v29_builder: Callable[..., ExpandedCryptoAllocationEligibilityBridgeResult] = build_expanded_crypto_allocation_eligibility_bridge,
    write_local_signals: bool = False,
) -> ExpandedCryptoApprovalTicketRefreshResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_output = _resolve_output_path(output_path, root)
    if not _is_under_outputs(resolved_output, root):
        blockers.append("approval ticket output_path must remain under outputs/.")

    bridge = None
    if not blockers:
        bridge = v29_result if v29_result is not None else v29_builder(
            current_date=current_date_text,
            write_local_signals=write_local_signals,
        )

    if bridge is None:
        ticket: dict[str, Any] = {}
    else:
        blockers.extend(getattr(bridge, "blockers", ()) or [])
        warnings.extend(getattr(bridge, "warnings", ()) or [])
        ticket = build_expanded_crypto_approval_ticket(
            current_date=current_date_text,
            v29_result=bridge,
        )
        blockers = _filter_resolved_ticket_blockers(
            blockers,
            ticket=ticket,
            write_ticket=write_ticket,
        )

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    wrote = False
    if write_ticket and not unique_blockers:
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(ticket, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        wrote = True

    stale_review_required = bool(ticket.get("portfolio_data_stale_review_required")) if ticket else False

    if unique_blockers:
        status = STATUS_BLOCKED
        builder_status = BUILDER_BLOCKED
    elif stale_review_required:
        status = STATUS_REVIEW_REQUIRED
        builder_status = BUILDER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        builder_status = BUILDER_READY

    return ExpandedCryptoApprovalTicketRefreshResult(
        status=status,
        builder_status=builder_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        output_path=str(resolved_output),
        approval_ticket_written=wrote,
        approval_ticket=ticket,
        selected_crypto_candidate=ticket.get("selected_crypto_candidate") if ticket else None,
        selected_crypto_amount_eur=float(ticket.get("selected_crypto_amount_eur") or 0.0) if ticket else 0.0,
        selected_stock_fund_etf_candidate=ticket.get("selected_stock_fund_etf_candidate") if ticket else None,
        selected_stock_fund_etf_amount_eur=float(ticket.get("selected_stock_fund_etf_amount_eur") or 0.0) if ticket else 0.0,
        allocation_basis_as_of=str(ticket.get("allocation_basis_as_of") or "") if ticket else "",
        ticket_generated_at=str(ticket.get("generated_at") or "") if ticket else "",
        expanded_crypto_candidate_reassigned=bool(ticket.get("expanded_crypto_candidate_reassigned")) if ticket else False,
        approval_ticket_refresh_required=bool(ticket.get("approval_ticket_refresh_required")) if ticket else False,
        recommendation_quality_current_data=False,
        portfolio_data_stale_review_required=stale_review_required,
        allocation_mutation=False,
        approval_ticket_mutation=wrote,
        portfolio_state_mutation=False,
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


def format_expanded_crypto_approval_ticket_refresh(
    result: ExpandedCryptoApprovalTicketRefreshResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Expanded Crypto Approval Ticket Refresh",
        f"status: {result.status}",
        f"builder status: {result.builder_status}",
        f"current date: {result.current_date}",
        f"ticket as_of: {result.allocation_basis_as_of or 'none'}",
        f"ticket generated_at: {result.ticket_generated_at or 'none'}",
        f"output path: {result.output_path}",
        f"approval ticket written: {result.approval_ticket_written}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"selected stock/fund/ETF candidate: {result.selected_stock_fund_etf_candidate or 'none'}",
        f"selected stock/fund/ETF amount: EUR {result.selected_stock_fund_etf_amount_eur:,.2f}",
        f"expanded crypto candidate reassigned: {result.expanded_crypto_candidate_reassigned}",
        f"approval ticket refresh required: {result.approval_ticket_refresh_required}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"portfolio data stale review required: {result.portfolio_data_stale_review_required}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
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

    if result.approval_ticket:
        lines.extend(
            [
                "",
                "Approval ticket summary:",
                f"- crypto lane: {result.approval_ticket.get('selected_crypto_candidate')} EUR {float(result.approval_ticket.get('selected_crypto_amount_eur') or 0.0):,.2f}",
                f"- stock/fund/ETF lane: {result.approval_ticket.get('selected_stock_fund_etf_candidate')} EUR {float(result.approval_ticket.get('selected_stock_fund_etf_amount_eur') or 0.0):,.2f}",
                f"- approval status: {result.approval_ticket.get('approval_status')}",
                "- final real-world buy remains manual outside J.A.R.V.I.S.",
            ]
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the local approval ticket from expanded crypto selection.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily approval-ticket refresh preview.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--write-ticket", action="store_true", help="Write refreshed local approval ticket under outputs/.")
    parser.add_argument("--write-local-signals", action="store_true", help="Write normalized local public crypto signals under jarvis/local.")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    result = build_expanded_crypto_approval_ticket_refresh_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_ticket=args.write_ticket,
        write_local_signals=args.write_local_signals,
    )
    print(format_expanded_crypto_approval_ticket_refresh(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())