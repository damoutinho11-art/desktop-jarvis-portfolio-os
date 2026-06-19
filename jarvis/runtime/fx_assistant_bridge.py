from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V118_0_FX_ASSISTANT_BRIDGE_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/fx_assistant_bridge_latest.json"
DEFAULT_FX_CACHE_PATH = Path("jarvis/local/free_research_api_cache.local.json")


@dataclass(frozen=True)
class FxAssistantBridgeResult:
    status: str
    current_date: str
    portfolio_base_currency: str
    preferred_provider: str
    cache_path: str
    provider_cache_seen: bool
    provider_id: str | None
    source_as_of: str | None
    usd_to_eur_rate: float | None
    eur_to_usd_rate: float | None
    conversion_available: bool
    freshness: str
    confidence: str
    missing_fields: list[str]
    warnings: list[str]
    blockers: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _find_fx_cache_record(path: Path) -> dict[str, Any] | None:
    data = _read_json(path)
    if not isinstance(data, dict):
        return None
    for record in data.get("records", []) or []:
        if not isinstance(record, dict):
            continue
        if str(record.get("lane") or "").lower() == "fx" or "fx" in str(record.get("provider_id") or "").lower():
            return record
    return None


def build_fx_assistant_bridge_result(
    *,
    current_date: str = "2026-06-18",
    cache_path: str | Path = DEFAULT_FX_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> FxAssistantBridgeResult:
    resolved_cache = Path(cache_path)
    record = _find_fx_cache_record(resolved_cache)
    provider_seen = bool(record)
    provider_id = str(record.get("provider_id")) if record else None
    source_as_of = None
    if record:
        source_as_of = str(record.get("current_date") or record.get("fetched_at") or "") or None

    missing = ["usd_to_eur_rate", "eur_to_usd_rate"]
    warnings = [
        "EUR is the portfolio base currency.",
        "USD quotes are shown in USD unless a trusted FX rate is available.",
        "ECB is the preferred future FX source for assistant-facing conversion.",
    ]
    if provider_seen:
        warnings.append("ECB FX cache metadata is present, but the parsed USD/EUR rate is not stored in the current cache contract.")
    else:
        warnings.append("No assistant-facing FX cache record is available.")
    warnings.append("No currency conversion is performed by this bridge until a trusted parsed FX rate exists.")

    result = FxAssistantBridgeResult(
        status=STATUS_READY,
        current_date=current_date,
        portfolio_base_currency="EUR",
        preferred_provider="ecb_fx_official",
        cache_path=str(resolved_cache),
        provider_cache_seen=provider_seen,
        provider_id=provider_id,
        source_as_of=source_as_of,
        usd_to_eur_rate=None,
        eur_to_usd_rate=None,
        conversion_available=False,
        freshness="metadata_only_no_parsed_rate" if provider_seen else "missing",
        confidence="low",
        missing_fields=missing,
        warnings=list(dict.fromkeys(warnings)),
        blockers=[],
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_fx_assistant_bridge(result: FxAssistantBridgeResult) -> str:
    return "\n".join(
        [
            "J.A.R.V.I.S. FX ASSISTANT BRIDGE",
            f"status: {result.status}",
            f"current date: {result.current_date}",
            f"base currency: {result.portfolio_base_currency}",
            f"preferred provider: {result.preferred_provider}",
            f"provider cache seen: {result.provider_cache_seen}",
            f"source_as_of: {result.source_as_of}",
            f"conversion available: {result.conversion_available}",
            f"freshness: {result.freshness}",
            f"confidence: {result.confidence}",
            "warnings:",
            *[f"- {warning}" for warning in result.warnings],
            "safety: no broker, credentials, orders, trades, buy/sell requests, or auto-approval.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run assistant-facing FX readiness bridge.")
    parser.add_argument("--fx-assistant-bridge", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--cache-path", default=str(DEFAULT_FX_CACHE_PATH))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_fx_assistant_bridge_result(
        current_date=args.current_date,
        cache_path=args.cache_path,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_fx_assistant_bridge(result))
    return 0


__all__ = [
    "STATUS_READY",
    "FxAssistantBridgeResult",
    "build_fx_assistant_bridge_result",
    "format_fx_assistant_bridge",
    "main",
]
