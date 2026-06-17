from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.weekly_packet import (
    PACKET_READY,
    PACKET_REVIEW_REQUIRED,
    STATUS_READY,
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
        evidence_pack_mutation=True,
        local_cache_mutation=True,
        blockers=(),
        warnings=(),
    )


class JarvisV500ManualWeeklyAmountRouterTests(unittest.TestCase):
    def test_budget_routes_to_crypto_and_etf_without_execution(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            weekly_budget_eur="100",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.packet_status, PACKET_READY)
        self.assertEqual(result.amount_router.router_status, "ROUTED_FOR_MANUAL_REVIEW")
        self.assertEqual(result.crypto_action.amount_eur, 40.0)
        self.assertEqual(result.equity_action.amount_eur, 60.0)
        self.assertEqual(result.stock_review_action.amount_eur, 0.0)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_crypto_is_capped_when_crypto_raw_weight_exceeds_risk_cap(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            weekly_budget_eur="100",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )

        self.assertEqual(result.amount_router.crypto_route.proposed_amount_eur, 40.0)
        self.assertTrue(result.amount_router.crypto_route.risk_cap_applied)

    def test_without_budget_packet_requires_manual_budget(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.packet_status, PACKET_REVIEW_REQUIRED)
        self.assertTrue(result.manual_budget_required)
        self.assertEqual(result.amount_router.router_status, "MANUAL_BUDGET_REQUIRED")
        self.assertIsNone(result.crypto_action.amount_eur)

    def test_budget_without_fresh_evidence_does_not_route(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            weekly_budget_eur="100",
            upstream_result=_upstream(evidence_items=()),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.amount_router.router_status, "NO_USABLE_EVIDENCE_FOR_ROUTING")
        self.assertEqual(result.amount_router.routed_budget_eur, 0.0)
        self.assertEqual(result.amount_router.unrouted_budget_eur, 100.0)
        self.assertEqual(result.crypto_action.amount_eur, 0.0)
        self.assertEqual(result.equity_action.amount_eur, 0.0)

    def test_format_shows_manual_amount_router(self) -> None:
        result = build_weekly_manual_buy_packet_result(
            current_date="2026-06-17",
            weekly_budget_eur="100",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )
        output = format_weekly_manual_buy_packet(result)

        self.assertIn("Manual amount router:", output)
        self.assertIn("router status: ROUTED_FOR_MANUAL_REVIEW", output)
        self.assertIn("crypto: 40.0 EUR", output)
        self.assertIn("ETF/fund: 60.0 EUR", output)
        self.assertIn("buy request created: False", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_weekly_budget_to_amount_packet(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = runtime_operator.main(
                ["--weekly-buy-prep", "--current-date", "2026-06-17", "--weekly-budget-eur", "100"]
            )

        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("J.A.R.V.I.S. WEEKLY MANUAL BUY PACKET", output)
        self.assertIn("Manual amount router:", output)
        self.assertIn("weekly budget EUR: 100.0", output)
        self.assertIn("no broker connection", output)

    def test_runtime_surface_reports_v50(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v50.0")
        self.assertEqual(surface["active_weekly_packet_module"], "jarvis.runtime.weekly_packet")


if __name__ == "__main__":
    unittest.main()