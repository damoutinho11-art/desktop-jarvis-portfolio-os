"""J.A.R.V.I.S. v44.0 free research API fetcher adapters + local cache.

v44 starts the real free-data adapter layer behind the v43 router.

Safety/design rules:

- daily mode remains approval-ticket read-only
- cache refresh is explicit through --refresh-free-research-cache
- cache writes are restricted to jarvis/local
- optional API keys are read only from environment variables
- failed free-provider fetches become warnings, not fake confidence
- no broker API, no order API, no execution
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
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
    FreeResearchApiRouterWeeklyPolicyResult,
    build_free_research_api_router_weekly_policy_result,
)

STATUS_READY = "JARVIS_V44_0_FREE_RESEARCH_API_FETCHER_ADAPTERS_LOCAL_CACHE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V44_0_FREE_RESEARCH_API_FETCHER_ADAPTERS_LOCAL_CACHE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V44_0_FREE_RESEARCH_API_FETCHER_ADAPTERS_LOCAL_CACHE_BLOCKED_SAFE"

CACHE_READY = "FREE_RESEARCH_API_FETCHER_LOCAL_CACHE_READY"
CACHE_REVIEW_REQUIRED = "FREE_RESEARCH_API_FETCHER_LOCAL_CACHE_REVIEW_REQUIRED"
CACHE_BLOCKED = "FREE_RESEARCH_API_FETCHER_LOCAL_CACHE_BLOCKED"

NEXT_STAGE = "free_research_api_cache_consumption_and_source_evidence_packs"

DEFAULT_FREE_RESEARCH_CACHE_PATH = "jarvis/local/free_research_api_cache.local.json"


@dataclass(frozen=True)
class ResearchFetchSpec:
    provider_id: str
    lane: str
    data_kind: str
    request_url: str
    headers: Mapping[str, str]
    optional: bool
    requires_api_key: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "lane": self.lane,
            "data_kind": self.data_kind,
            "request_url": self.request_url,
            "headers": dict(self.headers),
            "optional": self.optional,
            "requires_api_key": self.requires_api_key,
        }


@dataclass(frozen=True)
class ResearchCacheRecord:
    provider_id: str
    lane: str
    data_kind: str
    status: str
    fetched_at: str
    current_date: str
    request_url: str
    data_summary: Mapping[str, Any]
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "lane": self.lane,
            "data_kind": self.data_kind,
            "status": self.status,
            "fetched_at": self.fetched_at,
            "current_date": self.current_date,
            "request_url": self.request_url,
            "data_summary": dict(self.data_summary),
            "error": self.error,
        }


@dataclass(frozen=True)
class FreeResearchApiFetcherLocalCacheResult:
    status: str
    cache_status: str
    recommended_next_stage: str
    current_date: str
    operating_mode: str
    refresh_free_research_cache: bool
    cache_path: str
    cache_written: bool
    cache_record_count: int
    provider_fetch_count: int
    provider_success_count: int
    provider_failure_count: int
    upstream_weekly_policy_result: Any
    source_confidence_score: int | None
    source_confidence_grade: str | None
    free_stack_sufficient_for_weekly_investing: bool | None
    paid_api_required_now: bool | None
    broker_api_required_now: bool | None
    daily_check_in_only: bool | None
    weekly_buy_preparation_allowed: bool | None
    manual_buy_action_today: bool | None
    crypto_candidate: str | None
    etf_symbol: str | None
    stock_symbol: str | None
    cache_records: tuple[ResearchCacheRecord, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
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
            "cache_status": self.cache_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "operating_mode": self.operating_mode,
            "refresh_free_research_cache": self.refresh_free_research_cache,
            "cache_path": self.cache_path,
            "cache_written": self.cache_written,
            "cache_record_count": self.cache_record_count,
            "provider_fetch_count": self.provider_fetch_count,
            "provider_success_count": self.provider_success_count,
            "provider_failure_count": self.provider_failure_count,
            "upstream_weekly_policy_result": self.upstream_weekly_policy_result.to_dict()
            if hasattr(self.upstream_weekly_policy_result, "to_dict")
            else dict(getattr(self.upstream_weekly_policy_result, "__dict__", {})),
            "source_confidence_score": self.source_confidence_score,
            "source_confidence_grade": self.source_confidence_grade,
            "free_stack_sufficient_for_weekly_investing": self.free_stack_sufficient_for_weekly_investing,
            "paid_api_required_now": self.paid_api_required_now,
            "broker_api_required_now": self.broker_api_required_now,
            "daily_check_in_only": self.daily_check_in_only,
            "weekly_buy_preparation_allowed": self.weekly_buy_preparation_allowed,
            "manual_buy_action_today": self.manual_buy_action_today,
            "crypto_candidate": self.crypto_candidate,
            "etf_symbol": self.etf_symbol,
            "stock_symbol": self.stock_symbol,
            "cache_records": [record.to_dict() for record in self.cache_records],
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def _env_has_key(env: Mapping[str, str], key: str | None) -> bool:
    if not key:
        return False
    return bool(str(env.get(key, "")).strip())


def _split_csv(value: str | None, default: Sequence[str]) -> tuple[str, ...]:
    if not value:
        return tuple(default)
    parsed = tuple(item.strip() for item in value.split(",") if item.strip())
    return parsed or tuple(default)


def build_free_research_fetch_specs(
    *,
    env: Mapping[str, str] | None = None,
    coin_ids: Sequence[str] = ("bitcoin", "ethereum", "solana"),
    include_fmp: bool = False,
    include_sec: bool = False,
    fmp_symbols: Sequence[str] = ("MSFT", "AAPL", "NVDA"),
    sec_ciks: Sequence[str] = ("0000789019",),
) -> tuple[ResearchFetchSpec, ...]:
    source_env: Mapping[str, str] = env if env is not None else os.environ
    specs: list[ResearchFetchSpec] = []

    coin_ids_text = ",".join(coin_ids)
    coingecko_headers = {"accept": "application/json"}
    coingecko_key = str(source_env.get("JARVIS_COINGECKO_API_KEY", "")).strip()
    if coingecko_key:
        coingecko_headers["x-cg-demo-api-key"] = coingecko_key
    specs.append(
        ResearchFetchSpec(
            provider_id="coingecko_free_or_demo",
            lane="crypto",
            data_kind="simple_price_market_snapshot",
            request_url=(
                "https://api.coingecko.com/api/v3/simple/price"
                f"?ids={coin_ids_text}&vs_currencies=eur,usd"
                "&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            ),
            headers=coingecko_headers,
            optional=False,
            requires_api_key=False,
        )
    )

    specs.append(
        ResearchFetchSpec(
            provider_id="ecb_fx_official",
            lane="fx",
            data_kind="eur_usd_reference_latest",
            request_url="https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1&format=jsondata",
            headers={"accept": "application/json"},
            optional=False,
            requires_api_key=False,
        )
    )

    fmp_key = str(source_env.get("JARVIS_FMP_API_KEY", "")).strip()
    if include_fmp and fmp_key:
        symbols = ",".join(fmp_symbols)
        specs.append(
            ResearchFetchSpec(
                provider_id="fmp_free_optional",
                lane="stocks_etfs_fundamentals",
                data_kind="quote_profile_snapshot",
                request_url=f"https://financialmodelingprep.com/api/v3/quote/{symbols}?apikey={fmp_key}",
                headers={"accept": "application/json"},
                optional=True,
                requires_api_key=True,
            )
        )

    if include_sec:
        user_agent = str(source_env.get("JARVIS_SEC_USER_AGENT", "JarvisPortfolioOS/1.0 research-only")).strip()
        for cik in sec_ciks:
            specs.append(
                ResearchFetchSpec(
                    provider_id="sec_edgar_official",
                    lane="us_stock_validation",
                    data_kind=f"companyfacts_cik_{cik}",
                    request_url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                    headers={"accept": "application/json", "User-Agent": user_agent},
                    optional=True,
                    requires_api_key=False,
                )
            )

    return tuple(specs)


def _summarize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        keys = list(payload.keys())[:8]
        return {
            "payload_type": "dict",
            "top_level_key_count": len(payload),
            "top_level_keys": keys,
        }
    if isinstance(payload, list):
        return {
            "payload_type": "list",
            "item_count": len(payload),
            "first_item_type": type(payload[0]).__name__ if payload else "none",
        }
    return {"payload_type": type(payload).__name__}


def fetch_json_for_spec(
    spec: ResearchFetchSpec,
    *,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: int = 20,
) -> Any:
    request = urllib.request.Request(spec.request_url, headers=dict(spec.headers))
    open_func = opener if opener is not None else urllib.request.urlopen
    with open_func(request, timeout=timeout_seconds) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def fetch_records_for_specs(
    specs: Sequence[ResearchFetchSpec],
    *,
    current_date: str,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: int = 20,
) -> tuple[ResearchCacheRecord, ...]:
    records: list[ResearchCacheRecord] = []
    for spec in specs:
        try:
            payload = fetch_json_for_spec(spec, opener=opener, timeout_seconds=timeout_seconds)
            records.append(
                ResearchCacheRecord(
                    provider_id=spec.provider_id,
                    lane=spec.lane,
                    data_kind=spec.data_kind,
                    status="FETCH_READY",
                    fetched_at=_now_iso(),
                    current_date=current_date,
                    request_url=spec.request_url,
                    data_summary=_summarize_payload(payload),
                    error=None,
                )
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as exc:
            records.append(
                ResearchCacheRecord(
                    provider_id=spec.provider_id,
                    lane=spec.lane,
                    data_kind=spec.data_kind,
                    status="FETCH_FAILED",
                    fetched_at=_now_iso(),
                    current_date=current_date,
                    request_url=spec.request_url,
                    data_summary={},
                    error=str(exc),
                )
            )
    return tuple(records)


def write_free_research_cache(
    *,
    cache_path: str | Path,
    root: str | Path,
    current_date: str,
    operating_mode: str,
    records: Sequence[ResearchCacheRecord],
) -> Path:
    resolved_cache = _resolve_path(cache_path, root)
    if not _is_under(resolved_cache, root, "jarvis/local"):
        raise ValueError("free research cache path must remain under jarvis/local/.")

    success_count = sum(1 for record in records if record.status == "FETCH_READY")
    failure_count = sum(1 for record in records if record.status == "FETCH_FAILED")
    payload = {
        "cache_status": "FREE_RESEARCH_API_CACHE_WRITTEN",
        "current_date": current_date,
        "operating_mode": operating_mode,
        "record_count": len(records),
        "success_count": success_count,
        "failure_count": failure_count,
        "records": [record.to_dict() for record in records],
        "safety": {
            "broker_connection": False,
            "credentials_stored": False,
            "private_account_data_ingested": False,
            "buy_request_created": False,
            "order_created": False,
            "trade_executed": False,
        },
    }
    resolved_cache.parent.mkdir(parents=True, exist_ok=True)
    resolved_cache.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return resolved_cache


def build_free_research_api_fetcher_local_cache_result(
    *,
    current_date: str | None = None,
    operating_mode: str = MODE_DAILY_CHECK_IN,
    refresh_free_research_cache: bool = False,
    cache_path: str | Path = DEFAULT_FREE_RESEARCH_CACHE_PATH,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    env: Mapping[str, str] | None = None,
    include_fmp: bool = False,
    include_sec: bool = False,
    coin_ids: Sequence[str] = ("bitcoin", "ethereum", "solana"),
    fmp_symbols: Sequence[str] = ("MSFT", "AAPL", "NVDA"),
    sec_ciks: Sequence[str] = ("0000789019",),
    opener: Callable[..., Any] | None = None,
    weekly_policy_builder: Callable[..., FreeResearchApiRouterWeeklyPolicyResult] = build_free_research_api_router_weekly_policy_result,
    upstream_weekly_policy_result: FreeResearchApiRouterWeeklyPolicyResult | None = None,
) -> FreeResearchApiFetcherLocalCacheResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    if operating_mode not in {MODE_DAILY_CHECK_IN, MODE_WEEKLY_BUY_PREP}:
        blockers.append("operating_mode must be daily_check_in or weekly_buy_prep.")

    resolved_cache = _resolve_path(cache_path, root)
    if not _is_under(resolved_cache, root, "jarvis/local"):
        blockers.append("free research cache path must remain under jarvis/local/.")

    upstream = upstream_weekly_policy_result
    if upstream is None and not blockers:
        upstream = weekly_policy_builder(
            current_date=current_date_text,
            operating_mode=operating_mode,
            approval_ticket_path=approval_ticket_path,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
        )

    if upstream is not None:
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        warnings.extend(getattr(upstream, "warnings", ()) or [])
        upstream_status = str(getattr(upstream, "status", ""))
        if "BLOCKED" in upstream_status:
            blockers.append("free research API router weekly policy was blocked.")
        elif "READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status:
            warnings.append("free research API router weekly policy requires review.")

    records: tuple[ResearchCacheRecord, ...] = ()
    cache_written = False
    if refresh_free_research_cache and not blockers:
        specs = build_free_research_fetch_specs(
            env=env,
            coin_ids=coin_ids,
            include_fmp=include_fmp,
            include_sec=include_sec,
            fmp_symbols=fmp_symbols,
            sec_ciks=sec_ciks,
        )
        records = fetch_records_for_specs(specs, current_date=current_date_text, opener=opener)
        failure_count = sum(1 for record in records if record.status == "FETCH_FAILED")
        if failure_count:
            warnings.append(f"{failure_count} free research provider fetch(es) failed; cache was written with warnings.")
        try:
            write_free_research_cache(
                cache_path=cache_path,
                root=root,
                current_date=current_date_text,
                operating_mode=operating_mode,
                records=records,
            )
            cache_written = True
        except ValueError as exc:
            blockers.append(str(exc))
    elif not refresh_free_research_cache:
        records = ()

    provider_fetch_count = len(records)
    provider_success_count = sum(1 for record in records if record.status == "FETCH_READY")
    provider_failure_count = sum(1 for record in records if record.status == "FETCH_FAILED")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        cache_status = CACHE_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        cache_status = CACHE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        cache_status = CACHE_READY

    return FreeResearchApiFetcherLocalCacheResult(
        status=status,
        cache_status=cache_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        operating_mode=operating_mode,
        refresh_free_research_cache=refresh_free_research_cache,
        cache_path=str(resolved_cache),
        cache_written=cache_written,
        cache_record_count=len(records),
        provider_fetch_count=provider_fetch_count,
        provider_success_count=provider_success_count,
        provider_failure_count=provider_failure_count,
        upstream_weekly_policy_result=upstream,
        source_confidence_score=getattr(upstream, "source_confidence_score", None),
        source_confidence_grade=getattr(upstream, "source_confidence_grade", None),
        free_stack_sufficient_for_weekly_investing=getattr(upstream, "free_stack_sufficient_for_weekly_investing", None),
        paid_api_required_now=getattr(upstream, "paid_api_required_now", None),
        broker_api_required_now=getattr(upstream, "broker_api_required_now", None),
        daily_check_in_only=getattr(upstream, "daily_check_in_only", None),
        weekly_buy_preparation_allowed=getattr(upstream, "weekly_buy_preparation_allowed", None),
        manual_buy_action_today=getattr(upstream, "manual_buy_action_today", None),
        crypto_candidate=getattr(upstream, "crypto_candidate", None),
        etf_symbol=getattr(upstream, "etf_symbol", None),
        stock_symbol=getattr(upstream, "stock_symbol", None),
        cache_records=records,
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(upstream, "approval_ticket_mutation", False)),
        local_cache_mutation=cache_written,
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


def format_free_research_api_fetcher_local_cache(result: FreeResearchApiFetcherLocalCacheResult) -> str:
    lines = [
        "J.A.R.V.I.S. Free Research API Fetcher Adapters + Local Cache",
        f"status: {result.status}",
        f"cache status: {result.cache_status}",
        f"current date: {result.current_date}",
        f"operating mode: {result.operating_mode}",
        f"refresh free research cache: {result.refresh_free_research_cache}",
        f"cache path: {result.cache_path}",
        f"cache written: {result.cache_written}",
        f"cache record count: {result.cache_record_count}",
        f"provider fetch count: {result.provider_fetch_count}",
        f"provider success count: {result.provider_success_count}",
        f"provider failure count: {result.provider_failure_count}",
        f"source confidence score: {result.source_confidence_score}",
        f"source confidence grade: {result.source_confidence_grade}",
        f"free stack sufficient for weekly investing: {result.free_stack_sufficient_for_weekly_investing}",
        f"paid API required now: {result.paid_api_required_now}",
        f"broker API required now: {result.broker_api_required_now}",
        "",
        "Operating policy:",
        "- daily mode remains approval-ticket read-only",
        "- cache refresh is explicit and writes only under jarvis/local",
        "- weekly mode may prepare the manual review ticket",
        "- failed free-provider fetches become warnings, not fake confidence",
        "- broker APIs remain unnecessary for research and outside execution",
        "",
        "Three-lane snapshot:",
        f"- Crypto: {result.crypto_candidate or 'none'}",
        f"- ETF/fund: {result.etf_symbol or 'none'}",
        f"- Individual stock: {result.stock_symbol or 'none'}",
        "",
        "Cache records:",
    ]

    if result.cache_records:
        for record in result.cache_records:
            lines.append(
                f"- {record.provider_id}: {record.status}; lane={record.lane}; kind={record.data_kind}; error={record.error or 'none'}"
            )
    else:
        lines.append("- none; run with --refresh-free-research-cache to update local cache")

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
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
    parser = argparse.ArgumentParser(description="Run free research API fetcher adapters and local cache.")
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
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--refresh-free-research-cache", action="store_true")
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
    result = build_free_research_api_fetcher_local_cache_result(
        current_date=args.current_date,
        operating_mode=operating_mode,
        refresh_free_research_cache=args.refresh_free_research_cache,
        cache_path=args.free_research_cache_path,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        include_fmp=args.include_fmp,
        include_sec=args.include_sec,
        coin_ids=_split_csv(args.coin_ids, ("bitcoin", "ethereum", "solana")),
        fmp_symbols=_split_csv(args.fmp_symbols, ("MSFT", "AAPL", "NVDA")),
        sec_ciks=_split_csv(args.sec_ciks, ("0000789019",)),
    )
    print(format_free_research_api_fetcher_local_cache(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())