import json
import tempfile
import unittest
from pathlib import Path

from jarvis.market_data_loader import MarketDataError, load_market_data


def _write_market_data(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _valid_payload(prices: list[dict] | None = None) -> dict:
    return {
        "as_of": "2026-06-04",
        "base_currency": "EUR",
        "series": [
            {
                "asset_id": "quality_etf_candidate",
                "currency": "EUR",
                "prices": prices
                or [
                    {"date": "2026-05-01", "close": 100.0},
                    {"date": "2026-06-01", "close": 105.0},
                ],
            }
        ],
    }


class MarketDataLoaderTests(unittest.TestCase):
    def test_valid_fixture_loads(self) -> None:
        snapshot = load_market_data("jarvis/data/market_data.example.json")

        self.assertEqual(snapshot.base_currency, "EUR")
        self.assertEqual(len(snapshot.series), 2)
        self.assertEqual(snapshot.series[0].prices[-1].close, 116.0)

    def test_missing_required_fields_rejected(self) -> None:
        payload = _valid_payload()
        del payload["as_of"]

        with self.assertRaisesRegex(MarketDataError, "as_of exists"):
            load_market_data(_write_market_data(payload))

    def test_negative_or_zero_price_rejected(self) -> None:
        payload = _valid_payload([{"date": "2026-06-01", "close": 0.0}])

        with self.assertRaisesRegex(MarketDataError, "close must be positive"):
            load_market_data(_write_market_data(payload))

    def test_duplicate_dates_rejected(self) -> None:
        payload = _valid_payload(
            [
                {"date": "2026-06-01", "close": 100.0},
                {"date": "2026-06-01", "close": 101.0},
            ]
        )

        with self.assertRaisesRegex(MarketDataError, "duplicate price date"):
            load_market_data(_write_market_data(payload))

    def test_unsorted_dates_are_sorted_deterministically(self) -> None:
        payload = _valid_payload(
            [
                {"date": "2026-06-01", "close": 105.0},
                {"date": "2026-05-01", "close": 100.0},
            ]
        )

        snapshot = load_market_data(_write_market_data(payload))

        self.assertEqual(snapshot.series[0].prices[0].date.isoformat(), "2026-05-01")
        self.assertEqual(snapshot.series[0].prices[-1].date.isoformat(), "2026-06-01")


if __name__ == "__main__":
    unittest.main()
