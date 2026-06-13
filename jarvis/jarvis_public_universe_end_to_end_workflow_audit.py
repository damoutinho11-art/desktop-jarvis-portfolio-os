"""End-to-end public universe workflow audit.

v4.71 audits the v4.61-v4.70 public-universe research workflow. It is an audit
only: no fetching, cache writing, evidence extraction, evidence verification,
approval, recommendation, allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_UNIVERSE_E2E_AUDIT_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/e2e_audit")
REQUIRED_STAGE_ORDER = (
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
)
EXPECTED_HANDOFF_NAMES = (
    "discovery_to_manifest",
    "manifest_to_fetch_plan",
    "fetch_plan_to_local_cache",
    "local_cache_to_cache_audit",
    "cache_audit_to_normalizer",
    "normalizer_to_classifier",
    "classifier_to_research_queue",
    "research_queue_to_draft_packs",
    "draft_packs_to_operator_dashboard",
    "dashboard_to_v5_final_audit",
)
ALLOWED_HANDOFF_STATUSES = {
    "HANDOFF_READY_SAFE",
    "HANDOFF_PARTIAL_SAFE",
    "HANDOFF_BLOCKED_SAFE",
    "HANDOFF_NOT_APPLICABLE_SAFE",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_end_to_end_public_universe_workflow_audit",
    "proceed_to_v5_final_research_os_mvp_audit",
    "fix_public_universe_workflow_blockers",
    "rerun_public_universe_pipeline_reports",
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
    "audit_data_unverified",
    "end_to_end_audit_only",
)
STAGE_TRUE_SAFETY_FIELDS = (
    "safety_confirmed",
    "no_network_called",
    "no_fetch_executed",
    "no_cache_mutated_without_authorization",
    "no_evidence_extraction",
    "no_evidence_verification",
    "no_verified_evidence_promotion",
    "no_approval",
    "no_trust_claim",
    "no_investability_claim",
    "no_recommendation",
    "no_allocation",
    "no_buy_sell_signal",
    "no_trade",
    "no_registry_mutation",
    "no_candidate_write",
    "no_executor",
    "public_data_only",
    "manual_trust_required",
    "manual_approval_required",
    "final_purchase_external_manual_only",
)


@dataclass(frozen=True)
class PublicUniverseEndToEndWorkflowAuditResult:
    title: str
    version: str
    status: str
    audit_mode: str
    stage_count: int
    required_stage_count: int
    missing_stage_count: int
    duplicate_stage_count: int
    out_of_order_stage_count: int
    ready_stage_count: int
    partial_stage_count: int
    blocked_stage_count: int
    handoff_count: int
    ready_handoff_count: int
    partial_handoff_count: int
    blocked_handoff_count: int
    warning_count: int
    blocker_count: int
    workflow_counts: dict[str, Any]
    workflow_readiness_label: str
    v5_final_audit_readiness_label: str
    next_safe_action: str
    do_not_build_next: tuple[str, ...]
    stage_rows: tuple[dict[str, Any], ...]
    handoff_rows: tuple[dict[str, Any], ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
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
    audit_data_unverified: bool = True


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


def validate_e2e_audit_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
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
            blocked.append(f"{field} must be true.")
    for field in ("workflow_policy", "authorization_policy", "workflow_counts", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blocked.append(f"{field} must be an object.")
    for field in ("required_stage_order", "stage_audit_records", "handoff_audit_records"):
        if not isinstance(config.get(field, []), list):
            blocked.append(f"{field} must be a list.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)):
            blocked.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"safety_controls.{field} must be true.")
    action = normalize_text(config.get("next_manual_action"))
    if action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be valid.")
    if action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {action}.")
    policy = config.get("authorization_policy", {})
    if isinstance(policy, dict):
        expected = {
            "explicit_authorization_required": True,
            "default_write_allowed": False,
            "write_allowed_only_with_explicit_authorization": True,
            "local_cache_only": True,
            "audit_data_unverified": True,
            "no_evidence_verification": True,
            "no_approval": True,
            "no_allocation": True,
            "no_trade": True,
            "no_executor": True,
        }
        for field, value in expected.items():
            if policy.get(field) is not value:
                blocked.append(f"authorization_policy.{field} must be {str(value).lower()}.")
        if policy.get("required_authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
            blocked.append("authorization_policy.required_authorization_phrase must match.")
    return tuple(dict.fromkeys(blocked))


def validate_stage_audit_record(stage: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "stage_id",
        "stage_name",
        "version",
        "status",
        "expected_role",
        "input_count",
        "output_count",
        "blocker_count",
        "warning_count",
        "next_safe_action",
    )
    for field in required:
        if field not in stage:
            blocked.append(f"{field} is required.")
    for field in ("input_count", "output_count", "blocker_count", "warning_count"):
        if not isinstance(stage.get(field), int) or stage.get(field) < 0:
            blocked.append(f"{field} must be a non-negative integer.")
    for field in STAGE_TRUE_SAFETY_FIELDS:
        if stage.get(field) is not True:
            blocked.append(f"{field} must be true.")
    return tuple(blocked)


def validate_handoff_audit_record(handoff: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "from_stage_id",
        "to_stage_id",
        "handoff_name",
        "expected_input_label",
        "expected_output_label",
        "input_count",
        "output_count",
        "handoff_status",
        "blockers",
        "warnings",
    )
    for field in required:
        if field not in handoff:
            blocked.append(f"{field} is required.")
    for field in ("input_count", "output_count"):
        if not isinstance(handoff.get(field), int) or handoff.get(field) < 0:
            blocked.append(f"{field} must be a non-negative integer.")
    if handoff.get("handoff_status") not in ALLOWED_HANDOFF_STATUSES:
        blocked.append("handoff_status is not allowed.")
    if not isinstance(handoff.get("blockers", []), list):
        blocked.append("blockers must be a list.")
    if not isinstance(handoff.get("warnings", []), list):
        blocked.append("warnings must be a list.")
    return tuple(blocked)


def audit_required_stage_order(required_stage_order: list[Any] | tuple[Any, ...], stage_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any]:
    expected = tuple(normalize_text(stage_id) for stage_id in required_stage_order)
    observed = tuple(normalize_text(stage.get("stage_id")) for stage in stage_audit_records)
    missing = tuple(stage_id for stage_id in expected if stage_id not in observed)
    duplicates = tuple(stage_id for stage_id in observed if observed.count(stage_id) > 1)
    out_of_order = observed != expected[: len(observed)] or tuple(stage_id for stage_id in observed if stage_id in expected) != tuple(stage_id for stage_id in expected if stage_id in observed)
    blockers: list[str] = []
    if expected != REQUIRED_STAGE_ORDER:
        blockers.append("required_stage_order must match v4.61-v4.70 exact order.")
    if missing:
        blockers.append("missing required stage ids: " + ", ".join(missing))
    if duplicates:
        blockers.append("duplicate stage ids: " + ", ".join(tuple(dict.fromkeys(duplicates))))
    if out_of_order and observed:
        blockers.append("stage order is not the required v4.61-v4.70 order.")
    return {
        "missing_stage_count": len(missing),
        "duplicate_stage_count": len(set(duplicates)),
        "out_of_order_stage_count": 1 if out_of_order and observed else 0,
        "blockers": tuple(blockers),
        "warnings": (),
    }


def _classify_stage(stage: dict[str, Any]) -> str:
    status = normalize_text(stage.get("status")).upper()
    if stage.get("blocker_count", 0) > 0 or "BLOCKED" in status:
        return "blocked"
    if "PARTIAL" in status or "STALE" in status or "MISSING" in status:
        return "partial"
    if "READY" in status or "SAFE" in status:
        return "ready"
    return "partial"


def audit_stage_safety(stage_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    for stage in stage_audit_records:
        stage_id = normalize_text(stage.get("stage_id")) or "unknown"
        reasons = validate_stage_audit_record(stage)
        blockers.extend(f"{stage_id}: {reason}" for reason in reasons)
        readiness = _classify_stage(stage)
        if stage.get("warning_count", 0):
            warnings.append(f"{stage_id}: warning_count={stage.get('warning_count')}")
        rows.append(
            {
                "stage_id": stage_id,
                "stage_name": stage.get("stage_name"),
                "version": stage.get("version"),
                "status": stage.get("status"),
                "expected_role": stage.get("expected_role"),
                "readiness": readiness,
                "input_count": stage.get("input_count", 0),
                "output_count": stage.get("output_count", 0),
                "blocker_count": stage.get("blocker_count", 0),
                "warning_count": stage.get("warning_count", 0),
                "next_safe_action": stage.get("next_safe_action"),
                "safety_confirmed": stage.get("safety_confirmed") is True,
            }
        )
    order = {stage_id: index for index, stage_id in enumerate(REQUIRED_STAGE_ORDER)}
    return {
        "rows": tuple(sorted(rows, key=lambda row: order.get(row["stage_id"], 999))),
        "ready_stage_count": sum(1 for row in rows if row["readiness"] == "ready"),
        "partial_stage_count": sum(1 for row in rows if row["readiness"] == "partial"),
        "blocked_stage_count": sum(1 for row in rows if row["readiness"] == "blocked"),
        "blockers": tuple(dict.fromkeys(blockers)),
        "warnings": tuple(dict.fromkeys(warnings)),
    }


def audit_handoffs(handoff_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    names = [normalize_text(record.get("handoff_name")) for record in handoff_audit_records if isinstance(record, dict)]
    for name in EXPECTED_HANDOFF_NAMES:
        if name not in names:
            blockers.append(f"missing expected handoff: {name}")
    for record in handoff_audit_records:
        if not isinstance(record, dict):
            blockers.append("handoff audit record must be an object.")
            continue
        name = normalize_text(record.get("handoff_name")) or "unknown"
        reasons = validate_handoff_audit_record(record)
        blockers.extend(f"{name}: {reason}" for reason in reasons)
        status = record.get("handoff_status")
        record_blockers = tuple(str(item) for item in record.get("blockers", []) if normalize_text(item))
        record_warnings = tuple(str(item) for item in record.get("warnings", []) if normalize_text(item))
        blockers.extend(f"{name}: {item}" for item in record_blockers)
        warnings.extend(f"{name}: {item}" for item in record_warnings)
        rows.append(
            {
                "handoff_name": name,
                "from_stage_id": record.get("from_stage_id"),
                "to_stage_id": record.get("to_stage_id"),
                "handoff_status": status,
                "input_count": record.get("input_count", 0),
                "output_count": record.get("output_count", 0),
                "blocker_count": len(record_blockers),
                "warning_count": len(record_warnings),
            }
        )
    order = {name: index for index, name in enumerate(EXPECTED_HANDOFF_NAMES)}
    return {
        "rows": tuple(sorted(rows, key=lambda row: order.get(row["handoff_name"], 999))),
        "ready_handoff_count": sum(1 for row in rows if row["handoff_status"] == "HANDOFF_READY_SAFE"),
        "partial_handoff_count": sum(1 for row in rows if row["handoff_status"] in {"HANDOFF_PARTIAL_SAFE", "HANDOFF_NOT_APPLICABLE_SAFE"}),
        "blocked_handoff_count": sum(1 for row in rows if row["handoff_status"] == "HANDOFF_BLOCKED_SAFE"),
        "blockers": tuple(dict.fromkeys(blockers)),
        "warnings": tuple(dict.fromkeys(warnings)),
    }


def audit_count_coherence(workflow_counts: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    blockers: list[str] = []
    counts = {key: value for key, value in workflow_counts.items() if isinstance(value, int)}
    for field in (
        "source_manifest_count",
        "fetch_plan_count",
        "local_cache_entry_count",
        "cache_audit_entry_count",
        "normalized_record_count",
        "classified_record_count",
        "research_queue_item_count",
        "evidence_pack_draft_count",
        "dashboard_stage_count",
        "blocked_stage_count",
        "warning_count",
        "blocker_count",
    ):
        if field not in counts or counts[field] < 0:
            blockers.append(f"workflow_counts.{field} must be a non-negative integer.")
    if counts.get("classified_record_count", 0) > counts.get("normalized_record_count", 0):
        warnings.append("classified_record_count exceeds normalized_record_count; operator explanation required.")
    if counts.get("research_queue_item_count", 0) > counts.get("classified_record_count", 0):
        warnings.append("research_queue_item_count exceeds classified_record_count; operator explanation required.")
    if counts.get("evidence_pack_draft_count", 0) > counts.get("research_queue_item_count", 0):
        warnings.append("evidence_pack_draft_count exceeds research_queue_item_count; operator explanation required.")
    if counts.get("dashboard_stage_count", 0) != len(REQUIRED_STAGE_ORDER):
        blockers.append("dashboard_stage_count must be 10 for complete workflow.")
    if counts.get("blocker_count", 0) > 0:
        blockers.append("workflow_counts.blocker_count must be 0 for v5-ready label.")
    if counts.get("blocked_stage_count", 0) > 0:
        blockers.append("workflow_counts.blocked_stage_count must be 0 for v5-ready label.")
    return {"blockers": tuple(blockers), "warnings": tuple(warnings)}


def compute_workflow_readiness(stage_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...], handoff_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...], workflow_counts: dict[str, Any]) -> str:
    order_audit = audit_required_stage_order(REQUIRED_STAGE_ORDER, stage_audit_records)
    stage_audit = audit_stage_safety(stage_audit_records)
    handoff_audit = audit_handoffs(handoff_audit_records)
    count_audit = audit_count_coherence(workflow_counts)
    if stage_audit["blocked_stage_count"] or handoff_audit["blocked_handoff_count"] or any("must be true" in blocker for blocker in stage_audit["blockers"]):
        return "PUBLIC_UNIVERSE_E2E_WORKFLOW_BLOCKED_SAFE"
    if count_audit["blockers"] and any("blocked_stage_count" in blocker or "blocker_count" in blocker for blocker in count_audit["blockers"]):
        return "PUBLIC_UNIVERSE_E2E_WORKFLOW_BLOCKED_SAFE"
    if order_audit["blockers"] or stage_audit["partial_stage_count"] or handoff_audit["partial_handoff_count"] or count_audit["blockers"]:
        return "PUBLIC_UNIVERSE_E2E_WORKFLOW_PARTIAL_SAFE"
    dashboard = next((stage for stage in stage_audit_records if stage.get("stage_id") == "v4.70_public_research_operator_dashboard"), {})
    if "READY" not in normalize_text(dashboard.get("status")).upper():
        return "PUBLIC_UNIVERSE_E2E_WORKFLOW_NEEDS_OPERATOR_REVIEW_SAFE"
    return "PUBLIC_UNIVERSE_E2E_WORKFLOW_READY_FOR_V5_FINAL_AUDIT_SAFE"


def compute_v5_final_audit_readiness(stage_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...], handoff_audit_records: list[dict[str, Any]] | tuple[dict[str, Any], ...], workflow_counts: dict[str, Any]) -> str:
    label = compute_workflow_readiness(stage_audit_records, handoff_audit_records, workflow_counts)
    if label == "PUBLIC_UNIVERSE_E2E_WORKFLOW_READY_FOR_V5_FINAL_AUDIT_SAFE":
        return "V5_FINAL_AUDIT_READY_TO_RUN"
    if label == "PUBLIC_UNIVERSE_E2E_WORKFLOW_BLOCKED_SAFE":
        return "V5_FINAL_AUDIT_BLOCKED_REQUIRES_SAFETY_REVIEW"
    return "V5_FINAL_AUDIT_PARTIAL_REQUIRES_FIXES"


def evaluate_public_universe_end_to_end_workflow_audit(config: dict[str, Any]) -> PublicUniverseEndToEndWorkflowAuditResult:
    config_blockers = list(validate_e2e_audit_config(config))
    required_stage_order = tuple(normalize_text(stage_id) for stage_id in config.get("required_stage_order", []))
    stage_records = tuple(stage for stage in config.get("stage_audit_records", []) if isinstance(stage, dict))
    handoff_records = tuple(handoff for handoff in config.get("handoff_audit_records", []) if isinstance(handoff, dict))
    workflow_counts = config.get("workflow_counts", {}) if isinstance(config.get("workflow_counts"), dict) else {}
    order_audit = audit_required_stage_order(required_stage_order, stage_records)
    stage_audit = audit_stage_safety(stage_records)
    handoff_audit = audit_handoffs(handoff_records)
    count_audit = audit_count_coherence(workflow_counts)
    config_warnings = tuple(str(item) for item in config.get("redundant_next_steps_to_avoid", []) if normalize_text(item))
    warnings = tuple(
        dict.fromkeys(
            list(stage_audit["warnings"])
            + list(handoff_audit["warnings"])
            + list(count_audit["warnings"])
        )
    )
    blockers = tuple(
        dict.fromkeys(
            config_blockers
            + list(order_audit["blockers"])
            + list(stage_audit["blockers"])
            + list(handoff_audit["blockers"])
            + list(count_audit["blockers"])
        )
    )
    workflow_label = compute_workflow_readiness(stage_records, handoff_records, workflow_counts)
    v5_label = compute_v5_final_audit_readiness(stage_records, handoff_records, workflow_counts)
    authorized = _authorization_valid(config)
    if config_blockers or workflow_label == "PUBLIC_UNIVERSE_E2E_WORKFLOW_BLOCKED_SAFE":
        status = "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE"
    elif blockers or workflow_label != "PUBLIC_UNIVERSE_E2E_WORKFLOW_READY_FOR_V5_FINAL_AUDIT_SAFE":
        status = "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_FOR_V5_FINAL_AUDIT_SAFE"
    return PublicUniverseEndToEndWorkflowAuditResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. Public Universe End-to-End Workflow Audit",
        version=normalize_text(config.get("version")) or "v4.71",
        status=status,
        audit_mode=normalize_text(config.get("audit_mode")),
        stage_count=len(stage_records),
        required_stage_count=len(REQUIRED_STAGE_ORDER),
        missing_stage_count=order_audit["missing_stage_count"],
        duplicate_stage_count=order_audit["duplicate_stage_count"],
        out_of_order_stage_count=order_audit["out_of_order_stage_count"],
        ready_stage_count=stage_audit["ready_stage_count"],
        partial_stage_count=stage_audit["partial_stage_count"],
        blocked_stage_count=stage_audit["blocked_stage_count"],
        handoff_count=len(handoff_records),
        ready_handoff_count=handoff_audit["ready_handoff_count"],
        partial_handoff_count=handoff_audit["partial_handoff_count"],
        blocked_handoff_count=handoff_audit["blocked_handoff_count"],
        warning_count=sum(stage.get("warning_count", 0) for stage in stage_records) + sum(row["warning_count"] for row in handoff_audit["rows"]) + len(warnings),
        blocker_count=sum(stage.get("blocker_count", 0) for stage in stage_records) + sum(row["blocker_count"] for row in handoff_audit["rows"]) + len(blockers),
        workflow_counts=dict(workflow_counts),
        workflow_readiness_label=workflow_label,
        v5_final_audit_readiness_label=v5_label,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
        stage_rows=stage_audit["rows"],
        handoff_rows=handoff_audit["rows"],
        blockers=blockers,
        warnings=warnings,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("e2e audit output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("e2e audit output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured e2e audit output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _result_payload(result: PublicUniverseEndToEndWorkflowAuditResult, created_at: str) -> dict[str, Any]:
    return {
        "audit_created_at": created_at,
        "audit_data_unverified": True,
        "status": result.status,
        "workflow_readiness_label": result.workflow_readiness_label,
        "v5_final_audit_readiness_label": result.v5_final_audit_readiness_label,
        "stage_rows": list(result.stage_rows),
        "handoff_rows": list(result.handoff_rows),
        "workflow_counts": result.workflow_counts,
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }


def execute_authorized_e2e_audit_cache_write(
    config: dict[str, Any],
    audit_result: PublicUniverseEndToEndWorkflowAuditResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    if audit_result.status not in {"PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_FOR_V5_FINAL_AUDIT_SAFE", "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_READY_TO_WRITE_SAFE"}:
        blockers.append("audit result must be ready before writing.")
    if blockers:
        return {"status": "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    audit_created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = _result_payload(audit_result, audit_created_at)
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.e2e_workflow_audit.json"
    metadata_path = output_root / "public_asset_universe.e2e_workflow_audit.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "audit_created_at": audit_created_at,
        "stage_count": audit_result.stage_count,
        "handoff_count": audit_result.handoff_count,
        "content_sha256": digest,
        "audit_data_unverified": True,
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
        "status": "PUBLIC_UNIVERSE_E2E_WORKFLOW_AUDIT_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_universe_end_to_end_workflow_audit_summary(result: PublicUniverseEndToEndWorkflowAuditResult) -> str:
    return (
        f"status={result.status}; stages={result.stage_count}/{result.required_stage_count}; "
        f"missing={result.missing_stage_count}; duplicates={result.duplicate_stage_count}; "
        f"out_of_order={result.out_of_order_stage_count}; handoffs={result.handoff_count}; "
        f"ready_handoffs={result.ready_handoff_count}; blocked={result.blocked_stage_count}; "
        f"workflow={result.workflow_readiness_label}; v5={result.v5_final_audit_readiness_label}"
    )


def load_public_universe_end_to_end_workflow_audit_result(path: str | Path) -> PublicUniverseEndToEndWorkflowAuditResult:
    return evaluate_public_universe_end_to_end_workflow_audit(load_json(path))
