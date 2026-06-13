import copy
import unittest

from jarvis.jarvis_public_asset_universe_source_manifest import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_ASSET_UNIVERSES,
    REQUIRED_SOURCE_CATEGORIES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    evaluate_public_asset_universe_source_manifest,
    load_json,
    validate_source_manifest_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_source_manifest.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_asset_universe_source_manifest.synthetic_complete.example.json"
TEMPLATE = "templates/jarvis_public_asset_universe_sources.local.template.json"


def _complete_data():
    return load_json(SYNTHETIC_COMPLETE)


class PublicAssetUniverseSourceManifestTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_public_asset_universe_source_manifest(load_json(DEFAULT_CONFIG))

        self.assertIn(
            result.overall_status,
            {
                "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE",
                "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_PARTIAL_SAFE",
            },
        )
        self.assertFalse(result.network_calls)
        self.assertFalse(result.fetching)
        self.assertFalse(result.writes)

    def test_synthetic_complete_returns_ready(self) -> None:
        result = evaluate_public_asset_universe_source_manifest(_complete_data())

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_READY_SAFE")
        self.assertEqual(len(result.source_categories), 11)
        self.assertGreaterEqual(len(result.sources), 6)

    def test_required_source_categories_are_enforced(self) -> None:
        for category_id in REQUIRED_SOURCE_CATEGORIES:
            with self.subTest(category_id=category_id):
                data = _complete_data()
                data["source_categories"] = [
                    item for item in data["source_categories"] if item["source_category_id"] != category_id
                ]
                data["required_source_category_ids"] = [
                    item for item in data["required_source_category_ids"] if item != category_id
                ]
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_required_asset_universe_coverage_is_enforced(self) -> None:
        for universe_id in REQUIRED_ASSET_UNIVERSES:
            with self.subTest(universe_id=universe_id):
                data = _complete_data()
                data["required_asset_universe_ids"] = [
                    item for item in data["required_asset_universe_ids"] if item != universe_id
                ]
                data["sources"] = [
                    item
                    for item in data["sources"]
                    if universe_id not in item.get("target_asset_universes", [])
                ]
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_source_category_security_flags_block(self) -> None:
        for field in ("authentication_required", "credentials_allowed", "broker_api_allowed", "private_data_allowed", "trading_access_allowed"):
            with self.subTest(field=field):
                data = _complete_data()
                data["source_categories"][0][field] = True
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_source_entry_security_flags_block(self) -> None:
        for field, value in (
            ("public_only", False),
            ("authentication_required", True),
            ("credentials_allowed", True),
            ("broker_api_allowed", True),
            ("private_data_allowed", True),
            ("trading_access_allowed", True),
        ):
            with self.subTest(field=field):
                data = _complete_data()
                data["sources"][0][field] = value
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_source_url_safety_blocks_file_localhost_credentials_and_brokers(self) -> None:
        cases = (
            ("file:///tmp/source.csv", "Safe Name"),
            ("http://localhost/source.csv", "Safe Name"),
            ("https://example.com/source.csv?api_key=abc", "Safe Name"),
            ("https://example.com/source.csv", "Lightyear source"),
            ("https://lhv.example.com/source.csv", "Safe Name"),
            ("https://example.com/trading/orders", "Safe Name"),
        )
        for url, name in cases:
            with self.subTest(url=url, name=name):
                data = _complete_data()
                data["sources"][0]["source_url"] = url
                data["sources"][0]["source_name"] = name
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_future_fetch_policy_blocks_unsafe_values(self) -> None:
        for field, value in (
            ("default_fetch_allowed", True),
            ("future_fetch_allowed_only_with_explicit_authorization", False),
            ("local_cache_only", False),
            ("no_evidence_verification", False),
        ):
            with self.subTest(field=field):
                data = _complete_data()
                data["future_fetch_policy"][field] = value
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_identifier_policy_blocks_private_identifiers(self) -> None:
        for field in (
            "account_identifiers_allowed",
            "broker_specific_private_identifiers_allowed",
            "portfolio_identifiers_allowed",
            "user_holdings_identifiers_allowed",
        ):
            with self.subTest(field=field):
                data = _complete_data()
                data["identifier_policy"][field] = True
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_source_manifest_config(data))

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_source_manifest_config(data))

    def test_next_manual_action_no_manual_asset_entry_required_is_accepted(self) -> None:
        data = _complete_data()
        data["next_manual_action"] = "no_manual_asset_entry_required"

        result = evaluate_public_asset_universe_source_manifest(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_READY_SAFE")

    def test_blocked_next_manual_actions(self) -> None:
        for action in (
            "manually_enter_every_asset",
            "broker_integration",
            "credential_setup",
            "allocation_recommendation",
            "trade_execution",
        ):
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                result = evaluate_public_asset_universe_source_manifest(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_local_cache_policy_blocks_non_local_path(self) -> None:
        data = _complete_data()
        data["local_cache_policy"]["planned_paths"][0] = "jarvis\\data\\public_asset_universe\\"

        result = evaluate_public_asset_universe_source_manifest(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE")

    def test_template_exists_and_contains_no_credentials_or_private_claims(self) -> None:
        template = load_json(TEMPLATE)
        text = str(template).lower()

        self.assertIn("no credentials", text)
        self.assertIn("no broker urls", text)
        self.assertIn("future fetch requires explicit authorization", text)
        self.assertNotIn("api_key", text)
        self.assertNotIn("password", text)
        self.assertNotIn("private_data_allowed': true", text)


if __name__ == "__main__":
    unittest.main()
