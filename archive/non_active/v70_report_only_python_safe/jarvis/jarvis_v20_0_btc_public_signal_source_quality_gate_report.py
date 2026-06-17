"""Report smoke for J.A.R.V.I.S. v20.0 BTC public signal source-quality gate."""

from __future__ import annotations

import argparse
import json

from .jarvis_v20_0_btc_public_signal_source_quality_gate import (
    STATUS_READY,
    build_btc_public_signal_source_quality_gate_result,
    format_btc_public_signal_source_quality_gate,
)


def report_v20_0_btc_public_signal_source_quality_gate(
    *,
    root: str = ".",
    current_date: str | None = None,
    max_signal_age_days: int = 1,
) -> str:
    result = build_btc_public_signal_source_quality_gate_result(
        root=root,
        current_date=current_date,
        max_signal_age_days=max_signal_age_days,
    )
    lines = [
        "# J.A.R.V.I.S. v20.0 BTC Public Signal Source-Quality Gate",
        "",
        f"status: {result.status}",
        f"quality status: {result.quality_status}",
        f"source quality ready: {result.source_quality_ready}",
        f"signal file found: {result.signal_file_found}",
        f"selected signal file: {result.selected_signal_file or 'none'}",
        f"current date: {result.current_date}",
        f"max signal age days: {result.max_signal_age_days}",
        f"signal age days: {result.signal_age_days if result.signal_age_days is not None else 'unknown'}",
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
        "## Gate Console Output",
        "",
        "```text",
        format_btc_public_signal_source_quality_gate(result),
        "```",
    ]
    if result.source_quality_ready:
        lines.extend(
            [
                "",
                "## Quality-Gated BTC Public Signal",
                "",
                "```json",
                json.dumps(
                    {
                        "candidate_id": result.candidate_id,
                        "source_id": result.source_id,
                        "as_of": result.as_of,
                        "price_eur": result.price_eur,
                        "market_cap_eur": result.market_cap_eur,
                        "volume_24h_eur": result.volume_24h_eur,
                        "change_24h_pct": result.change_24h_pct,
                        "provider_last_updated_utc": result.provider_last_updated_utc,
                        "source_quality_ready": result.source_quality_ready,
                        "recommendation_quality_current_data": result.recommendation_quality_current_data,
                    },
                    indent=2,
                    sort_keys=True,
                ),
                "```",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report v20 BTC public signal source-quality gate readiness.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--max-signal-age-days", type=int, default=1)
    args = parser.parse_args(argv)
    report = report_v20_0_btc_public_signal_source_quality_gate(
        root=args.root,
        current_date=args.current_date,
        max_signal_age_days=args.max_signal_age_days,
    )
    print(report)
    return 0 if f"status: {STATUS_READY}" in report else 1


if __name__ == "__main__":
    raise SystemExit(main())