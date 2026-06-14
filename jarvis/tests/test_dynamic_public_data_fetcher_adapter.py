import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_public_data_fetcher_adapter import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_dynamic_public_data_fetcher_adapter,
)


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _endpoint_copy(transform) -> Path:
    payload = json.loads(Path(ENDPOINTS).read_text(encoding="utf-8"))
    transform(payload)
    return _write_json(payload)


class DynamicPublicDataFetcherAdapterTests(unittest.TestCase):
    def test_tracked_dynamic_endpoints_adapt_to_existing_fetcher_config(self) -> None:
        result = build_dynamic_public_data_fetcher_adapter(REGISTRY, BINDINGS, ENDPOINTS)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.import_plan_status, "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE")
        self.assertEqual(result.adapted_source_count, 6)
        self.assertEqual(result.blocked_source_count, 0)
        self.assertTrue(result.authorization_required)
        self.assertTrue(result.dry_run_default)
        self.assertTrue(result.network_forbidden_by_adapter)
        self.assertTrue(result.write_forbidden_by_adapter)
        self.assertTrue(result.local_cache_only)
        self.assertTrue(result.raw_data_unverified)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

        config = result.public_fetcher_config
        self.assertEqual(len(config["sources"]), 6)
        self.assertFalse(config["execute_fetch"])
        self.assertFalse(config["write_local_cache"])
        self.assertEqual(config["fetcher_mode"], "dry_run_default")
        self.assertTrue(all(source["public_source_only"] for source in config["sources"]))
        self.assertTrue(all(source["requires_credentials"] is False for source in config["sources"]))
        self.assertTrue(all(source["broker_or_trading_api"] is False for source in config["sources"]))

    def test_missing_endpoint_mapping_blocks_safely(self) -> None:
        def transform(payload: dict) -> None:
            payload["endpoints"] = payload["endpoints"][1:]

        result = build_dynamic_public_data_fetcher_adapter(
            REGISTRY, BINDINGS, _endpoint_copy(transform)
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.adapted_source_count, 5)
        self.assertEqual(result.blocked_source_count, 1)
        self.assertTrue(any("endpoint mapping is missing" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)

    def test_credential_query_parameter_blocks_safely(self) -> None:
        def transform(payload: dict) -> None:
            payload["endpoints"][0]["source_url"] = "https://example.com/market-data/btc.json?api_key=secret"

        result = build_dynamic_public_data_fetcher_adapter(
            REGISTRY, BINDINGS, _endpoint_copy(transform)
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("credential-looking query parameter" in blocker for blocker in result.blockers))
        self.assertTrue(result.network_forbidden_by_adapter)
        self.assertTrue(result.write_forbidden_by_adapter)

    def test_broker_endpoint_blocks_safely(self) -> None:
        def transform(payload: dict) -> None:
            payload["endpoints"][0]["source_url"] = "https://broker.example.com/login/market-data/btc.json"

        result = build_dynamic_public_data_fetcher_adapter(
            REGISTRY, BINDINGS, _endpoint_copy(transform)
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("broker/authenticated-looking endpoint" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
