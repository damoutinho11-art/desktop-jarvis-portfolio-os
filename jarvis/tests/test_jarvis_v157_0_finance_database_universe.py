from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.finance_database_universe import (
    STATUS_READY,
    build_finance_database_universe_result,
    normalize_fixture_universe,
    normalize_universe_record,
)


FIXTURE_UNIVERSE = {
    "equities": [
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "sector": "Technology",
        }
    ],
    "etfs_funds": [
        {
            "ticker": "VWCE",
            "name": "Vanguard FTSE All-World UCITS ETF",
            "exchange_code": "XETRA",
            "country_name": "Ireland",
            "currency_code": "EUR",
            "category": "Global equity ETF",
        }
    ],
    "indices": [{"symbol": "SPX", "name": "S&P 500", "currency": "USD"}],
    "currencies": [{"code": "EUR", "name": "Euro"}],
    "crypto": [{"symbol": "BTC", "name": "Bitcoin", "currency": "USD"}],
    "money_markets": [{"symbol": "EURMM", "name": "EUR money market"}],
}


class JarvisV157FinanceDatabaseUniverseTests(unittest.TestCase):
    def test_missing_dependency_returns_safe_warning(self) -> None:
        with patch("jarvis.runtime.finance_database_universe._load_financedatabase_module", return_value=None):
            result = build_finance_database_universe_result()

        self.assertEqual(result.status, STATUS_READY)
        self.assertFalse(result.dependency_available)
        self.assertFalse(result.universe_ready)
        self.assertEqual(result.blockers, [])
        self.assertIn("optional dependency not installed", result.warnings)

    def test_fixture_universe_normalization_works(self) -> None:
        result = build_finance_database_universe_result(fixture_universe=FIXTURE_UNIVERSE)

        self.assertTrue(result.dependency_available)
        self.assertTrue(result.universe_ready)
        self.assertEqual(result.metadata_counts["equities"], 1)
        self.assertEqual(result.metadata_counts["etfs_funds"], 1)
        symbols = {item["symbol"] for item in result.sample_instruments}
        self.assertIn("MSFT", symbols)
        self.assertIn("VWCE", symbols)

    def test_metadata_fields_normalized(self) -> None:
        row = normalize_universe_record(
            {
                "ticker": "is3q.de",
                "long_name": "iShares MSCI World Quality Factor",
                "mic": "XETRA",
                "domicile": "Ireland",
                "quote_currency": "EUR",
                "industry": "Quality ETF",
            },
            asset_type="fund",
        )

        self.assertEqual(row["symbol"], "IS3Q.DE")
        self.assertEqual(row["name"], "iShares MSCI World Quality Factor")
        self.assertEqual(row["asset_type"], "fund")
        self.assertEqual(row["exchange"], "XETRA")
        self.assertEqual(row["country"], "Ireland")
        self.assertEqual(row["currency"], "EUR")
        self.assertEqual(row["sector_category"], "Quality ETF")
        self.assertEqual(row["source"], "FinanceDatabase")

    def test_no_trading_execution_fields(self) -> None:
        _counts, samples = normalize_fixture_universe(FIXTURE_UNIVERSE)
        result = build_finance_database_universe_result(fixture_universe=FIXTURE_UNIVERSE).to_dict()
        text = str(result).lower() + str(samples).lower()

        for forbidden in ("broker", "credential", "password", "api_key", "buy_request", "sell_request", "order", "trade"):
            self.assertNotIn(forbidden, text)

    def test_operator_route_works(self) -> None:
        with patch(
            "jarvis.runtime.finance_database_universe.build_finance_database_universe_result",
            return_value=build_finance_database_universe_result(fixture_universe=FIXTURE_UNIVERSE),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--finance-database-universe"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V157_0_FINANCEDATABASE_UNIVERSE_ADAPTER_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
