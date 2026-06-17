"""Report CLI for J.A.R.V.I.S. v23.0 crypto-lane public signal selection gate."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate import (
    build_crypto_lane_public_signal_selection_gate_result,
    format_crypto_lane_public_signal_selection_gate,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report crypto-lane public signal selection status.")
    parser.add_argument("--current-date", default=None)
    args = parser.parse_args(argv)

    result = build_crypto_lane_public_signal_selection_gate_result(current_date=args.current_date)

    print("# J.A.R.V.I.S. v23.0 Crypto-Lane Public Signal Selection Gate")
    print()
    print(f"status: {result.status}")
    print(f"gate status: {result.gate_status}")
    print(f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}")
    print(f"selected crypto amount eur: {result.selected_crypto_amount_eur:,.2f}")
    print(f"crypto public signal universe ready: {result.crypto_public_signal_universe_ready}")
    print(f"candidate count: {result.candidate_count}")
    print(f"eligible candidate count: {result.eligible_candidate_count}")
    print(f"blocked candidate count: {result.blocked_candidate_count}")
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
    print("## Candidate Decisions")
    print()
    for item in result.candidate_decisions:
        print(f"- {item.candidate_id}: {item.decision_status}; selected {item.selected}")
        print(f"  - source_quality_ready: {item.source_quality_ready}")
        print(f"  - route: {item.route or 'none'}")
        print(f"  - platform_ready: {item.platform_ready}")
        print(f"  - ideal_amount_eur: {item.ideal_amount_eur:,.2f}")
        print(f"  - executable_amount_eur: {item.executable_amount_eur:,.2f}")
        if item.price_eur is not None:
            print(f"  - price_eur: {item.price_eur:,.2f}")
            print(f"  - change_24h_pct: {item.change_24h_pct:.4f}")
        if item.blockers:
            print(f"  - blockers: {', '.join(item.blockers)}")
    print()
    print("## Console Output")
    print()
    print("```text")
    print(format_crypto_lane_public_signal_selection_gate(result))
    print("```")
    print()
    print("## Result JSON")
    print()
    print("```json")
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    print("```")

    return 0 if result.status.endswith("_READY_SAFE") else 1


if __name__ == "__main__":
    raise SystemExit(main())