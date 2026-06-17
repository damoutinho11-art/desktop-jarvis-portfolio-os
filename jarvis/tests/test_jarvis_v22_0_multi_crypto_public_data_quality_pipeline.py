from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    DEFAULT_CANDIDATES,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_multi_crypto_public_data_quality_pipeline_result,
    format_multi_crypto_public_data_quality_pipeline,
)


def _write_raw(root: Path, source_id: str, coingecko_key: str, *, as_of: str = "2026-06-17", price: float = 10.0, change: float = 1.0) -> Path:
    raw_dir = root / "jarvis" / "local" / "public_data" / "v10_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{as_of}_{source_id}.json.raw"
    payload = {
        coingecko_key: {
            "eur": price,
            "eur_market_cap": 1000000.0,
            "eur_24h_vol": 100000.0,
            "eur_24h_change": change,
            "last_updated_at": 1781656726,
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class JarvisV220MultiCryptoPublicDataQualityPipelineTests(unittest.TestCase):
    def test_all_default_crypto_candidates_quality_gate_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price)

            result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.all_crypto_public_signals_ready)
            self.assertEqual(result.candidate_count, 3)
            self.assertEqual(result.source_quality_ready_count, 3)
            self.assertFalse(result.recommendation_quality_current_data)
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_writes_local_normalized_signals_only_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price)

            result = build_multi_crypto_public_data_quality_pipeline_result(
                root=root,
                current_date="2026-06-17",
                write_local_signals=True,
            )

            self.assertEqual(result.status, STATUS_READY)
            written = [item.normalized_signal_file for item in result.candidate_results]
            self.assertEqual(len([item for item in written if item]), 3)
            for path_text in written:
                self.assertIn("jarvis", path_text)
                self.assertIn("local", path_text)
                self.assertTrue(Path(path_text).exists())

    def test_missing_candidate_raw_file_causes_review_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw(root, "coingecko_btc_simple_price_eur", "bitcoin", price=56000.0)

            result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.source_quality_ready_count, 1)
            self.assertEqual(result.blocked_candidate_count, 2)
            self.assertIn("hype", " ".join(result.blockers))
            self.assertIn("tao", " ".join(result.blockers))

    def test_stale_raw_signal_blocks_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, as_of="2026-06-14", price=price)

            result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.source_quality_ready_count, 0)
            self.assertIn("stale", " ".join(result.blockers))

    def test_extreme_change_blocks_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                change = 99.0 if config.candidate_id == "hype" else 1.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price, change=change)

            result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertEqual(result.source_quality_ready_count, 2)
            self.assertIn("hype", " ".join(result.blockers))
            self.assertIn("exceeds sanity limit", " ".join(result.blockers))

    def test_raw_directory_must_remain_under_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_multi_crypto_public_data_quality_pipeline_result(
                root=root,
                raw_directory="outside",
                current_date="2026-06-17",
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertIn("raw_directory must be under ignored jarvis/local", " ".join(result.blockers))

    def test_console_output_summarizes_multi_crypto_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price)

            result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")
            output = format_multi_crypto_public_data_quality_pipeline(result)

            self.assertIn("Multi-Crypto Public Data Quality Pipeline", output)
            self.assertIn("btc", output)
            self.assertIn("hype", output)
            self.assertIn("tao", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()