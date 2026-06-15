"""Report CLI for the CoinGecko market_chart raw fixture transformer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_coingecko_market_chart_transformer import (
    DynamicCoinGeckoMarketChartTransformerResult,
    transform_coingecko_market_chart_file,
)


def build_dynamic_coingecko_market_chart_transformer_report(
    result: DynamicCoinGeckoMarketChartTransformerResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. CoinGecko Market Chart Raw Fixture Transformer",
        "Local fixture transformer only. No fetch, API call, broker integration, endpoint promotion, or execution.",
        f"status: {result.status}",
        f"input path: {result.input_path}",
        f"output path: {result.output_path}",
        f"normalized price count: {result.normalized_price_count}",
        f"fetching forbidden: {result.fetching_forbidden}",
        f"local fixture only: {result.local_fixture_only}",
        f"raw data unverified: {result.raw_data_unverified}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "warnings:",
    ]

    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.append("")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            "- no fetch performed",
            "- no API calls performed",
            "- no credentials used",
            "- no broker integration",
            "- no endpoint promotion",
            "- no buy request created",
            "- no approval granted",
            "- no execution",
            "- no trades executed",
        ]
    )
    return "\n".join(lines)


def report_dynamic_coingecko_market_chart_transformer(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> str:
    return build_dynamic_coingecko_market_chart_transformer_report(
        transform_coingecko_market_chart_file(input_path, output_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transform a local CoinGecko market_chart JSON fixture into normalizer-ready rows."
    )
    parser.add_argument("input_path")
    parser.add_argument("--output-path", default=None)
    args = parser.parse_args()

    print(report_dynamic_coingecko_market_chart_transformer(args.input_path, args.output_path))


if __name__ == "__main__":
    main()
