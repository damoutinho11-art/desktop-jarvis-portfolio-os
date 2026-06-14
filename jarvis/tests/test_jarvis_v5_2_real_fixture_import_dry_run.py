import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_v5_2_real_fixture_import_dry_run import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    IMPORT_TARGETS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    classify_import_status,
    evaluate_v5_2_real_fixture_import_dry_run,
    execute_authorized_v5_2_import_dry_run_snapshot_write,
    inspect_local_fixture_file,
    load_json,
    map_import_preview_to_pipeline,
    validate_import_fixture_record,
    validate_v5_2_real_fixture_import_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.synthetic_authorized_write.json"


def _complete_data() -> dict:
    return load_json(COMPLETE_CONFIG)


def _record() -> dict:
    return copy.deepcopy(_complete_data()["public_source_fixture_records"][0])


class V52RealFixtureImportDryRunTests(unittest.TestCase):
    def test_default_example_partials_safely(self) -> None:
        result = evaluate_v5_2_real_fixture_import_dry_run(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_PARTIAL_SAFE")
        self.assertEqual(result.fixture_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_executor)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_v5_2_real_fixture_import_dry_run(_complete_data())

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_SAFE")
        self.assertEqual(result.fixture_count, 8)
        self.assertEqual(result.ready_import_count, 8)
        self.assertEqual(result.shallow_metadata_count, 8)
        self.assertEqual(result.hash_fingerprint_count, 8)
        self.assertEqual(result.mapped_to_pipeline_count, 8)

    def test_synthetic_problematic_blocks_safely(self) -> None:
        result = evaluate_v5_2_real_fixture_import_dry_run(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE")
        self.assertGreater(result.unsafe_fixture_count, 0)
        self.assertGreater(result.duplicate_fixture_id_count, 0)
        self.assertGreater(result.blocked_mapping_count, 0)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_report_path_writes_nothing(self) -> None:
        result = evaluate_v5_2_real_fixture_import_dry_run(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_TO_WRITE_SAFE")
        self.assertEqual(result.ready_import_count, 1)
        self.assertTrue(result.imported_data_unverified)

    def test_csv_json_text_html_and_pdf_are_shallow_inspected_from_temp_files(self) -> None:
        config = _complete_data()
        records = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = [
                ("csv_fixture", "csv", "etf_universe", "universe_list", root / "etf.csv", "symbol,name\nVWCE,Synthetic ETF\n"),
                ("json_fixture", "json", "crypto_universe", "universe_list", root / "crypto.json", '[{"symbol": "BTC"}]\n'),
                ("txt_fixture", "txt", "equity_universe", "universe_list", root / "equity.txt", "AAA\nBBB\n"),
                ("md_fixture", "md", "fund_or_etp_universe", "universe_list", root / "fund.md", "# Synthetic\n- line\n"),
                ("html_fixture", "html_saved_public_page", "exchange_or_venue_reference", "exchange_reference", root / "page.html", "<html><body>Do not parse.</body></html>"),
                ("pdf_fixture", "pdf_public_document_reference_only", "public_document_reference", "public_document_reference", root / "doc.pdf", b"%PDF-1.4 synthetic\n"),
            ]
            for fixture_id, fixture_format, category, fixture_type, path, payload in fixtures:
                path.write_bytes(payload if isinstance(payload, bytes) else payload.encode("utf-8"))
                record = _record()
                record.update(
                    {
                        "fixture_id": fixture_id,
                        "source_id": fixture_id,
                        "source_name": f"{fixture_id} source",
                        "source_category_id": category,
                        "fixture_type": fixture_type,
                        "fixture_format": fixture_format,
                        "expected_local_path": str(path),
                        "fixture_status": "READY",
                    }
                )
                record.pop("synthetic_inspection", None)
                records.append(record)
            config["fixture_root"] = str(root)
            config["public_source_fixture_records"] = records
            config["import_policy"]["allow_inline_synthetic_inspection"] = False

            result = evaluate_v5_2_real_fixture_import_dry_run(config)

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_SAFE")
        self.assertEqual(result.ready_import_count, 6)
        metadata_by_id = {row["fixture_id"]: row["metadata_type"] for row in result.fixture_rows}
        self.assertEqual(metadata_by_id["csv_fixture"], "csv_shallow")
        self.assertEqual(metadata_by_id["json_fixture"], "json_shallow")
        self.assertEqual(metadata_by_id["txt_fixture"], "text_shallow")
        self.assertEqual(metadata_by_id["md_fixture"], "text_shallow")
        self.assertEqual(metadata_by_id["html_fixture"], "presence_size_hash_only")
        self.assertEqual(metadata_by_id["pdf_fixture"], "presence_size_hash_only")

    def test_html_and_pdf_metadata_only_never_parse_or_ocr(self) -> None:
        config = _complete_data()
        rows = {row["fixture_id"]: row for row in evaluate_v5_2_real_fixture_import_dry_run(config).import_preview_rows}

        for fixture_id in ("exchange_reference_html", "public_document_pdf_reference"):
            with self.subTest(fixture_id=fixture_id):
                metadata = rows[fixture_id]["shallow_metadata"]
                self.assertEqual(metadata["metadata_type"], "presence_size_hash_only")
                self.assertFalse(metadata["parsed_content"])
                self.assertFalse(metadata["ocr_performed"])

    def test_missing_file_blocks_or_partials_safely(self) -> None:
        config = _complete_data()
        with tempfile.TemporaryDirectory() as tmp:
            record = _record()
            record["expected_local_path"] = str(Path(tmp) / "missing.csv")
            record.pop("synthetic_inspection", None)
            config["fixture_root"] = tmp
            config["public_source_fixture_records"] = [record]
            config["import_policy"]["allow_inline_synthetic_inspection"] = False
            result = evaluate_v5_2_real_fixture_import_dry_run(config)

        self.assertEqual(result.status, "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE")
        self.assertEqual(result.missing_fixture_count, 1)
        self.assertIn("local fixture file is missing", " ".join(result.blockers))

    def test_import_disabled_is_skipped_without_preview(self) -> None:
        config = _complete_data()
        config["public_source_fixture_records"] = [_record()]
        config["public_source_fixture_records"][0]["import_enabled"] = False

        result = evaluate_v5_2_real_fixture_import_dry_run(config)

        self.assertEqual(result.skipped_import_count, 1)
        self.assertEqual(result.ready_import_count, 0)
        self.assertFalse(result.import_preview_rows[0]["dry_run_import_preview"])

    def test_stale_and_manual_refresh_require_review(self) -> None:
        for status in ("STALE", "MANUAL_REFRESH_REQUIRED"):
            with self.subTest(status=status):
                record = _record()
                record["fixture_status"] = status
                inspection = {"exists": True, "is_file": True, "blockers": (), "metadata": {"metadata_type": "synthetic"}, "sha256": "abc"}
                self.assertEqual(classify_import_status(record, inspection), status)

    def test_unsupported_category_format_path_and_true_flags_block(self) -> None:
        record = _record()
        record["source_category_id"] = "unsupported"
        record["fixture_format"] = "xlsx"
        record["expected_local_path"] = "jarvis/data/bad.xlsx"
        record["approved_asset"] = True

        blockers = validate_import_fixture_record(record, "jarvis/local/public_source_fixtures")

        self.assertIn("unsupported source_category_id", " ".join(blockers))
        self.assertIn("unsupported fixture_format", " ".join(blockers))
        self.assertIn("expected_local_path", " ".join(blockers))
        self.assertIn("approved_asset must be false", " ".join(blockers))

    def test_pipeline_mapping_has_all_import_targets_when_ready(self) -> None:
        record = _record()
        mapping = map_import_preview_to_pipeline(record, {"exists": True, "blockers": (), "metadata": {}, "sha256": "abc"})

        self.assertTrue(mapping["mapped"])
        self.assertEqual(mapping["import_targets"], IMPORT_TARGETS)

    def test_unsafe_top_level_safety_controls_are_blocked(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_v5_2_real_fixture_import_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_v5_2_real_fixture_import_config(mutated))

    def test_file_size_sha256_and_mtime_are_reported_without_full_metadata_parse_for_binary_formats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.pdf"
            path.write_bytes(b"%PDF-1.4 synthetic\n")
            record = _record()
            record.update({"fixture_format": "pdf_public_document_reference_only", "fixture_type": "public_document_reference", "expected_local_path": str(path)})

            inspection = inspect_local_fixture_file(record, tmp)

        self.assertTrue(inspection["exists"])
        self.assertEqual(inspection["size_bytes"], len(b"%PDF-1.4 synthetic\n"))
        self.assertEqual(len(inspection["sha256"]), 64)
        self.assertEqual(inspection["metadata"]["metadata_type"], "presence_size_hash_only")

    def test_authorized_write_function_writes_snapshot_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_v5_2_real_fixture_import_dry_run(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_2_import_dry_run_snapshot_write(
                config,
                result,
                now=datetime(2026, 6, 14, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(len(payload["import_preview_rows"]), 1)
        self.assertTrue(metadata["fixture_data_unverified"])
        self.assertTrue(metadata["imported_data_unverified"])
        for field in ("fetch_executed", "download_executed", "ocr", "pdf_parsing", "html_scraping", "evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_v5_2_real_fixture_import_dry_run(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_v5_2_import_dry_run_snapshot_write(config, result, output_root_override=tmp)
            self.assertFalse(Path(tmp, "jarvis_v5_2_real_fixture_import_dry_run.snapshot.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE")

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_v5_2_real_fixture_import_dry_run as module

        self.assertTrue(hasattr(module, "evaluate_v5_2_real_fixture_import_dry_run"))


if __name__ == "__main__":
    unittest.main()
