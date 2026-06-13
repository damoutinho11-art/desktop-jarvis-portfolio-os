"""Markdown report for v4.69 public evidence pack draft generator."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .jarvis_public_evidence_pack_draft_generator import (
    PublicEvidencePackDraftGeneratorResult,
    load_public_evidence_pack_draft_generator_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_evidence_pack_draft_generator.example.json")


def build_public_evidence_pack_draft_generator_report(result: PublicEvidencePackDraftGeneratorResult) -> str:
    section_counts = Counter()
    source_counts = Counter()
    checklist_counts = Counter()
    for draft in result.draft_packs:
        section_counts.update(draft["required_public_evidence_sections"])
        source_counts.update(draft["required_public_source_categories"])
        checklist_counts.update(draft["manual_verification_checklist"])
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"draft generator mode: {result.draft_generator_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Draft Pack Summary",
        f"- research queue item count: {result.queue_item_count}",
        f"- draft pack count: {result.draft_pack_count}",
        f"- ready draft count: {result.ready_draft_count}",
        f"- needs more public data count: {result.needs_more_public_data_count}",
        f"- manual source review count: {result.manual_source_review_count}",
        f"- blocked safe count: {result.blocked_safe_count}",
        "",
        "## Required Evidence Section Summary",
    ]
    if section_counts:
        for section in sorted(section_counts):
            lines.append(f"- {section}: {section_counts[section]}")
    else:
        lines.append("- none")
    lines.extend(["", "## Required Public Source Category Summary"])
    if source_counts:
        for source in sorted(source_counts):
            lines.append(f"- {source}: {source_counts[source]}")
    else:
        lines.append("- none")
    lines.extend(["", "## Manual Verification Checklist Summary"])
    if checklist_counts:
        for item in sorted(checklist_counts):
            lines.append(f"- {item}: {checklist_counts[item]}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Skipped / Blocked Item Summary",
            f"- skipped item count: {result.skipped_item_count}",
            f"- blocked item count: {result.blocked_item_count}",
            "- skipped items: " + (", ".join(result.skipped_items) if result.skipped_items else "none"),
            "- blocked items: " + (", ".join(result.blocked_items) if result.blocked_items else "none"),
            "",
            "## Duplicate Draft ID Summary",
            f"- duplicate draft pack id count: {result.duplicate_draft_pack_id_count}",
            "",
            "## Output / Write Authorization Summary",
            "- default write allowed: false",
            "- report writes files: false",
            "- optional write requires exact authorization phrase",
            "- draft evidence packs remain unverified and unapproved",
            "",
            "## Sample Draft Packs",
            "draft_pack_id | asset_id | priority | next manual research step | verification_status | approval_status",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    if result.draft_packs:
        for draft in result.draft_packs[:10]:
            lines.append(
                f"{draft['draft_pack_id']} | {draft['asset_id']} | {draft['research_priority_bucket']} | "
                f"{draft['next_manual_research_step']} | {draft['verification_status']} | {draft['approval_status']}"
            )
    else:
        lines.append("none | none | none | none | none | none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.69 drafts public evidence-pack checklists from public research queue items.",
            "- draft packs are workflow scaffolding only, not verified evidence.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.70 Operator Research Dashboard Integration.",
            "- public evidence must still be collected and manually reviewed later.",
            "",
            "## Do Not Build Next",
            "- evidence extraction inside v4.69",
            "- evidence verification inside v4.69",
            "- investment screening",
            "- research scoring based on returns",
            "- recommendation",
            "- scheduler",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not classification.",
            "- this is not a research priority queue.",
            "- this is not evidence extraction, verification, recommendation, approval, allocation, trading, or execution.",
            "",
            "## Next Efficient Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- public universe discovery -> source manifest -> local cache -> cache audit -> normalization -> classification -> research queue -> evidence packs -> human dashboard -> external manual action.",
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
            "This report does not claim evidence extraction, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_evidence_pack_draft_generator_report(load_public_evidence_pack_draft_generator_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public evidence pack draft generator report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to public evidence pack draft generator JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
