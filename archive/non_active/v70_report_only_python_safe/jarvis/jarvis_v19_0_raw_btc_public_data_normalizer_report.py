"""Report smoke for J.A.R.V.I.S. v19.0 raw BTC public data normalizer."""
from __future__ import annotations

import argparse
import json

from .jarvis_v19_0_raw_btc_public_data_normalizer import (
    STATUS_READY,
    build_raw_btc_public_data_normalizer_result,
    format_raw_btc_public_data_normalizer,
)


def report_v19_0_raw_btc_public_data_normalizer(*, write_local_signal: bool = False, root: str = ".") -> str:
    result = build_raw_btc_public_data_normalizer_result(write_local_signal=write_local_signal, root=root)
    lines = [
        "# J.A.R.V.I.S. v19.0 Raw BTC Public Data Normalizer",
        "",
        f"status: {result.status}",
        f"normalizer status: {result.normalizer_status}",
        f"raw file found: {result.raw_file_found}",
        f"selected raw file: {result.selected_raw_file or 'none'}",
        f"signal ready: {result.signal_ready}",
        f"signal written: {result.signal_written}",
        f"normalized signal file: {result.normalized_signal_file or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"buy request created: {result.buy_request_created}",
        f"broker connection forbidden: {result.broker_connection_forbidden}",
        f"credentials forbidden: {result.credentials_forbidden}",
        f"private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}",
        f"order creation forbidden: {result.order_creation_forbidden}",
        f"no trades executed: {result.no_trades_executed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}",
        "",
        "## Normalizer Console Output",
        "",
        "```text",
        format_raw_btc_public_data_normalizer(result),
        "```",
    ]
    if result.btc_signal:
        lines.extend(
            [
                "",
                "## Normalized BTC Signal JSON",
                "",
                "```json",
                json.dumps(result.btc_signal.to_dict(), indent=2, sort_keys=True),
                "```",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report v19 raw BTC public data normalization readiness.")
    parser.add_argument("--write-local-signal", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    report = report_v19_0_raw_btc_public_data_normalizer(write_local_signal=args.write_local_signal, root=args.root)
    print(report)
    return 0 if f"status: {STATUS_READY}" in report else 1


if __name__ == "__main__":
    raise SystemExit(main())
