import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_public_data_fetcher import AUTHORIZATION_PHRASE
from jarvis.jarvis_v10_0_autonomous_public_data_refresh_runtime import (
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v10_0_autonomous_public_data_refresh_runtime,
    build_demo_public_data_source_manifest,
)


def _valid_manifest():
    return {
        "title": "Synthetic public source manifest",
        "version": "test",
        "update_frequency": "daily",
        "sources": [
            {
                "source_id": "synthetic_public_json",
                "candidate_id": "btc_candidate",
                "display_name": "Synthetic public JSON",
                "source_type": "public_market_data_json",
                "source_url": "https://example.org/public/market.json",
                "update_frequency": "daily",
                "public_source_only": True,
                "requires_authentication": False,
                "requires_credentials": False,
                "broker_or_trading_api": False,
                "contains_private_data": False,
                "expected_content_type": "application/json",
            }
        ],
    }


class JarvisV100AutonomousPublicDataRefreshRuntimeTests(unittest.TestCase):
    def test_default_runtime_contract_is_ready_without_fetching(self) -> None:
        result = audit_v10_0_autonomous_public_data_refresh_runtime()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.runtime_contract_ready)
        self.assertTrue(result.source_manifest_loaded or result.demo_manifest_used)
        self.assertFalse(result.execute_fetch_requested)
        self.assertFalse(result.raw_public_data_refreshed)
        self.assertTrue(result.ready_for_downstream_normalization)
        self.assertFalse(result.ready_for_downstream_source_quality_gate)
        self.assertFalse(result.recommendation_quality_current_data)
        self.assertGreaterEqual(result.source_count, 1)
        self.assertGreaterEqual(result.valid_source_count, 1)
        self.assertEqual(result.blocked_source_count, 0)
        self.assertFalse(result.blockers)

        if result.source_manifest_loaded and not result.demo_manifest_used:
            self.assertTrue(result.autonomous_refresh_ready)

    def test_supplied_manifest_is_ready_for_autonomous_refresh_plan(self) -> None:
        result = audit_v10_0_autonomous_public_data_refresh_runtime(manifest=_valid_manifest())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.source_manifest_loaded)
        self.assertFalse(result.demo_manifest_used)
        self.assertTrue(result.autonomous_refresh_ready)
        self.assertEqual(result.fetcher_overall_status, "PUBLIC_DATA_FETCHER_PLAN_READY_SAFE")
        self.assertEqual(result.update_plan_count, 1)
        self.assertEqual(result.valid_source_count, 1)
        self.assertFalse(result.blockers)

    def test_authorized_fetch_writes_only_local_cache_with_injected_fetcher(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = audit_v10_0_autonomous_public_data_refresh_runtime(
                manifest=_valid_manifest(),
                execute_fetch=True,
                authorization_phrase=AUTHORIZATION_PHRASE,
                fetch_date="2026-06-16",
                fetch_func=lambda url: b'{"ok": true}',
                root=temp_dir,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.raw_public_data_refreshed)
            self.assertTrue(result.ready_for_downstream_source_quality_gate)
            self.assertEqual(result.fetched_file_count, 1)
            self.assertIn("jarvis", result.fetched_files[0])
            self.assertTrue(Path(result.fetched_files[0]).is_file())
            self.assertFalse(result.recommendation_quality_current_data)
            self.assertTrue(result.local_cache_only)
            self.assertTrue(result.raw_data_unverified)
            self.assertTrue(result.no_trades_executed)

    def test_execute_fetch_without_authorization_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = audit_v10_0_autonomous_public_data_refresh_runtime(
                manifest=_valid_manifest(),
                execute_fetch=True,
                authorization_phrase="",
                fetch_func=lambda url: b"should not write",
                root=temp_dir,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertEqual(result.fetched_file_count, 0)
            self.assertTrue(any("authorization phrase" in blocker.lower() for blocker in result.blockers))

    def test_unsafe_broker_or_private_source_blocks(self) -> None:
        manifest = _valid_manifest()
        manifest["sources"][0]["source_url"] = "https://broker.example.org/account/private"
        manifest["sources"][0]["broker_or_trading_api"] = True
        manifest["sources"][0]["contains_private_data"] = True

        result = audit_v10_0_autonomous_public_data_refresh_runtime(manifest=manifest)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertGreater(result.blocked_source_count, 0)
        self.assertTrue(any("broker" in blocker.lower() for blocker in result.blockers))
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.private_account_data_ingestion_forbidden)
        self.assertTrue(result.credentials_forbidden)

    def test_safety_flags_preserve_manual_final_buy_only(self) -> None:
        payload = audit_v10_0_autonomous_public_data_refresh_runtime(
            manifest=build_demo_public_data_source_manifest()
        ).to_dict()

        self.assertTrue(payload["source_selection_not_repeated"])
        self.assertTrue(payload["dry_run_planner_not_rebuilt"])
        self.assertTrue(payload["provider_registry_not_rebuilt"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])
        self.assertTrue(payload["private_account_data_ingestion_forbidden"])
        self.assertTrue(payload["credentials_forbidden"])

    def test_local_manifest_with_utf8_bom_loads_safely(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "public_data_sources.local.json"
            manifest_path.write_text("\ufeff" + json.dumps(_valid_manifest()), encoding="utf-8")

            result = audit_v10_0_autonomous_public_data_refresh_runtime(
                manifest_path=manifest_path,
                root=temp_dir,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.source_manifest_loaded)
            self.assertFalse(result.demo_manifest_used)
            self.assertEqual(result.valid_source_count, 1)
            self.assertFalse(result.blockers)

    def test_public_fetch_failure_is_reported_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            def failing_fetch(url: str) -> bytes:
                raise RuntimeError("HTTP 404 synthetic failure")

            result = audit_v10_0_autonomous_public_data_refresh_runtime(
                manifest=_valid_manifest(),
                execute_fetch=True,
                authorization_phrase=AUTHORIZATION_PHRASE,
                fetch_date="2026-06-17",
                fetch_func=failing_fetch,
                root=temp_dir,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertEqual(result.fetcher_overall_status, "PUBLIC_DATA_FETCHER_FETCH_FAILED_SAFE")
            self.assertEqual(result.fetched_file_count, 0)
            self.assertFalse(result.raw_public_data_refreshed)
            self.assertFalse(result.ready_for_downstream_source_quality_gate)
            self.assertTrue(any("public fetch failed" in blocker.lower() for blocker in result.blockers))
            self.assertTrue(result.local_cache_only)
            self.assertTrue(result.raw_data_unverified)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.order_placement_forbidden)
            self.assertTrue(result.no_trades_executed)


if __name__ == "__main__":
    unittest.main()
