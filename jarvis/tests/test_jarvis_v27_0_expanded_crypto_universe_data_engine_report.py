from __future__ import annotations

import unittest
from unittest.mock import patch

from jarvis.jarvis_v27_0_expanded_crypto_universe_data_engine_report import main


class JarvisV270ExpandedCryptoUniverseDataEngineReportTests(unittest.TestCase):
    def test_report_smoke_runs_without_execution(self) -> None:
        with patch("sys.argv", ["report", "--current-date", "2026-06-17"]):
            exit_code = main([])

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()