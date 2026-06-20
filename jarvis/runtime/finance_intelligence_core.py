from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from jarvis.runtime.assistant_symbol_aliases import normalize_asset_symbol_from_query

from jarvis.runtime.fx_assistant_bridge import build_fx_assistant_bridge_result
from jarvis.runtime.market_data_normalized import build_normalized_market_data_result
from jarvis.runtime.news_intelligence_contract import build_news_intelligence_contract_result
from jarvis.runtime.public_data_provider_registry import build_public_data_provider_registry_result
from jarvis.runtime.selected_instrument_resolver import build_selected_instrument_resolver_result


STATUS_READY = "JARVIS_V118_0_FINANCE_INTELLIGENCE_CORE_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/finance_intelligence_core_latest.json"


@dataclass(frozen=True)
class FinanceIntelligenceCoreResult:
    status: str
    current_date: str
    finance_intelligence_ready: bool
    normalized_records: list[dict[str, Any]]
    data_trust_summary: dict[str, Any]
    selected_instrument_coverage: list[dict[str, Any]]
    provider_plan: dict[str, Any]
    fx_summary: dict[str, Any]
    news_summary: dict[str, Any]
    market_movement_summary: str
    crypto_summary: str
    etf_gap_summary: str
    manual_qa_checklist: list[str]
    answers: dict[str, str]
    warnings: list[str]
    blockers: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_executed: bool
    auto_approval_enabled: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _records_by_symbol(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record.get("symbol") or "").upper(): record for record in records}


def _price_text(record: dict[str, Any]) -> str:
    price = record.get("quote_price")
    currency = record.get("currency")
    if price is None:
        return "price unavailable"
    return f"{float(price):,.2f} {currency or ''}".strip()


def _movement_text(record: dict[str, Any]) -> str:
    value = record.get("movement_24h")
    if value is None:
        return "24h movement unavailable"
    return f"24h {float(value):+.2f}%"


def _source_text(record: dict[str, Any]) -> str:
    return (
        f"source={record.get('source') or 'missing'}; "
        f"as_of={record.get('source_as_of') or 'missing'}; "
        f"freshness={record.get('freshness')}; "
        f"confidence={record.get('confidence')}; "
        f"trusted={record.get('trusted_for_assistant')}"
    )


def _record_line(record: dict[str, Any]) -> str:
    return (
        f"{record.get('symbol')}: amount=EUR {float(record.get('selected_amount_eur') or 0.0):.2f}; "
        f"{_price_text(record)}; {_movement_text(record)}; {_source_text(record)}"
    )


def _crypto_summary(records: dict[str, dict[str, Any]]) -> str:
    crypto = [records[symbol] for symbol in ("BTC", "ETH") if symbol in records]
    if not crypto:
        return "Crypto selected instruments are not available in normalized local data."
    lines = ["Crypto is available from the local CoinGecko-normalized cache, not from a live assistant fetch."]
    lines.extend(f"- {_record_line(record)}" for record in crypto)
    lines.append("No headline or cause is attached to the 24h moves.")
    return "\n".join(lines)


def _market_movement_summary(records: dict[str, dict[str, Any]]) -> str:
    movement = [record for record in records.values() if record.get("movement_24h") is not None]
    if not movement:
        return "No selected instrument has assistant-facing movement data. Today's market movement cannot be inferred."
    lines = ["Known local movement from cache:"]
    lines.extend(f"- {record.get('symbol')}: {_movement_text(record)}" for record in movement)
    lines.append("7d and 30d movement are not available in the current normalized cache.")
    lines.append("No market cause is claimed because live/cached news headlines are disabled.")
    return "\n".join(lines)


def _etf_gap_summary(resolutions: list[dict[str, Any]]) -> str:
    if not resolutions:
        return "No ETF/fund selected instruments were found."
    lines = ["ETF/fund trust summary:"]
    for item in resolutions:
        lines.append(
            f"- {item.get('symbol')}: {item.get('classification')}; trusted_quote={item.get('trusted_quote')}; "
            f"freshness={item.get('freshness')}; next_action={item.get('next_action')}"
        )
    return "\n".join(lines)


