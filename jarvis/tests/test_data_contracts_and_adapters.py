import tempfile
import unittest
from datetime import date
from pathlib import Path

from jarvis.data_contracts import (
    NormalizedMarketDataSnapshot,
    NormalizedMarketSeries,
    SourceMetadata,
)
from jarvis.risk_metrics import compute_market_risk_metrics
from jarvis.source_adapters import BaseSourceAdapter, LocalCSVMarketAdapter


def _write_csv(text: str) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".csv", delete=False, newline="") as file:
        file.write(text)
        return Path(file.name)


class DataContractsAndAdaptersTests(unittest.TestCase):
    def test_source_metadata_rejects_unknown_source_quality(self) -> None:
        with self.assertRaisesRegex(ValueError, "source_quality"):
            SourceMetadata("x", "Unknown", "spreadsheet_magic", date(2026, 6, 4))

    def test_source_metadata_requires_read_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "read-only"):
            SourceMetadata("x", "Mutable", "manual_csv", date(2026, 6, 4), read_only=False)

    def test_local_csv_market_adapter_returns_normalized_market_data(self) -> None:
        csv_path = _write_csv(
            "asset_id,currency,date,close\n"
            "csv_asset,EUR,2026-06-01,105\n"
            "csv_asset,EUR,2026-05-01,100\n"
        )
        snapshot = LocalCSVMarketAdapter(csv_path, as_of="2026-06-04").load_market_data()

        self.assertIsInstance(snapshot, NormalizedMarketDataSnapshot)
        self.assertIsInstance(snapshot.series[0], NormalizedMarketSeries)
        self.assertEqual(snapshot.source_metadata.source_quality, "manual_csv")
        self.assertTrue(snapshot.source_metadata.read_only)
        self.assertEqual(snapshot.series[0].prices[0].date.isoformat(), "2026-05-01")

    def test_core_metrics_consume_normalized_data_not_raw_csv_rows(self) -> None:
        csv_path = _write_csv(
            "asset_id,currency,date,close\n"
            "csv_asset,EUR,2025-06-01,100\n"
            "csv_asset,EUR,2025-12-01,110\n"
            "csv_asset,EUR,2026-06-01,121\n"
        )
        normalized_snapshot = LocalCSVMarketAdapter(csv_path, as_of="2026-06-04").load_market_data()

        metric = compute_market_risk_metrics(normalized_snapshot)[0]

        self.assertEqual(metric.asset_id, "csv_asset")
        self.assertEqual(metric.latest_price, 121.0)
        self.assertIsNotNone(metric.return_12m)

    def test_source_freshness_metadata_drives_stale_warning(self) -> None:
        csv_path = _write_csv(
            "asset_id,currency,date,close\n"
            "stale_asset,EUR,2026-05-01,100\n"
            "stale_asset,EUR,2026-05-10,101\n"
        )
        normalized_snapshot = LocalCSVMarketAdapter(csv_path, as_of="2026-06-04").load_market_data()

        metric = compute_market_risk_metrics(normalized_snapshot)[0]

        self.assertTrue(any("older than 7 days" in warning for warning in metric.warnings))

    def test_base_source_adapter_is_interface_only(self) -> None:
        with self.assertRaises(TypeError):
            BaseSourceAdapter()


if __name__ == "__main__":
    unittest.main()
