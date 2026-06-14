import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_allocation_optimizer import (
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    STATUS_READY,
    propose_dynamic_allocation,
)


POLICY = "jarvis/data/portfolio_policy.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, sleeve: str, asset_type: str = "ETF", risk_level: str = "medium") -> dict:
    asset = {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": asset_type,
        "sleeve": sleeve,
        "ticker": asset_id,
        "isin_or_symbol": asset_id,
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "approved_investable",
        "risk_level": risk_level,
    }
    if asset_type == "ETF":
        asset.update(
            {
                "provider": "Provider",
                "index_tracked": "Index",
                "replication_method": "physical",
            }
        )
    if asset_type == "crypto":
        asset.update(
            {
                "network_or_protocol": "Protocol",
                "custody_platforms": ["LHV Crypto Investments"],
                "transferable": False,
                "mica_route_possible": True,
            }
        )
    return asset


def _registry() -> Path:
    return _write_json(
        {
            "assets": [
                _asset("CORE", "global_core"),
                _asset("GROWTH", "growth_innovation", risk_level="high"),
                _asset("QUALITY", "quality_factor"),
                _asset("BTC", "crypto_core", "crypto", risk_level="high"),
                _asset("SPEC", "speculative_crypto", "crypto", risk_level="very_high"),
            ]
        }
    )


def _price_series(asset_id: str, start: float = 100.0, step: float = 2.0) -> dict:
    dates = [
        "2025-06-01",
        "2025-07-01",
        "2025-08-01",
        "2025-09-01",
        "2025-10-01",
        "2025-11-01",
        "2025-12-01",
        "2026-01-01",
        "2026-02-01",
        "2026-03-01",
        "2026-04-01",
        "2026-05-01",
        "2026-06-01",
    ]
    prices = [{"date": date, "close": start + index * step} for index, date in enumerate(dates)]
    return {"asset_id": asset_id, "currency": "EUR", "prices": prices}


def _market_data(asset_ids: list[str]) -> Path:
    return _write_json(
        {
            "as_of": "2026-06-04",
            "base_currency": "EUR",
            "series": [_price_series(asset_id) for asset_id in asset_ids],
        }
    )


class DynamicAllocationOptimizerTests(unittest.TestCase):
    def test_no_market_data_is_partial_safe(self) -> None:
        result = propose_dynamic_allocation("20y", POLICY, _registry())

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertAlmostEqual(sum(result.proposed_targets.values()), 1.0, places=5)
        self.assertTrue(any("no market data path supplied" in warning for warning in result.warnings))

    def test_mismatched_market_data_is_partial_safe(self) -> None:
        result = propose_dynamic_allocation(
            "20y",
            POLICY,
            _registry(),
            _market_data(["NOT_APPROVED"]),
        )

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertTrue(any("no matching approved asset IDs" in warning for warning in result.warnings))
        self.assertTrue(any("without matching approved-asset" in reason for reason in result.reasons))

    def test_complete_matching_market_data_can_be_ready_safe(self) -> None:
        approved_ids = ["CORE", "GROWTH", "QUALITY", "BTC", "SPEC"]
        result = propose_dynamic_allocation(
            "20y",
            POLICY,
            _registry(),
            _market_data(approved_ids),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.risk_metric_count, len(approved_ids))
        self.assertFalse(result.blockers)
        self.assertAlmostEqual(sum(result.proposed_targets.values()), 1.0, places=5)
        self.assertTrue(any("complete approved-asset" in reason for reason in result.reasons))

    def test_unknown_horizon_blocks_safely(self) -> None:
        result = propose_dynamic_allocation("99y", POLICY, _registry())

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("horizon must be one of" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