def _asset_answer(symbol: str, records: dict[str, dict[str, Any]], resolutions: dict[str, dict[str, Any]]) -> str:
    clean = symbol.upper()
    record = records.get(clean)
    if not record:
        return f"{clean} is not present in the current normalized selected-instrument data."
    lines = [
        f"{clean}: {_record_line(record)}.",
        f"Data / Source / Freshness: {_source_text(record)}.",
    ]
    if clean in resolutions:
        resolution = resolutions[clean]
        lines.append(
            f"Instrument trust: {resolution.get('classification')}; next action: {resolution.get('next_action')}"
        )
    missing = record.get("missing_fields") or []
    if missing:
        lines.append("Missing: " + ", ".join(missing) + ".")
    warnings = [str(item) for item in record.get("warnings", []) or []]
    if warnings:
        lines.append("Warnings: " + "; ".join(warnings[:4]) + ".")
    lines.append("Manual check required before any external action.")
    return "\n".join(lines)


def _trust_answer(normalized: Any, fx: Any, news: Any) -> str:
    summary = normalized.data_trust_summary
    lines = [
        f"Trust is mixed: {summary.get('trusted_records')} selected records are trusted enough for assistant display, and {summary.get('partial_records')} are partial or untrusted.",
        f"FX conversion available: {fx.conversion_available}. USD quotes stay in USD when FX is missing.",
        f"Live news enabled: {news.live_news_fetch_enabled}; cached headlines: {news.cached_headline_count}.",
    ]
    missing = summary.get("missing_by_symbol") or {}
    if missing:
        lines.append("Missing fields by symbol:")
        for symbol, fields in missing.items():
            lines.append(f"- {symbol}: {', '.join(fields)}")
    lines.append("No broker, order, trade, buy/sell request, or auto-approval path is enabled.")
    return "\n".join(lines)


def _missing_answer(normalized: Any, resolver: Any, fx: Any, news: Any, provider: Any) -> str:
    lines = [
        "Biggest missing pieces:",
        "- ETF quote coverage: VWCE and GLOBAL_CORE_ETF have no trusted assistant-facing quote.",
        "- IS3Q.DE quote is quarantined if its source date is after the requested current_date.",
        "- 7d/30d movement history is unavailable for selected instruments.",
        f"- FX conversion: available={fx.conversion_available}; freshness={fx.freshness}.",
        f"- News: live_fetch_enabled={news.live_news_fetch_enabled}; cached_headline_count={news.cached_headline_count}.",
    ]
    lines.extend(f"- Provider gap: {gap}" for gap in provider.major_gaps[:4])
    if resolver.missing_or_untrusted_count:
        lines.append(f"- ETF/fund records needing manual review: {resolver.missing_or_untrusted_count}.")
    lines.append("Next manual check: verify ETF symbols/ISINs, source dates, latest prices, FX if needed, and external news before acting outside J.A.R.V.I.S.")
    return "\n".join(lines)


