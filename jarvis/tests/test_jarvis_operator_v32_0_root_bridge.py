from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV320Tests(unittest.TestCase):
    def test_root_operator_points_to_v32_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v32_0_stock_fund_etf_data_freshness_engine")


if __name__ == "__main__":
    unittest.main()