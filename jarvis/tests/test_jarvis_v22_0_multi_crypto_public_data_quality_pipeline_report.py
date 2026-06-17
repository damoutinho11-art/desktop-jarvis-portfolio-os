from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline_report import main
from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import DEFAULT_CANDIDATES


def _write_raw(root: Path, source_id: str, coingecko_key: str, *, price: float = 10.0) -> None:
    raw_dir = root / "jarvis" / "local" / "public_data" / "v10_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        coingecko_key: {
            "eur": price,
            "eur_market_cap": 1000000.0,
            "eur_24h_vol": 100000.0,
            "eur_24h_change": 1.0,
            "last_updated_at": 1781656726,
        }
    }
    (raw_dir / f"2026-06-17_{source_id}.json.raw").write_text(json.dumps(payload), encoding="utf-8")


class JarvisV220MultiCryptoPublicDataQualityPipelineReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution_or_broker_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price)

            exit_code = main(
                [
                    "--raw-directory",
                    str(root / "jarvis" / "local" / "public_data" / "v10_raw"),
                    "--normalized-directory",
                    str(root / "jarvis" / "local" / "public_data" / "v22_multi_crypto_normalized"),
                    "--current-date",
                    "2026-06-17",
                ]
            )

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()