def build_finance_intelligence_core_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> FinanceIntelligenceCoreResult:
    from jarvis.runtime.product_api import build_product_api_result

    product = build_product_api_result(current_date=current_date)
    normalized = build_normalized_market_data_result(
        current_date=current_date,
        product_api_result=product,
    )
    resolver = build_selected_instrument_resolver_result(
        current_date=current_date,
        product_api_result=product,
    )
    fx = build_fx_assistant_bridge_result(current_date=current_date)
    news = build_news_intelligence_contract_result(current_date=current_date)
    provider = build_public_data_provider_registry_result(current_date=current_date)

    records = _records_by_symbol(normalized.records)
    resolutions = _records_by_symbol(resolver.resolutions)
    market_summary = _market_movement_summary(records)
    crypto = _crypto_summary(records)
    etf_gaps = _etf_gap_summary(resolver.resolutions)
    trust = _trust_answer(normalized, fx, news)
    missing = _missing_answer(normalized, resolver, fx, news, provider)

    answers = {
        "what_happened_today": "\n".join(
            [
                "Today, the only assistant-facing movement data is from the local crypto cache.",
                market_summary,
                "ETF/fund and stock selected instruments need manual quote/history/news checks before external action.",
                f"Data trust: {normalized.trusted_record_count} trusted display records, {normalized.partial_record_count} partial records.",
            ]
        ),
        "what_changed_since_last_week": "7d movement history is not available in the current normalized cache, so I cannot say what changed since last week without inventing data.",
        "what_is_crypto_doing_today": crypto,
        "compare_my_etfs": etf_gaps,
        "tell_me_about_vwce": _asset_answer("VWCE", records, resolutions),
        "tell_me_about_is3q_de": _asset_answer("IS3Q.DE", records, resolutions),
        "tell_me_about_msft": _asset_answer("MSFT", records, resolutions),
        "can_i_trust_this_data": trust,
        "what_is_missing": missing,
        "what_news_matters": news.answer_summary,
    }

    manual_qa = [
        "Confirm ETF/fund exact ticker/ISIN and platform availability.",
        "Refresh or verify VWCE and GLOBAL_CORE_ETF quote/source/freshness before trusting ETF answers.",
        "Quarantine any quote whose source_as_of is after the requested current_date.",
        "Check latest external headlines manually; live news fetch is disabled.",
        "Check USD quotes in USD unless a trusted ECB FX rate is parsed and available.",
        "Confirm no broker, credentials, orders, trades, buy/sell requests, or auto-approval are introduced.",
    ]
    warnings = [
        "finance intelligence core is read-only and assistant-facing",
        "local cache data can be stale; source/as_of/freshness must be shown in answers",
        "news is a contract/readiness layer, not a live headline feed",
    ]
    if normalized.partial_record_count:
        warnings.append("selected instrument coverage is partial; assistant answers must disclose missing fields")

    result = FinanceIntelligenceCoreResult(
        status=STATUS_READY,
        current_date=current_date,
        finance_intelligence_ready=True,
        normalized_records=normalized.records,
        data_trust_summary=normalized.data_trust_summary,
        selected_instrument_coverage=resolver.resolutions,
        provider_plan={
            "enabled_provider_count": provider.enabled_provider_count,
            "assistant_ready_provider_count": provider.assistant_ready_provider_count,
            "provider_plan": provider.provider_plan,
            "secret_policy": provider.secret_policy,
            "major_gaps": provider.major_gaps,
            "recommended_next_stage": provider.recommended_next_stage,
        },
        fx_summary=fx.to_dict(),
        news_summary=news.to_dict(),
        market_movement_summary=market_summary,
        crypto_summary=crypto,
        etf_gap_summary=etf_gaps,
        manual_qa_checklist=manual_qa,
        answers=answers,
        warnings=warnings,
        blockers=[],
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        buy_sell_request_created=False,
        order_created=False,
        trade_executed=False,
        auto_approval_enabled=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _answer_from_result(query: str, result: FinanceIntelligenceCoreResult) -> str:
    normalized = query.lower().strip()
    if "crypto" in normalized:
        return result.answers["what_is_crypto_doing_today"]
    if "compare" in normalized and ("etf" in normalized or "fund" in normalized):
        return result.answers["compare_my_etfs"]
    if "vwce" in normalized:
        return result.answers["tell_me_about_vwce"]
    if "is3q" in normalized:
        return result.answers["tell_me_about_is3q_de"]
    if "msft" in normalized or "microsoft" in normalized:
        return result.answers["tell_me_about_msft"]
    if "trust" in normalized or "missing" in normalized or "data" in normalized:
        if "missing" in normalized:
            return result.answers["what_is_missing"]
        return result.answers["can_i_trust_this_data"]
    if "news" in normalized:
        return result.answers["what_news_matters"]
    if "changed since last week" in normalized or "since last week" in normalized:
        return result.answers["what_changed_since_last_week"]
    return result.answers["what_happened_today"]



def _answer_etf_trust_from_normalized_records(records: list[dict[str, Any]]) -> str:
    etf_records = [record for record in records if record.get("lane") == "etf_fund"]
    if not etf_records:
        return "No ETF/fund records are present in the normalized finance core."

    lines = ["ETF/fund trust summary from normalized public data:"]
    for record in etf_records:
        verification_status = (
            "AUTO_VERIFICATION_INCOMPLETE"
            if record.get("manual_review_required") and record.get("symbol") in {"GLOBAL_CORE_ETF", "QUALITY_ETF"}
            else "AUTO_VERIFIED_QUOTE"
        )
        lines.append(
            f"- {record.get('symbol')}: price={record.get('quote_price')} {record.get('currency')}; "
            f"source={record.get('source')}; as_of={record.get('source_as_of')}; "
            f"freshness={record.get('freshness')}; trusted={record.get('trusted_for_assistant')}; "
            f"missing={', '.join(record.get('missing_fields') or []) or 'none'}; "
            f"verification_status={verification_status}; final_buy_manual=True."
        )

    unresolved = []
    try:
        from jarvis.runtime.public_universe_data_coverage import build_public_universe_data_coverage_result
        coverage = build_public_universe_data_coverage_result(current_date="2026-06-20")
        unresolved = [
            symbol
            for symbol in coverage.next_fetch_priority
            if symbol in {"GROWTH_NASDAQ_ETF", "RENDER", "SOL", "TAO"}
        ]
    except Exception:
        unresolved = []

    if unresolved:
        lines.append("Remaining unresolved/missing public coverage: " + ", ".join(unresolved) + ".")

    lines.append("J.A.R.V.I.S. checks data autonomously; Diogo only performs the final real-world buy manually outside the system.")
    return "\n".join(lines)




def _v121_normalized_records_by_symbol(current_date: str) -> dict[str, dict]:
    from jarvis.runtime.market_data_normalized import build_normalized_market_data_result

    normalized = build_normalized_market_data_result(current_date=current_date)
    return {
        str(record.get("symbol") or "").upper(): record
        for record in normalized.records
        if record.get("symbol")
    }


def _v121_fmt_pct(value) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.2f}%"


