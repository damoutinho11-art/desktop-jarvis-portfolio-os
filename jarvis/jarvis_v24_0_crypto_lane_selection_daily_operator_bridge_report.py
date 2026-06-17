"""Report CLI for J.A.R.V.I.S. v24.0 crypto-lane selection daily operator bridge."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v24_0_crypto_lane_selection_daily_operator_bridge import (
    build_crypto_lane_selection_daily_operator_bridge,
    build_crypto_lane_selection_daily_operator_console_output,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report daily operator crypto-lane selection bridge status.")
    parser.add_argument("--current-date", default=None)
    args = parser.parse_args(argv)

    result = build_crypto_lane_selection_daily_operator_bridge(current_date=args.current_date)

    print("# J.A.R.V.I.S. v24.0 Crypto-Lane Selection Daily Operator Bridge")
    print()
    print(f"status: {result.status}")
    print(f"bridge status: {result.bridge_status}")
    print(f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}")
    print(f"selected crypto amount eur: {result.selected_crypto_amount_eur:,.2f}")
    print(f"crypto selection ready: {result.crypto_selection_ready}")
    print(f"recommendation quality current data: {result.recommendation_quality_current_data}")
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
    print(build_crypto_lane_selection_daily_operator_console_output(result))
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