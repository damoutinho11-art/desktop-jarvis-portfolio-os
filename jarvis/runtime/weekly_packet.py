"""J.A.R.V.I.S. v49.0 weekly manual buy packet generator.

This module turns the current validated evidence/result chain into a user-facing
weekly manual buy packet.

It does not approve purchases, assign an amount automatically, create buy
requests, connect to brokers, create orders, or execute trades.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Sequence

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from jarvis.jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from jarvis.jarvis_v39_0_individual_stock_public_ranker import DEFAULT_RANKED_STOCKS_PATH
from jarvis.jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import DEFAULT_APPROVAL_TICKET_PATH
from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import MODE_WEEKLY_BUY_PREP
from jarvis.jarvis_v44_0_free_research_api_fetcher_adapters_local_cache import DEFAULT_FREE_RESEARCH_CACHE_PATH
from jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge import (
    DEFAULT_EVIDENCE_PACK_PATH,
    FreeResearchCacheEvidencePackBridgeResult,
    build_free_research_cache_evidence_pack_bridge_result,
)

STATUS_READY = "JARVIS_V49_0_WEEKLY_MANUAL_BUY_PACKET_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V49_0_WEEKLY_MANUAL_BUY_PACKET_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V49_0_WEEKLY_MANUAL_BUY_PACKET_BLOCKED_SAFE"

PACKET_READY = "WEEKLY_MANUAL_BUY_PACKET_READY"
PACKET_REVIEW_REQUIRED = "WEEKLY_MANUAL_BUY_PACKET_REVIEW_REQUIRED"
PACKET_BLOCKED = "WEEKLY_MANUAL_BUY_PACKET_BLOCKED"

NEXT_STAGE = "manual_weekly_amount_router"


@dataclass(frozen=True)
class WeeklyManualBuyAction:
    lane: str
    title: str
    selected: str
    amount_eur: float | None
    manual_amount_required: bool
    source_confidence: str
    evidence_summary: tuple[str, ...]
    risk_notes: tuple[str, ...]
    action_text: str
    approved_for_purchase: bool
    buy_request_created: bool
    order_created: bool
    trade_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane,
            "title": self.title,
            "selected": self.selected,
            "amount_eur": self.amount_eur,
            "manual_amount_required": self.manual_amount_required,
            "source_confidence": self.source_confidence,
            "evidence_summary": list(self.evidence_summary),
            "risk_notes": list(self.risk_notes),
            "action_text": self.action_text,
            "approved_for_purchase": self.approved_for_purchase,
            "buy_request_created": self.buy_request_created,
            "order_created": self.order_created,
            "trade_executed": self.trade_executed,
        }


@dataclass(frozen=True)
class WeeklyManualBuyPacketResult:
    status: str
    packet_status: str
    recommended_next_stage: str
    current_date: str
    weekly_budget_eur: float | None
    manual_budget_required: bool
    upstream_status: str | None
    source_confidence_score: int | None
    source_confidence_grade: str | None
    free_stack_sufficient_for_weekly_investing: bool | None
    paid_api_required_now: bool | None
    broker_api_required_now: bool | None
    evidence_item_count: int
    usable_evidence_count: int
    failed_evidence_count: int
    crypto_action: WeeklyManualBuyAction
    equity_action: WeeklyManualBuyAction
    stock_review_action: WeeklyManualBuyAction
    allocation_mutation: bool
    approval_ticket_mutation: bool
    evidence_pack_mutation: bool
    local_cache_mutation: bool
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
            "packet_status": self.packet_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "weekly_budget_eur": self.weekly_budget_eur,
            "manual_budget_required": self.manual_budget_required,
            "upstream_status": self.upstream_status,
            "source_confidence_score": self.source_confidence_score,
            "source_confidence_grade": self.source_confidence_grade,
            "free_stack_sufficient_for_weekly_investing": self.free_stack_sufficient_for_weekly_investing,
            "paid_api_required_now": self.paid_api_required_now,
            "broker_api_required_now": self.broker_api_required_now,
            "evidence_item_count": self.evidence_item_count,
            "usable_evidence_count": self.usable_evidence_count,
            "failed_evidence_count": self.failed_evidence_count,
            "crypto_action": self.crypto_action.to_dict(),
            "equity_action": self.equity_action.to_dict(),
            "stock_review_action": self.stock_review_action.to_dict(),
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "evidence_pack_mutation": self.evidence_pack_mutation,
            "local_cache_mutation": self.local_cache_mutation,
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


def _parse_budget(value: float | str | None) -> float | None:
    if value is None:
        return None
    try:
        budget = float(value)
    except (TypeError, ValueError):
        return None
    if budget <= 0:
        return None
    return round(budget, 2)


def _dedupe(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _evidence_lines_for_lane(evidence_items: Sequence[Any], lane: str) -> tuple[str, ...]:
    lines: list[str] = []
    for item in evidence_items:
        item_lane = str(getattr(item, "lane", ""))
        if item_lane != lane:
            continue
        provider = str(getattr(item, "provider_id", "unknown_provider"))
        quality = str(getattr(item, "source_quality", "UNKNOWN_SOURCE_QUALITY"))
        usable = bool(getattr(item, "usable_for_research", False))
        kind = str(getattr(item, "data_kind", "unknown"))
        lines.append(f"{provider}: {quality}; kind={kind}; usable={usable}")
    return tuple(lines)


def _all_evidence_lines(evidence_items: Sequence[Any]) -> tuple[str, ...]:
    lines: list[str] = []
    for item in evidence_items:
        provider = str(getattr(item, "provider_id", "unknown_provider"))
        quality = str(getattr(item, "source_quality", "UNKNOWN_SOURCE_QUALITY"))
        usable = bool(getattr(item, "usable_for_research", False))
        lane = str(getattr(item, "lane", "unknown"))
        lines.append(f"{provider}: {quality}; lane={lane}; usable={usable}")
    return tuple(lines)


def _source_confidence_text(score: int | None, grade: str | None) -> str:
    if score is None and grade is None:
        return "unknown"
    return f"{score} / {grade}"


def _manual_action(
    *,
    lane: str,
    title: str,
    selected: str | None,
    amount_eur: float | None,
    source_confidence: str,
    evidence_summary: Sequence[str],
    risk_notes: Sequence[str],
) -> WeeklyManualBuyAction:
    return WeeklyManualBuyAction(
        lane=lane,
        title=title,
        selected=selected or "none",
        amount_eur=amount_eur,
        manual_amount_required=amount_eur is None,
        source_confidence=source_confidence,
        evidence_summary=tuple(evidence_summary) or ("no refreshed evidence attached to this run",),
        risk_notes=tuple(risk_notes),
        action_text="Diogo reviews and, if satisfied, buys manually outside J.A.R.V.I.S.",
        approved_for_purchase=False,
        buy_request_created=False,
        order_created=False,
        trade_executed=False,
    )


def build_weekly_manual_buy_packet_result(
    *,
    current_date: str | None = None,
    weekly_budget_eur: float | str | None = None,
    refresh_free_research_cache: bool = False,
    write_evidence_pack: bool = False,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    free_research_cache_path: str | Path = DEFAULT_FREE_RESEARCH_CACHE_PATH,
    evidence_pack_path: str | Path = DEFAULT_EVIDENCE_PACK_PATH,
    max_age_days: int = 7,
    include_fmp: bool = False,
    include_sec: bool = False,
    coin_ids: Sequence[str] = ("bitcoin", "ethereum", "solana"),
    fmp_symbols: Sequence[str] = ("MSFT", "AAPL", "NVDA"),
    sec_ciks: Sequence[str] = ("0000789019",),
    upstream_result: FreeResearchCacheEvidencePackBridgeResult | None = None,
    evidence_builder: Callable[..., FreeResearchCacheEvidencePackBridgeResult] = build_free_research_cache_evidence_pack_bridge_result,
) -> WeeklyManualBuyPacketResult:
    current_date_text = current_date or _today_iso()
    budget = _parse_budget(weekly_budget_eur)
    warnings: list[str] = []
    blockers: list[str] = []

    if weekly_budget_eur is not None and budget is None:
        warnings.append("weekly_budget_eur was provided but is not a positive number; manual budget remains required.")

    upstream = upstream_result
    if upstream is None:
        upstream = evidence_builder(
            current_date=current_date_text,
            operating_mode=MODE_WEEKLY_BUY_PREP,
            refresh_free_research_cache=refresh_free_research_cache,
            write_evidence_pack=write_evidence_pack,
            cache_path=free_research_cache_path,
            evidence_pack_path=evidence_pack_path,
            approval_ticket_path=approval_ticket_path,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            max_age_days=max_age_days,
            include_fmp=include_fmp,
            include_sec=include_sec,
            coin_ids=coin_ids,
            fmp_symbols=fmp_symbols,
            sec_ciks=sec_ciks,
        )

    upstream_status = str(getattr(upstream, "status", ""))
    blockers.extend(getattr(upstream, "blockers", ()) or ())
    warnings.extend(getattr(upstream, "warnings", ()) or ())

    if "BLOCKED" in upstream_status:
        blockers.append("upstream evidence-pack bridge was blocked.")
    elif "READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status:
        warnings.append("upstream evidence-pack bridge requires review.")

    evidence_items = tuple(getattr(upstream, "evidence_items", ()) or ())
    source_confidence = _source_confidence_text(
        getattr(upstream, "source_confidence_score", None),
        getattr(upstream, "source_confidence_grade", None),
    )

    crypto_action = _manual_action(
        lane="crypto",
        title="Crypto manual action",
        selected=getattr(upstream, "crypto_candidate", None),
        amount_eur=None,
        source_confidence=source_confidence,
        evidence_summary=_evidence_lines_for_lane(evidence_items, "crypto"),
        risk_notes=(
            "crypto is volatile",
            "manual amount required in v49",
            "no automatic approval or execution",
        ),
    )

    equity_evidence = tuple(
        line
        for line in _all_evidence_lines(evidence_items)
        if "lane=fx" in line or "lane=stocks_etfs" in line or "lane=us_stock" in line
    )
    equity_action = _manual_action(
        lane="stock_fund_etf",
        title="ETF/fund manual action",
        selected=getattr(upstream, "etf_symbol", None),
        amount_eur=None,
        source_confidence=source_confidence,
        evidence_summary=equity_evidence,
        risk_notes=(
            "ETF/fund lane remains manual buy only",
            "manual amount required in v49",
            "public quote/fx evidence should be refreshed before action",
        ),
    )

    stock_review_evidence = (
        _evidence_lines_for_lane(evidence_items, "stocks_etfs_fundamentals")
        + _evidence_lines_for_lane(evidence_items, "us_stock_validation")
    )
    stock_review_action = _manual_action(
        lane="individual_stock_review",
        title="Individual stock review",
        selected=getattr(upstream, "stock_symbol", None),
        amount_eur=None,
        source_confidence=source_confidence,
        evidence_summary=stock_review_evidence
        or ("no refreshed stock-specific evidence attached to this run",),
        risk_notes=(
            "individual stock is review-only in this packet",
            "not automatically preferred over ETF/fund lane",
            "manual approval required before any real-world action",
        ),
    )

    if budget is None:
        warnings.append("weekly budget amount is not assigned by J.A.R.V.I.S.; Diogo must provide/choose the amount manually.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        packet_status = PACKET_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        packet_status = PACKET_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        packet_status = PACKET_READY

    return WeeklyManualBuyPacketResult(
        status=status,
        packet_status=packet_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        weekly_budget_eur=budget,
        manual_budget_required=budget is None,
        upstream_status=upstream_status or None,
        source_confidence_score=getattr(upstream, "source_confidence_score", None),
        source_confidence_grade=getattr(upstream, "source_confidence_grade", None),
        free_stack_sufficient_for_weekly_investing=getattr(upstream, "free_stack_sufficient_for_weekly_investing", None),
        paid_api_required_now=getattr(upstream, "paid_api_required_now", None),
        broker_api_required_now=getattr(upstream, "broker_api_required_now", None),
        evidence_item_count=int(getattr(upstream, "evidence_item_count", len(evidence_items)) or 0),
        usable_evidence_count=int(getattr(upstream, "usable_evidence_count", 0) or 0),
        failed_evidence_count=int(getattr(upstream, "failed_evidence_count", 0) or 0),
        crypto_action=crypto_action,
        equity_action=equity_action,
        stock_review_action=stock_review_action,
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(upstream, "approval_ticket_mutation", False)),
        evidence_pack_mutation=bool(getattr(upstream, "evidence_pack_mutation", False)),
        local_cache_mutation=bool(getattr(upstream, "local_cache_mutation", False)),
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


def _format_action(action: WeeklyManualBuyAction) -> list[str]:
    lines = [
        f"{action.title}:",
        f"- selected: {action.selected}",
        f"- amount EUR: {action.amount_eur if action.amount_eur is not None else 'manual required'}",
        f"- source confidence: {action.source_confidence}",
        "- evidence:",
    ]
    lines.extend(f"  - {line}" for line in action.evidence_summary)
    lines.append("- risk notes:")
    lines.extend(f"  - {line}" for line in action.risk_notes)
    lines.extend(
        [
            f"- action: {action.action_text}",
            f"- approved for purchase: {action.approved_for_purchase}",
            f"- buy request created: {action.buy_request_created}",
            f"- order created: {action.order_created}",
            f"- trade executed: {action.trade_executed}",
        ]
    )
    return lines


def format_weekly_manual_buy_packet(result: WeeklyManualBuyPacketResult) -> str:
    lines = [
        "J.A.R.V.I.S. WEEKLY MANUAL BUY PACKET",
        f"status: {result.status}",
        f"packet status: {result.packet_status}",
        f"current date: {result.current_date}",
        f"weekly budget EUR: {result.weekly_budget_eur if result.weekly_budget_eur is not None else 'manual required'}",
        f"manual budget required: {result.manual_budget_required}",
        f"source confidence score: {result.source_confidence_score}",
        f"source confidence grade: {result.source_confidence_grade}",
        f"free stack sufficient for weekly investing: {result.free_stack_sufficient_for_weekly_investing}",
        f"paid API required now: {result.paid_api_required_now}",
        f"broker API required now: {result.broker_api_required_now}",
        f"evidence item count: {result.evidence_item_count}",
        f"usable evidence count: {result.usable_evidence_count}",
        f"failed evidence count: {result.failed_evidence_count}",
        "",
        "Manual buy packet policy:",
        "- this packet prepares manual review only",
        "- J.A.R.V.I.S. does not approve purchases automatically",
        "- J.A.R.V.I.S. does not assign capital automatically in v49",
        "- Diogo performs any real-world buy manually outside the system",
        "",
    ]
    lines.extend(_format_action(result.crypto_action))
    lines.append("")
    lines.extend(_format_action(result.equity_action))
    lines.append("")
    lines.extend(_format_action(result.stock_review_action))
    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- evidence pack mutation: {result.evidence_pack_mutation}",
            f"- local cache mutation: {result.local_cache_mutation}",
            f"- portfolio state mutation: {result.portfolio_state_mutation}",
            f"- buy request created: {result.buy_request_created}",
            "- no broker connection",
            "- no credentials",
            "- no private account data ingestion",
            "- no orders created",
            "- no trades executed",
            "- final real-world buy remains manual outside J.A.R.V.I.S.",
        ]
    )

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


def _split_csv(value: str, default: Sequence[str]) -> tuple[str, ...]:
    parsed = tuple(item.strip() for item in str(value or "").split(",") if item.strip())
    return parsed or tuple(default)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the weekly manual buy packet.")
    parser.add_argument("--weekly-buy-prep", action="store_true", help="Generate the weekly manual buy packet.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--weekly-budget-eur", default=None)
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--free-research-cache-path", default=DEFAULT_FREE_RESEARCH_CACHE_PATH)
    parser.add_argument("--evidence-pack-path", default=DEFAULT_EVIDENCE_PACK_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--refresh-free-research-cache", action="store_true")
    parser.add_argument("--write-evidence-pack", action="store_true")
    parser.add_argument("--include-fmp", action="store_true")
    parser.add_argument("--include-sec", action="store_true")
    parser.add_argument("--coin-ids", default="bitcoin,ethereum,solana")
    parser.add_argument("--fmp-symbols", default="MSFT,AAPL,NVDA")
    parser.add_argument("--sec-ciks", default="0000789019")
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_weekly_manual_buy_packet_result(
        current_date=args.current_date,
        weekly_budget_eur=args.weekly_budget_eur,
        refresh_free_research_cache=args.refresh_free_research_cache,
        write_evidence_pack=args.write_evidence_pack,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        free_research_cache_path=args.free_research_cache_path,
        evidence_pack_path=args.evidence_pack_path,
        max_age_days=args.max_age_days,
        include_fmp=args.include_fmp,
        include_sec=args.include_sec,
        coin_ids=_split_csv(args.coin_ids, ("bitcoin", "ethereum", "solana")),
        fmp_symbols=_split_csv(args.fmp_symbols, ("MSFT", "AAPL", "NVDA")),
        sec_ciks=_split_csv(args.sec_ciks, ("0000789019",)),
    )
    print(format_weekly_manual_buy_packet(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())