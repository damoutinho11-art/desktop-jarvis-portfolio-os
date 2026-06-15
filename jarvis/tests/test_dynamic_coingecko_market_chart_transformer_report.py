import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jarvis.dynamic_coingecko_market_chart_transformer_report import (
    report_dynamic_coingecko_market_chart_transformer,
)


def _valid_payload() -> dict:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return {
        "prices": [
            [
                int((start + timedelta(days=index)).timestamp() * 1000),
                100.0 + index,
            ]
            for index in range(13)
        ]
    }


def _write_json(payload) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


class DynamicCoinGeckoMarketChartTransformerReportTests(unittest.TestCase):
    def test_report_contains_ready_status_for_valid_local_fixture(self) -> None:
        report = report_dynamic_coingecko_market_chart_transformer(_write_json(_valid_payload()))

        self.assertIn("J.A.R.V.I.S. CoinGecko Market Chart Raw Fixture Transformer", report)
        self.assertIn("status: DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_READY_SAFE", report)
        self.assertIn("normalized price count: 13", report)
        self.assertIn("blockers:\n- none", report)
        self.assertIn("- no fetch performed", report)
        self.assertIn("- no API calls performed", report)
        self.assertIn("- no endpoint promotion", report)
        self.assertIn("- no approval granted", report)
        self.assertIn("- no trades executed", report)

    def test_report_contains_blocked_status_for_invalid_local_fixture(self) -> None:
        report = report_dynamic_coingecko_market_chart_transformer(_write_json({"prices": []}))

        self.assertIn("status: DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_BLOCKED_SAFE", report)
        self.assertIn("payload prices must be a non-empty list", report)
        self.assertIn("- no broker integration", report)
        self.assertIn("- no execution", report)


if __name__ == "__main__":
    unittest.main()
