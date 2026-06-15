"""Report CLI for J.A.R.V.I.S. v6 personal finance command-center audit."""

from __future__ import annotations

import argparse

from .jarvis_v6_personal_finance_command_center_audit import (
    JarvisV6CommandCenterAuditResult,
    audit_jarvis_v6_personal_finance_command_center,
)


def build_jarvis_v6_personal_finance_command_center_audit_report(
    result: JarvisV6CommandCenterAuditResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6 Personal Finance Command Center Audit",
        "",
        f"status: {result.status}",
        f"release anchor: {result.release_anchor}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"capability count: {result.capability_count}",
        f"ready count: {result.ready_count}",
        f"partial count: {result.partial_count}",
        f"missing count: {result.missing_count}",
        "",
        "## Product Boundary",
        "",
        f"- broad universe scan required: {result.broad_universe_scan_required}",
        f"- flexible policy bands required: {result.flexible_policy_bands_required}",
        f"- policy intelligence required: {result.policy_intelligence_required}",
        (
            "- weekly crypto buy allowed if within risk bands: "
            f"{result.weekly_crypto_buy_allowed_if_within_risk_bands}"
        ),
        "",
        "## Capabilities",
    ]

    for capability in result.capabilities:
        lines.extend(
            [
                "",
                f"### {capability.capability_id}",
                f"- name: {capability.name}",
                f"- classification: {capability.classification}",
                f"- status: {capability.status}",
                f"- wired to current system: {capability.wired_to_current_system}",
                f"- next stage: {capability.next_stage}",
                "- existing files:",
            ]
        )
        if capability.existing_files:
            lines.extend(f"  - {path}" for path in capability.existing_files)
        else:
            lines.append("  - none")

        lines.append("- missing requirements:")
        if capability.missing_requirements:
            lines.extend(f"  - {item}" for item in capability.missing_requirements)
        else:
            lines.append("  - none")

        lines.append("- safety notes:")
        if capability.safety_notes:
            lines.extend(f"  - {item}" for item in capability.safety_notes)
        else:
            lines.append("  - none")

    lines.extend(
        [
            "",
            "## Warnings",
        ]
    )
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Blockers",
        ]
    )
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- manual policy approval required: {result.manual_policy_approval_required}",
            f"- manual buy execution only: {result.manual_buy_execution_only}",
            f"- automatic policy change forbidden: {result.automatic_policy_change_forbidden}",
            f"- automatic approval forbidden: {result.automatic_approval_forbidden}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- creates buy request: {result.creates_buy_request}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_jarvis_v6_personal_finance_command_center_audit(repo_root: str = ".") -> str:
    return build_jarvis_v6_personal_finance_command_center_audit_report(
        audit_jarvis_v6_personal_finance_command_center(repo_root)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6 personal finance command-center readiness."
    )
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    print(report_jarvis_v6_personal_finance_command_center_audit(args.repo_root))


if __name__ == "__main__":
    main()
