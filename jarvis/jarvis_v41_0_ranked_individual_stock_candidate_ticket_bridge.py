"""J.A.R.V.I.S. v41.0 ranked individual stock candidate ticket bridge.

v41 bridges the top v40/v39 ranked individual-stock candidate into the manual
approval-ticket flow as review-only.

It does not approve the stock, assign a buy amount, create a buy request, connect
brokers, create orders, or trade.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from .jarvis_v39_0_individual_stock_public_ranker import (
    DEFAULT_RANKED_STOCKS_PATH,
    DECISION_STATUS_NOT_APPROVED,
)
from .jarvis_v40_0_individual_stock_public_universe_bootstrap import (
    IndividualStockPublicUniverseBootstrapResult,
    build_individual_stock_public_universe_bootstrap_result,
    format_individual_stock_public_universe_bootstrap,
)

STATUS_READY = "JARVIS_V41_0_RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V41_0_RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V41_0_RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "RANKED_INDIVIDUAL_STOCK_CANDIDATE_TICKET_BRIDGE_BLOCKED"

NEXT_STAGE = "three_lane_manual_action_brief_crypto_etf_stock"

DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"

STOCK_TICKET_DECISION_STATUS = "RANKED_INDIVIDUAL_STOCK_CANDIDATE_BRIDGED_FOR_REVIEW_NOT_APPROVED"


@dataclass(frozen=True)
class RankedIndividualStockCandidateTicketBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    current_date: str
    approval_ticket_path: str
    stock_universe_path: str
    stock_signals_path: str
    ranked_stocks_path: str
    stock_candidate_available: bool
    stock_ticket_written: bool
    top_ranked_stock_id: str | None
    top_ranked_symbol: str | None
    top_ranked_name: str | None
    top_ranked_close_price: float | None
    top_ranked_currency: str | None
    top_ranked_ranking_score: float | None
    top_ranked_decision_status: str | None
    upstream_bootstrap_result: Any
    recommendation_quality_current_data: bool
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
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "approval_ticket_path": self.approval_ticket_path,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "ranked_stocks_path": self.ranked_stocks_path,
            "stock_candidate_available": self.stock_candidate_available,
            "stock_ticket_written": self.stock_ticket_written,
            "top_ranked_stock_id": self.top_ranked_stock_id,
            "top_ranked_symbol": self.top_ranked_symbol,
            "top_ranked_name": self.top_ranked_name,
            "top_ranked_close_price": self.top_ranked_close_price,
            "top_ranked_currency": self.top_ranked_currency,
            "top_ranked_ranking_score": self.top_ranked_ranking_score,
            "top_ranked_decision_status": self.top_ranked_decision_status,
            "upstream_bootstrap_result": self.upstream_bootstrap_result.to_dict()
            if hasattr(self.upstream_bootstrap_result, "to_dict")
            else dict(getattr(self.upstream_bootstrap_result, "__dict__", {})),
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
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


def _today_iso() -> str:
    return date.today().isoformat()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if len(text) >= 10:
        text = text[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _resolve_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under(path: Path, root: str | Path, child: str) -> bool:
    resolved = path.resolve()
    allowed_root = (Path(root) / child).resolve()
    try:
        resolved.relative_to(allowed_root)
        return True
    except ValueError:
        return False


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _candidate_attr(candidate: Any, name: str, default: Any = None) -> Any:
    if isinstance(candidate, dict):
        return candidate.get(name, default)
    return getattr(candidate, name, default)


def _top_ranked_candidate(upstream: Any) -> Any | None:
    ranker = getattr(upstream, "upstream_ranker_result", None)
    candidates = tuple(getattr(ranker, "ranked_candidates", ()) or ())
    if not candidates:
        return None
    return candidates[0]


def build_stock_ticket_payload(*, candidate: Any, current_date: str) -> dict[str, Any]:
    return {
        "decision_status": STOCK_TICKET_DECISION_STATUS,
        "bridged_at": current_date,
        "stock_id": _candidate_attr(candidate, "stock_id"),
        "rank": _candidate_attr(candidate, "rank"),
        "name": _candidate_attr(candidate, "name"),
        "ticker": _candidate_attr(candidate, "ticker"),
        "symbol": _candidate_attr(candidate, "symbol"),
        "exchange": _candidate_attr(candidate, "exchange"),
        "market": _candidate_attr(candidate, "market"),
        "sector": _candidate_attr(candidate, "sector"),
        "provider": _candidate_attr(candidate, "provider"),
        "currency": _candidate_attr(candidate, "currency"),
        "source_url": _candidate_attr(candidate, "source_url"),
        "source_as_of": _candidate_attr(candidate, "source_as_of"),
        "close_price": _candidate_attr(candidate, "close_price"),
        "priority_score": _candidate_attr(candidate, "priority_score"),
        "ranking_score": _candidate_attr(candidate, "ranking_score"),
        "source_status": _candidate_attr(candidate, "source_status"),
        "original_ranker_decision_status": _candidate_attr(candidate, "decision_status"),
        "amount_eur": None,
        "manual_amount_required": True,
        "approved_for_purchase": False,
        "buy_request_created": False,
        "order_created": False,
        "trade_executed": False,
        "safety_note": "Review-only ranked stock candidate. Not approved; Diogo must decide manually outside J.A.R.V.I.S.",
    }


def bridge_stock_candidate_into_ticket(
    *,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    root: str | Path = ".",
    current_date: str,
    candidate: Any,
) -> Path:
    resolved = _resolve_path(approval_ticket_path, root)
    if not _is_under(resolved, root, "outputs"):
        raise ValueError("approval ticket path must remain under outputs/.")
    if not resolved.exists():
        raise FileNotFoundError(f"approval ticket path does not exist: {resolved}")

    ticket = _read_json(resolved)
    ticket["selected_individual_stock_candidate"] = build_stock_ticket_payload(
        candidate=candidate,
        current_date=current_date,
    )
    ticket["individual_stock_source_metadata"] = {
        "metadata_status": "INDIVIDUAL_STOCK_RANKED_CANDIDATE_METADATA_READY",
        "bridged_at": current_date,
        "source_lane": "individual_stock_public_ranker",
        "decision_status": STOCK_TICKET_DECISION_STATUS,
        "approved_for_purchase": False,
        "manual_amount_required": True,
        "buy_request_created": False,
        "order_created": False,
        "trade_executed": False,
    }
    _write_json(resolved, ticket)
    return resolved


def build_ranked_individual_stock_candidate_ticket_bridge_result(
    *,
    current_date: str | None = None,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    bootstrap_stock_universe: bool = False,
    write_stock_signals: bool = False,
    write_ranked_stocks: bool = False,
    write_stock_ticket: bool = False,
    upstream_bootstrap_result: IndividualStockPublicUniverseBootstrapResult | None = None,
) -> RankedIndividualStockCandidateTicketBridgeResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_ticket = _resolve_path(approval_ticket_path, root)
    resolved_universe = _resolve_path(stock_universe_path, root)
    resolved_signals = _resolve_path(stock_signals_path, root)
    resolved_ranked = _resolve_path(ranked_stocks_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    for label, path in (
        ("stock universe path", resolved_universe),
        ("stock signals path", resolved_signals),
        ("ranked stocks path", resolved_ranked),
    ):
        if not _is_under(path, root, "jarvis/local"):
            blockers.append(f"{label} must remain under jarvis/local/.")

    upstream = None
    if not blockers:
        upstream = upstream_bootstrap_result if upstream_bootstrap_result is not None else build_individual_stock_public_universe_bootstrap_result(
            current_date=current_date_text,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
            bootstrap_stock_universe=bootstrap_stock_universe,
            write_stock_signals=write_stock_signals,
            write_ranked_stocks=write_ranked_stocks,
        )
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        upstream_status = str(getattr(upstream, "status", ""))
        upstream_warnings = tuple(getattr(upstream, "warnings", ()) or ())
        if "BLOCKED" in upstream_status:
            blockers.append("individual stock public universe bootstrap was blocked.")
    else:
        upstream_status = ""
        upstream_warnings = ()

    candidate = _top_ranked_candidate(upstream) if upstream is not None else None
    if candidate is None and not blockers:
        warnings.extend(upstream_warnings)
        if upstream_status and ("READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status):
            warnings.append("individual stock public universe bootstrap requires review.")
        warnings.append("no ranked individual stock candidate is available to bridge.")

    ticket_written = False
    if write_stock_ticket and candidate is not None and not blockers:
        try:
            bridge_stock_candidate_into_ticket(
                approval_ticket_path=approval_ticket_path,
                root=root,
                current_date=current_date_text,
                candidate=candidate,
            )
            ticket_written = True
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            blockers.append(str(exc))

    if candidate is not None and not write_stock_ticket and not blockers:
        warnings.append("ranked stock candidate is available but stock ticket bridge was not written.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return RankedIndividualStockCandidateTicketBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        approval_ticket_path=str(resolved_ticket),
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        ranked_stocks_path=str(resolved_ranked),
        stock_candidate_available=candidate is not None,
        stock_ticket_written=ticket_written,
        top_ranked_stock_id=_candidate_attr(candidate, "stock_id") if candidate is not None else None,
        top_ranked_symbol=_candidate_attr(candidate, "symbol") if candidate is not None else None,
        top_ranked_name=_candidate_attr(candidate, "name") if candidate is not None else None,
        top_ranked_close_price=_candidate_attr(candidate, "close_price") if candidate is not None else None,
        top_ranked_currency=_candidate_attr(candidate, "currency") if candidate is not None else None,
        top_ranked_ranking_score=_candidate_attr(candidate, "ranking_score") if candidate is not None else None,
        top_ranked_decision_status=_candidate_attr(candidate, "decision_status") if candidate is not None else None,
        upstream_bootstrap_result=upstream,
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=ticket_written,
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


def _format_upstream_summary(upstream: Any) -> str:
    if upstream is None:
        return "none"
    return "\n".join(
        [
            "J.A.R.V.I.S. Individual Stock Public Universe Bootstrap",
            f"status: {getattr(upstream, 'status', 'unknown')}",
            f"bootstrap universe written: {getattr(upstream, 'bootstrap_universe_written', 'unknown')}",
            f"stock signals written: {getattr(upstream, 'stock_signals_written', 'unknown')}",
            f"ranked stocks written: {getattr(upstream, 'ranked_stocks_written', 'unknown')}",
            f"ranked candidate count: {getattr(upstream, 'ranked_candidate_count', 'unknown')}",
            f"top ranked stock id: {getattr(upstream, 'top_ranked_stock_id', None) or 'none'}",
            f"top ranked symbol: {getattr(upstream, 'top_ranked_symbol', None) or 'none'}",
        ]
    )


def format_ranked_individual_stock_candidate_ticket_bridge(result: RankedIndividualStockCandidateTicketBridgeResult) -> str:
    lines = [
        "J.A.R.V.I.S. Ranked Individual Stock Candidate Ticket Bridge",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"current date: {result.current_date}",
        f"approval ticket path: {result.approval_ticket_path}",
        f"stock universe path: {result.stock_universe_path}",
        f"stock signals path: {result.stock_signals_path}",
        f"ranked stocks path: {result.ranked_stocks_path}",
        f"stock candidate available: {result.stock_candidate_available}",
        f"stock ticket written: {result.stock_ticket_written}",
        f"top ranked stock id: {result.top_ranked_stock_id or 'none'}",
        f"top ranked symbol: {result.top_ranked_symbol or 'none'}",
        f"top ranked name: {result.top_ranked_name or 'none'}",
        f"top ranked close price: {result.top_ranked_close_price if result.top_ranked_close_price is not None else 'none'}",
        f"top ranked currency: {result.top_ranked_currency or 'none'}",
        f"top ranked ranking score: {result.top_ranked_ranking_score if result.top_ranked_ranking_score is not None else 'none'}",
        f"top ranked decision status: {result.top_ranked_decision_status or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "Important:",
        "- ranked stock candidate is review-only",
        "- non-top upstream universe warnings do not approve or block this bridge after a top candidate is written",
        "- no stock is approved for purchase",
        "- amount_eur is not assigned by this bridge",
        "- final real-world buy remains manual outside J.A.R.V.I.S.",
        "",
        "Safety:",
        f"- allocation mutation: {result.allocation_mutation}",
        f"- approval ticket mutation: {result.approval_ticket_mutation}",
        f"- portfolio state mutation: {result.portfolio_state_mutation}",
        f"- buy request created: {result.buy_request_created}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
        "",
        "Upstream bootstrap summary:",
        _format_upstream_summary(result.upstream_bootstrap_result),
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
    parser = argparse.ArgumentParser(description="Bridge ranked stock candidate into manual approval ticket as review-only.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run ranked stock candidate ticket bridge.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--bootstrap-stock-universe", action="store_true", help="Write starter public stock universe under jarvis/local.")
    parser.add_argument("--write-stock-signals", action="store_true", help="Write local individual stock public signals under jarvis/local.")
    parser.add_argument("--write-ranked-stocks", action="store_true", help="Write local ranked individual stock candidates under jarvis/local.")
    parser.add_argument("--write-stock-ticket", action="store_true", help="Bridge the top ranked stock candidate into the manual approval ticket.")
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

    result = build_ranked_individual_stock_candidate_ticket_bridge_result(
        current_date=args.current_date,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        bootstrap_stock_universe=args.bootstrap_stock_universe,
        write_stock_signals=args.write_stock_signals,
        write_ranked_stocks=args.write_ranked_stocks,
        write_stock_ticket=args.write_stock_ticket,
    )
    print(format_ranked_individual_stock_candidate_ticket_bridge(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())