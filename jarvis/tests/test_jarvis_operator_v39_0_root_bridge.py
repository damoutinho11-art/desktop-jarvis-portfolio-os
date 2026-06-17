from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV390Tests(unittest.TestCase):
    def test_root_operator_points_to_v39_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v39_0_individual_stock_public_ranker")


if __name__ == "__main__":
    unittest.main()