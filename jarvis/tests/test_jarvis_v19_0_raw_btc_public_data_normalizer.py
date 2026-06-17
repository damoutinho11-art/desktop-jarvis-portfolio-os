import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v19_0_raw_btc_public_data_normalizer import (
    DEFAULT_SOURCE_ID,
    STATUS_BLOCKED,
    STATUS_READY,
    build_raw_btc_public_data_normalizer_result,
    normalize_coingecko_btc_raw,
)


class JarvisV190RawBtcPublicDataNormalizerTests(unittest.TestCase):
    def _write_raw(self, root: str, payload: dict, filename: str = "2026-06-17_coingecko_btc_simple_price_eur.json.raw") -> Path:
        raw_dir = Path(root) / "jarvis" / "local" / "public_data" / "v10_raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir / filename
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_normalizes_valid_coingecko_btc_raw_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_file = self._write_raw(
                temp_dir,
                {
                    "bitcoin": {
                        "eur": 56569,
                        "eur_market_cap": 1133363561099.5803,
                        "eur_24h_vol": 22777201329.998524,
                        "eur_24h_change": -1.036540118449373,
                        "last_updated_at": 1781654676,
                    }
                },
            )

            signal, blockers, warnings = normalize_coingecko_btc_raw(raw_file)

            self.assertFalse(blockers)
            self.assertFalse(warnings)
            self.assertIsNotNone(signal)
            assert signal is not None
            self.assertEqual(signal.candidate_id, "btc")
            self.assertEqual(signal.source_id, DEFAULT_SOURCE_ID)
            self.assertEqual(signal.as_of, "2026-06-17")
            self.assertEqual(signal.price_eur, 56569.0)
            self.assertEqual(signal.change_24h_pct, -1.03654012)
            self.assertTrue(signal.raw_data_unverified)
            self.assertTrue(signal.normalized_public_signal)
            self.assertTrue(signal.ready_for_source_quality_gate)

    def test_result_finds_latest_raw_file_without_mutating_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._write_raw(
                temp_dir,
                {
                    "bitcoin": {
                        "eur": 56000,
                        "eur_market_cap": 1000,
                        "eur_24h_vol": 100,
                        "eur_24h_change": 1,
                        "last_updated_at": 1781654000,
                    }
                },
                filename="2026-06-16_coingecko_btc_simple_price_eur.json.raw",
            )
            self._write_raw(
                temp_dir,
                {
                    "bitcoin": {
                        "eur": 56569,
                        "eur_market_cap": 1133363561099.5803,
                        "eur_24h_vol": 22777201329.998524,
                        "eur_24h_change": -1.036540118449373,
                        "last_updated_at": 1781654676,
                    }
                },
                filename="2026-06-17_coingecko_btc_simple_price_eur.json.raw",
            )

            result = build_raw_btc_public_data_normalizer_result(root=temp_dir)

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.signal_ready)
            self.assertFalse(result.signal_written)
            self.assertFalse(result.recommendation_quality_current_data)
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)
            self.assertIn("2026-06-17", result.selected_raw_file)
            self.assertIsNotNone(result.btc_signal)
            assert result.btc_signal is not None
            self.assertEqual(result.btc_signal.price_eur, 56569.0)

    def test_can_write_normalized_signal_only_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._write_raw(
                temp_dir,
                {
                    "bitcoin": {
                        "eur": 56569,
                        "eur_market_cap": 1133363561099.5803,
                        "eur_24h_vol": 22777201329.998524,
                        "eur_24h_change": -1.036540118449373,
                        "last_updated_at": 1781654676,
                    }
                },
            )

            result = build_raw_btc_public_data_normalizer_result(root=temp_dir, write_local_signal=True)

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.signal_written)
            self.assertTrue(result.normalized_signal_file)
            output = Path(result.normalized_signal_file)
            self.assertTrue(output.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["candidate_id"], "btc")
            self.assertEqual(payload["price_eur"], 56569.0)
            self.assertTrue(payload["raw_data_unverified"])

    def test_blocks_normalized_signal_write_outside_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._write_raw(
                temp_dir,
                {
                    "bitcoin": {
                        "eur": 56569,
                        "eur_market_cap": 1133363561099.5803,
                        "eur_24h_vol": 22777201329.998524,
                        "eur_24h_change": -1.036540118449373,
                        "last_updated_at": 1781654676,
                    }
                },
            )

            result = build_raw_btc_public_data_normalizer_result(
                root=temp_dir,
                normalized_directory="outputs/not_allowed",
                write_local_signal=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.signal_ready)
            self.assertFalse(result.signal_written)
            self.assertTrue(any("jarvis/local" in blocker for blocker in result.blockers))
            self.assertFalse(result.allocation_mutation)
            self.assertTrue(result.no_trades_executed)

    def test_invalid_payload_blocks_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_file = self._write_raw(temp_dir, {"bitcoin": {"eur": -1}})

            signal, blockers, warnings = normalize_coingecko_btc_raw(raw_file)

            self.assertIsNone(signal)
            self.assertTrue(any("positive" in blocker for blocker in blockers))
            self.assertTrue(any("market cap" in blocker for blocker in blockers))
            self.assertFalse(warnings)

    def test_missing_raw_file_blocks_normalizer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = build_raw_btc_public_data_normalizer_result(root=temp_dir)

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.raw_file_found)
            self.assertFalse(result.signal_ready)
            self.assertTrue(any("No raw BTC public data file" in blocker for blocker in result.blockers))
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.no_trades_executed)


if __name__ == "__main__":
    unittest.main()
