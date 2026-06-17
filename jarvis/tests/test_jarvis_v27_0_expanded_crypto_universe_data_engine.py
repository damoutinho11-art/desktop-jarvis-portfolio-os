from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v27_0_expanded_crypto_universe_data_engine import (
    DEFAULT_EXPANDED_CRYPTO_UNIVERSE,
    STATUS_READY,
    build_expanded_crypto_public_data_source_manifest,
    build_expanded_crypto_universe_data_engine_result,
)


def _raw_payload(key: str, price: float, market_cap: float, volume: float, change: float) -> dict:
    return {
        key: {
            "eur": price,
            "eur_market_cap": market_cap,
            "eur_24h_vol": volume,
            "eur_24h_change": change,
            "last_updated_at": 1781654400,
        }
    }


def _write_raw(root: Path, source_id: str, key: str, price: float, market_cap: float, volume: float, change: float) -> None:
    raw = root / "jarvis" / "local" / "public_data" / "v10_raw"
    raw.mkdir(parents=True, exist_ok=True)
    path = raw / f"2026-06-17_{source_id}.json.raw"
    path.write_text(json.dumps(_raw_payload(key, price, market_cap, volume, change)), encoding="utf-8")


class JarvisV270ExpandedCryptoUniverseDataEngineTests(unittest.TestCase):
    def test_manifest_expands_crypto_universe_with_public_safe_sources(self) -> None:
        manifest = build_expanded_crypto_public_data_source_manifest()

        self.assertEqual(len(manifest["sources"]), len(DEFAULT_EXPANDED_CRYPTO_UNIVERSE))
        self.assertGreaterEqual(len(manifest["sources"]), 10)
        for source in manifest["sources"]:
            self.assertEqual(source["source_type"], "public_market_data_json")
            self.assertTrue(source["public_source_only"])
            self.assertFalse(source["requires_credentials"])
            self.assertFalse(source["broker_or_trading_api"])
            self.assertFalse(source["contains_private_data"])
            self.assertIn("coingecko.com/api/v3/simple/price", source["source_url"])

    def test_scores_ready_public_crypto_candidates_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw(root, "coingecko_btc_simple_price_eur", "bitcoin", 56606.0, 1_100_000_000_000.0, 20_000_000_000.0, -1.1)
            _write_raw(root, "coingecko_eth_simple_price_eur", "ethereum", 3100.0, 350_000_000_000.0, 8_000_000_000.0, 2.4)
            (root / "portfolio_state.json").write_text(
                json.dumps({"platform_status": {"lhv_crypto_ready": True, "kraken_ready": False}}),
                encoding="utf-8",
            )

            result = build_expanded_crypto_universe_data_engine_result(
                current_date="2026-06-17",
                root=str(root) if False else None,  # sentinel to ensure no unsupported arg is used
            ) if False else build_expanded_crypto_universe_data_engine_result(
                current_date="2026-06-17",
                portfolio_state_path=root / "portfolio_state.json",
                raw_directory=root / "jarvis" / "local" / "public_data" / "v10_raw",
                normalized_directory=root / "jarvis" / "local" / "public_data" / "v22_multi_crypto_normalized",
                candidates=DEFAULT_EXPANDED_CRYPTO_UNIVERSE[:2],
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.full_public_data_coverage)
            self.assertEqual(result.source_quality_ready_count, 2)
            self.assertEqual(result.ranked_candidate_count, 2)
            self.assertIn(result.top_candidate_id, {"btc", "eth"})
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_missing_raw_data_is_review_required_not_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "portfolio_state.json").write_text(
                json.dumps({"platform_status": {"lhv_crypto_ready": True}}),
                encoding="utf-8",
            )
            result = build_expanded_crypto_universe_data_engine_result(
                current_date="2026-06-17",
                portfolio_state_path=root / "portfolio_state.json",
                raw_directory=root / "jarvis" / "local" / "public_data" / "v10_raw",
                normalized_directory=root / "jarvis" / "local" / "public_data" / "v22_multi_crypto_normalized",
                candidates=DEFAULT_EXPANDED_CRYPTO_UNIVERSE[:2],
            )

            self.assertFalse(result.full_public_data_coverage)
            self.assertEqual(result.source_quality_ready_count, 0)
            self.assertEqual(result.ranked_candidate_count, 0)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.no_trades_executed)

    def test_partial_public_data_coverage_writes_missing_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw(root, "coingecko_btc_simple_price_eur", "bitcoin", 56606.0, 1_100_000_000_000.0, 20_000_000_000.0, -1.1)
            (root / "portfolio_state.json").write_text(
                json.dumps({"platform_status": {"lhv_crypto_ready": True}}),
                encoding="utf-8",
            )
            missing_manifest_path = root / "jarvis" / "local" / "public_data_sources.missing.local.json"

            result = build_expanded_crypto_universe_data_engine_result(
                current_date="2026-06-17",
                missing_manifest_path=missing_manifest_path,
                portfolio_state_path=root / "portfolio_state.json",
                raw_directory=root / "jarvis" / "local" / "public_data" / "v10_raw",
                normalized_directory=root / "jarvis" / "local" / "public_data" / "v22_multi_crypto_normalized",
                write_missing_manifest=True,
                candidates=DEFAULT_EXPANDED_CRYPTO_UNIVERSE[:2],
            )

            self.assertFalse(result.status.endswith("_READY_SAFE"))
            self.assertTrue(missing_manifest_path.exists())
            payload = json.loads(missing_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual([source["candidate_id"] for source in payload["sources"]], ["eth"])
    def test_write_manifest_is_limited_to_ignored_local_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "jarvis" / "local" / "public_data_sources.local.json"
            result = build_expanded_crypto_universe_data_engine_result(
                current_date="2026-06-17",
                manifest_path=manifest_path,
                portfolio_state_path=root / "portfolio_state.json",
                raw_directory=root / "jarvis" / "local" / "public_data" / "v10_raw",
                normalized_directory=root / "jarvis" / "local" / "public_data" / "v22_multi_crypto_normalized",
                write_local_manifest=True,
                candidates=DEFAULT_EXPANDED_CRYPTO_UNIVERSE[:2],
            )

            self.assertTrue(result.manifest_written)
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["sources"]), 2)


if __name__ == "__main__":
    unittest.main()