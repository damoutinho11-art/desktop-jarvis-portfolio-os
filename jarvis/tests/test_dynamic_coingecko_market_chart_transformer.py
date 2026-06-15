import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jarvis.dynamic_coingecko_market_chart_transformer import (
    STATUS_BLOCKED,
    STATUS_READY,
    transform_coingecko_market_chart_file,
    transform_coingecko_market_chart_payload,
)


def _timestamp_ms(year: int, month: int, day: int) -> int:
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


def _valid_payload(days: int = 13) -> dict:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return {
        "prices": [
            [
                int((start + timedelta(days=index)).timestamp() * 1000),
                100.0 + index,
            ]
            for index in range(days)
        ]
    }


def _write_json(payload) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


class DynamicCoinGeckoMarketChartTransformerTests(unittest.TestCase):
    def test_valid_payload_transforms_to_normalizer_ready_rows(self) -> None:
        result = transform_coingecko_market_chart_payload(_valid_payload())

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.normalized_price_count, 13)
        self.assertEqual(
            result.normalized_payload["prices"][0],
            {"date": "2026-01-01", "close": 100.0},
        )
        self.assertFalse(result.blockers)

    def test_utc_timestamp_conversion_is_correct(self) -> None:
        result = transform_coingecko_market_chart_payload(
            {"prices": [[_timestamp_ms(2026, 6, 14), 123.45]] * 12}
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.normalized_payload["prices"], [{"date": "2026-06-14", "close": 123.45}])
        self.assertTrue(any("fewer than 12" in blocker for blocker in result.blockers))

    def test_duplicate_same_day_rows_keep_last_value(self) -> None:
        payload = _valid_payload()
        payload["prices"].append([_timestamp_ms(2026, 1, 1) + 1, 999.0])

        result = transform_coingecko_market_chart_payload(payload)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.normalized_payload["prices"][0], {"date": "2026-01-01", "close": 999.0})
        self.assertEqual(result.normalized_price_count, 13)

    def test_rows_are_sorted_by_date(self) -> None:
        payload = _valid_payload()
        payload["prices"] = list(reversed(payload["prices"]))

        result = transform_coingecko_market_chart_payload(payload)
        dates = [row["date"] for row in result.normalized_payload["prices"]]

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(dates, sorted(dates))

    def test_missing_prices_blocks_safely(self) -> None:
        result = transform_coingecko_market_chart_payload({})

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("prices must be a non-empty list" in blocker for blocker in result.blockers))
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.local_fixture_only)

    def test_bad_json_object_shape_blocks_safely(self) -> None:
        result = transform_coingecko_market_chart_payload([[_timestamp_ms(2026, 1, 1), 100.0]])

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("JSON object" in blocker for blocker in result.blockers))

    def test_bad_row_shape_blocks_safely(self) -> None:
        payload = _valid_payload()
        payload["prices"][0] = [_timestamp_ms(2026, 1, 1), 100.0, "extra"]

        result = transform_coingecko_market_chart_payload(payload)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("two-item" in blocker for blocker in result.blockers))

    def test_non_positive_or_bool_timestamp_or_price_blocks_safely(self) -> None:
        payload = _valid_payload()
        payload["prices"][0] = [False, 100.0]
        payload["prices"][1] = [0, 100.0]
        payload["prices"][2] = [_timestamp_ms(2026, 1, 3), True]
        payload["prices"][3] = [_timestamp_ms(2026, 1, 4), 0]

        result = transform_coingecko_market_chart_payload(payload)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("timestamp must be a positive number" in blocker for blocker in result.blockers))
        self.assertTrue(any("price must be a positive number" in blocker for blocker in result.blockers))

    def test_fewer_than_12_rows_blocks_safely(self) -> None:
        result = transform_coingecko_market_chart_payload(_valid_payload(days=11))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.normalized_price_count, 11)
        self.assertTrue(any("fewer than 12" in blocker for blocker in result.blockers))

    def test_file_transform_writes_output_only_when_output_path_is_provided(self) -> None:
        input_path = _write_json(_valid_payload())
        output_path = Path(tempfile.mkdtemp()) / "normalized.json"

        no_write = transform_coingecko_market_chart_file(input_path)
        self.assertEqual(no_write.status, STATUS_READY)
        self.assertIsNone(no_write.output_path)
        self.assertFalse(output_path.exists())

        written = transform_coingecko_market_chart_file(input_path, output_path)
        self.assertEqual(written.status, STATUS_READY)
        self.assertEqual(written.output_path, str(output_path))
        self.assertTrue(output_path.exists())
        self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), written.normalized_payload)

    def test_file_transform_bad_json_blocks_safely(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
            file.write("{bad json")
            path = Path(file.name)

        result = transform_coingecko_market_chart_file(path)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("failed to parse input JSON" in blocker for blocker in result.blockers))

    def test_safety_flags_remain_no_fetch_no_approval_no_execution_no_trades(self) -> None:
        result = transform_coingecko_market_chart_payload(_valid_payload())
        payload = result.to_dict()

        self.assertTrue(payload["fetching_forbidden"])
        self.assertTrue(payload["local_fixture_only"])
        self.assertTrue(payload["raw_data_unverified"])
        self.assertTrue(payload["manual_approval_required"])
        self.assertTrue(payload["execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertFalse(payload["grants_approval"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
