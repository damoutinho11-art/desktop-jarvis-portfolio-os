import unittest

from jarvis.dynamic_market_data_intake_validator_report import report_dynamic_market_data_intake


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


class DynamicMarketDataIntakeValidatorReportTests(unittest.TestCase):
    def test_report_contains_ready_rows_and_safety_boundary(self) -> None:
        report = report_dynamic_market_data_intake(REGISTRY, BINDINGS, MARKET_DATA)

        self.assertIn("J.A.R.V.I.S. Dynamic Market Data Intake Validator", report)
        self.assertIn("status: DYNAMIC_MARKET_DATA_INTAKE_READY_SAFE", report)
        self.assertIn("import plan status: DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE", report)
        self.assertIn("ready series count: 6", report)
        self.assertIn("blocked series count: 0", report)
        self.assertIn("vwce_global_core_candidate / global_core / ETF: MARKET_DATA_INTAKE_READY", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
