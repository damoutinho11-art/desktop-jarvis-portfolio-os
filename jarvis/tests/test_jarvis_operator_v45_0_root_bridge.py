from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV450Tests(unittest.TestCase):
    def test_root_operator_points_to_v45_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge")


if __name__ == "__main__":
    unittest.main()