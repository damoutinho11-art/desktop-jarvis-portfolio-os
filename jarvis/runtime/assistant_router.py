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
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.voice_briefing import build_voice_briefing_result


STATUS_READY = "JARVIS_V113_0_ASSISTANT_ROUTER_READY_SAFE"
STATUS_REFUSED = "JARVIS_V113_0_ASSISTANT_ROUTER_REFUSED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_router_latest.json"

SUPPORTED_INTENTS = [
    "finance_intelligence",
    "today_plan",
    "what_changed",
    "review_list",
    "voice_briefing",
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


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _jarvis_close(text: str) -> str:
    if "Manual-only safety is active." in text:
        return text
    return (
        f"{text}\n\n"
        "Manual-only safety is active. I can prepare the evidence, but you make the final manual decision. "
        "Ready when you are."
    )


def _daily_plan_reply(current_date: str) -> tuple[str, list[str]]:
    product = build_product_api_result(current_date=current_date)
    week = product.week_plan or {}
    selected = week.get("selected_instruments") or []
    selected_text = ", ".join(
        f"{item.get('symbol')} {_money(item.get('amount_eur'))}"
        for item in selected
        if isinstance(item, dict)
    ) or "selected instruments need review"
    reply = (
        "Good evening, Diogo. Today's manual plan is "
        f"emergency {_money(week.get('emergency_top_up_eur'))}, "
        f"crypto {_money(week.get('crypto_eur'))}, "
        f"ETF/fund {_money(week.get('etf_fund_eur'))}, and "
        f"stock {_money(week.get('individual_stock_eur'))}. "
        f"Selected review items: {selected_text}."
    )
    return _jarvis_close(reply), list(product.warnings or [])


def _dashboard_reply(current_date: str) -> tuple[str, list[str]]:
    product = build_product_api_result(current_date=current_date)
    ready = "ready for manual use" if product.dashboard_ready else "needs review"
    reply = (
        f"Good evening, Diogo. The dashboard is {ready}. "
        "Open `outputs/dashboard_latest.html` or run `Start Jarvis.bat` for the local app view."
    )
    return _jarvis_close(reply), list(product.warnings or [])


def _review_reply(current_date: str) -> tuple[str, list[str]]:
    product = build_product_api_result(current_date=current_date)
    live_news = product.live_news_context or {}
    holdings = product.manual_holdings or {}
    review_items = [
        "the manual plan amounts",
        "quote freshness in Market Movement",
        "Risk & Safety",
        "System Checks",
    ]
    if not holdings.get("holdings_ready"):
        review_items.append("manual holdings status")
    if not live_news.get("usable_count"):
        review_items.append("Market Headlines optional context")
    reply = "Good evening, Diogo. Review " + ", ".join(review_items) + "."
    return _jarvis_close(reply), list(product.warnings or [])


def _what_changed_reply() -> str:
    return _jarvis_close(
        "Good evening, Diogo. I can compare the current dashboard against safe local session memory. "
        "If this is the first run, there may be no previous snapshot yet."
    )


def _crypto_cap_reply() -> str:
    return _jarvis_close(
        "Good evening, Diogo. Crypto is capped so the manual plan stays balanced and risk-aware. "
        "Treat the cap as a review guardrail, not an instruction to act."
    )


def classify_assistant_intent(query: str) -> str:
    normalized = _normalize(query)
    if not normalized:
        return "help"
    if any(phrase in normalized for phrase in ["manual check", "before buying", "before any external action"]):
        return "finance_intelligence"
    if any(
        phrase in normalized
        for phrase in [
            "buy",
            "sell",
            "trade",
            "order",
            "execute",
            "place an order",
            "liquidate",
            "connect broker",
            "lightyear",
            "lhv",
            "ibkr",
            "interactive brokers",
            "auto rebalance",
            "rebalance automatically",
        ]
    ):
        return "safety"
    v125_alias_symbol = normalize_asset_symbol_from_query(query)
    if v125_alias_symbol is not None:
        return "asset_lookup"
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
    if any(phrase in normalized for phrase in ["read me the briefing", "voice briefing", "daily briefing"]):
        return "voice_briefing"
    if any(phrase in normalized for phrase in ["what should i review", "what to review", "review today"]):
        return "review_list"
    if any(phrase in normalized for phrase in ["what changed", "changed since last time"]):
        return "what_changed"
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
    if any(word in normalized for word in ["allocation", "why only", "why these", "why btc", "why eth", "crypto capped"]):
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
        tool = build_assistant_news_context_result(current_date=current_date)
        reply = format_assistant_news_context(tool)
        source = tool.source
        as_of = tool.current_date
        freshness = tool.freshness
        confidence = tool.confidence
        live_fetch_enabled = bool(tool.live_fetch_enabled)
        local_cache_only = not bool(tool.live_fetch_enabled)
        warnings.extend(tool.warnings)
        blockers.extend(tool.blockers)
    elif intent in {"finance_intelligence", "data_freshness", "blockers"}:
        core = build_finance_intelligence_core_result(current_date=current_date)
        reply = answer_finance_intelligence_question(query, current_date=current_date, result=core)
        source = "finance_intelligence_core"
        freshness = "normalized_local_cache"
        confidence = "medium"
        warnings.extend(core.warnings)
    elif intent == "today_plan":
        reply, product_warnings = _daily_plan_reply(current_date)
        source = "product_api.week_plan"
        freshness = "local_contract"
        confidence = "high"
        warnings.extend(product_warnings)
    elif intent == "dashboard":
        reply, product_warnings = _dashboard_reply(current_date)
        source = "product_api.dashboard"
        freshness = "local_contract"
        confidence = "high"
        warnings.extend(product_warnings)
    elif intent == "review_list":
        reply, product_warnings = _review_reply(current_date)
        source = "product_api.dashboard_review"
        freshness = "local_contract"
        confidence = "high"
        warnings.extend(product_warnings)
    elif intent == "what_changed":
        from jarvis.runtime.what_changed_since_last_time import build_what_changed_since_last_time_result

        changed = build_what_changed_since_last_time_result(current_date=current_date)
        reply = _jarvis_close(f"Good evening, Diogo. {changed.summary_text}")
        source = "jarvis_session_memory"
        freshness = "local_memory"
        confidence = "medium"
    elif intent == "voice_briefing":
        voice = build_voice_briefing_result(current_date=current_date)
        reply = voice.text
        source = "voice_briefing"
        freshness = "local_contract"
        confidence = "high"
        warnings.extend(voice.warnings)
        blockers.extend(voice.blockers)
    elif intent == "allocation_explanation":
        reply = _crypto_cap_reply()
        source = "assistant_router_policy"
        freshness = "local_contract"
        confidence = "medium"
    elif intent == "risk_summary":
        reply, product_warnings = _review_reply(current_date)
        reply = _jarvis_close(
            "Good evening, Diogo. Main risks to review are stale or missing market data, concentration, headline uncertainty, "
            "and any mismatch between the manual plan and your real external account state."
        )
        source = "product_api.risk_review"
        freshness = "local_contract"
        confidence = "medium"
        warnings.extend(product_warnings)
    elif intent == "safety":
        execution_refused = any(
            word in _normalize(query)
            for word in [
                "buy",
                "sell",
                "trade",
                "order",
                "execute",
                "liquidate",
                "broker",
                "lightyear",
                "lhv",
                "ibkr",
                "rebalance",
            ]
        )
        reply = (
            "Good evening, Diogo. I cannot connect to brokers, log into Lightyear, LHV, or IBKR, create buy/sell requests, "
            "place orders, liquidate positions, execute trades, auto-rebalance, or auto-approve anything. "
            "I can prepare the evidence, but you make the final manual decision."
        )
        if execution_refused:
            reply = "Request refused safely. " + reply
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
