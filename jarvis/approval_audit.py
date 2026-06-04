"""Deterministic approval request audit CLI."""

from __future__ import annotations

from pathlib import Path

from .manual_approval_workflow import load_approval_requests, validate_approval_requests


def build_approval_audit_report(path: str | Path) -> str:
    results = validate_approval_requests(load_approval_requests(path))
    valid_pending = [
        result
        for result in results
        if result.valid and result.request.status == "pending_manual_approval"
    ]
    blocked = [result for result in results if not result.valid]
    warnings = []
    for result in results:
        warnings.extend(result.warnings)

    lines = [
        "J.A.R.V.I.S. Manual Approval Audit",
        "Read-only local fixture. No execution performed.",
        f"total requests: {len(results)}",
        f"valid pending requests: {len(valid_pending)}",
        f"blocked requests: {len(blocked)}",
        "manual approval status:",
    ]
    for result in results:
        lines.append(
            f"- {result.request.request_id}: {result.effective_status}; "
            f"manual_approval_required={result.request.manual_approval_required}; "
            f"auto_execute={result.request.auto_execute}"
        )
        for blocker in result.blockers:
            lines.append(f"  blocker: {blocker}")

    lines.append("warnings:")
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit local manual approval request fixtures.")
    parser.add_argument("approval_path", nargs="?", default="jarvis/data/approval_requests.example.json")
    args = parser.parse_args()
    print(build_approval_audit_report(args.approval_path))


if __name__ == "__main__":
    main()
