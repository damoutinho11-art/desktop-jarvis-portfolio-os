"""Public source fixture wiring and operator runbook.

v5.1 prepares local public-source fixture metadata for the public research
pipeline. It is read-only by default and never fetches, downloads, scrapes,
extracts evidence, verifies evidence, approves assets, recommends, allocates,
trades, mutates registries, or creates an executor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_source_fixtures/v5_1")
DEFAULT_FIXTURE_ROOT = "jarvis/local/public_source_fixtures"
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
PIPELINE_STAGES = (
    "source_manifest",
    "fetch_dry_run_planner",
    "local_cache_builder",
    "cache_integrity_audit",
    "normalizer",
    "classifier",
    "research_queue",
    "draft_evidence_pack_generator",
    "operator_dashboard",
    "e2e_audit",
)
VALID_NEXT_MANUAL_ACTIONS = {
    "review_public_source_fixture_wiring",
    "prepare_local_public_source_fixtures",
    "proceed_to_v5_2_fixture_import_dry_run",
    "proceed_to_v5_2_explicit_authorized_public_fetch_stub",
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
    "live_fetch_adapter_inside_v5_1",
    "scraping",
    "evidence_verification",
    "broker_integration",
    "executor",
    "investment_recommendation",
    "allocation_engine",
    "registry_mutation",
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
    "fixture_wiring_only",
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
FORBIDDEN_RECORD_KEYS = (
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


@dataclass(frozen=True)
class V51PublicSourceFixtureWiringResult:
    title: str
    version: str
    status: str
    fixture_wiring_mode: str
    fixture_count: int
    ready_fixture_count: int
    missing_fixture_count: int
    stale_fixture_count: int
    manual_refresh_required_count: int
    invalid_path_count: int
    unsupported_format_count: int
    unsafe_fixture_count: int
    duplicate_fixture_id_count: int
    mapped_to_pipeline_count: int
    blocked_mapping_count: int
    fixture_rows: tuple[dict[str, Any], ...]
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
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_approval: bool = True
    no_recommendation: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_fixture_only: bool = True
    fixture_data_unverified: bool = True


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


def _fixture_root(config: dict[str, Any]) -> str:
    policy = config.get("fixture_root_policy", {})
    if isinstance(policy, dict):
        return normalize_text(policy.get("fixture_root")) or DEFAULT_FIXTURE_ROOT
    return DEFAULT_FIXTURE_ROOT


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


def validate_fixture_path(path: str | Path, fixture_root: str | Path) -> tuple[str, ...]:
    blockers: list[str] = []
    text = _normalized_path_text(path)
    if not text:
        return ("expected_local_path is required.",)
    blocked_roots = ("docs", "templates", "jarvis/data", "registry", "candidate_assets")
    if text in {".", ""} or any(text == root or text.startswith(root + "/") for root in blocked_roots):
        blockers.append("expected_local_path must not target docs, templates, jarvis/data, registry, candidate files, or repo root.")
    if not _path_is_under(text, fixture_root):
        blockers.append("expected_local_path must stay under the configured public source fixture root.")
    return tuple(dict.fromkeys(blockers))


def _scan_for_forbidden_keys(value: Any, prefix: str = "") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = normalize_text(key).lower()
            full_key = f"{prefix}.{key_text}" if prefix else key_text
            if any(forbidden in key_text for forbidden in FORBIDDEN_RECORD_KEYS):
                blockers.append(f"forbidden private/credential field present: {full_key}")
            blockers.extend(_scan_for_forbidden_keys(nested, full_key))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            blockers.extend(_scan_for_forbidden_keys(nested, f"{prefix}[{index}]"))
    return tuple(blockers)


def validate_public_source_fixture_record(record: dict[str, Any], fixture_root: str | Path) -> tuple[str, ...]:
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
    blockers.extend(validate_fixture_path(record.get("expected_local_path", ""), fixture_root))
    if record.get("public_only") is not True:
        blockers.append("public_only must be true.")
    for field in FORBIDDEN_RECORD_TRUE_FIELDS:
        if record.get(field) is True:
            blockers.append(f"{field} must be false.")
    blockers.extend(_scan_for_forbidden_keys(record))
    return tuple(dict.fromkeys(blockers))


def classify_fixture_status(record: dict[str, Any], current_date: str | None = None) -> str:
    status = normalize_text(record.get("fixture_status")).upper()
    if status in {"READY", "MISSING", "STALE", "MANUAL_REFRESH_REQUIRED", "INVALID"}:
        return status
    if record.get("fixture_present") is False:
        return "MISSING"
    if record.get("stale") is True or normalize_text(record.get("data_freshness_status")).upper() in {"STALE", "CACHE_STALE_SAFE"}:
        return "STALE"
    if record.get("manual_refresh_required") is True:
        return "MANUAL_REFRESH_REQUIRED"
    return "READY"


def map_fixture_to_pipeline(record: dict[str, Any]) -> dict[str, Any]:
    category = normalize_text(record.get("source_category_id"))
    fixture_id = normalize_text(record.get("fixture_id"))
    if category not in SUPPORTED_SOURCE_CATEGORIES:
        return {
            "fixture_id": fixture_id,
            "source_category_id": category,
            "mapped": False,
            "pipeline_stages": (),
            "blocked_reason": "unsupported source category cannot be mapped.",
        }
    return {
        "fixture_id": fixture_id,
        "source_category_id": category,
        "mapped": True,
        "pipeline_stages": PIPELINE_STAGES,
        "blocked_reason": "",
    }


def validate_v5_1_fixture_wiring_config(config: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
        "local_fixture_only",
        "local_cache_only",
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
    for field in ("fixture_policy", "authorization_policy", "fixture_root_policy", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("accepted_fixture_formats", "public_source_fixture_records", "pipeline_mapping_rules", "operator_runbook_steps"):
        if not isinstance(config.get(field, []), list):
            blockers.append(f"{field} must be a list.")
    formats = {normalize_text(item) for item in config.get("accepted_fixture_formats", []) if normalize_text(item)}
    if formats and not formats.issubset(SUPPORTED_FIXTURE_FORMATS):
        blockers.append("accepted_fixture_formats contains unsupported formats.")
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


def evaluate_v5_1_public_source_fixture_wiring(config: dict[str, Any]) -> V51PublicSourceFixtureWiringResult:
    config_blockers = list(validate_v5_1_fixture_wiring_config(config))
    fixture_root = _fixture_root(config)
    records = tuple(record for record in config.get("public_source_fixture_records", []) if isinstance(record, dict))
    fixture_ids = [normalize_text(record.get("fixture_id")) for record in records]
    duplicates = tuple(fixture_id for fixture_id in fixture_ids if fixture_id and fixture_ids.count(fixture_id) > 1)
    duplicate_ids = tuple(dict.fromkeys(duplicates))
    fixture_rows: list[dict[str, Any]] = []
    mapping_rows: list[dict[str, Any]] = []
    blockers: list[str] = list(config_blockers)
    warnings: list[str] = []
    for duplicate_id in duplicate_ids:
        blockers.append(f"duplicate fixture_id: {duplicate_id}")
    for record in records:
        fixture_id = normalize_text(record.get("fixture_id")) or "missing"
        row_blockers = list(validate_public_source_fixture_record(record, fixture_root))
        row_warnings: list[str] = []
        status = classify_fixture_status(record, normalize_text(config.get("current_date")))
        if status == "MISSING":
            row_warnings.append("fixture is missing and must be manually placed.")
        elif status == "STALE":
            row_warnings.append("fixture is stale and requires manual refresh.")
        elif status == "MANUAL_REFRESH_REQUIRED":
            row_warnings.append("fixture requires manual refresh.")
        if row_blockers:
            blockers.extend(f"{fixture_id}: {reason}" for reason in row_blockers)
        if row_warnings:
            warnings.extend(f"{fixture_id}: {warning}" for warning in row_warnings)
        mapping = map_fixture_to_pipeline(record)
        if not mapping["mapped"]:
            blockers.append(f"{fixture_id}: {mapping['blocked_reason']}")
        mapping_rows.append(mapping)
        fixture_rows.append(
            {
                "fixture_id": fixture_id,
                "source_id": record.get("source_id"),
                "source_category_id": record.get("source_category_id"),
                "fixture_format": record.get("fixture_format"),
                "expected_local_path": record.get("expected_local_path"),
                "fixture_status": status,
                "ready": status == "READY" and not row_blockers,
                "blocker_count": len(row_blockers),
                "warning_count": len(row_warnings),
                "mapped_to_pipeline": mapping["mapped"],
                "source_verified_by_operator": record.get("source_verified_by_operator") is True,
                "evidence_verified": False,
                "downloaded_by_jarvis": False,
            }
        )
    ordered_rows = tuple(sorted(fixture_rows, key=lambda row: row["fixture_id"]))
    ordered_mappings = tuple(sorted(mapping_rows, key=lambda row: row["fixture_id"]))
    blocker_tuple = tuple(dict.fromkeys(blockers))
    warning_tuple = tuple(dict.fromkeys(warnings))
    ready_count = sum(1 for row in ordered_rows if row["ready"])
    missing_count = sum(1 for row in ordered_rows if row["fixture_status"] == "MISSING")
    stale_count = sum(1 for row in ordered_rows if row["fixture_status"] == "STALE")
    manual_refresh_count = sum(1 for row in ordered_rows if row["fixture_status"] == "MANUAL_REFRESH_REQUIRED")
    invalid_path_count = sum(1 for row in ordered_rows if "expected_local_path" in " ".join([b for b in blocker_tuple if b.startswith(row["fixture_id"])]))
    unsupported_format_count = sum(1 for row in ordered_rows if normalize_text(row["fixture_format"]) not in SUPPORTED_FIXTURE_FORMATS)
    unsafe_fixture_count = sum(1 for row in ordered_rows if row["blocker_count"] > 0)
    blocked_mapping_count = sum(1 for row in ordered_mappings if not row["mapped"])
    authorized = _authorization_valid(config)
    if config_blockers or unsafe_fixture_count or duplicate_ids:
        status = "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE"
    elif not records or ready_count == 0:
        status = "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE"
    elif missing_count or stale_count or manual_refresh_count or blocked_mapping_count:
        status = "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_PARTIAL_SAFE"
    elif authorized:
        status = "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_TO_WRITE_SAFE"
    else:
        status = "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_SAFE"
    return V51PublicSourceFixtureWiringResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.1 Public Source Fixture Wiring",
        version=normalize_text(config.get("version")) or "v5.1",
        status=status,
        fixture_wiring_mode=normalize_text(config.get("fixture_wiring_mode")),
        fixture_count=len(records),
        ready_fixture_count=ready_count,
        missing_fixture_count=missing_count,
        stale_fixture_count=stale_count,
        manual_refresh_required_count=manual_refresh_count,
        invalid_path_count=invalid_path_count,
        unsupported_format_count=unsupported_format_count,
        unsafe_fixture_count=unsafe_fixture_count,
        duplicate_fixture_id_count=len(duplicate_ids),
        mapped_to_pipeline_count=sum(1 for row in ordered_mappings if row["mapped"]),
        blocked_mapping_count=blocked_mapping_count,
        fixture_rows=ordered_rows,
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
        return ("v5.1 fixture wiring output root is required.",)
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if text in blocked_roots or text.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5.1 fixture wiring output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute_authorized_v5_1_fixture_wiring_snapshot_write(
    config: dict[str, Any],
    result: V51PublicSourceFixtureWiringResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None and not _path_is_under(output_root, ALLOWED_OUTPUT_ROOT):
        blockers.append("path must stay under the configured v5.1 fixture wiring output root.")
    if result.status not in {"V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_SAFE", "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_READY_TO_WRITE_SAFE"}:
        blockers.append("fixture wiring result must be ready before writing.")
    if blockers:
        return {"status": "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "snapshot_created_at": created_at,
        "status": result.status,
        "fixture_data_unverified": True,
        "fixture_count": result.fixture_count,
        "ready_fixture_count": result.ready_fixture_count,
        "fixture_rows": list(result.fixture_rows),
        "pipeline_mapping_rows": list(result.pipeline_mapping_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_1_public_source_fixture_wiring.snapshot.json"
    metadata_path = output_root / "jarvis_v5_1_public_source_fixture_wiring.snapshot.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "snapshot_created_at": created_at,
        "fixture_count": result.fixture_count,
        "ready_fixture_count": result.ready_fixture_count,
        "content_sha256": digest,
        "fixture_data_unverified": True,
        "fetch_executed": False,
        "download_executed": False,
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
        "status": "V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_1_public_source_fixture_wiring_summary(result: V51PublicSourceFixtureWiringResult) -> str:
    return (
        f"status={result.status}; fixtures={result.fixture_count}; ready={result.ready_fixture_count}; "
        f"missing={result.missing_fixture_count}; stale={result.stale_fixture_count}; "
        f"manual_refresh={result.manual_refresh_required_count}; unsafe={result.unsafe_fixture_count}; "
        f"mapped={result.mapped_to_pipeline_count}; blocked_mapping={result.blocked_mapping_count}"
    )


def load_v5_1_public_source_fixture_wiring_result(path: str | Path) -> V51PublicSourceFixtureWiringResult:
    return evaluate_v5_1_public_source_fixture_wiring(load_json(path))
