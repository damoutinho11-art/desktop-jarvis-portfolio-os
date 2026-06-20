from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.live_news_fetcher import SCHEMA_VERSION


def _cache_payload() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "current_date": "2026-06-20",
        "fetched_at": "2026-06-20T10:00:00Z",
        "trusted_read_only": True,
        "items": [
            {
                "schema_version": SCHEMA_VERSION,
                "current_date": "2026-06-20",
                "source": "Fixture public RSS",
                "source_url": "https://example.test/rss",
                "feed_url": "https://example.test/rss",
                "title": "Bitcoin headline context for crypto market",
                "summary": "Possible context only.",
                "published_at": "Sat, 20 Jun 2026 08:00:00 GMT",
                "entity_tags": ["BTC", "crypto market"],
                "lane_tags": ["crypto"],
                "url": "https://example.test/btc",
                "freshness_status": "fresh",
                "trusted_read_only": True,
            }
        ],
        "source_failures": [],
        "warnings": [],
    }


class JarvisV137DashboardUiRedesignTests(unittest.TestCase):
    def test_dashboard_html_has_product_app_sections_and_safety_banner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_dashboard_contract_result(
                current_date="2026-06-20",
                manual_holdings_path=Path(tmp) / "missing_holdings.local.json",
                live_news_cache_path=Path(tmp) / "missing_news.local.json",
            )
            page = render_dashboard_html(result)

        expected_sections = [
            "Top Status / Readiness",
            "Today's Manual Plan",
            "Holdings Status",
            "Market Movement",
            "Live News / Headline Context",
            "Risk & Safety",
            "Blockers / Warnings",
            "How to Use Today",
            "Useful Commands",
        ]
        for section in expected_sections:
            self.assertIn(section, page)
        self.assertIn("Manual-only safety", page)
        self.assertIn("No broker connection, credentials, orders, trades, buy/sell requests, or auto-approval", page)
        self.assertIn("Start Jarvis.bat", page)

    def test_missing_holdings_and_news_are_friendly_setup_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_dashboard_contract_result(
                current_date="2026-06-20",
                manual_holdings_path=Path(tmp) / "missing_holdings.local.json",
                live_news_cache_path=Path(tmp) / "missing_news.local.json",
            )
            page = render_dashboard_html(result)

        self.assertTrue(result.dashboard_contract_ready)
        self.assertIn("Holdings not entered yet", page)
        self.assertIn("No local live news cache yet", page)
        self.assertIn("missing news is not a blocker", page)
        self.assertNotIn("broker_import", page)

    def test_cached_live_news_rows_show_source_freshness_and_possible_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "live_news_cache.local.json"
            cache_path.write_text(json.dumps(_cache_payload()), encoding="utf-8")
            result = build_dashboard_contract_result(
                current_date="2026-06-20",
                manual_holdings_path=Path(tmp) / "missing_holdings.local.json",
                live_news_cache_path=cache_path,
            )
            page = render_dashboard_html(result)

        self.assertIn("Bitcoin headline context for crypto market", page)
        self.assertIn("source=Fixture public RSS", page)
        self.assertIn("freshness=fresh", page)
        self.assertIn("Possible context only", page)
        self.assertNotIn("caused", page.lower())


if __name__ == "__main__":
    unittest.main()
