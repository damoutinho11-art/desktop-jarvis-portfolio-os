import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v20_0_btc_public_signal_source_quality_gate import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_btc_public_signal_source_quality_gate_result,
)


class JarvisV200BtcPublicSignalSourceQualityGateTests(unittest.TestCase):
    def _write_signal(
        self,
        root: str,
        payload: dict,
        filename: str = "2026-06-17_coingecko_btc_simple_price_eur.normalized.json",
    ) -> Path:
        signal_dir = Path(root) / "jarvis" / "local" / "public_data" / "v19_normalized"
        signal_dir.mkdir(parents=True, exist_ok=True)
        path = signal_dir / filename
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _valid_signal(self) -> dict:
        return {
            "as_of": "2026-06-17",
            "candidate_id": "btc",
            "change_24h_pct": -1.22036404,
            "market_cap_eur": 1133363561099.5803,
            "normalized_public_signal": True,
            "price_eur": 56545.0,
            "provider_last_updated_at": 1781655053,
            "provider_last_updated_utc": "2026-06-17T00:10:53+00:00",
            "raw_data_unverified": True,
            "ready_for_source_quality_gate": True,
            "source_file": "jarvis/local/public_data/v10_raw/2026-06-17_coingecko_btc_simple_price_eur.json.raw",
            "source_id": "coingecko_btc_simple_price_eur",
            "volume_24h_eur": 22234807893.14144,
        }

    def test_fresh_valid_signal_passes_quality_gate_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._write_signal(temp_dir, self._valid_signal())
            result = build_btc_public_signal_source_quality_gate_result(
                root=temp_dir,
                current_date="2026-06-17",
            )
            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.source_quality_ready)
            self.assertEqual(result.signal_age_days, 0)
            self.assertEqual(result.candidate_id, "btc")
            self.assertEqual(result.source_id, "coingecko_btc_simple_price_eur")
            self.assertEqual(result.price_eur, 56545.0)
            self.assertFalse(result.recommendation_quality_current_data)
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_stale_signal_blocks_quality_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signal = self._valid_signal()
            signal["as_of"] = "2026-06-14"
            self._write_signal(temp_dir, signal, filename="2026-06-14_coingecko_btc_simple_price_eur.normalized.json")
            result = build_btc_public_signal_source_quality_gate_result(
                root=temp_dir,
                current_date="2026-06-17",
                max_signal_age_days=1,
            )
            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.source_quality_ready)
            self.assertEqual(result.signal_age_days, 3)
            self.assertTrue(any("stale" in blocker for blocker in result.blockers))
            self.assertFalse(result.allocation_mutation)
            self.assertTrue(result.no_trades_executed)

    def test_missing_signal_blocks_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = build_btc_public_signal_source_quality_gate_result(root=temp_dir, current_date="2026-06-17")
            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertFalse(result.signal_file_found)
            self.assertTrue(any("No normalized BTC public signal" in blocker for blocker in result.blockers))
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.no_trades_executed)

    def test_out_of_range_price_blocks_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signal = self._valid_signal()
            signal["price_eur"] = 5.0
            self._write_signal(temp_dir, signal)
            result = build_btc_public_signal_source_quality_gate_result(root=temp_dir, current_date="2026-06-17")
            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("price_eur" in blocker for blocker in result.blockers))
            self.assertFalse(result.source_quality_ready)

    def test_extreme_change_blocks_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signal = self._valid_signal()
            signal["change_24h_pct"] = 91.0
            self._write_signal(temp_dir, signal)
            result = build_btc_public_signal_source_quality_gate_result(root=temp_dir, current_date="2026-06-17")
            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("24h change" in blocker for blocker in result.blockers))
            self.assertFalse(result.source_quality_ready)

    def test_selects_latest_normalized_signal_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            older = self._valid_signal()
            older["as_of"] = "2026-06-16"
            older["price_eur"] = 56000.0
            self._write_signal(temp_dir, older, filename="2026-06-16_coingecko_btc_simple_price_eur.normalized.json")
            newer = self._valid_signal()
            newer["as_of"] = "2026-06-17"
            newer["price_eur"] = 56545.0
            self._write_signal(temp_dir, newer, filename="2026-06-17_coingecko_btc_simple_price_eur.normalized.json")
            result = build_btc_public_signal_source_quality_gate_result(root=temp_dir, current_date="2026-06-17")
            self.assertEqual(result.status, STATUS_READY)
            self.assertIn("2026-06-17", result.selected_signal_file)
            self.assertEqual(result.price_eur, 56545.0)

    def test_signal_directory_must_remain_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = build_btc_public_signal_source_quality_gate_result(
                root=temp_dir,
                signal_directory="outputs/not_allowed",
                current_date="2026-06-17",
            )
            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("jarvis/local" in blocker for blocker in result.blockers))
            self.assertFalse(result.source_quality_ready)
            self.assertFalse(result.allocation_mutation)


if __name__ == "__main__":
    unittest.main()