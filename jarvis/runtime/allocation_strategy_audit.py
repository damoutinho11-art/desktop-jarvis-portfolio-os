"""J.A.R.V.I.S. v51.0 allocation strategy and data coverage audit.

This stage separates the current weekly contribution router from a true full
portfolio allocation engine.

It is audit/gate only. It does not mutate portfolio allocation, approve buys,
create buy requests, connect to brokers, create orders, or execute trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from jarvis.jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from jarvis.jarvis_v39_0_individual_stock_public_ranker import DEFAULT_RANKED_STOCKS_PATH
from jarvis.jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import DEFAULT_APPROVAL_TICKET_PATH
from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import MODE_DAILY_CHECK_IN
from jarvis.jarvis_v44_0_free_research_api_fetcher_adapters_local_cache import DEFAULT_FREE_RESEARCH_CACHE_PATH
from jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge import (
    DEFAULT_EVIDENCE_PACK_PATH,
    FreeResearchCacheEvidencePackBridgeResult,
    build_free_research_cache_evidence_pack_bridge_result,
)

STATUS_READY = "JARVIS_V51_0_ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V51_0_ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V51_0_ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_BLOCKED_SAFE"

AUDIT_READY = "ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_READY"
AUDIT_REVIEW_REQUIRED = "ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_REVIEW_REQUIRED"
AUDIT_BLOCKED = "ALLOCATION_STRATEGY_DATA_COVERAGE_AUDIT_BLOCKED"

NEXT_STAGE = "manual_portfolio_snapshot_intake"
DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH = "jarvis/local/manual_portfolio_snapshot.local.json"
DEFAULT_OUTPUT_PATH = "outputs/allocation_strategy_data_coverage_audit_latest.json"


@dataclass(frozen=True)
class DataCoverageItem:
    key: str
    label: str
    required_for_weekly_router: bool
    required_for_full_allocation: bool
    available: bool
    source: str
    status: str
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "required_for_weekly_router": self.required_for_weekly_router,
            "required_for_full_allocation": self.required_for_full_allocation,
            "available": self.available,
            "source": self.source,
            "status": self.status,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AllocationStrategyDataCoverageAuditResult:
    status: str
    audit_status: str
    recommended_next_stage: str
    current_date: str
    strategy_name: str
    implemented_strategy_summary: str
    target_strategy_summary: str
    weekly_router_allowed: bool
    full_allocation_allowed: bool
    full_allocation_blocked_reason: str
    current_weekly_router_policy: tuple[str, ...]
    target_allocator_policy: tuple[str, ...]
    coverage_items: tuple[DataCoverageItem, ...]
    weekly_router_required_coverage_ready: bool
    full_allocation_required_coverage_ready: bool
    available_count: int
    missing_weekly_router_required_count: int
    missing_full_allocation_required_count: int
    missing_full_allocation_required_keys: tuple[str, ...]
    upstream_status: str | None
    source_confidence_score: int | None
    source_confidence_grade: str | None
    paid_api_required_now: bool | None
    broker_api_required_now: bool | None
    free_stack_sufficient_for_weekly_investing: bool | None
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "audit_status": self.audit_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "strategy_name": self.strategy_name,
            "implemented_strategy_summary": self.implemented_strategy_summary,
            "target_strategy_summary": self.target_strategy_summary,
            "weekly_router_allowed": self.weekly_router_allowed,
            "full_allocation_allowed": self.full_allocation_allowed,
            "full_allocation_blocked_reason": self.full_allocation_blocked_reason,
            "current_weekly_router_policy": list(self.current_weekly_router_policy),
            "target_allocator_policy": list(self.target_allocator_policy),
            "coverage_items": [item.to_dict() for item in self.coverage_items],
            "weekly_router_required_coverage_ready": self.weekly_router_required_coverage_ready,
            "full_allocation_required_coverage_ready": self.full_allocation_required_coverage_ready,
            "available_count": self.available_count,
            "missing_weekly_router_required_count": self.missing_weekly_router_required_count,
            "missing_full_allocation_required_count": self.missing_full_allocation_required_count,
            "missing_full_allocation_required_keys": list(self.missing_full_allocation_required_keys),
            "upstream_status": self.upstream_status,
            "source_confidence_score": self.source_confidence_score,
            "source_confidence_grade": self.source_confidence_grade,
            "paid_api_required_now": self.paid_api_required_now,
            "broker_api_required_now": self.broker_api_required_now,
            "free_stack_sufficient_for_weekly_investing": self.free_stack_sufficient_for_weekly_investing,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _dedupe(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _safe_json_load(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _manual_snapshot_coverage(path: Path) -> tuple[bool, bool, bool, bool, str]:
    payload = _safe_json_load(path)
    if not payload:
        return False, False, False, False, "manual portfolio snapshot not found or unreadable"

    if bool(payload.get("is_template", False)):
        return False, False, False, False, "manual portfolio snapshot is still a template"

    holdings = payload.get("holdings")
    cash = payload.get("cash_eur")
    cost_basis = payload.get("cost_basis")
    brokerless = payload.get("brokerless_manual_snapshot", True)

    holdings_ready = isinstance(holdings, list) and len(holdings) > 0
    cash_ready = isinstance(cash, (int, float)) and cash >= 0
    cost_basis_ready = isinstance(cost_basis, (dict, list)) and len(cost_basis) > 0
    brokerless_ready = bool(brokerless)

    return holdings_ready, cash_ready, cost_basis_ready, brokerless_ready, "manual portfolio snapshot file present"


def _evidence_items(upstream: Any) -> tuple[Any, ...]:
    return tuple(getattr(upstream, "evidence_items", ()) or ())


def _has_usable_lane(evidence_items: Sequence[Any], lanes: set[str]) -> bool:
    return any(
        str(getattr(item, "lane", "")) in lanes and bool(getattr(item, "usable_for_research", False))
        for item in evidence_items
    )


def _has_stock_specific_evidence(evidence_items: Sequence[Any]) -> bool:
    return _has_usable_lane(evidence_items, {"stocks_etfs_fundamentals", "us_stock_validation"})


def _item(
    *,
    key: str,
    label: str,
    weekly: bool,
    full: bool,
    available: bool,
    source: str,
    notes: Sequence[str],
) -> DataCoverageItem:
    if available:
        status = "COVERED"
    elif weekly:
        status = "MISSING_WEEKLY_ROUTER_REQUIRED"
    elif full:
        status = "MISSING_FULL_ALLOCATION_REQUIRED"
    else:
        status = "OPTIONAL_MISSING"
    return DataCoverageItem(
        key=key,
        label=label,
        required_for_weekly_router=weekly,
        required_for_full_allocation=full,
        available=available,
        source=source,
        status=status,
        notes=tuple(notes),
    )


def _build_coverage_items(
    *,
    upstream: Any,
    manual_snapshot_path: Path,
) -> tuple[DataCoverageItem, ...]:
    evidence = _evidence_items(upstream)
    holdings_ready, cash_ready, cost_basis_ready, brokerless_ready, snapshot_note = _manual_snapshot_coverage(manual_snapshot_path)
    crypto_evidence_ready = _has_usable_lane(evidence, {"crypto"})
    etf_fx_evidence_ready = _has_usable_lane(evidence, {"fx", "stocks_etfs", "etf_quote"})
    stock_evidence_ready = _has_stock_specific_evidence(evidence)

    return (
        _item(
            key="crypto_public_evidence",
            label="Crypto public/free evidence",
            weekly=True,
            full=True,
            available=crypto_evidence_ready,
            source="CoinGecko free/demo evidence pack",
            notes=("required before routing weekly crypto amount",),
        ),
        _item(
            key="etf_fx_public_evidence",
            label="ETF/fund public quote or FX evidence",
            weekly=True,
            full=True,
            available=etf_fx_evidence_ready,
            source="ECB FX / Yahoo public quote evidence chain",
            notes=("required before routing weekly ETF/fund amount",),
        ),
        _item(
            key="stock_specific_public_evidence",
            label="Individual-stock public/fundamental evidence",
            weekly=False,
            full=True,
            available=stock_evidence_ready,
            source="FMP optional / SEC official / future stock evidence lanes",
            notes=("missing stock-specific evidence keeps individual stock review-only",),
        ),
        _item(
            key="manual_holdings_snapshot",
            label="Manual current holdings snapshot",
            weekly=False,
            full=True,
            available=holdings_ready,
            source=str(manual_snapshot_path),
            notes=(snapshot_note, "needed for concentration-aware allocation"),
        ),
        _item(
            key="manual_cash_snapshot",
            label="Manual available cash snapshot",
            weekly=False,
            full=True,
            available=cash_ready,
            source=str(manual_snapshot_path),
            notes=(snapshot_note, "needed for full portfolio allocation and cash drag review"),
        ),
        _item(
            key="manual_cost_basis",
            label="Manual cost basis snapshot",
            weekly=False,
            full=True,
            available=cost_basis_ready,
            source=str(manual_snapshot_path),
            notes=(snapshot_note, "needed for tax/realized-risk aware allocation"),
        ),
        _item(
            key="brokerless_manual_snapshot_policy",
            label="Brokerless manual snapshot policy",
            weekly=False,
            full=True,
            available=brokerless_ready,
            source=str(manual_snapshot_path),
            notes=("manual snapshot must not require broker credentials or broker APIs",),
        ),
        _item(
            key="correlation_risk_model",
            label="Cross-lane correlation/risk model",
            weekly=False,
            full=True,
            available=False,
            source="not implemented",
            notes=("needed before claiming optimal portfolio allocation",),
        ),
        _item(
            key="dynamic_target_policy",
            label="Dynamic target allocation policy",
            weekly=False,
            full=True,
            available=False,
            source="not implemented",
            notes=("needed before replacing v50 manual router with allocation brain",),
        ),
    )


def build_allocation_strategy_data_coverage_audit_result(
    *,
    current_date: str | None = None,
    refresh_free_research_cache: bool = False,
    write_evidence_pack: bool = False,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    free_research_cache_path: str | Path = DEFAULT_FREE_RESEARCH_CACHE_PATH,
    evidence_pack_path: str | Path = DEFAULT_EVIDENCE_PACK_PATH,
    manual_portfolio_snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    max_age_days: int = 7,
    include_fmp: bool = False,
    include_sec: bool = False,
    coin_ids: Sequence[str] = ("bitcoin", "ethereum", "solana"),
    fmp_symbols: Sequence[str] = ("MSFT", "AAPL", "NVDA"),
    sec_ciks: Sequence[str] = ("0000789019",),
    upstream_result: FreeResearchCacheEvidencePackBridgeResult | None = None,
    evidence_builder: Callable[..., FreeResearchCacheEvidencePackBridgeResult] = build_free_research_cache_evidence_pack_bridge_result,
) -> AllocationStrategyDataCoverageAuditResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    upstream = upstream_result
    if upstream is None:
        upstream = evidence_builder(
            current_date=current_date_text,
            operating_mode=MODE_DAILY_CHECK_IN,
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
        blockers.append("upstream evidence bridge was blocked.")
    elif "READY" not in upstream_status:
        warnings.append("upstream evidence bridge is not ready.")

    coverage_items = _build_coverage_items(
        upstream=upstream,
        manual_snapshot_path=Path(manual_portfolio_snapshot_path),
    )
    weekly_missing = tuple(item for item in coverage_items if item.required_for_weekly_router and not item.available)
    full_missing = tuple(item for item in coverage_items if item.required_for_full_allocation and not item.available)

    weekly_ready = len(weekly_missing) == 0
    full_ready = len(full_missing) == 0

    if not weekly_ready:
        warnings.append("weekly amount routing should stay review-required because required weekly evidence is missing.")
    if not full_ready:
        warnings.append("full portfolio allocation is blocked until required data coverage is complete.")

    full_reason = (
        "full allocation allowed by data coverage gate"
        if full_ready
        else "missing required data: " + ", ".join(item.key for item in full_missing)
    )

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        audit_status = AUDIT_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        audit_status = AUDIT_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        audit_status = AUDIT_READY

    return AllocationStrategyDataCoverageAuditResult(
        status=status,
        audit_status=audit_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        strategy_name="quality_first_dynamic_allocator_data_gate",
        implemented_strategy_summary="v50 implements a weekly manual amount router, not a full portfolio allocator.",
        target_strategy_summary="full allocator should rank opportunities by evidence quality, freshness, risk, diversification, holdings, cash, cost basis, concentration, and missing-data penalties.",
        weekly_router_allowed=weekly_ready and not unique_blockers,
        full_allocation_allowed=full_ready and not unique_blockers,
        full_allocation_blocked_reason=full_reason,
        current_weekly_router_policy=(
            "weekly contribution routing only",
            "evidence-aware crypto and ETF/fund lanes",
            "crypto capped at 40 percent",
            "individual stock remains review-only at 0 EUR",
            "manual review only, no execution",
        ),
        target_allocator_policy=(
            "separate weekly contribution routing from full portfolio allocation",
            "require manual holdings/cash/cost-basis snapshot before full allocation",
            "penalize missing or stale data",
            "respect risk caps and concentration limits",
            "use free sources first; paid API only if a proven data gap remains",
            "never require broker API for research or manual-buy workflow",
        ),
        coverage_items=coverage_items,
        weekly_router_required_coverage_ready=weekly_ready,
        full_allocation_required_coverage_ready=full_ready,
        available_count=sum(1 for item in coverage_items if item.available),
        missing_weekly_router_required_count=len(weekly_missing),
        missing_full_allocation_required_count=len(full_missing),
        missing_full_allocation_required_keys=tuple(item.key for item in full_missing),
        upstream_status=upstream_status or None,
        source_confidence_score=getattr(upstream, "source_confidence_score", None),
        source_confidence_grade=getattr(upstream, "source_confidence_grade", None),
        paid_api_required_now=getattr(upstream, "paid_api_required_now", None),
        broker_api_required_now=getattr(upstream, "broker_api_required_now", None),
        free_stack_sufficient_for_weekly_investing=getattr(upstream, "free_stack_sufficient_for_weekly_investing", None),
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(upstream, "approval_ticket_mutation", False)),
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def _write_output(result: AllocationStrategyDataCoverageAuditResult, output_path: str | Path) -> None:
    path = Path(output_path)
    if path.is_absolute() or not str(path).replace("\\", "/").startswith("outputs/"):
        raise ValueError("allocation strategy audit output path must remain under outputs/.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_allocation_strategy_data_coverage_audit(
    result: AllocationStrategyDataCoverageAuditResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. ALLOCATION STRATEGY + DATA COVERAGE AUDIT",
        f"status: {result.status}",
        f"audit status: {result.audit_status}",
        f"current date: {result.current_date}",
        f"strategy name: {result.strategy_name}",
        f"implemented strategy: {result.implemented_strategy_summary}",
        f"target strategy: {result.target_strategy_summary}",
        f"weekly router allowed: {result.weekly_router_allowed}",
        f"full allocation allowed: {result.full_allocation_allowed}",
        f"full allocation blocked reason: {result.full_allocation_blocked_reason}",
        f"source confidence score: {result.source_confidence_score}",
        f"source confidence grade: {result.source_confidence_grade}",
        f"free stack sufficient for weekly investing: {result.free_stack_sufficient_for_weekly_investing}",
        f"paid API required now: {result.paid_api_required_now}",
        f"broker API required now: {result.broker_api_required_now}",
        f"available coverage items: {result.available_count}",
        f"missing weekly-router required items: {result.missing_weekly_router_required_count}",
        f"missing full-allocation required items: {result.missing_full_allocation_required_count}",
        "",
        "Current weekly router policy:",
    ]
    lines.extend(f"- {item}" for item in result.current_weekly_router_policy)
    lines.extend(["", "Target allocation policy:"])
    lines.extend(f"- {item}" for item in result.target_allocator_policy)

    lines.extend(["", "Data coverage:"])
    for item in result.coverage_items:
        lines.extend(
            [
                f"- {item.key}: {item.status}",
                f"  label: {item.label}",
                f"  weekly required: {item.required_for_weekly_router}",
                f"  full allocation required: {item.required_for_full_allocation}",
                f"  source: {item.source}",
            ]
        )
        for note in item.notes:
            lines.append(f"  note: {note}")

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            "- no broker connection",
            "- no credentials",
            "- no private account data ingestion",
            "- no orders created",
            "- no trades executed",
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
    parser = argparse.ArgumentParser(description="Audit allocation strategy and data coverage.")
    parser.add_argument("--allocation-strategy-audit", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--free-research-cache-path", default=DEFAULT_FREE_RESEARCH_CACHE_PATH)
    parser.add_argument("--evidence-pack-path", default=DEFAULT_EVIDENCE_PACK_PATH)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--write-output", action="store_true")
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

    result = build_allocation_strategy_data_coverage_audit_result(
        current_date=args.current_date,
        refresh_free_research_cache=args.refresh_free_research_cache,
        write_evidence_pack=args.write_evidence_pack,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        free_research_cache_path=args.free_research_cache_path,
        evidence_pack_path=args.evidence_pack_path,
        manual_portfolio_snapshot_path=args.manual_portfolio_snapshot_path,
        max_age_days=args.max_age_days,
        include_fmp=args.include_fmp,
        include_sec=args.include_sec,
        coin_ids=_split_csv(args.coin_ids, ("bitcoin", "ethereum", "solana")),
        fmp_symbols=_split_csv(args.fmp_symbols, ("MSFT", "AAPL", "NVDA")),
        sec_ciks=_split_csv(args.sec_ciks, ("0000789019",)),
    )
    if args.write_output:
        _write_output(result, args.output_path)
    print(format_allocation_strategy_data_coverage_audit(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())