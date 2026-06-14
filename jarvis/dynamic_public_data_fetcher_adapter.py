"""Dynamic public data fetcher adapter for J.A.R.V.I.S.

Adapter-only bridge from dynamic portfolio market import rows into the existing
jarvis_public_data_fetcher config shape.

This module does not fetch, download, scrape, call APIs, write cache files,
connect to brokers, create buy requests, approve assets, mutate registries, or
execute trades.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_market_import_plan import (
    STATUS_READY as IMPORT_PLAN_READY,
    build_dynamic_market_import_plan,
)
from .jarvis_public_data_fetcher import (
    AUTHORIZATION_PHRASE,
    validate_fetcher_config,
    validate_source,
)


STATUS_READY = "DYNAMIC_PUBLIC_DATA_FETCHER_ADAPTER_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_PUBLIC_DATA_FETCHER_ADAPTER_BLOCKED_SAFE"


@dataclass(frozen=True)
class DynamicPublicDataFetcherAdapterRow:
    asset_id: str
    source_id: str
    source_type: str | None
    source_url: str | None
    update_frequency: str | None
    cache_series_id: str | None
    expected_currency: str | None
    valid_for_public_fetcher: bool
    status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "update_frequency": self.update_frequency,
            "cache_series_id": self.cache_series_id,
            "expected_currency": self.expected_currency,
            "valid_for_public_fetcher": self.valid_for_public_fetcher,
            "status": self.status,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicPublicDataFetcherAdapterResult:
    status: str
    import_plan_status: str
    adapted_source_count: int
    blocked_source_count: int
    rows: tuple[DynamicPublicDataFetcherAdapterRow, ...]
    public_fetcher_config: dict[str, Any]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    authorization_required: bool
    authorization_phrase: str
    dry_run_default: bool
    network_forbidden_by_adapter: bool
    write_forbidden_by_adapter: bool
    local_cache_only: bool
    raw_data_unverified: bool
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "import_plan_status": self.import_plan_status,
            "adapted_source_count": self.adapted_source_count,
            "blocked_source_count": self.blocked_source_count,
            "rows": [row.to_dict() for row in self.rows],
            "public_fetcher_config": self.public_fetcher_config,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "authorization_required": self.authorization_required,
            "authorization_phrase": self.authorization_phrase,
            "dry_run_default": self.dry_run_default,
            "network_forbidden_by_adapter": self.network_forbidden_by_adapter,
            "write_forbidden_by_adapter": self.write_forbidden_by_adapter,
            "local_cache_only": self.local_cache_only,
            "raw_data_unverified": self.raw_data_unverified,
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("dynamic public data fetcher endpoint config must be a JSON object.")
    return raw


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _safe_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return safe or "dynamic_public_source"


def _endpoints_by_asset_id(endpoint_path: str | Path) -> dict[str, dict[str, Any]]:
    raw = _load_json(endpoint_path)
    endpoints = raw.get("endpoints", [])
    if not isinstance(endpoints, list):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        asset_id = _text(endpoint.get("asset_id"))
        if asset_id:
            result[asset_id] = endpoint
    return result


def _safe_fetcher_config(source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "title": "JARVIS Dynamic Public Market Data Fetcher Config",
        "version": "dynamic_adapter_v1",
        "fetcher_mode": "dry_run_default",
        "dry_run_only": True,
        "execute_fetch": False,
        "write_local_cache": False,
        "authorization_phrase": "",
        "authorization_phrase_required": AUTHORIZATION_PHRASE,
        "update_frequency": "daily",
        "output_directory": "jarvis/local/public_data/dynamic_market",
        "safety_controls": {
            "registry_mutation": False,
            "registry_file_written": False,
            "candidate_registry_write": False,
            "candidate_intake_file_written": False,
            "persisted_candidate_packet": False,
            "executor_created": False,
            "approved_asset": False,
            "trusted_asset": False,
            "investable": False,
            "evidence_verification_started": False,
            "promoted_verified_evidence": False,
            "allocation_recommendation": False,
            "portfolio_construction": False,
            "portfolio_weight": False,
            "buy_signal": False,
            "sell_signal": False,
            "trade_executed": False,
            "broker_api_used": False,
            "authenticated_api_used": False,
            "credentials_used": False,
            "private_file_ingested": False,
            "private_account_data_ingested": False,
            "automatic_evidence_extraction": False,
        },
        "sources": source_rows,
    }


def build_dynamic_public_data_fetcher_adapter(
    registry_path: str | Path,
    binding_path: str | Path,
    endpoint_path: str | Path,
) -> DynamicPublicDataFetcherAdapterResult:
    import_plan = build_dynamic_market_import_plan(registry_path, binding_path)
    endpoints = _endpoints_by_asset_id(endpoint_path)

    warnings: list[str] = list(import_plan.warnings)
    blockers: list[str] = list(import_plan.blockers)
    rows: list[DynamicPublicDataFetcherAdapterRow] = []
    source_rows: list[dict[str, Any]] = []

    for import_row in import_plan.rows:
        endpoint = endpoints.get(import_row.asset_id, {})

        source_id = f"dynamic_market_{_safe_id(import_row.asset_id)}"
        source_type = _text(endpoint.get("source_type"))
        source_url = _text(endpoint.get("source_url"))
        update_frequency = _text(endpoint.get("update_frequency")) or "daily"

        source_row = {
            "source_id": source_id,
            "candidate_id": import_row.asset_id,
            "display_name": import_row.asset_id,
            "source_type": source_type,
            "source_url": source_url,
            "update_frequency": update_frequency,
            "public_source_only": endpoint.get("public_source_only") is True,
            "requires_authentication": endpoint.get("requires_authentication") is True,
            "requires_credentials": endpoint.get("requires_credentials") is True,
            "broker_or_trading_api": endpoint.get("broker_or_trading_api") is True,
            "contains_private_data": endpoint.get("contains_private_data") is True,
            "dynamic_cache_series_id": import_row.cache_series_id,
            "expected_currency": import_row.expected_currency,
        }

        validation = validate_source(source_row)
        row_blockers = list(import_row.blockers) + list(validation.blocked_reasons)
        row_warnings = list(import_row.warnings) + list(validation.warnings)

        if import_plan.status != IMPORT_PLAN_READY:
            row_blockers.append(f"{import_row.asset_id}: import plan is not ready.")
        if import_row.asset_id not in endpoints:
            row_blockers.append(f"{import_row.asset_id}: endpoint mapping is missing.")

        valid = not row_blockers
        status = "PUBLIC_FETCHER_SOURCE_READY" if valid else "PUBLIC_FETCHER_SOURCE_BLOCKED"

        if valid:
            source_rows.append(source_row)

        rows.append(
            DynamicPublicDataFetcherAdapterRow(
                asset_id=import_row.asset_id,
                source_id=source_id,
                source_type=source_type,
                source_url=source_url,
                update_frequency=update_frequency,
                cache_series_id=import_row.cache_series_id,
                expected_currency=import_row.expected_currency,
                valid_for_public_fetcher=valid,
                status=status,
                warnings=tuple(dict.fromkeys(row_warnings)),
                blockers=tuple(dict.fromkeys(row_blockers)),
            )
        )

    public_fetcher_config = _safe_fetcher_config(source_rows)
    config_blockers = list(validate_fetcher_config(public_fetcher_config))

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    blockers.extend(config_blockers)

    adapted_count = sum(1 for row in rows if row.status == "PUBLIC_FETCHER_SOURCE_READY")
    blocked_count = sum(1 for row in rows if row.status == "PUBLIC_FETCHER_SOURCE_BLOCKED")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicPublicDataFetcherAdapterResult(
        status=status,
        import_plan_status=import_plan.status,
        adapted_source_count=adapted_count,
        blocked_source_count=blocked_count,
        rows=tuple(rows),
        public_fetcher_config=public_fetcher_config,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        authorization_required=True,
        authorization_phrase=AUTHORIZATION_PHRASE,
        dry_run_default=True,
        network_forbidden_by_adapter=True,
        write_forbidden_by_adapter=True,
        local_cache_only=True,
        raw_data_unverified=True,
        manual_approval_required=True,
        execution_forbidden=True,
    )
