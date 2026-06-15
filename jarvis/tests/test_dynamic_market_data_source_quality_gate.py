import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_data_source_quality_gate import (
    STATUS_BLOCKED,
    STATUS_READY,
    audit_dynamic_market_data_source_quality,
)


DEFAULT_REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"
DEFAULT_MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, asset_type: str, ticker: str, **overrides) -> dict:
    payload = {
        "asset_id": asset_id,
        "name": f"{ticker} asset",
        "asset_type": asset_type,
        "sleeve": "global_core" if asset_type == "ETF" else "crypto_core",
        "ticker": ticker,
        "isin_or_symbol": "IE00BK5BQT80" if asset_type == "ETF" else ticker,
        "platforms": ["Manual Public Source Review"],
        "currency": "EUR",
        "domicile": "Ireland" if asset_type == "ETF" else "n/a",
        "distribution_policy": "accumulating" if asset_type == "ETF" else "n/a",
        "ter_or_fee": 0.2 if asset_type == "ETF" else 0.0,
        "data_source": "verified_public_source_reference_for_quality_gate",
        "approval_status": "approved_investable",
        "risk_level": "medium" if asset_type == "ETF" else "high",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
        "network_or_protocol": "Protocol",
        "custody_platforms": ["Manual Public Source Review"],
        "transferable": False,
        "mica_route_possible": True,
    }
    if asset_type == "ETF":
        for field in ("network_or_protocol", "custody_platforms", "transferable", "mica_route_possible"):
            payload.pop(field)
    else:
        for field in ("provider", "index_tracked", "replication_method"):
            payload.pop(field)
    payload.update(overrides)
    return payload


def _registry(*assets: dict) -> Path:
    return _write_json({"assets": list(assets)})


def _bindings(asset_ids: list[str], provider: str = "stooq_public_csv") -> Path:
    return _write_json(
        {
            "binding_pack_id": "quality_ready_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": [
                {
                    "asset_id": asset_id,
                    "source_provider": provider if not asset_id.startswith(("btc", "hype", "tao")) else "coingecko_public_api",
                    "source_symbol": asset_id,
                    "cache_series_id": asset_id,
                    "expected_currency": "EUR",
                    "enabled": True,
                }
                for asset_id in asset_ids
            ],
        }
    )


def _endpoints(asset_ids: list[str], **overrides) -> Path:
    endpoints = []
    for asset_id in asset_ids:
        is_crypto = asset_id.startswith(("btc", "hype", "tao"))
        payload = {
            "asset_id": asset_id,
            "source_type": "public_market_data_json" if is_crypto else "public_market_data_csv",
            "source_url": (
                f"https://coingecko.local.test/market-data/{asset_id}.json"
                if is_crypto
                else f"https://stooq.local.test/market-data/{asset_id}.csv"
            ),
            "update_frequency": "daily",
            "public_source_only": True,
            "requires_authentication": False,
            "requires_credentials": False,
            "broker_or_trading_api": False,
            "contains_private_data": False,
            "cross_check_source": "manual_secondary_public_market_source",
        }
        if is_crypto:
            payload["coingecko_coin_id"] = {
                "btc_crypto_core_candidate": "bitcoin",
                "hype_speculative_crypto_candidate": "hyperliquid",
                "tao_speculative_crypto_candidate": "bittensor",
            }[asset_id]
        payload.update(overrides)
        endpoints.append(payload)
    return _write_json(
        {
            "endpoint_pack_id": "quality_ready_endpoints",
            "manual_review_required": True,
            "authorization_required_before_fetch": True,
            "execution_forbidden": True,
            "endpoints": endpoints,
        }
    )


def _market_data(asset_ids: list[str], currency: str = "EUR", date_prefix: str = "2026-06") -> Path:
    prices = [{"date": f"{date_prefix}-{day:02d}", "close": 100.0 + day} for day in range(1, 14)]
    return _write_json(
        {
            "as_of": f"{date_prefix}-14",
            "base_currency": "EUR",
            "raw_data_unverified": True,
            "execution_forbidden": True,
            "creates_buy_request": False,
            "no_trades_executed": True,
            "series": [
                {
                    "asset_id": asset_id,
                    "currency": currency,
                    "prices": prices,
                }
                for asset_id in asset_ids
            ],
        }
    )


def _quality_ready_paths() -> tuple[Path, Path, Path, Path]:
    asset_ids = [
        "vwce_global_core_candidate",
        "btc_crypto_core_candidate",
        "hype_speculative_crypto_candidate",
        "tao_speculative_crypto_candidate",
    ]
    return (
        _registry(
            _asset("vwce_global_core_candidate", "ETF", "VWCE"),
            _asset("btc_crypto_core_candidate", "crypto", "BTC", coingecko_coin_id="bitcoin"),
            _asset("hype_speculative_crypto_candidate", "crypto", "HYPE", coingecko_coin_id="hyperliquid"),
            _asset("tao_speculative_crypto_candidate", "crypto", "TAO", coingecko_coin_id="bittensor"),
        ),
        _bindings(asset_ids),
        _endpoints(asset_ids),
        _market_data(asset_ids),
    )


