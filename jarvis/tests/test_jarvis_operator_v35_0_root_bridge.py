from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV350Tests(unittest.TestCase):
    def test_root_operator_points_to_v35_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v35_0_selected_stock_fund_etf_instrument_ticket_bridge")


if __name__ == "__main__":
    unittest.main()