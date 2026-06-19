from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from jarvis.runtime.assistant_asset_lookup import (
    AssistantAssetLookupResult,
    build_assistant_asset_lookup_result,
)
from jarvis.runtime.assistant_data_source_registry import build_assistant_data_source_registry_result
from jarvis.runtime.assistant_market_data_bridge import find_market_data_record
from jarvis.runtime.product_api import build_product_api_result


STATUS_READY = "JARVIS_V111_0_ASSISTANT_MARKET_CONTEXT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V111_0_ASSISTANT_MARKET_CONTEXT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_market_context_latest.json"


@dataclass(frozen=True)
class AssistantMarketContextResult:
    status: str
    current_date: str
    context_type: str
    assets: list[dict[str, Any]]
    portfolio_impact: str
    movement_summary: str
    news_summary: str
    source: str
    as_of: str
    freshness: str
    confidence: str
    live_fetch_enabled: bool
    local_cache_only: bool
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


def _asset_summary(result: AssistantAssetLookupResult, current_date: str) -> dict[str, Any]:
    market_record = find_market_data_record(result.matched_symbol or "", current_date=current_date) or {}
    return {
        "symbol": result.matched_symbol,
        "name": result.matched_name,
        "lane": result.lane,
        "selected_in_plan": result.selected_in_plan,
        "recommended_amount_eur": result.recommended_amount_eur,
        "price": result.price if result.price is not None else market_record.get("current_price"),
        "currency": result.currency or market_record.get("currency"),
        "source": result.source or market_record.get("source"),
        "as_of": result.as_of or market_record.get("as_of"),
        "freshness": result.freshness,
        "confidence": result.confidence,
        "candidate_score": result.candidate_score,
        "rank": result.rank,
        "movement_24h_pct": market_record.get("movement_24h_pct"),
        "movement_7d_pct": market_record.get("movement_7d_pct"),
        "movement_available": bool(market_record.get("movement_available")),
        "missing_fields": list(market_record.get("missing_fields", []) or []),
        "warnings": list(dict.fromkeys(list(result.warnings) + list(market_record.get("warnings", []) or []))),
        "blockers": list(result.blockers),
    }


