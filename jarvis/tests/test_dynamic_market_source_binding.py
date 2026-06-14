import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_source_binding import (
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    STATUS_READY,
    audit_dynamic_market_source_bindings,
)


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str = "CORE") -> dict:
    return {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": "ETF",
        "sleeve": "global_core",
        "ticker": asset_id,
        "isin_or_symbol": asset_id,
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "approved_investable",
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
    }


def _registry(*assets: dict) -> Path:
    return _write_json({"assets": list(assets)})


def _binding(asset_id: str = "CORE", **overrides) -> dict:
    payload = {
        "asset_id": asset_id,
        "source_provider": "manual_market_fixture",
        "source_symbol": asset_id,
        "cache_series_id": asset_id,
        "expected_currency": "EUR",
        "enabled": True,
    }
    payload.update(overrides)
    return payload


def _bindings(*bindings: dict) -> Path:
    return _write_json(
        {
            "binding_pack_id": "test_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": list(bindings),
        }
    )


class DynamicMarketSourceBindingTests(unittest.TestCase):
    def test_complete_binding_is_ready_safe(self) -> None:
        result = audit_dynamic_market_source_bindings(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE")),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.ready_binding_count, 1)
        self.assertEqual(result.missing_binding_count, 0)
        self.assertEqual(result.blocked_binding_count, 0)
        self.assertFalse(result.blockers)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_missing_binding_blocks_safely(self) -> None:
        result = audit_dynamic_market_source_bindings(
            _registry(_asset("CORE")),
            _bindings(),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.missing_binding_count, 1)
        self.assertTrue(any("no market source binding" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)

    def test_disabled_or_placeholder_binding_blocks_safely(self) -> None:
        result = audit_dynamic_market_source_bindings(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE", enabled=False, source_symbol="TODO")),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.blocked_binding_count, 1)
        self.assertTrue(any("binding is not enabled" in blocker for blocker in result.blockers))
        self.assertTrue(any("source_symbol is missing" in blocker for blocker in result.blockers))

    def test_partial_when_some_bindings_ready_and_some_missing(self) -> None:
        result = audit_dynamic_market_source_bindings(
            _registry(_asset("CORE"), _asset("GROWTH")),
            _bindings(_binding("CORE")),
        )

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertEqual(result.ready_binding_count, 1)
        self.assertEqual(result.missing_binding_count, 1)

    def test_extra_non_approved_binding_warns(self) -> None:
        result = audit_dynamic_market_source_bindings(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE"), _binding("EXTRA")),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(any("non-approved asset ids" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
