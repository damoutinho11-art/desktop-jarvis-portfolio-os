import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_raw_cache_normalizer import (
    STATUS_BLOCKED,
    STATUS_READY,
    normalize_dynamic_market_raw_cache,
)
from jarvis.dynamic_public_data_fetcher_adapter import build_dynamic_public_data_fetcher_adapter


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def _csv_payload(start: float = 100.0) -> str:
    lines = ["date,close"]
    for month in range(1, 13):
        lines.append(f"2026-{month:02d}-01,{start + month}")
    return "\n".join(lines) + "\n"


class DynamicMarketRawCacheNormalizerTests(unittest.TestCase):
    def test_normalizes_all_adapter_sources_from_csv_raw_cache(self) -> None:
        adapter = build_dynamic_public_data_fetcher_adapter(REGISTRY, BINDINGS, ENDPOINTS)

        with tempfile.TemporaryDirectory() as tmp:
            raw_paths = []
            for index, row in enumerate(adapter.rows):
                path = Path(tmp) / f"2026-06-15_{row.source_id}.csv.raw"
                path.write_text(_csv_payload(100.0 + index), encoding="utf-8")
                raw_paths.append(path)

            result = normalize_dynamic_market_raw_cache(REGISTRY, BINDINGS, ENDPOINTS, tuple(raw_paths))

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.expected_source_count, 6)
        self.assertEqual(result.normalized_series_count, 6)
        self.assertEqual(result.ready_row_count, 6)
        self.assertEqual(result.blocked_row_count, 0)
        self.assertEqual(result.as_of, "2026-12-01")
        self.assertEqual(result.normalized_market_data["base_currency"], "EUR")
        self.assertEqual(len(result.normalized_market_data["series"]), 6)
        self.assertFalse(result.blockers)
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.local_raw_cache_only)
        self.assertTrue(result.raw_data_unverified)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_blocks_when_raw_cache_files_are_missing(self) -> None:
        result = normalize_dynamic_market_raw_cache(REGISTRY, BINDINGS, ENDPOINTS, ())

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.normalized_series_count, 0)
        self.assertTrue(any("raw cache file is missing" in blocker for blocker in result.blockers))


if __name__ == "__main__":
    unittest.main()
