import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v19_0_raw_btc_public_data_normalizer import STATUS_READY
from jarvis.jarvis_v19_0_raw_btc_public_data_normalizer_report import (
    report_v19_0_raw_btc_public_data_normalizer,
)


class JarvisV190RawBtcPublicDataNormalizerReportTests(unittest.TestCase):
    def test_report_smoke_uses_local_raw_signal_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_dir = Path(temp_dir) / "jarvis" / "local" / "public_data" / "v10_raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / "2026-06-17_coingecko_btc_simple_price_eur.json.raw").write_text(
                json.dumps(
                    {
                        "bitcoin": {
                            "eur": 56569,
                            "eur_market_cap": 1133363561099.5803,
                            "eur_24h_vol": 22777201329.998524,
                            "eur_24h_change": -1.036540118449373,
                            "last_updated_at": 1781654676,
                        }
                    }
                ),
                encoding="utf-8",
            )

            report = report_v19_0_raw_btc_public_data_normalizer(root=temp_dir)

            self.assertIn(f"status: {STATUS_READY}", report)
            self.assertIn("signal ready: True", report)
            self.assertIn("price_eur", report)
            self.assertIn("56569", report)
            self.assertIn("recommendation quality current data: False", report)
            self.assertIn("allocation mutation: False", report)
            self.assertIn("buy request created: False", report)
            self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
