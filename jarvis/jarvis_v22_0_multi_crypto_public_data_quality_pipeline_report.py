"""Report CLI for J.A.R.V.I.S. v22.0 multi-crypto public data quality pipeline."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    build_multi_crypto_public_data_quality_pipeline_result,
    format_multi_crypto_public_data_quality_pipeline,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report multi-crypto public data quality pipeline status.")
    parser.add_argument("--raw-directory", default="jarvis/local/public_data/v10_raw")
    parser.add_argument("--normalized-directory", default="jarvis/local/public_data/v22_multi_crypto_normalized")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--max-signal-age-days", type=int, default=1)
    parser.add_argument("--write-local-signals", action="store_true")
    args = parser.parse_args(argv)

    result = build_multi_crypto_public_data_quality_pipeline_result(
        raw_directory=args.raw_directory,
        normalized_directory=args.normalized_directory,
        current_date=args.current_date,
        max_signal_age_days=args.max_signal_age_days,
        write_local_signals=args.write_local_signals,
    )

    print("# J.A.R.V.I.S. v22.0 Multi-Crypto Public Data Quality Pipeline")
    print()
    print(f"status: {result.status}")
    print(f"pipeline status: {result.pipeline_status}")
    print(f"current date: {result.current_date}")
    print(f"candidate count: {result.candidate_count}")
    print(f"source quality ready count: {result.source_quality_ready_count}")
    print(f"blocked candidate count: {result.blocked_candidate_count}")
    print(f"all crypto public signals ready: {result.all_crypto_public_signals_ready}")
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
    print("## Candidate Signals")
    print()
    for item in result.candidate_results:
        signal = item.signal
        print(f"- {item.candidate_id}: {item.quality_status}; ready {item.source_quality_ready}")
        if signal:
            print(f"  - price_eur: {signal.price_eur:,.2f}")
            print(f"  - change_24h_pct: {signal.change_24h_pct:.4f}")
            print(f"  - source: {signal.source_id}")
            print(f"  - as_of: {signal.as_of}")
            print(f"  - signal_age_days: {signal.signal_age_days}")
            print(f"  - normalized_signal_file: {item.normalized_signal_file or 'none'}")
        if item.blockers:
            print(f"  - blockers: {', '.join(item.blockers)}")
    print()
    print("## Console Output")
    print()
    print("```text")
    print(format_multi_crypto_public_data_quality_pipeline(result))
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