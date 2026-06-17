from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV310Tests(unittest.TestCase):
    def test_root_operator_points_to_v31_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v31_0_approval_ticket_consumption_closeout")


if __name__ == "__main__":
    unittest.main()