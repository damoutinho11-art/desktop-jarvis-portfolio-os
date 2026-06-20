from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.final_product_acceptance_gate import (
    build_final_product_acceptance_gate_result,
    format_final_product_acceptance_gate,
)
from jarvis.runtime.manual_holdings_update import DEFAULT_MANUAL_HOLDINGS_PATH
from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.public_universe_quote_fetcher import main as _quote_fetcher_main
from jarvis.runtime.safety import build_safety_check_console_output


STATUS_READY = "JARVIS_V129_0_DAILY_OPERATOR_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V129_0_DAILY_OPERATOR_REVIEW_REQUIRED_SAFE"


@dataclass
class DailyOperatorResult:
    status: str
    current_date: str
    daily_operator_ready: bool
    quote_refresh_attempted: bool
    quote_refresh_exit_code: int | None
    dashboard_written: bool
    final_acceptance_ready: bool
    product_mode_ready: bool
    safety_ready: bool
    dashboard_path: str
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _clean_warnings(warnings: list[str]) -> list[str]:
    cleaned: list[str] = []
    for warning in warnings:
        text = str(warning or "").strip()
        if not text:
            continue
        if "unresolved local imports" in text:
            continue
        if text not in cleaned:
            cleaned.append(text)
    return cleaned


def _run_quote_refresh(current_date: str, max_targets: int) -> tuple[int, str]:
    argv = [
        "--current-date",
        current_date,
        "--write-cache",
        "--max-targets",
        str(max_targets),
    ]
    buffer = StringIO()
    with redirect_stdout(buffer):
        exit_code = _quote_fetcher_main(argv)
    return int(exit_code or 0), buffer.getvalue()


def _build_dashboard(
    current_date: str, write_dashboard: bool, manual_holdings_path: str | Path
) -> tuple[bool, str, dict[str, Any]]:
    try:
        dashboard = build_dashboard_contract_result(
            current_date=current_date, write_dashboard=write_dashboard, manual_holdings_path=manual_holdings_path
        )
    except TypeError:
        dashboard = build_dashboard_contract_result(current_date=current_date)
    data = _plain(dashboard)
    path = str(data.get("dashboard_path") or "outputs/dashboard_latest.html")
    written = bool(data.get("dashboard_html_written")) or bool(write_dashboard and Path(path).exists())
    return written, path, data


def build_daily_operator_result(
    *,
    current_date: str = "2026-06-20",
    refresh_quotes: bool = True,
    write_dashboard: bool = True,
    max_targets: int = 10,
    manual_holdings_path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
) -> DailyOperatorResult:
    blockers: list[str] = []
    warnings: list[str] = []

    quote_exit_code: int | None = None
    quote_output = ""
    if refresh_quotes:
        try:
            quote_exit_code, quote_output = _run_quote_refresh(current_date, max_targets)
            if quote_exit_code != 0:
                blockers.append(f"quote refresh failed with exit code {quote_exit_code}")
        except Exception as exc:  # defensive: daily operator must report, not hide
            quote_exit_code = 1
            blockers.append(f"quote refresh raised {type(exc).__name__}: {exc}")
    else:
        warnings.append("quote refresh skipped by operator flag")

    dashboard_written, dashboard_path, dashboard_data = _build_dashboard(current_date, write_dashboard, manual_holdings_path)
    if write_dashboard and not dashboard_written:
        blockers.append("dashboard was not written")

    final_gate = build_final_product_acceptance_gate_result(current_date=current_date)
    if not final_gate.final_acceptance_ready:
        blockers.extend(final_gate.blockers or ["final acceptance gate is not ready"])

    product = build_product_mode_result(mode="today", current_date=current_date)
    product_data = _plain(product)
    product_mode_ready = "READY_SAFE" in str(product_data.get("status") or "") and not list(product_data.get("blockers") or [])
    if not product_mode_ready:
        blockers.append("product mode today is not ready")

    safety_output = build_safety_check_console_output()
    safety_ready = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    if not safety_ready:
        blockers.append("safety check did not block execution")

    holdings = ((dashboard_data.get("sections") or {}).get("manual_holdings") or {})
    if not bool(holdings.get("holdings_ready")):
        warnings.append("manual holdings not ready; holdings are a review note, not a daily blocker")

    warnings.extend(_clean_warnings(list(product_data.get("warnings") or [])))
    warnings.extend(_clean_warnings(list(final_gate.warnings or [])))
    warnings.append("daily operator is read-only/manual-only and creates no broker/order/trade capability")
    if not bool(holdings.get("file_exists")):
        warnings.append("manual holdings file missing; Diogo has not entered actual buys yet")
    warnings = _clean_warnings(list(dict.fromkeys(warnings)))

    ready = not blockers

    return DailyOperatorResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        daily_operator_ready=ready,
        quote_refresh_attempted=refresh_quotes,
        quote_refresh_exit_code=quote_exit_code,
        dashboard_written=dashboard_written,
        final_acceptance_ready=bool(final_gate.final_acceptance_ready),
        product_mode_ready=product_mode_ready,
        safety_ready=safety_ready,
        dashboard_path=dashboard_path,
        blockers=blockers,
        warnings=warnings,
        proof={
            "quote_refresh_output_contains_records": "FETCHED RECORDS:" in quote_output if quote_output else False,
            "final_acceptance_status": final_gate.status,
            "product_status": product_data.get("status"),
            "dashboard_status": dashboard_data.get("status"),
            "dashboard_path": dashboard_path,
            "safety_blocked": safety_ready,
            "holdings_status": holdings.get("status"),
            "holdings_ready": holdings.get("holdings_ready"),
            "holdings_file_exists": holdings.get("file_exists"),
        },
    )


