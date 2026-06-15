from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_public_source_transformer_readiness import (
    DEFAULT_CANDIDATE_MATRIX_PATH,
    DynamicPublicSourceTransformerReadinessResult,
    audit_dynamic_public_source_transformer_readiness,
)


def build_dynamic_public_source_transformer_readiness_report(
    result: DynamicPublicSourceTransformerReadinessResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Public Source Transformer Readiness",
        "Report-only transformer-readiness plan. No fetching or execution performed.",
        f"status: {result.status}",
        f"candidate count: {result.candidate_count}",
        f"normalizer ready count: {result.normalizer_ready_count}",
        f"transformer required count: {result.transformer_required_count}",
        f"support only count: {result.support_only_count}",
        f"promotion allowed count: {result.promotion_allowed_count}",
        f"manual review required: {result.manual_review_required}",
        f"fetching forbidden: {result.fetching_forbidden}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "rows:",
    ]

    if result.rows:
        for row in result.rows:
            lines.append(
                f"- {row.source_key}: {row.readiness_classification}; "
                f"provider={row.provider_candidate}; parser={row.parser_compatibility_status}"
            )
            for warning in row.warnings:
                lines.append(f"  warning: {warning}")
            for blocker in row.blockers:
                lines.append(f"  blocker: {blocker}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.append("")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            "- no market fetch performed",
            "- no broker integration",
            "- no buy request created",
            "- no approval granted",
            "- no endpoint promotion",
            "- no execution",
            "- no trades executed",
        ]
    )

    return "\n".join(lines)


def report_dynamic_public_source_transformer_readiness(
    candidate_matrix_path: str | Path = DEFAULT_CANDIDATE_MATRIX_PATH,
) -> str:
    return build_dynamic_public_source_transformer_readiness_report(
        audit_dynamic_public_source_transformer_readiness(candidate_matrix_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the J.A.R.V.I.S. dynamic public source transformer readiness plan."
    )
    parser.add_argument("candidate_matrix_path", nargs="?", default=DEFAULT_CANDIDATE_MATRIX_PATH)
    args = parser.parse_args()

    print(report_dynamic_public_source_transformer_readiness(args.candidate_matrix_path))


if __name__ == "__main__":
    main()
