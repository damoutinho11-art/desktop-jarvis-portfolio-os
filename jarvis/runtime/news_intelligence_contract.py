from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V118_0_NEWS_INTELLIGENCE_CONTRACT_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/news_intelligence_contract_latest.json"
DEFAULT_NEWS_CACHE_PATH = Path("jarvis/local/news/headlines.local.json")


@dataclass(frozen=True)
class NewsIntelligenceContractResult:
    status: str
    current_date: str
    live_news_fetch_enabled: bool
    local_cached_news_available: bool
    cached_headline_count: int
    cache_path: str
    future_headline_schema: list[str]
    relevance_dimensions: list[str]
    portfolio_symbols: list[str]
    answer_summary: str
    warnings: list[str]
    blockers: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _cached_headlines(path: Path) -> list[dict[str, Any]]:
    data = _read_json(path)
    if not isinstance(data, dict):
        return []
    headlines = data.get("headlines", [])
    return [item for item in headlines if isinstance(item, dict)]


def build_news_intelligence_contract_result(
    *,
    current_date: str = "2026-06-18",
    cache_path: str | Path = DEFAULT_NEWS_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> NewsIntelligenceContractResult:
    resolved_cache = Path(cache_path)
    headlines = _cached_headlines(resolved_cache)
    local_cached_news_available = bool(headlines)
    answer_summary = (
        "No cached headlines are available, and live news fetch is disabled. "
        "J.A.R.V.I.S. can list what data is missing and what external sources Diogo should check, "
        "but it must not invent headlines or market causes."
    )
    if local_cached_news_available:
        answer_summary = (
            "Cached headlines are available locally. Each answer must show source, timestamp, URL/id, "
            "and relevance reason before making any portfolio-relevance claim."
        )

    warnings = [
        "live news fetch is disabled",
        "no fake headlines are generated",
        "no market cause is claimed without a sourced cached headline and matching market data",
        "future provider keys must be optional environment variables and must never be written to cache/logs/reports/URLs",
    ]
    result = NewsIntelligenceContractResult(
        status=STATUS_READY,
        current_date=current_date,
        live_news_fetch_enabled=False,
        local_cached_news_available=local_cached_news_available,
        cached_headline_count=len(headlines),
        cache_path=str(resolved_cache),
        future_headline_schema=[
            "headline_id",
            "source",
            "published_at",
            "url",
            "title",
            "summary",
            "symbols",
            "lanes",
            "macro_tags",
            "relevance_reason",
            "confidence",
        ],
        relevance_dimensions=[
            "direct_symbol_match",
            "portfolio_lane_match",
            "macro_rate_or_fx_context",
            "crypto_market_structure",
            "ETF_region_or_factor_exposure",
            "freshness_and_source_quality",
        ],
        portfolio_symbols=["BTC", "ETH", "GLOBAL_CORE_ETF", "VWCE", "IS3Q.DE", "MSFT"],
        answer_summary=answer_summary,
        warnings=warnings,
        blockers=[],
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
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_news_intelligence_contract(result: NewsIntelligenceContractResult) -> str:
    lines = [
        "J.A.R.V.I.S. NEWS INTELLIGENCE CONTRACT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"live news fetch enabled: {result.live_news_fetch_enabled}",
        f"local cached news available: {result.local_cached_news_available}",
        f"cached headline count: {result.cached_headline_count}",
        f"cache path: {result.cache_path}",
        "answer:",
        result.answer_summary,
        "",
        "FUTURE HEADLINE SCHEMA:",
        *[f"- {field}" for field in result.future_headline_schema],
        "",
        "RELEVANCE PLAN:",
        *[f"- {field}" for field in result.relevance_dimensions],
        "",
        "WARNINGS:",
        *[f"- {warning}" for warning in result.warnings],
        "safety: no broker, credentials, orders, trades, fake headlines, or auto-approval.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run safe news intelligence contract.")
    parser.add_argument("--news-intelligence-contract", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--cache-path", default=str(DEFAULT_NEWS_CACHE_PATH))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_news_intelligence_contract_result(
        current_date=args.current_date,
        cache_path=args.cache_path,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_news_intelligence_contract(result))
    return 0


__all__ = [
    "STATUS_READY",
    "NewsIntelligenceContractResult",
    "build_news_intelligence_contract_result",
    "format_news_intelligence_contract",
    "main",
]
