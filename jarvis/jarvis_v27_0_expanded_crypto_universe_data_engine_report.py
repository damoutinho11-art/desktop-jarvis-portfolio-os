"""Report CLI for J.A.R.V.I.S. v27.0 expanded crypto universe data engine."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v27_0_expanded_crypto_universe_data_engine import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_MISSING_MANIFEST_PATH,
    DEFAULT_NORMALIZED_DIRECTORY,
    DEFAULT_PORTFOLIO_STATE_PATH,
    DEFAULT_RAW_DIRECTORY,
    build_expanded_crypto_universe_data_engine_result,
    format_expanded_crypto_universe_data_engine,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report expanded crypto universe data-engine status.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manifest-path", default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--missing-manifest-path", default=DEFAULT_MISSING_MANIFEST_PATH)
    parser.add_argument("--portfolio-state-path", default=DEFAULT_PORTFOLIO_STATE_PATH)
    parser.add_argument("--raw-directory", default=DEFAULT_RAW_DIRECTORY)
    parser.add_argument("--normalized-directory", default=DEFAULT_NORMALIZED_DIRECTORY)
    parser.add_argument("--max-signal-age-days", type=int, default=1)
    parser.add_argument("--write-local-manifest", action="store_true")
    parser.add_argument("--write-missing-manifest", action="store_true")
    parser.add_argument("--write-local-signals", action="store_true")
    args = parser.parse_args(argv)

    result = build_expanded_crypto_universe_data_engine_result(
        current_date=args.current_date,
        manifest_path=args.manifest_path,
        missing_manifest_path=args.missing_manifest_path,
        portfolio_state_path=args.portfolio_state_path,
        raw_directory=args.raw_directory,
        normalized_directory=args.normalized_directory,
        max_signal_age_days=args.max_signal_age_days,
        write_local_manifest=args.write_local_manifest,
        write_missing_manifest=args.write_missing_manifest,
        write_local_signals=args.write_local_signals,
    )

    print("# J.A.R.V.I.S. v27.0 Expanded Crypto Universe Data Engine")
    print()
    print(f"status: {result.status}")
    print(f"engine status: {result.engine_status}")
    print(f"current date: {result.current_date}")
    print(f"universe candidate count: {result.universe_candidate_count}")
    print(f"manifest path: {result.manifest_path}")
    print(f"manifest written: {result.manifest_written}")
    print(f"public data pipeline status: {result.public_data_pipeline_status}")
    print(f"source quality ready count: {result.source_quality_ready_count}")
    print(f"source quality blocked count: {result.source_quality_blocked_count}")
    print(f"full public data coverage: {result.full_public_data_coverage}")
    print(f"platform ready count: {result.platform_ready_count}")
    print(f"ranked candidate count: {result.ranked_candidate_count}")
    print(f"top candidate: {result.top_candidate_id or 'none'}")
    print(f"top candidate score: {result.top_candidate_score:,.2f}")
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
    print(format_expanded_crypto_universe_data_engine(result))
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