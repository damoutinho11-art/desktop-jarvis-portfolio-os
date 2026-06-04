"""Deterministic audit for manual asset status change requests."""

from __future__ import annotations

from pathlib import Path

from .asset_status_workflow import load_asset_status_requests, validate_asset_status_requests


def build_asset_status_audit_report(path: str | Path) -> str:
    results = validate_asset_status_requests(load_asset_status_requests(path))
    valid = [result for result in results if result.valid]
    blocked = [result for result in results if not result.valid]
    lines = [
        "J.A.R.V.I.S. Asset Status Change Audit",
        "Read-only local fixture. No asset approvals applied.",
        f"valid requests: {len(valid)}",
        f"blocked requests: {len(blocked)}",
        "requests:",
    ]
    for result in results:
        request = result.request
        lines.append(
            f"- {request.request_id}: {request.current_status} -> {request.requested_status}; "
            f"allowed_transition={result.allowed_transition}; "
            f"manual_approval_required={request.manual_approval_required}; "
            f"auto_execute={request.auto_execute}"
        )
        if result.missing_confirmations:
            lines.append(f"  missing confirmations: {', '.join(result.missing_confirmations)}")
        else:
            lines.append("  missing confirmations: none")
        for blocker in result.blockers:
            lines.append(f"  blocker: {blocker}")
    lines.append("No registry files modified.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit local asset status change requests.")
    parser.add_argument("requests_path", nargs="?", default="jarvis/data/asset_status_requests.example.json")
    args = parser.parse_args()
    print(build_asset_status_audit_report(args.requests_path))


if __name__ == "__main__":
    main()
