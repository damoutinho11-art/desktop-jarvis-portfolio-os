from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV420Tests(unittest.TestCase):
    def test_root_operator_points_to_v42_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v42_0_three_lane_daily_action_brief")


if __name__ == "__main__":
    unittest.main()