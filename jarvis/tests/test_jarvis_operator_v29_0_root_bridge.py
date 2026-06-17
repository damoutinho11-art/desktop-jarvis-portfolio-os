from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV290Tests(unittest.TestCase):
    def test_root_operator_points_to_v29_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v29_0_expanded_crypto_allocation_eligibility_bridge")


if __name__ == "__main__":
    unittest.main()