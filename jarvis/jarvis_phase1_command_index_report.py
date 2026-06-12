"""Read-only J.A.R.V.I.S. Phase 1 command index report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("jarvis/data/jarvis_phase1_command_index.example.json")


def load_command_index(path: str | Path = DEFAULT_INPUT) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_command_index_report(data: dict[str, Any]) -> str:
    stages = data.get("stages", [])
    commands = data.get("key_commands", {})
    statuses = data.get("final_audit_statuses", [])
    safety = data.get("safety_flags", {})

    lines = [
        f"# {data.get('title', 'J.A.R.V.I.S. Phase 1 Command Index')}",
        "",
        f"version: {data.get('version', 'unknown')}",
        f"Phase 1 complete: {str(data.get('phase_1_complete') is True).lower()}",
        "Phase 1 backend gate chain is complete.",
        f"no executor: {str(data.get('no_executor') is True).lower()}",
        f"no mutation: {str(data.get('no_mutation') is True).lower()}",
        "",
        "This report is read-only. It creates no approvals, writes no registry files, runs no executor, and performs no trades.",
        "",
        "## Stages",
    ]
    for stage in stages:
        lines.append(f"- {stage['id']}: {stage['short_name']} (`python -m {stage['report_module']}`)")

    lines.extend(["", "## Key Commands"])
    for key in sorted(commands):
        lines.append(f"- {key}: `{commands[key]}`")

    lines.extend(["", "## Final Audit Statuses"])
    for status in statuses:
        lines.append(f"- {status}")

    lines.extend(
        [
            "",
            "## Safety Non-Execution Statements",
            "no executor",
            "no mutation",
            "no registry mutation",
            "no registry file written",
            "no approved asset automatically",
            "no evidence verification automatically",
            "no verified evidence promotion executed automatically",
            "no allocation recommendation",
            "no buy signal",
            "no buy/sell requests",
            "no trade executed",
            "no broker/authenticated APIs",
            "no credentials",
            "no private file auto-ingest",
            "no automatic source fetching/downloads/extraction",
        ]
    )
    lines.extend(f"- {key}: {str(value).lower()}" for key, value in sorted(safety.items()))
    lines.extend(
        [
            "",
            "## Future Candidate Intake Placeholder",
            str(data.get("future_candidate_intake_placeholder", "Future candidate intake belongs to v4.49 only.")),
            "",
            "This command index does not claim promotion, approval, execution, allocation, buy/sell, or trading authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_command_index_report(load_command_index(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. Phase 1 command index.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to the static command index JSON file.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
