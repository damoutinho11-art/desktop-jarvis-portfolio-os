"""Operator fixture review queue for v5.3.

v5.3 consumes v5.2 import-preview metadata and builds a manual operator review
queue. It does not read fixture files, fetch, scrape, parse HTML/PDF, verify
evidence, approve assets, recommend allocations, mutate registries, trade, or
create an executor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_source_fixtures/v5_3_operator_review_queue")
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
VALID_NEXT_MANUAL_ACTIONS = {
    "review_operator_fixture_queue",
    "fix_rejected_fixture_metadata",
    "prepare_missing_local_public_fixtures",
    "refresh_stale_public_fixtures",
    "proceed_to_v5_4_research_draft_source_router",
    "proceed_to_v5_4_explicit_authorized_public_fetch_stub",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "live_fetch_now",
    "evidence_verification",
    "approval",
    "trust_asset",
    "mark_investable",
    "registry_mutation",
    "allocation_recommendation",
    "trade_execution",
    "executor_creation",
}
BLOCKED_NEXT_STAGES = (
    "evidence_verification",
    "approval",
    "trust",
    "investability",
    "registry_mutation",
    "recommendation",
    "allocation",
    "trade",
    "executor",
)
DO_NOT_BUILD_NEXT = (
    "live_fetch_adapter_inside_v5_3",
    "scraping",
    "ocr",
    "pdf_parsing",
    "html_scraping",
    "evidence_verification",
    "asset_approval",
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
    "manual_operator_review_required",
    "no_execution_invariant",
    "final_purchase_external_manual_only",
    "local_fixture_only",
    "fixture_data_unverified",
    "imported_data_unverified",
    "review_queue_unverified",
    "dry_run_only",
    "review_queue_only",
)
FORBIDDEN_ROW_TRUE_FIELDS = (
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


@dataclass(frozen=True)
class V53OperatorFixtureReviewQueueResult:
    title: str
    version: str
    status: str
    operator_fixture_review_queue_mode: str
    import_preview_count: int
    review_queue_count: int
    accepted_for_research_draft_only_count: int
    needs_operator_review_count: int
    deferred_count: int
    rejected_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    unsafe_count: int
    unsupported_format_count: int
    unsupported_category_count: int
    duplicate_fixture_id_count: int
    private_or_credential_risk_count: int
    forbidden_flag_count: int
    missing_fixture_count: int
    stale_fixture_count: int
    manual_refresh_required_count: int
    review_rows: tuple[dict[str, Any], ...]
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
    review_queue_unverified: bool = True
    manual_operator_review_required: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def _row_private_or_credential_risk(row: dict[str, Any]) -> bool:
    return row.get("credential_or_private_risk") is True or bool(_scan_for_forbidden_keys(row))


def validate_import_preview_row(row: dict[str, Any]) -> tuple[str, ...]:
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
        "import_status",
    ):
        if not normalize_text(row.get(field)):
            blockers.append(f"{field} is required.")
    if normalize_text(row.get("source_category_id")) not in SUPPORTED_SOURCE_CATEGORIES:
        blockers.append(f"unsupported source_category_id: {normalize_text(row.get('source_category_id')) or 'missing'}")
    if normalize_text(row.get("fixture_format")) not in SUPPORTED_FIXTURE_FORMATS:
        blockers.append(f"unsupported fixture_format: {normalize_text(row.get('fixture_format')) or 'missing'}")
    if row.get("public_only") is not True:
        blockers.append("public_only must be true.")
    if row.get("credential_or_private_risk") is True:
        blockers.append("credential_or_private_risk must be false.")
    for field in FORBIDDEN_ROW_TRUE_FIELDS:
        if row.get(field) is True:
            blockers.append(f"{field} must be false.")
    blockers.extend(_scan_for_forbidden_keys(row))
    return tuple(dict.fromkeys(blockers))


def evaluate_import_preview_row_for_review(row: dict[str, Any]) -> str:
    validation_text = " ".join(validate_import_preview_row(row))
    if row.get("duplicate_fixture_id") is True:
        return "rejected_duplicate_fixture_id"
    if row.get("credential_or_private_risk") is True or "forbidden private/credential field" in validation_text:
        return "rejected_private_or_credential_risk"
    if row.get("public_only") is not True:
        return "rejected_not_public_only"
    if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS):
        return "rejected_forbidden_flags"
    if row.get("unsafe_path") is True:
        return "rejected_unsafe_path"
    if row.get("unsupported_format") is True or normalize_text(row.get("fixture_format")) not in SUPPORTED_FIXTURE_FORMATS:
        return "rejected_unsupported_format"
    if row.get("unsupported_category") is True or normalize_text(row.get("source_category_id")) not in SUPPORTED_SOURCE_CATEGORIES:
        return "rejected_unsupported_category"
    import_status = normalize_text(row.get("import_status")).upper()
    if row.get("missing_fixture") is True or import_status == "MISSING":
        return "deferred_missing_file"
    if row.get("stale_fixture") is True or import_status == "STALE":
        return "deferred_stale_fixture"
    if row.get("manual_refresh_required") is True or import_status == "MANUAL_REFRESH_REQUIRED":
        return "deferred_manual_refresh_required"
    if row.get("import_enabled") is False:
        return "needs_operator_review"
    return "needs_operator_review"


def assign_review_priority(row: dict[str, Any], decision: str) -> str:
    if decision.startswith("rejected_") or decision.startswith("deferred_"):
        return "high"
    if row.get("import_enabled") is False:
        return "low"
    return "medium"


def _allowed_next_stage(decision: str) -> str:
    if decision == "accepted_for_research_draft_only":
        return "research_draft_source_router_only"
    if decision == "deferred_missing_file":
        return "missing_fixture_preparation"
    if decision in {"deferred_stale_fixture", "deferred_manual_refresh_required"}:
        return "manual_fixture_refresh"
    if decision == "needs_operator_review":
        return "manual_fixture_metadata_fix"
    return "stop_blocked_safe"


def build_review_queue_row(row: dict[str, Any], decision: str, priority: str, index: int) -> dict[str, Any]:
    review_id = f"operator_fixture_review::{normalize_text(row.get('fixture_id')) or index:}"
    reason_by_decision = {
        "needs_operator_review": "operator must manually review fixture metadata before research-draft routing.",
        "accepted_for_research_draft_only": "fixture metadata is accepted only as an unverified research draft source reference.",
        "deferred_missing_file": "fixture import preview indicates the local public fixture is missing.",
        "deferred_stale_fixture": "fixture import preview indicates stale fixture metadata.",
        "deferred_manual_refresh_required": "fixture import preview requires manual refresh.",
        "rejected_unsafe_path": "fixture path is unsafe for public fixture review.",
        "rejected_unsupported_format": "fixture format is unsupported.",
        "rejected_unsupported_category": "fixture source category is unsupported.",
        "rejected_forbidden_flags": "fixture row contains forbidden true safety flags.",
        "rejected_duplicate_fixture_id": "fixture id is duplicated.",
        "rejected_private_or_credential_risk": "fixture row contains private or credential risk.",
        "rejected_not_public_only": "fixture row is not marked public_only true.",
    }
    return {
        "review_id": review_id,
        "fixture_id": normalize_text(row.get("fixture_id")),
        "source_id": normalize_text(row.get("source_id")),
        "source_name": normalize_text(row.get("source_name")),
        "source_category_id": normalize_text(row.get("source_category_id")),
        "fixture_format": normalize_text(row.get("fixture_format")),
        "review_priority": priority,
        "review_decision": decision,
        "review_reason": reason_by_decision.get(decision, "operator review required."),
        "required_operator_action": _allowed_next_stage(decision),
        "allowed_next_stage": _allowed_next_stage(decision),
        "blocked_next_stage": BLOCKED_NEXT_STAGES,
        "evidence_verified": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "recommendation": False,
        "allocation": False,
        "trade": False,
        "executor": False,
    }


def validate_v5_3_operator_fixture_review_queue_config(config: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
        "local_fixture_only",
        "local_cache_only",
        "fixture_data_unverified",
        "imported_data_unverified",
        "review_queue_unverified",
        "manual_operator_review_required",
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
    for field in ("review_queue_policy", "authorization_policy", "dry_run_output_policy", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("import_preview_rows", "review_decision_rules", "operator_runbook_steps"):
        if not isinstance(config.get(field, []), list):
            blockers.append(f"{field} must be a list.")
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
            "review_queue_unverified": True,
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


def _auto_accept_enabled(config: dict[str, Any]) -> bool:
    policy = config.get("review_queue_policy", {})
    return isinstance(policy, dict) and policy.get("auto_accept_for_research_draft_only") is True


def evaluate_v5_3_operator_fixture_review_queue(config: dict[str, Any]) -> V53OperatorFixtureReviewQueueResult:
    config_blockers = list(validate_v5_3_operator_fixture_review_queue_config(config))
    rows = tuple(row for row in config.get("import_preview_rows", []) if isinstance(row, dict))
    ids = [normalize_text(row.get("fixture_id")) for row in rows]
    duplicate_ids = tuple(dict.fromkeys(fixture_id for fixture_id in ids if fixture_id and ids.count(fixture_id) > 1))
    blockers: list[str] = list(config_blockers)
    warnings: list[str] = []
    for duplicate_id in duplicate_ids:
        blockers.append(f"duplicate fixture_id: {duplicate_id}")
    review_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        fixture_id = normalize_text(row.get("fixture_id")) or f"missing_{index}"
        row_blockers = list(validate_import_preview_row(row))
        duplicate = fixture_id in duplicate_ids or row.get("duplicate_fixture_id") is True
        if duplicate:
            row["duplicate_fixture_id"] = True
        decision = evaluate_import_preview_row_for_review(row)
        if decision == "needs_operator_review" and _auto_accept_enabled(config):
            ready = (
                normalize_text(row.get("import_status")).upper() == "READY"
                and row.get("import_enabled") is not False
                and row.get("hash_fingerprint_present") is True
                and row.get("shallow_metadata_present") is True
                and not row_blockers
                and not duplicate
            )
            if ready:
                decision = "accepted_for_research_draft_only"
        priority = assign_review_priority(row, decision)
        if row_blockers:
            blockers.extend(f"{fixture_id}: {reason}" for reason in row_blockers)
        if decision.startswith("deferred_"):
            warnings.append(f"{fixture_id}: {decision}")
        review_rows.append(build_review_queue_row(row, decision, priority, index))
    ordered_rows = tuple(sorted(review_rows, key=lambda row: row["review_id"]))
    blocker_tuple = tuple(dict.fromkeys(blockers))
    warning_tuple = tuple(dict.fromkeys(warnings))
    decision_counts = {decision: sum(1 for row in ordered_rows if row["review_decision"] == decision) for decision in {row["review_decision"] for row in ordered_rows}}
    rejected_count = sum(1 for row in ordered_rows if row["review_decision"].startswith("rejected_"))
    deferred_count = sum(1 for row in ordered_rows if row["review_decision"].startswith("deferred_"))
    forbidden_flag_count = sum(1 for row in rows if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS))
    private_or_credential_count = sum(1 for row in rows if _row_private_or_credential_risk(row))
    unsafe_count = sum(1 for row in rows if row.get("unsafe_path") is True)
    unsupported_format_count = sum(1 for row in rows if row.get("unsupported_format") is True or normalize_text(row.get("fixture_format")) not in SUPPORTED_FIXTURE_FORMATS)
    unsupported_category_count = sum(1 for row in rows if row.get("unsupported_category") is True or normalize_text(row.get("source_category_id")) not in SUPPORTED_SOURCE_CATEGORIES)
    missing_count = sum(1 for row in rows if row.get("missing_fixture") is True or normalize_text(row.get("import_status")).upper() == "MISSING")
    stale_count = sum(1 for row in rows if row.get("stale_fixture") is True or normalize_text(row.get("import_status")).upper() == "STALE")
    manual_refresh_count = sum(1 for row in rows if row.get("manual_refresh_required") is True or normalize_text(row.get("import_status")).upper() == "MANUAL_REFRESH_REQUIRED")
    hard_block = bool(config_blockers or blocker_tuple or rejected_count or private_or_credential_count or forbidden_flag_count or unsupported_format_count or unsupported_category_count or duplicate_ids or unsafe_count)
    authorized = _authorization_valid(config)
    if hard_block:
        status = "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE"
    elif not rows or deferred_count:
        status = "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_PARTIAL_SAFE"
    elif authorized:
        status = "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_TO_WRITE_SAFE"
    else:
        status = "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_SAFE"
    return V53OperatorFixtureReviewQueueResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.3 Operator Fixture Review Queue",
        version=normalize_text(config.get("version")) or "v5.3",
        status=status,
        operator_fixture_review_queue_mode=normalize_text(config.get("operator_fixture_review_queue_mode")),
        import_preview_count=len(rows),
        review_queue_count=len(ordered_rows),
        accepted_for_research_draft_only_count=decision_counts.get("accepted_for_research_draft_only", 0),
        needs_operator_review_count=decision_counts.get("needs_operator_review", 0),
        deferred_count=deferred_count,
        rejected_count=rejected_count,
        high_priority_count=sum(1 for row in ordered_rows if row["review_priority"] == "high"),
        medium_priority_count=sum(1 for row in ordered_rows if row["review_priority"] == "medium"),
        low_priority_count=sum(1 for row in ordered_rows if row["review_priority"] == "low"),
        unsafe_count=unsafe_count,
        unsupported_format_count=unsupported_format_count,
        unsupported_category_count=unsupported_category_count,
        duplicate_fixture_id_count=len(duplicate_ids) + sum(1 for row in rows if row.get("duplicate_fixture_id") is True and normalize_text(row.get("fixture_id")) not in duplicate_ids),
        private_or_credential_risk_count=private_or_credential_count,
        forbidden_flag_count=forbidden_flag_count,
        missing_fixture_count=missing_count,
        stale_fixture_count=stale_count,
        manual_refresh_required_count=manual_refresh_count,
        review_rows=ordered_rows,
        operator_runbook_steps=tuple(str(item) for item in config.get("operator_runbook_steps", []) if normalize_text(item)),
        blockers=blocker_tuple,
        warnings=warning_tuple,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = _normalized_path_text(path)
    if not text:
        return ("v5.3 review queue output root is required.",)
    if text in {"docs", "templates", "jarvis/data", "."} or text.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5.3 review queue output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def execute_authorized_v5_3_review_queue_snapshot_write(
    config: dict[str, Any],
    result: V53OperatorFixtureReviewQueueResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None and not _path_is_under(output_root, ALLOWED_OUTPUT_ROOT):
        blockers.append("path must stay under the configured v5.3 review queue output root.")
    if result.status not in {"V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_SAFE", "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_TO_WRITE_SAFE"}:
        blockers.append("review queue result must be ready before writing.")
    if blockers:
        return {"status": "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "snapshot_created_at": created_at,
        "status": result.status,
        "review_queue_unverified": True,
        "manual_operator_review_required": True,
        "review_rows": list(result.review_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_3_operator_fixture_review_queue.snapshot.json"
    metadata_path = output_root / "jarvis_v5_3_operator_fixture_review_queue.snapshot.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "snapshot_created_at": created_at,
        "content_sha256": _sha256_bytes(raw_bytes),
        "review_queue_count": result.review_queue_count,
        "accepted_for_research_draft_only_count": result.accepted_for_research_draft_only_count,
        "review_queue_unverified": True,
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
        "status": "V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_3_operator_fixture_review_queue_summary(result: V53OperatorFixtureReviewQueueResult) -> str:
    return (
        f"status={result.status}; import_previews={result.import_preview_count}; queue={result.review_queue_count}; "
        f"accepted={result.accepted_for_research_draft_only_count}; needs_review={result.needs_operator_review_count}; "
        f"deferred={result.deferred_count}; rejected={result.rejected_count}; high={result.high_priority_count}; "
        f"medium={result.medium_priority_count}; low={result.low_priority_count}"
    )


def load_v5_3_operator_fixture_review_queue_result(path: str | Path) -> V53OperatorFixtureReviewQueueResult:
    return evaluate_v5_3_operator_fixture_review_queue(load_json(path))
