from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from jarvis.runtime.assistant_data_source_registry import build_assistant_data_source_registry_result
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output


STATUS_READY = "JARVIS_V110_0_ASSISTANT_ASSET_LOOKUP_READY_SAFE"
STATUS_NOT_FOUND = "JARVIS_V110_0_ASSISTANT_ASSET_LOOKUP_NOT_FOUND_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V110_0_ASSISTANT_ASSET_LOOKUP_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_asset_lookup_latest.json"


@dataclass(frozen=True)
class AssistantAssetLookupResult:
    status: str
    current_date: str
    query: str
    matched_symbol: str | None
    matched_name: str | None
    lane: str | None
    selected_in_plan: bool
    recommended_amount_eur: float | None
    price: float | None
    currency: str | None
    source: str | None
    as_of: str | None
    freshness: str
    confidence: str
    candidate_score: float | None
    rank: int | None
    role_in_portfolio: str
    key_risks: list[str]
    available_assets: list[str]
    warnings: list[str]
    blockers: list[str]
    manual_only_safety_note: str
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_symbol(value: str) -> str:
    return value.upper().strip().replace(":", ".")


def _candidate_aliases(item: dict[str, Any]) -> set[str]:
    symbol = _normalize_symbol(str(item.get("symbol") or ""))
    aliases = {symbol}
    if symbol.endswith(".DE"):
        aliases.add(symbol[:-3])
    aliases.add(str(item.get("candidate_id") or "").upper().replace("_", "."))
    name = str(item.get("name") or "").upper()
    if name:
        aliases.add(name)
    return {alias for alias in aliases if alias}


def _risk_for_lane(lane: str | None) -> list[str]:
    if lane == "crypto":
        return [
            "crypto volatility can be severe",
            "crypto lane remains capped and requires manual review",
            "local data may not explain intraday moves without live news",
        ]
    if lane == "etf_fund":
        return [
            "ETF/fund values can fall with broad equity markets",
            "manual platform and exact instrument check remains required",
            "overlap and concentration should be reviewed before any external buy",
        ]
    if lane == "individual_stock":
        return [
            "single-stock risk is higher than diversified ETF exposure",
            "stock sleeve sizing is intentionally conservative",
            "manual company/news review remains required",
        ]
    return ["asset was not matched to a known current lane"]


def _role_for_lane(lane: str | None, symbol: str | None) -> str:
    if lane == "crypto":
        return f"{symbol} is used as selected crypto exposure in the current manual plan."
    if lane == "etf_fund":
        return f"{symbol} is used as ETF/fund exposure in the current manual plan."
    if lane == "individual_stock":
        return f"{symbol} is used as the conservative individual-stock sleeve in the current manual plan."
    return "No current portfolio role is available from local data."


@lru_cache(maxsize=8)
def _cached_product_api_result(current_date: str) -> Any:
    return build_product_api_result(current_date=current_date)


@lru_cache(maxsize=8)
def _cached_data_source_registry_result(current_date: str) -> Any:
    return build_assistant_data_source_registry_result(current_date=current_date)


@lru_cache(maxsize=1)
def _safety_ok() -> bool:
    output = build_safety_check_console_output()
    return "BLOCKED:" in output and "No execution action was taken" in output


def _match_asset(query: str, selections: list[dict[str, Any]], scores: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, bool]:
    clean = _normalize_symbol(query)
    all_rows = [(row, True) for row in selections] + [(row, False) for row in scores]
    for row, selected in all_rows:
        aliases = _candidate_aliases(row)
        if clean in aliases:
            return row, selected
    for row, selected in all_rows:
        aliases = _candidate_aliases(row)
        if any(clean and clean in alias for alias in aliases):
            return row, selected
    return None, False


