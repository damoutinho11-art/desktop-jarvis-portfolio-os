"""Real public fixture import dry-run.

v5.2 inspects operator-provided local public fixture files for import-preview
safety only. It performs no network calls, fetching, downloading, scraping,
OCR, PDF parsing, HTML scraping, evidence extraction, evidence verification,
approval, recommendation, allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_source_fixtures/v5_2_import_dry_run")
DEFAULT_FIXTURE_ROOT = "jarvis/local/public_source_fixtures"
DEFAULT_MAX_BYTES = 2 * 1024 * 1024
SUPPORTED_SOURCE_CATEGORIES = {
    "etf_universe",
    "equity_universe",
    "fund_or_etp_universe",
    "crypto_universe",
    "market_reference_universe",
    "issuer_or_provider_reference",
    "exchange_or_venue_reference",
    "public_document_reference",
}
SUPPORTED_FIXTURE_FORMATS = {
    "csv",
    "json",
    "txt",
    "md",
    "html_saved_public_page",
    "pdf_public_document_reference_only",
    "unknown",
}
SUPPORTED_FIXTURE_TYPES = {
    "universe_list",
    "issuer_reference",
    "provider_reference",
    "exchange_reference",
    "public_document_reference",
    "market_reference",
    "metadata_reference",
    "unknown",
}
IMPORT_TARGETS = (
    "source_manifest_candidate",
    "fetch_planner_local_fixture_reference",
    "local_cache_candidate",
    "cache_audit_candidate",
    "normalizer_input_candidate",
    "classifier_input_candidate",
    "research_queue_input_candidate",
    "evidence_pack_draft_source_reference",
    "operator_dashboard_source_reference",
    "e2e_workflow_audit_source_reference",
)
VALID_NEXT_MANUAL_ACTIONS = {
    "review_real_fixture_import_dry_run",
    "prepare_missing_local_public_fixtures",
    "fix_fixture_metadata",
    "proceed_to_v5_3_operator_fixture_review_queue",
    "proceed_to_v5_3_explicit_authorized_public_fetch_stub",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "live_fetch_now",
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
    "trade_execution",
    "executor_creation",
}
DO_NOT_BUILD_NEXT = (
    "live_fetch_adapter_inside_v5_2",
    "scraping",
    "ocr",
    "pdf_parsing",
    "html_scraping",
    "evidence_verification",
    "broker_integration",
    "executor",
)
FALSE_REQUIRED_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "scraping",
    "api_calls",
    "writes_without_explicit_authorization",
    "cache_mutation_without_explicit_authorization",
    "subprocess_execution",
    "scheduler_creation",
    "browser_automation",
    "broker_integration",
    "lightyear_integration",
    "lhv_integration",
    "crypto_exchange_integration",
    "credentials_used",
    "private_file_ingested",
    "automatic_private_data_ingest",
    "account_data_ingested",
    "source_parsing_as_evidence",
    "ocr",
    "pdf_parsing",
    "html_scraping",
    "evidence_extraction",
    "evidence_verification",
    "verified_evidence_promotion",
    "investment_screening",
    "research_scoring",
    "ranking_by_investment_merit",
    "recommendation",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "executor_created",
)
TRUE_REQUIRED_SAFETY_FIELDS = (
    "public_data_only",
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
    "final_purchase_external_manual_only",
    "local_fixture_only",
    "fixture_data_unverified",
    "imported_data_unverified",
    "dry_run_only",
    "import_preview_only",
)
FORBIDDEN_RECORD_TRUE_FIELDS = (
    "downloaded_by_jarvis",
    "evidence_verified",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "executor_created",
    "registry_mutation",
    "candidate_registry_write",
)
FORBIDDEN_KEYS = (
    "credential",
    "credentials",
    "api_key",
    "secret",
    "password",
    "account_number",
    "account_id",
    "private_key",
    "wallet_seed",
)
EXTENSION_BY_FORMAT = {
    "csv": ".csv",
    "json": ".json",
    "txt": ".txt",
    "md": ".md",
    "html_saved_public_page": (".html", ".htm"),
    "pdf_public_document_reference_only": ".pdf",
}


@dataclass(frozen=True)
class V52RealFixtureImportDryRunResult:
    title: str
    version: str
    status: str
    import_dry_run_mode: str
    fixture_count: int
    import_candidate_count: int
    ready_import_count: int
    skipped_import_count: int
    missing_fixture_count: int
    stale_fixture_count: int
    manual_refresh_required_count: int
    invalid_path_count: int
    unsupported_format_count: int
    unsafe_fixture_count: int
    duplicate_fixture_id_count: int
    shallow_metadata_count: int
    hash_fingerprint_count: int
    mapped_to_pipeline_count: int
    blocked_mapping_count: int
    fixture_rows: tuple[dict[str, Any], ...]
    import_preview_rows: tuple[dict[str, Any], ...]
    pipeline_mapping_rows: tuple[dict[str, Any], ...]
    operator_runbook_steps: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_safe_action: str
    do_not_build_next: tuple[str, ...]
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_download_executed: bool = True
    no_scraping_executed: bool = True
    no_api_called: bool = True
    no_ocr: bool = True
    no_pdf_parsing: bool = True
    no_html_scraping: bool = True
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_approval: bool = True
    no_recommendation: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_fixture_only: bool = True
    fixture_data_unverified: bool = True
    imported_data_unverified: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _authorization_valid(config: dict[str, Any]) -> bool:
    policy = config.get("authorization_policy", {})
    if not isinstance(policy, dict):
        return False
    return (
        policy.get("explicit_authorization_required") is True
        and policy.get("required_authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase_valid") is True
        and policy.get("default_write_allowed") is False
        and policy.get("write_allowed_only_with_explicit_authorization") is True
    )


def _normalized_path_text(path: str | Path) -> str:
    return normalize_text(path).replace("\\", "/").rstrip("/")


def _path_is_under(path: str | Path, root: str | Path) -> bool:
    text = _normalized_path_text(path)
    root_text = _normalized_path_text(root)
    if not text or not root_text:
        return False
    if text == root_text or text.startswith(root_text + "/"):
        return True
    try:
        Path(text).resolve().relative_to(Path(root_text).resolve())
        return True
    except (OSError, ValueError):
        return False


def _scan_for_forbidden_keys(value: Any, prefix: str = "") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = normalize_text(key).lower()
            full_key = f"{prefix}.{key_text}" if prefix else key_text
            if any(forbidden in key_text for forbidden in FORBIDDEN_KEYS) and nested not in (False, None, "", (), [], {}):
                blockers.append(f"forbidden private/credential field present: {full_key}")
            blockers.extend(_scan_for_forbidden_keys(nested, full_key))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            blockers.extend(_scan_for_forbidden_keys(nested, f"{prefix}[{index}]"))
    return tuple(blockers)


def validate_fixture_path(path: str | Path, fixture_root: str | Path) -> tuple[str, ...]:
    text = _normalized_path_text(path)
    if not text:
        return ("expected_local_path is required.",)
    blockers: list[str] = []
    blocked_roots = ("docs", "templates", "jarvis/data", "registry", "candidate_assets", "private", "account")
    if text in {".", ""} or any(text == root or text.startswith(root + "/") for root in blocked_roots):
        blockers.append("expected_local_path must not target docs, templates, jarvis/data, registry, candidate, private/account, or repo root paths.")
    if not _path_is_under(text, fixture_root):
        blockers.append("expected_local_path must stay under the configured fixture_root.")
    return tuple(dict.fromkeys(blockers))


def validate_import_fixture_record(record: dict[str, Any], fixture_root: str | Path) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "fixture_id",
        "source_id",
        "source_name",
        "source_category_id",
        "asset_universe",
        "fixture_type",
        "fixture_format",
        "expected_local_path",
    ):
        if not normalize_text(record.get(field)):
            blockers.append(f"{field} is required.")
    category = normalize_text(record.get("source_category_id"))
    if category not in SUPPORTED_SOURCE_CATEGORIES:
        blockers.append(f"unsupported source_category_id: {category or 'missing'}")
    fixture_format = normalize_text(record.get("fixture_format"))
    if fixture_format not in SUPPORTED_FIXTURE_FORMATS:
        blockers.append(f"unsupported fixture_format: {fixture_format or 'missing'}")
    fixture_type = normalize_text(record.get("fixture_type"))
    if fixture_type and fixture_type not in SUPPORTED_FIXTURE_TYPES:
        blockers.append(f"unsupported fixture_type: {fixture_type}")
    blockers.extend(validate_fixture_path(record.get("expected_local_path", ""), fixture_root))
    if record.get("public_only") is not True:
        blockers.append("public_only must be true.")
    for field in FORBIDDEN_RECORD_TRUE_FIELDS:
        if record.get(field) is True:
            blockers.append(f"{field} must be false.")
    blockers.extend(_scan_for_forbidden_keys(record))
    return tuple(dict.fromkeys(blockers))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_limited(path: Path, max_bytes: int) -> bytes:
    with path.open("rb") as handle:
        return handle.read(max_bytes + 1)


def _extension_matches(path: Path, fixture_format: str) -> bool:
    expected = EXTENSION_BY_FORMAT.get(fixture_format)
    if expected is None:
        return True
    suffix = path.suffix.lower()
    if isinstance(expected, tuple):
        return suffix in expected
    return suffix == expected


def inspect_csv_fixture(path: str | Path, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    raw = _read_limited(Path(path), max_bytes)
    truncated = len(raw) > max_bytes
    text = raw[:max_bytes].decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(text.splitlines()))
    header = tuple(rows[0]) if rows else ()
    return {"metadata_type": "csv_shallow", "row_count": max(0, len(rows) - 1), "header_columns": header, "truncated": truncated}


def inspect_json_fixture(path: str | Path, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    raw = _read_limited(Path(path), max_bytes)
    truncated = len(raw) > max_bytes
    data = json.loads(raw[:max_bytes].decode("utf-8", errors="replace"))
    if isinstance(data, dict):
        return {"metadata_type": "json_shallow", "top_level_type": "object", "top_level_keys": tuple(sorted(str(key) for key in data.keys())), "item_count": len(data), "truncated": truncated}
    if isinstance(data, list):
        return {"metadata_type": "json_shallow", "top_level_type": "list", "top_level_keys": (), "item_count": len(data), "truncated": truncated}
    return {"metadata_type": "json_shallow", "top_level_type": type(data).__name__, "top_level_keys": (), "item_count": 1, "truncated": truncated}


def inspect_text_fixture(path: str | Path, max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    raw = _read_limited(Path(path), max_bytes)
    truncated = len(raw) > max_bytes
    text = raw[:max_bytes].decode("utf-8", errors="replace")
    return {"metadata_type": "text_shallow", "line_count": len(text.splitlines()), "truncated": truncated}


def inspect_local_fixture_file(record: dict[str, Any], fixture_root: str | Path, max_bytes: int | None = None) -> dict[str, Any]:
    max_read = int(max_bytes or DEFAULT_MAX_BYTES)
    path = Path(record.get("expected_local_path", ""))
    fixture_format = normalize_text(record.get("fixture_format"))
    blockers = list(validate_fixture_path(path, fixture_root))
    if blockers:
        return {"exists": False, "is_file": False, "blockers": tuple(blockers), "warnings": (), "metadata": {}, "sha256": ""}
    if not path.exists():
        return {"exists": False, "is_file": False, "blockers": ("local fixture file is missing.",), "warnings": (), "metadata": {}, "sha256": ""}
    if not path.is_file():
        return {"exists": True, "is_file": False, "blockers": ("local fixture path is not a file.",), "warnings": (), "metadata": {}, "sha256": ""}
    stat = path.stat()
    warnings: list[str] = []
    blockers = []
    if not _extension_matches(path, fixture_format):
        blockers.append("file extension does not match declared fixture_format.")
    metadata: dict[str, Any] = {"metadata_type": "metadata_only"}
    try:
        if fixture_format == "csv":
            metadata = inspect_csv_fixture(path, max_read)
        elif fixture_format == "json":
            metadata = inspect_json_fixture(path, max_read)
        elif fixture_format in {"txt", "md"}:
            metadata = inspect_text_fixture(path, max_read)
        elif fixture_format in {"html_saved_public_page", "pdf_public_document_reference_only"}:
            metadata = {"metadata_type": "presence_size_hash_only", "parsed_content": False, "ocr_performed": False}
        else:
            metadata = {"metadata_type": "presence_size_hash_only"}
    except Exception as exc:  # malformed local fixture should not crash report
        blockers.append(f"shallow metadata inspection failed safely: {exc.__class__.__name__}")
    return {
        "exists": True,
        "is_file": True,
        "path": str(path),
        "size_bytes": stat.st_size,
        "sha256": _sha256_file(path),
        "last_modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        "extension_matches": _extension_matches(path, fixture_format),
        "metadata": metadata,
        "blockers": tuple(blockers),
        "warnings": tuple(warnings),
    }


def _inline_inspection(record: dict[str, Any]) -> dict[str, Any]:
    inspection = record.get("synthetic_inspection", {})
    if not isinstance(inspection, dict):
        inspection = {}
    return {
        "exists": inspection.get("exists", True),
        "is_file": inspection.get("is_file", True),
        "path": record.get("expected_local_path"),
        "size_bytes": inspection.get("size_bytes", 128),
        "sha256": inspection.get("sha256", _sha256_bytes(normalize_text(record.get("fixture_id")).encode("utf-8"))),
        "last_modified": inspection.get("last_modified", "2026-06-13T00:00:00+00:00"),
        "extension_matches": inspection.get("extension_matches", True),
        "metadata": inspection.get("metadata", {"metadata_type": "synthetic_shallow"}),
        "blockers": tuple(inspection.get("blockers", [])),
        "warnings": tuple(inspection.get("warnings", [])),
    }


def classify_import_status(record: dict[str, Any], inspection: dict[str, Any], current_date: str | None = None) -> str:
    if record.get("import_enabled") is False:
        return "SKIPPED_IMPORT_DISABLED"
    status = normalize_text(record.get("fixture_status")).upper()
    if status in {"STALE", "MANUAL_REFRESH_REQUIRED"}:
        return status
    if not inspection.get("exists"):
        return "MISSING"
    if inspection.get("blockers"):
        return "INVALID"
    return "READY"


def map_fixture_to_import_preview(record: dict[str, Any], inspection: dict[str, Any]) -> dict[str, Any]:
    fixture_id = normalize_text(record.get("fixture_id"))
    enabled = record.get("import_enabled") is not False
    status = classify_import_status(record, inspection)
    return {
        "fixture_id": fixture_id,
        "source_category_id": record.get("source_category_id"),
        "fixture_format": record.get("fixture_format"),
        "import_enabled": enabled,
        "import_status": status,
        "dry_run_import_preview": enabled and status == "READY",
        "hash_fingerprint": inspection.get("sha256", ""),
        "shallow_metadata": inspection.get("metadata", {}),
        "evidence_verified": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "recommendation": False,
        "allocation_recommendation": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "executor_created": False,
    }


def map_import_preview_to_pipeline(record: dict[str, Any], inspection: dict[str, Any]) -> dict[str, Any]:
    fixture_id = normalize_text(record.get("fixture_id"))
    category = normalize_text(record.get("source_category_id"))
    if category not in SUPPORTED_SOURCE_CATEGORIES:
        return {"fixture_id": fixture_id, "mapped": False, "import_targets": (), "blocked_reason": "unsupported source category cannot be mapped."}
    if record.get("import_enabled") is False:
        return {"fixture_id": fixture_id, "mapped": False, "import_targets": (), "blocked_reason": "import disabled by operator."}
    if not inspection.get("exists") or inspection.get("blockers"):
        return {"fixture_id": fixture_id, "mapped": False, "import_targets": (), "blocked_reason": "fixture inspection is not ready."}
    return {"fixture_id": fixture_id, "mapped": True, "import_targets": IMPORT_TARGETS, "blocked_reason": ""}


def validate_v5_2_real_fixture_import_config(config: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
        "local_fixture_only",
        "local_cache_only",
        "fixture_data_unverified",
        "imported_data_unverified",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_scraping",
        "no_api_calls",
        "no_browser_automation",
        "no_subprocess",
        "no_scheduler_creation",
        "no_broker_integration",
        "no_private_data_ingest",
    ):
        if config.get(field) is not True:
            blockers.append(f"{field} must be true.")
    for field in ("import_policy", "authorization_policy", "dry_run_output_policy", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("public_source_fixture_records", "import_mapping_rules", "operator_runbook_steps"):
        if not isinstance(config.get(field, []), list):
            blockers.append(f"{field} must be a list.")
    if not normalize_text(config.get("fixture_root")):
        blockers.append("fixture_root is required.")
    blockers.extend(_scan_for_forbidden_keys(config))
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)):
            blockers.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blockers.append(f"safety_controls.{field} must be true.")
    action = normalize_text(config.get("next_manual_action"))
    if action not in VALID_NEXT_MANUAL_ACTIONS:
        blockers.append("next_manual_action must be valid.")
    if action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blockers.append(f"next_manual_action must not be {action}.")
    policy = config.get("authorization_policy", {})
    if isinstance(policy, dict):
        expected = {
            "explicit_authorization_required": True,
            "default_write_allowed": False,
            "write_allowed_only_with_explicit_authorization": True,
            "local_fixture_only": True,
            "fixture_data_unverified": True,
            "imported_data_unverified": True,
            "no_fetching": True,
            "no_evidence_verification": True,
            "no_approval": True,
            "no_allocation": True,
            "no_trade": True,
            "no_executor": True,
        }
        for field, value in expected.items():
            if policy.get(field) is not value:
                blockers.append(f"authorization_policy.{field} must be {str(value).lower()}.")
        if policy.get("required_authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
            blockers.append("authorization_policy.required_authorization_phrase must match.")
    return tuple(dict.fromkeys(blockers))


def _should_use_inline_inspection(config: dict[str, Any], record: dict[str, Any]) -> bool:
    policy = config.get("import_policy", {})
    return bool(isinstance(policy, dict) and policy.get("allow_inline_synthetic_inspection") is True and isinstance(record.get("synthetic_inspection"), dict))


def evaluate_v5_2_real_fixture_import_dry_run(config: dict[str, Any]) -> V52RealFixtureImportDryRunResult:
    config_blockers = list(validate_v5_2_real_fixture_import_config(config))
    fixture_root = normalize_text(config.get("fixture_root")) or DEFAULT_FIXTURE_ROOT
    max_bytes = int(config.get("import_policy", {}).get("max_inspection_bytes", DEFAULT_MAX_BYTES)) if isinstance(config.get("import_policy"), dict) else DEFAULT_MAX_BYTES
    records = tuple(record for record in config.get("public_source_fixture_records", []) if isinstance(record, dict))
    fixture_ids = [normalize_text(record.get("fixture_id")) for record in records]
    duplicate_ids = tuple(dict.fromkeys(fixture_id for fixture_id in fixture_ids if fixture_id and fixture_ids.count(fixture_id) > 1))
    blockers: list[str] = list(config_blockers)
    warnings: list[str] = []
    for duplicate_id in duplicate_ids:
        blockers.append(f"duplicate fixture_id: {duplicate_id}")
    fixture_rows: list[dict[str, Any]] = []
    preview_rows: list[dict[str, Any]] = []
    mapping_rows: list[dict[str, Any]] = []
    for record in records:
        fixture_id = normalize_text(record.get("fixture_id")) or "missing"
        record_blockers = list(validate_import_fixture_record(record, fixture_root))
        if _should_use_inline_inspection(config, record):
            inspection = _inline_inspection(record)
        else:
            inspection = inspect_local_fixture_file(record, fixture_root, max_bytes=max_bytes)
        inspection_blockers = list(inspection.get("blockers", ()))
        record_blockers.extend(inspection_blockers)
        status = classify_import_status(record, inspection, normalize_text(config.get("current_date")))
        row_warnings = list(inspection.get("warnings", ()))
        if status == "MISSING":
            row_warnings.append("local fixture file is missing.")
        elif status == "STALE":
            row_warnings.append("fixture is stale and requires manual refresh.")
        elif status == "MANUAL_REFRESH_REQUIRED":
            row_warnings.append("fixture requires manual refresh.")
        elif status == "SKIPPED_IMPORT_DISABLED":
            row_warnings.append("fixture import disabled by operator.")
        if record_blockers:
            blockers.extend(f"{fixture_id}: {reason}" for reason in record_blockers)
        if row_warnings:
            warnings.extend(f"{fixture_id}: {warning}" for warning in row_warnings)
        preview = map_fixture_to_import_preview(record, inspection)
        mapping = map_import_preview_to_pipeline(record, inspection)
        if not mapping["mapped"] and status not in {"SKIPPED_IMPORT_DISABLED"}:
            warnings.append(f"{fixture_id}: {mapping['blocked_reason']}")
        fixture_rows.append(
            {
                "fixture_id": fixture_id,
                "source_category_id": record.get("source_category_id"),
                "fixture_format": record.get("fixture_format"),
                "expected_local_path": record.get("expected_local_path"),
                "import_enabled": record.get("import_enabled") is not False,
                "import_status": status,
                "exists": inspection.get("exists") is True,
                "size_bytes": inspection.get("size_bytes", 0),
                "sha256": inspection.get("sha256", ""),
                "metadata_type": inspection.get("metadata", {}).get("metadata_type", ""),
                "blocker_count": len(record_blockers),
                "warning_count": len(row_warnings),
            }
        )
        preview_rows.append(preview)
        mapping_rows.append(mapping)
    ordered_fixtures = tuple(sorted(fixture_rows, key=lambda row: row["fixture_id"]))
    ordered_previews = tuple(sorted(preview_rows, key=lambda row: row["fixture_id"]))
    ordered_mappings = tuple(sorted(mapping_rows, key=lambda row: row["fixture_id"]))
    blocker_tuple = tuple(dict.fromkeys(blockers))
    warning_tuple = tuple(dict.fromkeys(warnings))
    unsafe_count = sum(1 for row in ordered_fixtures if row["blocker_count"] > 0)
    missing_count = sum(1 for row in ordered_fixtures if row["import_status"] == "MISSING")
    stale_count = sum(1 for row in ordered_fixtures if row["import_status"] == "STALE")
    manual_refresh_count = sum(1 for row in ordered_fixtures if row["import_status"] == "MANUAL_REFRESH_REQUIRED")
    skipped_count = sum(1 for row in ordered_fixtures if row["import_status"] == "SKIPPED_IMPORT_DISABLED")
    unsupported_format_count = sum(1 for row in ordered_fixtures if normalize_text(row["fixture_format"]) not in SUPPORTED_FIXTURE_FORMATS)
    invalid_path_count = sum(1 for row in ordered_fixtures if "expected_local_path" in " ".join([b for b in blocker_tuple if b.startswith(row["fixture_id"])]))
    import_candidate_count = sum(1 for row in ordered_previews if row["import_enabled"])
    ready_import_count = sum(1 for row in ordered_previews if row["dry_run_import_preview"])
    shallow_metadata_count = sum(1 for row in ordered_previews if bool(row["shallow_metadata"]))
    hash_count = sum(1 for row in ordered_previews if bool(row["hash_fingerprint"]))
    mapped_count = sum(1 for row in ordered_mappings if row["mapped"])
    blocked_mapping_count = sum(1 for row in ordered_mappings if not row["mapped"])
    authorized = _authorization_valid(config)
    if config_blockers or unsafe_count or duplicate_ids or unsupported_format_count:
        status = "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE"
    elif not records or ready_import_count == 0:
        status = "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_PARTIAL_SAFE"
    elif missing_count or stale_count or manual_refresh_count or skipped_count or blocked_mapping_count:
        status = "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_PARTIAL_SAFE"
    elif authorized:
        status = "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_TO_WRITE_SAFE"
    else:
        status = "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_SAFE"
    return V52RealFixtureImportDryRunResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.2 Real Fixture Import Dry-Run",
        version=normalize_text(config.get("version")) or "v5.2",
        status=status,
        import_dry_run_mode=normalize_text(config.get("import_dry_run_mode")),
        fixture_count=len(records),
        import_candidate_count=import_candidate_count,
        ready_import_count=ready_import_count,
        skipped_import_count=skipped_count,
        missing_fixture_count=missing_count,
        stale_fixture_count=stale_count,
        manual_refresh_required_count=manual_refresh_count,
        invalid_path_count=invalid_path_count,
        unsupported_format_count=unsupported_format_count,
        unsafe_fixture_count=unsafe_count,
        duplicate_fixture_id_count=len(duplicate_ids),
        shallow_metadata_count=shallow_metadata_count,
        hash_fingerprint_count=hash_count,
        mapped_to_pipeline_count=mapped_count,
        blocked_mapping_count=blocked_mapping_count,
        fixture_rows=ordered_fixtures,
        import_preview_rows=ordered_previews,
        pipeline_mapping_rows=ordered_mappings,
        operator_runbook_steps=tuple(str(item) for item in config.get("operator_runbook_steps", []) if normalize_text(item)),
        blockers=blocker_tuple,
        warnings=warning_tuple,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = _normalized_path_text(path)
    if not text:
        return ("v5.2 import dry-run output root is required.",)
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if text in blocked_roots or text.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5.2 import dry-run output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def execute_authorized_v5_2_import_dry_run_snapshot_write(
    config: dict[str, Any],
    result: V52RealFixtureImportDryRunResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None and not _path_is_under(output_root, ALLOWED_OUTPUT_ROOT):
        blockers.append("path must stay under the configured v5.2 import dry-run output root.")
    if result.status not in {"V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_SAFE", "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_TO_WRITE_SAFE"}:
        blockers.append("import dry-run result must be ready before writing.")
    if blockers:
        return {"status": "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "snapshot_created_at": created_at,
        "status": result.status,
        "fixture_data_unverified": True,
        "imported_data_unverified": True,
        "fixture_rows": list(result.fixture_rows),
        "import_preview_rows": list(result.import_preview_rows),
        "pipeline_mapping_rows": list(result.pipeline_mapping_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_2_real_fixture_import_dry_run.snapshot.json"
    metadata_path = output_root / "jarvis_v5_2_real_fixture_import_dry_run.snapshot.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "snapshot_created_at": created_at,
        "content_sha256": digest,
        "fixture_count": result.fixture_count,
        "ready_import_count": result.ready_import_count,
        "fixture_data_unverified": True,
        "imported_data_unverified": True,
        "fetch_executed": False,
        "download_executed": False,
        "ocr": False,
        "pdf_parsing": False,
        "html_scraping": False,
        "evidence_verified": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "allocation_recommendation": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "registry_mutation": False,
        "executor_created": False,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "status": "V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_2_real_fixture_import_dry_run_summary(result: V52RealFixtureImportDryRunResult) -> str:
    return (
        f"status={result.status}; fixtures={result.fixture_count}; ready_imports={result.ready_import_count}; "
        f"missing={result.missing_fixture_count}; stale={result.stale_fixture_count}; skipped={result.skipped_import_count}; "
        f"unsafe={result.unsafe_fixture_count}; metadata={result.shallow_metadata_count}; hashes={result.hash_fingerprint_count}; "
        f"mapped={result.mapped_to_pipeline_count}"
    )


def load_v5_2_real_fixture_import_dry_run_result(path: str | Path) -> V52RealFixtureImportDryRunResult:
    return evaluate_v5_2_real_fixture_import_dry_run(load_json(path))
