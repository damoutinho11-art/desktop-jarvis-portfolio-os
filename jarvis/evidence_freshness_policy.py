"""Evidence freshness and refresh-policy checks for verified evidence intake."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, load_asset_registry
from .public_source_fetcher import load_public_source_configs, run_public_source_fetcher
from .verified_evidence_intake import load_verified_evidence_intake


REFERENCE_DATE = date(2026, 6, 7)
REFRESH_MODES = {
    "public_auto_refresh_allowed",
    "manual_refresh_required",
    "account_specific_manual_required",
    "no_refresh_required",
}
ETF_EVIDENCE_TYPES = {
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "market_data",
    "exposure_data",
    "tax_route",
    "platform_availability",
}
CRYPTO_EVIDENCE_TYPES = {
    "protocol_metadata",
    "market_data",
    "platform_availability",
    "custody_route",
    "tax_route",
    "crypto_risk_notes",
}


@dataclass(frozen=True)
class EvidenceFreshnessRule:
    evidence_type: str
    max_age_days: int
    refresh_mode: str
    source_types_allowed: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class EvidenceFreshnessConfig:
    target_asset_ids: tuple[str, ...]
    rules: tuple[EvidenceFreshnessRule, ...]
    public_source_fetch_path: str | None


@dataclass(frozen=True)
class EvidenceFreshnessResult:
    asset_id: str
    evidence_type: str
    evidence_id: str | None
    as_of: str | None
    age_days: int | None
    freshness_status: str
    refresh_mode: str
    auto_refresh_available: bool
    manual_refresh_required: bool
    account_specific_required: bool
    recommended_action: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceFreshnessSummary:
    target_assets_checked: tuple[str, ...]
    fresh_count: int
    stale_count: int
    missing_count: int
    invalid_date_count: int
    auto_refresh_available_count: int
    manual_refresh_required_count: int
    account_specific_refresh_required_count: int
    recommended_actions_by_evidence_type: dict[str, str]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceFreshnessPack:
    freshness_report_status: str
    results: tuple[EvidenceFreshnessResult, ...]
    summary: EvidenceFreshnessSummary
    draft_refresh_records: tuple[dict[str, object], ...]
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _require_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer.")
    return value


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def _parse_rule(raw: dict[str, Any]) -> EvidenceFreshnessRule:
    item = _require_mapping(raw, "freshness rule")
    refresh_mode = _require_text(item.get("refresh_mode"), "refresh_mode")
    if refresh_mode not in REFRESH_MODES:
        raise ValueError(f"refresh_mode {refresh_mode} is not allowed.")
    return EvidenceFreshnessRule(
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        max_age_days=_require_int(item.get("max_age_days"), "max_age_days"),
        refresh_mode=refresh_mode,
        source_types_allowed=_require_text_list(item.get("source_types_allowed"), "source_types_allowed"),
        notes=_require_text(item.get("notes"), "notes"),
    )


def load_evidence_freshness_config(path: str | Path) -> EvidenceFreshnessConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "evidence freshness policy")
    rules = raw.get("rules")
    if not isinstance(rules, list):
        raise ValueError("evidence freshness policy must contain a rules list.")
    target_assets = raw.get("target_asset_ids", ["vwce_global_core_candidate"])
    public_source_fetch_path = raw.get("public_source_fetch_path")
    if public_source_fetch_path is not None and not isinstance(public_source_fetch_path, str):
        raise ValueError("public_source_fetch_path must be text when provided.")
    return EvidenceFreshnessConfig(
        target_asset_ids=_require_text_list(target_assets, "target_asset_ids"),
        rules=tuple(_parse_rule(rule) for rule in rules),
        public_source_fetch_path=public_source_fetch_path,
    )


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _recommended_action(status: str, rule: EvidenceFreshnessRule) -> str:
    if status == "fresh":
        return "keep_current_evidence"
    if rule.refresh_mode == "public_auto_refresh_allowed":
        return "public_refresh_draft"
    if rule.refresh_mode == "account_specific_manual_required":
        return "manual_account_reverification"
    if rule.refresh_mode == "manual_refresh_required":
        return "manual_review"
    return "no_refresh_required"


def _result_for_record(asset_id: str, rule: EvidenceFreshnessRule, record: dict[str, Any] | None) -> EvidenceFreshnessResult:
    warnings: list[str] = []
    blockers: list[str] = []
    if record is None:
        status = "missing"
        age_days = None
        as_of = None
        evidence_id = None
    else:
        evidence_id = str(record.get("evidence_id", ""))
        as_of = str(record.get("as_of", ""))
        try:
            age_days = (REFERENCE_DATE - _parse_date(as_of)).days
            status = "fresh" if age_days <= rule.max_age_days else "stale"
        except ValueError:
            age_days = None
            status = "invalid_date"
            warnings.append(f"{evidence_id}: invalid as_of date {as_of}.")

    action = _recommended_action(status, rule)
    return EvidenceFreshnessResult(
        asset_id=asset_id,
        evidence_type=rule.evidence_type,
        evidence_id=evidence_id,
        as_of=as_of,
        age_days=age_days,
        freshness_status=status,
        refresh_mode=rule.refresh_mode,
        auto_refresh_available=action == "public_refresh_draft",
        manual_refresh_required=action in {"manual_review", "manual_account_reverification"},
        account_specific_required=action == "manual_account_reverification",
        recommended_action=action,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def _latest_records_by_asset_and_type(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        asset_id = str(record.get("asset_id", ""))
        evidence_type = str(record.get("evidence_type", ""))
        key = (asset_id, evidence_type)
        if key not in latest:
            latest[key] = record
            continue
        current_as_of = str(latest[key].get("as_of", ""))
        candidate_as_of = str(record.get("as_of", ""))
        if candidate_as_of > current_as_of:
            latest[key] = record
    return latest


def _rules_for_asset(asset_type: str, rules: tuple[EvidenceFreshnessRule, ...]) -> tuple[EvidenceFreshnessRule, ...]:
    allowed = CRYPTO_EVIDENCE_TYPES if asset_type == "crypto" else ETF_EVIDENCE_TYPES
    return tuple(rule for rule in rules if rule.evidence_type in allowed)


def _draft_refresh_records(
    registry_path: str | Path | AssetRegistry,
    config: EvidenceFreshnessConfig,
    results: tuple[EvidenceFreshnessResult, ...],
) -> tuple[dict[str, object], ...]:
    if not config.public_source_fetch_path:
        return ()
    needed = {
        (result.asset_id, result.evidence_type)
        for result in results
        if result.auto_refresh_available
    }
    if not needed:
        return ()
    run = run_public_source_fetcher(registry_path, config.public_source_fetch_path)
    source_configs_by_id = {config_item.source_id: config_item for config_item in load_public_source_configs(config.public_source_fetch_path)}
    drafts: list[dict[str, object]] = []
    for item in run.results:
        record = item.draft_evidence_record
        source_config = source_configs_by_id.get(item.source_id)
        if record is None or source_config is None:
            continue
        if (str(record["asset_id"]), str(record["evidence_type"])) not in needed:
            continue
        if source_config.source_type not in next(
            rule.source_types_allowed
            for rule in config.rules
            if rule.evidence_type == str(record["evidence_type"])
        ):
            continue
        draft = dict(record)
        draft["evidence_id"] = f"refresh_{draft['evidence_id']}"
        draft["verified_by_user"] = False
        draft["verification_notes"] = "Auto-refresh public evidence draft. User verification required."
        drafts.append(draft)
    return tuple(drafts)


def build_evidence_freshness_pack(
    registry_path: str | Path | AssetRegistry,
    intake_path: str | Path,
    config: EvidenceFreshnessConfig,
) -> EvidenceFreshnessPack:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    blockers: list[str] = []
    for asset_id in config.target_asset_ids:
        if asset_id not in assets_by_id:
            blockers.append(f"{asset_id}: target asset not found in registry.")

    records = load_verified_evidence_intake(intake_path)
    latest = _latest_records_by_asset_and_type(records)
    result_items: list[EvidenceFreshnessResult] = []
    for asset_id in config.target_asset_ids:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            continue
        for rule in _rules_for_asset(asset.asset_type, config.rules):
            result_items.append(_result_for_record(asset_id, rule, latest.get((asset_id, rule.evidence_type))))
    results = tuple(result_items)
    blockers.extend(blocker for result in results for blocker in result.blockers)
    warnings = tuple(dict.fromkeys(warning for result in results for warning in result.warnings))
    drafts = _draft_refresh_records(registry_path, config, results)
    actions = {f"{result.asset_id}:{result.evidence_type}": result.recommended_action for result in results}
    summary = EvidenceFreshnessSummary(
        target_assets_checked=config.target_asset_ids,
        fresh_count=sum(result.freshness_status == "fresh" for result in results),
        stale_count=sum(result.freshness_status == "stale" for result in results),
        missing_count=sum(result.freshness_status == "missing" for result in results),
        invalid_date_count=sum(result.freshness_status == "invalid_date" for result in results),
        auto_refresh_available_count=sum(result.auto_refresh_available for result in results),
        manual_refresh_required_count=sum(result.manual_refresh_required for result in results),
        account_specific_refresh_required_count=sum(result.account_specific_required for result in results),
        recommended_actions_by_evidence_type=dict(sorted(actions.items())),
        warnings=warnings,
        blockers=tuple(dict.fromkeys(blockers)),
    )
    status = "BLOCKED" if blockers else "WARNING" if summary.stale_count or summary.missing_count or summary.invalid_date_count else "FRESH"
    return EvidenceFreshnessPack(
        freshness_report_status=status,
        results=results,
        summary=summary,
        draft_refresh_records=drafts,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_evidence_freshness_pack_from_files(
    registry_path: str | Path,
    intake_path: str | Path,
    config_path: str | Path,
) -> EvidenceFreshnessPack:
    return build_evidence_freshness_pack(
        registry_path,
        intake_path,
        load_evidence_freshness_config(config_path),
    )


def write_draft_refresh_records(pack: EvidenceFreshnessPack, path: str | Path) -> Path:
    if not pack.draft_refresh_records:
        raise ValueError("no draft refresh records available to write.")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"records": list(pack.draft_refresh_records)}, indent=2, sort_keys=True), encoding="utf-8")
    return target
