import unittest

from jarvis.jarvis_public_asset_universe_fetch_dry_run_planner import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_source_fetch_dry_run_plan,
    compute_fetch_order,
    evaluate_public_asset_universe_fetch_dry_run,
    load_json,
    validate_fetch_dry_run_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_fetch_dry_run_planner.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_asset_universe_fetch_dry_run_planner.synthetic_complete.json"


def _complete_data():
    return load_json(SYNTHETIC_COMPLETE)


class PublicAssetUniverseFetchDryRunPlannerTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_public_asset_universe_fetch_dry_run(load_json(DEFAULT_CONFIG))

        self.assertIn(
            result.status,
            {
                "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE",
                "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_PARTIAL_SAFE",
            },
        )
        self.assertTrue(result.no_fetch_executed)
        self.assertTrue(result.no_cache_written)
        self.assertTrue(result.no_network_called)

    def test_synthetic_complete_returns_ready(self) -> None:
        result = evaluate_public_asset_universe_fetch_dry_run(_complete_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_READY_SAFE")
        self.assertGreater(result.eligible_count, 0)
        self.assertGreater(result.manual_reference_only_count, 0)
        self.assertEqual(result.blocked_count, 0)

    def test_source_dry_run_plans_are_generated_for_safe_sources(self) -> None:
        result = evaluate_public_asset_universe_fetch_dry_run(_complete_data())

        self.assertEqual(result.source_count, 7)
        self.assertEqual(len(result.source_plans), 7)
        self.assertTrue(result.planned_raw_cache_paths)

    def test_eligible_manual_and_blocked_statuses(self) -> None:
        data = _complete_data()
        eligible_plan = build_source_fetch_dry_run_plan(data["source_manifest"]["sources"][0], data["planned_cache_policy"])
        manual_plan = build_source_fetch_dry_run_plan(data["source_manifest"]["sources"][4], data["planned_cache_policy"])
        blocked_source = dict(data["source_manifest"]["sources"][0])
        blocked_source["credentials_allowed"] = True
        blocked_plan = build_source_fetch_dry_run_plan(blocked_source, data["planned_cache_policy"])

        self.assertEqual(eligible_plan.eligibility_status, "FETCH_DRY_RUN_ELIGIBLE_SAFE")
        self.assertEqual(manual_plan.eligibility_status, "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE")
        self.assertEqual(blocked_plan.eligibility_status, "FETCH_DRY_RUN_BLOCKED_SAFE")

    def test_authorization_policy_enforced_without_fetching(self) -> None:
        data = _complete_data()
        data["authorization_policy"]["authorization_phrase_present"] = True
        data["authorization_policy"]["authorization_phrase_valid"] = True

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")
        self.assertTrue(result.no_fetch_executed)

    def test_even_if_authorized_false_blocks(self) -> None:
        data = _complete_data()
        data["authorization_policy"]["even_if_authorized_this_stage_still_does_not_fetch"] = False

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")

    def test_default_fetch_allowed_true_blocks(self) -> None:
        data = _complete_data()
        data["authorization_policy"]["default_fetch_allowed"] = True

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")

    def test_missing_source_manifest_blocks(self) -> None:
        data = _complete_data()
        data.pop("source_manifest")

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")

    def test_planned_cache_path_outside_local_blocks(self) -> None:
        data = _complete_data()
        data["planned_cache_policy"]["planned_paths"][0] = "jarvis\\data\\public_asset_universe\\raw\\"

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")

    def test_source_security_flags_block(self) -> None:
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
                data["source_manifest"]["sources"][0][field] = value
                result = evaluate_public_asset_universe_fetch_dry_run(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_PARTIAL_SAFE")
                self.assertGreater(result.blocked_count, 0)

    def test_unsupported_source_type_and_fetch_method_block(self) -> None:
        for field, value in (
            ("source_type", "broker_api"),
            ("allowed_future_fetch_method", "authenticated_api"),
        ):
            with self.subTest(field=field):
                data = _complete_data()
                data["source_manifest"]["sources"][0][field] = value
                result = evaluate_public_asset_universe_fetch_dry_run(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_PARTIAL_SAFE")

    def test_source_url_safety_blocks(self) -> None:
        cases = (
            ("file:///tmp/source.csv", "Safe Name"),
            ("http://localhost/source.csv", "Safe Name"),
            ("https://example.com/source.csv?token=abc", "Safe Name"),
            ("https://example.com/source.csv", "Lightyear source"),
            ("https://lhv.example.com/source.csv", "Safe Name"),
        )
        for url, name in cases:
            with self.subTest(url=url, name=name):
                data = _complete_data()
                data["source_manifest"]["sources"][0]["source_url"] = url
                data["source_manifest"]["sources"][0]["source_name"] = name
                result = evaluate_public_asset_universe_fetch_dry_run(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_PARTIAL_SAFE")

    def test_fetch_order_is_deterministic(self) -> None:
        result = evaluate_public_asset_universe_fetch_dry_run(_complete_data())

        self.assertEqual(
            result.fetch_order,
            (
                "market_reference_source",
                "identifier_mapping_source",
                "equity_universe_source",
                "etf_universe_source",
                "fund_etp_universe_source",
                "market_data_source",
                "crypto_reference_source",
            ),
        )
        self.assertEqual(result.fetch_order, compute_fetch_order(result.source_plans))

    def test_planned_paths_are_deterministic(self) -> None:
        result = evaluate_public_asset_universe_fetch_dry_run(_complete_data())

        self.assertIn("jarvis\\local\\public_asset_universe\\raw\\equity_universe_source.raw.csv", result.planned_raw_cache_paths)
        self.assertIn("jarvis\\local\\public_asset_universe\\metadata\\etf_universe_source.metadata.json", result.planned_metadata_paths)
        self.assertIn("jarvis\\local\\public_asset_universe\\fetch_plans\\etf_universe_source.fetch_plan.json", result.planned_fetch_plan_paths)

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_fetch_dry_run_config(data))

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_fetch_dry_run_config(data))

    def test_next_manual_action_no_manual_asset_entry_required_is_accepted(self) -> None:
        data = _complete_data()
        data["next_manual_action"] = "no_manual_asset_entry_required"

        result = evaluate_public_asset_universe_fetch_dry_run(data)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_READY_SAFE")

    def test_blocked_next_manual_actions(self) -> None:
        for action in (
            "execute_fetch_now",
            "manually_enter_every_asset",
            "broker_integration",
            "credential_setup",
            "allocation_recommendation",
            "trade_execution",
        ):
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                result = evaluate_public_asset_universe_fetch_dry_run(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE")


if __name__ == "__main__":
    unittest.main()
