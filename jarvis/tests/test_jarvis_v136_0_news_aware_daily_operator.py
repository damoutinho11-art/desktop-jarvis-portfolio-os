from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime.assistant_news_context import build_assistant_news_context_result, format_assistant_news_context
from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.daily_operator import build_daily_operator_result, format_daily_operator
from jarvis.runtime.live_news_fetcher import SCHEMA_VERSION
from jarvis.runtime.product_api import build_product_api_result, format_product_api


@dataclass
class _NewsResult:
    status: str
    fetch_attempted: bool
    usable_count: int
    source_failures: list
    warnings: list
    blockers: list
    top_headlines: list
    cache_loaded: bool = False
    cache_written: bool = False

    def to_dict(self):
        return asdict(self)


def _ready_news() -> _NewsResult:
    return _NewsResult(
        status="JARVIS_V135_0_LIVE_NEWS_FETCHER_READY_SAFE",
        fetch_attempted=True,
        usable_count=2,
        source_failures=[],
        warnings=[],
        blockers=[],
        top_headlines=[
            {
                "title": "Bitcoin headline context",
                "source": "Fixture public RSS",
                "freshness_status": "fresh",
                "url": "https://example.test/btc",
                "entity_tags": ["BTC"],
                "lane_tags": ["crypto"],
                "trusted_read_only": True,
            }
        ],
    )


def _review_news() -> _NewsResult:
    return _NewsResult(
        status="JARVIS_V135_0_LIVE_NEWS_FETCHER_REVIEW_REQUIRED_SAFE",
        fetch_attempted=True,
        usable_count=0,
        source_failures=[{"source": "Fixture", "error": "network unavailable"}],
        warnings=["no usable live news headlines available; this is a review note, not a trading blocker"],
        blockers=[],
        top_headlines=[],
    )


def _daily_common_patches(news_result: _NewsResult):
    dashboard_payload = {
        "status": "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE",
        "sections": {
            "manual_holdings": {
                "status": "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
                "holdings_ready": False,
                "file_exists": False,
            }
        },
    }
    final_gate = SimpleNamespace(
        final_acceptance_ready=True,
        status="JARVIS_V128_0_FINAL_PRODUCT_ACCEPTANCE_GATE_READY_SAFE",
        blockers=[],
        warnings=[],
    )
    product = SimpleNamespace(status="JARVIS_PRODUCT_MODE_READY_SAFE", blockers=[], warnings=[])
    return (
        patch("jarvis.runtime.daily_operator._build_dashboard", return_value=(False, "outputs/dashboard_latest.html", dashboard_payload)),
        patch("jarvis.runtime.daily_operator.build_final_product_acceptance_gate_result", return_value=final_gate),
        patch("jarvis.runtime.daily_operator.build_product_mode_result", return_value=product),
        patch("jarvis.runtime.daily_operator.build_live_news_fetcher_result", return_value=news_result),
        patch(
            "jarvis.runtime.daily_operator.build_safety_check_console_output",
            return_value="BLOCKED: dry run. No execution action was taken.",
        ),
    )


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


