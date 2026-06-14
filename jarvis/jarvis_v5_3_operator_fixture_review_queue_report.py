"""Markdown report for v5.3 operator fixture review queue."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_3_operator_fixture_review_queue import (
    V53OperatorFixtureReviewQueueResult,
    load_v5_3_operator_fixture_review_queue_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_3_operator_fixture_review_queue.example.json")


def build_v5_3_operator_fixture_review_queue_report(result: V53OperatorFixtureReviewQueueResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"operator fixture review queue mode: {result.operator_fixture_review_queue_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Import Preview Summary",
        f"- import preview count: {result.import_preview_count}",
        f"- unsafe count: {result.unsafe_count}",
        f"- unsupported format count: {result.unsupported_format_count}",
        f"- unsupported category count: {result.unsupported_category_count}",
        f"- duplicate fixture id count: {result.duplicate_fixture_id_count}",
        f"- private or credential risk count: {result.private_or_credential_risk_count}",
        f"- forbidden flag count: {result.forbidden_flag_count}",
        f"- missing fixture count: {result.missing_fixture_count}",
        f"- stale fixture count: {result.stale_fixture_count}",
        f"- manual refresh required count: {result.manual_refresh_required_count}",
        "",
        "## Review Queue Summary",
        f"- review queue count: {result.review_queue_count}",
        f"- accepted for research draft only count: {result.accepted_for_research_draft_only_count}",
        f"- needs operator review count: {result.needs_operator_review_count}",
        f"- deferred count: {result.deferred_count}",
        f"- rejected count: {result.rejected_count}",
        "review id | fixture id | category | format | priority | decision | allowed next stage | blocked next stages",
        "--- | --- | --- | --- | --- | --- | --- | ---",
    ]
    if result.review_rows:
        for row in result.review_rows:
            lines.append(
                f"{row['review_id']} | {row['fixture_id']} | {row['source_category_id']} | {row['fixture_format']} | "
                f"{row['review_priority']} | {row['review_decision']} | {row['allowed_next_stage']} | "
                f"{', '.join(row['blocked_next_stage'])}"
            )
    else:
        lines.append("none | none | none | none | none | none | none | none")
    lines.extend(
        [
            "",
            "## Review Decision Summary",
            f"- accepted_for_research_draft_only: {result.accepted_for_research_draft_only_count}",
            f"- needs_operator_review: {result.needs_operator_review_count}",
            f"- deferred: {result.deferred_count}",
            f"- rejected: {result.rejected_count}",
            "- accepted_for_research_draft_only is only unverified research-draft source routing.",
            "- accepted_for_research_draft_only is not evidence verification, approval, trust, investability, recommendation, allocation, buy/sell, or trade.",
            "",
            "## Review Priority Summary",
            f"- high priority count: {result.high_priority_count}",
            f"- medium priority count: {result.medium_priority_count}",
            f"- low priority count: {result.low_priority_count}",
            "",
            "## Blockers / Warnings",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Operator Runbook Steps",
        ]
    )
    if result.operator_runbook_steps:
        lines.extend(f"{index}. {step}" for index, step in enumerate(result.operator_runbook_steps, start=1))
    else:
        lines.append("1. Review import-preview rows before any downstream source routing.")
    lines.extend(
        [
            "",
            "## Output / Write Authorization Summary",
            "- report wrote files: false",
            f"- ready to write with explicit authorization: {str(result.status == 'V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_READY_TO_WRITE_SAFE').lower()}",
            "- required phrase: AUTHORIZE_V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE",
            "- optional write root: jarvis/local/public_source_fixtures/v5_3_operator_review_queue",
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
            "- v5.1 wired public fixture preparation.",
            "- v5.2 dry-ran local public fixture import.",
            "- v5.3 creates a manual operator review queue from import-preview metadata only.",
            "",
            "## Where We Need To Go",
            "- operators review, accept for research-draft-only routing, defer, or reject fixture metadata.",
            "- next efficient phase is v5.4 Research Draft Source Router, still without evidence verification or fetching.",
            "",
            "## Anti-Redundancy Statement",
            "- v5.1 answers what fixtures should exist and where.",
            "- v5.2 answers whether local fixture metadata can be import-previewed safely.",
            "- v5.3 answers which import previews require manual accept, defer, or reject decisions before downstream draft routing.",
            "- this layer does not repeat fixture wiring or file inspection.",
            "",
            "## Post-v5.2 Phase Statement",
            "- v5.3 is a human-control queue after import dry-run.",
            "- it does not add fetching, evidence verification, approval, recommendation, or execution.",
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
    return build_v5_3_operator_fixture_review_queue_report(load_v5_3_operator_fixture_review_queue_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.3 operator fixture review queue report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.3 operator fixture review queue JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
