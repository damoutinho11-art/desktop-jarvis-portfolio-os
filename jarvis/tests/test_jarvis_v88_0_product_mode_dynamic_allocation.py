from __future__ import annotations

from pathlib import Path
import unittest


class JarvisV880ProductModeDynamicAllocationTests(unittest.TestCase):
    def test_product_mode_uses_v88_status_identity(self) -> None:
        source = Path("jarvis/runtime/product_mode_operator.py").read_text(encoding="utf-8-sig")

        self.assertTrue("JARVIS_V88_0_PRODUCT_MODE_DYNAMIC_ALLOCATION_READY_SAFE" in source or "JARVIS_V90_0_DYNAMIC_SLEEVE_SCORING_READY_SAFE" in source)
        self.assertTrue("JARVIS_V88_0_PRODUCT_MODE_DYNAMIC_ALLOCATION_REVIEW_REQUIRED_SAFE" in source or "JARVIS_V90_0_DYNAMIC_SLEEVE_SCORING_REVIEW_REQUIRED_SAFE" in source)

    def test_old_zero_stock_reason_is_removed(self) -> None:
        source = Path("jarvis/runtime/product_mode_operator.py").read_text(encoding="utf-8-sig")

        self.assertNotIn("Reason stock is zero: v83 dynamic allocator has not assigned stock sizing yet.", source)
        self.assertIn("Dynamic quality allocation active", source)

    def test_operator_surface_is_v88(self) -> None:
        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8-sig")

        self.assertIn('ACTIVE_RUNTIME_STAGE = "v90.0"', source)
        self.assertIn('CURRENT_OPERATOR_SURFACE = "dynamic_sleeve_scoring_refactor"', source)


if __name__ == "__main__":
    unittest.main()
