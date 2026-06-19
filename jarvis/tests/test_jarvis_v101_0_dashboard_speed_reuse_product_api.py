from __future__ import annotations

from time import perf_counter
import unittest

from jarvis.runtime import operator
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.full_system_audit import build_full_system_audit_result
from jarvis.runtime.product_api import build_product_api_result


class JarvisV1010DashboardSpeedReuseProductApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        started = perf_counter()
        cls.product_api = build_product_api_result(current_date="2026-06-18")
        cls.product_api_elapsed = round(perf_counter() - started, 3)

    def test_full_audit_accepts_prebuilt_product_api(self) -> None:
        audit = build_full_system_audit_result(
            current_date="2026-06-18",
            product_api_result=self.product_api,
            product_api_elapsed_seconds=self.product_api_elapsed,
        )

        self.assertTrue(audit.product_api_ready)
        self.assertTrue(audit.data_readiness_ready)
        self.assertTrue(audit.news_coverage_ready)
        self.assertTrue(audit.safety_ready)
        self.assertEqual(audit.blockers, [])
        self.assertEqual(
            audit.speed_checks["product_api_elapsed_seconds"],
            self.product_api_elapsed,
        )

    def test_dashboard_contract_reuses_product_api_path(self) -> None:
        result = build_dashboard_contract_result(current_date="2026-06-18")

        self.assertTrue(result.dashboard_contract_ready)
        self.assertTrue(result.backend_ready)
        self.assertTrue(result.product_api_ready)
        self.assertTrue(result.full_audit_ready)
        self.assertTrue(result.manual_only)
        self.assertEqual(result.blockers, [])

    def test_operator_surface_v101(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v101.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "dashboard_speed_reuse_product_api")


if __name__ == "__main__":
    unittest.main()
