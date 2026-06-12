"""Markdown report for the v4.57 public data fetcher control plane."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_data_fetcher import (
    AUTHORIZATION_PHRASE,
    evaluate_public_data_fetcher,
    fetch_public_sources,
    load_json,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_data_fetcher.example.json")


def _load_manifest(config: dict, explicit_manifest_path: str | None) -> dict | None:
    if explicit_manifest_path:
        return load_json(explicit_manifest_path)
    path = config.get("source_manifest_path")
    if isinstance(path, str) and path and path != "inline_synthetic_manifest":
        return load_json(path)
    return None


def build_public_data_fetcher_report(evaluation) -> str:
    lines = [
        f"# {evaluation.title}",
        "",
        f"version: {evaluation.version}",
        f"overall status: {evaluation.overall_status}",
        f"fetcher mode: {evaluation.fetcher_mode or 'missing'}",
        f"dry-run only: {str(evaluation.dry_run_only).lower()}",
        f"execute fetch: {str(evaluation.execute_fetch).lower()}",
        f"write local cache: {str(evaluation.write_local_cache).lower()}",
        f"authorization phrase valid: {str(evaluation.authorization_phrase_valid).lower()}",
        f"update frequency: {evaluation.update_frequency or 'missing'}",
        f"source count: {evaluation.source_count}",
        f"output cache directory: {evaluation.output_directory or 'missing'}",
        "",
        "Default mode is dry-run/no-network/no-write.",
        "Daily updates are preferred for market/reference freshness.",
        "Weekly updates are acceptable for low-volatility metadata.",
        "This implementation does not install a scheduler automatically.",
        "Fetched data is raw/unverified local cache only when explicitly authorized.",
        "No evidence verification occurred.",
        "No candidate approval, trust, or investability occurred.",
        "No registry or candidate registry mutation occurred.",
        "No broker/authenticated API or credentials are used.",
        "",
        "## Sources",
    ]
    for source in evaluation.source_validations:
        lines.extend(
            [
                f"### {source.source_id}",
                f"- source type: {source.source_type}",
                f"- source url: {source.source_url}",
                f"- update frequency: {source.update_frequency}",
                f"- valid: {str(source.valid).lower()}",
                f"- blocked reasons: {', '.join(source.blocked_reasons) if source.blocked_reasons else 'none'}",
                f"- warnings: {', '.join(source.warnings) if source.warnings else 'none'}",
            ]
        )
    lines.extend(["", "## Update Plan"])
    if evaluation.update_plan:
        for item in evaluation.update_plan:
            lines.append(
                f"- {item.source_id}: {item.planned_action}; frequency={item.update_frequency}; raw_unverified_data_only={str(item.raw_unverified_data_only).lower()}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Fetched Files"])
    lines.extend(f"- {path}" for path in evaluation.fetched_files) if evaluation.fetched_files else lines.append("- none")
    lines.extend(["", "## Blocked Reasons"])
    lines.extend(f"- {reason}" for reason in evaluation.blocked_reasons) if evaluation.blocked_reasons else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in evaluation.warnings) if evaluation.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Route",
            "v4.56 manual candidate data entry workspace -> v4.57 public data fetcher local cache control plane -> future manual source review/fact entry only if separately requested -> v4.27-v4.47 evidence/manual review pipeline",
            "",
            "## Safety Statements",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic private data ingest",
            "no automatic evidence extraction",
            "fetched data ignored from git/local cache only when explicitly authorized",
            "",
            "This report does not claim evidence verification, approval, trust, investability, allocation, portfolio weight, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, automatic evidence extraction, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT, manifest_path: str | None = None) -> str:
    config = load_json(path)
    manifest = _load_manifest(config, manifest_path)
    return build_public_data_fetcher_report(evaluate_public_data_fetcher(config, manifest))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. public data fetcher report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to fetcher config JSON.")
    parser.add_argument("--manifest", default=None, help="Optional public source manifest JSON.")
    parser.add_argument("--execute-fetch", action="store_true", help="Explicitly request public fetch into ignored local cache.")
    parser.add_argument("--authorization-phrase", default="", help="Required exact phrase for real fetch.")
    args = parser.parse_args()

    config = load_json(args.input)
    if args.execute_fetch:
        config = {**config, "execute_fetch": True, "authorization_phrase": args.authorization_phrase}
    manifest = _load_manifest(config, args.manifest)
    if args.execute_fetch and str(args.input).replace("\\", "/").startswith("jarvis/data/"):
        config = {**config, "dry_run_only": True, "write_local_cache": False}
    evaluation = (
        fetch_public_sources(config, manifest or {"sources": []})
        if args.execute_fetch and args.authorization_phrase == AUTHORIZATION_PHRASE and manifest is not None
        else evaluate_public_data_fetcher(config, manifest)
    )
    print(build_public_data_fetcher_report(evaluation))


if __name__ == "__main__":
    main()
