import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_asset_universe_local_cache_builder import (
    AUTHORIZATION_DEPENDENT_SAFETY_FIELDS,
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_AUTHORIZATION_PHRASE,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_metadata_record,
    evaluate_public_asset_universe_local_cache_builder,
    execute_authorized_local_cache_build,
    load_json,
    validate_cache_path,
    validate_local_cache_builder_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.example.json"
UNAUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.synthetic_unauthorized.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_asset_universe_local_cache_builder.synthetic_authorized.json"


def _authorized_data():
    return load_json(AUTHORIZED_CONFIG)


class FakeFetcher:
    def __init__(self, fail_url: str | None = None) -> None:
        self.calls: list[str] = []
        self.fail_url = fail_url

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if self.fail_url and self.fail_url == url:
            raise RuntimeError("synthetic fetch failure")
        return f"raw fixture for {url}\n".encode("utf-8")


class PublicAssetUniverseLocalCacheBuilderTests(unittest.TestCase):
    def test_default_example_blocks_without_fetch_or_write(self) -> None:
        result = evaluate_public_asset_universe_local_cache_builder(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE")
        self.assertFalse(result.fetch_executed)
        self.assertFalse(result.writes_performed)

    def test_unauthorized_fixture_blocks(self) -> None:
        result = evaluate_public_asset_universe_local_cache_builder(load_json(UNAUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE")
        self.assertFalse(result.fetch_executed)

    def test_synthetic_authorized_evaluation_ready_without_fetch_or_write(self) -> None:
        result = evaluate_public_asset_universe_local_cache_builder(_authorized_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_READY_TO_FETCH_SAFE")
        self.assertEqual(result.authorization_status, "authorized")
        self.assertFalse(result.fetch_executed)
        self.assertFalse(result.writes_performed)

    def test_execute_authorized_build_uses_fake_fetcher_and_temp_cache_root(self) -> None:
        data = _authorized_data()
        fetcher = FakeFetcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = execute_authorized_local_cache_build(
                data,
                fetcher=fetcher,
                now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
                cache_root_override=tmpdir,
            )

            self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_PARTIAL_LOCAL_CACHE_SAFE")
            self.assertEqual(result.fetched_count, 2)
            self.assertEqual(result.skipped_sources, ("fund_etp_universe_source",))
            self.assertEqual(len(fetcher.calls), 2)
            for path in result.written_raw_cache_paths + result.written_metadata_paths:
                self.assertTrue(Path(path).exists())
                Path(path).resolve().relative_to(Path(tmpdir).resolve())

    def test_fake_fetcher_called_only_with_exact_authorization(self) -> None:
        data = _authorized_data()
        data["authorization_phrase"] = "WRONG"
        data["authorization_phrase_valid"] = False
        fetcher = FakeFetcher()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = execute_authorized_local_cache_build(data, fetcher=fetcher, cache_root_override=tmpdir)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE")
        self.assertEqual(fetcher.calls, [])

    def test_failed_fake_fetch_is_partial_without_unsafe_behavior(self) -> None:
        data = _authorized_data()
        fetcher = FakeFetcher(fail_url=data["source_fetch_plans"][0]["source_url"])
        with tempfile.TemporaryDirectory() as tmpdir:
            result = execute_authorized_local_cache_build(data, fetcher=fetcher, cache_root_override=tmpdir)

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_PARTIAL_LOCAL_CACHE_SAFE")
        self.assertEqual(result.fetched_count, 1)
        self.assertEqual(result.failed_count, 1)
        self.assertTrue(result.no_evidence_verification)
        self.assertTrue(result.no_approval)
        self.assertTrue(result.no_trade)

    def test_raw_and_metadata_paths_are_deterministic(self) -> None:
        result = evaluate_public_asset_universe_local_cache_builder(_authorized_data())

        first = result.source_plans[0]
        self.assertEqual(first.raw_cache_path, "jarvis\\local\\public_asset_universe\\raw\\market_reference_source.raw.json")
        self.assertEqual(first.metadata_path, "jarvis\\local\\public_asset_universe\\metadata\\market_reference_source.metadata.json")

    def test_metadata_contains_hash_and_safety_flags(self) -> None:
        result = evaluate_public_asset_universe_local_cache_builder(_authorized_data())
        metadata = build_metadata_record(
            result.source_plans[0],
            b"abc",
            "raw.json",
            "metadata.json",
            "2026-01-02T03:04:05+00:00",
            "explicit_public_json_fetch_local_cache_only",
        )

        self.assertEqual(metadata["content_sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertTrue(metadata["raw_unverified"])
        for field in (
            "evidence_verified",
            "approved_asset",
            "trusted_asset",
            "investable",
            "allocation_recommendation",
            "portfolio_weight",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "executor_created",
        ):
            self.assertFalse(metadata[field])

    def test_validate_cache_path_blocks_outside_allowed_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outside = Path(tmpdir).parent / "outside.raw.json"
            self.assertTrue(validate_cache_path(outside, tmpdir))

    def test_write_paths_under_data_docs_templates_block(self) -> None:
        for field, path in (
            ("raw_cache_path", "jarvis\\data\\bad.raw.json"),
            ("metadata_path", "docs\\bad.metadata.json"),
            ("fetch_plan_path", "templates\\bad.fetch_plan.json"),
        ):
            with self.subTest(field=field):
                data = _authorized_data()
                data["source_fetch_plans"][0][field] = path
                result = evaluate_public_asset_universe_local_cache_builder(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_SAFE")

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
                data = _authorized_data()
                data["source_fetch_plans"][0][field] = value
                result = evaluate_public_asset_universe_local_cache_builder(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_SAFE")

    def test_unsupported_source_type_and_fetch_method_block(self) -> None:
        for field, value in (
            ("source_type", "broker_api"),
            ("allowed_future_fetch_method", "authenticated_api"),
        ):
            with self.subTest(field=field):
                data = _authorized_data()
                data["source_fetch_plans"][0][field] = value
                result = evaluate_public_asset_universe_local_cache_builder(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_SAFE")

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
                data = _authorized_data()
                data["source_fetch_plans"][0]["source_url"] = url
                data["source_fetch_plans"][0]["source_name"] = name
                result = evaluate_public_asset_universe_local_cache_builder(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_SAFE")

    def test_unsafe_safety_controls_block(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _authorized_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_local_cache_builder_config(data))

    def test_unauthorized_config_with_authorization_dependent_activity_blocks(self) -> None:
        for field in AUTHORIZATION_DEPENDENT_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = load_json(UNAUTHORIZED_CONFIG)
                data["safety_controls"][field] = True
                result = evaluate_public_asset_universe_local_cache_builder(data)
                self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE")

    def test_authorized_config_may_report_authorized_local_cache_activity_flags(self) -> None:
        for field in AUTHORIZATION_DEPENDENT_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _authorized_data()
                data["safety_controls"][field] = True
                blockers = validate_local_cache_builder_config(data)
                self.assertNotIn(f"safety_controls.{field} may be true only with exact authorization.", blockers)

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _authorized_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_local_cache_builder_config(data))

    def test_required_authorization_phrase_constant(self) -> None:
        self.assertEqual(
            REQUIRED_AUTHORIZATION_PHRASE,
            "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE",
        )

    def test_tests_require_no_internet_by_using_fake_fetcher(self) -> None:
        data = _authorized_data()
        fetcher = FakeFetcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            execute_authorized_local_cache_build(data, fetcher=fetcher, cache_root_override=tmpdir)
        self.assertTrue(all(url.startswith("https://example.com/") for url in fetcher.calls))

    def test_no_subprocess_calls_are_needed(self) -> None:
        data = _authorized_data()
        result = evaluate_public_asset_universe_local_cache_builder(data)
        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_READY_TO_FETCH_SAFE")


if __name__ == "__main__":
    unittest.main()
