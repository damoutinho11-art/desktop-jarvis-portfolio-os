"""Report CLI for J.A.R.V.I.S. dynamic raw market cache normalizer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_raw_cache_normalizer import (
    DynamicMarketRawCacheNormalizerResult,
    normalize_dynamic_market_raw_cache,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_ENDPOINT_PATH = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def build_dynamic_market_raw_cache_normalizer_report(result: DynamicMarketRawCacheNormalizerResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Raw Cache Normalizer",
        "Converts local raw public-cache files into normalized market data. No fetching performed.",
        f"status: {result.status}",
        f"adapter status: {result.adapter_status}",
        f"raw file count: {result.raw_file_count}",
        f"expected source count: {result.expected_source_count}",
        f"normalized series count: {result.normalized_series_count}",
        f"ready row count: {result.ready_row_count}",
        f"blocked row count: {result.blocked_row_count}",
        f"as_of: {result.as_of}",
        f"fetching forbidden: {result.fetching_forbidden}",
        f"local raw cache only: {result.local_raw_cache_only}",
        f"raw data unverified: {result.raw_data_unverified}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "normalizer rows:",
    ]

    for row in result.rows:
        lines.append(
            f"- {row.asset_id}: {row.status}; source_id={row.source_id}; "
            f"series={row.cache_series_id}; currency={row.expected_currency}; "
            f"prices={row.parsed_price_count}; raw_path={row.raw_path}"
        )
        for warning in row.warnings:
            lines.append(f"  warning: {warning}")
        for blocker in row.blockers:
            lines.append(f"  blocker: {blocker}")

    if not result.rows:
        lines.append("- none")

    lines.append("")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.append("")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            "- no public fetch performed by normalizer",
            "- raw cache data remains unverified",
            "- normalized market data is not approval",
            "- no broker integration",
            "- no buy request created",
            "- no approval granted",
            "- no execution",
            "- no trades executed",
        ]
    )
    return "\n".join(lines)


def report_dynamic_market_raw_cache_normalizer(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    endpoint_path: str | Path = DEFAULT_ENDPOINT_PATH,
    raw_cache_paths: tuple[str | Path, ...] = (),
    as_of: str | None = None,
) -> str:
    return build_dynamic_market_raw_cache_normalizer_report(
        normalize_dynamic_market_raw_cache(
            registry_path,
            binding_path,
            endpoint_path,
            raw_cache_paths,
            as_of=as_of,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize dynamic public raw cache files into market data shape.")
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("endpoint_path", nargs="?", default=DEFAULT_ENDPOINT_PATH)
    parser.add_argument("--as-of", default=None)
    parser.add_argument("raw_cache_paths", nargs="*")
    args = parser.parse_args()

    print(
        report_dynamic_market_raw_cache_normalizer(
            args.registry_path,
            args.binding_path,
            args.endpoint_path,
            tuple(args.raw_cache_paths),
            as_of=args.as_of,
        )
    )


if __name__ == "__main__":
    main()
