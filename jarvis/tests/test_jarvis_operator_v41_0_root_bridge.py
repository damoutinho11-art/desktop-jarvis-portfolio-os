from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV410Tests(unittest.TestCase):
    def test_root_operator_points_to_v41_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge")


if __name__ == "__main__":
    unittest.main()