from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV280Tests(unittest.TestCase):
    def test_root_operator_points_to_v28_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v28_0_expanded_crypto_ranking_daily_operator_bridge")


if __name__ == "__main__":
    unittest.main()