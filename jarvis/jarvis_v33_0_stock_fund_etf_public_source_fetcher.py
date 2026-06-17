"""J.A.R.V.I.S. v33.0 stock/fund/ETF public source fetcher.

v33 adds the ETF/fund lane's first real public data intake bridge.

It is strict by design:
- no invented ETF tickers
- no static market data
- no stale fixture promotion
- no source metadata marked ready unless fresh public data was fetched
- no broker/private-account connection
- no orders/trades

The source manifest is local and user/operator controlled because abstract sleeves
such as quality_etf are not real market symbols. v33 can create a local template,
but it will not treat that template as live data until real provider/symbol entries
are filled and fetched.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import DEFAULT_OUTPUT_PATH
from .jarvis_v32_0_stock_fund_etf_data_freshness_engine import (
    StockFundEtfDataFreshnessEngineResult,
    build_stock_fund_etf_data_freshness_engine_result,
    format_stock_fund_etf_data_freshness_engine,
)

STATUS_READY = "JARVIS_V33_0_STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V33_0_STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V33_0_STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_BLOCKED_SAFE"

FETCHER_READY = "STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_READY"
FETCHER_REVIEW_REQUIRED = "STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_REVIEW_REQUIRED"
FETCHER_BLOCKED = "STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_BLOCKED"

NEXT_STAGE = "stock_fund_etf_public_source_ticket_metadata_bridge"

DEFAULT_SOURCE_MANIFEST_PATH = "jarvis/local/stock_fund_etf_public_sources.local.json"
DEFAULT_OUTPUT_SIGNALS_PATH = "jarvis/local/stock_fund_etf_public_signals.local.json"

SOURCE_READY = "ETF_PUBLIC_SOURCE_READY"
SOURCE_MISSING = "ETF_PUBLIC_SOURCE_MISSING"
SOURCE_UNSUPPORTED = "ETF_PUBLIC_SOURCE_UNSUPPORTED"
SOURCE_FETCH_FAILED = "ETF_PUBLIC_SOURCE_FETCH_FAILED"
SOURCE_STALE = "ETF_PUBLIC_SOURCE_STALE"
SOURCE_INVALID = "ETF_PUBLIC_SOURCE_INVALID"

SUPPORTED_PROVIDERS = ("yahoo_chart", "stooq_csv")


@dataclass(frozen=True)
class StockFundEtfPublicSourceSignal:
    candidate_id: str
    provider: str | None
    symbol: str | None
    source_url: str | None
    source_as_of: str | None
    fetched_at: str | None
    close_price: float | None
    currency: str | None
    age_days: int | None
    source_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "provider": self.provider,
            "symbol": self.symbol,
            "source_url": self.source_url,
            "source_as_of": self.source_as_of,
            "fetched_at": self.fetched_at,
            "close_price": self.close_price,
            "currency": self.currency,
            "age_days": self.age_days,
            "source_status": self.source_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class StockFundEtfPublicSourceFetcherResult:
    status: str
    fetcher_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    source_manifest_path: str
    output_signals_path: str
    source_manifest_loaded: bool
    source_manifest_template_written: bool
    public_signals_written: bool
    selected_stock_fund_etf_candidate: str | None
    selected_stock_fund_etf_amount_eur: float
    etf_candidate_count: int
    source_ready_count: int
    source_missing_count: int
    source_failed_count: int
    source_stale_count: int
    selected_candidate_source_status: str
    all_selected_sources_fresh: bool
    network_fetch_attempted_count: int
    upstream_freshness_result: Any
    signals: tuple[StockFundEtfPublicSourceSignal, ...]
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
        upstream = self.upstream_freshness_result
        return {
            "status": self.status,
            "fetcher_status": self.fetcher_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "source_manifest_path": self.source_manifest_path,
            "output_signals_path": self.output_signals_path,
            "source_manifest_loaded": self.source_manifest_loaded,
            "source_manifest_template_written": self.source_manifest_template_written,
            "public_signals_written": self.public_signals_written,
            "selected_stock_fund_etf_candidate": self.selected_stock_fund_etf_candidate,
            "selected_stock_fund_etf_amount_eur": self.selected_stock_fund_etf_amount_eur,
            "etf_candidate_count": self.etf_candidate_count,
            "source_ready_count": self.source_ready_count,
            "source_missing_count": self.source_missing_count,
            "source_failed_count": self.source_failed_count,
            "source_stale_count": self.source_stale_count,
            "selected_candidate_source_status": self.selected_candidate_source_status,
            "all_selected_sources_fresh": self.all_selected_sources_fresh,
            "network_fetch_attempted_count": self.network_fetch_attempted_count,
            "upstream_freshness_result": upstream.to_dict() if hasattr(upstream, "to_dict") else dict(getattr(upstream, "__dict__", {})),
            "signals": [signal.to_dict() for signal in self.signals],
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


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


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


def _today_iso() -> str:
    return date.today().isoformat()


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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _amount(value: Any) -> float:
    return round(float(value or 0.0), 2)


def _candidate_records_from_ticket(ticket: dict[str, Any]) -> list[str]:
    selected = str(ticket.get("selected_stock_fund_etf_candidate") or "")
    candidates: list[str] = []

    verdict = ticket.get("etf_scoring_verdict") or {}
    if isinstance(verdict, dict):
        sleeves = verdict.get("sleeves") or verdict.get("ranked_candidates") or []
        if isinstance(sleeves, list):
            for item in sleeves:
                if not isinstance(item, dict):
                    continue
                for key in ("candidate_id", "sleeve", "asset", "symbol", "ticker", "id"):
                    if item.get(key):
                        candidates.append(str(item[key]))
                        break

    weekly_dual_lane = ticket.get("weekly_dual_lane_mandate") or {}
    if isinstance(weekly_dual_lane, dict):
        lane = weekly_dual_lane.get("stock_fund_etf_lane") or {}
        if isinstance(lane, dict) and lane.get("asset"):
            candidates.append(str(lane["asset"]))

    if selected:
        candidates.append(selected)

    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _manifest_sources(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = manifest.get("sources", {})
    if isinstance(sources, dict):
        return {str(key): dict(value) for key, value in sources.items() if isinstance(value, dict)}
    if isinstance(sources, list):
        output: dict[str, dict[str, Any]] = {}
        for item in sources:
            if isinstance(item, dict) and item.get("candidate_id"):
                output[str(item["candidate_id"])] = dict(item)
        return output
    return {}


def build_stock_fund_etf_public_source_manifest_template(
    *,
    current_date: str,
    candidates: list[str],
) -> dict[str, Any]:
    return {
        "version": 1,
        "generated_at": current_date,
        "purpose": "Local operator-managed ETF/fund public source manifest. Fill real provider/symbol values only; do not commit this file.",
        "supported_providers": list(SUPPORTED_PROVIDERS),
        "sources": {
            candidate: {
                "candidate_id": candidate,
                "provider": "",
                "symbol": "",
                "source_url": "",
                "currency": "",
                "notes": "Fill with a real public quote source such as yahoo_chart or stooq_csv. Leave blank until verified.",
            }
            for candidate in candidates
        },
    }


def _default_fetch_text(url: str, timeout_seconds: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "JARVIS-Portfolio-OS/1.0 read-only public data freshness checker",
            "Accept": "application/json,text/csv,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _yahoo_chart_url(symbol: str) -> str:
    encoded = urllib.parse.quote(symbol, safe="")
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=5d&interval=1d&includeAdjustedClose=true"


def _stooq_csv_url(symbol: str) -> str:
    encoded = urllib.parse.quote(symbol, safe="")
    return f"https://stooq.com/q/l/?s={encoded}&f=sd2t2ohlcv&h&e=csv"


def _last_non_null(values: list[Any]) -> Any:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def _parse_yahoo_chart(payload: str, *, candidate_id: str, source: dict[str, Any], current_date_text: str, max_age_days: int) -> StockFundEtfPublicSourceSignal:
    provider = "yahoo_chart"
    symbol = str(source.get("symbol") or "")
    source_url = str(source.get("source_url") or _yahoo_chart_url(symbol))
    warnings: list[str] = []
    blockers: list[str] = []

    data = json.loads(payload)
    result = (((data.get("chart") or {}).get("result") or [None])[0]) or {}
    timestamps = result.get("timestamp") or []
    quote = (((result.get("indicators") or {}).get("quote") or [None])[0]) or {}
    close_values = quote.get("close") or []
    meta = result.get("meta") or {}

    latest_timestamp = _last_non_null(timestamps)
    close_price = _last_non_null(close_values)
    if latest_timestamp is None or close_price is None:
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider,
            symbol=symbol,
            source_url=source_url,
            source_as_of=None,
            fetched_at=current_date_text,
            close_price=None,
            currency=str(source.get("currency") or meta.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_INVALID,
            blockers=(),
            warnings=(f"{candidate_id} Yahoo chart payload did not contain a latest timestamp and close price.",),
        )

    source_as_of = datetime.fromtimestamp(int(latest_timestamp), tz=timezone.utc).date().isoformat()
    current = _parse_date(current_date_text) or date.today()
    parsed_source = _parse_date(source_as_of)
    age_days = (current - parsed_source).days if parsed_source else None

    if age_days is None or age_days < 0:
        status = SOURCE_INVALID
        warnings.append(f"{candidate_id} fetched source date is invalid or in the future.")
    elif age_days > max_age_days:
        status = SOURCE_STALE
        warnings.append(f"{candidate_id} fetched public source data is {age_days} days old; refresh required.")
    else:
        status = SOURCE_READY

    return StockFundEtfPublicSourceSignal(
        candidate_id=candidate_id,
        provider=provider,
        symbol=symbol,
        source_url=source_url,
        source_as_of=source_as_of,
        fetched_at=current_date_text,
        close_price=round(float(close_price), 6),
        currency=str(source.get("currency") or meta.get("currency") or "") or None,
        age_days=age_days,
        source_status=status,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _parse_stooq_csv(payload: str, *, candidate_id: str, source: dict[str, Any], current_date_text: str, max_age_days: int) -> StockFundEtfPublicSourceSignal:
    provider = "stooq_csv"
    symbol = str(source.get("symbol") or "")
    source_url = str(source.get("source_url") or _stooq_csv_url(symbol))
    rows = list(csv.DictReader(StringIO(payload)))
    warnings: list[str] = []

    if not rows:
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider,
            symbol=symbol,
            source_url=source_url,
            source_as_of=None,
            fetched_at=current_date_text,
            close_price=None,
            currency=str(source.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_INVALID,
            blockers=(),
            warnings=(f"{candidate_id} Stooq CSV response had no rows.",),
        )

    row = rows[-1]
    date_text = str(row.get("Date") or row.get("date") or "")
    close_text = str(row.get("Close") or row.get("close") or "")
    parsed_source = _parse_date(date_text)
    try:
        close_price = float(close_text)
    except (TypeError, ValueError):
        close_price = None

    if parsed_source is None or close_price is None:
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider,
            symbol=symbol,
            source_url=source_url,
            source_as_of=date_text or None,
            fetched_at=current_date_text,
            close_price=None,
            currency=str(source.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_INVALID,
            blockers=(),
            warnings=(f"{candidate_id} Stooq CSV response did not contain valid Date and Close values.",),
        )

    current = _parse_date(current_date_text) or date.today()
    age_days = (current - parsed_source).days
    if age_days < 0:
        status = SOURCE_INVALID
        warnings.append(f"{candidate_id} fetched source date is in the future.")
    elif age_days > max_age_days:
        status = SOURCE_STALE
        warnings.append(f"{candidate_id} fetched public source data is {age_days} days old; refresh required.")
    else:
        status = SOURCE_READY

    return StockFundEtfPublicSourceSignal(
        candidate_id=candidate_id,
        provider=provider,
        symbol=symbol,
        source_url=source_url,
        source_as_of=parsed_source.isoformat(),
        fetched_at=current_date_text,
        close_price=round(close_price, 6),
        currency=str(source.get("currency") or "") or None,
        age_days=age_days,
        source_status=status,
        blockers=(),
        warnings=tuple(warnings),
    )


def _fetch_source(
    *,
    candidate_id: str,
    source: dict[str, Any],
    current_date_text: str,
    max_age_days: int,
    fetch_text: Callable[[str], str],
) -> StockFundEtfPublicSourceSignal:
    provider = str(source.get("provider") or "").strip()
    symbol = str(source.get("symbol") or "").strip()
    if not provider or not symbol:
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider or None,
            symbol=symbol or None,
            source_url=str(source.get("source_url") or "") or None,
            source_as_of=None,
            fetched_at=None,
            close_price=None,
            currency=str(source.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_MISSING,
            blockers=(),
            warnings=(f"{candidate_id} has no real ETF/fund provider and symbol in the local public source manifest.",),
        )

    if provider not in SUPPORTED_PROVIDERS:
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider,
            symbol=symbol,
            source_url=str(source.get("source_url") or "") or None,
            source_as_of=None,
            fetched_at=None,
            close_price=None,
            currency=str(source.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_UNSUPPORTED,
            blockers=(),
            warnings=(f"{candidate_id} uses unsupported ETF/fund public source provider {provider}.",),
        )

    source_url = str(source.get("source_url") or "")
    if not source_url:
        source_url = _yahoo_chart_url(symbol) if provider == "yahoo_chart" else _stooq_csv_url(symbol)

    try:
        payload = fetch_text(source_url)
    except Exception as exc:  # pragma: no cover - exact exception depends on environment/network
        return StockFundEtfPublicSourceSignal(
            candidate_id=candidate_id,
            provider=provider,
            symbol=symbol,
            source_url=source_url,
            source_as_of=None,
            fetched_at=current_date_text,
            close_price=None,
            currency=str(source.get("currency") or "") or None,
            age_days=None,
            source_status=SOURCE_FETCH_FAILED,
            blockers=(),
            warnings=(f"{candidate_id} public source fetch failed: {exc}",),
        )

    if provider == "yahoo_chart":
        return _parse_yahoo_chart(payload, candidate_id=candidate_id, source={**source, "source_url": source_url}, current_date_text=current_date_text, max_age_days=max_age_days)
    return _parse_stooq_csv(payload, candidate_id=candidate_id, source={**source, "source_url": source_url}, current_date_text=current_date_text, max_age_days=max_age_days)


def build_stock_fund_etf_public_source_fetcher_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    source_manifest_path: str | Path = DEFAULT_SOURCE_MANIFEST_PATH,
    output_signals_path: str | Path = DEFAULT_OUTPUT_SIGNALS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_local_signals: bool = False,
    write_local_manifest_template: bool = False,
    fetch_text: Callable[[str], str] = _default_fetch_text,
    upstream_freshness_result: StockFundEtfDataFreshnessEngineResult | None = None,
    upstream_builder: Callable[..., StockFundEtfDataFreshnessEngineResult] = build_stock_fund_etf_data_freshness_engine_result,
) -> StockFundEtfPublicSourceFetcherResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_ticket = _resolve_path(ticket_path, root)
    resolved_manifest = _resolve_path(source_manifest_path, root)
    resolved_output = _resolve_path(output_signals_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    if not _is_under(resolved_manifest, root, "jarvis/local"):
        blockers.append("stock/fund/ETF public source manifest path must remain under jarvis/local/.")
    if not _is_under(resolved_output, root, "jarvis/local"):
        blockers.append("stock/fund/ETF public signal output path must remain under jarvis/local/.")

    ticket: dict[str, Any] = {}
    candidates: list[str] = []
    if not blockers:
        if not resolved_ticket.exists():
            warnings.append("approval ticket is missing; ETF/fund public source fetch cannot identify candidates.")
        else:
            ticket = _load_json(resolved_ticket)
            candidates = _candidate_records_from_ticket(ticket)

    template_written = False
    if write_local_manifest_template and not blockers:
        template = build_stock_fund_etf_public_source_manifest_template(
            current_date=current_date_text,
            candidates=candidates,
        )
        _write_json(resolved_manifest, template)
        template_written = True

    manifest: dict[str, Any] = {}
    manifest_loaded = False
    if not blockers and resolved_manifest.exists():
        manifest = _load_json(resolved_manifest)
        manifest_loaded = True
    elif not blockers:
        warnings.append("stock/fund/ETF public source manifest is missing; no ETF/fund public data was fetched.")

    sources = _manifest_sources(manifest)
    signals: list[StockFundEtfPublicSourceSignal] = []
    fetch_attempts = 0

    for candidate_id in candidates:
        source = sources.get(candidate_id)
        if source is None:
            signals.append(
                StockFundEtfPublicSourceSignal(
                    candidate_id=candidate_id,
                    provider=None,
                    symbol=None,
                    source_url=None,
                    source_as_of=None,
                    fetched_at=None,
                    close_price=None,
                    currency=None,
                    age_days=None,
                    source_status=SOURCE_MISSING,
                    blockers=(),
                    warnings=(f"{candidate_id} has no entry in the stock/fund/ETF public source manifest.",),
                )
            )
            continue

        if str(source.get("provider") or "").strip() and str(source.get("symbol") or "").strip():
            fetch_attempts += 1
        signals.append(
            _fetch_source(
                candidate_id=candidate_id,
                source=source,
                current_date_text=current_date_text,
                max_age_days=max_age_days,
                fetch_text=fetch_text,
            )
        )

    if not candidates:
        warnings.append("No stock/fund/ETF candidates found in approval ticket.")

    if write_local_signals and not blockers:
        _write_json(
            resolved_output,
            {
                "version": 1,
                "current_date": current_date_text,
                "source_manifest_path": str(resolved_manifest),
                "signals": [signal.to_dict() for signal in signals],
                "safety": {
                    "allocation_mutation": False,
                    "approval_ticket_mutation": False,
                    "portfolio_state_mutation": False,
                    "buy_request_created": False,
                    "broker_connection_forbidden": True,
                    "credentials_forbidden": True,
                    "private_account_data_ingestion_forbidden": True,
                    "order_creation_forbidden": True,
                    "trades_executed": False,
                },
            },
        )

    upstream = None
    if not blockers:
        upstream = upstream_freshness_result if upstream_freshness_result is not None else upstream_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            root=root,
            max_age_days=max_age_days,
            write_local_signals=write_local_signals,
        )
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        warnings.extend(getattr(upstream, "warnings", ()) or [])

    for signal in signals:
        warnings.extend(signal.warnings)
        blockers.extend(signal.blockers)

    source_ready_count = sum(1 for signal in signals if signal.source_status == SOURCE_READY)
    source_missing_count = sum(1 for signal in signals if signal.source_status in {SOURCE_MISSING, SOURCE_UNSUPPORTED, SOURCE_INVALID})
    source_failed_count = sum(1 for signal in signals if signal.source_status == SOURCE_FETCH_FAILED)
    source_stale_count = sum(1 for signal in signals if signal.source_status == SOURCE_STALE)

    selected_candidate = str(ticket.get("selected_stock_fund_etf_candidate") or "") if ticket else ""
    selected_signal = next((signal for signal in signals if signal.candidate_id == selected_candidate), None)
    selected_status = selected_signal.source_status if selected_signal else SOURCE_MISSING
    all_selected_fresh = bool(selected_signal and selected_signal.source_status == SOURCE_READY)

    if selected_candidate and selected_signal is None:
        warnings.append(f"selected stock/fund/ETF candidate {selected_candidate} has no public source signal.")
    if not all_selected_fresh:
        warnings.append("Selected stock/fund/ETF candidate does not have fresh fetched public source data.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)
    upstream_status = str(getattr(upstream, "status", "")) if upstream is not None else ""
    upstream_blocked = "BLOCKED" in upstream_status
    upstream_requires_review = "REVIEW_REQUIRED" in upstream_status

    if unique_blockers or upstream_blocked:
        status = STATUS_BLOCKED
        fetcher_status = FETCHER_BLOCKED
    elif unique_warnings or upstream_requires_review or not all_selected_fresh:
        status = STATUS_REVIEW_REQUIRED
        fetcher_status = FETCHER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        fetcher_status = FETCHER_READY

    return StockFundEtfPublicSourceFetcherResult(
        status=status,
        fetcher_status=fetcher_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        source_manifest_path=str(resolved_manifest),
        output_signals_path=str(resolved_output),
        source_manifest_loaded=manifest_loaded,
        source_manifest_template_written=template_written,
        public_signals_written=bool(write_local_signals and not blockers),
        selected_stock_fund_etf_candidate=selected_candidate or None,
        selected_stock_fund_etf_amount_eur=_amount(ticket.get("selected_stock_fund_etf_amount_eur")) if ticket else 0.0,
        etf_candidate_count=len(candidates),
        source_ready_count=source_ready_count,
        source_missing_count=source_missing_count,
        source_failed_count=source_failed_count,
        source_stale_count=source_stale_count,
        selected_candidate_source_status=selected_status,
        all_selected_sources_fresh=all_selected_fresh,
        network_fetch_attempted_count=fetch_attempts,
        upstream_freshness_result=upstream,
        signals=tuple(signals),
        recommendation_quality_current_data=all_selected_fresh and not upstream_requires_review and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=False,
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


def _format_signals(result: StockFundEtfPublicSourceFetcherResult) -> str:
    lines = ["Stock/Fund/ETF public source signals:"]
    for signal in result.signals:
        age = f"{signal.age_days} days" if signal.age_days is not None else "unknown"
        close = f"{signal.close_price:,.6f}" if signal.close_price is not None else "none"
        lines.append(
            f"- {signal.candidate_id}: {signal.source_status}; provider {signal.provider or 'none'}; "
            f"symbol {signal.symbol or 'none'}; as_of {signal.source_as_of or 'none'}; age {age}; close {close}; currency {signal.currency or 'unknown'}"
        )
        if signal.source_url:
            lines.append(f"  source_url: {signal.source_url}")
        for warning in signal.warnings:
            lines.append(f"  warning: {warning}")
    return "\n".join(lines)


def _upstream_console_output(upstream: Any) -> str:
    if upstream is None:
        return "none"
    required = ("engine_status", "freshness_items", "selected_candidate_metadata_status")
    if all(hasattr(upstream, attr) for attr in required):
        return format_stock_fund_etf_data_freshness_engine(upstream)

    return "\n".join(
        [
            "J.A.R.V.I.S. Stock/Fund/ETF Data Freshness Engine",
            f"status: {getattr(upstream, 'status', 'unknown')}",
            f"selected stock/fund/ETF candidate: {getattr(upstream, 'selected_stock_fund_etf_candidate', 'unknown')}",
            f"selected candidate metadata status: {getattr(upstream, 'selected_candidate_metadata_status', 'unknown')}",
            "no broker connection",
            "no credentials",
            "no private account data ingestion",
            "no orders created",
            "no trades executed",
        ]
    )


def format_stock_fund_etf_public_source_fetcher(
    result: StockFundEtfPublicSourceFetcherResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Stock/Fund/ETF Public Source Fetcher",
        f"status: {result.status}",
        f"fetcher status: {result.fetcher_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"source manifest path: {result.source_manifest_path}",
        f"output signals path: {result.output_signals_path}",
        f"source manifest loaded: {result.source_manifest_loaded}",
        f"source manifest template written: {result.source_manifest_template_written}",
        f"public signals written: {result.public_signals_written}",
        f"selected stock/fund/ETF candidate: {result.selected_stock_fund_etf_candidate or 'none'}",
        f"selected stock/fund/ETF amount: EUR {result.selected_stock_fund_etf_amount_eur:,.2f}",
        f"ETF candidate count: {result.etf_candidate_count}",
        f"source ready count: {result.source_ready_count}",
        f"source missing count: {result.source_missing_count}",
        f"source failed count: {result.source_failed_count}",
        f"source stale count: {result.source_stale_count}",
        f"selected candidate source status: {result.selected_candidate_source_status}",
        f"all selected sources fresh: {result.all_selected_sources_fresh}",
        f"network fetch attempted count: {result.network_fetch_attempted_count}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        _format_signals(result),
        "",
        "Upstream ETF freshness gate:",
        _upstream_console_output(result.upstream_freshness_result),
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
    parser = argparse.ArgumentParser(description="Fetch fresh public ETF/fund data from configured local source manifest.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run stock/fund/ETF public source fetcher.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--source-manifest-path", default=DEFAULT_SOURCE_MANIFEST_PATH)
    parser.add_argument("--output-signals-path", default=DEFAULT_OUTPUT_SIGNALS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-local-signals", action="store_true", help="Write fetched stock/fund/ETF public signals under jarvis/local.")
    parser.add_argument("--write-local-manifest-template", action="store_true", help="Write a local manifest template under jarvis/local without treating it as real data.")
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

    result = build_stock_fund_etf_public_source_fetcher_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        source_manifest_path=args.source_manifest_path,
        output_signals_path=args.output_signals_path,
        max_age_days=args.max_age_days,
        write_local_signals=args.write_local_signals,
        write_local_manifest_template=args.write_local_manifest_template,
    )
    print(format_stock_fund_etf_public_source_fetcher(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())