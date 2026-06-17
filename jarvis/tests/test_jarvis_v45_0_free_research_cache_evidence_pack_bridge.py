from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import (
    MODE_DAILY_CHECK_IN,
    MODE_WEEKLY_BUY_PREP,
)
from jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_free_research_cache_evidence_pack_bridge_result,
    format_free_research_cache_evidence_pack_bridge,
)


def _record(status: str = "FETCH_READY") -> SimpleNamespace:
    return SimpleNamespace(
        provider_id="coingecko_free_or_demo",
        lane="crypto",
        data_kind="simple_price_market_snapshot",
        status=status,
        fetched_at="2026-06-17T00:00:00+00:00",
        current_date="2026-06-17",
        request_url="https://api.coingecko.com/api/v3/simple/price",
        data_summary={"payload_type": "dict"},
        error=None if status == "FETCH_READY" else "failed",
        to_dict=lambda: {
            "provider_id": "coingecko_free_or_demo",
            "lane": "crypto",
            "data_kind": "simple_price_market_snapshot",
            "status": status,
            "fetched_at": "2026-06-17T00:00:00+00:00",
            "current_date": "2026-06-17",
            "request_url": "https://api.coingecko.com/api/v3/simple/price",
            "data_summary": {"payload_type": "dict"},
            "error": None if status == "FETCH_READY" else "failed",
        },
    )


def _upstream(records=(), *, local_cache_mutation: bool = False, approval_ticket_mutation: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V44_0_FREE_RESEARCH_API_FETCHER_ADAPTERS_LOCAL_CACHE_READY_SAFE",
        cache_records=tuple(records),
        source_confidence_score=70,
        source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
        free_stack_sufficient_for_weekly_investing=True,
        paid_api_required_now=False,
        broker_api_required_now=False,
        crypto_candidate="hype",
        etf_symbol="IS3Q.DE",
        stock_symbol="MSFT",
        approval_ticket_mutation=approval_ticket_mutation,
        local_cache_mutation=local_cache_mutation,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": "ready"},
    )


class JarvisV450FreeResearchCacheEvidencePackBridgeTests(unittest.TestCase):
    def test_daily_default_without_cache_is_ready_and_non_mutating(self) -> None:
        result = build_free_research_cache_evidence_pack_bridge_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_fetcher_result=_upstream(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.evidence_pack_written)
        self.assertFalse(result.evidence_pack_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)

    def test_write_evidence_pack_from_upstream_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_cache_evidence_pack_bridge_result(
                current_date="2026-06-17",
                operating_mode=MODE_DAILY_CHECK_IN,
                root=Path(tmp),
                write_evidence_pack=True,
                upstream_fetcher_result=_upstream(records=(_record(),)),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.evidence_pack_written)
            self.assertTrue(result.evidence_pack_mutation)
            self.assertEqual(result.evidence_item_count, 1)
            self.assertEqual(result.usable_evidence_count, 1)
            payload = json.loads(Path(result.evidence_pack_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["evidence_pack_status"], "FREE_RESEARCH_EVIDENCE_PACK_WRITTEN")
            self.assertFalse(payload["safety"]["trade_executed"])

    def test_read_existing_cache_when_upstream_has_no_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / "jarvis" / "local" / "free_research_api_cache.local.json"
            cache.parent.mkdir(parents=True)
            cache.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "provider_id": "ecb_fx_official",
                                "lane": "fx",
                                "data_kind": "eur_usd_reference_latest",
                                "status": "FETCH_READY",
                                "fetched_at": "2026-06-17T00:00:00+00:00",
                                "current_date": "2026-06-17",
                                "request_url": "https://data-api.ecb.europa.eu",
                                "data_summary": {"payload_type": "dict"},
                                "error": None,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = build_free_research_cache_evidence_pack_bridge_result(
                current_date="2026-06-17",
                root=root,
                upstream_fetcher_result=_upstream(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.cache_available)
            self.assertEqual(result.evidence_item_count, 1)
            self.assertEqual(result.evidence_items[0].source_quality, "OFFICIAL_FREE_SOURCE_READY")

    def test_failed_record_reviews(self) -> None:
        result = build_free_research_cache_evidence_pack_bridge_result(
            current_date="2026-06-17",
            write_evidence_pack=True,
            upstream_fetcher_result=_upstream(records=(_record(status="FETCH_FAILED"),)),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.failed_evidence_count, 1)
        self.assertTrue(any("evidence item" in warning for warning in result.warnings))

    def test_write_requested_without_records_reviews(self) -> None:
        result = build_free_research_cache_evidence_pack_bridge_result(
            current_date="2026-06-17",
            write_evidence_pack=True,
            upstream_fetcher_result=_upstream(),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertIn("no free research cache records are available for evidence pack.", result.warnings)

    def test_evidence_path_outside_outputs_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_cache_evidence_pack_bridge_result(
                current_date="2026-06-17",
                root=Path(tmp),
                evidence_pack_path="jarvis/local/bad.json",
                upstream_fetcher_result=_upstream(records=(_record(),)),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("evidence pack path must remain under outputs/.", result.blockers)

    def test_cache_path_outside_local_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_free_research_cache_evidence_pack_bridge_result(
                current_date="2026-06-17",
                root=Path(tmp),
                cache_path="outputs/bad_cache.json",
                upstream_fetcher_result=_upstream(records=(_record(),)),
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("free research cache path must remain under jarvis/local/.", result.blockers)

    def test_weekly_mode_preserves_approval_ticket_mutation_from_upstream_policy(self) -> None:
        result = build_free_research_cache_evidence_pack_bridge_result(
            current_date="2026-06-17",
            operating_mode=MODE_WEEKLY_BUY_PREP,
            upstream_fetcher_result=_upstream(
                records=(_record(),),
                approval_ticket_mutation=True,
            ),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_console_mentions_evidence_policy_and_safety(self) -> None:
        result = build_free_research_cache_evidence_pack_bridge_result(
            current_date="2026-06-17",
            upstream_fetcher_result=_upstream(records=(_record(),)),
        )
        output = format_free_research_cache_evidence_pack_bridge(result)

        self.assertIn("Free Research Cache Evidence Pack Bridge", output)
        self.assertIn("evidence-pack writes are explicit", output)
        self.assertIn("does not approve buys", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()