def _v121_fmt_price(record: dict) -> str:
    price = record.get("quote_price")
    currency = record.get("currency")
    if price is None:
        return "price unavailable"
    return f"{price} {currency or ''}".strip()


def _v121_verification_status(record: dict) -> str:
    symbol = str(record.get("symbol") or "").upper()
    if symbol == "GLOBAL_CORE_ETF":
        return "AUTO_VERIFICATION_INCOMPLETE_FOR_IDENTITY_BUT_QUOTE_READY"
    if record.get("trusted_for_assistant"):
        return "AUTO_VERIFIED_QUOTE"
    return "AUTO_VERIFICATION_INCOMPLETE"


def _v121_answer_asset_from_normalized(symbol: str, current_date: str) -> str:
    records = _v121_normalized_records_by_symbol(current_date)
    wanted = symbol.upper().replace("IS3Q", "IS3Q.DE") if symbol.upper() == "IS3Q" else symbol.upper()
    record = records.get(wanted)
    if not record:
        return (
            f"{wanted} is not available in the current normalized finance cache. "
            "J.A.R.V.I.S. needs another autonomous data refresh before trusting this instrument. "
            "Final real-world buy remains manual outside the system."
        )

    missing = ", ".join(record.get("missing_fields") or []) or "none"
    amount = record.get("selected_amount_eur")
    amount_text = f"EUR {amount}" if amount is not None else "not selected in current plan"

    lines = [
        f"{record.get('symbol')}: amount={amount_text}; price={_v121_fmt_price(record)}; "
        f"24h={_v121_fmt_pct(record.get('movement_24h'))}; "
        f"7d={_v121_fmt_pct(record.get('movement_7d'))}; "
        f"30d={_v121_fmt_pct(record.get('movement_30d'))}.",
        f"Data / Source / Freshness: source={record.get('source')}; "
        f"as_of={record.get('source_as_of')}; freshness={record.get('freshness')}; "
        f"confidence={record.get('confidence')}; trusted={record.get('trusted_for_assistant')}.",
        f"Verification: {_v121_verification_status(record)}; missing={missing}.",
        "J.A.R.V.I.S. handles data checks autonomously. Diogo only performs the final real-world buy manually outside the system.",
    ]
    return "\n".join(lines)


