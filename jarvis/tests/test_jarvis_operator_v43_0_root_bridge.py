from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV430Tests(unittest.TestCase):
    def test_root_operator_points_to_v43_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v43_0_free_research_api_router_weekly_policy")


if __name__ == "__main__":
    unittest.main()