def build_assistant_asset_lookup_result(
    *,
    asset: str,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantAssetLookupResult:
    product = _cached_product_api_result(current_date)
    data_sources = _cached_data_source_registry_result(current_date)
    safety_ok = _safety_ok()

    selections = list(product.week_plan.get("selected_instruments", []) or [])
    scores = list(product.candidate_scores or [])
    available_symbols = sorted({str(row.get("symbol")) for row in selections + scores if row.get("symbol")})
    row, selected = _match_asset(asset, selections, scores)

    blockers: list[str] = []
    warnings = [
        "asset lookup uses local product API and candidate score data only",
        "live price/news fetch is not enabled by this lookup",
    ]
    if not safety_ok:
        blockers.append("safety check did not block execution")

    if row is None:
        blockers.append(f"unknown asset: {asset}")
        result = AssistantAssetLookupResult(
            status=STATUS_NOT_FOUND,
            current_date=current_date,
            query=asset,
            matched_symbol=None,
            matched_name=None,
            lane=None,
            selected_in_plan=False,
            recommended_amount_eur=None,
            price=None,
            currency=None,
            source=None,
            as_of=None,
            freshness="unavailable",
            confidence="low",
            candidate_score=None,
            rank=None,
            role_in_portfolio="No match found in local selected instruments or candidate scores.",
            key_risks=_risk_for_lane(None),
            available_assets=available_symbols,
            warnings=warnings,
            blockers=blockers,
            manual_only_safety_note="Read-only lookup. No broker, order, trade, or auto-approval path is enabled.",
            execution_forbidden=True,
            broker_connection=False,
            credentials_used=False,
            order_created=False,
            trade_executed=False,
            report_written=bool(write_report),
            report_path=str(output_path),
        )
    else:
        symbol = str(row.get("symbol") or "").upper()
        lane = str(row.get("lane") or "")
        amount = row.get("amount_eur") if selected else None
        score = row.get("score")
        rank = None
        if score is not None:
            lane_scores = [item for item in scores if item.get("lane") == lane]
            ordered = sorted(lane_scores, key=lambda item: float(item.get("score") or 0.0), reverse=True)
            for index, item in enumerate(ordered, start=1):
                if _normalize_symbol(str(item.get("symbol") or "")) == symbol:
                    rank = index
                    break
        elif selected:
            score_row, _ = _match_asset(symbol, [], scores)
            if score_row:
                score = score_row.get("score")
                lane_scores = [item for item in scores if item.get("lane") == lane]
                ordered = sorted(lane_scores, key=lambda item: float(item.get("score") or 0.0), reverse=True)
                for index, item in enumerate(ordered, start=1):
                    if _normalize_symbol(str(item.get("symbol") or "")) == symbol:
                        rank = index
                        break

        source = str(row.get("source") or "product_api.instrument_summary")
        as_of = str(row.get("as_of") or current_date) if selected else None
        source_lane = {
            "crypto": "crypto_prices",
            "etf_fund": "etf_fund_prices",
            "individual_stock": "stock_prices",
        }.get(lane)
        source_status = next((source for source in data_sources.sources if source.source_id == source_lane), None)
        freshness = "ready" if source_status and source_status.ready_for_assistant else "partial_or_unavailable"
        confidence = "medium" if selected else "low"
        if score is not None and float(score) >= 0.75:
            confidence = "medium_high" if selected else "medium"

        result = AssistantAssetLookupResult(
            status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
            current_date=current_date,
            query=asset,
            matched_symbol=symbol,
            matched_name=str(row.get("name") or symbol),
            lane=lane,
            selected_in_plan=selected,
            recommended_amount_eur=round(float(amount), 2) if amount is not None else None,
            price=None,
            currency="EUR" if selected else None,
            source=source,
            as_of=as_of,
            freshness=freshness,
            confidence=confidence,
            candidate_score=round(float(score), 4) if score is not None else None,
            rank=rank,
            role_in_portfolio=_role_for_lane(lane, symbol),
            key_risks=_risk_for_lane(lane),
            available_assets=available_symbols,
            warnings=warnings,
            blockers=blockers,
            manual_only_safety_note="Read-only lookup. No broker, order, trade, or auto-approval path is enabled.",
            execution_forbidden=True,
            broker_connection=False,
            credentials_used=False,
            order_created=False,
            trade_executed=False,
            report_written=bool(write_report),
            report_path=str(output_path),
        )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def build_etf_comparison_result(
    *,
    current_date: str = "2026-06-18",
) -> list[AssistantAssetLookupResult]:
    product = _cached_product_api_result(current_date)
    etf_symbols = [
        str(item.get("symbol"))
        for item in product.week_plan.get("selected_instruments", []) or []
        if item.get("lane") == "etf_fund" and item.get("symbol")
    ]
    return [
        build_assistant_asset_lookup_result(asset=symbol, current_date=current_date)
        for symbol in etf_symbols
    ]


def format_assistant_asset_lookup(result: AssistantAssetLookupResult) -> str:
    if result.status == STATUS_NOT_FOUND:
        available = ", ".join(result.available_assets[:20])
        return "\n".join(
            [
                f"I could not find {result.query} in local selected instruments or candidate scores.",
                f"Available assets include: {available or 'none'}.",
                "Data / Source / Freshness: local product API only; freshness unavailable for this unknown asset.",
                f"Safety: {result.manual_only_safety_note}",
            ]
        )

    amount = (
        f" It receives EUR {result.recommended_amount_eur:.2f} in the current manual plan."
        if result.recommended_amount_eur is not None
        else " It is not selected in the current manual plan."
    )
    score = f" Candidate score: {result.candidate_score:.0%}." if result.candidate_score is not None else ""
    rank = f" Rank in lane: {result.rank}." if result.rank is not None else ""
    risks = "; ".join(result.key_risks)
    return "\n".join(
        [
            f"{result.matched_symbol} is {result.matched_name} in the {result.lane} lane.{amount}",
            f"Why: {result.role_in_portfolio}{score}{rank}",
            (
                "Data / Source / Freshness: "
                f"source={result.source}; as_of={result.as_of or 'not available'}; "
                f"freshness={result.freshness}; confidence={result.confidence}; "
                "live fetch enabled=False; local cache only=True."
            ),
            f"Risks: {risks}.",
            "Manual checklist: confirm exact instrument, platform availability, latest price/news, and personal suitability before any external action.",
            f"Safety: {result.manual_only_safety_note}",
        ]
    )


def format_etf_comparison(results: list[AssistantAssetLookupResult]) -> str:
    if not results:
        return "No ETF/fund selections are available in the local plan. Safety: read-only and manual-only."
    lines = ["ETF/fund comparison from local plan data:"]
    for result in results:
        lines.append(
            f"- {result.matched_symbol}: EUR {result.recommended_amount_eur:.2f}; "
            f"score={result.candidate_score if result.candidate_score is not None else 'n/a'}; "
            f"source={result.source}; as_of={result.as_of}; freshness={result.freshness}"
        )
    lines.append("This is a comparison, not a buy/sell request. Manual approval remains required.")
    return "\n".join(lines)


def format_assistant_asset_lookup_report(result: AssistantAssetLookupResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT ASSET LOOKUP",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"query: {result.query}",
        f"matched symbol: {result.matched_symbol}",
        f"matched name: {result.matched_name}",
        f"lane: {result.lane}",
        f"selected in plan: {result.selected_in_plan}",
        f"recommended amount EUR: {result.recommended_amount_eur}",
        f"price: {result.price}",
        f"currency: {result.currency}",
        f"source: {result.source}",
        f"as_of: {result.as_of}",
        f"freshness: {result.freshness}",
        f"confidence: {result.confidence}",
        f"candidate score: {result.candidate_score}",
        f"rank: {result.rank}",
        "",
        "ROLE:",
        result.role_in_portfolio,
        "",
        "RISKS:",
    ]
    lines.extend(f"- {risk}" for risk in result.key_risks or ["none"])
    lines.append("")
    lines.append("WARNINGS:")
    lines.extend(f"- {warning}" for warning in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.extend(
        [
            "",
            "SAFETY:",
            f"- manual-only note: {result.manual_only_safety_note}",
            f"- execution forbidden: {result.execution_forbidden}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "",
            "HUMAN REPLY:",
            format_assistant_asset_lookup(result),
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant asset lookup.")
    parser.add_argument("--assistant-asset-lookup", action="store_true")
    parser.add_argument("--asset", default="")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_asset_lookup_result(
        asset=args.asset,
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_asset_lookup_report(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_NOT_FOUND",
    "STATUS_REVIEW_REQUIRED",
    "AssistantAssetLookupResult",
    "build_assistant_asset_lookup_result",
    "build_etf_comparison_result",
    "format_assistant_asset_lookup",
    "format_etf_comparison",
    "format_assistant_asset_lookup_report",
    "main",
]