def format_daily_operator(result: DailyOperatorResult) -> str:
    lines = [
        "J.A.R.V.I.S. DAILY OPERATOR",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"daily operator ready: {result.daily_operator_ready}",
        "",
        "TODAY:",
        f"- final acceptance ready: {result.final_acceptance_ready}",
        f"- product mode ready: {result.product_mode_ready}",
        f"- dashboard written: {result.dashboard_written}",
        f"- dashboard path: {result.dashboard_path}",
        f"- quote refresh attempted: {result.quote_refresh_attempted}",
        f"- quote refresh exit code: {result.quote_refresh_exit_code}",
        f"- safety ready: {result.safety_ready}",
        f"- holdings ready: {result.proof.get('holdings_ready')}",
        f"- holdings file exists: {result.proof.get('holdings_file_exists')}",
        "",
        "PROOF:",
        f"- final acceptance status: {result.proof.get('final_acceptance_status')}",
        f"- product status: {result.proof.get('product_status')}",
        f"- dashboard status: {result.proof.get('dashboard_status')}",
        f"- safety blocked: {result.proof.get('safety_blocked')}",
        f"- holdings status: {result.proof.get('holdings_status')}",
        "",
        "WARNINGS:",
        *[f"- {warning}" for warning in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {blocker}" for blocker in result.blockers or ["none"]],
        "",
        "Open dashboard: start .\\outputs\\dashboard_latest.html",
        "Safety: read-only and manual-only. No broker, credential, order, trade, or auto-approval path is enabled.",
    ]
    return "\n".join(lines)


def _arg_value(args: list[str], flag: str, default: str) -> str:
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return default


def main(argv: list[str] | None = None) -> int:
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    current_date = _arg_value(args, "--current-date", "2026-06-20")
    max_targets = int(_arg_value(args, "--max-targets", "10"))
    refresh_quotes = "--skip-refresh" not in args
    write_dashboard = "--no-write-dashboard" not in args
    manual_holdings_path = _arg_value(args, "--holdings-path", DEFAULT_MANUAL_HOLDINGS_PATH)

    result = build_daily_operator_result(
        current_date=current_date,
        refresh_quotes=refresh_quotes,
        write_dashboard=write_dashboard,
        max_targets=max_targets,
        manual_holdings_path=manual_holdings_path,
    )
    print(format_daily_operator(result))
    return 0 if result.daily_operator_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
