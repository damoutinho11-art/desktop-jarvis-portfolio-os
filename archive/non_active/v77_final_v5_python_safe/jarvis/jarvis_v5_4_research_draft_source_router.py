"""Research draft source router for v5.4.

v5.4 consumes v5.3 operator fixture review-row metadata and routes safe,
accepted fixture metadata into unverified research-draft source references only.
It does not read external fixture files, fetch, scrape, parse source content,
verify evidence, approve assets, recommend allocations, mutate registries,
trade, or create an executor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_source_fixtures/v5_4_research_draft_source_router")
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
ROUTEABLE_REVIEW_DECISIONS = {"accepted_for_research_draft_only", "needs_operator_review"}
DEFERRED_REVIEW_DECISIONS = {"deferred_missing_file", "deferred_stale_fixture", "deferred_manual_refresh_required"}
REJECTED_REVIEW_DECISIONS = {
    "rejected_unsafe_path",
    "rejected_unsupported_format",
    "rejected_unsupported_category",
    "rejected_forbidden_flags",
    "rejected_duplicate_fixture_id",
    "rejected_private_or_credential_risk",
    "rejected_not_public_only",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_research_draft_source_routes",
    "fix_blocked_source_references",
    "refresh_deferred_public_fixtures",
    "proceed_to_v5_5_public_research_packet_draft_assembler",
    "proceed_to_v5_5_explicit_authorized_public_fetch_stub",
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
ALLOWED_DOWNSTREAM_USE = (
    "research_packet_draft_source_reference_only",
    "manual_source_review_context_only",
    "operator_dashboard_reference_only",
)
BLOCKED_DOWNSTREAM_USE = (
    "evidence_verification",
    "source_truth_verification",
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
    "live_fetch_adapter_inside_v5_4",
    "scraping",
    "ocr",
    "pdf_parsing",
    "html_scraping",
    "evidence_verification",
    "source_truth_verification",
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
    "external_file_read",
    "evidence_extraction",
    "evidence_verification",
    "source_truth_verification",
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
    "research_draft_sources_unverified",
    "dry_run_only",
    "source_router_only",
)
FORBIDDEN_ROW_TRUE_FIELDS = (
    "downloaded_by_jarvis",
    "evidence_verified",
    "approved_asset",
    "trusted_asset",
    "investable",
    "recommendation",
    "allocation",
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
class V54ResearchDraftSourceRouterResult:
    title: str
    version: str
    status: str
    research_draft_source_router_mode: str
    review_row_count: int
    source_route_count: int
    routed_reference_count: int
    pending_operator_review_count: int
    deferred_route_count: int
    blocked_route_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    unsafe_count: int
    unsupported_format_count: int
    unsupported_category_count: int
    duplicate_review_id_count: int
    duplicate_fixture_id_count: int
    private_or_credential_risk_count: int
    forbidden_flag_count: int
    missing_fixture_count: int
    stale_fixture_count: int
    manual_refresh_required_count: int
    route_rows: tuple[dict[str, Any], ...]
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
    no_external_file_read: bool = True
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_source_truth_verification: bool = True
    no_approval: bool = True
    no_recommendation: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_fixture_only: bool = True
    fixture_data_unverified: bool = True
    imported_data_unverified: bool = True
    review_queue_unverified: bool = True
    research_draft_sources_unverified: bool = True
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


def validate_review_row(row: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "review_id",
        "fixture_id",
        "source_id",
        "source_name",
        "source_category_id",
        "asset_universe",
        "fixture_type",
        "fixture_format",
        "expected_local_path",
        "review_decision",
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


def evaluate_review_row_for_source_routing(row: dict[str, Any], router_policy: dict[str, Any] | None = None) -> str:
    validation_text = " ".join(validate_review_row(row))
    if row.get("duplicate_review_id") is True or row.get("duplicate_fixture_id") is True:
        return "block_duplicate_fixture_id"
    if row.get("credential_or_private_risk") is True or "forbidden private/credential field" in validation_text:
        return "block_private_or_credential_risk"
    if row.get("public_only") is not True:
        return "block_not_public_only"
    if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS):
        return "block_forbidden_flags"
    if row.get("unsafe_path") is True:
        return "block_unsafe_path"
    if row.get("unsupported_format") is True or normalize_text(row.get("fixture_format")) not in SUPPORTED_FIXTURE_FORMATS:
        return "block_unsupported_format"
    if row.get("unsupported_category") is True or normalize_text(row.get("source_category_id")) not in SUPPORTED_SOURCE_CATEGORIES:
        return "block_unsupported_category"
    review_decision = normalize_text(row.get("review_decision"))
    if row.get("missing_fixture") is True or review_decision == "deferred_missing_file":
        return "defer_missing_file"
    if row.get("stale_fixture") is True or review_decision == "deferred_stale_fixture":
        return "defer_stale_fixture"
    if row.get("manual_refresh_required") is True or review_decision == "deferred_manual_refresh_required":
        return "defer_manual_refresh_required"
    if review_decision in REJECTED_REVIEW_DECISIONS:
        return {
            "rejected_unsafe_path": "block_unsafe_path",
            "rejected_unsupported_format": "block_unsupported_format",
            "rejected_unsupported_category": "block_unsupported_category",
            "rejected_forbidden_flags": "block_forbidden_flags",
            "rejected_duplicate_fixture_id": "block_duplicate_fixture_id",
            "rejected_private_or_credential_risk": "block_private_or_credential_risk",
            "rejected_not_public_only": "block_not_public_only",
        }[review_decision]
    if review_decision == "accepted_for_research_draft_only":
        return "route_to_research_draft_reference_only"
    if review_decision == "needs_operator_review":
        if isinstance(router_policy, dict) and router_policy.get("allow_pending_operator_review_reference") is True:
            return "route_to_research_draft_reference_only"
        return "block_not_operator_accepted"
    return "block_not_operator_accepted"


def assign_route_priority(row: dict[str, Any], decision: str) -> str:
    if decision == "block_not_operator_accepted":
        return "medium"
    if decision.startswith("block_") or decision.startswith("defer_"):
        return "high"
    return "low"


def _source_reference_type(decision: str) -> str:
    if decision == "route_to_research_draft_reference_only":
        return "research_draft_source_reference"
    if decision in {"defer_missing_file", "defer_stale_fixture"}:
        return "deferred_source_reference"
    if decision == "defer_manual_refresh_required":
        return "manual_refresh_required_reference"
    if decision == "block_not_operator_accepted":
        return "manual_fix_required_reference"
    return "blocked_source_reference"


def _required_operator_action(decision: str) -> str:
    if decision == "route_to_research_draft_reference_only":
        return "review_research_draft_source_routes"
    if decision == "defer_missing_file":
        return "prepare_missing_local_public_fixtures"
    if decision in {"defer_stale_fixture", "defer_manual_refresh_required"}:
        return "refresh_deferred_public_fixtures"
    return "fix_blocked_source_references"


def build_source_route_row(row: dict[str, Any], decision: str, priority: str, index: int) -> dict[str, Any]:
    route_id = f"research_draft_source_route::{normalize_text(row.get('review_id')) or index}"
    reasons = {
        "route_to_research_draft_reference_only": "operator-accepted metadata may be referenced in future research-draft preparation only.",
        "defer_missing_file": "review row indicates missing fixture metadata.",
        "defer_stale_fixture": "review row indicates stale fixture metadata.",
        "defer_manual_refresh_required": "review row requires manual fixture refresh.",
        "block_unsafe_path": "unsafe path blocks research-draft source routing.",
        "block_unsupported_format": "unsupported format blocks research-draft source routing.",
        "block_unsupported_category": "unsupported source category blocks research-draft source routing.",
        "block_forbidden_flags": "forbidden safety flags block routing.",
        "block_duplicate_fixture_id": "duplicate review or fixture id blocks routing.",
        "block_private_or_credential_risk": "private or credential risk blocks routing.",
        "block_not_public_only": "non-public fixture metadata blocks routing.",
        "block_not_operator_accepted": "operator has not accepted this row for research-draft-only routing.",
    }
    return {
        "route_id": route_id,
        "review_id": normalize_text(row.get("review_id")),
        "fixture_id": normalize_text(row.get("fixture_id")),
        "source_id": normalize_text(row.get("source_id")),
        "source_name": normalize_text(row.get("source_name")),
        "source_category_id": normalize_text(row.get("source_category_id")),
        "asset_universe": normalize_text(row.get("asset_universe")),
        "fixture_type": normalize_text(row.get("fixture_type")),
        "fixture_format": normalize_text(row.get("fixture_format")),
        "route_decision": decision,
        "route_reason": reasons.get(decision, "route decision requires manual review."),
        "route_priority": priority,
        "source_reference_type": _source_reference_type(decision),
        "allowed_downstream_use": ALLOWED_DOWNSTREAM_USE,
        "blocked_downstream_use": BLOCKED_DOWNSTREAM_USE,
        "required_operator_action": _required_operator_action(decision),
        "evidence_verified": False,
        "source_verified": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "recommendation": False,
        "allocation": False,
        "trade": False,
        "executor": False,
    }


def validate_v5_4_research_draft_source_router_config(config: dict[str, Any]) -> tuple[str, ...]:
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
        "research_draft_sources_unverified",
        "manual_operator_review_required",
        "manual_trust_required",
        "manual_approval_required",
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
    for field in ("router_policy", "authorization_policy", "dry_run_output_policy", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("review_rows", "source_routing_rules", "operator_runbook_steps"):
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
            "research_draft_sources_unverified": True,
            "no_fetching": True,
            "no_evidence_verification": True,
            "no_source_truth_verification": True,
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


def evaluate_v5_4_research_draft_source_router(config: dict[str, Any]) -> V54ResearchDraftSourceRouterResult:
    config_blockers = list(validate_v5_4_research_draft_source_router_config(config))
    rows = tuple(row for row in config.get("review_rows", []) if isinstance(row, dict))
    review_ids = [normalize_text(row.get("review_id")) for row in rows]
    fixture_ids = [normalize_text(row.get("fixture_id")) for row in rows]
    duplicate_review_ids = tuple(dict.fromkeys(item for item in review_ids if item and review_ids.count(item) > 1))
    duplicate_fixture_ids = tuple(dict.fromkeys(item for item in fixture_ids if item and fixture_ids.count(item) > 1))
    blockers: list[str] = list(config_blockers)
    warnings: list[str] = []
    for duplicate_id in duplicate_review_ids:
        blockers.append(f"duplicate review_id: {duplicate_id}")
    for duplicate_id in duplicate_fixture_ids:
        blockers.append(f"duplicate fixture_id: {duplicate_id}")
    route_rows: list[dict[str, Any]] = []
    router_policy = config.get("router_policy", {}) if isinstance(config.get("router_policy"), dict) else {}
    for index, row in enumerate(rows, start=1):
        review_id = normalize_text(row.get("review_id")) or f"missing_{index}"
        row_blockers = list(validate_review_row(row))
        if review_id in duplicate_review_ids:
            row["duplicate_review_id"] = True
        if normalize_text(row.get("fixture_id")) in duplicate_fixture_ids:
            row["duplicate_fixture_id"] = True
        decision = evaluate_review_row_for_source_routing(row, router_policy)
        priority = assign_route_priority(row, decision)
        if row_blockers:
            blockers.extend(f"{review_id}: {reason}" for reason in row_blockers)
        if decision.startswith("defer_") or decision == "block_not_operator_accepted":
            warnings.append(f"{review_id}: {decision}")
        route_rows.append(build_source_route_row(row, decision, priority, index))
    ordered_routes = tuple(sorted(route_rows, key=lambda row: row["route_id"]))
    blocker_tuple = tuple(dict.fromkeys(blockers))
    warning_tuple = tuple(dict.fromkeys(warnings))
    blocked_count = sum(1 for row in ordered_routes if row["route_decision"].startswith("block_"))
    deferred_count = sum(1 for row in ordered_routes if row["route_decision"].startswith("defer_"))
    routed_count = sum(1 for row in ordered_routes if row["route_decision"] == "route_to_research_draft_reference_only")
    pending_count = sum(1 for row in ordered_routes if row["route_decision"] == "block_not_operator_accepted")
    forbidden_flag_count = sum(1 for row in rows if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS))
    private_or_credential_count = sum(1 for row in rows if _row_private_or_credential_risk(row))
    unsafe_count = sum(1 for row in rows if row.get("unsafe_path") is True)
    unsupported_format_count = sum(1 for row in rows if row.get("unsupported_format") is True or normalize_text(row.get("fixture_format")) not in SUPPORTED_FIXTURE_FORMATS)
    unsupported_category_count = sum(1 for row in rows if row.get("unsupported_category") is True or normalize_text(row.get("source_category_id")) not in SUPPORTED_SOURCE_CATEGORIES)
    missing_count = sum(1 for row in rows if row.get("missing_fixture") is True or normalize_text(row.get("review_decision")) == "deferred_missing_file")
    stale_count = sum(1 for row in rows if row.get("stale_fixture") is True or normalize_text(row.get("review_decision")) == "deferred_stale_fixture")
    manual_refresh_count = sum(1 for row in rows if row.get("manual_refresh_required") is True or normalize_text(row.get("review_decision")) == "deferred_manual_refresh_required")
    hard_block = bool(
        config_blockers
        or blocker_tuple
        or unsafe_count
        or unsupported_format_count
        or unsupported_category_count
        or duplicate_review_ids
        or duplicate_fixture_ids
        or private_or_credential_count
        or forbidden_flag_count
        or any(row["route_decision"].startswith("block_") and row["route_decision"] != "block_not_operator_accepted" for row in ordered_routes)
    )
    authorized = _authorization_valid(config)
    if hard_block:
        status = "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE"
    elif not rows or deferred_count or pending_count:
        status = "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_PARTIAL_SAFE"
    elif authorized:
        status = "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_TO_WRITE_SAFE"
    else:
        status = "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_SAFE"
    return V54ResearchDraftSourceRouterResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.4 Research Draft Source Router",
        version=normalize_text(config.get("version")) or "v5.4",
        status=status,
        research_draft_source_router_mode=normalize_text(config.get("research_draft_source_router_mode")),
        review_row_count=len(rows),
        source_route_count=len(ordered_routes),
        routed_reference_count=routed_count,
        pending_operator_review_count=pending_count,
        deferred_route_count=deferred_count,
        blocked_route_count=blocked_count,
        high_priority_count=sum(1 for row in ordered_routes if row["route_priority"] == "high"),
        medium_priority_count=sum(1 for row in ordered_routes if row["route_priority"] == "medium"),
        low_priority_count=sum(1 for row in ordered_routes if row["route_priority"] == "low"),
        unsafe_count=unsafe_count,
        unsupported_format_count=unsupported_format_count,
        unsupported_category_count=unsupported_category_count,
        duplicate_review_id_count=len(duplicate_review_ids),
        duplicate_fixture_id_count=len(duplicate_fixture_ids) + sum(1 for row in rows if row.get("duplicate_fixture_id") is True and normalize_text(row.get("fixture_id")) not in duplicate_fixture_ids),
        private_or_credential_risk_count=private_or_credential_count,
        forbidden_flag_count=forbidden_flag_count,
        missing_fixture_count=missing_count,
        stale_fixture_count=stale_count,
        manual_refresh_required_count=manual_refresh_count,
        route_rows=ordered_routes,
        operator_runbook_steps=tuple(str(item) for item in config.get("operator_runbook_steps", []) if normalize_text(item)),
        blockers=blocker_tuple,
        warnings=warning_tuple,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = _normalized_path_text(path)
    if not text:
        return ("v5.4 source router output root is required.",)
    if text in {"docs", "templates", "jarvis/data", "."} or text.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5.4 source router output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def execute_authorized_v5_4_source_router_snapshot_write(
    config: dict[str, Any],
    result: V54ResearchDraftSourceRouterResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None and not _path_is_under(output_root, ALLOWED_OUTPUT_ROOT):
        blockers.append("path must stay under the configured v5.4 source router output root.")
    if result.status not in {"V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_SAFE", "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_TO_WRITE_SAFE"}:
        blockers.append("source router result must be ready before writing.")
    if blockers:
        return {"status": "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "snapshot_created_at": created_at,
        "status": result.status,
        "research_draft_sources_unverified": True,
        "route_rows": list(result.route_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_4_research_draft_source_router.snapshot.json"
    metadata_path = output_root / "jarvis_v5_4_research_draft_source_router.snapshot.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "snapshot_created_at": created_at,
        "content_sha256": _sha256_bytes(raw_bytes),
        "source_route_count": result.source_route_count,
        "routed_reference_count": result.routed_reference_count,
        "research_draft_sources_unverified": True,
        "external_file_read": False,
        "fetch_executed": False,
        "download_executed": False,
        "ocr": False,
        "pdf_parsing": False,
        "html_scraping": False,
        "evidence_verified": False,
        "source_verified": False,
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
        "status": "V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_4_research_draft_source_router_summary(result: V54ResearchDraftSourceRouterResult) -> str:
    return (
        f"status={result.status}; review_rows={result.review_row_count}; routes={result.source_route_count}; "
        f"routed={result.routed_reference_count}; pending={result.pending_operator_review_count}; "
        f"deferred={result.deferred_route_count}; blocked={result.blocked_route_count}; high={result.high_priority_count}; "
        f"medium={result.medium_priority_count}; low={result.low_priority_count}"
    )


def load_v5_4_research_draft_source_router_result(path: str | Path) -> V54ResearchDraftSourceRouterResult:
    return evaluate_v5_4_research_draft_source_router(load_json(path))
