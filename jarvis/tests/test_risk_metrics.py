import unittest

from jarvis.market_data_loader import load_market_data
from jarvis.risk_metrics import compute_market_risk_metrics


class RiskMetricsTests(unittest.TestCase):
    def test_returns_are_computed_when_windows_exist(self) -> None:
        snapshot = load_market_data("jarvis/data/market_data.example.json")
        metric = compute_market_risk_metrics(snapshot)[0]

        self.assertIsNotNone(metric.return_1m)
        self.assertIsNotNone(metric.return_3m)
        self.assertIsNotNone(metric.return_6m)
        self.assertIsNotNone(metric.return_12m)
        self.assertAlmostEqual(metric.return_1m or 0.0, 116.0 / 114.0 - 1.0, places=6)

    def test_missing_windows_produce_warnings(self) -> None:
        snapshot = load_market_data("jarvis/data/market_data.example.json")
        short_series = snapshot.series[0].__class__(
            snapshot.series[0].asset_id,
            snapshot.series[0].currency,
            snapshot.series[0].prices[-2:],
        )
        short_snapshot = snapshot.__class__(snapshot.as_of, snapshot.base_currency, (short_series,))
        metric = compute_market_risk_metrics(short_snapshot)[0]

        self.assertIsNone(metric.return_3m)
        self.assertTrue(any("insufficient data" in warning for warning in metric.warnings))

    def test_volatility_is_computed(self) -> None:
        metric = compute_market_risk_metrics(load_market_data("jarvis/data/market_data.example.json"))[0]

        self.assertIsNotNone(metric.annualized_volatility)
        self.assertGreater(metric.annualized_volatility or 0.0, 0.0)

    def test_max_drawdown_is_computed(self) -> None:
        metric = compute_market_risk_metrics(load_market_data("jarvis/data/market_data.example.json"))[1]

        self.assertLess(metric.max_drawdown, 0.0)

    def test_stale_sparse_and_non_eur_warnings(self) -> None:
        snapshot = load_market_data("jarvis/data/market_data.example.json")
        stale_sparse_series = snapshot.series[0].__class__(
            "usd_sparse_asset",
            "USD",
            snapshot.series[0].prices[:3],
        )
        stale_snapshot = snapshot.__class__(snapshot.as_of, snapshot.base_currency, (stale_sparse_series,))
        metric = compute_market_risk_metrics(stale_snapshot)[0]

        self.assertTrue(any("older than 7 days" in warning for warning in metric.warnings))
        self.assertTrue(any("fewer than 10" in warning for warning in metric.warnings))
        self.assertTrue(any("currency is USD" in warning for warning in metric.warnings))


if __name__ == "__main__":
    unittest.main()