def build_assistant_market_context_result(
    *,
    context_type: str = "market",
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantMarketContextResult:
    result = _build_readonly_assistant_market_context_result(context_type, current_date)

    if write_report:
        result = AssistantMarketContextResult(
            **{
                **result.to_dict(),
                "report_written": True,
                "report_path": str(output_path),
            }
        )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


@lru_cache(maxsize=16)
def _build_readonly_assistant_market_context_result(
    context_type: str,
    current_date: str,
) -> AssistantMarketContextResult:
    normalized_context = context_type.lower().strip() or "market"
    product = build_product_api_result(current_date=current_date)
    data_sources = build_assistant_data_source_registry_result(current_date=current_date)

    selected = list(product.week_plan.get("selected_instruments", []) or [])
    if normalized_context == "crypto":
        symbols = [str(item.get("symbol")) for item in selected if item.get("lane") == "crypto" and item.get("symbol")]
    elif normalized_context in {"etf", "fund", "etf_fund"}:
        symbols = [str(item.get("symbol")) for item in selected if item.get("lane") == "etf_fund" and item.get("symbol")]
    elif normalized_context in {"stock", "stocks"}:
        symbols = [str(item.get("symbol")) for item in selected if item.get("lane") == "individual_stock" and item.get("symbol")]
    else:
        symbols = [str(item.get("symbol")) for item in selected if item.get("symbol")]

    lookup_results = [
        build_assistant_asset_lookup_result(asset=symbol, current_date=current_date)
        for symbol in symbols
    ]
    assets = [_asset_summary(result, current_date) for result in lookup_results if result.matched_symbol]

    source_ids = {
        "crypto": ["crypto_prices", "macro_news"],
        "etf": ["etf_fund_prices", "macro_news"],
        "fund": ["etf_fund_prices", "macro_news"],
        "etf_fund": ["etf_fund_prices", "macro_news"],
        "stock": ["stock_prices", "macro_news"],
        "stocks": ["stock_prices", "macro_news"],
        "market": ["crypto_prices", "etf_fund_prices", "stock_prices", "macro_news"],
    }.get(normalized_context, ["crypto_prices", "etf_fund_prices", "stock_prices", "macro_news"])
    relevant_sources = [source for source in data_sources.sources if source.source_id in source_ids]
    ready_sources = [source for source in relevant_sources if source.ready_for_assistant]
    blockers = []
    warnings = [
        "market context uses local product API, assistant asset lookup, and data source registry only",
        "live market/news fetch is not enabled by this tool",
        "movement direction and causes cannot be determined without current price history or live news",
    ]
    if not assets:
        blockers.append(f"no selected assets found for context type: {normalized_context}")

    freshness = "ready" if ready_sources else "partial_or_unavailable"
    if any(not source.live_fetch_supported for source in relevant_sources):
        warnings.append("one or more relevant sources are local-cache/manual-only")
    if any(source.source_id == "macro_news" and not source.ready_for_assistant for source in relevant_sources):
        warnings.append("live news is unavailable; manual news review is required")

    crypto_amount = sum(float(item.get("amount_eur") or 0.0) for item in selected if item.get("lane") == "crypto")
    investable_amount = sum(float(item.get("amount_eur") or 0.0) for item in selected)
    monthly_value = (
        product.week_plan.get("monthly_contribution_eur")
        or product.week_plan.get("monthly_amount_eur")
        or product.week_plan.get("monthly_eur")
        or product.week_plan.get("total_monthly_amount_eur")
        or product.week_plan.get("total_amount_eur")
    )
    try:
        monthly_amount = float(monthly_value)
    except (TypeError, ValueError):
        monthly_amount = investable_amount + 75.0
    emergency_value = product.week_plan.get("emergency_top_up_eur") or product.week_plan.get("emergency_amount_eur")
    try:
        emergency_amount = float(emergency_value)
    except (TypeError, ValueError):
        emergency_amount = max(monthly_amount - investable_amount, 0.0)

    portfolio_impact = (
        f"Crypto selected amount is EUR {crypto_amount:.2f}; crypto remains capped at 20% / EUR 100.00 this cycle. "
        f"Selected investable instruments total EUR {investable_amount:.2f}; full monthly manual plan is EUR {monthly_amount:.2f}, "
        f"including EUR {emergency_amount:.2f} emergency top-up if applicable. "
        "J.A.R.V.I.S. can describe local plan exposure but does not change allocations or create orders."
    )
    movement_assets = [asset for asset in assets if asset.get("movement_available")]
    if movement_assets:
        movement_bits = []
        for asset in movement_assets:
            value = asset.get("movement_24h_pct")
            if value is not None:
                movement_bits.append(f"{asset.get('symbol')} 24h {float(value):+.2f}%")
        movement_summary = (
            "Local normalized cache shows: "
            + ("; ".join(movement_bits) if movement_bits else "movement fields present but not printable")
            + ". This is local cache movement, not a live headline or claimed cause."
        )
    else:
        movement_summary = (
            "Local data does not include enough current price-history context; today's movement cannot be determined from this cache. "
            "Manually check latest quotes and source timestamps before acting externally."
        )
    news_summary = (
        "Live news fetch is not enabled. I can only report local readiness and cached/source availability; no headline or cause is claimed."
    )
    source = ", ".join(source.source_id for source in relevant_sources) or "local_product_api"
    as_of_values = [asset.get("as_of") for asset in assets if asset.get("as_of")]
    as_of = max(str(value) for value in as_of_values) if as_of_values else current_date
    confidence = "medium" if assets and ready_sources else "low"

    return AssistantMarketContextResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        context_type=normalized_context,
        assets=assets,
        portfolio_impact=portfolio_impact,
        movement_summary=movement_summary,
        news_summary=news_summary,
        source=source,
        as_of=as_of,
        freshness=freshness,
        confidence=confidence,
        live_fetch_enabled=False,
        local_cache_only=True,
        warnings=list(dict.fromkeys(warnings)),
        blockers=blockers,
        manual_only_safety_note="Read-only market context. No broker, order, trade, buy/sell request, or auto-approval path is enabled.",
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        report_written=False,
        report_path=str(DEFAULT_OUTPUT_PATH),
    )


