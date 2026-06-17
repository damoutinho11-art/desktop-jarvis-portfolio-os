"""J.A.R.V.I.S. v34.0 stock/fund/ETF sleeve-to-instrument resolver.

v34 separates ETF strategy sleeves from buyable instruments.

A sleeve such as quality_etf is a portfolio mandate, not a buyable asset. v34
requires a local instrument universe that maps each sleeve to real ETF/fund
instruments. A real instrument can become selected only if it has a configured
public provider/symbol and fresh fetched public quote data.

No stale/static/fake ETF data is promoted.
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
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import DEFAULT_OUTPUT_PATH
from .jarvis_v33_0_stock_fund_etf_public_source_fetcher import (
    SOURCE_FETCH_FAILED,
    SOURCE_INVALID,
    SOURCE_MISSING,
    SOURCE_READY,
    SOURCE_STALE,
    SOURCE_UNSUPPORTED,
    StockFundEtfPublicSourceFetcherResult,
    StockFundEtfPublicSourceSignal,
    _default_fetch_text,
    _fetch_source,
    build_stock_fund_etf_public_source_fetcher_result,
    format_stock_fund_etf_public_source_fetcher,
)

STATUS_READY = "JARVIS_V34_0_STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V34_0_STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V34_0_STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_BLOCKED_SAFE"

RESOLVER_READY = "STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_READY"
RESOLVER_REVIEW_REQUIRED = "STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_REVIEW_REQUIRED"
RESOLVER_BLOCKED = "STOCK_FUND_ETF_SLEEVE_TO_INSTRUMENT_RESOLVER_BLOCKED"

NEXT_STAGE = "stock_fund_etf_selected_instrument_ticket_bridge"

DEFAULT_INSTRUMENT_UNIVERSE_PATH = "jarvis/local/stock_fund_etf_instrument_universe.local.json"
DEFAULT_OUTPUT_RESOLUTION_PATH = "jarvis/local/stock_fund_etf_selected_instrument.local.json"

INSTRUMENT_SELECTED = "SELECTED_REAL_INSTRUMENT_FOR_SLEEVE"
INSTRUMENT_READY_NOT_SELECTED = "REAL_INSTRUMENT_READY_NOT_SELECTED"
INSTRUMENT_MISSING_SOURCE = "REAL_INSTRUMENT_MISSING_PUBLIC_SOURCE"
INSTRUMENT_FETCH_FAILED = "REAL_INSTRUMENT_PUBLIC_FETCH_FAILED"
INSTRUMENT_STALE = "REAL_INSTRUMENT_PUBLIC_SOURCE_STALE"
INSTRUMENT_INVALID = "REAL_INSTRUMENT_PUBLIC_SOURCE_INVALID"


@dataclass(frozen=True)
class StockFundEtfInstrumentDecision:
    sleeve_id: str
    instrument_id: str
    name: str | None
    isin: str | None
    ticker: str | None
    provider: str | None
    symbol: str | None
    currency: str | None
    exchange: str | None
    expense_ratio: float | None
    priority_score: float
    public_source_status: str
    source_as_of: str | None
    close_price: float | None
    source_url: str | None
    selected: bool
    decision_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "instrument_id": self.instrument_id,
            "name": self.name,
            "isin": self.isin,
            "ticker": self.ticker,
            "provider": self.provider,
            "symbol": self.symbol,
            "currency": self.currency,
            "exchange": self.exchange,
            "expense_ratio": self.expense_ratio,
            "priority_score": self.priority_score,
            "public_source_status": self.public_source_status,
            "source_as_of": self.source_as_of,
            "close_price": self.close_price,
            "source_url": self.source_url,
            "selected": self.selected,
            "decision_status": self.decision_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class StockFundEtfSleeveToInstrumentResolverResult:
    status: str
    resolver_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    instrument_universe_path: str
    output_resolution_path: str
    instrument_universe_loaded: bool
    instrument_universe_template_written: bool
    instrument_resolution_written: bool
    selected_sleeve: str | None
    selected_sleeve_amount_eur: float
    available_sleeve_count: int
    selected_sleeve_instrument_count: int
    ready_instrument_count: int
    missing_source_instrument_count: int
    stale_or_failed_instrument_count: int
    selected_instrument_id: str | None
    selected_instrument_name: str | None
    selected_instrument_isin: str | None
    selected_instrument_ticker: str | None
    selected_instrument_provider: str | None
    selected_instrument_symbol: str | None
    selected_instrument_currency: str | None
    selected_instrument_source_as_of: str | None
    selected_instrument_close_price: float | None
    selected_instrument_source_url: str | None
    selected_instrument_public_source_ready: bool
    network_fetch_attempted_count: int
    upstream_public_source_result: Any
    instrument_decisions: tuple[StockFundEtfInstrumentDecision, ...]
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
        upstream = self.upstream_public_source_result
        return {
            "status": self.status,
            "resolver_status": self.resolver_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "instrument_universe_path": self.instrument_universe_path,
            "output_resolution_path": self.output_resolution_path,
            "instrument_universe_loaded": self.instrument_universe_loaded,
            "instrument_universe_template_written": self.instrument_universe_template_written,
            "instrument_resolution_written": self.instrument_resolution_written,
            "selected_sleeve": self.selected_sleeve,
            "selected_sleeve_amount_eur": self.selected_sleeve_amount_eur,
            "available_sleeve_count": self.available_sleeve_count,
            "selected_sleeve_instrument_count": self.selected_sleeve_instrument_count,
            "ready_instrument_count": self.ready_instrument_count,
            "missing_source_instrument_count": self.missing_source_instrument_count,
            "stale_or_failed_instrument_count": self.stale_or_failed_instrument_count,
            "selected_instrument_id": self.selected_instrument_id,
            "selected_instrument_name": self.selected_instrument_name,
            "selected_instrument_isin": self.selected_instrument_isin,
            "selected_instrument_ticker": self.selected_instrument_ticker,
            "selected_instrument_provider": self.selected_instrument_provider,
            "selected_instrument_symbol": self.selected_instrument_symbol,
            "selected_instrument_currency": self.selected_instrument_currency,
            "selected_instrument_source_as_of": self.selected_instrument_source_as_of,
            "selected_instrument_close_price": self.selected_instrument_close_price,
            "selected_instrument_source_url": self.selected_instrument_source_url,
            "selected_instrument_public_source_ready": self.selected_instrument_public_source_ready,
            "network_fetch_attempted_count": self.network_fetch_attempted_count,
            "upstream_public_source_result": upstream.to_dict() if hasattr(upstream, "to_dict") else dict(getattr(upstream, "__dict__", {})),
            "instrument_decisions": [decision.to_dict() for decision in self.instrument_decisions],
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


def _sleeves_from_ticket(ticket: dict[str, Any]) -> list[str]:
    selected = str(ticket.get("selected_stock_fund_etf_candidate") or "")
    sleeves: list[str] = []

    verdict = ticket.get("etf_scoring_verdict") or {}
    if isinstance(verdict, dict):
        entries = verdict.get("sleeves") or verdict.get("ranked_candidates") or []
        if isinstance(entries, list):
            for item in entries:
                if not isinstance(item, dict):
                    continue
                for key in ("sleeve", "candidate_id", "asset", "id"):
                    if item.get(key):
                        sleeves.append(str(item[key]))
                        break

    weekly_dual_lane = ticket.get("weekly_dual_lane_mandate") or {}
    if isinstance(weekly_dual_lane, dict):
        lane = weekly_dual_lane.get("stock_fund_etf_lane") or {}
        if isinstance(lane, dict) and lane.get("asset"):
            sleeves.append(str(lane["asset"]))

    if selected:
        sleeves.append(selected)

    return list(dict.fromkeys(sleeve for sleeve in sleeves if sleeve))


def build_stock_fund_etf_instrument_universe_template(
    *,
    current_date: str,
    sleeves: list[str],
) -> dict[str, Any]:
    return {
        "version": 1,
        "generated_at": current_date,
        "purpose": "Local operator-managed sleeve-to-real-instrument universe. Fill real ETF/fund instruments only; do not commit this file.",
        "sleeves": {
            sleeve: {
                "sleeve_id": sleeve,
                "description": "",
                "instruments": [
                    {
                        "instrument_id": "",
                        "name": "",
                        "isin": "",
                        "ticker": "",
                        "exchange": "",
                        "currency": "",
                        "provider": "",
                        "symbol": "",
                        "source_url": "",
                        "factsheet_url": "",
                        "expense_ratio": None,
                        "priority_score": 0.0,
                        "notes": "Fill with a real buyable ETF/fund and a verified public quote source. Blank entries never count as data.",
                    }
                ],
            }
            for sleeve in sleeves
        },
    }


def _instrument_universe_sleeves(universe: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sleeves = universe.get("sleeves", {})
    if isinstance(sleeves, dict):
        return {str(key): dict(value) for key, value in sleeves.items() if isinstance(value, dict)}

    if isinstance(sleeves, list):
        output: dict[str, dict[str, Any]] = {}
        for item in sleeves:
            if isinstance(item, dict) and item.get("sleeve_id"):
                output[str(item["sleeve_id"])] = dict(item)
        return output

    return {}


def _instruments_for_sleeve(universe: dict[str, Any], sleeve_id: str | None) -> list[dict[str, Any]]:
    if not sleeve_id:
        return []
    sleeves = _instrument_universe_sleeves(universe)
    sleeve = sleeves.get(sleeve_id, {})
    instruments = sleeve.get("instruments") if isinstance(sleeve, dict) else []
    if not isinstance(instruments, list):
        return []
    return [dict(item) for item in instruments if isinstance(item, dict)]


def _instrument_id(instrument: dict[str, Any], index: int) -> str:
    for key in ("instrument_id", "id", "isin", "ticker", "symbol", "name"):
        value = instrument.get(key)
        if value:
            return str(value)
    return f"unnamed_instrument_{index + 1}"


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _priority_score(instrument: dict[str, Any]) -> float:
    return float(_float_or_none(instrument.get("priority_score")) or 0.0)


def _decision_status_for_signal(signal: StockFundEtfPublicSourceSignal, *, selected: bool) -> str:
    if selected:
        return INSTRUMENT_SELECTED
    if signal.source_status == SOURCE_READY:
        return INSTRUMENT_READY_NOT_SELECTED
    if signal.source_status in {SOURCE_MISSING, SOURCE_UNSUPPORTED}:
        return INSTRUMENT_MISSING_SOURCE
    if signal.source_status == SOURCE_STALE:
        return INSTRUMENT_STALE
    if signal.source_status in {SOURCE_INVALID}:
        return INSTRUMENT_INVALID
    return INSTRUMENT_FETCH_FAILED


def _decision_from_instrument(
    *,
    sleeve_id: str,
    instrument: dict[str, Any],
    index: int,
    signal: StockFundEtfPublicSourceSignal,
    selected: bool,
) -> StockFundEtfInstrumentDecision:
    return StockFundEtfInstrumentDecision(
        sleeve_id=sleeve_id,
        instrument_id=_instrument_id(instrument, index),
        name=str(instrument.get("name") or "") or None,
        isin=str(instrument.get("isin") or "") or None,
        ticker=str(instrument.get("ticker") or "") or None,
        provider=signal.provider,
        symbol=signal.symbol,
        currency=signal.currency or str(instrument.get("currency") or "") or None,
        exchange=str(instrument.get("exchange") or "") or None,
        expense_ratio=_float_or_none(instrument.get("expense_ratio")),
        priority_score=_priority_score(instrument),
        public_source_status=signal.source_status,
        source_as_of=signal.source_as_of,
        close_price=signal.close_price,
        source_url=signal.source_url,
        selected=selected,
        decision_status=_decision_status_for_signal(signal, selected=selected),
        blockers=signal.blockers,
        warnings=signal.warnings,
    )


def _rank_ready_instruments(decisions: list[StockFundEtfInstrumentDecision]) -> list[StockFundEtfInstrumentDecision]:
    ready = [decision for decision in decisions if decision.public_source_status == SOURCE_READY]
    return sorted(
        ready,
        key=lambda item: (
            -item.priority_score,
            item.expense_ratio if item.expense_ratio is not None else 999.0,
            item.instrument_id,
        ),
    )


def build_stock_fund_etf_sleeve_to_instrument_resolver_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    instrument_universe_path: str | Path = DEFAULT_INSTRUMENT_UNIVERSE_PATH,
    output_resolution_path: str | Path = DEFAULT_OUTPUT_RESOLUTION_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_local_instrument_template: bool = False,
    write_local_resolution: bool = False,
    fetch_text: Callable[[str], str] = _default_fetch_text,
    upstream_public_source_result: StockFundEtfPublicSourceFetcherResult | None = None,
    upstream_builder: Callable[..., StockFundEtfPublicSourceFetcherResult] = build_stock_fund_etf_public_source_fetcher_result,
) -> StockFundEtfSleeveToInstrumentResolverResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_ticket = _resolve_path(ticket_path, root)
    resolved_universe = _resolve_path(instrument_universe_path, root)
    resolved_output = _resolve_path(output_resolution_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    if not _is_under(resolved_universe, root, "jarvis/local"):
        blockers.append("instrument universe path must remain under jarvis/local/.")
    if not _is_under(resolved_output, root, "jarvis/local"):
        blockers.append("instrument resolution output path must remain under jarvis/local/.")

    ticket: dict[str, Any] = {}
    sleeves: list[str] = []
    selected_sleeve: str | None = None
    selected_sleeve_amount = 0.0
    if not blockers:
        if not resolved_ticket.exists():
            warnings.append("approval ticket is missing; sleeve-to-instrument resolution cannot identify ETF sleeve.")
        else:
            ticket = _load_json(resolved_ticket)
            sleeves = _sleeves_from_ticket(ticket)
            selected_sleeve = str(ticket.get("selected_stock_fund_etf_candidate") or "") or None
            selected_sleeve_amount = _amount(ticket.get("selected_stock_fund_etf_amount_eur"))

    template_written = False
    if write_local_instrument_template and not blockers:
        template = build_stock_fund_etf_instrument_universe_template(
            current_date=current_date_text,
            sleeves=sleeves,
        )
        _write_json(resolved_universe, template)
        template_written = True

    universe: dict[str, Any] = {}
    universe_loaded = False
    if not blockers and resolved_universe.exists():
        universe = _load_json(resolved_universe)
        universe_loaded = True
    elif not blockers:
        warnings.append("stock/fund/ETF instrument universe is missing; no sleeve can resolve to a real instrument.")

    upstream = None
    if not blockers:
        upstream = upstream_public_source_result if upstream_public_source_result is not None else upstream_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            root=root,
            max_age_days=max_age_days,
            write_local_signals=False,
        )
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        warnings.extend(getattr(upstream, "warnings", ()) or [])

    instruments = _instruments_for_sleeve(universe, selected_sleeve)
    if selected_sleeve and not instruments:
        warnings.append(f"selected sleeve {selected_sleeve} has no real instruments in the local instrument universe.")

    decisions_raw: list[StockFundEtfInstrumentDecision] = []
    network_fetch_attempts = 0
    for index, instrument in enumerate(instruments):
        candidate_id = _instrument_id(instrument, index)
        source = {
            "provider": instrument.get("provider"),
            "symbol": instrument.get("symbol") or instrument.get("ticker"),
            "source_url": instrument.get("source_url"),
            "currency": instrument.get("currency"),
        }
        if str(source.get("provider") or "").strip() and str(source.get("symbol") or "").strip():
            network_fetch_attempts += 1
        signal = _fetch_source(
            candidate_id=candidate_id,
            source=source,
            current_date_text=current_date_text,
            max_age_days=max_age_days,
            fetch_text=fetch_text,
        )
        decisions_raw.append(
            _decision_from_instrument(
                sleeve_id=selected_sleeve or "unknown",
                instrument=instrument,
                index=index,
                signal=signal,
                selected=False,
            )
        )

    ranked_ready = _rank_ready_instruments(decisions_raw)
    selected_decision = ranked_ready[0] if ranked_ready else None
    decisions: list[StockFundEtfInstrumentDecision] = []
    for decision in decisions_raw:
        is_selected = bool(selected_decision and decision.instrument_id == selected_decision.instrument_id)
        decisions.append(
            StockFundEtfInstrumentDecision(
                **{
                    **decision.to_dict(),
                    "selected": is_selected,
                    "decision_status": _decision_status_for_signal(
                        StockFundEtfPublicSourceSignal(
                            candidate_id=decision.instrument_id,
                            provider=decision.provider,
                            symbol=decision.symbol,
                            source_url=decision.source_url,
                            source_as_of=decision.source_as_of,
                            fetched_at=current_date_text if decision.source_as_of else None,
                            close_price=decision.close_price,
                            currency=decision.currency,
                            age_days=None,
                            source_status=decision.public_source_status,
                            blockers=decision.blockers,
                            warnings=decision.warnings,
                        ),
                        selected=is_selected,
                    ),
                }
            )
        )

    for decision in decisions:
        warnings.extend(decision.warnings)
        blockers.extend(decision.blockers)

    ready_count = sum(1 for decision in decisions if decision.public_source_status == SOURCE_READY)
    missing_count = sum(1 for decision in decisions if decision.public_source_status in {SOURCE_MISSING, SOURCE_UNSUPPORTED})
    stale_or_failed_count = sum(1 for decision in decisions if decision.public_source_status in {SOURCE_STALE, SOURCE_FETCH_FAILED, SOURCE_INVALID})

    selected = next((decision for decision in decisions if decision.selected), None)
    if selected is None:
        warnings.append("selected stock/fund/ETF sleeve has no selected real instrument with fresh public data.")

    resolution_written = False
    if write_local_resolution and not blockers:
        _write_json(
            resolved_output,
            {
                "version": 1,
                "current_date": current_date_text,
                "selected_sleeve": selected_sleeve,
                "selected_sleeve_amount_eur": selected_sleeve_amount,
                "selected_instrument": selected.to_dict() if selected else None,
                "instrument_decisions": [decision.to_dict() for decision in decisions],
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
        resolution_written = True

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    upstream_status = str(getattr(upstream, "status", "")) if upstream is not None else ""
    upstream_blocked = "BLOCKED" in upstream_status
    upstream_requires_review = "REVIEW_REQUIRED" in upstream_status

    selected_ready = bool(selected and selected.public_source_status == SOURCE_READY)
    if unique_blockers or upstream_blocked:
        status = STATUS_BLOCKED
        resolver_status = RESOLVER_BLOCKED
    elif unique_warnings or upstream_requires_review or not selected_ready:
        status = STATUS_REVIEW_REQUIRED
        resolver_status = RESOLVER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        resolver_status = RESOLVER_READY

    return StockFundEtfSleeveToInstrumentResolverResult(
        status=status,
        resolver_status=resolver_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        instrument_universe_path=str(resolved_universe),
        output_resolution_path=str(resolved_output),
        instrument_universe_loaded=universe_loaded,
        instrument_universe_template_written=template_written,
        instrument_resolution_written=resolution_written,
        selected_sleeve=selected_sleeve,
        selected_sleeve_amount_eur=selected_sleeve_amount,
        available_sleeve_count=len(_instrument_universe_sleeves(universe)),
        selected_sleeve_instrument_count=len(instruments),
        ready_instrument_count=ready_count,
        missing_source_instrument_count=missing_count,
        stale_or_failed_instrument_count=stale_or_failed_count,
        selected_instrument_id=selected.instrument_id if selected else None,
        selected_instrument_name=selected.name if selected else None,
        selected_instrument_isin=selected.isin if selected else None,
        selected_instrument_ticker=selected.ticker if selected else None,
        selected_instrument_provider=selected.provider if selected else None,
        selected_instrument_symbol=selected.symbol if selected else None,
        selected_instrument_currency=selected.currency if selected else None,
        selected_instrument_source_as_of=selected.source_as_of if selected else None,
        selected_instrument_close_price=selected.close_price if selected else None,
        selected_instrument_source_url=selected.source_url if selected else None,
        selected_instrument_public_source_ready=selected_ready,
        network_fetch_attempted_count=network_fetch_attempts,
        upstream_public_source_result=upstream,
        instrument_decisions=tuple(decisions),
        recommendation_quality_current_data=selected_ready and not upstream_requires_review and not unique_warnings,
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


def _format_decisions(result: StockFundEtfSleeveToInstrumentResolverResult) -> str:
    lines = ["Stock/Fund/ETF real instrument decisions:"]
    if not result.instrument_decisions:
        lines.append("- none")
        return "\n".join(lines)

    for decision in result.instrument_decisions:
        selected = "SELECTED" if decision.selected else "not selected"
        close = f"{decision.close_price:,.6f}" if decision.close_price is not None else "none"
        expense = f"{decision.expense_ratio:,.4f}" if decision.expense_ratio is not None else "unknown"
        lines.append(
            f"- {decision.instrument_id}: {decision.decision_status}; {selected}; sleeve {decision.sleeve_id}; "
            f"ticker {decision.ticker or 'none'}; provider {decision.provider or 'none'}; symbol {decision.symbol or 'none'}; "
            f"source_status {decision.public_source_status}; as_of {decision.source_as_of or 'none'}; close {close}; "
            f"currency {decision.currency or 'unknown'}; expense_ratio {expense}; priority_score {decision.priority_score:,.2f}"
        )
        if decision.source_url:
            lines.append(f"  source_url: {decision.source_url}")
        for warning in decision.warnings:
            lines.append(f"  warning: {warning}")
    return "\n".join(lines)


def _upstream_console_output(upstream: Any) -> str:
    if upstream is None:
        return "none"
    required = ("fetcher_status", "signals", "selected_candidate_source_status")
    if all(hasattr(upstream, attr) for attr in required):
        return format_stock_fund_etf_public_source_fetcher(upstream)
    return "\n".join(
        [
            "J.A.R.V.I.S. Stock/Fund/ETF Public Source Fetcher",
            f"status: {getattr(upstream, 'status', 'unknown')}",
            f"selected stock/fund/ETF candidate: {getattr(upstream, 'selected_stock_fund_etf_candidate', 'unknown')}",
            f"selected candidate source status: {getattr(upstream, 'selected_candidate_source_status', 'unknown')}",
            "no broker connection",
            "no credentials",
            "no private account data ingestion",
            "no orders created",
            "no trades executed",
        ]
    )


def format_stock_fund_etf_sleeve_to_instrument_resolver(
    result: StockFundEtfSleeveToInstrumentResolverResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Stock/Fund/ETF Sleeve-to-Instrument Resolver",
        f"status: {result.status}",
        f"resolver status: {result.resolver_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"instrument universe path: {result.instrument_universe_path}",
        f"output resolution path: {result.output_resolution_path}",
        f"instrument universe loaded: {result.instrument_universe_loaded}",
        f"instrument universe template written: {result.instrument_universe_template_written}",
        f"instrument resolution written: {result.instrument_resolution_written}",
        f"selected sleeve: {result.selected_sleeve or 'none'}",
        f"selected sleeve amount: EUR {result.selected_sleeve_amount_eur:,.2f}",
        f"available sleeve count: {result.available_sleeve_count}",
        f"selected sleeve instrument count: {result.selected_sleeve_instrument_count}",
        f"ready instrument count: {result.ready_instrument_count}",
        f"missing source instrument count: {result.missing_source_instrument_count}",
        f"stale or failed instrument count: {result.stale_or_failed_instrument_count}",
        f"selected instrument id: {result.selected_instrument_id or 'none'}",
        f"selected instrument name: {result.selected_instrument_name or 'none'}",
        f"selected instrument ISIN: {result.selected_instrument_isin or 'none'}",
        f"selected instrument ticker: {result.selected_instrument_ticker or 'none'}",
        f"selected instrument provider: {result.selected_instrument_provider or 'none'}",
        f"selected instrument symbol: {result.selected_instrument_symbol or 'none'}",
        f"selected instrument currency: {result.selected_instrument_currency or 'none'}",
        f"selected instrument source as_of: {result.selected_instrument_source_as_of or 'none'}",
        f"selected instrument close price: {result.selected_instrument_close_price if result.selected_instrument_close_price is not None else 'none'}",
        f"selected instrument public source ready: {result.selected_instrument_public_source_ready}",
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
        _format_decisions(result),
        "",
        "Upstream public source fetcher:",
        _upstream_console_output(result.upstream_public_source_result),
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
    parser = argparse.ArgumentParser(description="Resolve stock/fund/ETF sleeves to real fresh public-data-backed instruments.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run stock/fund/ETF sleeve-to-instrument resolver.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--instrument-universe-path", default=DEFAULT_INSTRUMENT_UNIVERSE_PATH)
    parser.add_argument("--output-resolution-path", default=DEFAULT_OUTPUT_RESOLUTION_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-local-instrument-template", action="store_true", help="Write a local sleeve-to-instrument universe template under jarvis/local.")
    parser.add_argument("--write-local-resolution", action="store_true", help="Write selected real instrument resolution under jarvis/local.")
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

    result = build_stock_fund_etf_sleeve_to_instrument_resolver_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        instrument_universe_path=args.instrument_universe_path,
        output_resolution_path=args.output_resolution_path,
        max_age_days=args.max_age_days,
        write_local_instrument_template=args.write_local_instrument_template,
        write_local_resolution=args.write_local_resolution,
    )
    print(format_stock_fund_etf_sleeve_to_instrument_resolver(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())