class JarvisV136NewsAwareDailyOperatorTests(unittest.TestCase):
    def test_daily_operator_skips_news_by_default(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _daily_common_patches(_ready_news()):
                stack.enter_context(item)
            result = build_daily_operator_result(
                current_date="2026-06-20",
                refresh_quotes=False,
                write_dashboard=False,
            )

        self.assertTrue(result.daily_operator_ready)
        self.assertFalse(result.proof["news_attempted"])
        self.assertFalse(result.proof["news_ready"])
        self.assertEqual(result.proof["news_headline_count"], 0)
        self.assertEqual(result.proof["news_source_failures"], 0)
        self.assertIn("live news skipped", " ".join(result.warnings))

    def test_daily_operator_include_news_adds_proof(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _daily_common_patches(_ready_news()):
                stack.enter_context(item)
            result = build_daily_operator_result(
                current_date="2026-06-20",
                refresh_quotes=False,
                write_dashboard=False,
                include_news=True,
            )
        text = format_daily_operator(result)

        self.assertTrue(result.daily_operator_ready)
        self.assertTrue(result.proof["news_attempted"])
        self.assertTrue(result.proof["news_ready"])
        self.assertEqual(result.proof["news_headline_count"], 2)
        self.assertIn("news attempted: True", text)
        self.assertIn("headline count: 2", text)

    def test_news_failure_is_warning_not_blocker_unless_required(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _daily_common_patches(_review_news()):
                stack.enter_context(item)
            result = build_daily_operator_result(
                current_date="2026-06-20",
                refresh_quotes=False,
                write_dashboard=False,
                include_news=True,
            )

        self.assertTrue(result.daily_operator_ready)
        self.assertEqual(result.blockers, [])
        self.assertFalse(result.proof["news_ready"])
        self.assertEqual(result.proof["news_source_failures"], 1)
        self.assertIn("live news not ready", " ".join(result.warnings))

        with contextlib.ExitStack() as stack:
            for item in _daily_common_patches(_review_news()):
                stack.enter_context(item)
            required = build_daily_operator_result(
                current_date="2026-06-20",
                refresh_quotes=False,
                write_dashboard=False,
                include_news=True,
                require_news=True,
            )

        self.assertFalse(required.daily_operator_ready)
        self.assertIn("required_live_news_not_ready", required.blockers)

    def test_product_api_exposes_live_news_cache_context_with_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "live_news_cache.local.json"
            cache_path.write_text(json.dumps(_cache_payload()), encoding="utf-8")

            class _Instrument:
                def to_dict(self):
                    return {"warnings": [], "selections": [], "lane_totals": {}, "candidate_scores": []}

            data_readiness = SimpleNamespace(
                to_dict=lambda: {
                    "product_recommendations_allowed": True,
                    "data_readiness_ready": True,
                    "blockers": [],
                    "warnings": [],
                },
            )
            news_coverage = SimpleNamespace(
                to_dict=lambda: {
                    "news_coverage_ready": True,
                    "live_news_fetch_enabled": False,
                    "covered_categories": ["crypto", "macro"],
                    "blockers": [],
                    "warnings": [],
                },
            )
            product = SimpleNamespace(status="READY_SAFE", product_verdict="ready", blockers=[], warnings=[])
            with (
                patch("jarvis.runtime.product_api.build_product_mode_result", return_value=product),
                patch("jarvis.runtime.product_api.build_data_readiness_status_result", return_value=data_readiness),
                patch("jarvis.runtime.product_api.build_news_coverage_readiness_result", return_value=news_coverage),
                patch("jarvis.runtime.product_api.build_fast_product_instrument_summary", return_value=_Instrument()),
                patch(
                    "jarvis.runtime.product_api.build_safety_check_console_output",
                    return_value="BLOCKED: dry run. No execution action was taken.",
                ),
            ):
                result = build_product_api_result(
                    current_date="2026-06-20",
                    live_news_cache_path=cache_path,
                    manual_holdings_path=Path(tmp) / "missing_holdings.local.json",
                )

        self.assertTrue(result.api_ready)
        self.assertEqual(result.live_news_context["usable_count"], 1)
        text = format_product_api(result)
        self.assertIn("LIVE NEWS CONTEXT", text)
        self.assertIn("source=Fixture public RSS", text)
        self.assertIn("freshness=fresh", text)
        self.assertNotIn("caused", text.lower())

    def test_assistant_news_context_uses_possible_context_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "live_news_cache.local.json"
            cache_path.write_text(json.dumps(_cache_payload()), encoding="utf-8")

            result = build_assistant_news_context_result(
                current_date="2026-06-20",
                live_news_cache_path=cache_path,
            )
            text = format_assistant_news_context(result)

        self.assertTrue(result.local_cached_news_available)
        self.assertEqual(result.cached_headline_count, 1)
        self.assertIn("Headline context", text)
        self.assertIn("possible context", text)
        self.assertIn("source=Fixture public RSS", text)
        self.assertIn("freshness=fresh", text)
        self.assertIn("will not say headlines caused", text)

    def test_assistant_router_news_context_uses_live_cache_language(self) -> None:
        fake_context = SimpleNamespace(
            current_date="2026-06-20",
            source="live_news_cache + news_coverage_readiness",
            freshness="local_cache",
            confidence="medium_for_source_labels_low_for_causality",
            live_fetch_enabled=False,
            warnings=[],
            blockers=[],
        )
        with (
            patch("jarvis.runtime.assistant_router.build_assistant_news_context_result", return_value=fake_context),
            patch("jarvis.runtime.assistant_router.format_assistant_news_context", return_value="Headline context: possible context only. source=Fixture; freshness=fresh."),
        ):
            result = build_assistant_router_result(query="What news matters today?", current_date="2026-06-20")

        self.assertEqual(result.intent, "news_context")
        self.assertIn("possible context", result.reply)
        self.assertIn("freshness=fresh", result.reply)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_daily_operator_cli_accepts_news_flags_with_mocked_news(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in _daily_common_patches(_ready_news()):
                stack.enter_context(item)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = __import__("jarvis.runtime.daily_operator", fromlist=["main"]).main(
                    [
                        "--daily-operator",
                        "--current-date",
                        "2026-06-20",
                        "--skip-refresh",
                        "--no-write-dashboard",
                        "--include-news",
                    ]
                )
        self.assertEqual(code, 0)
        self.assertIn("news attempted: True", output.getvalue())


if __name__ == "__main__":
    unittest.main()
