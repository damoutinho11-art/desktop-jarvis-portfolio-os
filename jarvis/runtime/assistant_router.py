from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from jarvis.runtime.assistant_symbol_aliases import normalize_asset_symbol_from_query

from jarvis.runtime.assistant_asset_lookup import (
    build_assistant_asset_lookup_result,
    build_etf_comparison_result,
    format_assistant_asset_lookup,
    format_etf_comparison,
)
from jarvis.runtime.assistant_market_context import (
    build_assistant_market_context_result,
    format_assistant_market_context,
)
from jarvis.runtime.assistant_news_context import (
    build_assistant_news_context_result,
    format_assistant_news_context,
)
from jarvis.runtime.chat_interface_contract import build_chat_interface_contract_result, format_chat_reply
from jarvis.runtime.finance_intelligence_core import (
    answer_finance_intelligence_question,
    build_finance_intelligence_core_result,
)
from jarvis.runtime.news_intelligence_contract import build_news_intelligence_contract_result


STATUS_READY = "JARVIS_V113_0_ASSISTANT_ROUTER_READY_SAFE"
STATUS_REFUSED = "JARVIS_V113_0_ASSISTANT_ROUTER_REFUSED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_router_latest.json"

SUPPORTED_INTENTS = [
    "finance_intelligence",
    "today_plan",
    "portfolio_overview",
    "asset_lookup",
    "etf_compare",
    "crypto_market_context",
    "market_context",
    "news_context",
    "allocation_explanation",
    "risk_summary",
    "data_freshness",
    "blockers",
    "safety",
    "dashboard",
    "help",
    "unsupported",
]


@dataclass(frozen=True)
class AssistantRouterResult:
    status: str
    current_date: str
    query: str
    intent: str
    tool_id: str
    reply: str
    source: str
    as_of: str
    freshness: str
    confidence: str
    live_fetch_enabled: bool
    local_cache_only: bool
    warnings: list[str]
    blockers: list[str]
    safety_note: str
    execution_refused: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize(value: str) -> str:
    return value.lower().strip()


def _extract_asset_query(query: str) -> str:
    alias = normalize_asset_symbol_from_query(query)
    if alias:
        return alias
    upper = query.upper().replace("?", " ")
    for candidate in ["GROWTH_NASDAQ_ETF", "GLOBAL_CORE_ETF", "IS3Q.DE", "VWCE", "MSFT", "BTC", "ETH", "IS3Q"]:
        if candidate in upper:
            return candidate
    return query


def classify_assistant_intent(query: str) -> str:
    normalized = _normalize(query)
    v125_alias_symbol = normalize_asset_symbol_from_query(query)
    if v125_alias_symbol is not None:
        return "asset_lookup"
    if not normalized:
        return "help"
    if any(phrase in normalized for phrase in ["manual check", "before buying", "before any external action"]):
        return "finance_intelligence"
    if any(word in normalized for word in ["buy", "sell", "trade", "order", "execute", "place an order"]):
        return "safety"
    if any(word in normalized for word in ["dashboard", "open dashboard"]):
        return "dashboard"
    if any(word in normalized for word in ["safe", "safety", "can you trade", "broker", "credential"]):
        return "safety"
    if any(phrase in normalized for phrase in ["what happened today", "what changed since last week", "changed since last week", "manual check", "before buying"]):
        return "finance_intelligence"
    if any(word in normalized for word in ["blocker", "blocked", "warning", "problem"]):
        return "blockers"
    if any(word in normalized for word in ["freshness", "trust this data", "can i trust", "missing"]):
        return "data_freshness"
    if any(word in normalized for word in ["risk", "risks"]):
        return "risk_summary"
    if any(word in normalized for word in ["news", "headline", "headlines"]) or "why is crypto moving" in normalized:
        return "news_context"
    if "crypto" in normalized and any(word in normalized for word in ["doing", "market", "moving", "changed", "today"]):
        return "crypto_market_context"
    if any(word in normalized for word in ["what changed", "markets", "market doing", "important today"]):
        return "market_context"
    if any(word in normalized for word in ["compare etf", "compare my etf", "compare the etf", "compare funds"]):
        return "etf_compare"
    known_symbols = ["btc", "eth", "vwce", "is3q", "is3q.de", "msft", "global_core_etf"]
    if any(symbol in normalized for symbol in known_symbols):
        return "asset_lookup"
    if any(word in normalized for word in ["allocation", "why only", "why these", "why btc", "why eth"]):
        return "allocation_explanation"
    if any(word in normalized for word in ["plan today", "today plan", "my plan", "portfolio overview", "how am i doing"]):
        return "today_plan"
    return "help"


