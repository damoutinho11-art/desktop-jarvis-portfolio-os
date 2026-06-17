"""Markdown report for v5.2 real fixture import dry-run."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_2_real_fixture_import_dry_run import (
    V52RealFixtureImportDryRunResult,
    load_v5_2_real_fixture_import_dry_run_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_2_real_fixture_import_dry_run.example.json")


def build_v5_2_real_fixture_import_dry_run_report(result: V52RealFixtureImportDryRunResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"import dry-run mode: {result.import_dry_run_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Fixture Summary",
        f"- fixture count: {result.fixture_count}",
        f"- import candidate count: {result.import_candidate_count}",
        f"- ready import count: {result.ready_import_count}",
        f"- skipped import count: {result.skipped_import_count}",
        f"- missing fixture count: {result.missing_fixture_count}",
        f"- stale fixture count: {result.stale_fixture_count}",
        f"- manual refresh required count: {result.manual_refresh_required_count}",
        f"- invalid path count: {result.invalid_path_count}",
        f"- unsupported format count: {result.unsupported_format_count}",
        f"- unsafe fixture count: {result.unsafe_fixture_count}",
        f"- duplicate fixture id count: {result.duplicate_fixture_id_count}",
        "fixture id | category | format | status | exists | size bytes | metadata | blockers | warnings",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    if result.fixture_rows:
        for row in result.fixture_rows:
            lines.append(
                f"{row['fixture_id']} | {row['source_category_id']} | {row['fixture_format']} | "
                f"{row['import_status']} | {str(row['exists']).lower()} | {row['size_bytes']} | "
                f"{row['metadata_type'] or 'none'} | {row['blocker_count']} | {row['warning_count']}"
            )
    else:
        lines.append("none | none | none | none | false | 0 | none | 0 | 0")
    lines.extend(
        [
            "",
            "## Local File Inspection Summary",
            f"- shallow metadata count: {result.shallow_metadata_count}",
            f"- hash fingerprint count: {result.hash_fingerprint_count}",
            "- CSV inspection reads row count and header columns only.",
            "- JSON inspection reads top-level type, keys, and item count only.",
            "- TXT/MD inspection reads line count only.",
            "- HTML/PDF inspection records presence, size, hash, and timestamp only.",
            "- no OCR: true",
            "- no PDF parsing: true",
            "- no HTML scraping: true",
            "",
            "## Import Preview Summary",
            "fixture id | import status | dry-run preview | hash present | evidence verified | approved asset | buy signal",
            "--- | --- | --- | --- | --- | --- | ---",
        ]
    )
    if result.import_preview_rows:
        for row in result.import_preview_rows:
            lines.append(
                f"{row['fixture_id']} | {row['import_status']} | {str(row['dry_run_import_preview']).lower()} | "
                f"{str(bool(row['hash_fingerprint'])).lower()} | {str(row['evidence_verified']).lower()} | "
                f"{str(row['approved_asset']).lower()} | {str(row['buy_signal']).lower()}"
            )
    else:
        lines.append("none | none | false | false | false | false | false")
    lines.extend(
        [
            "",
            "## Pipeline Mapping Summary",
            f"- mapped to pipeline count: {result.mapped_to_pipeline_count}",
            f"- blocked mapping count: {result.blocked_mapping_count}",
            "fixture id | mapped | import targets | blocked reason",
            "--- | --- | --- | ---",
        ]
    )
    if result.pipeline_mapping_rows:
        for row in result.pipeline_mapping_rows:
            targets = ", ".join(row["import_targets"]) if row["import_targets"] else "none"
            lines.append(f"{row['fixture_id']} | {str(row['mapped']).lower()} | {targets} | {row['blocked_reason'] or 'none'}")
    else:
        lines.append("none | false | none | none")
    lines.extend(
        [
            "",
            "## Operator Runbook Steps",
        ]
    )
    if result.operator_runbook_steps:
        lines.extend(f"{index}. {step}" for index, step in enumerate(result.operator_runbook_steps, start=1))
    else:
        lines.append("1. Prepare local public-source fixtures before importing anything downstream.")
    lines.extend(
        [
            "",
            "## Blockers / Warnings",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Output / Write Authorization Summary",
            f"- report wrote files: false",
            f"- ready to write with explicit authorization: {str(result.status == 'V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_READY_TO_WRITE_SAFE').lower()}",
            "- required phrase: AUTHORIZE_V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE",
            "- optional write root: jarvis/local/public_source_fixtures/v5_2_import_dry_run",
            "- committed examples do not require real local cache files.",
            "",
            "## Next Safe Operator Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.do_not_build_next)
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v5.0 is sealed.",
            "- v5.1 wired operator-managed public fixture metadata.",
            "- v5.2 performs local-only import dry-run inspection of public fixtures.",
            "- fixture import previews remain unverified and unapproved.",
            "",
            "## Where We Need To Go",
            "- review fixture import dry-run results manually.",
            "- prepare missing local public fixtures manually when needed.",
            "- proceed to v5.3 operator fixture review queue or explicit authorized public fetch stub only after review.",
            "",
            "## Post-v5.1 Phase Statement",
            "- v5.2 is an operational bridge after fixture wiring.",
            "- it does not change the v5.0 verdict or add live fetching.",
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no browser automation",
            "no subprocess execution",
            "no scheduler creation",
            "no broker integration",
            "no Lightyear integration",
            "no LHV integration",
            "no crypto exchange integration",
            "no credentials",
            "no private/account data ingest",
            "no OCR",
            "no PDF parsing",
            "no HTML scraping",
            "no source parsing as verified evidence",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no investment screening",
            "no research scoring based on expected returns",
            "no ranking by investment merit",
            "no recommendation",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not claim fetching, scraping, OCR, PDF parsing, HTML scraping, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_v5_2_real_fixture_import_dry_run_report(load_v5_2_real_fixture_import_dry_run_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.2 real fixture import dry-run report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.2 real fixture import dry-run JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
