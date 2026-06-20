import unittest

from jarvis.runtime.dashboard_contract import (
    _v127_clean_dashboard_warnings,
    build_dashboard_contract_result,
    format_dashboard_contract,
)


class TestJarvisV127DashboardUXFinalPolish(unittest.TestCase):
    def test_dashboard_contract_status_is_v127_ready(self):
        result = build_dashboard_contract_result(current_date="2026-06-20")
        self.assertEqual(result.status, "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE")
        self.assertTrue(result.dashboard_contract_ready)
        text = format_dashboard_contract(result)
        self.assertIn("manual-only safety: True", text)
        self.assertIn("manual approval remains required", text)
        self.assertIn("no broker, credentials, order, trade, or auto-approval path is enabled", text)
        self.assertEqual(result.blockers, [])

    def test_dashboard_warning_output_is_cleaned(self):
        result = build_dashboard_contract_result(current_date="2026-06-20")
        text = format_dashboard_contract(result)

        self.assertIn("WARNINGS:", text)
        self.assertIn("manual approval remains required", text)
        self.assertIn("no broker, credentials, order, trade, or auto-approval path is enabled", text)
        self.assertNotIn("product-mode audit warning: unresolved local imports", text)
        self.assertNotIn("ignored non-data preflight blocker", text)
        self.assertNotIn("this command does not fetch data", text)

    def test_warning_cleaner_limits_dashboard_noise(self):
        noisy = [
            "dashboard contract is local/static and does not start a web server",
            "this command does not fetch data, approve purchases, connect brokers, create orders, or trade",
            "product-mode audit warning: unresolved local imports: 1",
            "manual approval remains required; no execution path is created",
            "no broker, credentials, order, trade, or auto-approval path is enabled",
        ]
        cleaned = _v127_clean_dashboard_warnings(noisy)

        self.assertLessEqual(len(cleaned), 8)
        self.assertIn("manual approval remains required; no execution path is created", cleaned)
        self.assertNotIn("product-mode audit warning: unresolved local imports: 1", cleaned)


if __name__ == "__main__":
    unittest.main()
