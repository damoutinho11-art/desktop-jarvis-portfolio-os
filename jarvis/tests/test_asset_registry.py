import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import AssetRegistryError, load_asset_registry, registry_summary


def _write_registry(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _etf_asset(**overrides) -> dict:
    asset = {
        "asset_id": "quality_candidate",
        "name": "Quality candidate",
        "asset_type": "ETF",
        "sleeve": "quality_etf",
        "ticker": "QETF",
        "isin_or_symbol": "IE00TEST0001",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "candidate_unreviewed",
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Quality Index",
        "replication_method": "physical",
    }
    asset.update(overrides)
    return asset


def _crypto_asset(**overrides) -> dict:
    asset = {
        "asset_id": "btc_candidate",
        "name": "Bitcoin candidate",
        "asset_type": "crypto",
        "sleeve": "btc",
        "ticker": "BTC",
        "isin_or_symbol": "BTC",
        "platforms": ["LHV Crypto Investments"],
        "currency": "EUR",
        "domicile": "not_applicable",
        "distribution_policy": "not_applicable",
        "ter_or_fee": 0.0,
        "data_source": "manual_test",
        "approval_status": "test_position",
        "risk_level": "high",
        "network_or_protocol": "Bitcoin",
        "custody_platforms": ["LHV Crypto Investments"],
        "transferable": False,
        "mica_route_possible": True,
    }
    asset.update(overrides)
    return asset


class AssetRegistryTests(unittest.TestCase):
    def test_valid_registry_loads_and_summarizes(self) -> None:
        registry = load_asset_registry(_write_registry({"assets": [_etf_asset(), _crypto_asset()]}))
        summary = registry_summary(registry)

        self.assertEqual(len(registry.assets), 2)
        self.assertEqual(summary["asset_type"], {"ETF": 1, "crypto": 1})
        self.assertEqual(summary["approval_status"], {"candidate_unreviewed": 1, "test_position": 1})

    def test_duplicate_asset_id_is_rejected(self) -> None:
        payload = {"assets": [_etf_asset(), _crypto_asset(asset_id="quality_candidate")]}

        with self.assertRaisesRegex(AssetRegistryError, "duplicate asset_id quality_candidate"):
            load_asset_registry(_write_registry(payload))

    def test_invalid_approval_status_is_rejected(self) -> None:
        payload = {"assets": [_etf_asset(approval_status="secretly_approved")]}

        with self.assertRaisesRegex(AssetRegistryError, "approval_status secretly_approved is invalid"):
            load_asset_registry(_write_registry(payload))

    def test_etf_missing_required_field_is_rejected(self) -> None:
        asset = _etf_asset()
        del asset["index_tracked"]

        with self.assertRaisesRegex(AssetRegistryError, "missing required field index_tracked"):
            load_asset_registry(_write_registry({"assets": [asset]}))

    def test_crypto_missing_required_field_is_rejected(self) -> None:
        asset = _crypto_asset()
        del asset["custody_platforms"]

        with self.assertRaisesRegex(AssetRegistryError, "missing required field custody_platforms"):
            load_asset_registry(_write_registry({"assets": [asset]}))

    def test_negative_fee_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssetRegistryError, "ter_or_fee must be non-negative"):
            load_asset_registry(_write_registry({"assets": [_etf_asset(ter_or_fee=-0.1)]}))

    def test_non_eur_currency_warns(self) -> None:
        registry = load_asset_registry(_write_registry({"assets": [_etf_asset(currency="USD")]}))

        self.assertEqual(registry.warnings[0].code, "non_eur_currency")


if __name__ == "__main__":
    unittest.main()
