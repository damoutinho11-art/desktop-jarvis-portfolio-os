"""Readable report for draft evidence manual verification queues."""

from __future__ import annotations

from pathlib import Path

from .evidence_verification_queue import build_evidence_verification_queue


def build_evidence_verification_report(registry_path: str | Path, sources_path: str | Path) -> str:
    queue = build_evidence_verification_queue(registry_path, sources_path)
    sample_questions = queue.tasks[0].verification_questions if queue.tasks else ()
    lines = [
        "J.A.R.V.I.S. Evidence Verification Queue Report",
        "Manual verification queue only. No evidence is automatically verified.",
        "verification queue status: READY" if queue.tasks else "verification queue status: EMPTY",
        f"total draft evidence records: {len(queue.tasks)}",
        f"pending verification tasks: {sum(task.verification_status == 'pending_user_verification' for task in queue.tasks)}",
        f"blocked sources: {len(queue.blocked_sources)}",
        "warnings:",
    ]
    lines.extend(f"- {warning}" for warning in queue.warnings) if queue.warnings else lines.append("- none")
    lines.append("sample verification questions:")
    lines.extend(f"- {question}" for question in sample_questions) if sample_questions else lines.append("- none")
    lines.extend(
        [
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build manual verification queue for draft source evidence.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("sources_path", nargs="?", default="jarvis/data/source_evidence_sources.example.json")
    args = parser.parse_args()
    print(build_evidence_verification_report(args.registry_path, args.sources_path))


if __name__ == "__main__":
    main()
