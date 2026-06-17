from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    DEFAULT_CANDIDATES,
    build_multi_crypto_public_data_quality_pipeline_result,
)
from jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate_report import main


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


class JarvisV230CryptoLanePublicSignalSelectionGateReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for config in DEFAULT_CANDIDATES:
                price = 56000.0 if config.candidate_id == "btc" else 50.0
                _write_raw(root, config.source_id, config.coingecko_key, price=price)

            public_signal_result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")

            with patch(
                "jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate.build_multi_crypto_public_data_quality_pipeline_result",
                return_value=public_signal_result,
            ), patch(
                "jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate._load_json",
                side_effect=[
                    {"asset_routes": {"btc": "lhv_crypto", "hype": "lhv_crypto", "tao": "kraken"}},
                    {"platform_status": {"lhv_crypto_ready": True, "kraken_ready": False}},
                ],
            ), patch(
                "jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate._build_allocation_result",
                return_value={
                    "ideal_allocations_cents": {"btc": 4154, "hype": 0, "tao": 0},
                    "executable_allocations_cents": {"btc": 4154, "hype": 0, "tao": 0},
                },
            ):
                exit_code = main(["--current-date", "2026-06-17"])

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()