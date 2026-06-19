from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.assistant_market_data_bridge import build_assistant_market_data_bridge_result
from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
from jarvis.runtime.local_server_live_endpoint_smoke import build_local_server_live_endpoint_smoke_result
from jarvis.runtime.public_data_provider_registry import build_public_data_provider_registry_result
from jarvis.runtime.safety import build_safety_check_console_output


STATUS_READY = "JARVIS_V118_0_CURRENT_RUNTIME_FAST_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V118_0_CURRENT_RUNTIME_FAST_GATE_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/current_runtime_fast_gate_latest.json"


@dataclass(frozen=True)
class CurrentRuntimeFastGateResult:
    status: str
    current_date: str
    fast_gate_ready: bool
    elapsed_seconds: float
    checks: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_executed: bool
    auto_approval_enabled: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_current_runtime_fast_gate_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> CurrentRuntimeFastGateResult:
    started = time.perf_counter()
    blockers: list[str] = []
    warnings = [
        "fast gate intentionally avoids full historical unittest discovery",
        "fast gate is read-only and does not create broker/order/trade capabilities",
    ]

    safety_output = build_safety_check_console_output()
    safety_ready = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    finance = build_finance_intelligence_core_result(current_date=current_date)
    provider = build_public_data_provider_registry_result(current_date=current_date)
    bridge = build_assistant_market_data_bridge_result(current_date=current_date)
    live_smoke = build_local_server_live_endpoint_smoke_result(current_date=current_date)

    checks = {
        "safety_check_blocks": safety_ready,
        "finance_intelligence_ready": finance.finance_intelligence_ready,
        "normalized_records": len(finance.normalized_records),
        "provider_registry_status": provider.status,
        "assistant_market_data_bridge_status": bridge.status,
        "local_server_live_smoke_ready": live_smoke.live_endpoint_smoke_ready,
        "forbidden_capabilities": {
            "broker_connection": bool(finance.broker_connection or provider.broker_connection or bridge.broker_connection or live_smoke.broker_connection),
            "credentials_used": bool(finance.credentials_used or provider.credentials_used or bridge.credentials_used or live_smoke.credentials_used),
            "order_created": bool(finance.order_created or provider.order_created or bridge.order_created or live_smoke.order_created),
            "trade_executed": bool(finance.trade_executed or provider.trade_executed or bridge.trade_executed or live_smoke.trade_executed),
            "buy_sell_request_created": bool(finance.buy_sell_request_created),
            "auto_approval_enabled": bool(finance.auto_approval_enabled),
        },
    }
    if not finance.finance_intelligence_ready:
        blockers.append("finance_intelligence_core_not_ready")
    if len(finance.normalized_records) < 3:
        blockers.append("normalized_market_data_record_count_too_low")
    if not live_smoke.live_endpoint_smoke_ready:
        blockers.append("local_server_live_endpoint_smoke_not_ready")
    for key, value in checks["forbidden_capabilities"].items():
        if value:
            blockers.append(f"forbidden_capability_enabled:{key}")

    elapsed = round(time.perf_counter() - started, 3)
    if elapsed > 60:
        warnings.append(f"fast gate elapsed_seconds={elapsed}; investigate product stack speed before v1.0")

    blockers = list(dict.fromkeys(blockers))
    result = CurrentRuntimeFastGateResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        fast_gate_ready=not blockers,
        elapsed_seconds=elapsed,
        checks=checks,
        warnings=warnings,
        blockers=blockers,
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        buy_sell_request_created=False,
        order_created=False,
        trade_executed=False,
        auto_approval_enabled=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_current_runtime_fast_gate(result: CurrentRuntimeFastGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. CURRENT RUNTIME FAST GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"fast gate ready: {result.fast_gate_ready}",
        f"elapsed seconds: {result.elapsed_seconds}",
        "",
        "CHECKS:",
    ]
    for key, value in result.checks.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "SAFETY:",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- buy/sell request created: {result.buy_sell_request_created}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            f"- auto approval enabled: {result.auto_approval_enabled}",
            "",
            "WARNINGS:",
            *[f"- {warning}" for warning in result.warnings],
            "",
            "BLOCKERS:",
            *[f"- {blocker}" for blocker in result.blockers or ["none"]],
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded current-runtime fast gate.")
    parser.add_argument("--current-runtime-fast-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_current_runtime_fast_gate_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_current_runtime_fast_gate(result))
    return 0 if result.fast_gate_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "CurrentRuntimeFastGateResult",
    "build_current_runtime_fast_gate_result",
    "format_current_runtime_fast_gate",
    "main",
]
