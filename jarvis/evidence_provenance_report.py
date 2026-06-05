"""Readable report for the evidence provenance gate."""

from __future__ import annotations

from pathlib import Path

from .evidence_provenance import build_evidence_provenance_gate


def build_evidence_provenance_report(registry_path: str | Path, provenance_path: str | Path) -> str:
    result = build_evidence_provenance_gate(registry_path, provenance_path)
    summary = result.summary
    lines = [
        "J.A.R.V.I.S. Evidence Provenance Gate Report",
        "Read-only provenance audit. Test evidence is not real status-promotion evidence.",
        f"total candidates: {summary.total_candidates}",
        f"candidates with only synthetic/test evidence: {summary.only_synthetic_or_test_evidence_count}",
        f"candidates with verified review evidence: {summary.verified_review_evidence_count}",
        f"real_status_promotion_allowed count: {summary.real_status_promotion_allowed_count}",
        "blockers:",
    ]
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.extend(
        [
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "Manual approval required for all future actions.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit evidence provenance without approvals or registry mutation.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("provenance_path", nargs="?", default="jarvis/data/evidence_provenance.example.json")
    args = parser.parse_args()
    print(build_evidence_provenance_report(args.registry_path, args.provenance_path))


if __name__ == "__main__":
    main()