class DynamicMarketDataSourceQualityGateTests(unittest.TestCase):
    def test_default_dynamic_fixture_blocks_for_source_quality(self) -> None:
        result = audit_dynamic_market_data_source_quality(
            DEFAULT_REGISTRY,
            DEFAULT_BINDINGS,
            DEFAULT_ENDPOINTS,
            DEFAULT_MARKET_DATA,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.ready_row_count, 0)
        self.assertTrue(any("example.com" in blocker for blocker in result.blockers))
        self.assertTrue(any("synthetic or fixture" in blocker for blocker in result.blockers))
        self.assertTrue(any("manual_market_fixture" in blocker for blocker in result.blockers))
        self.assertTrue(any("crypto asset requires" in blocker for blocker in result.blockers))
        self.assertTrue(any("cross_check_source" in blocker for blocker in result.blockers))
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.raw_data_unverified)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_quality_ready_temp_fixture_reaches_ready_safe(self) -> None:
        result = audit_dynamic_market_data_source_quality(*_quality_ready_paths())

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.approved_asset_count, 4)
        self.assertEqual(result.ready_row_count, 4)
        self.assertEqual(result.blocked_row_count, 0)
        self.assertFalse(result.blockers)
        self.assertTrue(all(row.freshness_status == "FRESH_ENOUGH" for row in result.rows))

    def test_etf_requires_isin_like_identifier(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        raw = json.loads(Path(registry).read_text(encoding="utf-8"))
        raw["assets"][0]["isin_or_symbol"] = "VWCE"
        result = audit_dynamic_market_data_source_quality(
            _write_json(raw),
            bindings,
            endpoints,
            market_data,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("ETF isin_or_symbol is not ISIN-like" in blocker for blocker in result.blockers))

    def test_crypto_requires_coin_identity(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        raw = json.loads(Path(registry).read_text(encoding="utf-8"))
        for asset in raw["assets"]:
            asset.pop("coingecko_coin_id", None)
        endpoint_raw = json.loads(Path(endpoints).read_text(encoding="utf-8"))
        for endpoint in endpoint_raw["endpoints"]:
            endpoint.pop("coingecko_coin_id", None)

        result = audit_dynamic_market_data_source_quality(
            _write_json(raw),
            bindings,
            _write_json(endpoint_raw),
            market_data,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("crypto asset requires" in blocker for blocker in result.blockers))

    def test_missing_cross_check_blocks_without_manual_waiver(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        endpoint_raw = json.loads(Path(endpoints).read_text(encoding="utf-8"))
        for endpoint in endpoint_raw["endpoints"]:
            endpoint.pop("cross_check_source", None)

        result = audit_dynamic_market_data_source_quality(
            registry,
            bindings,
            _write_json(endpoint_raw),
            market_data,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("missing cross_check_source" in blocker for blocker in result.blockers))

    def test_manual_cross_check_waiver_allows_missing_cross_check(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        endpoint_raw = json.loads(Path(endpoints).read_text(encoding="utf-8"))
        for endpoint in endpoint_raw["endpoints"]:
            endpoint.pop("cross_check_source", None)
            endpoint["manual_cross_check_waiver"] = True

        result = audit_dynamic_market_data_source_quality(
            registry,
            bindings,
            _write_json(endpoint_raw),
            market_data,
        )

        self.assertEqual(result.status, STATUS_READY)

    def test_market_data_currency_points_and_freshness_are_enforced(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        raw = json.loads(Path(market_data).read_text(encoding="utf-8"))
        raw["series"][0]["currency"] = "USD"
        raw["series"][1]["prices"] = raw["series"][1]["prices"][:11]
        for index, price in enumerate(raw["series"][2]["prices"], start=1):
            price["date"] = f"2026-05-{index:02d}"

        result = audit_dynamic_market_data_source_quality(
            registry,
            bindings,
            endpoints,
            _write_json(raw),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("does not match expected_currency" in blocker for blocker in result.blockers))
        self.assertTrue(any("fewer than 12 price points" in blocker for blocker in result.blockers))
        self.assertTrue(any("days before as_of" in blocker for blocker in result.blockers))

    def test_endpoint_safety_fields_are_enforced(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        raw = json.loads(Path(endpoints).read_text(encoding="utf-8"))
        raw["endpoints"][0]["requires_authentication"] = True
        raw["endpoints"][1]["requires_credentials"] = True
        raw["endpoints"][2]["broker_or_trading_api"] = True
        raw["endpoints"][3]["contains_private_data"] = True

        result = audit_dynamic_market_data_source_quality(
            registry,
            bindings,
            _write_json(raw),
            market_data,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("requires authentication" in blocker for blocker in result.blockers))
        self.assertTrue(any("requires credentials" in blocker for blocker in result.blockers))
        self.assertTrue(any("broker_or_trading_api" in blocker for blocker in result.blockers))
        self.assertTrue(any("contains private data" in blocker for blocker in result.blockers))

    def test_each_asset_requires_exactly_one_endpoint_binding_and_series(self) -> None:
        registry, bindings, endpoints, market_data = _quality_ready_paths()
        endpoint_raw = json.loads(Path(endpoints).read_text(encoding="utf-8"))
        endpoint_raw["endpoints"].append(dict(endpoint_raw["endpoints"][0]))
        binding_raw = json.loads(Path(bindings).read_text(encoding="utf-8"))
        binding_raw["bindings"] = binding_raw["bindings"][1:]
        market_raw = json.loads(Path(market_data).read_text(encoding="utf-8"))
        market_raw["series"] = market_raw["series"][1:]

        result = audit_dynamic_market_data_source_quality(
            registry,
            _write_json(binding_raw),
            _write_json(endpoint_raw),
            _write_json(market_raw),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("expected exactly one endpoint row" in blocker for blocker in result.blockers))
        self.assertTrue(any("expected exactly one binding row" in blocker for blocker in result.blockers))
        self.assertTrue(any("expected exactly one market data series" in blocker for blocker in result.blockers))


if __name__ == "__main__":
    unittest.main()