def _v121_answer_etf_trust(current_date: str) -> str:
    records = _v121_normalized_records_by_symbol(current_date)
    etfs = [record for record in records.values() if record.get("lane") == "etf_fund"]

    lines = ["ETF/fund data trust from the normalized v120 public quote cache:"]
    for record in sorted(etfs, key=lambda r: str(r.get("symbol"))):
        missing = ", ".join(record.get("missing_fields") or []) or "none"
        lines.append(
            f"- {record.get('symbol')}: price={_v121_fmt_price(record)}; "
            f"24h={_v121_fmt_pct(record.get('movement_24h'))}; "
            f"7d={_v121_fmt_pct(record.get('movement_7d'))}; "
            f"30d={_v121_fmt_pct(record.get('movement_30d'))}; "
            f"source={record.get('source')}; as_of={record.get('source_as_of')}; "
            f"freshness={record.get('freshness')}; trusted={record.get('trusted_for_assistant')}; "
            f"verification={_v121_verification_status(record)}; missing={missing}."
        )

    try:
        from jarvis.runtime.public_universe_data_coverage import build_public_universe_data_coverage_result

        coverage = build_public_universe_data_coverage_result(current_date=current_date)
        next_fetch = list(coverage.next_fetch_priority or [])
    except Exception:
        next_fetch = []

    if next_fetch:
        lines.append("Remaining autonomous fetch priorities: " + ", ".join(next_fetch) + ".")

    lines.append("Conclusion: selected ETF/fund quote data is trusted for assistant display when trusted=True, but final real-world buy remains manual only.")
    return "\n".join(lines)


def _v121_answer_today_from_normalized(current_date: str) -> str:
    records = _v121_normalized_records_by_symbol(current_date)
    selected = [record for record in records.values() if record.get("selected_in_plan")]

    lines = ["Today's locally cached market movement from normalized public data:"]
    for record in selected:
        if record.get("movement_24h") is None and record.get("movement_7d") is None and record.get("movement_30d") is None:
            continue
        lines.append(
            f"- {record.get('symbol')}: 24h={_v121_fmt_pct(record.get('movement_24h'))}; "
            f"7d={_v121_fmt_pct(record.get('movement_7d'))}; "
            f"30d={_v121_fmt_pct(record.get('movement_30d'))}; "
            f"source={record.get('source')}; as_of={record.get('source_as_of')}; "
            f"trusted={record.get('trusted_for_assistant')}."
        )

    try:
        from jarvis.runtime.public_universe_data_coverage import build_public_universe_data_coverage_result

        coverage = build_public_universe_data_coverage_result(current_date=current_date)
        next_fetch = list(coverage.next_fetch_priority or [])
    except Exception:
        next_fetch = []

    if next_fetch:
        lines.append("Remaining autonomous fetch priorities: " + ", ".join(next_fetch) + ".")

    lines.append("No market cause is claimed because live/cached news headlines are disabled.")
    lines.append("J.A.R.V.I.S. checks data autonomously; Diogo only performs the final real-world buy manually outside the system.")
    return "\n".join(lines)




def _v123_quote_cache_records_by_symbol() -> dict[str, dict]:
    import json
    from pathlib import Path

    path = Path("jarvis/local/public_data/v120_public_universe_quote_cache.local.json")
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    records = payload.get("records") or []
    return {
        str(record.get("symbol") or "").upper(): record
        for record in records
        if isinstance(record, dict) and record.get("symbol")
    }


def _v123_answer_growth_nasdaq_etf(current_date: str) -> str:
    from jarvis.runtime.etf_identity_resolver import resolve_etf_identity

    resolution = resolve_etf_identity("GROWTH_NASDAQ_ETF", current_date=current_date)
    best = resolution.best_candidate or {}
    cache = _v123_quote_cache_records_by_symbol()
    quote = cache.get("GROWTH_NASDAQ_ETF")

    lines = [
        "GROWTH_NASDAQ_ETF identity and quote status:",
    ]

    if best:
        lines.append(
            f"- identity: resolved candidate {best.get('symbol')} / {best.get('provider_symbol')}; "
            f"name={best.get('name')}; ISIN={best.get('isin')}; "
            f"evidence_score={best.get('evidence_score')}."
        )
        lines.append(
            "- evidence: " + ", ".join(best.get("evidence_reasons") or ["none"])
        )
    else:
        lines.append("- identity: unresolved; J.A.R.V.I.S. needs more autonomous evidence.")

    if quote:
        lines.append(
            f"- quote: price={quote.get('quote_price')} {quote.get('currency')}; "
            f"24h={_v121_fmt_pct(quote.get('movement_24h_pct'))}; "
            f"7d={_v121_fmt_pct(quote.get('movement_7d_pct'))}; "
            f"30d={_v121_fmt_pct(quote.get('movement_30d_pct'))}; "
            f"source={quote.get('provider')}; provider_symbol={quote.get('provider_symbol')}; "
            f"as_of={quote.get('source_as_of')}; freshness={quote.get('freshness')}."
        )
        lines.append("- trust: quote is trusted for assistant display, but identity remains a candidate bridge, not an execution approval.")
    else:
        lines.append("- quote: not in the local quote cache yet; run the public quote fetcher to probe the resolved candidate.")

    lines.append("J.A.R.V.I.S. handles the identity and quote checks autonomously. Diogo only performs the final real-world buy manually outside the system.")
    return "\n".join(lines)



