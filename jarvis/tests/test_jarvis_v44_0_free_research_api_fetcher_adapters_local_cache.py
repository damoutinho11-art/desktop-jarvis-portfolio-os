from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.error import URLError

from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import (
    MODE_DAILY_CHECK_IN,
    MODE_WEEKLY_BUY_PREP,
)
from jarvis.jarvis_v44_0_free_research_api_fetcher_adapters_local_cache import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_free_research_api_fetcher_local_cache_result,
    build_free_research_fetch_specs,
    fetch_records_for_specs,
    format_free_research_api_fetcher_local_cache,
)


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _opener_success(request, timeout=20):  # noqa: ANN001
    return _FakeResponse({"ok": True, "url": request.full_url})


def _opener_fail(request, timeout=20):  # noqa: ANN001
    raise URLError("network unavailable")


def _weekly_policy_ready(*, approval_ticket_mutation: bool = False, mode: str = MODE_DAILY_CHECK_IN) -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V43_0_FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_READY_SAFE",
        source_confidence_score=70,
        source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
        free_stack_sufficient_for_weekly_investing=True,
        paid_api_required_now=False,
        broker_api_required_now=False,
        daily_check_in_only=mode == MODE_DAILY_CHECK_IN,
        weekly_buy_preparation_allowed=mode == MODE_WEEKLY_BUY_PREP,
        manual_buy_action_today=mode == MODE_WEEKLY_BUY_PREP,
        crypto_candidate="hype",
        etf_symbol="IS3Q.DE",
        stock_symbol="MSFT",
        approval_ticket_mutation=approval_ticket_mutation,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": "ready"},
    )


class JarvisV440FreeResearchApiFetcherLocalCacheTests(unittest.TestCase):
    def test_daily_no_refresh_is_read_only_and_cache_not_written(self) -> None:
        result = build_free_research_api_fetcher_local_cache_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            refresh_free_research_cache=False,
            upstream_weekly_policy_result=_weekly_policy_ready(approval_ticket_mutation=False),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.cache_written)
        self.assertFalse(result.local_cache_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)

    def test_weekly_no_refresh_keeps_weekly_ticket_policy_but_no_cache_write(self) -> None:
        result = build_free_research_api_fetcher_local_cache_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            refresh_free_research_cache=False,
            upstream_weekly_policy_result=_weekly_policy_ready(
                approval_ticket_mutation=True,
                mode=MODE_WEEKLY_BUY_PREP,
            ),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.cache_written)
        self.assertFalse(result.local_cache_mutation)
        self.assertTrue(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_refresh_cache_writes_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_api_fetcher_local_cache_result(
                current_date="2026-06-17",
                operating_mode=MODE_DAILY_CHECK_IN,
                refresh_free_research_cache=True,
                root=Path(tmp),
                opener=_opener_success,
                upstream_weekly_policy_result=_weekly_policy_ready(approval_ticket_mutation=False),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.cache_written)
            self.assertTrue(result.local_cache_mutation)
            self.assertGreaterEqual(result.cache_record_count, 2)
            self.assertEqual(result.provider_failure_count, 0)
            cache = Path(result.cache_path)
            self.assertTrue(cache.exists())
            payload = json.loads(cache.read_text(encoding="utf-8"))
            self.assertEqual(payload["cache_status"], "FREE_RESEARCH_API_CACHE_WRITTEN")
            self.assertFalse(payload["safety"]["trade_executed"])

    def test_refresh_failure_writes_warning_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_api_fetcher_local_cache_result(
                current_date="2026-06-17",
                operating_mode=MODE_DAILY_CHECK_IN,
                refresh_free_research_cache=True,
                root=Path(tmp),
                opener=_opener_fail,
                upstream_weekly_policy_result=_weekly_policy_ready(approval_ticket_mutation=False),
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.cache_written)
            self.assertGreaterEqual(result.provider_failure_count, 2)
            self.assertTrue(any("free research provider fetch" in warning for warning in result.warnings))

    def test_cache_path_outside_jarvis_local_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_api_fetcher_local_cache_result(
                current_date="2026-06-17",
                root=Path(tmp),
                cache_path="outputs/bad_cache.json",
                upstream_weekly_policy_result=_weekly_policy_ready(),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("free research cache path must remain under jarvis/local/.", result.blockers)

    def test_optional_fmp_spec_requires_key_and_flag(self) -> None:
        without_key = build_free_research_fetch_specs(env={}, include_fmp=True)
        self.assertFalse(any(spec.provider_id == "fmp_free_optional" for spec in without_key))

        with_key = build_free_research_fetch_specs(
            env={"JARVIS_FMP_API_KEY": "key"},
            include_fmp=True,
        )
        self.assertTrue(any(spec.provider_id == "fmp_free_optional" for spec in with_key))

    def test_sec_spec_is_explicit_optional(self) -> None:
        specs = build_free_research_fetch_specs(env={}, include_sec=True)
        sec_specs = [spec for spec in specs if spec.provider_id == "sec_edgar_official"]

        self.assertEqual(len(sec_specs), 1)
        self.assertFalse(sec_specs[0].requires_api_key)
        self.assertIn("User-Agent", sec_specs[0].headers)

    def test_fetch_records_for_specs_summarizes_success(self) -> None:
        specs = build_free_research_fetch_specs(env={}, coin_ids=("bitcoin",))
        records = fetch_records_for_specs(specs[:1], current_date="2026-06-17", opener=_opener_success)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, "FETCH_READY")
        self.assertEqual(records[0].data_summary["payload_type"], "dict")

    def test_console_mentions_cache_and_safety(self) -> None:
        result = build_free_research_api_fetcher_local_cache_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            refresh_free_research_cache=False,
            upstream_weekly_policy_result=_weekly_policy_ready(approval_ticket_mutation=False),
        )
        output = format_free_research_api_fetcher_local_cache(result)

        self.assertIn("Free Research API Fetcher Adapters + Local Cache", output)
        self.assertIn("cache refresh is explicit", output)
        self.assertIn("jarvis/local", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()