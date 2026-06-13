"""Public research operator dashboard integration.

v4.70 summarizes the public-universe research pipeline from v4.61 through
v4.69. It is dashboard/report integration only: no fetching, cache writing,
evidence extraction, evidence verification, approval, recommendation,
allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_RESEARCH_DASHBOARD_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/operator_dashboard")
REQUIRED_STAGE_IDS = (
    "v4.61_discovery_plan",
    "v4.62_source_manifest",
    "v4.63_fetch_dry_run_planner",
    "v4.64_local_cache_builder",
    "v4.65_cache_integrity_freshness_audit",
    "v4.66_normalizer",
    "v4.67_classifier",
    "v4.68_research_priority_queue",
    "v4.69_public_evidence_pack_draft_generator",
)
VALID_NEXT_MANUAL_ACTIONS = {
    "review_operator_research_dashboard",
    "proceed_to_end_to_end_public_universe_workflow_audit",
    "fix_public_universe_stage_blockers",
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
    "dashboard_data_unverified",
    "operator_dashboard_only",
)


@dataclass(frozen=True)
class PublicResearchOperatorDashboardResult:
    title: str
    version: str
    status: str
    dashboard_mode: str
    stage_count: int
    ready_stage_count: int
    partial_stage_count: int
    blocked_stage_count: int
    warning_count: int
    blocker_count: int
    normalized_record_count: int
    classified_record_count: int
    research_queue_item_count: int
    draft_pack_count: int
    high_ready_research_count: int
    medium_ready_research_count: int
    needs_more_public_data_count: int
    needs_manual_source_review_count: int
    blocked_safe_count: int
    pipeline_readiness_label: str
    v5_mvp_readiness_label: str
    next_safe_action: str
    do_not_build_next: tuple[str, ...]
    dashboard_sections: tuple[str, ...]
    stage_rows: tuple[dict[str, Any], ...]
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
    no_executor: bool = True
    local_cache_only: bool = True
    dashboard_data_unverified: bool = True


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


def validate_dashboard_config(config: dict[str, Any]) -> tuple[str, ...]:
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
    for field in ("dashboard_policy", "authorization_policy", "public_universe_counts", "safety_controls"):
        if not isinstance(config.get(field), dict):
            blocked.append(f"{field} must be an object.")
    if not isinstance(config.get("public_universe_stage_summaries", []), list):
        blocked.append("public_universe_stage_summaries must be a list.")
    if not isinstance(config.get("public_universe_blockers", []), list):
        blocked.append("public_universe_blockers must be a list.")
    if not isinstance(config.get("public_universe_warnings", []), list):
        blocked.append("public_universe_warnings must be a list.")
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
            "dashboard_data_unverified": True,
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


def validate_stage_summary(stage: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "stage_id",
        "stage_name",
        "version",
        "status",
        "ready_count",
        "partial_count",
        "blocked_count",
        "item_count",
        "blocker_count",
        "warning_count",
        "next_safe_action",
    )
    for field in required:
        if field not in stage:
            blocked.append(f"{field} is required.")
    for field in (
        "safety_confirmed",
        "no_network_called",
        "no_fetch_executed",
        "no_evidence_verification",
        "no_approval",
        "no_allocation",
        "no_trade",
        "no_executor",
    ):
        if stage.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("ready_count", "partial_count", "blocked_count", "item_count", "blocker_count", "warning_count"):
        if not isinstance(stage.get(field), int) or stage.get(field) < 0:
            blocked.append(f"{field} must be a non-negative integer.")
    return tuple(blocked)


def classify_stage_readiness(stage: dict[str, Any]) -> str:
    status = normalize_text(stage.get("status")).upper()
    if stage.get("blocker_count", 0) > 0 or stage.get("blocked_count", 0) > 0 or "BLOCKED" in status:
        return "blocked"
    if stage.get("partial_count", 0) > 0 or "PARTIAL" in status or "STALE" in status or "MANUAL_REVIEW" in status:
        return "partial"
    if stage.get("ready_count", 0) > 0 or "READY" in status or "SAFE" in status:
        return "ready"
    return "partial"


def compute_pipeline_readiness(stage_summaries: tuple[dict[str, Any], ...], counts: dict[str, Any]) -> str:
    readiness = [classify_stage_readiness(stage) for stage in stage_summaries]
    required_present = {stage.get("stage_id") for stage in stage_summaries}
    if any(value == "blocked" for value in readiness):
        return "PUBLIC_RESEARCH_PIPELINE_BLOCKED_SAFE"
    if not set(REQUIRED_STAGE_IDS).issubset(required_present):
        return "PUBLIC_RESEARCH_PIPELINE_PARTIAL_SAFE"
    if any(value == "partial" for value in readiness):
        return "PUBLIC_RESEARCH_PIPELINE_PARTIAL_SAFE"
    if counts.get("draft_pack_count", 0) > 0:
        return "PUBLIC_RESEARCH_PIPELINE_READY_FOR_WORKFLOW_AUDIT_SAFE"
    return "PUBLIC_RESEARCH_PIPELINE_NEEDS_OPERATOR_REVIEW_SAFE"


def compute_v5_mvp_readiness(stage_summaries: tuple[dict[str, Any], ...], counts: dict[str, Any]) -> str:
    label = compute_pipeline_readiness(stage_summaries, counts)
    if label == "PUBLIC_RESEARCH_PIPELINE_READY_FOR_WORKFLOW_AUDIT_SAFE":
        return "V5_MVP_NEAR_READY_REQUIRES_END_TO_END_AUDIT"
    if label == "PUBLIC_RESEARCH_PIPELINE_BLOCKED_SAFE":
        return "V5_MVP_BLOCKED_REQUIRES_SAFETY_REVIEW"
    return "V5_MVP_PARTIAL_REQUIRES_FIXES"


def build_stage_rows(stage_summaries: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for stage in stage_summaries:
        readiness = classify_stage_readiness(stage)
        rows.append(
            {
                "stage_id": stage.get("stage_id"),
                "stage_name": stage.get("stage_name"),
                "version": stage.get("version"),
                "status": stage.get("status"),
                "readiness": readiness,
                "ready": readiness == "ready",
                "item_count": stage.get("item_count", 0),
                "blocker_count": stage.get("blocker_count", 0),
                "warning_count": stage.get("warning_count", 0),
                "next_safe_action": stage.get("next_safe_action"),
                "safety_confirmed": stage.get("safety_confirmed") is True,
            }
        )
    order = {stage_id: index for index, stage_id in enumerate(REQUIRED_STAGE_IDS)}
    return tuple(sorted(rows, key=lambda row: order.get(row["stage_id"], 999)))


def build_dashboard_sections(config: dict[str, Any], stage_summaries: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    return (
        "public_universe_pipeline_stage_table",
        "public_research_counts",
        "queue_and_draft_pack_summary",
        "blockers_and_warnings",
        "pipeline_readiness",
        "v5_mvp_readiness",
        "operator_next_action",
        "safety_invariant",
    )


def _count_value(counts: dict[str, Any], field: str) -> int:
    value = counts.get(field, 0)
    return value if isinstance(value, int) and value >= 0 else 0


def evaluate_public_research_operator_dashboard(config: dict[str, Any]) -> PublicResearchOperatorDashboardResult:
    config_blockers = list(validate_dashboard_config(config))
    raw_stages = config.get("public_universe_stage_summaries", [])
    stage_summaries: list[dict[str, Any]] = []
    stage_blockers: list[str] = []
    if isinstance(raw_stages, list):
        for stage in raw_stages:
            if not isinstance(stage, dict):
                stage_blockers.append("stage summary must be an object.")
                continue
            stage_id = normalize_text(stage.get("stage_id")) or "unknown"
            reasons = validate_stage_summary(stage)
            if reasons:
                stage_blockers.append(f"{stage_id}: {'; '.join(reasons)}")
            stage_summaries.append(stage)
    present_ids = {normalize_text(stage.get("stage_id")) for stage in stage_summaries}
    missing_stage_ids = tuple(stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id not in present_ids)
    if missing_stage_ids:
        stage_blockers.append("missing required stage ids: " + ", ".join(missing_stage_ids))
    counts = config.get("public_universe_counts", {}) if isinstance(config.get("public_universe_counts"), dict) else {}
    stage_rows = build_stage_rows(tuple(stage_summaries))
    ready_stage_count = sum(1 for row in stage_rows if row["readiness"] == "ready")
    partial_stage_count = sum(1 for row in stage_rows if row["readiness"] == "partial")
    blocked_stage_count = sum(1 for row in stage_rows if row["readiness"] == "blocked")
    warnings = tuple(dict.fromkeys(str(item) for item in config.get("public_universe_warnings", []) if normalize_text(item)))
    explicit_blockers = tuple(str(item) for item in config.get("public_universe_blockers", []) if normalize_text(item))
    blockers = tuple(dict.fromkeys(config_blockers + list(stage_blockers) + list(explicit_blockers)))
    pipeline_label = compute_pipeline_readiness(tuple(stage_summaries), counts)
    v5_label = compute_v5_mvp_readiness(tuple(stage_summaries), counts)
    authorized = _authorization_valid(config)
    if config_blockers or blocked_stage_count > 0 or pipeline_label == "PUBLIC_RESEARCH_PIPELINE_BLOCKED_SAFE":
        status = "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_BLOCKED_SAFE"
    elif blockers or partial_stage_count > 0 or pipeline_label != "PUBLIC_RESEARCH_PIPELINE_READY_FOR_WORKFLOW_AUDIT_SAFE":
        status = "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_SAFE"
    return PublicResearchOperatorDashboardResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. Public Research Operator Dashboard",
        version=normalize_text(config.get("version")) or "v4.70",
        status=status,
        dashboard_mode=normalize_text(config.get("dashboard_mode")),
        stage_count=len(stage_rows),
        ready_stage_count=ready_stage_count,
        partial_stage_count=partial_stage_count,
        blocked_stage_count=blocked_stage_count,
        warning_count=sum(row["warning_count"] for row in stage_rows) + len(warnings),
        blocker_count=sum(row["blocker_count"] for row in stage_rows) + len(blockers),
        normalized_record_count=_count_value(counts, "normalized_record_count"),
        classified_record_count=_count_value(counts, "classified_record_count"),
        research_queue_item_count=_count_value(counts, "research_queue_item_count"),
        draft_pack_count=_count_value(counts, "draft_pack_count"),
        high_ready_research_count=_count_value(counts, "high_ready_research_count"),
        medium_ready_research_count=_count_value(counts, "medium_ready_research_count"),
        needs_more_public_data_count=_count_value(counts, "needs_more_public_data_count"),
        needs_manual_source_review_count=_count_value(counts, "needs_manual_source_review_count"),
        blocked_safe_count=_count_value(counts, "blocked_safe_count"),
        pipeline_readiness_label=pipeline_label,
        v5_mvp_readiness_label=v5_label,
        next_safe_action=normalize_text(config.get("next_manual_action")),
        do_not_build_next=DO_NOT_BUILD_NEXT,
        dashboard_sections=build_dashboard_sections(config, tuple(stage_summaries)),
        stage_rows=stage_rows,
        blockers=blockers,
        warnings=warnings,
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("operator dashboard output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("operator dashboard output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured operator dashboard output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _result_payload(result: PublicResearchOperatorDashboardResult, created_at: str) -> dict[str, Any]:
    return {
        "dashboard_created_at": created_at,
        "dashboard_data_unverified": True,
        "status": result.status,
        "pipeline_readiness_label": result.pipeline_readiness_label,
        "v5_mvp_readiness_label": result.v5_mvp_readiness_label,
        "stage_rows": list(result.stage_rows),
        "public_universe_counts": {
            "normalized_record_count": result.normalized_record_count,
            "classified_record_count": result.classified_record_count,
            "research_queue_item_count": result.research_queue_item_count,
            "draft_pack_count": result.draft_pack_count,
        },
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
    }


def execute_authorized_operator_dashboard_cache_write(
    config: dict[str, Any],
    dashboard_result: PublicResearchOperatorDashboardResult,
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    if dashboard_result.status not in {"PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_SAFE", "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_READY_TO_WRITE_SAFE"}:
        blockers.append("dashboard result must be ready before writing.")
    if blockers:
        return {"status": "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    dashboard_created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = _result_payload(dashboard_result, dashboard_created_at)
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.operator_dashboard.json"
    metadata_path = output_root / "public_asset_universe.operator_dashboard.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "dashboard_created_at": dashboard_created_at,
        "stage_count": dashboard_result.stage_count,
        "content_sha256": digest,
        "dashboard_data_unverified": True,
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
        "status": "PUBLIC_RESEARCH_OPERATOR_DASHBOARD_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_research_operator_dashboard_summary(result: PublicResearchOperatorDashboardResult) -> str:
    return (
        f"status={result.status}; stages={result.stage_count}; ready={result.ready_stage_count}; "
        f"partial={result.partial_stage_count}; blocked={result.blocked_stage_count}; "
        f"normalized={result.normalized_record_count}; classified={result.classified_record_count}; "
        f"queue={result.research_queue_item_count}; drafts={result.draft_pack_count}; "
        f"pipeline={result.pipeline_readiness_label}; v5={result.v5_mvp_readiness_label}"
    )


def load_public_research_operator_dashboard_result(path: str | Path) -> PublicResearchOperatorDashboardResult:
    return evaluate_public_research_operator_dashboard(load_json(path))
