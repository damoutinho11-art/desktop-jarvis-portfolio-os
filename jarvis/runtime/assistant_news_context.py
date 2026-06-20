from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.live_news_fetcher import (
    DEFAULT_LIVE_NEWS_CACHE_PATH,
    build_live_news_fetcher_result,
)
from jarvis.runtime.news_coverage_readiness import build_news_coverage_readiness_result


STATUS_READY = "JARVIS_V112_0_ASSISTANT_NEWS_CONTEXT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V112_0_ASSISTANT_NEWS_CONTEXT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_news_context_latest.json"


@dataclass(frozen=True)
class AssistantNewsContextResult:
    status: str
    current_date: str
    categories: list[str]
    covered_categories: list[str]
    missing_categories: list[str]
    local_cached_news_available: bool
    live_fetch_enabled: bool
    manual_review_required: bool
    cached_headline_count: int
    headline_context: list[dict[str, Any]]
    source_failures: list[dict[str, Any]]
    live_news_cache_path: str
    summary: str
    source: str
    as_of: str
    freshness: str
    confidence: str
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


def _build_readonly_news_context(current_date: str, live_news_cache_path: str | Path) -> AssistantNewsContextResult:
    readiness = build_news_coverage_readiness_result(current_date=current_date)
    live_news = build_live_news_fetcher_result(
        current_date=current_date,
        cache_path=live_news_cache_path,
        fetch_news=False,
    )
    blockers = list(readiness.blockers)
    blockers.extend(live_news.blockers)
    warnings = [
        "Assistant news context uses local cached headline context only; it does not fetch live news by itself.",
        "Headlines are possible context only, not proof of price-movement causality.",
        "Manual review is required before relying on any external news.",
    ]
    warnings.extend(live_news.warnings)
    headline_context = list(live_news.top_headlines)
    if headline_context:
        summary = (
            "Local cached headline context is available. Treat it as possible context only; "
            "verify source timestamps and URLs before any external action."
        )
    else:
        summary = (
            "No local live headline cache is available yet. Run --live-news-fetch --write-news-cache "
            "to collect read-only public headline context."
        )
    return AssistantNewsContextResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        categories=list(readiness.required_categories),
        covered_categories=list(readiness.covered_categories),
        missing_categories=list(readiness.missing_categories),
        local_cached_news_available=bool(live_news.usable_count),
        live_fetch_enabled=bool(live_news.fetch_attempted),
        manual_review_required=True,
        cached_headline_count=int(live_news.usable_count),
        headline_context=headline_context,
        source_failures=list(live_news.source_failures),
        live_news_cache_path=str(live_news.cache_path),
        summary=summary,
        source="live_news_cache + news_coverage_readiness",
        as_of=current_date,
        freshness="local_cache" if live_news.usable_count else "no_local_live_news_cache",
        confidence="medium_for_source_labels_low_for_causality",
        warnings=list(dict.fromkeys(warnings + list(readiness.warnings))),
        blockers=blockers,
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        report_written=False,
        report_path=str(DEFAULT_OUTPUT_PATH),
    )


def build_assistant_news_context_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
    live_news_cache_path: str | Path = DEFAULT_LIVE_NEWS_CACHE_PATH,
) -> AssistantNewsContextResult:
    result = _build_readonly_news_context(current_date, live_news_cache_path)
    if write_report:
        result = AssistantNewsContextResult(
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


def format_assistant_news_context(result: AssistantNewsContextResult) -> str:
    if result.headline_context:
        headline_lines = ["Headline context (possible context only):"]
        for item in result.headline_context[:5]:
            headline_lines.append(
                "- "
                f"{item.get('title')} "
                f"(source={item.get('source')}; freshness={item.get('freshness_status')}; url={item.get('url') or 'n/a'})"
            )
    else:
        headline_lines = ["Headline context: no local live headline cache is available."]
    return "\n".join(
        [
            f"Coverage categories: {', '.join(result.categories)}.",
            f"Missing categories: {', '.join(result.missing_categories) or 'none'}.",
            f"Cached headline count: {result.cached_headline_count}.",
            *headline_lines,
            "I will not say headlines caused a price move without direct evidence; treat them as possible context.",
            f"Manual review required: {result.manual_review_required}.",
            f"Summary: {result.summary}",
            (
                "Data / Source / Freshness: "
                f"source={result.source}; as_of={result.as_of}; freshness={result.freshness}; "
                f"confidence={result.confidence}; live fetch enabled={result.live_fetch_enabled}; "
                f"local cached news available={result.local_cached_news_available}; "
                f"cache_path={result.live_news_cache_path}."
            ),
            "Manual checklist: check reputable external headlines, source timestamps, and relevance before any external action.",
            "Safety: read-only news context. No broker, order, trade, buy/sell request, headline fabrication, or auto-approval path is enabled.",
        ]
    )


def format_assistant_news_context_report(result: AssistantNewsContextResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT NEWS CONTEXT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"live fetch enabled: {result.live_fetch_enabled}",
        f"local cached news available: {result.local_cached_news_available}",
        f"manual review required: {result.manual_review_required}",
        f"cached headline count: {result.cached_headline_count}",
        f"source: {result.source}",
        f"as_of: {result.as_of}",
        f"freshness: {result.freshness}",
        f"confidence: {result.confidence}",
        "",
        "CATEGORIES:",
        f"- required: {', '.join(result.categories)}",
        f"- covered: {', '.join(result.covered_categories) or 'none'}",
        f"- missing: {', '.join(result.missing_categories) or 'none'}",
        "",
        "HEADLINE CONTEXT:",
    ]
    if result.headline_context:
        lines.extend(f"- {item.get('title')} | source={item.get('source')} | freshness={item.get('freshness_status')}" for item in result.headline_context)
    else:
        lines.append("- none")
    lines.extend([
        "WARNINGS:",
    ])
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
            format_assistant_news_context(result),
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant news context.")
    parser.add_argument("--assistant-news-context", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--news-cache-path", default=DEFAULT_LIVE_NEWS_CACHE_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_news_context_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
        live_news_cache_path=args.news_cache_path,
    )
    print(format_assistant_news_context_report(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "AssistantNewsContextResult",
    "build_assistant_news_context_result",
    "format_assistant_news_context",
    "format_assistant_news_context_report",
    "main",
]
