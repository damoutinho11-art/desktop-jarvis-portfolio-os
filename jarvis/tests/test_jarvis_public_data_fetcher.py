import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_public_data_fetcher import (
    AUTHORIZATION_PHRASE,
    evaluate_public_data_fetcher,
    fetch_public_sources,
    load_json,
    validate_source,
    validate_source_manifest,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_data_fetcher.example.json"
SYNTHETIC_PLAN = "jarvis/data/jarvis_public_data_fetcher.synthetic_plan.example.json"
TEMPLATE_MANIFEST = "templates/jarvis_public_data_sources.local.template.json"


def _safe_source(**overrides):
    source = {
        "source_id": "safe_public_csv",
        "candidate_id": "synthetic_candidate",
        "display_name": "Synthetic public source",
        "asset_type": "etf",
        "source_type": "public_reference_csv",
        "source_url": "https://example.com/reference.csv",
        "update_frequency": "daily",
        "expected_content_type": "text/csv",
        "public_source_only": True,
        "requires_authentication": False,
        "requires_credentials": False,
        "broker_or_trading_api": False,
        "contains_private_data": False,
        "intended_use": "raw_unverified_public_reference_cache_only",
        "notes": "synthetic",
    }
    source.update(overrides)
    return source


def _fetch_config(**overrides):
    config = load_json(SYNTHETIC_PLAN)
    config.update(
        {
            "dry_run_only": False,
            "execute_fetch": True,
            "write_local_cache": True,
            "authorization_phrase": AUTHORIZATION_PHRASE,
            "output_directory": "jarvis/local/public_data_snapshots",
            "fetch_date": "2026-06-12",
        }
    )
    config.update(overrides)
    return config


class PublicDataFetcherTests(unittest.TestCase):
    def test_default_config_is_plan_only_no_network_write(self) -> None:
        config = load_json(DEFAULT_CONFIG)
        manifest = load_json(TEMPLATE_MANIFEST)
        evaluation = evaluate_public_data_fetcher(config, manifest)

        self.assertEqual(evaluation.overall_status, "PUBLIC_DATA_FETCHER_PLAN_READY_SAFE")
        self.assertTrue(evaluation.dry_run_only)
        self.assertFalse(evaluation.execute_fetch)
        self.assertFalse(evaluation.write_local_cache)
        self.assertEqual(evaluation.fetched_files, ())

    def test_synthetic_plan_returns_plan_ready(self) -> None:
        evaluation = evaluate_public_data_fetcher(load_json(SYNTHETIC_PLAN))

        self.assertEqual(evaluation.overall_status, "PUBLIC_DATA_FETCHER_PLAN_READY_SAFE")
        self.assertEqual(evaluation.source_count, 2)

    def test_daily_weekly_manual_frequencies_are_accepted(self) -> None:
        for frequency in ("daily", "weekly", "manual"):
            with self.subTest(frequency=frequency):
                result = validate_source(_safe_source(update_frequency=frequency))
                self.assertTrue(result.valid)

    def test_invalid_frequency_is_blocked(self) -> None:
        result = validate_source(_safe_source(update_frequency="hourly"))

        self.assertFalse(result.valid)
        self.assertIn("update_frequency must be daily, weekly, or manual.", result.blocked_reasons)

    def test_manifest_validates_public_unauthenticated_sources(self) -> None:
        validations = validate_source_manifest({"sources": [_safe_source()]})

        self.assertEqual(len(validations), 1)
        self.assertTrue(validations[0].valid)

    def test_auth_credentials_broker_private_sources_block(self) -> None:
        cases = {
            "requires_authentication": {"requires_authentication": True},
            "requires_credentials": {"requires_credentials": True},
            "broker_or_trading_api": {"broker_or_trading_api": True},
            "contains_private_data": {"contains_private_data": True},
        }
        for name, override in cases.items():
            with self.subTest(name=name):
                self.assertFalse(validate_source(_safe_source(**override)).valid)

    def test_file_and_private_sources_block(self) -> None:
        for url in ("file:///tmp/reference.csv", "https://example.com/private/reference.csv", "C:/local/reference.csv"):
            with self.subTest(url=url):
                self.assertFalse(validate_source(_safe_source(source_url=url)).valid)

    def test_credential_query_parameters_block(self) -> None:
        for key in ("api_key", "token", "secret", "password", "auth", "credential"):
            with self.subTest(key=key):
                result = validate_source(_safe_source(source_url=f"https://example.com/reference.csv?{key}=x"))
                self.assertFalse(result.valid)
                self.assertTrue(any(key in reason for reason in result.blocked_reasons))

    def test_fetch_requires_exact_phrase_dry_run_off_and_write_enabled(self) -> None:
        manifest = {"sources": [_safe_source()]}
        cases = (
            {"authorization_phrase": "wrong"},
            {"dry_run_only": True},
            {"write_local_cache": False},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            for override in cases:
                with self.subTest(override=override):
                    result = fetch_public_sources(_fetch_config(**override), manifest, fetch_func=lambda _url: b"x", root=tmpdir)
                    self.assertNotEqual(result.overall_status, "PUBLIC_DATA_FETCHER_FETCH_COMPLETED_LOCAL_CACHE_ONLY_SAFE")
                    self.assertFalse(list(Path(tmpdir).rglob("*.raw")))

    def test_fetch_cannot_write_outside_jarvis_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = fetch_public_sources(
                _fetch_config(output_directory="jarvis/data/public_data_snapshots"),
                {"sources": [_safe_source()]},
                fetch_func=lambda _url: b"x",
                root=tmpdir,
            )

        self.assertNotEqual(result.overall_status, "PUBLIC_DATA_FETCHER_FETCH_COMPLETED_LOCAL_CACHE_ONLY_SAFE")
        self.assertTrue(any("under ignored jarvis/local" in reason for reason in result.blocked_reasons))

    def test_authorized_fetch_uses_injected_fetch_func_and_writes_temp_local_cache_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = fetch_public_sources(
                _fetch_config(),
                {"sources": [_safe_source()]},
                fetch_func=lambda url: f"raw data from {url}".encode("utf-8"),
                root=tmpdir,
            )
            files = list(Path(tmpdir).rglob("*.raw"))

        self.assertEqual(result.overall_status, "PUBLIC_DATA_FETCHER_FETCH_COMPLETED_LOCAL_CACHE_ONLY_SAFE")
        self.assertEqual(len(result.fetched_files), 1)
        self.assertEqual(len(files), 1)
        self.assertIn("jarvis", result.fetched_files[0].replace("\\", "/"))
        self.assertFalse(result.evidence_verified)
        self.assertFalse(result.registry_mutation)
        self.assertFalse(result.buy_signal)
        self.assertFalse(result.trade_executed)

    def test_safety_controls_block_unsafe_config(self) -> None:
        for field in ("registry_mutation", "candidate_registry_write", "approved_asset", "trade_executed"):
            with self.subTest(field=field):
                config = load_json(SYNTHETIC_PLAN)
                config["safety_controls"][field] = True
                result = evaluate_public_data_fetcher(config)
                self.assertEqual(result.overall_status, "PUBLIC_DATA_FETCHER_BLOCKED_SAFE")


if __name__ == "__main__":
    unittest.main()
