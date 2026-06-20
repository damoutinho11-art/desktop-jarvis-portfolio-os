"""J.A.R.V.I.S. v135.0 read-only live news fetcher.

Fetches public/free RSS-style headlines as context only. It never requires
credentials, never logs in, never scrapes behind auth, and never creates
recommendations, approvals, orders, or trades.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V135_0_LIVE_NEWS_FETCHER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V135_0_LIVE_NEWS_FETCHER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V135_0_LIVE_NEWS_FETCHER_BLOCKED_SAFE"

DEFAULT_LIVE_NEWS_CACHE_PATH = "jarvis/local/live_news_cache.local.json"
SCHEMA_VERSION = "JARVIS_LIVE_NEWS_CACHE_V1"

DEFAULT_FEEDS: tuple[dict[str, Any], ...] = (
    {
        "source": "CoinDesk public RSS",
        "feed_url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
        "default_entity_tags": ["crypto market"],
        "default_lane_tags": ["crypto"],
    },
    {
        "source": "Cointelegraph public RSS",
        "feed_url": "https://cointelegraph.com/rss",
        "default_entity_tags": ["crypto market"],
        "default_lane_tags": ["crypto"],
    },
    {
        "source": "ECB public RSS",
        "feed_url": "https://www.ecb.europa.eu/rss/press.html",
        "default_entity_tags": ["macro", "rates", "central bank"],
        "default_lane_tags": ["macro"],
    },
    {
        "source": "Microsoft public blog RSS",
        "feed_url": "https://blogs.microsoft.com/feed/",
        "default_entity_tags": ["MSFT"],
        "default_lane_tags": ["individual_stock"],
    },
    {
        "source": "MarketWatch public top stories RSS",
        "feed_url": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "default_entity_tags": ["ETF/fund", "global equity market", "macro"],
        "default_lane_tags": ["etf_fund", "macro"],
    },
)


@dataclass(frozen=True)
class LiveNewsFetcherResult:
    status: str
    current_date: str
    fetched_at: str
    fetch_attempted: bool
    cache_path: str
    cache_loaded: bool
    cache_written: bool
    fetched_count: int
    usable_count: int
    stale_count: int
    source_failures: list[dict[str, str]]
    headlines: list[dict[str, Any]]
    top_headlines: list[dict[str, Any]]
    warnings: list[str]
    blockers: list[str]
    safety_flags: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


FeedFetcher = Callable[[Mapping[str, Any], float], str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dedupe(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element: ET.Element, names: set[str]) -> str:
    for child in list(element):
        if _local_name(child.tag) in names:
            return _safe_text(child.text)
    return ""


def _entry_link(element: ET.Element) -> str:
    direct = _child_text(element, {"link"})
    if direct:
        return direct
    for child in list(element):
        if _local_name(child.tag) == "link":
            href = child.attrib.get("href")
            if href:
                return _safe_text(href)
    return ""


def _parse_published_date(value: str) -> datetime | None:
    text = _safe_text(value)
    if not text:
        return None
    try:
        parsed = parsedate_to_datetime(text)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        normalized = text.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _freshness_status(published_at: str, current_date: str) -> str:
    parsed = _parse_published_date(published_at)
    if parsed is None:
        return "unknown_published_at"
    try:
        current = datetime.fromisoformat(current_date).replace(tzinfo=timezone.utc)
    except Exception:
        current = datetime.now(timezone.utc)
    age_days = abs((current.date() - parsed.date()).days)
    if age_days <= 1:
        return "fresh"
    if age_days <= 7:
        return "recent"
    return "stale"


def _classify_tags(title: str, summary: str, feed: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    text = f"{title} {summary}".lower()
    entity_tags: list[str] = []
    lane_tags: list[str] = []

    if any(word in text for word in ("bitcoin", " btc ", "btc-", "btc:", "btc")):
        entity_tags.append("BTC")
        lane_tags.append("crypto")
    if any(word in text for word in ("ethereum", " ether ", " eth ", "eth-", "eth:", "eth")):
        entity_tags.append("ETH")
        lane_tags.append("crypto")
    if any(word in text for word in ("crypto", "digital asset", "stablecoin", "token")):
        entity_tags.append("crypto market")
        lane_tags.append("crypto")
    if any(word in text for word in ("microsoft", "msft", "azure", "windows")):
        entity_tags.append("MSFT")
        lane_tags.append("individual_stock")
    if any(word in text for word in ("etf", "fund", "global equity", "equities", "stocks", "msci", "world market")):
        entity_tags.append("ETF/fund")
        entity_tags.append("global equity market")
        lane_tags.append("etf_fund")
    if any(word in text for word in ("inflation", "rates", "central bank", "ecb", "fed", "macro", "monetary")):
        entity_tags.append("macro")
        lane_tags.append("macro")

    if not entity_tags:
        entity_tags.extend(str(item) for item in feed.get("default_entity_tags", []) or [])
    if not lane_tags:
        lane_tags.extend(str(item) for item in feed.get("default_lane_tags", []) or [])

    return _dedupe(entity_tags), _dedupe(lane_tags)


def _parse_feed_items(feed_xml: str, feed: Mapping[str, Any], *, current_date: str) -> list[dict[str, Any]]:
    root = ET.fromstring(feed_xml)
    entries: list[ET.Element] = []
    for element in root.iter():
        local = _local_name(element.tag)
        if local in {"item", "entry"}:
            entries.append(element)

    parsed_items: list[dict[str, Any]] = []
    for entry in entries:
        title = _child_text(entry, {"title"})
        summary = _child_text(entry, {"description", "summary", "content", "subtitle"})
        published_at = _child_text(entry, {"pubdate", "published", "updated", "date"})
        url = _entry_link(entry)
        if not title:
            continue
        entity_tags, lane_tags = _classify_tags(title, summary, feed)
        parsed_items.append(
            {
                "schema_version": SCHEMA_VERSION,
                "current_date": current_date,
                "source": str(feed.get("source") or "public RSS"),
                "source_url": str(feed.get("feed_url") or ""),
                "feed_url": str(feed.get("feed_url") or ""),
                "title": title,
                "summary": summary,
                "published_at": published_at or None,
                "entity_tags": entity_tags,
                "lane_tags": lane_tags,
                "url": url,
                "freshness_status": _freshness_status(published_at, current_date),
                "trusted_read_only": True,
            }
        )
    return parsed_items


def _default_feed_fetcher(feed: Mapping[str, Any], timeout_seconds: float) -> str:
    url = str(feed.get("feed_url") or "")
    request = Request(
        url,
        headers={
            "User-Agent": "JARVIS-Portfolio-OS/135 read-only public RSS checker",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.5",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8", errors="replace")


def _safety_flags() -> dict[str, Any]:
    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    return {
        "trusted_read_only": True,
        "public_free_sources_only": True,
        "credentials_used": False,
        "browser_login": False,
        "auth_scraping": False,
        "recommendation_mutation": False,
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "buy_request_created": False,
        "sell_request_created": False,
        "broker_connection": False,
        "order_created": False,
        "trade_executed": False,
        "auto_approval": False,
        "safety_check_blocked_execution": safety_blocked,
    }


def _cache_payload(result: LiveNewsFetcherResult) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "current_date": result.current_date,
        "fetched_at": result.fetched_at,
        "trusted_read_only": True,
        "items": result.headlines,
        "source_failures": result.source_failures,
        "warnings": result.warnings,
    }


def _load_cache(path: Path, current_date: str) -> tuple[bool, list[dict[str, Any]], list[str], list[dict[str, str]]]:
    if not path.exists():
        return False, [], ["live news cache missing; run --live-news-fetch --write-news-cache to create it"], []
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return False, [], [f"live news cache unreadable: {exc}"], []
    if not isinstance(payload, Mapping):
        return False, [], ["live news cache root is not an object"], []
    items = payload.get("items", [])
    if not isinstance(items, list):
        items = []
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        row.setdefault("schema_version", SCHEMA_VERSION)
        row.setdefault("current_date", current_date)
        row.setdefault("trusted_read_only", True)
        row.setdefault("freshness_status", _freshness_status(str(row.get("published_at") or ""), current_date))
        normalized.append(row)
    failures = payload.get("source_failures", [])
    normalized_failures = [dict(item) for item in failures if isinstance(item, Mapping)] if isinstance(failures, list) else []
    return True, normalized, [], normalized_failures


def _usable_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable: list[dict[str, Any]] = []
    for item in items:
        if item.get("trusted_read_only") is not True:
            continue
        if not item.get("title"):
            continue
        if not (item.get("entity_tags") or item.get("lane_tags")):
            continue
        usable.append(item)
    return usable


def _build_result(
    *,
    current_date: str,
    cache_path: str | Path,
    fetched_at: str,
    fetch_attempted: bool,
    cache_loaded: bool,
    cache_written: bool,
    headlines: list[dict[str, Any]],
    source_failures: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
) -> LiveNewsFetcherResult:
    usable = _usable_items(headlines)
    stale_count = sum(1 for item in usable if item.get("freshness_status") == "stale")
    safety = _safety_flags()
    if not safety.get("safety_check_blocked_execution"):
        blockers.append("safety_check_did_not_block_execution")
    if source_failures:
        warnings.append("one or more public news sources were unavailable")
    if not usable:
        warnings.append("no usable live news headlines available; this is a review note, not a trading blocker")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)
    status = STATUS_BLOCKED if unique_blockers else STATUS_READY if usable else STATUS_REVIEW_REQUIRED

    return LiveNewsFetcherResult(
        status=status,
        current_date=current_date,
        fetched_at=fetched_at,
        fetch_attempted=fetch_attempted,
        cache_path=str(cache_path),
        cache_loaded=cache_loaded,
        cache_written=cache_written,
        fetched_count=len(headlines),
        usable_count=len(usable),
        stale_count=stale_count,
        source_failures=source_failures,
        headlines=headlines,
        top_headlines=usable[:8],
        warnings=unique_warnings,
        blockers=unique_blockers,
        safety_flags=safety,
    )


def build_live_news_fetcher_result(
    *,
    current_date: str = "2026-06-20",
    cache_path: str | Path = DEFAULT_LIVE_NEWS_CACHE_PATH,
    fetch_news: bool = False,
    write_cache: bool = False,
    feeds: Iterable[Mapping[str, Any]] = DEFAULT_FEEDS,
    feed_fetcher: FeedFetcher | None = None,
    timeout_seconds: float = 6.0,
    fetched_at: str | None = None,
) -> LiveNewsFetcherResult:
    path = Path(cache_path)
    fetched_at_text = fetched_at or _now_iso()
    warnings: list[str] = []
    blockers: list[str] = []
    source_failures: list[dict[str, str]] = []
    headlines: list[dict[str, Any]] = []
    cache_loaded = False
    cache_written = False
    fetcher = feed_fetcher or _default_feed_fetcher

    if fetch_news:
        for feed in list(feeds):
            source = str(feed.get("source") or "public RSS")
            feed_url = str(feed.get("feed_url") or "")
            try:
                xml_text = fetcher(feed, timeout_seconds)
                parsed = _parse_feed_items(xml_text, feed, current_date=current_date)
                headlines.extend(parsed[:10])
            except Exception as exc:
                source_failures.append(
                    {
                        "source": source,
                        "feed_url": feed_url,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        if write_cache:
            interim = _build_result(
                current_date=current_date,
                cache_path=path,
                fetched_at=fetched_at_text,
                fetch_attempted=True,
                cache_loaded=False,
                cache_written=True,
                headlines=headlines,
                source_failures=source_failures,
                warnings=list(warnings),
                blockers=list(blockers),
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(_cache_payload(interim), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            cache_written = True
    else:
        cache_loaded, headlines, cache_warnings, cache_failures = _load_cache(path, current_date)
        warnings.extend(cache_warnings)
        source_failures.extend(cache_failures)
        if write_cache:
            warnings.append("--write-news-cache ignored because no live fetch was requested")

    return _build_result(
        current_date=current_date,
        cache_path=path,
        fetched_at=fetched_at_text,
        fetch_attempted=fetch_news,
        cache_loaded=cache_loaded,
        cache_written=cache_written,
        headlines=headlines,
        source_failures=source_failures,
        warnings=warnings,
        blockers=blockers,
    )


def format_live_news_fetcher(result: LiveNewsFetcherResult) -> str:
    lines = [
        "J.A.R.V.I.S. LIVE NEWS FETCHER",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"fetched at: {result.fetched_at}",
        f"fetch attempted: {result.fetch_attempted}",
        f"cache path: {result.cache_path}",
        f"cache loaded: {result.cache_loaded}",
        f"cache written: {result.cache_written}",
        f"fetched count: {result.fetched_count}",
        f"usable count: {result.usable_count}",
        f"stale count: {result.stale_count}",
        f"source failures: {len(result.source_failures)}",
        "",
        "TOP HEADLINES:",
    ]
    if result.top_headlines:
        for item in result.top_headlines:
            tags = ", ".join(list(item.get("entity_tags") or []) + list(item.get("lane_tags") or []))
            lines.append(
                f"- {item.get('title')} | source={item.get('source')} | freshness={item.get('freshness_status')} | tags={tags or 'none'} | url={item.get('url') or 'n/a'}"
            )
    else:
        lines.append("- none")

    lines.append("")
    lines.append("SOURCE FAILURES:")
    if result.source_failures:
        for failure in result.source_failures:
            lines.append(f"- {failure.get('source')}: {failure.get('error')}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SAFETY FLAGS:",
            f"- trusted read-only: {result.safety_flags.get('trusted_read_only')}",
            f"- public/free sources only: {result.safety_flags.get('public_free_sources_only')}",
            f"- credentials used: {result.safety_flags.get('credentials_used')}",
            f"- browser login: {result.safety_flags.get('browser_login')}",
            f"- recommendation mutation: {result.safety_flags.get('recommendation_mutation')}",
            f"- allocation mutation: {result.safety_flags.get('allocation_mutation')}",
            f"- approval ticket mutation: {result.safety_flags.get('approval_ticket_mutation')}",
            f"- buy request created: {result.safety_flags.get('buy_request_created')}",
            f"- sell request created: {result.safety_flags.get('sell_request_created')}",
            f"- broker connection: {result.safety_flags.get('broker_connection')}",
            f"- order created: {result.safety_flags.get('order_created')}",
            f"- trade executed: {result.safety_flags.get('trade_executed')}",
            f"- auto approval: {result.safety_flags.get('auto_approval')}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append("Safety: headlines are context only. Do not infer causality without direct evidence. No broker, credential, order, trade, approval, or recommendation mutation path is enabled.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch or inspect read-only public live news context.")
    parser.add_argument("--live-news-fetch", action="store_true")
    parser.add_argument("--live-news-status", action="store_true")
    parser.add_argument("--write-news-cache", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--news-cache-path", default=DEFAULT_LIVE_NEWS_CACHE_PATH)
    parser.add_argument("--timeout-seconds", type=float, default=6.0)
    args = parser.parse_args(argv)

    result = build_live_news_fetcher_result(
        current_date=args.current_date,
        cache_path=args.news_cache_path,
        fetch_news=bool(args.live_news_fetch),
        write_cache=bool(args.write_news_cache),
        timeout_seconds=args.timeout_seconds,
    )
    print(format_live_news_fetcher(result))
    return 0 if result.status != STATUS_BLOCKED else 1


__all__ = [
    "DEFAULT_FEEDS",
    "DEFAULT_LIVE_NEWS_CACHE_PATH",
    "SCHEMA_VERSION",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "LiveNewsFetcherResult",
    "build_live_news_fetcher_result",
    "format_live_news_fetcher",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
