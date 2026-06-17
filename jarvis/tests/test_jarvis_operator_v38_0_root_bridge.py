from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV380Tests(unittest.TestCase):
    def test_root_operator_points_to_v38_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v38_0_individual_stock_public_universe_engine")


if __name__ == "__main__":
    unittest.main()