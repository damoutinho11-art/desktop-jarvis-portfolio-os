from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV330Tests(unittest.TestCase):
    def test_root_operator_points_to_v33_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v33_0_stock_fund_etf_public_source_fetcher")


if __name__ == "__main__":
    unittest.main()