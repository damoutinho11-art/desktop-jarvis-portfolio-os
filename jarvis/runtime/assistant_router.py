from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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


STATUS_READY = "JARVIS_V113_0_ASSISTANT_ROUTER_READY_SAFE"
STATUS_REFUSED = "JARVIS_V113_0_ASSISTANT_ROUTER_REFUSED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_router_latest.json"

SUPPORTED_INTENTS = [
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
    upper = query.upper().replace("?", " ")
    for candidate in ["IS3Q.DE", "GLOBAL_CORE_ETF", "VWCE", "MSFT", "BTC", "ETH", "IS3Q"]:
        if candidate in upper:
            return candidate
    return query


def classify_assistant_intent(query: str) -> str:
    normalized = _normalize(query)
    if not normalized:
        return "help"
    if any(word in normalized for word in ["buy", "sell", "trade", "order", "execute", "place an order"]):
        return "safety"
    if any(word in normalized for word in ["dashboard", "open dashboard"]):
        return "dashboard"
    if any(word in normalized for word in ["safe", "safety", "can you trade", "broker", "credential"]):
        return "safety"
    if any(word in normalized for word in ["blocker", "blocked", "warning", "problem"]):
        return "blockers"
    if any(word in normalized for word in ["freshness", "trust this data", "can i trust"]):
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
        tool = build_assistant_asset_lookup_result(asset=_extract_asset_query(query), current_date=current_date)
        reply = format_assistant_asset_lookup(tool)
        source = str(tool.source)
        as_of = str(tool.as_of or current_date)
        freshness = tool.freshness
        confidence = tool.confidence
        blockers.extend(tool.blockers)
    elif intent == "etf_compare":
        reply = format_etf_comparison(build_etf_comparison_result(current_date=current_date))
        source = "assistant_asset_lookup"
        freshness = "local_product_plan"
    elif intent == "crypto_market_context":
        tool = build_assistant_market_context_result(context_type="crypto", current_date=current_date)
        reply = format_assistant_market_context(tool)
        source = tool.source
        as_of = tool.as_of
        freshness = tool.freshness
        confidence = tool.confidence
        blockers.extend(tool.blockers)
    elif intent == "market_context":
        tool = build_assistant_market_context_result(context_type="market", current_date=current_date)
        reply = format_assistant_market_context(tool)
        source = tool.source
        as_of = tool.as_of
        freshness = tool.freshness
        confidence = tool.confidence
        blockers.extend(tool.blockers)
    elif intent == "news_context":
        tool = build_assistant_news_context_result(current_date=current_date)
        reply = format_assistant_news_context(tool)
        source = tool.source
        as_of = tool.as_of
        freshness = tool.freshness
        confidence = tool.confidence
        blockers.extend(tool.blockers)
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
