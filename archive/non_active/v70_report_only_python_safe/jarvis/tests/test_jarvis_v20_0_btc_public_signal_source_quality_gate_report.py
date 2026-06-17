import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v20_0_btc_public_signal_source_quality_gate import STATUS_READY
from jarvis.jarvis_v20_0_btc_public_signal_source_quality_gate_report import (
    report_v20_0_btc_public_signal_source_quality_gate,
)


class JarvisV200BtcPublicSignalSourceQualityGateReportTests(unittest.TestCase):
    def test_report_smoke_quality_gates_local_signal_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signal_dir = Path(temp_dir) / "jarvis" / "local" / "public_data" / "v19_normalized"
            signal_dir.mkdir(parents=True, exist_ok=True)
            (signal_dir / "2026-06-17_coingecko_btc_simple_price_eur.normalized.json").write_text(
                json.dumps(
                    {
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
                ),
                encoding="utf-8",
            )
            report = report_v20_0_btc_public_signal_source_quality_gate(
                root=temp_dir,
                current_date="2026-06-17",
            )
            self.assertIn(f"status: {STATUS_READY}", report)
            self.assertIn("source quality ready: True", report)
            self.assertIn("recommendation quality current data: False", report)
            self.assertIn("allocation mutation: False", report)
            self.assertIn("approval ticket mutation: False", report)
            self.assertIn("buy request created: False", report)
            self.assertIn("no trades executed: True", report)
            self.assertIn("Quality-Gated BTC Public Signal", report)


if __name__ == "__main__":
    unittest.main()