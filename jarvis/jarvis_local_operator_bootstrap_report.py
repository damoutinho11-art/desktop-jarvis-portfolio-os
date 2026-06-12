"""Markdown report for v4.60 local operator bootstrap."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_local_operator_bootstrap import LocalOperatorBootstrapResult, load_local_operator_bootstrap_result


DEFAULT_INPUT = Path("jarvis/data/jarvis_local_operator_bootstrap.example.json")


def build_local_operator_bootstrap_report(result: LocalOperatorBootstrapResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.overall_status}",
        f"bootstrap mode: {result.bootstrap_mode or 'missing'}",
        f"report only: {str(result.report_only).lower()}",
        f"no network: {str(result.no_network).lower()}",
        f"no writes: {str(result.no_writes).lower()}",
        f"no subprocess: {str(result.no_subprocess).lower()}",
        f"no scheduler creation: {str(result.no_scheduler_creation).lower()}",
        f"local paths not created by code: {str(result.local_paths_not_created_by_code).lower()}",
        f"gitignore guardrail status: {result.gitignore_guardrail_status}",
        f"next manual action: {result.next_manual_action or 'missing'}",
        "",
        "Commands are documented only and were not executed.",
        "Code did not create local files or directories.",
        "",
        "## Templates",
    ]
    if result.templates:
        for template in result.templates:
            lines.extend(
                [
                    f"### {template.template_id}",
                    f"- template path: {template.template_path}",
                    f"- recommended local copy path: {template.recommended_local_copy_path}",
                    f"- purpose: {template.purpose}",
                    f"- contains private data: {str(template.contains_private_data).lower()}",
                    f"- should commit template: {str(template.should_commit_template).lower()}",
                    f"- should commit local copy: {str(template.should_commit_local_copy).lower()}",
                ]
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Recommended Ignored Local Paths"])
    lines.extend(f"- {path}" for path in result.recommended_local_paths) if result.recommended_local_paths else lines.append("- none")
    lines.extend(["", "## Missing Gitignore Patterns"])
    lines.extend(f"- {pattern}" for pattern in result.missing_gitignore_patterns) if result.missing_gitignore_patterns else lines.append("- none")
    lines.extend(["", "## Manual PowerShell Copy Commands"])
    lines.extend(f"- `{command}`" for command in result.required_manual_commands) if result.required_manual_commands else lines.append("- none")
    lines.extend(["", "## Manual Dry-Run Report Commands"])
    lines.extend(f"- `{command}`" for command in result.reports_to_run_manually) if result.reports_to_run_manually else lines.append("- none")
    lines.extend(["", "## Smoke Checks"])
    lines.extend(f"- {check}" for check in result.smoke_checks) if result.smoke_checks else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- Phase 1 and Phase 2 safety/reporting layers are in place.",
            "- Local bootstrap now documents how the operator can safely create ignored local files manually.",
            "- This layer verifies the bootstrap plan, not the private data itself.",
            "",
            "## Where We Need To Go",
            "- edit local candidate watchlist",
            "- configure local public source manifest",
            "- then optionally run v4.57 explicit fetch manually",
            "",
            "## Do Not Build Next",
            "- more gates",
            "- scheduler/executor",
            "- evidence extraction",
            "- registry mutation",
            "- allocation/buy/sell/trade logic",
            "",
            "## Route",
            "v4.56 manual candidate data entry workspace -> v4.57 public data fetcher local cache control plane -> v4.58 public data freshness monitor -> v4.59 operator dashboard -> v4.60 local operator bootstrap -> future local manual data entry by user",
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
            "no writes",
            "no directory creation",
            "no template copying by code",
            "no subprocess execution",
            "no scheduler creation",
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
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic private data ingest",
            "no fetched data committed",
            "",
            "This report does not claim fetching, writing, scheduling, evidence verification, approval, trust, investability, allocation, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, automatic evidence extraction, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_local_operator_bootstrap_report(load_local_operator_bootstrap_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. local operator bootstrap report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to bootstrap JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
