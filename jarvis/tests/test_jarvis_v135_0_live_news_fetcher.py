from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.live_news_fetcher import (
    DEFAULT_LIVE_NEWS_CACHE_PATH,
    SCHEMA_VERSION,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_live_news_fetcher_result,
    format_live_news_fetcher,
)

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fixture Feed</title>
    <item>
      <title>Bitcoin and Ethereum climb as crypto market liquidity improves</title>
      <description>BTC and ETH headline context for the crypto lane.</description>
      <pubDate>Sat, 20 Jun 2026 08:00:00 GMT</pubDate>
      <link>https://example.test/crypto</link>
    </item>
    <item>
      <title>Microsoft Azure demand supports MSFT investor focus</title>
      <description>Microsoft public headline context only.</description>
      <pubDate>Sat, 20 Jun 2026 09:00:00 GMT</pubDate>
      <link>https://example.test/msft</link>
    </item>
    <item>
      <title>Central bank rates and inflation shape global equity market</title>
      <description>Macro and ETF fund context.</description>
      <pubDate>Fri, 12 Jun 2026 09:00:00 GMT</pubDate>
      <link>https://example.test/macro</link>
    </item>
  </channel>
</rss>
"""


def _fixture_fetcher(feed, timeout_seconds):
    return RSS_FIXTURE


def _failing_fetcher(feed, timeout_seconds):
    raise OSError("network unavailable in test")


class JarvisV135LiveNewsFetcherTests(unittest.TestCase):
    def test_missing_cache_status_is_review_required_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_news_cache.local.json"

            result = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.fetch_attempted)
            self.assertFalse(result.cache_loaded)
            self.assertFalse(result.cache_written)
            self.assertEqual(result.usable_count, 0)
            self.assertEqual(result.blockers, [])
            self.assertFalse(result.safety_flags["credentials_used"])
            self.assertFalse(result.safety_flags["order_created"])
            self.assertFalse(result.safety_flags["trade_executed"])
            self.assertIn("cache missing", " ".join(result.warnings))

    def test_fetch_fixture_parses_required_entities_and_safety_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_news_cache.local.json"

            result = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=True,
                feeds=[
                    {
                        "source": "Fixture public RSS",
                        "feed_url": "https://example.test/rss",
                        "default_entity_tags": ["crypto market"],
                        "default_lane_tags": ["crypto"],
                    }
                ],
                feed_fetcher=_fixture_fetcher,
                fetched_at="2026-06-20T10:00:00Z",
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.fetch_attempted)
            self.assertEqual(result.fetched_count, 3)
            self.assertEqual(result.usable_count, 3)
            self.assertEqual(result.stale_count, 1)
            self.assertEqual(result.source_failures, [])
            titles = " ".join(item["title"] for item in result.headlines)
            self.assertIn("Bitcoin", titles)
            self.assertIn("Microsoft", titles)
            tags = {tag for item in result.headlines for tag in item["entity_tags"]}
            self.assertTrue({"BTC", "ETH", "crypto market", "MSFT", "macro", "ETF/fund", "global equity market"} & tags)
            self.assertTrue(all(item["trusted_read_only"] for item in result.headlines))
            self.assertFalse(result.safety_flags["recommendation_mutation"])
            self.assertFalse(result.safety_flags["approval_ticket_mutation"])
            self.assertFalse(result.safety_flags["broker_connection"])

    def test_write_cache_only_when_explicit_flag_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_news_cache.local.json"

            no_write = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=True,
                feeds=[{"source": "Fixture", "feed_url": "https://example.test/rss"}],
                feed_fetcher=_fixture_fetcher,
            )
            self.assertFalse(no_write.cache_written)
            self.assertFalse(path.exists())

            written = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=True,
                write_cache=True,
                feeds=[{"source": "Fixture", "feed_url": "https://example.test/rss"}],
                feed_fetcher=_fixture_fetcher,
                fetched_at="2026-06-20T10:00:00Z",
            )
            self.assertTrue(written.cache_written)
            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
            self.assertTrue(payload["trusted_read_only"])
            self.assertEqual(len(payload["items"]), 3)

            status = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=False,
            )
            self.assertEqual(status.status, STATUS_READY)
            self.assertTrue(status.cache_loaded)
            self.assertEqual(status.usable_count, 3)

    def test_source_failure_is_review_required_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_news_cache.local.json"

            result = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=True,
                feeds=[{"source": "Broken public RSS", "feed_url": "https://example.test/rss"}],
                feed_fetcher=_failing_fetcher,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.fetched_count, 0)
            self.assertEqual(result.usable_count, 0)
            self.assertEqual(len(result.source_failures), 1)
            self.assertEqual(result.blockers, [])
            self.assertIn("unavailable", result.source_failures[0]["error"])

    def test_format_and_operator_route_are_user_facing_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_news_cache.local.json"
            result = build_live_news_fetcher_result(
                current_date="2026-06-20",
                cache_path=path,
                fetch_news=True,
                feeds=[{"source": "Fixture", "feed_url": "https://example.test/rss"}],
                feed_fetcher=_fixture_fetcher,
            )
            text = format_live_news_fetcher(result)
            self.assertIn("J.A.R.V.I.S. LIVE NEWS FETCHER", text)
            self.assertIn("fetched count: 3", text)
            self.assertIn("usable count: 3", text)
            self.assertIn("TOP HEADLINES", text)
            self.assertIn("credentials used: False", text)
            self.assertIn("trade executed: False", text)
            self.assertIn("Do not infer causality", text)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--live-news-status", "--current-date", "2026-06-20", "--news-cache-path", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("J.A.R.V.I.S. LIVE NEWS FETCHER", output.getvalue())

    def test_runtime_surface_and_gitignore_track_live_news_cache(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()
        self.assertEqual(surface["active_live_news_fetcher_module"], "jarvis.runtime.live_news_fetcher")
        self.assertEqual(DEFAULT_LIVE_NEWS_CACHE_PATH, "jarvis/local/live_news_cache.local.json")
        gitignore = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("jarvis/local/live_news_cache.local.json", gitignore)


if __name__ == "__main__":
    unittest.main()
