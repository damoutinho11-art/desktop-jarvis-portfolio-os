"""J.A.R.V.I.S. v24.0 crypto-lane selection daily operator bridge.

v24 replaces the BTC-only v21 daily evidence view with the v23 crypto-lane
selection gate. The active root daily command can now show the selected crypto
candidate from the BTC/HYPE/TAO public-signal universe, while still preserving
stale-data review warnings and the no-execution boundary.
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
from .jarvis_v23_0_crypto_lane_public_signal_selection_gate import (
    CryptoLanePublicSignalSelectionGateResult,
    build_crypto_lane_public_signal_selection_gate_result,
    format_crypto_lane_public_signal_selection_gate,
)

STATUS_READY = "JARVIS_V24_0_CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V24_0_CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V24_0_CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "CRYPTO_LANE_SELECTION_DAILY_OPERATOR_BRIDGE_BLOCKED"

NEXT_STAGE = "crypto_lane_scoring_and_approval_ticket_integration"


@dataclass(frozen=True)
class CryptoLaneSelectionDailyOperatorBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    daily_readiness_result: Any
    crypto_selection_result: CryptoLanePublicSignalSelectionGateResult
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    crypto_selection_ready: bool
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
        daily = self.daily_readiness_result
        return {
            "status": self.status,
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "daily_readiness_result": daily.to_dict() if hasattr(daily, "to_dict") else dict(getattr(daily, "__dict__", {})),
            "crypto_selection_result": self.crypto_selection_result.to_dict(),
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "crypto_selection_ready": self.crypto_selection_ready,
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


def _daily_status_requires_review(daily_readiness_result: Any) -> bool:
    daily_status = str(getattr(daily_readiness_result, "status", ""))
    return "REVIEW_REQUIRED" in daily_status or bool(getattr(daily_readiness_result, "stale_data_review_required", False))


def build_crypto_lane_selection_daily_operator_bridge(
    *,
    current_date: str | None = None,
    daily_readiness_result: RealDailyReadinessGateResult | None = None,
    crypto_selection_result: CryptoLanePublicSignalSelectionGateResult | None = None,
    daily_readiness_builder: Callable[..., RealDailyReadinessGateResult] = build_real_daily_readiness_gate,
    crypto_selection_builder: Callable[..., CryptoLanePublicSignalSelectionGateResult] = build_crypto_lane_public_signal_selection_gate_result,
) -> CryptoLaneSelectionDailyOperatorBridgeResult:
    parsed_current_date = _parse_date(current_date)
    blockers: list[str] = []
    warnings: list[str] = []

    if current_date is not None and parsed_current_date is None:
        blockers.append("current_date must use YYYY-MM-DD format when provided.")

    readiness = daily_readiness_result
    if readiness is None:
        readiness = daily_readiness_builder(current_date=parsed_current_date)

    selection = crypto_selection_result
    if selection is None:
        selection = crypto_selection_builder(current_date=current_date)

    blockers.extend(getattr(readiness, "blockers", ()) or ())
    warnings.extend(getattr(readiness, "warnings", ()) or ())
    blockers.extend(getattr(selection, "blockers", ()) or ())
    warnings.extend(getattr(selection, "warnings", ()) or ())

    crypto_selection_ready = bool(getattr(selection, "selected_crypto_candidate", None))
    if not crypto_selection_ready:
        warnings.append("No crypto candidate was selected by the public-signal selection gate.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif _daily_status_requires_review(readiness):
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return CryptoLaneSelectionDailyOperatorBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        daily_readiness_result=readiness,
        crypto_selection_result=selection,
        selected_crypto_candidate=getattr(selection, "selected_crypto_candidate", None),
        selected_crypto_amount_eur=float(getattr(selection, "selected_crypto_amount_eur", 0.0) or 0.0),
        crypto_selection_ready=crypto_selection_ready,
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


def _daily_readiness_console_output(daily_readiness_result: Any) -> str:
    if hasattr(daily_readiness_result, "allocation_result"):
        return build_real_daily_readiness_console_output(daily_readiness_result)
    blockers = getattr(daily_readiness_result, "blockers", ()) or ()
    warnings = getattr(daily_readiness_result, "warnings", ()) or ()
    return "\n".join(
        [
            "J.A.R.V.I.S. Real Allocation Daily Operator",
            f"status: {getattr(daily_readiness_result, 'status', 'unknown')}",
            f"data readiness: {getattr(daily_readiness_result, 'readiness_status', 'unknown')}",
            f"blockers: {', '.join(str(item) for item in blockers) if blockers else 'none'}",
            f"warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}",
        ]
    )


def build_crypto_lane_selection_daily_operator_console_output(
    result: CryptoLaneSelectionDailyOperatorBridgeResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Operator with Crypto-Lane Selection",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"crypto selection ready: {result.crypto_selection_ready}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        "Crypto-lane selection:",
        format_crypto_lane_public_signal_selection_gate(result.crypto_selection_result),
        "",
        "Daily allocation/readiness:",
        _daily_readiness_console_output(result.daily_readiness_result),
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
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. daily operator with crypto-lane selection.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily readiness with crypto-lane public-signal selection.")
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

    result = build_crypto_lane_selection_daily_operator_bridge(current_date=args.current_date)
    print(build_crypto_lane_selection_daily_operator_console_output(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())