"""Report CLI for J.A.R.V.I.S. v25.0 daily approval ticket refresh builder."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v25_0_daily_approval_ticket_refresh_builder import (
    DEFAULT_OUTPUT_PATH,
    build_daily_approval_ticket_refresh_builder_result,
    format_daily_approval_ticket_refresh_builder,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report approval ticket refresh builder status.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--write-ticket", action="store_true")
    args = parser.parse_args(argv)

    result = build_daily_approval_ticket_refresh_builder_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_ticket=args.write_ticket,
    )

    print("# J.A.R.V.I.S. v25.0 Daily Approval Ticket Refresh Builder")
    print()
    print(f"status: {result.status}")
    print(f"builder status: {result.builder_status}")
    print(f"current date: {result.current_date}")
    print(f"output path: {result.output_path}")
    print(f"approval ticket written: {result.approval_ticket_written}")
    print(f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}")
    print(f"selected crypto amount eur: {result.selected_crypto_amount_eur:,.2f}")
    print(f"selected stock/fund/ETF candidate: {result.selected_stock_fund_etf_candidate or 'none'}")
    print(f"selected stock/fund/ETF amount eur: {result.selected_stock_fund_etf_amount_eur:,.2f}")
    print(f"recommendation quality current data: {result.recommendation_quality_current_data}")
    print(f"portfolio data stale review required: {result.portfolio_data_stale_review_required}")
    print(f"allocation mutation: {result.allocation_mutation}")
    print(f"approval ticket mutation: {result.approval_ticket_mutation}")
    print(f"buy request created: {result.buy_request_created}")
    print(f"broker connection forbidden: {result.broker_connection_forbidden}")
    print(f"credentials forbidden: {result.credentials_forbidden}")
    print(f"private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}")
    print(f"order creation forbidden: {result.order_creation_forbidden}")
    print(f"no trades executed: {result.no_trades_executed}")
    print(f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}")
    print(f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}")
    print()
    print("## Console Output")
    print()
    print("```text")
    print(format_daily_approval_ticket_refresh_builder(result))
    print("```")
    print()
    print("## Approval Ticket JSON")
    print()
    print("```json")
    print(json.dumps(result.approval_ticket, indent=2, sort_keys=True))
    print("```")
    print()
    print("## Result JSON")
    print()
    print("```json")
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    print("```")

    return 0 if not result.status.endswith("_BLOCKED_SAFE") else 1


if __name__ == "__main__":
    raise SystemExit(main())