def format_assistant_market_context(result: AssistantMarketContextResult) -> str:
    if not result.assets:
        return "\n".join(
            [
                f"I do not have local selected assets for {result.context_type} context.",
                f"Blockers: {', '.join(result.blockers) or 'none'}.",
                (
                    "Data / Source / Freshness: "
                    f"source={result.source}; as_of={result.as_of}; freshness={result.freshness}; "
                    f"confidence={result.confidence}; live fetch enabled={result.live_fetch_enabled}; local cache only={result.local_cache_only}."
                ),
                f"Safety: {result.manual_only_safety_note}",
            ]
        )

    asset_lines = []
    for asset in result.assets:
        amount = asset.get("recommended_amount_eur")
        amount_text = f"EUR {float(amount):.2f}" if amount is not None else "not selected"
        movement = asset.get("movement_24h_pct")
        movement_text = f"; 24h={float(movement):+.2f}%" if movement is not None else "; 24h=not available"
        price = asset.get("price")
        currency = asset.get("currency")
        price_text = f"{price} {currency}" if price is not None and currency else "not available"
        asset_lines.append(
            f"- {asset.get('symbol')}: {amount_text}; price={price_text}{movement_text}; "
            f"source={asset.get('source')}; as_of={asset.get('as_of')}; freshness={asset.get('freshness')}"
        )
    return "\n".join(
        [
            f"Based on local data, {result.context_type} context is available but not live.",
            "Current local assets:",
            *asset_lines,
            f"What changed: {result.movement_summary}",
            f"News: {result.news_summary}",
            f"What this means for your plan: {result.portfolio_impact}",
            (
                "Data / Source / Freshness: "
                f"source={result.source}; as_of={result.as_of}; freshness={result.freshness}; "
                f"confidence={result.confidence}; live fetch enabled={result.live_fetch_enabled}; local cache only={result.local_cache_only}."
            ),
            "Manual checklist: verify latest market quotes, any major news, platform availability, and personal suitability before any external action.",
            f"Safety: {result.manual_only_safety_note}",
        ]
    )


def format_assistant_market_context_report(result: AssistantMarketContextResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT MARKET CONTEXT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"context type: {result.context_type}",
        f"asset count: {len(result.assets)}",
        f"source: {result.source}",
        f"as_of: {result.as_of}",
        f"freshness: {result.freshness}",
        f"confidence: {result.confidence}",
        f"live fetch enabled: {result.live_fetch_enabled}",
        f"local cache only: {result.local_cache_only}",
        "",
        "ASSETS:",
    ]
    for asset in result.assets:
        lines.append(
            f"- {asset.get('symbol')}: amount={asset.get('recommended_amount_eur')}; "
            f"price={asset.get('price')}; source={asset.get('source')}; as_of={asset.get('as_of')}"
        )
    if not result.assets:
        lines.append("- none")
    lines.extend(
        [
            "",
            "MOVEMENT:",
            result.movement_summary,
            "",
            "NEWS:",
            result.news_summary,
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {warning}" for warning in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.extend(
        [
            "",
            "SAFETY:",
            f"- execution forbidden: {result.execution_forbidden}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "",
            "HUMAN REPLY:",
            format_assistant_market_context(result),
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant market context.")
    parser.add_argument("--assistant-market-context", action="store_true")
    parser.add_argument("--context", default="market")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_market_context_result(
        context_type=args.context,
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_market_context_report(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "AssistantMarketContextResult",
    "build_assistant_market_context_result",
    "format_assistant_market_context",
    "format_assistant_market_context_report",
    "main",
]
