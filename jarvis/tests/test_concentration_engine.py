import unittest

from jarvis.concentration_engine import (
    calculate_combined_top_holdings,
    calculate_country_exposure,
    calculate_largest_single_holding_exposure,
    calculate_pairwise_holding_overlap,
    calculate_sector_exposure,
    generate_concentration_warnings,
)
from jarvis.exposure_loader import AssetExposure, ExposureHolding


def _asset(
    asset_id: str,
    holdings: list[tuple[str, float]],
    countries: dict[str, float] | None = None,
    sectors: dict[str, float] | None = None,
) -> AssetExposure:
    return AssetExposure(
        asset_id,
        tuple(ExposureHolding(name, weight) for name, weight in holdings),
        countries or {},
        sectors or {},
    )


class ConcentrationEngineTests(unittest.TestCase):
    def test_pairwise_overlap_calculation(self) -> None:
        asset_a = _asset("a", [("Company A", 0.10), ("Company B", 0.05)])
        asset_b = _asset("b", [(" company a ", 0.06), ("Company C", 0.04)])

        self.assertEqual(calculate_pairwise_holding_overlap(asset_a, asset_b), 0.06)

    def test_combined_top_holdings_calculation(self) -> None:
        exposures = {
            "a": _asset("a", [("Company A", 0.20)]),
            "b": _asset("b", [("Company A", 0.10), ("Company B", 0.10)]),
        }

        holdings = calculate_combined_top_holdings({"a": 0.50, "b": 0.50}, exposures)

        self.assertEqual(holdings[0], ("company a", 0.15))
        self.assertEqual(holdings[1], ("company b", 0.05))

    def test_country_exposure_calculation(self) -> None:
        exposures = {
            "a": _asset("a", [], {"US": 0.60}),
            "b": _asset("b", [], {"US": 0.20, "IE": 0.50}),
        }

        countries = calculate_country_exposure({"a": 0.50, "b": 0.50}, exposures)

        self.assertEqual(countries["US"], 0.40)
        self.assertEqual(countries["IE"], 0.25)

    def test_sector_exposure_calculation(self) -> None:
        exposures = {
            "a": _asset("a", [], sectors={"Technology": 0.40}),
            "b": _asset("b", [], sectors={"Healthcare": 0.30}),
        }

        sectors = calculate_sector_exposure({"a": 0.50, "b": 0.50}, exposures)

        self.assertEqual(sectors["Technology"], 0.20)
        self.assertEqual(sectors["Healthcare"], 0.15)

    def test_largest_single_holding_warning(self) -> None:
        exposures = {"a": _asset("a", [("Company A", 0.30)])}

        warnings = generate_concentration_warnings({"a": 0.50}, exposures)

        self.assertTrue(any("largest single holding" in warning for warning in warnings))

    def test_top_10_concentration_warning(self) -> None:
        exposures = {
            "a": _asset(
                "a",
                [(f"Company {index}", 0.05) for index in range(10)],
            )
        }

        warnings = generate_concentration_warnings({"a": 1.0}, exposures)

        self.assertTrue(any("top 10 combined holdings" in warning for warning in warnings))

    def test_us_exposure_warning(self) -> None:
        exposures = {"a": _asset("a", [], {"United States": 0.80})}

        warnings = generate_concentration_warnings({"a": 1.0}, exposures)

        self.assertTrue(any("US country exposure" in warning for warning in warnings))

    def test_technology_exposure_warning(self) -> None:
        exposures = {"a": _asset("a", [], sectors={"Information Technology": 0.40})}

        warnings = generate_concentration_warnings({"a": 1.0}, exposures)

        self.assertTrue(any("Technology sector exposure" in warning for warning in warnings))

    def test_largest_single_holding_exposure(self) -> None:
        exposures = {"a": _asset("a", [("Company A", 0.20), ("Company B", 0.10)])}

        largest = calculate_largest_single_holding_exposure({"a": 0.50}, exposures)

        self.assertEqual(largest, ("company a", 0.10))


if __name__ == "__main__":
    unittest.main()
