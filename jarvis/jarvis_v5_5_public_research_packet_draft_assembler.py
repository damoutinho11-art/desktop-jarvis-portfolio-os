"""Public research packet draft assembler for v5.5.

v5.5 consumes v5.4 route-row metadata and groups safe, routed source references
into unverified public research packet drafts only. It does not read external
fixture files, fetch, scrape, parse source content, extract or verify evidence,
approve assets, recommend allocations, mutate registries, trade, or create an
executor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_source_fixtures/v5_5_public_research_packet_drafts")
SUPPORTED_SOURCE_REFERENCE_TYPES = {
    "research_draft_source_reference",
    "deferred_source_reference",
    "manual_refresh_required_reference",
    "manual_fix_required_reference",
    "blocked_source_reference",
}
ROUTEABLE_DECISIONS = {"route_to_research_draft_reference_only"}
DEFERRED_DECISIONS = {"defer_missing_file", "defer_stale_fixture", "defer_manual_refresh_required"}
BLOCKED_DOWNSTREAM_USE = (
    "evidence_extraction",
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
ALLOWED_DOWNSTREAM_USE = (
    "human_research_packet_review_only",
    "manual_source_review_context_only",
    "operator_dashboard_reference_only",
)
VALID_NEXT_MANUAL_ACTIONS = {
    "review_public_research_packet_drafts",
    "fix_blocked_packet_draft_routes",
    "refresh_deferred_public_source_routes",
    "proceed_to_v5_6_public_research_packet_human_review_queue",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "live_fetch_now",
    "evidence_extraction",
    "evidence_verification",
    "source_truth_verification",
    "approval",
    "trust_asset",
    "mark_investable",
    "registry_mutation",
    "allocation_recommendation",
    "trade_execution",
    "executor_creation",
}
DO_NOT_BUILD_NEXT = (
    "live_fetch_adapter_inside_v5_5",
    "scraping",
    "ocr",
    "pdf_parsing",
    "html_scraping",
    "evidence_extraction",
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
    "packet_drafts_unverified",
    "dry_run_only",
    "packet_draft_assembler_only",
)
FORBIDDEN_ROW_TRUE_FIELDS = (
    "downloaded_by_jarvis",
    "evidence_verified",
    "source_verified",
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
class V55PublicResearchPacketDraftAssemblerResult:
    title: str
    version: str
    status: str
    public_research_packet_draft_assembler_mode: str
    route_row_count: int
    packet_group_count: int
    packet_draft_count: int
    source_reference_count: int
    ready_packet_count: int
    deferred_packet_count: int
    blocked_packet_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    invalid_route_row_count: int
    duplicate_route_id_count: int
    duplicate_source_reference_count: int
    forbidden_flag_count: int
    private_or_credential_risk_count: int
    unsupported_source_reference_type_count: int
    route_not_ready_count: int
    deferred_route_count: int
    blocked_route_count: int
    packet_rows: tuple[dict[str, Any], ...]
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
    packet_drafts_unverified: bool = True
    manual_operator_review_required: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def _row_private_or_credential_risk(row: dict[str, Any]) -> bool:
    return row.get("credential_or_private_risk") is True or bool(_scan_for_forbidden_keys(row))


def validate_route_row(row: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "route_id",
        "review_id",
        "fixture_id",
        "source_id",
        "source_name",
        "source_category_id",
        "asset_universe",
        "fixture_type",
        "fixture_format",
        "route_decision",
        "source_reference_type",
    ):
        if not normalize_text(row.get(field)):
            blockers.append(f"{field} is required.")
    if normalize_text(row.get("source_reference_type")) not in SUPPORTED_SOURCE_REFERENCE_TYPES:
        blockers.append(f"unsupported source_reference_type: {normalize_text(row.get('source_reference_type')) or 'missing'}")
    for field in FORBIDDEN_ROW_TRUE_FIELDS:
        if row.get(field) is True:
            blockers.append(f"{field} must be false.")
    blockers.extend(_scan_for_forbidden_keys(row))
    return tuple(dict.fromkeys(blockers))


def evaluate_route_row_for_packet_assembly(row: dict[str, Any], assembler_policy: dict[str, Any] | None = None) -> str:
    validation_text = " ".join(validate_route_row(row))
    if row.get("duplicate_route_id") is True or row.get("duplicate_source_reference") is True:
        return "block_duplicate_source_reference"
    if row.get("credential_or_private_risk") is True or "forbidden private/credential field" in validation_text:
        return "block_private_or_credential_risk"
    if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS):
        return "block_forbidden_flags"
    if normalize_text(row.get("source_reference_type")) not in SUPPORTED_SOURCE_REFERENCE_TYPES:
        return "block_unsupported_source_reference_type"
    decision = normalize_text(row.get("route_decision"))
    reference_type = normalize_text(row.get("source_reference_type"))
    if decision in DEFERRED_DECISIONS or reference_type in {"deferred_source_reference", "manual_refresh_required_reference"}:
        return "defer_source_reference"
    if decision.startswith("block_") or reference_type in {"blocked_source_reference", "manual_fix_required_reference"}:
        return "block_source_reference"
    if decision in ROUTEABLE_DECISIONS and reference_type == "research_draft_source_reference":
        return "assemble_public_research_packet_draft"
    if isinstance(assembler_policy, dict) and assembler_policy.get("allow_manual_fix_required_references") is True and reference_type == "manual_fix_required_reference":
        return "defer_source_reference"
    return "block_not_routable_for_packet_draft"


def _packet_group_key(row: dict[str, Any], assembler_policy: dict[str, Any] | None = None) -> str:
    policy = assembler_policy if isinstance(assembler_policy, dict) else {}
    group_by = normalize_text(policy.get("group_by")) or "asset_universe"
    if group_by == "source_category_id":
        return normalize_text(row.get("source_category_id")) or "unknown_source_category"
    if group_by == "source_id":
        return normalize_text(row.get("source_id")) or "unknown_source"
    return normalize_text(row.get("asset_universe")) or "unknown_asset_universe"


def group_route_rows_for_packets(route_rows: list[dict[str, Any]] | tuple[dict[str, Any], ...], assembler_policy: dict[str, Any] | None = None) -> tuple[dict[str, Any], ...]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in route_rows:
        if not isinstance(row, dict):
            continue
        groups.setdefault(_packet_group_key(row, assembler_policy), []).append(row)
    return tuple({"packet_group_key": key, "route_rows": tuple(sorted(rows, key=lambda item: normalize_text(item.get("route_id"))))} for key, rows in sorted(groups.items()))


def _packet_priority(decisions: tuple[str, ...]) -> str:
    if any(decision.startswith("block_") for decision in decisions):
        return "high"
    if any(decision.startswith("defer_") for decision in decisions):
        return "medium"
    return "low"


def _packet_draft_type(decisions: tuple[str, ...]) -> str:
    if any(decision.startswith("block_") for decision in decisions):
        return "blocked_public_research_packet_draft"
    if any(decision.startswith("defer_") for decision in decisions):
        return "deferred_public_research_packet_draft"
    return "public_research_packet_draft"


def build_packet_row(packet_group: dict[str, Any], route_evaluations: dict[str, str], index: int) -> dict[str, Any]:
    rows = tuple(row for row in packet_group.get("route_rows", ()) if isinstance(row, dict))
    decisions = tuple(route_evaluations.get(normalize_text(row.get("route_id")), "block_not_routable_for_packet_draft") for row in rows)
    packet_key = normalize_text(packet_group.get("packet_group_key")) or f"group_{index}"
    draft_type = _packet_draft_type(decisions)
    route_ids = tuple(normalize_text(row.get("route_id")) for row in rows)
    source_reference_ids = tuple(normalize_text(row.get("source_id")) for row in rows)
    return {
        "packet_id": f"public_research_packet_draft::{packet_key}",
        "packet_group_key": packet_key,
        "packet_draft_type": draft_type,
        "packet_decision": "assemble_unverified_public_research_packet_draft" if draft_type == "public_research_packet_draft" else "hold_for_manual_route_fix_or_refresh",
        "packet_reason": "source-route metadata grouped into an unverified packet draft for human review only." if draft_type == "public_research_packet_draft" else "one or more source routes are blocked or deferred.",
        "packet_priority": _packet_priority(decisions),
        "route_ids": route_ids,
        "source_reference_ids": source_reference_ids,
        "source_reference_count": len(rows),
        "allowed_downstream_use": ALLOWED_DOWNSTREAM_USE,
        "blocked_downstream_use": BLOCKED_DOWNSTREAM_USE,
        "required_operator_action": "review_public_research_packet_drafts" if draft_type == "public_research_packet_draft" else "fix_blocked_packet_draft_routes",
        "packet_draft_unverified": True,
        "evidence_extracted": False,
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


def validate_v5_5_public_research_packet_draft_assembler_config(config: dict[str, Any]) -> tuple[str, ...]:
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
        "packet_drafts_unverified",
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
    for field in ("assembler_policy", "authorization_policy", "dry_run_output_policy", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("route_rows", "packet_assembly_rules", "operator_runbook_steps"):
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
            "packet_drafts_unverified": True,
            "no_fetching": True,
            "no_evidence_extraction": True,
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


def evaluate_v5_5_public_research_packet_draft_assembler(config: dict[str, Any]) -> V55PublicResearchPacketDraftAssemblerResult:
    config_blockers = list(validate_v5_5_public_research_packet_draft_assembler_config(config))
    rows = tuple(row for row in config.get("route_rows", []) if isinstance(row, dict))
    route_ids = [normalize_text(row.get("route_id")) for row in rows]
    source_refs = [normalize_text(row.get("source_id")) for row in rows]
    duplicate_route_ids = tuple(dict.fromkeys(item for item in route_ids if item and route_ids.count(item) > 1))
    duplicate_source_refs = tuple(dict.fromkeys(item for item in source_refs if item and source_refs.count(item) > 1))
    blockers: list[str] = list(config_blockers)
    warnings: list[str] = []
    for duplicate_id in duplicate_route_ids:
        blockers.append(f"duplicate route_id: {duplicate_id}")
    for duplicate_id in duplicate_source_refs:
        blockers.append(f"duplicate source reference: {duplicate_id}")
    assembler_policy = config.get("assembler_policy", {}) if isinstance(config.get("assembler_policy"), dict) else {}
    route_evaluations: dict[str, str] = {}
    for index, row in enumerate(rows, start=1):
        route_id = normalize_text(row.get("route_id")) or f"missing_{index}"
        if route_id in duplicate_route_ids:
            row["duplicate_route_id"] = True
        if normalize_text(row.get("source_id")) in duplicate_source_refs:
            row["duplicate_source_reference"] = True
        row_blockers = list(validate_route_row(row))
        decision = evaluate_route_row_for_packet_assembly(row, assembler_policy)
        route_evaluations[route_id] = decision
        if row_blockers:
            blockers.extend(f"{route_id}: {reason}" for reason in row_blockers)
        if decision.startswith("defer_") or decision.startswith("block_"):
            warnings.append(f"{route_id}: {decision}")
    packet_rows: list[dict[str, Any]] = []
    for index, group in enumerate(group_route_rows_for_packets(rows, assembler_policy), start=1):
        packet_rows.append(build_packet_row(group, route_evaluations, index))
    ordered_packets = tuple(sorted(packet_rows, key=lambda row: row["packet_id"]))
    blocker_tuple = tuple(dict.fromkeys(blockers))
    warning_tuple = tuple(dict.fromkeys(warnings))
    blocked_packet_count = sum(1 for row in ordered_packets if row["packet_draft_type"] == "blocked_public_research_packet_draft")
    deferred_packet_count = sum(1 for row in ordered_packets if row["packet_draft_type"] == "deferred_public_research_packet_draft")
    ready_packet_count = sum(1 for row in ordered_packets if row["packet_draft_type"] == "public_research_packet_draft")
    route_not_ready_count = sum(1 for decision in route_evaluations.values() if decision == "block_not_routable_for_packet_draft")
    blocked_route_count = sum(1 for decision in route_evaluations.values() if decision.startswith("block_"))
    deferred_route_count = sum(1 for decision in route_evaluations.values() if decision.startswith("defer_"))
    forbidden_flag_count = sum(1 for row in rows if any(row.get(field) is True for field in FORBIDDEN_ROW_TRUE_FIELDS))
    private_or_credential_count = sum(1 for row in rows if _row_private_or_credential_risk(row))
    unsupported_reference_count = sum(1 for row in rows if normalize_text(row.get("source_reference_type")) not in SUPPORTED_SOURCE_REFERENCE_TYPES)
    invalid_count = sum(1 for row in rows if validate_route_row(row))
    hard_block = bool(
        config_blockers
        or blocker_tuple
        or duplicate_route_ids
        or duplicate_source_refs
        or private_or_credential_count
        or forbidden_flag_count
        or unsupported_reference_count
        or any(decision.startswith("block_") and decision != "block_not_routable_for_packet_draft" for decision in route_evaluations.values())
    )
    authorized = _authorization_valid(config)
    if hard_block:
        status = "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_BLOCKED_SAFE"
    elif not rows or deferred_route_count or route_not_ready_count or blocked_route_count:
        status = "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_PARTIAL_SAFE"
    elif authorized:
        status = "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_TO_WRITE_SAFE"
    else:
        status = "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_SAFE"
    return V55PublicResearchPacketDraftAssemblerResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.5 Public Research Packet Draft Assembler",
        version=normalize_text(config.get("version")) or "v5.5",
        status=status,
        public_research_packet_draft_assembler_mode=normalize_text(config.get("public_research_packet_draft_assembler_mode")),
        route_row_count=len(rows),
        packet_group_count=len(ordered_packets),
        packet_draft_count=len(ordered_packets),
        source_reference_count=sum(row["source_reference_count"] for row in ordered_packets),
        ready_packet_count=ready_packet_count,
        deferred_packet_count=deferred_packet_count,
        blocked_packet_count=blocked_packet_count,
        high_priority_count=sum(1 for row in ordered_packets if row["packet_priority"] == "high"),
        medium_priority_count=sum(1 for row in ordered_packets if row["packet_priority"] == "medium"),
        low_priority_count=sum(1 for row in ordered_packets if row["packet_priority"] == "low"),
        invalid_route_row_count=invalid_count,
        duplicate_route_id_count=len(duplicate_route_ids),
        duplicate_source_reference_count=len(duplicate_source_refs),
        forbidden_flag_count=forbidden_flag_count,
        private_or_credential_risk_count=private_or_credential_count,
        unsupported_source_reference_type_count=unsupported_reference_count,
        route_not_ready_count=route_not_ready_count,
        deferred_route_count=deferred_route_count,
        blocked_route_count=blocked_route_count,
        packet_rows=ordered_packets,
        operator_runbook_steps=tuple(str(item) for item in config.get("operator_runbook_steps", []) if normalize_text(item)),
        blockers=blocker_tuple,
        warnings=warning_tuple,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = _normalized_path_text(path)
    if not text:
        return ("v5.5 packet draft output root is required.",)
    if text in {"docs", "templates", "jarvis/data", "."} or text.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5.5 packet draft output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def execute_authorized_v5_5_packet_draft_snapshot_write(
    config: dict[str, Any],
    result: V55PublicResearchPacketDraftAssemblerResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None and not _path_is_under(output_root, ALLOWED_OUTPUT_ROOT):
        blockers.append("path must stay under the configured v5.5 packet draft output root.")
    if result.status not in {"V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_SAFE", "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_TO_WRITE_SAFE"}:
        blockers.append("packet draft assembler result must be ready before writing.")
    if blockers:
        return {"status": "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "snapshot_created_at": created_at,
        "status": result.status,
        "packet_drafts_unverified": True,
        "packet_rows": list(result.packet_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_5_public_research_packet_draft_assembler.snapshot.json"
    metadata_path = output_root / "jarvis_v5_5_public_research_packet_draft_assembler.snapshot.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "snapshot_created_at": created_at,
        "content_sha256": _sha256_bytes(raw_bytes),
        "packet_draft_count": result.packet_draft_count,
        "source_reference_count": result.source_reference_count,
        "packet_drafts_unverified": True,
        "external_file_read": False,
        "fetch_executed": False,
        "download_executed": False,
        "ocr": False,
        "pdf_parsing": False,
        "html_scraping": False,
        "evidence_extracted": False,
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
        "status": "V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_5_public_research_packet_draft_assembler_summary(result: V55PublicResearchPacketDraftAssemblerResult) -> str:
    return (
        f"status={result.status}; route_rows={result.route_row_count}; packets={result.packet_draft_count}; "
        f"ready={result.ready_packet_count}; deferred={result.deferred_packet_count}; blocked={result.blocked_packet_count}; "
        f"high={result.high_priority_count}; medium={result.medium_priority_count}; low={result.low_priority_count}"
    )


def load_v5_5_public_research_packet_draft_assembler_result(path: str | Path) -> V55PublicResearchPacketDraftAssemblerResult:
    return evaluate_v5_5_public_research_packet_draft_assembler(load_json(path))
