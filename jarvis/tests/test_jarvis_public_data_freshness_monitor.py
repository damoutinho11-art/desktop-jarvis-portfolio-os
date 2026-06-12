import copy
import unittest

from jarvis.jarvis_public_data_freshness_monitor import (
    evaluate_public_data_freshness,
    evaluate_source_freshness,
    load_json,
    parse_date_or_datetime,
    validate_cache_entry,
    validate_monitor_config,
    validate_source,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_data_freshness_monitor.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_public_data_freshness_monitor.synthetic_complete.example.json"


def _source(**overrides):
    data = {
        "source_id": "source_a",
        "candidate_id": "candidate_a",
        "display_name": "Source A",
        "asset_type": "etf",
        "source_type": "public_reference_csv",
        "source_url": "https://example.com/source.csv",
        "update_frequency": "daily",
        "expected_content_type": "text/csv",
        "public_source_only": True,
        "requires_authentication": False,
        "requires_credentials": False,
        "broker_or_trading_api": False,
        "contains_private_data": False,
        "intended_use": "freshness_monitor_only",
        "notes": "synthetic",
    }
    data.update(overrides)
    return data


def _cache(**overrides):
    data = {
        "source_id": "source_a",
        "cache_path": "jarvis/local/public_data_snapshots/2026-06-12_source_a.csv.raw",
        "fetched_at": "2026-06-12",
        "fetch_status": "success",
        "raw_unverified": True,
        "local_cache_only": True,
        "committed_to_git": False,
    }
    data.update(overrides)
    return data


def _all_fresh_config():
    return {
        "version": "v4.58",
        "title": "All Fresh",
        "monitor_mode": "public_data_freshness_monitor_report_only",
        "report_only": True,
        "no_network": True,
        "execute_fetch": False,
        "parse_evidence": False,
        "verify_evidence": False,
        "promote_verified_evidence": False,
        "current_date": "2026-06-12",
        "sources": [_source(source_id="daily", update_frequency="daily"), _source(source_id="weekly", update_frequency="weekly")],
        "local_cache_index": [
            _cache(source_id="daily", fetched_at="2026-06-11"),
            _cache(source_id="weekly", fetched_at="2026-06-05"),
        ],
        "safety_controls": {
            "execute_fetch": False,
            "no_network": True,
            "report_only": True,
            "parse_evidence": False,
            "verify_evidence": False,
            "promote_verified_evidence": False,
            "registry_mutation": False,
            "approved_asset": False,
            "trusted_asset": False,
            "investable": False,
            "allocation_recommendation": False,
            "buy_signal": False,
            "sell_signal": False,
            "trade_executed": False,
            "executor_created": False,
            "broker_api_used": False,
            "credentials_used": False,
            "private_file_ingested": False,
            "automatic_source_fetching": False,
            "automatic_download": False,
        },
    }


class PublicDataFreshnessMonitorTests(unittest.TestCase):
    def test_default_example_is_safe_report_only(self) -> None:
        result = evaluate_public_data_freshness(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.overall_status, "PUBLIC_DATA_FRESHNESS_MONITOR_PARTIAL_SAFE")
        self.assertTrue(result.no_network)
        self.assertFalse(result.execute_fetch)

    def test_synthetic_complete_returns_stale_or_missing(self) -> None:
        result = evaluate_public_data_freshness(load_json(SYNTHETIC_COMPLETE))

        self.assertEqual(result.overall_status, "PUBLIC_DATA_FRESHNESS_MONITOR_STALE_OR_MISSING_SAFE")
        self.assertEqual(result.fresh_count, 2)
        self.assertEqual(result.stale_count, 1)
        self.assertEqual(result.missing_count, 1)
        self.assertEqual(result.manual_policy_count, 1)

    def test_all_fresh_config_returns_all_fresh(self) -> None:
        result = evaluate_public_data_freshness(_all_fresh_config())

        self.assertEqual(result.overall_status, "PUBLIC_DATA_FRESHNESS_MONITOR_ALL_FRESH_SAFE")
        self.assertEqual(result.fresh_count, 2)

    def test_daily_and_weekly_boundaries(self) -> None:
        current = parse_date_or_datetime("2026-06-12")
        cases = (
            ("daily", "2026-06-11", "SOURCE_FRESH_SAFE"),
            ("daily", "2026-06-10", "SOURCE_STALE_SAFE"),
            ("weekly", "2026-06-05", "SOURCE_FRESH_SAFE"),
            ("weekly", "2026-06-04", "SOURCE_STALE_SAFE"),
        )
        for frequency, fetched_at, expected in cases:
            with self.subTest(frequency=frequency, fetched_at=fetched_at):
                result = evaluate_source_freshness(
                    _source(update_frequency=frequency),
                    [_cache(fetched_at=fetched_at)],
                    current,
                )
                self.assertEqual(result.freshness_status, expected)

    def test_manual_missing_and_failed_statuses(self) -> None:
        current = parse_date_or_datetime("2026-06-12")
        self.assertEqual(
            evaluate_source_freshness(_source(update_frequency="manual"), [], current).freshness_status,
            "SOURCE_MANUAL_POLICY_SAFE",
        )
        self.assertEqual(evaluate_source_freshness(_source(), [], current).freshness_status, "SOURCE_MISSING_SAFE")
        self.assertEqual(
            evaluate_source_freshness(_source(), [_cache(fetch_status="failed")], current).freshness_status,
            "SOURCE_FETCH_FAILED_SAFE",
        )

    def test_invalid_source_fields_block(self) -> None:
        cases = (
            {"update_frequency": "hourly"},
            {"requires_authentication": True},
            {"requires_credentials": True},
            {"broker_or_trading_api": True},
            {"contains_private_data": True},
        )
        for override in cases:
            with self.subTest(override=override):
                self.assertTrue(validate_source(_source(**override)))

    def test_credential_query_params_block(self) -> None:
        for key in ("api_key", "token", "secret", "password", "auth", "credential"):
            with self.subTest(key=key):
                reasons = validate_source(_source(source_url=f"https://example.com/source.csv?{key}=x"))
                self.assertTrue(any(key in reason for reason in reasons))

    def test_cache_validation_blocks_bad_paths_and_flags(self) -> None:
        cases = (
            {"cache_path": "outputs/cache.raw"},
            {"cache_path": "jarvis/data/cache.raw"},
            {"committed_to_git": True},
            {"raw_unverified": False},
            {"local_cache_only": False},
        )
        for override in cases:
            with self.subTest(override=override):
                self.assertFalse(validate_cache_entry(_cache(**override)).valid)

    def test_unsafe_monitor_controls_block(self) -> None:
        unsafe_fields = (
            "execute_fetch",
            "parse_evidence",
            "verify_evidence",
            "promote_verified_evidence",
            "registry_mutation",
            "approved_asset",
            "trusted_asset",
            "investable",
            "allocation_recommendation",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "executor_created",
            "broker_api_used",
            "credentials_used",
            "private_file_ingested",
            "automatic_source_fetching",
            "automatic_download",
        )
        for field in unsafe_fields:
            with self.subTest(field=field):
                config = copy.deepcopy(_all_fresh_config())
                config["safety_controls"][field] = True
                self.assertTrue(validate_monitor_config(config))
        for field, value in (("no_network", False), ("report_only", False)):
            config = copy.deepcopy(_all_fresh_config())
            config[field] = value
            config["safety_controls"][field] = value
            self.assertTrue(validate_monitor_config(config))


if __name__ == "__main__":
    unittest.main()
