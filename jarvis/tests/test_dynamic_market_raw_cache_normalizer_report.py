import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_raw_cache_normalizer_report import report_dynamic_market_raw_cache_normalizer
from jarvis.dynamic_public_data_fetcher_adapter import build_dynamic_public_data_fetcher_adapter


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def _csv_payload() -> str:
    lines = ["date,close"]
    for month in range(1, 13):
        lines.append(f"2026-{month:02d}-01,{100 + month}")
    return "\n".join(lines) + "\n"


class DynamicMarketRawCacheNormalizerReportTests(unittest.TestCase):
    def test_report_contains_ready_status_and_safety(self) -> None:
        adapter = build_dynamic_public_data_fetcher_adapter(REGISTRY, BINDINGS, ENDPOINTS)

        with tempfile.TemporaryDirectory() as tmp:
            raw_paths = []
            for row in adapter.rows:
                path = Path(tmp) / f"2026-06-15_{row.source_id}.csv.raw"
                path.write_text(_csv_payload(), encoding="utf-8")
                raw_paths.append(path)

            report = report_dynamic_market_raw_cache_normalizer(
                REGISTRY, BINDINGS, ENDPOINTS, tuple(raw_paths)
            )

        self.assertIn("J.A.R.V.I.S. Dynamic Market Raw Cache Normalizer", report)
        self.assertIn("status: DYNAMIC_MARKET_RAW_CACHE_NORMALIZER_READY_SAFE", report)
        self.assertIn("normalized series count: 6", report)
        self.assertIn("raw data unverified: True", report)
        self.assertIn("- no public fetch performed by normalizer", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
