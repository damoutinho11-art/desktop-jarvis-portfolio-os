"""J.A.R.V.I.S. v45.0 free research cache evidence pack bridge.

v45 consumes the v44 local free-research cache and turns it into a compact
evidence pack that later scoring/ranking stages can read.

Safety/design rules:

- daily mode stays non-mutating by default
- cache refresh is still explicit
- evidence-pack writing is explicit through --write-evidence-pack
- cache reads are restricted to jarvis/local
- evidence-pack writes are restricted to outputs
- no approval, no buy request, no broker, no orders, no trades
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from .jarvis_v39_0_individual_stock_public_ranker import DEFAULT_RANKED_STOCKS_PATH
from .jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import DEFAULT_APPROVAL_TICKET_PATH
from .jarvis_v43_0_free_research_api_router_weekly_policy import (
    MODE_DAILY_CHECK_IN,
    MODE_WEEKLY_BUY_PREP,
)
from .jarvis_v44_0_free_research_api_fetcher_adapters_local_cache import (
    DEFAULT_FREE_RESEARCH_CACHE_PATH,
    FreeResearchApiFetcherLocalCacheResult,
    ResearchCacheRecord,
    build_free_research_api_fetcher_local_cache_result,
)

STATUS_READY = "JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_BLOCKED_SAFE"

EVIDENCE_READY = "FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY"
EVIDENCE_REVIEW_REQUIRED = "FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_REVIEW_REQUIRED"
EVIDENCE_BLOCKED = "FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_BLOCKED"

NEXT_STAGE = "evidence_pack_consumption_in_three_lane_source_confidence_gate"

DEFAULT_EVIDENCE_PACK_PATH = "outputs/free_research_evidence_pack_latest.json"


@dataclass(frozen=True)
class FreeResearchEvidenceItem:
    provider_id: str
    lane: str
    data_kind: str
    status: str
    fetched_at: str | None
    current_date: str | None
    request_url: str | None
    source_quality: str
    usable_for_research: bool
    warning: str | None
    data_summary: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "lane": self.lane,
            "data_kind": self.data_kind,
            "status": self.status,
            "fetched_at": self.fetched_at,
            "current_date": self.current_date,
            "request_url": self.request_url,
            "source_quality": self.source_quality,
            "usable_for_research": self.usable_for_research,
            "warning": self.warning,
            "data_summary": dict(self.data_summary),
        }


@dataclass(frozen=True)
class FreeResearchCacheEvidencePackBridgeResult:
    status: str
    evidence_status: str
    recommended_next_stage: str
    current_date: str
    operating_mode: str
    refresh_free_research_cache: bool
    write_evidence_pack: bool
    cache_path: str
    evidence_pack_path: str
    cache_available: bool
    evidence_pack_written: bool
    cache_record_count: int
    evidence_item_count: int
    usable_evidence_count: int
    failed_evidence_count: int
    upstream_fetcher_result: Any
    source_confidence_score: int | None
    source_confidence_grade: str | None
    free_stack_sufficient_for_weekly_investing: bool | None
    paid_api_required_now: bool | None
    broker_api_required_now: bool | None
    crypto_candidate: str | None
    etf_symbol: str | None
    stock_symbol: str | None
    evidence_items: tuple[FreeResearchEvidenceItem, ...]
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
            "evidence_status": self.evidence_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "operating_mode": self.operating_mode,
            "refresh_free_research_cache": self.refresh_free_research_cache,
            "write_evidence_pack": self.write_evidence_pack,
            "cache_path": self.cache_path,
            "evidence_pack_path": self.evidence_pack_path,
            "cache_available": self.cache_available,
            "evidence_pack_written": self.evidence_pack_written,
            "cache_record_count": self.cache_record_count,
            "evidence_item_count": self.evidence_item_count,
            "usable_evidence_count": self.usable_evidence_count,
            "failed_evidence_count": self.failed_evidence_count,
            "upstream_fetcher_result": self.upstream_fetcher_result.to_dict()
            if hasattr(self.upstream_fetcher_result, "to_dict")
            else dict(getattr(self.upstream_fetcher_result, "__dict__", {})),
            "source_confidence_score": self.source_confidence_score,
            "source_confidence_grade": self.source_confidence_grade,
            "free_stack_sufficient_for_weekly_investing": self.free_stack_sufficient_for_weekly_investing,
            "paid_api_required_now": self.paid_api_required_now,
            "broker_api_required_now": self.broker_api_required_now,
            "crypto_candidate": self.crypto_candidate,
            "etf_symbol": self.etf_symbol,
            "stock_symbol": self.stock_symbol,
            "evidence_items": [item.to_dict() for item in self.evidence_items],
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


def _record_get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _record_to_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, dict):
        return dict(record)
    if hasattr(record, "to_dict"):
        return dict(record.to_dict())
    return dict(getattr(record, "__dict__", {}))


def _source_quality(provider_id: str, status: str) -> str:
    if status != "FETCH_READY":
        return "FAILED"
    if provider_id in {"sec_edgar_official", "ecb_fx_official"}:
        return "OFFICIAL_FREE_SOURCE_READY"
    if provider_id == "coingecko_free_or_demo":
        return "PUBLIC_CRYPTO_SOURCE_READY"
    if provider_id == "fmp_free_optional":
        return "OPTIONAL_RESEARCH_API_SOURCE_READY"
    if provider_id == "yahoo_chart_public_fallback":
        return "PUBLIC_PRICE_FALLBACK_READY"
    return "FREE_SOURCE_READY"


def _build_evidence_item(record: Any) -> FreeResearchEvidenceItem:
    record_dict = _record_to_dict(record)
    provider_id = str(record_dict.get("provider_id") or "unknown_provider")
    status = str(record_dict.get("status") or "UNKNOWN")
    error = record_dict.get("error")
    warning = str(error) if error else None
    usable = status == "FETCH_READY"
    return FreeResearchEvidenceItem(
        provider_id=provider_id,
        lane=str(record_dict.get("lane") or "unknown"),
        data_kind=str(record_dict.get("data_kind") or "unknown"),
        status=status,
        fetched_at=record_dict.get("fetched_at"),
        current_date=record_dict.get("current_date"),
        request_url=record_dict.get("request_url"),
        source_quality=_source_quality(provider_id, status),
        usable_for_research=usable,
        warning=warning,
        data_summary=dict(record_dict.get("data_summary") or {}),
    )


def _read_cache_records(cache_path: Path) -> tuple[dict[str, Any], ...]:
    payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
    records = payload.get("records", [])
    if not isinstance(records, list):
        return ()
    return tuple(record for record in records if isinstance(record, dict))


def _write_evidence_pack(
    *,
    evidence_pack_path: str | Path,
    root: str | Path,
    current_date: str,
    operating_mode: str,
    cache_path: str,
    evidence_items: Sequence[FreeResearchEvidenceItem],
) -> Path:
    resolved_evidence = _resolve_path(evidence_pack_path, root)
    if not _is_under(resolved_evidence, root, "outputs"):
        raise ValueError("evidence pack path must remain under outputs/.")

    usable_count = sum(1 for item in evidence_items if item.usable_for_research)
    failed_count = sum(1 for item in evidence_items if not item.usable_for_research)
    payload = {
        "evidence_pack_status": "FREE_RESEARCH_EVIDENCE_PACK_WRITTEN",
        "current_date": current_date,
        "operating_mode": operating_mode,
        "cache_path": cache_path,
        "evidence_item_count": len(evidence_items),
        "usable_evidence_count": usable_count,
        "failed_evidence_count": failed_count,
        "evidence_items": [item.to_dict() for item in evidence_items],
        "safety": {
            "approval_ticket_mutated_by_evidence_pack": False,
            "broker_connection": False,
            "credentials_stored": False,
            "private_account_data_ingested": False,
            "buy_request_created": False,
            "order_created": False,
            "trade_executed": False,
        },
    }
    resolved_evidence.parent.mkdir(parents=True, exist_ok=True)
    resolved_evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return resolved_evidence


def build_free_research_cache_evidence_pack_bridge_result(
    *,
    current_date: str | None = None,
    operating_mode: str = MODE_DAILY_CHECK_IN,
    refresh_free_research_cache: bool = False,
    write_evidence_pack: bool = False,
    cache_path: str | Path = DEFAULT_FREE_RESEARCH_CACHE_PATH,
    evidence_pack_path: str | Path = DEFAULT_EVIDENCE_PACK_PATH,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    include_fmp: bool = False,
    include_sec: bool = False,
    coin_ids: Sequence[str] = ("bitcoin", "ethereum", "solana"),
    fmp_symbols: Sequence[str] = ("MSFT", "AAPL", "NVDA"),
    sec_ciks: Sequence[str] = ("0000789019",),
    opener: Callable[..., Any] | None = None,
    fetcher_builder: Callable[..., FreeResearchApiFetcherLocalCacheResult] = build_free_research_api_fetcher_local_cache_result,
    upstream_fetcher_result: FreeResearchApiFetcherLocalCacheResult | None = None,
) -> FreeResearchCacheEvidencePackBridgeResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    if operating_mode not in {MODE_DAILY_CHECK_IN, MODE_WEEKLY_BUY_PREP}:
        blockers.append("operating_mode must be daily_check_in or weekly_buy_prep.")

    resolved_cache = _resolve_path(cache_path, root)
    resolved_evidence = _resolve_path(evidence_pack_path, root)

    if not _is_under(resolved_cache, root, "jarvis/local"):
        blockers.append("free research cache path must remain under jarvis/local/.")
    if not _is_under(resolved_evidence, root, "outputs"):
        blockers.append("evidence pack path must remain under outputs/.")

    upstream = upstream_fetcher_result
    if upstream is None and not blockers:
        upstream = fetcher_builder(
            current_date=current_date_text,
            operating_mode=operating_mode,
            refresh_free_research_cache=refresh_free_research_cache,
            cache_path=cache_path,
            approval_ticket_path=approval_ticket_path,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
            include_fmp=include_fmp,
            include_sec=include_sec,
            coin_ids=coin_ids,
            fmp_symbols=fmp_symbols,
            sec_ciks=sec_ciks,
            opener=opener,
        )

    if upstream is not None:
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        warnings.extend(getattr(upstream, "warnings", ()) or [])
        upstream_status = str(getattr(upstream, "status", ""))
        if "BLOCKED" in upstream_status:
            blockers.append("free research API fetcher local cache was blocked.")
        elif "READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status:
            warnings.append("free research API fetcher local cache requires review.")

    raw_records: tuple[Any, ...] = tuple(getattr(upstream, "cache_records", ()) or ()) if upstream is not None else ()
    cache_available = bool(raw_records)

    if not raw_records and resolved_cache.exists():
        try:
            raw_records = _read_cache_records(resolved_cache)
            cache_available = True
        except (json.JSONDecodeError, OSError) as exc:
            blockers.append(f"free research cache could not be read: {exc}")

    evidence_items = tuple(_build_evidence_item(record) for record in raw_records)
    failed_count = sum(1 for item in evidence_items if not item.usable_for_research)
    usable_count = sum(1 for item in evidence_items if item.usable_for_research)

    if (refresh_free_research_cache or write_evidence_pack) and not evidence_items and not blockers:
        warnings.append("no free research cache records are available for evidence pack.")

    if failed_count:
        warnings.append(f"{failed_count} evidence item(s) are not usable for research.")

    evidence_written = False
    if write_evidence_pack and not blockers:
        try:
            _write_evidence_pack(
                evidence_pack_path=evidence_pack_path,
                root=root,
                current_date=current_date_text,
                operating_mode=operating_mode,
                cache_path=str(resolved_cache),
                evidence_items=evidence_items,
            )
            evidence_written = True
        except ValueError as exc:
            blockers.append(str(exc))

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        evidence_status = EVIDENCE_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        evidence_status = EVIDENCE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        evidence_status = EVIDENCE_READY

    return FreeResearchCacheEvidencePackBridgeResult(
        status=status,
        evidence_status=evidence_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        operating_mode=operating_mode,
        refresh_free_research_cache=refresh_free_research_cache,
        write_evidence_pack=write_evidence_pack,
        cache_path=str(resolved_cache),
        evidence_pack_path=str(resolved_evidence),
        cache_available=cache_available,
        evidence_pack_written=evidence_written,
        cache_record_count=len(raw_records),
        evidence_item_count=len(evidence_items),
        usable_evidence_count=usable_count,
        failed_evidence_count=failed_count,
        upstream_fetcher_result=upstream,
        source_confidence_score=getattr(upstream, "source_confidence_score", None),
        source_confidence_grade=getattr(upstream, "source_confidence_grade", None),
        free_stack_sufficient_for_weekly_investing=getattr(upstream, "free_stack_sufficient_for_weekly_investing", None),
        paid_api_required_now=getattr(upstream, "paid_api_required_now", None),
        broker_api_required_now=getattr(upstream, "broker_api_required_now", None),
        crypto_candidate=getattr(upstream, "crypto_candidate", None),
        etf_symbol=getattr(upstream, "etf_symbol", None),
        stock_symbol=getattr(upstream, "stock_symbol", None),
        evidence_items=evidence_items,
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(upstream, "approval_ticket_mutation", False)),
        evidence_pack_mutation=evidence_written,
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


def format_free_research_cache_evidence_pack_bridge(result: FreeResearchCacheEvidencePackBridgeResult) -> str:
    lines = [
        "J.A.R.V.I.S. Free Research Cache Evidence Pack Bridge",
        f"status: {result.status}",
        f"evidence status: {result.evidence_status}",
        f"current date: {result.current_date}",
        f"operating mode: {result.operating_mode}",
        f"refresh free research cache: {result.refresh_free_research_cache}",
        f"write evidence pack: {result.write_evidence_pack}",
        f"cache path: {result.cache_path}",
        f"evidence pack path: {result.evidence_pack_path}",
        f"cache available: {result.cache_available}",
        f"evidence pack written: {result.evidence_pack_written}",
        f"cache record count: {result.cache_record_count}",
        f"evidence item count: {result.evidence_item_count}",
        f"usable evidence count: {result.usable_evidence_count}",
        f"failed evidence count: {result.failed_evidence_count}",
        f"source confidence score: {result.source_confidence_score}",
        f"source confidence grade: {result.source_confidence_grade}",
        f"free stack sufficient for weekly investing: {result.free_stack_sufficient_for_weekly_investing}",
        f"paid API required now: {result.paid_api_required_now}",
        f"broker API required now: {result.broker_api_required_now}",
        "",
        "Evidence policy:",
        "- cache reads are restricted to jarvis/local",
        "- evidence-pack writes are explicit and restricted to outputs",
        "- evidence pack does not approve buys or mutate the approval ticket",
        "- failed provider records stay visible as review warnings",
        "- broker APIs remain unnecessary for research and outside execution",
        "",
        "Three-lane snapshot:",
        f"- Crypto: {result.crypto_candidate or 'none'}",
        f"- ETF/fund: {result.etf_symbol or 'none'}",
        f"- Individual stock: {result.stock_symbol or 'none'}",
        "",
        "Evidence items:",
    ]

    if result.evidence_items:
        for item in result.evidence_items:
            lines.append(
                f"- {item.provider_id}: {item.source_quality}; lane={item.lane}; kind={item.data_kind}; usable={item.usable_for_research}"
            )
    else:
        lines.append("- none")

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bridge free research cache into an evidence pack.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily check-in mode.")
    mode.add_argument("--weekly-buy-prep", action="store_true", help="Run weekly manual buy preparation mode.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--free-research-cache-path", default=DEFAULT_FREE_RESEARCH_CACHE_PATH)
    parser.add_argument("--evidence-pack-path", default=DEFAULT_EVIDENCE_PACK_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--refresh-free-research-cache", action="store_true")
    parser.add_argument("--write-evidence-pack", action="store_true")
    parser.add_argument("--include-fmp", action="store_true", help="Use optional FMP fetch only when JARVIS_FMP_API_KEY exists.")
    parser.add_argument("--include-sec", action="store_true", help="Use optional SEC EDGAR validation fetch.")
    parser.add_argument("--coin-ids", default="bitcoin,ethereum,solana")
    parser.add_argument("--fmp-symbols", default="MSFT,AAPL,NVDA")
    parser.add_argument("--sec-ciks", default="0000789019")
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

    operating_mode = MODE_WEEKLY_BUY_PREP if args.weekly_buy_prep else MODE_DAILY_CHECK_IN
    result = build_free_research_cache_evidence_pack_bridge_result(
        current_date=args.current_date,
        operating_mode=operating_mode,
        refresh_free_research_cache=args.refresh_free_research_cache,
        write_evidence_pack=args.write_evidence_pack,
        cache_path=args.free_research_cache_path,
        evidence_pack_path=args.evidence_pack_path,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        include_fmp=args.include_fmp,
        include_sec=args.include_sec,
        coin_ids=tuple(item.strip() for item in args.coin_ids.split(",") if item.strip()),
        fmp_symbols=tuple(item.strip() for item in args.fmp_symbols.split(",") if item.strip()),
        sec_ciks=tuple(item.strip() for item in args.sec_ciks.split(",") if item.strip()),
    )
    print(format_free_research_cache_evidence_pack_bridge(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())