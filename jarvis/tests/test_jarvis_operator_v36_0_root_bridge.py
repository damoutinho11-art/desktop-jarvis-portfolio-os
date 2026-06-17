from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV360Tests(unittest.TestCase):
    def test_root_operator_points_to_v36_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v36_0_autonomous_daily_refresh_action_brief")


if __name__ == "__main__":
    unittest.main()