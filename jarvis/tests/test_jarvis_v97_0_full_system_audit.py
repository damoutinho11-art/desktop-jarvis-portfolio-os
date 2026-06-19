from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.full_system_audit import (
    STATUS_READY,
    build_full_system_audit_result,
    format_full_system_audit,
)


class JarvisV970FullSystemAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_full_system_audit_result(
            current_date="2026-06-18",
            speed_warning_seconds=120.0,
        )

    def test_audit_ready_with_expected_warning(self) -> None:
        self.assertEqual(self.result.status, STATUS_READY)
        self.assertEqual(self.result.audit_verdict, "READY_WITH_AUDIT_WARNINGS")
        self.assertEqual(self.result.blockers, [])
        self.assertTrue(any("news coverage" in warning for warning in self.result.warnings))

    def test_dashboard_chat_voice_backend_is_ready(self) -> None:
        self.assertTrue(self.result.dashboard_chat_voice_backend_ready)
        self.assertTrue(self.result.product_api_ready)
        self.assertTrue(self.result.data_readiness_ready)
        self.assertTrue(self.result.product_recommendations_allowed)

    def test_formula_invariants_pass(self) -> None:
        checks = self.result.formula_checks
        self.assertTrue(self.result.formula_invariants_ready)
        self.assertTrue(checks["allocation_total_matches_monthly"])
        self.assertTrue(checks["crypto_within_twenty_percent_cap"])
        self.assertTrue(checks["selected_crypto_matches_lane"])
        self.assertTrue(checks["selected_etf_fund_matches_lane"])
        self.assertTrue(checks["selected_stock_matches_lane"])
        self.assertTrue(checks["candidate_scores_present"])

    def test_data_and_universe_checks_pass(self) -> None:
        data = self.result.data_checks
        universe = self.result.universe_checks

        self.assertTrue(data["crypto_data_ready"])
        self.assertTrue(data["fx_data_ready"])
        self.assertTrue(data["etf_fund_data_ready"])
        self.assertTrue(data["stock_data_ready"])
        self.assertTrue(data["portfolio_data_ready"])
        self.assertTrue(data["monthly_expenses_data_ready"])
        self.assertEqual(data["missing_data"], [])

        self.assertTrue(universe["crypto_universe_ready"])
        self.assertTrue(universe["etf_universe_ready"])
        self.assertTrue(universe["stock_universe_ready"])
        self.assertEqual(universe["missing_universe"], [])

    def test_safety_checks_pass(self) -> None:
        safety = self.result.safety_checks

        self.assertTrue(self.result.safety_ready)
        self.assertTrue(safety["safety_check_blocked_execution"])
        self.assertTrue(safety["manual_approval_required"])
        self.assertTrue(safety["execution_forbidden"])
        self.assertFalse(safety["broker_connection"])
        self.assertFalse(safety["credentials_used"])
        self.assertFalse(safety["order_created"])
        self.assertFalse(safety["trade_executed"])

    def test_format_is_operator_readable(self) -> None:
        output = format_full_system_audit(self.result)

        self.assertIn("J.A.R.V.I.S. FULL SYSTEM AUDIT", output)
        self.assertIn("verdict: READY_WITH_AUDIT_WARNINGS", output)
        self.assertIn("FORMULA CHECKS:", output)
        self.assertIn("DATA CHECKS:", output)
        self.assertIn("UNIVERSE CHECKS:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_routes_v97_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v97.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "full_system_audit")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--full-system-audit", source)
        self.assertIn("_full_system_audit_main", source)


if __name__ == "__main__":
    unittest.main()
