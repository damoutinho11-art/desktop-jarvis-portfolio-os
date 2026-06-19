from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.product_api import STATUS_READY, build_product_api_result, format_product_api


class JarvisV960ProductApiLayerTests(unittest.TestCase):
    def test_product_api_is_ready_for_dashboard_chat_voice(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.api_ready)
        self.assertTrue(result.dashboard_ready)
        self.assertTrue(result.chat_ready)
        self.assertTrue(result.voice_ready)
        self.assertTrue(result.product_recommendations_allowed)
        self.assertEqual(result.blockers, [])

    def test_api_payload_contains_week_plan_and_selected_instruments(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")
        symbols = [item["symbol"] for item in result.week_plan["selected_instruments"]]

        self.assertAlmostEqual(result.week_plan["monthly_contribution_eur"], 500.0)
        self.assertAlmostEqual(result.week_plan["crypto_eur"], 100.0)
        self.assertAlmostEqual(result.week_plan["etf_fund_eur"], 275.0)
        self.assertAlmostEqual(result.week_plan["individual_stock_eur"], 50.0)
        self.assertIn("BTC", symbols)
        self.assertIn("ETH", symbols)
        self.assertIn("GLOBAL_CORE_ETF", symbols)
        self.assertIn("IS3Q.DE", symbols)
        self.assertIn("MSFT", symbols)

    def test_api_payload_contains_data_readiness_and_candidate_scores(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")

        self.assertTrue(result.data_readiness["data_readiness_ready"])
        self.assertTrue(result.data_readiness["product_recommendations_allowed"])
        self.assertGreaterEqual(result.data_readiness["crypto_candidate_count"], 5)
        self.assertGreaterEqual(result.data_readiness["etf_candidate_count"], 3)
        self.assertGreaterEqual(result.data_readiness["stock_candidate_count"], 15)
        self.assertGreater(len(result.candidate_scores), 0)

    def test_api_safety_is_manual_only(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")
        safety = result.safety_status

        self.assertTrue(safety["safety_check_blocked_execution"])
        self.assertTrue(safety["manual_approval_required"])
        self.assertTrue(safety["execution_forbidden"])
        self.assertFalse(safety["broker_connection"])
        self.assertFalse(safety["credentials_used"])
        self.assertFalse(safety["order_created"])
        self.assertFalse(safety["trade_executed"])

    def test_format_is_cli_and_ui_friendly(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")
        output = format_product_api(result)

        self.assertIn("J.A.R.V.I.S. PRODUCT API", output)
        self.assertIn("dashboard ready: True", output)
        self.assertIn("chat ready: True", output)
        self.assertIn("voice ready: True", output)
        self.assertIn("SELECTED INSTRUMENTS:", output)
        self.assertIn("BLOCKERS:", output)

    def test_operator_routes_v96_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v96.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "product_api_layer")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--product-api-status", source)
        self.assertIn("_product_api_main", source)


if __name__ == "__main__":
    unittest.main()
