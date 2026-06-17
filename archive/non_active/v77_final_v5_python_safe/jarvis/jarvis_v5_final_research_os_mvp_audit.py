"""Final Research OS MVP audit.

v5.0 is a release-readiness audit only. It does not fetch, parse evidence,
verify evidence, approve assets, recommend, allocate, trade, mutate registry
files, write by default, or create an executor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_V5_FINAL_RESEARCH_OS_MVP_AUDIT_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/v5_final_audit")
REQUIRED_STAGE_CHAIN = (
    "phase1_manual_evidence_workflow",
    "phase2_candidate_intake_workspace",
    "v4.61_discovery_plan",
    "v4.62_source_manifest",
    "v4.63_fetch_dry_run_planner",
    "v4.64_local_cache_builder",
    "v4.65_cache_integrity_freshness_audit",
    "v4.66_normalizer",
    "v4.67_classifier",
    "v4.68_research_priority_queue",
    "v4.69_public_evidence_pack_draft_generator",
    "v4.70_public_research_operator_dashboard",
    "v4.71_public_universe_end_to_end_workflow_audit",
)
REQUIRED_PRESENT_CAPABILITIES = (
    "public_universe_discovery_planning",
    "source_manifest_definition",
    "fetch_dry_run_planning",
    "authorized_local_cache_builder",
    "cache_integrity_freshness_audit",
    "public_asset_normalization",
    "public_asset_classification",
    "research_priority_queue",
    "public_evidence_pack_draft_generation",
    "operator_research_dashboard",
    "end_to_end_workflow_audit",
    "manual_evidence_review_boundary",
    "manual_approval_boundary",
    "no_execution_boundary",
)
FORBIDDEN_CAPABILITIES = (
    "broker_execution",
    "lightyear_execution",
    "lhv_execution",
    "crypto_exchange_execution",
    "credential_use",
    "private_account_ingest",
    "automatic_evidence_verification",
    "automatic_approval",
    "automatic_trust",
    "automatic_investability",
    "investment_recommendation",
    "allocation_recommendation",
    "portfolio_weight_generation",
    "buy_signal",
    "sell_signal",
    "trade_execution",
    "executor_creation",
    "registry_mutation_without_manual_authorization",
)
REQUIRED_FINAL_AUDIT_AREAS = (
    "product_definition",
    "public_universe_workflow",
    "manual_trust_boundary",
    "manual_approval_boundary",
    "no_execution_boundary",
    "local_first_boundary",
    "no_private_data_boundary",
    "no_broker_boundary",
    "evidence_draft_boundary",
    "operator_dashboard_boundary",
    "regression_safety_boundary",
    "v5_release_readiness",
)
ALLOWED_FINAL_AUDIT_RECORD_STATUSES = {
    "FINAL_AUDIT_AREA_READY_SAFE",
    "FINAL_AUDIT_AREA_PARTIAL_SAFE",
    "FINAL_AUDIT_AREA_BLOCKED_SAFE",
    "FINAL_AUDIT_AREA_REVIEW_REQUIRED_SAFE",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_v5_final_research_os_mvp_audit",
    "tag_v5_research_os_mvp_after_manual_review",
    "fix_final_audit_blockers",
    "rerun_end_to_end_public_universe_workflow_audit",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
    "trade_execution",
    "executor_creation",
}
DO_NOT_BUILD_NEXT = (
    "broker_integration",
    "executor_creation",
    "trade_execution",
    "investment_recommendation",
    "asset_approval",
    "evidence_verification",
    "registry_mutation",
    "allocation_recommendation",
    "screening_inside_v5_0",
    "research_scoring_inside_v5_0",
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
    "local_cache_only",
    "final_audit_data_unverified",
    "final_mvp_audit_only",
)
FINAL_RECORD_TRUE_FIELDS = (
    "safety_confirmed",
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_confirmed",
    "no_evidence_verification",
    "no_approval",
    "no_recommendation",
    "no_allocation",
    "no_trade",
    "no_executor",
)


@dataclass(frozen=True)
class V5FinalResearchOSMVPAuditResult:
    title: str
    version: str
    status: str
    release_candidate_label: str
    final_verdict: str
    mvp_readiness_label: str
    product_definition: str
    required_stage_count: int
    present_stage_count: int
    missing_stage_count: int
    duplicate_stage_count: int
    out_of_order_stage_count: int
    required_capability_count: int
    present_capability_count: int
    forbidden_capability_violation_count: int
    final_audit_area_count: int
    ready_area_count: int
    partial_area_count: int
    blocked_area_count: int
    warning_count: int
    blocker_count: int
    public_universe_e2e_status: str
    phase1_safety_status: str
    manual_trust_boundary_status: str
    manual_approval_boundary_status: str
    no_execution_boundary_status: str
    local_first_boundary_status: str
    out_of_scope_after_v5: tuple[str, ...]
    recommended_next_phase: str
    do_not_build_next: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    stage_rows: tuple[dict[str, Any], ...]
    capability_rows: tuple[dict[str, Any], ...]
    final_audit_area_rows: tuple[dict[str, Any], ...]
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_mutated: bool = True
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_verified_evidence_promotion: bool = True
    no_investment_screening: bool = True
    no_research_scoring: bool = True
    no_recommendation: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_registry_mutation: bool = True
    no_candidate_write: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    final_audit_data_unverified: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _as_tuple(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()


def _record_id(item: Any) -> str:
    if isinstance(item, dict):
        return normalize_text(item.get("stage_id") or item.get("area") or item.get("capability_id"))
    return normalize_text(item)


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


def validate_v5_final_audit_config(config: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
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
    for field in (
        "release_policy",
        "authorization_policy",
        "required_capability_matrix",
        "public_universe_e2e_audit_summary",
        "phase1_safety_audit_summary",
        "manual_trust_boundary_summary",
        "no_execution_boundary_summary",
        "safety_controls",
    ):
        if not isinstance(config.get(field), dict):
            blockers.append(f"{field} must be an object.")
    for field in ("required_stage_chain", "final_audit_records"):
        if not isinstance(config.get(field, []), list):
            blockers.append(f"{field} must be a list.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)):
            blockers.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blockers.append(f"safety_controls.{field} must be true.")
    policy = config.get("authorization_policy", {})
    if isinstance(policy, dict):
        expected = {
            "explicit_authorization_required": True,
            "default_write_allowed": False,
            "write_allowed_only_with_explicit_authorization": True,
            "local_cache_only": True,
            "final_audit_data_unverified": True,
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
    action = normalize_text(config.get("next_manual_action"))
    if action not in VALID_NEXT_MANUAL_ACTIONS:
        blockers.append("next_manual_action must be valid.")
    if action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blockers.append(f"next_manual_action must not be {action}.")
    return tuple(dict.fromkeys(blockers))


def audit_required_stage_chain(required_stage_chain: list[Any] | tuple[Any, ...]) -> dict[str, Any]:
    observed = tuple(_record_id(stage) for stage in required_stage_chain)
    missing = tuple(stage_id for stage_id in REQUIRED_STAGE_CHAIN if stage_id not in observed)
    duplicates = tuple(stage_id for stage_id in observed if observed.count(stage_id) > 1)
    in_required_order = tuple(stage_id for stage_id in observed if stage_id in REQUIRED_STAGE_CHAIN)
    expected_seen_order = tuple(stage_id for stage_id in REQUIRED_STAGE_CHAIN if stage_id in observed)
    out_of_order = bool(observed) and (observed != REQUIRED_STAGE_CHAIN[: len(observed)] or in_required_order != expected_seen_order)
    blockers: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    if missing:
        blockers.append("missing required stage ids: " + ", ".join(missing))
    if duplicates:
        blockers.append("duplicate stage ids: " + ", ".join(tuple(dict.fromkeys(duplicates))))
    if out_of_order:
        blockers.append("stage order is not the required v5.0 release chain.")
    for item in required_stage_chain:
        if isinstance(item, dict):
            stage_id = _record_id(item)
            status = normalize_text(item.get("status")) or "UNKNOWN"
            blocker_count = item.get("blocker_count", 0)
            warning_count = item.get("warning_count", 0)
            safety_confirmed = item.get("safety_confirmed") is True
            if not safety_confirmed:
                blockers.append(f"{stage_id}: safety_confirmed must be true.")
            if not isinstance(blocker_count, int) or blocker_count < 0:
                blockers.append(f"{stage_id}: blocker_count must be a non-negative integer.")
                blocker_count = 1
            if not isinstance(warning_count, int) or warning_count < 0:
                blockers.append(f"{stage_id}: warning_count must be a non-negative integer.")
                warning_count = 0
            if "BLOCKED" in status.upper() or blocker_count > 0:
                blockers.append(f"{stage_id}: critical stage is blocked.")
            if "PARTIAL" in status.upper() or "REVIEW" in status.upper():
                warnings.append(f"{stage_id}: stage requires operator review.")
            for field in FALSE_REQUIRED_SAFETY_FIELDS:
                if item.get(field) is True:
                    blockers.append(f"{stage_id}: {field} must not be true.")
            rows.append(
                {
                    "stage_id": stage_id,
                    "status": status,
                    "ready": "READY" in status.upper() and "BLOCKED" not in status.upper(),
                    "blocker_count": blocker_count,
                    "warning_count": warning_count,
                    "safety_confirmed": safety_confirmed,
                }
            )
        else:
            rows.append(
                {
                    "stage_id": normalize_text(item),
                    "status": "STAGE_PRESENT_READY_SAFE",
                    "ready": True,
                    "blocker_count": 0,
                    "warning_count": 0,
                    "safety_confirmed": True,
                }
            )
    order = {stage_id: index for index, stage_id in enumerate(REQUIRED_STAGE_CHAIN)}
    return {
        "required_stage_count": len(REQUIRED_STAGE_CHAIN),
        "present_stage_count": len(observed),
        "missing_stage_count": len(missing),
        "duplicate_stage_count": len(set(duplicates)),
        "out_of_order_stage_count": 1 if out_of_order else 0,
        "rows": tuple(sorted(rows, key=lambda row: order.get(row["stage_id"], 999))),
        "blockers": tuple(dict.fromkeys(blockers)),
        "warnings": tuple(dict.fromkeys(warnings)),
    }


def audit_required_capability_matrix(required_capability_matrix: dict[str, Any]) -> dict[str, Any]:
    present_items = _as_tuple(required_capability_matrix.get("present_capabilities"))
    absent_items = _as_tuple(required_capability_matrix.get("absent_capabilities"))
    present_map = {_record_id(item): item for item in present_items}
    absent_map = {_record_id(item): item for item in absent_items}
    blockers: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    present_count = 0
    forbidden_violations = 0
    for capability in REQUIRED_PRESENT_CAPABILITIES:
        item = present_map.get(capability)
        present = bool(item and (not isinstance(item, dict) or item.get("present") is True))
        if present:
            present_count += 1
        else:
            blockers.append(f"missing required capability: {capability}")
        rows.append({"capability_id": capability, "required_state": "present", "present": present, "violation": False})
    for capability in FORBIDDEN_CAPABILITIES:
        item = absent_map.get(capability)
        violation = bool(item and isinstance(item, dict) and item.get("present") is True)
        absent = bool(item and (not isinstance(item, dict) or item.get("absent") is True))
        if violation or not absent:
            forbidden_violations += 1
            blockers.append(f"forbidden capability present or unconfirmed absent: {capability}")
        rows.append({"capability_id": capability, "required_state": "absent", "present": violation, "violation": violation or not absent})
    if warnings:
        warnings = list(dict.fromkeys(warnings))
    return {
        "required_capability_count": len(REQUIRED_PRESENT_CAPABILITIES),
        "present_capability_count": present_count,
        "forbidden_capability_violation_count": forbidden_violations,
        "rows": tuple(rows),
        "blockers": tuple(dict.fromkeys(blockers)),
        "warnings": tuple(warnings),
    }


def validate_final_audit_record(record: dict[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in ("record_id", "area", "status", "evidence_summary", "blocker_count", "warning_count"):
        if field not in record:
            blockers.append(f"{field} is required.")
    if record.get("status") not in ALLOWED_FINAL_AUDIT_RECORD_STATUSES:
        blockers.append("status is not allowed.")
    for field in ("blocker_count", "warning_count"):
        if not isinstance(record.get(field), int) or record.get(field) < 0:
            blockers.append(f"{field} must be a non-negative integer.")
    for field in FINAL_RECORD_TRUE_FIELDS:
        if record.get(field) is not True:
            blockers.append(f"{field} must be true.")
    return tuple(blockers)


def audit_final_audit_records(final_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    areas = tuple(normalize_text(record.get("area")) for record in final_audit_records if isinstance(record, dict))
    missing = tuple(area for area in REQUIRED_FINAL_AUDIT_AREAS if area not in areas)
    if missing:
        blockers.append("missing final audit areas: " + ", ".join(missing))
    for record in final_audit_records:
        if not isinstance(record, dict):
            blockers.append("final audit record must be an object.")
            continue
        area = normalize_text(record.get("area")) or "unknown"
        reasons = validate_final_audit_record(record)
        blockers.extend(f"{area}: {reason}" for reason in reasons)
        status = normalize_text(record.get("status"))
        blocker_count = record.get("blocker_count", 0) if isinstance(record.get("blocker_count", 0), int) else 1
        warning_count = record.get("warning_count", 0) if isinstance(record.get("warning_count", 0), int) else 0
        if status == "FINAL_AUDIT_AREA_BLOCKED_SAFE" or blocker_count > 0:
            blockers.append(f"{area}: final audit area is blocked.")
        if status in {"FINAL_AUDIT_AREA_PARTIAL_SAFE", "FINAL_AUDIT_AREA_REVIEW_REQUIRED_SAFE"} or warning_count:
            warnings.append(f"{area}: final audit area requires manual review.")
        rows.append(
            {
                "record_id": record.get("record_id"),
                "area": area,
                "status": status,
                "ready": status == "FINAL_AUDIT_AREA_READY_SAFE" and blocker_count == 0,
                "blocker_count": blocker_count,
                "warning_count": warning_count,
                "safety_confirmed": record.get("safety_confirmed") is True,
            }
        )
    order = {area: index for index, area in enumerate(REQUIRED_FINAL_AUDIT_AREAS)}
    return {
        "rows": tuple(sorted(rows, key=lambda row: order.get(row["area"], 999))),
        "final_audit_area_count": len(rows),
        "ready_area_count": sum(1 for row in rows if row["status"] == "FINAL_AUDIT_AREA_READY_SAFE" and row["blocker_count"] == 0),
        "partial_area_count": sum(1 for row in rows if row["status"] in {"FINAL_AUDIT_AREA_PARTIAL_SAFE", "FINAL_AUDIT_AREA_REVIEW_REQUIRED_SAFE"}),
        "blocked_area_count": sum(1 for row in rows if row["status"] == "FINAL_AUDIT_AREA_BLOCKED_SAFE" or row["blocker_count"] > 0),
        "blockers": tuple(dict.fromkeys(blockers)),
        "warnings": tuple(dict.fromkeys(warnings)),
    }


def _summary_status(config: dict[str, Any], key: str) -> tuple[str, bool]:
    summary = config.get(key, {})
    if not isinstance(summary, dict):
        return "MISSING", False
    status = normalize_text(summary.get("status")) or "MISSING"
    confirmed = summary.get("confirmed") is True or summary.get("ready") is True
    return status, confirmed


def compute_final_verdict(
    config: dict[str, Any],
    stage_audit: dict[str, Any],
    capability_audit: dict[str, Any],
    final_records_audit: dict[str, Any],
) -> str:
    if validate_v5_final_audit_config(config):
        return "JARVIS_V5_RESEARCH_OS_MVP_BLOCKED_SAFE"
    public_e2e_status, public_e2e_confirmed = _summary_status(config, "public_universe_e2e_audit_summary")
    phase1_status, phase1_confirmed = _summary_status(config, "phase1_safety_audit_summary")
    manual_trust_status, manual_trust_confirmed = _summary_status(config, "manual_trust_boundary_summary")
    manual_approval_status, manual_approval_confirmed = _summary_status(config, "manual_approval_boundary_summary")
    no_execution_status, no_execution_confirmed = _summary_status(config, "no_execution_boundary_summary")
    hard_block = (
        stage_audit["blocked_stage_count"] if "blocked_stage_count" in stage_audit else 0
    ) or capability_audit["forbidden_capability_violation_count"] or final_records_audit["blocked_area_count"]
    if hard_block or not phase1_confirmed or not manual_trust_confirmed or not manual_approval_confirmed or not no_execution_confirmed:
        return "JARVIS_V5_RESEARCH_OS_MVP_BLOCKED_SAFE"
    if "READY_FOR_V5_FINAL_AUDIT" not in public_e2e_status and "READY_TO_RUN" not in public_e2e_status:
        return "JARVIS_V5_RESEARCH_OS_MVP_PARTIAL_SAFE"
    partial = (
        stage_audit["missing_stage_count"]
        or stage_audit["duplicate_stage_count"]
        or stage_audit["out_of_order_stage_count"]
        or capability_audit["present_capability_count"] != capability_audit["required_capability_count"]
        or final_records_audit["final_audit_area_count"] != len(REQUIRED_FINAL_AUDIT_AREAS)
        or final_records_audit["partial_area_count"]
        or bool(stage_audit["blockers"])
        or bool(capability_audit["blockers"])
        or bool(final_records_audit["blockers"])
        or not public_e2e_confirmed
    )
    if partial:
        return "JARVIS_V5_RESEARCH_OS_MVP_PARTIAL_SAFE"
    return "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE"


def compute_mvp_readiness_label(config: dict[str, Any], final_verdict: str) -> str:
    if final_verdict == "JARVIS_V5_RESEARCH_OS_MVP_READY_SAFE":
        return "V5_RESEARCH_OS_MVP_READY_FOR_TAG_SAFE"
    if final_verdict == "JARVIS_V5_RESEARCH_OS_MVP_BLOCKED_SAFE":
        return "V5_RESEARCH_OS_MVP_BLOCKED_REQUIRES_SAFETY_REVIEW"
    return "V5_RESEARCH_OS_MVP_PARTIAL_REQUIRES_FIXES"


def evaluate_v5_final_research_os_mvp_audit(config: dict[str, Any]) -> V5FinalResearchOSMVPAuditResult:
    config_blockers = list(validate_v5_final_audit_config(config))
    stage_audit = audit_required_stage_chain(config.get("required_stage_chain", []))
    capability_audit = audit_required_capability_matrix(config.get("required_capability_matrix", {}) if isinstance(config.get("required_capability_matrix"), dict) else {})
    final_records_audit = audit_final_audit_records(tuple(record for record in config.get("final_audit_records", []) if isinstance(record, dict)))
    boundary_blockers: list[str] = []
    for key, label in (
        ("phase1_safety_audit_summary", "phase1 safety boundary"),
        ("manual_trust_boundary_summary", "manual trust boundary"),
        ("manual_approval_boundary_summary", "manual approval boundary"),
        ("no_execution_boundary_summary", "no-execution boundary"),
        ("local_first_boundary_summary", "local-first boundary"),
    ):
        status, confirmed = _summary_status(config, key)
        if not confirmed:
            boundary_blockers.append(f"{label} is not confirmed.")
        if "BLOCKED" in status.upper():
            boundary_blockers.append(f"{label} is blocked.")
    public_e2e_status, public_e2e_confirmed = _summary_status(config, "public_universe_e2e_audit_summary")
    if not public_e2e_confirmed or ("READY_FOR_V5_FINAL_AUDIT" not in public_e2e_status and "READY_TO_RUN" not in public_e2e_status):
        boundary_blockers.append("v4.71 public universe e2e audit is not ready for v5 final audit.")
    blockers = tuple(
        dict.fromkeys(
            config_blockers
            + list(stage_audit["blockers"])
            + list(capability_audit["blockers"])
            + list(final_records_audit["blockers"])
            + boundary_blockers
        )
    )
    warnings = tuple(dict.fromkeys(list(stage_audit["warnings"]) + list(capability_audit["warnings"]) + list(final_records_audit["warnings"])))
    verdict = compute_final_verdict(config, stage_audit, capability_audit, final_records_audit)
    readiness_label = compute_mvp_readiness_label(config, verdict)
    authorized = _authorization_valid(config)
    if verdict == "JARVIS_V5_RESEARCH_OS_MVP_BLOCKED_SAFE":
        status = "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE"
    elif verdict == "JARVIS_V5_RESEARCH_OS_MVP_PARTIAL_SAFE":
        status = "V5_FINAL_RESEARCH_OS_MVP_AUDIT_PARTIAL_SAFE"
    elif authorized:
        status = "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_TO_WRITE_SAFE"
    else:
        status = "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_SAFE"
    phase1_status, _ = _summary_status(config, "phase1_safety_audit_summary")
    manual_trust_status, _ = _summary_status(config, "manual_trust_boundary_summary")
    manual_approval_status, _ = _summary_status(config, "manual_approval_boundary_summary")
    no_execution_status, _ = _summary_status(config, "no_execution_boundary_summary")
    local_first_status, _ = _summary_status(config, "local_first_boundary_summary")
    return V5FinalResearchOSMVPAuditResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. v5.0 Final Research OS MVP Audit",
        version=normalize_text(config.get("version")) or "v5.0",
        status=status,
        release_candidate_label=normalize_text(config.get("release_candidate_label")) or "missing",
        final_verdict=verdict,
        mvp_readiness_label=readiness_label,
        product_definition=normalize_text(config.get("product_definition")),
        required_stage_count=stage_audit["required_stage_count"],
        present_stage_count=stage_audit["present_stage_count"],
        missing_stage_count=stage_audit["missing_stage_count"],
        duplicate_stage_count=stage_audit["duplicate_stage_count"],
        out_of_order_stage_count=stage_audit["out_of_order_stage_count"],
        required_capability_count=capability_audit["required_capability_count"],
        present_capability_count=capability_audit["present_capability_count"],
        forbidden_capability_violation_count=capability_audit["forbidden_capability_violation_count"],
        final_audit_area_count=final_records_audit["final_audit_area_count"],
        ready_area_count=final_records_audit["ready_area_count"],
        partial_area_count=final_records_audit["partial_area_count"],
        blocked_area_count=final_records_audit["blocked_area_count"],
        warning_count=sum(row["warning_count"] for row in stage_audit["rows"]) + sum(row["warning_count"] for row in final_records_audit["rows"]) + len(warnings),
        blocker_count=sum(row["blocker_count"] for row in stage_audit["rows"]) + sum(row["blocker_count"] for row in final_records_audit["rows"]) + len(blockers),
        public_universe_e2e_status=public_e2e_status,
        phase1_safety_status=phase1_status,
        manual_trust_boundary_status=manual_trust_status,
        manual_approval_boundary_status=manual_approval_status,
        no_execution_boundary_status=no_execution_status,
        local_first_boundary_status=local_first_status,
        out_of_scope_after_v5=tuple(str(item) for item in config.get("out_of_scope_after_v5", []) if normalize_text(item)),
        recommended_next_phase=normalize_text(config.get("release_policy", {}).get("recommended_next_phase")) if isinstance(config.get("release_policy"), dict) else "",
        do_not_build_next=DO_NOT_BUILD_NEXT,
        blockers=blockers,
        warnings=warnings,
        stage_rows=stage_audit["rows"],
        capability_rows=capability_audit["rows"],
        final_audit_area_rows=final_records_audit["rows"],
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("v5 final audit output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("v5 final audit output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured v5 final audit output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _result_payload(result: V5FinalResearchOSMVPAuditResult, audit_created_at: str) -> dict[str, Any]:
    return {
        "audit_created_at": audit_created_at,
        "status": result.status,
        "release_candidate_label": result.release_candidate_label,
        "final_verdict": result.final_verdict,
        "mvp_readiness_label": result.mvp_readiness_label,
        "final_audit_data_unverified": True,
        "stage_rows": list(result.stage_rows),
        "capability_rows": list(result.capability_rows),
        "final_audit_area_rows": list(result.final_audit_area_rows),
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }


def execute_authorized_v5_final_audit_cache_write(
    config: dict[str, Any],
    audit_result: V5FinalResearchOSMVPAuditResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    if audit_result.status not in {"V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_SAFE", "V5_FINAL_RESEARCH_OS_MVP_AUDIT_READY_TO_WRITE_SAFE"}:
        blockers.append("v5 final audit result must be ready before writing.")
    if blockers:
        return {"status": "V5_FINAL_RESEARCH_OS_MVP_AUDIT_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    audit_created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = _result_payload(audit_result, audit_created_at)
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "jarvis_v5_final_research_os_mvp_audit.json"
    metadata_path = output_root / "jarvis_v5_final_research_os_mvp_audit.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "audit_created_at": audit_created_at,
        "final_verdict": audit_result.final_verdict,
        "mvp_readiness_label": audit_result.mvp_readiness_label,
        "content_sha256": digest,
        "final_audit_data_unverified": True,
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
        "status": "V5_FINAL_RESEARCH_OS_MVP_AUDIT_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_v5_final_research_os_mvp_audit_summary(result: V5FinalResearchOSMVPAuditResult) -> str:
    return (
        f"status={result.status}; verdict={result.final_verdict}; readiness={result.mvp_readiness_label}; "
        f"stages={result.present_stage_count}/{result.required_stage_count}; missing={result.missing_stage_count}; "
        f"capabilities={result.present_capability_count}/{result.required_capability_count}; "
        f"forbidden_violations={result.forbidden_capability_violation_count}; "
        f"areas={result.ready_area_count}/{len(REQUIRED_FINAL_AUDIT_AREAS)}; blockers={result.blocker_count}"
    )


def load_v5_final_research_os_mvp_audit_result(path: str | Path) -> V5FinalResearchOSMVPAuditResult:
    return evaluate_v5_final_research_os_mvp_audit(load_json(path))
