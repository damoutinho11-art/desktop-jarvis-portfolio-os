import unittest

from jarvis.dynamic_market_import_plan_report import report_dynamic_market_import_plan


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"


class DynamicMarketImportPlanReportTests(unittest.TestCase):
    def test_report_contains_ready_rows_and_safety_boundary(self) -> None:
        report = report_dynamic_market_import_plan(REGISTRY, BINDINGS)

        self.assertIn("J.A.R.V.I.S. Dynamic Market Import Plan", report)
        self.assertIn("status: DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE", report)
        self.assertIn("source binding status: DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE", report)
        self.assertIn("ready row count: 6", report)
        self.assertIn("fetching forbidden: True", report)
        self.assertIn("vwce_global_core_candidate / global_core / ETF: IMPORT_PLAN_READY", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
