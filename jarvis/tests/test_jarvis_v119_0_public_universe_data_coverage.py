import unittest

from jarvis.runtime.public_universe_data_coverage import (
    STATUS_READY,
    build_public_universe_data_coverage_result,
)


class TestJarvisV119PublicUniverseDataCoverage(unittest.TestCase):
    def test_result_ready_safe(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)
        self.assertFalse(result.auto_approval_enabled)

    def test_selected_symbols_are_covered(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        selected = set(result.selected_symbols)
        self.assertIn("BTC", selected)
        self.assertIn("ETH", selected)
        self.assertIn("MSFT", selected)
        self.assertIn("VWCE", selected)
        self.assertIn("GLOBAL_CORE_ETF", selected)
        self.assertIn("IS3Q.DE", selected)

    def test_lane_summaries_exist(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        lanes = {summary["lane"] for summary in result.lane_summaries}
        self.assertIn("crypto", lanes)
        self.assertIn("etf_fund", lanes)
        self.assertIn("individual_stock", lanes)

    def test_etf_gaps_are_prioritized(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        priority = set(result.next_fetch_priority)
        self.assertTrue({"GLOBAL_CORE_ETF", "VWCE", "IS3Q.DE"} & priority)

    def test_selected_trusted_records_are_not_downgraded_by_universe_scan(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        records = {record["symbol"]: record for record in result.records}
        self.assertTrue(records["BTC"]["trusted_quote"])
        self.assertTrue(records["ETH"]["trusted_quote"])
        self.assertTrue(records["MSFT"]["trusted_quote"])
        self.assertEqual(records["MSFT"]["lane"], "individual_stock")

    def test_no_duplicate_symbol_records(self):
        result = build_public_universe_data_coverage_result(current_date="2026-06-18")
        symbols = [record["symbol"] for record in result.records]
        self.assertEqual(len(symbols), len(set(symbols)))



if __name__ == "__main__":
    unittest.main()
