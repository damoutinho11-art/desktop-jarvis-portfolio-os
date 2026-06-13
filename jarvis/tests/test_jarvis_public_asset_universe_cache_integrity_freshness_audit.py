import copy
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    compute_freshness_status,
    compute_integrity_status,
    evaluate_cache_coverage,
    evaluate_cache_entry,
    evaluate_public_asset_universe_cache_integrity_freshness_audit,
    load_json,
    sha256_bytes,
    validate_cache_audit_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_problematic.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _safe_entry():
    return copy.deepcopy(_complete_data()["cache_entries"][0])


class PublicAssetUniverseCacheIntegrityFreshnessAuditTests(unittest.TestCase):
    def test_default_example_blocks_without_reading_directories(self) -> None:
        result = evaluate_public_asset_universe_cache_integrity_freshness_audit(load_json(DEFAULT_CONFIG))

        self.assertIn(
            result.status,
            {
                "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_BLOCKED_SAFE",
                "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_PARTIAL_SAFE",
            },
        )
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_written)

    def test_synthetic_complete_is_ready(self) -> None:
        result = evaluate_public_asset_universe_cache_integrity_freshness_audit(_complete_data())

        self.assertEqual(result.status, "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_READY_SAFE")
        self.assertEqual(result.coverage_status, "CACHE_COVERAGE_COMPLETE_SAFE")
        self.assertEqual(result.fresh_count, 2)
        self.assertEqual(result.manual_review_count, 1)

    def test_synthetic_problematic_reports_integrity_issues(self) -> None:
        result = evaluate_public_asset_universe_cache_integrity_freshness_audit(load_json(PROBLEMATIC_CONFIG))

        self.assertIn(
            result.status,
            {
                "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_STALE_OR_MISSING_SAFE",
                "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_INTEGRITY_ISSUES_SAFE",
            },
        )
        self.assertGreater(result.hash_mismatch_count, 0)
        self.assertGreater(result.missing_count, 0)

    def test_integrity_missing_raw(self) -> None:
        entry = _safe_entry()
        entry["observed_raw_exists"] = False
        entry.pop("raw_content_inline", None)

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_MISSING_RAW_SAFE")

    def test_integrity_missing_metadata(self) -> None:
        entry = _safe_entry()
        entry["observed_metadata_exists"] = False
        entry.pop("metadata_inline", None)

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_MISSING_METADATA_SAFE")

    def test_integrity_hash_mismatch(self) -> None:
        entry = _safe_entry()
        entry["metadata_inline"]["content_sha256"] = "0" * 64

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_HASH_MISMATCH_SAFE")

    def test_integrity_unsafe_metadata(self) -> None:
        entry = _safe_entry()
        entry["metadata_inline"]["approved_asset"] = True

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_UNSAFE_METADATA_SAFE")

    def test_integrity_invalid_path(self) -> None:
        entry = _safe_entry()
        entry["raw_cache_path"] = "docs\\bad.raw.json"

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_INVALID_PATH_SAFE")

    def test_failed_fetch_statuses(self) -> None:
        entry = _safe_entry()
        entry["fetch_status"] = "failed"

        result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_FAILED_FETCH_SAFE")
        self.assertEqual(result.freshness_status, "CACHE_FAILED_FETCH_SAFE")

    def test_freshness_thresholds(self) -> None:
        self.assertEqual(compute_freshness_status("2026-06-12", "2026-06-13", "daily", "ok"), "CACHE_FRESH_SAFE")
        self.assertEqual(compute_freshness_status("2026-06-11", "2026-06-13", "daily", "ok"), "CACHE_STALE_SAFE")
        self.assertEqual(compute_freshness_status("2026-06-06", "2026-06-13", "weekly", "ok"), "CACHE_FRESH_SAFE")
        self.assertEqual(compute_freshness_status("2026-06-05", "2026-06-13", "weekly", "ok"), "CACHE_STALE_SAFE")
        self.assertEqual(compute_freshness_status("2026-05-13", "2026-06-13", "monthly", "ok"), "CACHE_FRESH_SAFE")
        self.assertEqual(compute_freshness_status("2026-05-12", "2026-06-13", "monthly", "ok"), "CACHE_STALE_SAFE")
        self.assertEqual(compute_freshness_status("2026-01-01", "2026-06-13", "manual", "ok"), "CACHE_MANUAL_REVIEW_REQUIRED_SAFE")
        self.assertEqual(compute_freshness_status("2026-01-01", "2026-06-13", "quarterly", "ok"), "CACHE_BLOCKED_SAFE")

    def test_coverage_complete_and_missing(self) -> None:
        complete = _complete_data()
        result = evaluate_public_asset_universe_cache_integrity_freshness_audit(complete)
        self.assertEqual(result.coverage_status, "CACHE_COVERAGE_COMPLETE_SAFE")

        missing = evaluate_cache_coverage(complete["expected_source_plans"], result.per_source_results[:-1])
        self.assertEqual(missing.coverage_status, "CACHE_COVERAGE_PARTIAL_SAFE")
        self.assertEqual(missing.missing_source_count, 1)

    def test_file_backed_mode_reads_explicit_temp_files_and_does_not_write(self) -> None:
        data = _complete_data()
        raw_bytes = b"file backed raw\n"
        digest = sha256_bytes(raw_bytes)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_path = root / "raw" / "file_source.raw.json"
            metadata_path = root / "metadata" / "file_source.metadata.json"
            raw_path.parent.mkdir(parents=True)
            metadata_path.parent.mkdir(parents=True)
            raw_path.write_bytes(raw_bytes)
            metadata_path.write_text(
                json.dumps(
                    {
                        **data["cache_entries"][0]["metadata_inline"],
                        "source_id": "file_source",
                        "content_sha256": digest,
                        "content_length": len(raw_bytes),
                        "fetched_at": "2026-06-13",
                    }
                ),
                encoding="utf-8",
            )
            entry = copy.deepcopy(data["cache_entries"][0])
            entry.update(
                {
                    "source_id": "file_source",
                    "file_backed": True,
                    "raw_cache_path": str(raw_path),
                    "metadata_path": str(metadata_path),
                    "raw_content_inline": None,
                    "metadata_inline": None,
                    "expected_update_frequency": "daily",
                    "fetched_at": "2026-06-13",
                }
            )
            before = {path.relative_to(root) for path in root.rglob("*")}
            result = evaluate_cache_entry(entry, "2026-06-13", root)
            after = {path.relative_to(root) for path in root.rglob("*")}

        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_OK_SAFE")
        self.assertEqual(result.freshness_status, "CACHE_FRESH_SAFE")
        self.assertEqual(before, after)

    def test_file_backed_path_outside_cache_root_blocks(self) -> None:
        entry = _safe_entry()
        with tempfile.TemporaryDirectory() as tmpdir:
            entry["file_backed"] = True
            entry["raw_cache_path"] = str(Path(tmpdir).parent / "outside.raw.json")
            entry["metadata_path"] = str(Path(tmpdir) / "metadata.json")
            result = evaluate_cache_entry(entry, "2026-06-13", tmpdir)
        self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_INVALID_PATH_SAFE")

    def test_forbidden_path_roots_block(self) -> None:
        for path in ("docs\\bad.raw.json", "templates\\bad.raw.json", "jarvis\\data\\bad.raw.json"):
            with self.subTest(path=path):
                entry = _safe_entry()
                entry["raw_cache_path"] = path
                result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")
                self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_INVALID_PATH_SAFE")

    def test_unsafe_metadata_claims_block(self) -> None:
        fields = (
            "evidence_verified",
            "approved_asset",
            "trusted_asset",
            "investable",
            "allocation_recommendation",
            "portfolio_weight",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "registry_mutation",
            "candidate_registry_write",
            "executor_created",
        )
        for field in fields:
            with self.subTest(field=field):
                entry = _safe_entry()
                entry["metadata_inline"][field] = True
                result = evaluate_cache_entry(entry, "2026-06-13", "jarvis\\local\\public_asset_universe\\")
                self.assertEqual(result.integrity_status, "CACHE_INTEGRITY_UNSAFE_METADATA_SAFE")

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_cache_audit_config(data))

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_cache_audit_config(data))

    def test_next_manual_action_values(self) -> None:
        for action in (
            "review_cache_audit",
            "repair_cache_by_rerunning_authorized_fetch",
            "proceed_to_public_asset_universe_normalizer",
            "fix_cache_metadata",
            "no_manual_asset_entry_required",
        ):
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                self.assertNotIn("next_manual_action must be valid.", validate_cache_audit_config(data))

        for action in (
            "execute_fetch_now",
            "normalize_now",
            "classify_now",
            "evidence_verification",
            "approval",
            "registry_mutation",
            "allocation_recommendation",
            "trade_execution",
            "executor_creation",
        ):
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                self.assertTrue(validate_cache_audit_config(data))

    def test_module_requires_no_internet_or_subprocess(self) -> None:
        result = evaluate_public_asset_universe_cache_integrity_freshness_audit(_complete_data())
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_fetch_executed)
        self.assertTrue(result.no_cache_written)


if __name__ == "__main__":
    unittest.main()
