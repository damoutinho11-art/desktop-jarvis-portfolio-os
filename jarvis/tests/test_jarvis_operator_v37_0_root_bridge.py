from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV370Tests(unittest.TestCase):
    def test_root_operator_points_to_v37_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v37_0_autonomous_dual_lane_daily_refresh")


if __name__ == "__main__":
    unittest.main()