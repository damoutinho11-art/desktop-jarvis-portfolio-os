import copy
import unittest

from jarvis.jarvis_public_asset_universe_discovery_plan import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_SOURCE_CATEGORIES,
    REQUIRED_TARGET_UNIVERSES,
    TRUE_REQUIRED_SAFETY_FIELDS,
    evaluate_public_asset_universe_discovery_plan,
    load_json,
    validate_discovery_plan_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_discovery_plan.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_asset_universe_discovery_plan.synthetic_complete.example.json"


def _complete_data():
    return load_json(SYNTHETIC_COMPLETE)


class PublicAssetUniverseDiscoveryPlanTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_public_asset_universe_discovery_plan(load_json(DEFAULT_CONFIG))

        self.assertIn(
            result.overall_status,
            {
                "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE",
                "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_PARTIAL_SAFE",
            },
        )
        self.assertFalse(result.network_calls)
        self.assertFalse(result.fetching)
        self.assertFalse(result.writes)

    def test_synthetic_complete_returns_ready(self) -> None:
        result = evaluate_public_asset_universe_discovery_plan(_complete_data())

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_READY_SAFE")
        self.assertEqual(len(result.target_asset_universes), 5)
        self.assertEqual(len(result.public_source_categories), 7)

    def test_required_target_universes_are_enforced(self) -> None:
        for universe_id in REQUIRED_TARGET_UNIVERSES:
            with self.subTest(universe_id=universe_id):
                data = _complete_data()
                data["target_asset_universes"] = [
                    item for item in data["target_asset_universes"] if item["universe_id"] != universe_id
                ]
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_required_source_categories_are_enforced(self) -> None:
        for category_id in REQUIRED_SOURCE_CATEGORIES:
            with self.subTest(category_id=category_id):
                data = _complete_data()
                data["public_source_categories"] = [
                    item for item in data["public_source_categories"] if item["source_category_id"] != category_id
                ]
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_source_category_security_flags_block(self) -> None:
        for field in ("authentication_required", "credentials_allowed", "broker_api_allowed", "private_data_allowed"):
            with self.subTest(field=field):
                data = _complete_data()
                data["public_source_categories"][0][field] = True
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_target_universe_public_and_discovery_flags_block(self) -> None:
        for field, value in (("public_only", False), ("automated_discovery_goal", False), ("manual_entry_primary_path", True)):
            with self.subTest(field=field):
                data = _complete_data()
                data["target_asset_universes"][0][field] = value
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_human_action_boundary_blocks_execution_broker_and_credentials(self) -> None:
        for field in ("jarvis_may_execute_trade", "jarvis_may_login_to_broker", "jarvis_may_store_credentials"):
            with self.subTest(field=field):
                data = _complete_data()
                data["human_action_boundary"][field] = True
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_discovery_plan_config(data))

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_discovery_plan_config(data))

    def test_next_manual_action_no_manual_asset_entry_required_is_accepted(self) -> None:
        data = _complete_data()
        data["next_manual_action"] = "no_manual_asset_entry_required"

        result = evaluate_public_asset_universe_discovery_plan(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_READY_SAFE")

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
                result = evaluate_public_asset_universe_discovery_plan(data)
                self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_default_status_values_are_required(self) -> None:
        data = _complete_data()
        data["target_asset_universes"][0]["default_status_values"]["approval_status"] = "APPROVED"

        result = evaluate_public_asset_universe_discovery_plan(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_forbidden_screening_output_blocks(self) -> None:
        data = _complete_data()
        data["screening_plan"]["allowed_outputs"].append("BUY")

        result = evaluate_public_asset_universe_discovery_plan(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE")

    def test_stage_with_false_boundary_partials_safely(self) -> None:
        data = copy.deepcopy(_complete_data())
        data["future_build_sequence"][0]["real_new_boundary"] = False

        result = evaluate_public_asset_universe_discovery_plan(data)

        self.assertEqual(result.overall_status, "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_PARTIAL_SAFE")
        self.assertTrue(result.warnings)


if __name__ == "__main__":
    unittest.main()
