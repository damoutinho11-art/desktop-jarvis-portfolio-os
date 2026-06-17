from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.allocation_strategy_audit import (
    AUDIT_REVIEW_REQUIRED,
    STATUS_REVIEW_REQUIRED,
    build_allocation_strategy_data_coverage_audit_result,
    format_allocation_strategy_data_coverage_audit,
)


def _evidence(provider: str, lane: str, quality: str, kind: str = "snapshot") -> SimpleNamespace:
    return SimpleNamespace(
        provider_id=provider,
        lane=lane,
        source_quality=quality,
        data_kind=kind,
        usable_for_research=True,
    )


def _upstream(evidence_items=()) -> SimpleNamespace:
    return SimpleNamespace(
        status="JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY_SAFE",
        source_confidence_score=70,
        source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
        free_stack_sufficient_for_weekly_investing=True,
        paid_api_required_now=False,
        broker_api_required_now=False,
        evidence_items=tuple(evidence_items),
        approval_ticket_mutation=False,
        blockers=(),
        warnings=(),
    )


class JarvisV510AllocationStrategyDataCoverageAuditTests(unittest.TestCase):
    def test_weekly_router_allowed_but_full_allocation_blocked_with_public_evidence_only(self) -> None:
        result = build_allocation_strategy_data_coverage_audit_result(
            current_date="2026-06-17",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.audit_status, AUDIT_REVIEW_REQUIRED)
        self.assertTrue(result.weekly_router_allowed)
        self.assertFalse(result.full_allocation_allowed)
        self.assertIn("manual_holdings_snapshot", result.missing_full_allocation_required_keys)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_missing_weekly_evidence_blocks_weekly_router_readiness(self) -> None:
        result = build_allocation_strategy_data_coverage_audit_result(
            current_date="2026-06-17",
            upstream_result=_upstream(evidence_items=()),
        )

        self.assertFalse(result.weekly_router_allowed)
        self.assertFalse(result.full_allocation_allowed)
        self.assertGreaterEqual(result.missing_weekly_router_required_count, 2)

    def test_manual_snapshot_improves_full_allocation_coverage_but_does_not_complete_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "manual_portfolio_snapshot.local.json"
            snapshot.write_text(
                '{"brokerless_manual_snapshot": true, "cash_eur": 250, "holdings": [{"symbol": "IS3Q.DE", "amount_eur": 100}], "cost_basis": {"IS3Q.DE": 100}}',
                encoding="utf-8",
            )

            result = build_allocation_strategy_data_coverage_audit_result(
                current_date="2026-06-17",
                manual_portfolio_snapshot_path=snapshot,
                upstream_result=_upstream(
                    evidence_items=(
                        _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                        _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                    )
                ),
            )

            covered_keys = {item.key for item in result.coverage_items if item.available}
            self.assertIn("manual_holdings_snapshot", covered_keys)
            self.assertIn("manual_cash_snapshot", covered_keys)
            self.assertIn("manual_cost_basis", covered_keys)
            self.assertFalse(result.full_allocation_allowed)
            self.assertIn("correlation_risk_model", result.missing_full_allocation_required_keys)

    def test_format_is_clear_about_current_strategy_not_full_allocator(self) -> None:
        result = build_allocation_strategy_data_coverage_audit_result(
            current_date="2026-06-17",
            upstream_result=_upstream(
                evidence_items=(
                    _evidence("coingecko_free_or_demo", "crypto", "PUBLIC_CRYPTO_SOURCE_READY"),
                    _evidence("ecb_fx_official", "fx", "OFFICIAL_FREE_SOURCE_READY"),
                )
            ),
        )
        output = format_allocation_strategy_data_coverage_audit(result)

        self.assertIn("ALLOCATION STRATEGY + DATA COVERAGE AUDIT", output)
        self.assertIn("v50 implements a weekly manual amount router, not a full portfolio allocator", output)
        self.assertIn("weekly router allowed: True", output)
        self.assertIn("full allocation allowed: False", output)
        self.assertIn("approval ticket mutation: False", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_allocation_strategy_audit(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = runtime_operator.main(["--allocation-strategy-audit", "--current-date", "2026-06-17"])

        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("J.A.R.V.I.S. ALLOCATION STRATEGY + DATA COVERAGE AUDIT", output)
        self.assertIn("full allocation allowed: False", output)
        self.assertIn("approval ticket mutation: False", output)

    def test_runtime_surface_reports_v51_and_audit_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertEqual(surface["active_runtime_stage"], "v51.0")
        self.assertEqual(
            surface["active_allocation_strategy_audit_module"],
            "jarvis.runtime.allocation_strategy_audit",
        )


if __name__ == "__main__":
    unittest.main()