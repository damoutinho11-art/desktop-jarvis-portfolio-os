from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV340Tests(unittest.TestCase):
    def test_root_operator_points_to_v34_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver")


if __name__ == "__main__":
    unittest.main()