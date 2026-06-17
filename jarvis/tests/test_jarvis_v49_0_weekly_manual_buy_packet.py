from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import MODE_DAILY_CHECK_IN
from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.weekly_packet import (
    PACKET_REVIEW_REQUIRED,
    STATUS_REVIEW_REQUIRED,
    build_weekly_manual_buy_packet_result,
    format_weekly_manual_buy_packet,
)


def _evidence(provider: str, lane: str, quality: str, kind: str = "snapshot") -> SimpleNamespace:
    return SimpleNamespace(
        provider_id=provider,
        lane=lane,
        source_quality=quality,
        data_kind=kind,
        usable_for_research=True,
    )


def _upstream(*, approval_ticket_mutation: bool = True, evidence_items=()) -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY_SAFE",
        source_confidence_score=70,
        source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
        free_stack_sufficient_for_weekly_investing=True,
        paid_api_required_now=False,
        broker_api_required_now=False,
        evidence_item_count=len(tuple(evidence_items)),
        usable_evidence_count=len(tuple(evidence_items)),
        failed_evidence_count=0,
        crypto_candidate="hype",
        etf_symbol="IS3Q.DE",
        stock_symbol="MSFT",
        evidence_items=tuple(evidence_items),
        approval_ticket_mutation=approval_ticket_mutation,
        evidence_pack_mutation=False,
        local_cache_mutation=False,
        blockers=(),
        warnings=(),
    )


class JarvisV490WeeklyManualBuyPacketTests(unittest.TestCase):
    def test_weekly_packet_builds_manual_actions_without_execution(self) -> None:
        evidence_items = (
            _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
            _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
        )
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            upstream_result=_upstream(evidence_items=evidence_items),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.packet_status, PACKET_REVIEW_REQUIRED)
        self.assertEqual(result.crypto_action.selected, "hype")
        self.assertEqual(result.equity_action.selected, "IS3Q.DE")
        self.assertEqual(result.stock_review_action.selected, "MSFT")
        self.assertTrue(result.manual_budget_required)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.crypto_action.approved_for_purchase)
        self.assertFalse(result.crypto_action.trade_executed)
        self.assertTrue(result.no_trades_executed)

    def test_stock_review_does_not_reuse_crypto_or_fx_evidence(self) -> None:
        evidence_items = (
            _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
            _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
        )

        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            upstream_result=_upstream(evidence_items=evidence_items),
        )

        stock_evidence = "\n".join(result.stock_review_action.evidence_summary)
        self.assertIn("no refreshed stock-specific evidence", stock_evidence)
        self.assertNotIn("coingecko_free_or_demo", stock_evidence)
        self.assertNotIn("ecb_fx_official", stock_evidence)

    def test_stock_review_uses_stock_specific_evidence_when_available(self) -> None:
        evidence_items = (
            _evidence("sec_edgar_official", "us_stock_validation", "OFFICIAL_FREE_SOURCE_READY"),
            _evidence("fmp_free_optional", "stocks_etfs_fundamentals", "OPTIONAL_RESEARCH_API_SOURCE_READY"),
        )

        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            upstream_result=_upstream(evidence_items=evidence_items),
        )

        stock_evidence = "\n".join(result.stock_review_action.evidence_summary)
        self.assertIn("sec_edgar_official", stock_evidence)
        self.assertIn("fmp_free_optional", stock_evidence)
    def test_budget_can_be_displayed_and_routed_without_allocation_mutation(self) -> None:
        evidence_items = (
            _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
            _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
        )
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            weekly_budget_eur="100",
            upstream_result=_upstream(evidence_items=evidence_items),
        )

        self.assertEqual(result.weekly_budget_eur, 100.0)
        self.assertFalse(result.manual_budget_required)
        self.assertEqual(result.crypto_action.amount_eur, 40.0)
        self.assertEqual(result.equity_action.amount_eur, 60.0)
        self.assertEqual(result.stock_review_action.amount_eur, 0.0)
        self.assertFalse(result.allocation_mutation)

    def test_format_contains_user_facing_packet_and_safety(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )
        output = format_weekly_manual_buy_packet(result)

        self.assertIn("J.A.R.V.I.S. WEEKLY MANUAL BUY PACKET", output)
        self.assertIn("Crypto manual action", output)
        self.assertIn("ETF/fund manual action", output)
        self.assertIn("Individual stock review", output)
        self.assertIn("buy request created: False", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_weekly_mode_to_packet(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = runtime_operator.main(["--weekly-buy-prep", "--current-date", "2026-06-17"])

        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("J.A.R.V.I.S. WEEKLY MANUAL BUY PACKET", output)
        self.assertIn("buy request created: False", output)

    def test_runtime_facade_keeps_daily_backend_available(self) -> None:
        result = runtime_operator.build_current_operator_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_fetcher_result=SimpleNamespace(
                status="JARVIS_V44_0_FREE_RESEARCH_API_FETCHER_ADAPTERS_LOCAL_CACHE_READY_SAFE",
                cache_records=(),
                source_confidence_score=70,
                source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
                free_stack_sufficient_for_weekly_investing=True,
                paid_api_required_now=False,
                broker_api_required_now=False,
                crypto_candidate="hype",
                etf_symbol="IS3Q.DE",
                stock_symbol="MSFT",
                approval_ticket_mutation=False,
                local_cache_mutation=False,
                blockers=(),
                warnings=(),
                to_dict=lambda: {"status": "ready"},
            ),
        )

        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)


if __name__ == "__main__":
    unittest.main()