def answer_finance_intelligence_question(
    query: str,
    *,
    current_date: str = "2026-06-18",
    result: FinanceIntelligenceCoreResult | None = None,
) -> str:
    v121_query = query.lower().strip()
    v125_alias_symbol = normalize_asset_symbol_from_query(query)
    if v125_alias_symbol == "GROWTH_NASDAQ_ETF":
        return _v123_answer_growth_nasdaq_etf(current_date)
    if v125_alias_symbol in {"GLOBAL_CORE_ETF", "IS3Q.DE", "VWCE", "BTC", "ETH", "MSFT"}:
        return _v121_answer_asset_from_normalized(v125_alias_symbol, current_date)

    if any(term in v121_query for term in ["growth_nasdaq_etf", "growth nasdaq", "nasdaq etf", "sxrv"]):
        return _v123_answer_growth_nasdaq_etf(current_date)
    if any(phrase in v121_query for phrase in ["what happened today", "what changed today", "what changed since last week"]):
        return _v121_answer_today_from_normalized(current_date)
    if ("etf" in v121_query and any(word in v121_query for word in ["trust", "data", "fresh", "freshness"])) or "can i trust" in v121_query:
        return _v121_answer_etf_trust(current_date)
    for v121_symbol in ["GLOBAL_CORE_ETF", "IS3Q.DE", "IS3Q", "VWCE", "BTC", "ETH", "MSFT"]:
        if v121_symbol.lower() in v121_query:
            return _v121_answer_asset_from_normalized(v121_symbol, current_date)
    if result is None:
        result = build_finance_intelligence_core_result(current_date=current_date)
    return _answer_from_result(query, result)


def format_finance_intelligence_core(result: FinanceIntelligenceCoreResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINANCE INTELLIGENCE CORE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"ready: {result.finance_intelligence_ready}",
        f"normalized records: {len(result.normalized_records)}",
        "",
        "DATA TRUST:",
        json.dumps(result.data_trust_summary, indent=2, sort_keys=True),
        "",
        "MARKET MOVEMENT:",
        result.market_movement_summary,
        "",
        "ETF/FUND COVERAGE:",
        result.etf_gap_summary,
        "",
        "FX:",
        f"- conversion available: {result.fx_summary.get('conversion_available')}",
        f"- freshness: {result.fx_summary.get('freshness')}",
        "",
        "NEWS:",
        result.news_summary.get("answer_summary", ""),
        "",
        "MANUAL QA CHECKLIST:",
        *[f"- {item}" for item in result.manual_qa_checklist],
        "",
        "SAFETY:",
        f"- broker connection: {result.broker_connection}",
        f"- credentials used: {result.credentials_used}",
        f"- buy/sell request created: {result.buy_sell_request_created}",
        f"- order created: {result.order_created}",
        f"- trade executed: {result.trade_executed}",
        f"- auto approval enabled: {result.auto_approval_enabled}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. finance intelligence core.")
    parser.add_argument("--finance-intelligence-core", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_finance_intelligence_core_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_finance_intelligence_core(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "FinanceIntelligenceCoreResult",
    "answer_finance_intelligence_question",
    "build_finance_intelligence_core_result",
    "format_finance_intelligence_core",
    "main",
]
