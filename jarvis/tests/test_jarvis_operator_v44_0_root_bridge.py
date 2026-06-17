from __future__ import annotations

import unittest

import jarvis_operator


class JarvisRootOperatorV440Tests(unittest.TestCase):
    def test_root_operator_points_to_v44_daily_operator(self) -> None:
        self.assertEqual(jarvis_operator.main.__module__, "jarvis.jarvis_v44_0_free_research_api_fetcher_adapters_local_cache")


if __name__ == "__main__":
    unittest.main()