"""Local operator bootstrap guide and smoke-test evaluator.

v4.60 is guide/report/smoke-test only. It documents safe manual bootstrap
commands as strings and validates the plan. It does not create directories,
copy templates, run subprocesses, fetch, schedule tasks, scan local/private
folders, ingest private files, verify evidence, mutate registries, approve,
recommend allocation, trade, or execute.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_TEMPLATE_PATHS = (
    "templates/jarvis_manual_candidate_watchlist_entry.local.template.json",
    "templates/jarvis_public_data_sources.local.template.json",
)

VALID_NEXT_MANUAL_ACTIONS = {
    "copy_templates_to_ignored_local_paths",
    "edit_local_candidate_watchlist",
    "configure_local_public_source_manifest",
    "run_dry_run_reports",
    "run_operator_dashboard",
}

BLOCKED_NEXT_MANUAL_ACTIONS = {
    "another_gate",
    "another_review_layer",
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_execution",
    "executor_creation",
    "scheduler_creation",
}

FALSE_REQUIRED_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "writes",
    "directory_creation",
    "template_copying_by_code",
    "subprocess_execution",
    "scheduler_creation",
    "source_parsing_as_evidence",
    "evidence_extraction",
    "evidence_verification",
    "verified_evidence_promotion",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_packet_file",
    "executor_created",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "broker_api_used",
    "credentials_used",
    "private_file_ingested",
    "automatic_private_data_ingest",
    "fetched_data_committed",
)

TRUE_REQUIRED_SAFETY_FIELDS = (
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
    "local_files_must_remain_uncommitted",
)


@dataclass(frozen=True)
class BootstrapTemplateEntry:
    template_id: str
    template_path: str
    recommended_local_copy_path: str
    purpose: str
    contains_private_data: bool
    should_commit_template: bool
    should_commit_local_copy: bool
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class LocalOperatorBootstrapResult:
    title: str
    version: str
    overall_status: str
    bootstrap_mode: str
    report_only: bool
    no_network: bool
    no_writes: bool
    no_subprocess: bool
    no_scheduler_creation: bool
    local_paths_not_created_by_code: bool
    templates: tuple[BootstrapTemplateEntry, ...]
    recommended_local_paths: tuple[str, ...]
    gitignore_expectations: tuple[str, ...]
    missing_gitignore_patterns: tuple[str, ...]
    gitignore_guardrail_status: str
    required_manual_commands: tuple[str, ...]
    reports_to_run_manually: tuple[str, ...]
    smoke_checks: tuple[str, ...]
    next_manual_action: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    network_calls: bool = False
    fetching: bool = False
    downloading: bool = False
    writes: bool = False
    directory_creation: bool = False
    template_copying_by_code: bool = False
    subprocess_execution: bool = False
    scheduler_creation: bool = False
    source_parsing_as_evidence: bool = False
    evidence_extraction: bool = False
    evidence_verification: bool = False
    verified_evidence_promotion: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    candidate_intake_file_written: bool = False
    persisted_packet_file: bool = False
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_private_data_ingest: bool = False
    fetched_data_committed: bool = False
    manual_trust_required: bool = True
    manual_approval_required: bool = True
    no_execution_invariant: bool = True
    local_files_must_remain_uncommitted: bool = True


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_local_path(path: str) -> tuple[str, ...]:
    normalized = path.replace("\\", "/").lower()
    if normalized.startswith(("jarvis/local/", "jarvis/private/", "local/", "private/")):
        if normalized.endswith(".json") and not normalized.endswith(".local.json") and "public_data_snapshots/" not in normalized:
            return ("local json paths should end with .local.json.",)
        return ()
    return ("recommended local path must be under jarvis/local, jarvis/private, local, or private.",)


def validate_template_entry(entry: dict[str, Any]) -> BootstrapTemplateEntry:
    blocked: list[str] = []
    template_path = _text(entry.get("template_path"))
    copy_path = _text(entry.get("recommended_local_copy_path"))
    for field in ("template_id", "template_path", "recommended_local_copy_path", "purpose"):
        if not _text(entry.get(field)):
            blocked.append(f"{field} is required.")
    if entry.get("contains_private_data") is not False:
        blocked.append("contains_private_data must be false.")
    if entry.get("should_commit_template") is not True:
        blocked.append("should_commit_template must be true.")
    if entry.get("should_commit_local_copy") is not False:
        blocked.append("should_commit_local_copy must be false.")
    blocked.extend(validate_local_path(copy_path))
    return BootstrapTemplateEntry(
        template_id=_text(entry.get("template_id")),
        template_path=template_path,
        recommended_local_copy_path=copy_path,
        purpose=_text(entry.get("purpose")),
        contains_private_data=_bool(entry.get("contains_private_data")),
        should_commit_template=_bool(entry.get("should_commit_template")),
        should_commit_local_copy=_bool(entry.get("should_commit_local_copy")),
        blocked_reasons=tuple(blocked),
    )


def validate_gitignore_expectations(patterns: tuple[str, ...], gitignore_text: str | None = None) -> tuple[str, ...]:
    if gitignore_text is None:
        gitignore_path = Path(".gitignore")
        gitignore_text = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    existing = {line.strip() for line in gitignore_text.splitlines() if line.strip() and not line.strip().startswith("#")}
    return tuple(pattern for pattern in patterns if pattern not in existing)


def validate_bootstrap_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in ("report_only", "no_network", "no_writes", "no_subprocess", "no_scheduler_creation", "local_paths_not_created_by_code"):
        if config.get(field) is not True:
            blocked.append(f"{field} must be true.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        blocked.append("safety_controls must be an object.")
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(config.get(field)) or _bool(safety.get(field)):
            blocked.append(f"{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"{field} must be true.")
    templates = config.get("templates", [])
    if not isinstance(templates, list):
        blocked.append("templates must be a list.")
        templates = []
    template_paths = {_text(entry.get("template_path")) for entry in templates if isinstance(entry, dict)}
    for required in REQUIRED_TEMPLATE_PATHS:
        if required not in template_paths:
            blocked.append(f"required template missing: {required}")
    local_paths = _list(config.get("recommended_local_paths"))
    if not local_paths:
        blocked.append("recommended_local_paths must not be empty.")
    for path in local_paths:
        blocked.extend(validate_local_path(path))
    next_action = _text(config.get("next_manual_action"))
    if next_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be an allowed local operator action.")
    if next_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_action}.")
    for field in ("required_manual_commands", "reports_to_run_manually"):
        values = config.get(field, [])
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            blocked.append(f"{field} must be a list of strings.")
    return tuple(blocked)


def evaluate_local_operator_bootstrap(
    config: dict[str, Any], gitignore_text: str | None = None
) -> LocalOperatorBootstrapResult:
    templates = tuple(validate_template_entry(entry) for entry in config.get("templates", []) if isinstance(entry, dict))
    blocked = list(validate_bootstrap_config(config))
    blocked.extend(f"{template.template_id}: {reason}" for template in templates for reason in template.blocked_reasons)
    gitignore_expectations = _list(config.get("gitignore_expectations"))
    missing_gitignore = validate_gitignore_expectations(gitignore_expectations, gitignore_text=gitignore_text)
    warnings = []
    if missing_gitignore:
        warnings.append("some gitignore guardrail patterns are missing.")
    if blocked:
        status = "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE"
    elif warnings or len(templates) < len(REQUIRED_TEMPLATE_PATHS):
        status = "LOCAL_OPERATOR_BOOTSTRAP_PARTIAL_SAFE"
    else:
        status = "LOCAL_OPERATOR_BOOTSTRAP_READY_SAFE"
    safety = config.get("safety_controls", {}) if isinstance(config.get("safety_controls"), dict) else {}
    return LocalOperatorBootstrapResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Local Operator Bootstrap",
        version=_text(config.get("version")) or "v4.60",
        overall_status=status,
        bootstrap_mode=_text(config.get("bootstrap_mode")),
        report_only=_bool(config.get("report_only")),
        no_network=_bool(config.get("no_network")),
        no_writes=_bool(config.get("no_writes")),
        no_subprocess=_bool(config.get("no_subprocess")),
        no_scheduler_creation=_bool(config.get("no_scheduler_creation")),
        local_paths_not_created_by_code=_bool(config.get("local_paths_not_created_by_code")),
        templates=templates,
        recommended_local_paths=_list(config.get("recommended_local_paths")),
        gitignore_expectations=gitignore_expectations,
        missing_gitignore_patterns=missing_gitignore,
        gitignore_guardrail_status="complete" if not missing_gitignore else "partial",
        required_manual_commands=_list(config.get("required_manual_commands")),
        reports_to_run_manually=_list(config.get("reports_to_run_manually")),
        smoke_checks=_list(config.get("smoke_checks")),
        next_manual_action=_text(config.get("next_manual_action")),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(warnings),
        **{field: _bool(safety.get(field)) for field in FALSE_REQUIRED_SAFETY_FIELDS},
        **{field: _bool(safety.get(field)) for field in TRUE_REQUIRED_SAFETY_FIELDS},
    )


def render_bootstrap_summary(result: LocalOperatorBootstrapResult) -> str:
    return (
        f"status={result.overall_status}; templates={len(result.templates)}; "
        f"gitignore={result.gitignore_guardrail_status}; next={result.next_manual_action}"
    )


def load_local_operator_bootstrap_result(path: str | Path) -> LocalOperatorBootstrapResult:
    return evaluate_local_operator_bootstrap(load_json(path))