def build_assistant_router_result(
    *,
    query: str,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantRouterResult:
    intent = classify_assistant_intent(query)
    warnings = ["assistant router is read-only and manual-only"]
    blockers: list[str] = []
    source = "chat_interface_contract"
    as_of = current_date
    freshness = "local_contract"
    confidence = "medium"
    live_fetch_enabled = False
    local_cache_only = True
    tool_id = intent
    execution_refused = False

    if intent == "asset_lookup":
        asset = _extract_asset_query(query)
        if asset.upper() in {"BTC", "ETH", "VWCE", "GLOBAL_CORE_ETF", "GROWTH_NASDAQ_ETF", "IS3Q", "IS3Q.DE", "MSFT"}:
            core = build_finance_intelligence_core_result(current_date=current_date)
            reply = answer_finance_intelligence_question(asset, current_date=current_date, result=core)
            source = "finance_intelligence_core.normalized_market_data"
            as_of = current_date
            freshness = "normalized_local_cache"
            confidence = "medium"
            warnings.extend(core.warnings)
        else:
            tool = build_assistant_asset_lookup_result(asset=asset, current_date=current_date)
            reply = format_assistant_asset_lookup(tool)
            if tool.price is not None and "Price:" not in reply:
                price_line = f"Price: {float(tool.price):,.2f} {tool.currency or ''}."
                reply_lines = reply.splitlines()
                insert_at = 1 if reply_lines else 0
                reply_lines.insert(insert_at, price_line)
                reply = "\n".join(reply_lines)
            source = str(tool.source)
            as_of = str(tool.as_of or current_date)
            freshness = tool.freshness
            confidence = tool.confidence
            blockers.extend(tool.blockers)
    elif intent == "etf_compare":
        core = build_finance_intelligence_core_result(current_date=current_date)
        reply = core.answers["compare_my_etfs"]
        source = "finance_intelligence_core.selected_instrument_resolver"
        freshness = "normalized_local_cache"
        confidence = "medium"
        warnings.extend(core.warnings)
    elif intent == "crypto_market_context":
        core = build_finance_intelligence_core_result(current_date=current_date)
        reply = core.answers["what_is_crypto_doing_today"]
        source = "finance_intelligence_core.normalized_market_data"
        freshness = "normalized_local_cache"
        confidence = "medium"
        warnings.extend(core.warnings)
    elif intent == "market_context":
        core = build_finance_intelligence_core_result(current_date=current_date)
        reply = answer_finance_intelligence_question(query, current_date=current_date, result=core)
        source = "finance_intelligence_core"
        freshness = "normalized_local_cache"
        confidence = "medium"
        warnings.extend(core.warnings)
    elif intent == "news_context":
        tool = build_news_intelligence_contract_result(current_date=current_date)
        reply = "\n".join(
            [
                tool.answer_summary,
                (
                    "Data / Source / Freshness: source=news_intelligence_contract; "
                    f"as_of={tool.current_date}; live_news_fetch_enabled={tool.live_news_fetch_enabled}; "
                    f"local_cached_news_available={tool.local_cached_news_available}; cached_headline_count={tool.cached_headline_count}."
                ),
                "Manual checklist: check reputable external headlines, timestamps, URLs, and relevance before any external action.",
            ]
        )
        source = "news_intelligence_contract"
        as_of = tool.current_date
        freshness = "news_contract_no_live_fetch"
        confidence = "medium_for_contract_low_for_headlines"
        blockers.extend(tool.blockers)
    elif intent in {"finance_intelligence", "data_freshness", "blockers"}:
        core = build_finance_intelligence_core_result(current_date=current_date)
        reply = answer_finance_intelligence_question(query, current_date=current_date, result=core)
        source = "finance_intelligence_core"
        freshness = "normalized_local_cache"
        confidence = "medium"
        warnings.extend(core.warnings)
    elif intent == "safety":
        execution_refused = any(word in _normalize(query) for word in ["buy", "sell", "trade", "order", "execute"])
        reply = (
            "Safety is active. J.A.R.V.I.S. is read-only and manual-only: no broker connection, no credentials, "
            "no buy/sell request creation, no orders, no trades, and no auto-approval. "
            "I can summarize local data and produce manual checklists, but Diogo performs any real-world action externally."
        )
        if execution_refused:
            reply = "I cannot create buy/sell requests, place orders, connect to a broker, or execute trades. " + reply
        source = "assistant_router_safety"
        freshness = "not_applicable"
        confidence = "high"
    else:
        fallback = build_chat_interface_contract_result(query=query, current_date=current_date)
        reply = format_chat_reply(fallback)
        source = "chat_interface_contract"
        as_of = fallback.current_date
        freshness = "local_contract"
        confidence = "medium"
        blockers.extend(fallback.blockers)

    safety_note = "Read-only assistant route. No broker, credentials, order, trade, buy/sell request, or auto-approval path is enabled."
    result = AssistantRouterResult(
        status=STATUS_REFUSED if execution_refused else STATUS_READY,
        current_date=current_date,
        query=query,
        intent=intent,
        tool_id=tool_id,
        reply=reply,
        source=source,
        as_of=as_of,
        freshness=freshness,
        confidence=confidence,
        live_fetch_enabled=live_fetch_enabled,
        local_cache_only=local_cache_only,
        warnings=warnings,
        blockers=blockers,
        safety_note=safety_note,
        execution_refused=execution_refused,
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


def format_assistant_router_result(result: AssistantRouterResult) -> str:
    return "\n".join(
        [
            "J.A.R.V.I.S. ASSISTANT ROUTER",
            f"status: {result.status}",
            f"intent: {result.intent}",
            f"tool: {result.tool_id}",
            f"source: {result.source}",
            f"as_of: {result.as_of}",
            f"freshness: {result.freshness}",
            f"confidence: {result.confidence}",
            f"live fetch enabled: {result.live_fetch_enabled}",
            f"local cache only: {result.local_cache_only}",
            "",
            "REPLY:",
            result.reply,
            "",
            "SAFETY:",
            result.safety_note,
            f"broker connection: {result.broker_connection}",
            f"credentials used: {result.credentials_used}",
            f"order created: {result.order_created}",
            f"trade executed: {result.trade_executed}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant router.")
    parser.add_argument("--assistant-router", action="store_true")
    parser.add_argument("--query", default="")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_router_result(
        query=args.query,
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_router_result(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REFUSED",
    "SUPPORTED_INTENTS",
    "AssistantRouterResult",
    "classify_assistant_intent",
    "build_assistant_router_result",
    "format_assistant_router_result",
    "main",
]
