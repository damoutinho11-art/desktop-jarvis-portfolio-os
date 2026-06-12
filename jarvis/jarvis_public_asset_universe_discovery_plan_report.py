"""Markdown report for v4.61 public asset universe discovery plan."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_discovery_plan import (
    PublicAssetUniverseDiscoveryPlanResult,
    load_public_asset_universe_discovery_plan_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_discovery_plan.example.json")


def _bool_text(value: object) -> str:
    return str(value is True).lower()


def build_public_asset_universe_discovery_plan_report(result: PublicAssetUniverseDiscoveryPlanResult) -> str:
    cache_paths = result.local_cache_plan.get("planned_paths", [])
    classification_tags = result.classification_plan.get("classification_tags", [])
    allowed_screening = result.screening_plan.get("allowed_outputs", [])
    forbidden_screening = result.screening_plan.get("forbidden_outputs", [])
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.overall_status}",
        f"plan mode: {result.plan_mode or 'missing'}",
        f"report only: {_bool_text(result.report_only)}",
        f"no network: {_bool_text(result.no_network)}",
        f"no fetching: {_bool_text(result.no_fetching)}",
        f"no downloading: {_bool_text(result.no_downloading)}",
        f"no writes: {_bool_text(result.no_writes)}",
        f"no cache creation: {_bool_text(result.no_cache_creation)}",
        f"no subprocess: {_bool_text(result.no_subprocess)}",
        f"no scheduler creation: {_bool_text(result.no_scheduler_creation)}",
        f"no broker integration: {_bool_text(result.no_broker_integration)}",
        "",
        "## Strategic Correction",
        "- no manual one-by-one asset entry as the primary workflow.",
        "- public universe discovery is the main workflow.",
        "- manual candidate entry remains optional for forced or user-specific research ideas.",
        "- J.A.R.V.I.S. should eventually fetch public research data through explicit local-cache stages.",
        "- final real-world purchases remain manual and external, including Lightyear, LHV, or crypto venues outside J.A.R.V.I.S.",
        "",
        "## Target Asset Universes",
        "universe | asset class | required fields | source categories",
        "--- | --- | --- | ---",
    ]
    if result.target_asset_universes:
        for universe in result.target_asset_universes:
            lines.append(
                f"{universe.universe_id} | {universe.asset_class} | {len(universe.required_fields)} | {', '.join(universe.source_categories)}"
            )
    else:
        lines.append("none | none | 0 | none")
    lines.extend(["", "## Public Source Categories", "source category | update frequency | expected fields", "--- | --- | ---"])
    if result.public_source_categories:
        for category in result.public_source_categories:
            lines.append(
                f"{category.source_category_id} | {category.expected_update_frequency} | {', '.join(category.expected_fields)}"
            )
    else:
        lines.append("none | none | none")
    lines.extend(["", "## Required Fields Summary"])
    if result.required_universe_fields:
        for universe_id, fields in sorted(result.required_universe_fields.items()):
            lines.append(f"- {universe_id}: {', '.join(fields)}")
    else:
        lines.append("- none")
    lines.extend(["", "## Local Cache Plan"])
    lines.append("- cache writes are not performed in v4.61.")
    lines.append("- local cache must remain ignored and uncommitted.")
    lines.append("- raw data remains unverified; normalized data remains unapproved.")
    lines.append("- future cache builder must require explicit authorization and be local-cache-only.")
    lines.append("- no fetched data committed.")
    for path in cache_paths if isinstance(cache_paths, list) else []:
        lines.append(f"- planned path only: {path}")
    lines.extend(["", "## Classification Plan"])
    for tag in classification_tags if isinstance(classification_tags, list) else []:
        lines.append(f"- {tag}")
    lines.extend(
        [
            "- classification does not imply approved, trusted, investable, buy, sell, allocation, or portfolio weight.",
            "",
            "## Screening Plan",
            f"- allowed outputs: {', '.join(allowed_screening) if isinstance(allowed_screening, list) else 'none'}",
            f"- forbidden outputs: {', '.join(forbidden_screening) if isinstance(forbidden_screening, list) else 'none'}",
            "- screening is research prioritization only and not investment advice.",
            "",
            "## Evidence Readiness Route",
        ]
    )
    lines.extend(f"- {step}" for step in result.evidence_readiness_route) if result.evidence_readiness_route else lines.append("- none")
    lines.extend(
        [
            "- discovery is not verification.",
            "- cache is not evidence verification.",
            "- classification is not approval.",
            "- screening is not investment advice.",
            "- evidence pack generation is not a buy/sell signal.",
            "- final real-world purchase is manual and external.",
            "",
            "## Human Action Boundary",
        ]
    )
    for key, value in sorted(result.human_action_boundary.items()):
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Future Build Sequence"])
    for stage in result.future_build_sequence:
        lines.extend(
            [
                f"### {stage.stage_id} {stage.stage_name}",
                f"- real new boundary: {str(stage.real_new_boundary).lower()}",
                f"- purpose: {stage.purpose}",
                f"- why not redundant: {stage.why_not_redundant}",
            ]
        )
    if not result.future_build_sequence:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.61 defines the public universe discovery plan and safety schema.",
            "- v4.60 local bootstrap remains useful for optional local operator files.",
            "- manual one-by-one entry is no longer the main candidate discovery path.",
            "",
            "## Where We Need To Go",
            "- build the public source manifest schema next.",
            "- then plan explicit local-cache fetches without default network activity.",
            "- later normalize, classify, screen for research priority, and generate evidence packs.",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.redundant_next_steps_to_avoid) if result.redundant_next_steps_to_avoid else lines.append("- another gate")
    lines.extend(
        [
            "",
            "## Redundancy Check",
            "- do not build another manual one-candidate-at-a-time gate as the main path.",
            "- do not build review-of-review loops.",
            "- do not build an executor, broker integration, allocation engine, or trading bot.",
            "",
            "## Next Efficient Action",
            f"- {result.next_manual_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- local-first public research OS, not a trading bot.",
            "- public universe discovery -> source manifest -> local cache -> freshness -> classification -> screening -> evidence packs -> human dashboard -> external manual action.",
            "",
            "## Blocked Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in result.blocked_reasons) if result.blocked_reasons else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no writes",
            "no cache creation",
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
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not claim fetching, API calls, scraping, writing, scheduling, broker integration, Lightyear integration, LHV integration, crypto exchange integration, credential use, evidence verification, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_discovery_plan_report(
        load_public_asset_universe_discovery_plan_result(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe discovery plan report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to discovery plan JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
