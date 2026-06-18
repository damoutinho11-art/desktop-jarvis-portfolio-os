from __future__ import annotations

from pathlib import Path
import unittest


PRODUCT_MODE_SOURCE = Path("jarvis/runtime/product_mode_operator.py").read_text(encoding="utf-8")
OPERATOR_SOURCE = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")


class JarvisV920ProductModeInstrumentSelectorIntegrationTests(unittest.TestCase):
    def test_product_mode_status_strings_are_v92(self) -> None:
        self.assertIn(
            "JARVIS_V92_0_PRODUCT_MODE_INSTRUMENT_SELECTOR_INTEGRATION_READY_SAFE",
            PRODUCT_MODE_SOURCE,
        )
        self.assertIn(
            "JARVIS_V92_0_PRODUCT_MODE_INSTRUMENT_SELECTOR_INTEGRATION_REVIEW_REQUIRED_SAFE",
            PRODUCT_MODE_SOURCE,
        )

    def test_week_mode_wires_multi_candidate_selector(self) -> None:
        self.assertIn("build_multi_candidate_instrument_selector_result", PRODUCT_MODE_SOURCE)
        self.assertIn("Selected manual instruments:", PRODUCT_MODE_SOURCE)
        self.assertIn("Instrument selector active:", PRODUCT_MODE_SOURCE)
        self.assertIn("for lane in (", PRODUCT_MODE_SOURCE)
        self.assertIn('"crypto"', PRODUCT_MODE_SOURCE)
        self.assertIn('"etf_fund"', PRODUCT_MODE_SOURCE)
        self.assertIn('"individual_stock"', PRODUCT_MODE_SOURCE)

    def test_operator_surface_is_v92_product_integration(self) -> None:
        self.assertIn('ACTIVE_RUNTIME_STAGE = "v92.0"', OPERATOR_SOURCE)
        self.assertIn(
            'CURRENT_OPERATOR_SURFACE = "product_mode_instrument_selector_integration"',
            OPERATOR_SOURCE,
        )

    def test_no_execution_language_was_removed(self) -> None:
        self.assertIn("J.A.R.V.I.S. creates no orders", PRODUCT_MODE_SOURCE)
        self.assertIn("manual-only", PRODUCT_MODE_SOURCE)
        self.assertIn("no broker, credentials, order, trade, or auto-approval path is enabled", PRODUCT_MODE_SOURCE)


if __name__ == "__main__":
    unittest.main()
