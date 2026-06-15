"""Report CLI for J.A.R.V.I.S. dynamic public data fetcher adapter."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_public_data_fetcher_adapter import (
    DynamicPublicDataFetcherAdapterResult,
    build_dynamic_public_data_fetcher_adapter,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_ENDPOINT_PATH = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def build_dynamic_public_data_fetcher_adapter_report(result: DynamicPublicDataFetcherAdapterResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Public Data Fetcher Adapter",
        "Adapter-only bridge into existing jarvis_public_data_fetcher config. No fetching performed.",
        f"status: {result.status}",
        f"import plan status: {result.import_plan_status}",
        f"adapted source count: {result.adapted_source_count}",
        f"blocked source count: {result.blocked_source_count}",
        f"authorization required: {result.authorization_required}",
        f"authorization phrase: {result.authorization_phrase}",
        f"dry run default: {result.dry_run_default}",
        f"network forbidden by adapter: {result.network_forbidden_by_adapter}",
        f"write forbidden by adapter: {result.write_forbidden_by_adapter}",
        f"local cache only: {result.local_cache_only}",
        f"raw data unverified: {result.raw_data_unverified}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "adapter rows:",
    ]

    for row in result.rows:
        lines.append(
            f"- {row.asset_id}: {row.status}; source_id={row.source_id}; "
            f"type={row.source_type}; content_type={row.expected_content_type}; frequency={row.update_frequency}; "
            f"series={row.cache_series_id}"
        )
        for warning in row.warnings:
            lines.append(f"  warning: {warning}")
        for blocker in row.blockers:
            lines.append(f"  blocker: {blocker}")

    if not result.rows:
        lines.append("- none")

    lines.append("")
    lines.append("public fetcher config:")
    lines.append(f"- source count: {len(result.public_fetcher_config.get('sources', []))}")
    lines.append(f"- execute_fetch: {result.public_fetcher_config.get('execute_fetch')}")
    lines.append(f"- write_local_cache: {result.public_fetcher_config.get('write_local_cache')}")

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
            "- no market fetch performed by adapter",
            "- existing public fetcher must handle any future authorized fetch",
            "- no broker integration",
            "- no buy request created",
            "- no approval granted",
            "- no execution",
            "- no trades executed",
        ]
    )
    return "\n".join(lines)


def report_dynamic_public_data_fetcher_adapter(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    endpoint_path: str | Path = DEFAULT_ENDPOINT_PATH,
) -> str:
    return build_dynamic_public_data_fetcher_adapter_report(
        build_dynamic_public_data_fetcher_adapter(registry_path, binding_path, endpoint_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dynamic public data fetcher adapter config.")
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("endpoint_path", nargs="?", default=DEFAULT_ENDPOINT_PATH)
    args = parser.parse_args()

    print(report_dynamic_public_data_fetcher_adapter(args.registry_path, args.binding_path, args.endpoint_path))


if __name__ == "__main__":
    main()
