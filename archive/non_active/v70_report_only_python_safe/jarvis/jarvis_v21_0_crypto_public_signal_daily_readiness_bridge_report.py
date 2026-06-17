"""Report CLI for J.A.R.V.I.S. v21.0 crypto public signal daily readiness bridge."""
from __future__ import annotations

import argparse
import json

from .jarvis_v21_0_crypto_public_signal_daily_readiness_bridge import (
    build_crypto_public_signal_daily_readiness_bridge,
    build_crypto_public_signal_daily_readiness_console_output,
)


def build_report_markdown(current_date: str | None = None) -> str:
    result = build_crypto_public_signal_daily_readiness_bridge(current_date=current_date)
    signal = result.btc_public_signal_result
    lines = [
        "# J.A.R.V.I.S. v21.0 Crypto Public Signal Daily Readiness Bridge",
        "",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"crypto public signal ready: {result.crypto_public_signal_ready}",
        f"crypto public signal used for evidence: {result.crypto_public_signal_used_for_evidence}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        f"broker connection forbidden: {result.broker_connection_forbidden}",
        f"credentials forbidden: {result.credentials_forbidden}",
        f"private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}",
        f"order creation forbidden: {result.order_creation_forbidden}",
        f"no trades executed: {result.no_trades_executed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}",
        "",
        "## BTC Public Signal Evidence",
        "",
        f"- quality status: {signal.quality_status}",
        f"- source quality ready: {signal.source_quality_ready}",
        f"- signal age days: {signal.signal_age_days if signal.signal_age_days is not None else 'unknown'}",
        f"- candidate: {signal.candidate_id or 'none'}",
        f"- source: {signal.source_id or 'none'}",
        f"- as_of: {signal.as_of or 'none'}",
        f"- price_eur: {signal.price_eur:,.2f}" if signal.price_eur is not None else "- price_eur: none",
        f"- change_24h_pct: {signal.change_24h_pct:.4f}" if signal.change_24h_pct is not None else "- change_24h_pct: none",
        "- use: evidence only; allocation/scoring/ticket unchanged",
        "",
        "## Console Output",
        "",
        "```text",
        build_crypto_public_signal_daily_readiness_console_output(result),
        "```",
        "",
        "## Result JSON",
        "",
        "```json",
        json.dumps(result.to_dict(), indent=2, sort_keys=True),
        "```",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the v21 crypto public signal daily readiness bridge report.")
    parser.add_argument("--current-date", default=None)
    args = parser.parse_args(argv)
    print(build_report_markdown(current_date=args.current_date))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())