from __future__ import annotations

import unittest
from types import SimpleNamespace

import jarvis_operator
from jarvis.jarvis_v43_0_free_research_api_router_weekly_policy import MODE_DAILY_CHECK_IN
from jarvis.runtime import operator as runtime_operator


def _upstream_fetcher() -> SimpleNamespace:
    return SimpleNamespace(
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
    )


class JarvisV480StableRuntimeFacadeTests(unittest.TestCase):
    def test_root_operator_points_to_stable_runtime_facade(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.runtime.operator")

    def test_facade_declares_current_versioned_backend(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["stable_runtime_facade"], "jarvis.runtime.operator")
        self.assertEqual(
            surface["active_runtime_module"],
            "jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge",
        )
        self.assertEqual(surface["active_runtime_stage"], "v45.0")

    def test_facade_builds_same_daily_non_mutating_result(self) -> None:
        result = runtime_operator.build_current_operator_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_fetcher_result=_upstream_fetcher(),
        )

        self.assertEqual(result.status, runtime_operator.STATUS_READY)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.evidence_pack_mutation)
        self.assertFalse(result.local_cache_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_facade_format_preserves_current_operator_title_and_safety(self) -> None:
        result = runtime_operator.build_current_operator_result(
            current_date="2026-06-17",
            operating_mode=MODE_DAILY_CHECK_IN,
            upstream_fetcher_result=_upstream_fetcher(),
        )
        output = runtime_operator.format_current_operator_result(result)

        self.assertIn("J.A.R.V.I.S. Free Research Cache Evidence Pack Bridge", output)
        self.assertIn("approval ticket mutation: False", output)
        self.assertIn("buy request created: False", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()