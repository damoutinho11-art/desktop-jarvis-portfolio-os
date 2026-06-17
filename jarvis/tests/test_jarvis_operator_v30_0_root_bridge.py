from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV300Tests(unittest.TestCase):
    def test_root_operator_points_to_v30_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v30_0_expanded_crypto_approval_ticket_refresh")


if __name__ == "__main__":
    unittest.main()