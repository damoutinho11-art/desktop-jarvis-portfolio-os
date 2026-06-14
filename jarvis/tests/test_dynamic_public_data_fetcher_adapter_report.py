import unittest

from jarvis.dynamic_public_data_fetcher_adapter_report import report_dynamic_public_data_fetcher_adapter


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


class DynamicPublicDataFetcherAdapterReportTests(unittest.TestCase):
    def test_report_contains_ready_adapter_config_and_safety_boundary(self) -> None:
        report = report_dynamic_public_data_fetcher_adapter(REGISTRY, BINDINGS, ENDPOINTS)

        self.assertIn("J.A.R.V.I.S. Dynamic Public Data Fetcher Adapter", report)
        self.assertIn("status: DYNAMIC_PUBLIC_DATA_FETCHER_ADAPTER_READY_SAFE", report)
        self.assertIn("adapted source count: 6", report)
        self.assertIn("blocked source count: 0", report)
        self.assertIn("dry run default: True", report)
        self.assertIn("network forbidden by adapter: True", report)
        self.assertIn("write forbidden by adapter: True", report)
        self.assertIn("- source count: 6", report)
        self.assertIn("- execute_fetch: False", report)
        self.assertIn("- write_local_cache: False", report)
        self.assertIn("- no market fetch performed by adapter", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
