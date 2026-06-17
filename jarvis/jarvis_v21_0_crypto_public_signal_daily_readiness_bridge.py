"""J.A.R.V.I.S. v21.0 crypto public signal daily readiness bridge.

This module promotes the quality-gated BTC public signal from an isolated v20
check into the active daily operator view. It is product integration, not a new
research-only display: the daily command can now show whether the crypto lane
has a current quality-gated public signal before Diogo performs any manual
real-world buy outside J.A.R.V.I.S.

Safety boundary remains unchanged:
- no allocation score mutation;
- no approval ticket mutation;
- no buy request;
- no broker connection;
- no credentials;
- no private brokerage/account data ingestion;
- no order placement;
- no trade execution.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import (
    RealDailyReadinessGateResult,
    build_real_daily_readiness_console_output,
    build_real_daily_readiness_gate,
    build_safety_check_console_output,
)
from .jarvis_v20_0_btc_public_signal_source_quality_gate import (
    BtcPublicSignalQualityResult,
    build_btc_public_signal_source_quality_gate_result,
)

STATUS_READY = "JARVIS_V21_0_CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V21_0_CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V21_0_CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_BLOCKED_SAFE"
BRIDGE_READY = "CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "CRYPTO_PUBLIC_SIGNAL_DAILY_READINESS_BRIDGE_BLOCKED"
NEXT_STAGE = "multi_asset_public_signal_expansion"


@dataclass(frozen=True)
class CryptoPublicSignalDailyReadinessBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    daily_readiness_result: RealDailyReadinessGateResult
    btc_public_signal_result: BtcPublicSignalQualityResult
    crypto_public_signal_ready: bool
    crypto_public_signal_used_for_evidence: bool
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "daily_readiness_result": self.daily_readiness_result.to_dict(),
            "btc_public_signal_result": self.btc_public_signal_result.to_dict(),
            "crypto_public_signal_ready": self.crypto_public_signal_ready,
            "crypto_public_signal_used_for_evidence": self.crypto_public_signal_used_for_evidence,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _format_eur(value: float | None) -> str:
    if value is None:
        return "none"
    return f"EUR {value:,.2f}"


def _format_pct(value: float | None) -> str:
    if value is None:
        return "none"
    return f"{value:.4f}%"


def build_crypto_public_signal_daily_readiness_bridge(
    *,
    current_date: str | None = None,
    daily_readiness_result: RealDailyReadinessGateResult | None = None,
    btc_public_signal_result: BtcPublicSignalQualityResult | None = None,
    daily_readiness_builder: Callable[..., RealDailyReadinessGateResult] = build_real_daily_readiness_gate,
    btc_public_signal_builder: Callable[..., BtcPublicSignalQualityResult] = build_btc_public_signal_source_quality_gate_result,
) -> CryptoPublicSignalDailyReadinessBridgeResult:
    parsed_current_date = _parse_date(current_date)
    blockers: list[str] = []
    warnings: list[str] = []

    if current_date is not None and parsed_current_date is None:
        blockers.append("current_date must use YYYY-MM-DD format when provided.")

    readiness = daily_readiness_result
    if readiness is None:
        readiness = daily_readiness_builder(current_date=parsed_current_date)

    btc_signal = btc_public_signal_result
    if btc_signal is None:
        btc_signal = btc_public_signal_builder(current_date=current_date)

    blockers.extend(getattr(readiness, "blockers", ()) or ())
    warnings.extend(getattr(readiness, "warnings", ()) or ())

    crypto_public_signal_ready = bool(getattr(btc_signal, "source_quality_ready", False))
    if not crypto_public_signal_ready:
        warnings.append("BTC public signal is not source-quality ready; crypto lane public evidence is not current.")
        blockers.extend(getattr(btc_signal, "blockers", ()) or ())
    warnings.extend(getattr(btc_signal, "warnings", ()) or ())

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    daily_status = str(getattr(readiness, "status", ""))
    daily_review_required = "REVIEW_REQUIRED" in daily_status or bool(getattr(readiness, "stale_data_review_required", False))

    if unique_blockers:
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif daily_review_required:
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return CryptoPublicSignalDailyReadinessBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        daily_readiness_result=readiness,
        btc_public_signal_result=btc_signal,
        crypto_public_signal_ready=crypto_public_signal_ready,
        crypto_public_signal_used_for_evidence=crypto_public_signal_ready,
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def _crypto_signal_lines(signal: BtcPublicSignalQualityResult) -> list[str]:
    return [
        "",
        "Crypto public signal:",
        f"- BTC signal: {signal.quality_status}; ready {signal.source_quality_ready}; age {signal.signal_age_days if signal.signal_age_days is not None else 'unknown'} days",
        f"- price: {_format_eur(signal.price_eur)}; 24h change: {_format_pct(signal.change_24h_pct)}",
        f"- source: {signal.source_id or 'none'}; as_of: {signal.as_of or 'none'}; provider updated: {signal.provider_last_updated_utc or 'none'}",
        "- use: crypto-lane evidence only; allocation/scoring/ticket unchanged until a later integration gate",
    ]


def build_crypto_public_signal_daily_readiness_console_output(
    result: CryptoPublicSignalDailyReadinessBridgeResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Operator with Crypto Public Signal",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"crypto public signal ready: {result.crypto_public_signal_ready}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        *_crypto_signal_lines(result.btc_public_signal_result),
        "",
        "Daily allocation/readiness:",
        build_real_daily_readiness_console_output(result.daily_readiness_result),
    ]
    if result.blockers:
        lines.extend(["", "Bridge blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("bridge blockers: none")
    if result.warnings:
        lines.extend(["", "Bridge warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("bridge warnings: none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. daily operator with crypto public signal readiness.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily readiness with crypto public signal evidence.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0
    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0
    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    result = build_crypto_public_signal_daily_readiness_bridge(current_date=args.current_date)
    print(build_crypto_public_signal_daily_readiness_console_output(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())