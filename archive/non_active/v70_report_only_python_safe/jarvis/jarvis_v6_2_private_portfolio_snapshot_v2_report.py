"""Report CLI for J.A.R.V.I.S. v6.2 private portfolio snapshot v2."""

from __future__ import annotations

import argparse

from .jarvis_v6_2_private_portfolio_snapshot_v2 import (
    PrivatePortfolioSnapshotV2AuditResult,
    audit_v6_2_private_portfolio_snapshot_v2,
)


def build_v6_2_private_portfolio_snapshot_v2_report(
    result: PrivatePortfolioSnapshotV2AuditResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.2 Private Portfolio Snapshot v2",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"private snapshot v2 ready: {result.private_snapshot_v2_ready}",
        "",
        "## Portfolio State",
        "",
        f"- snapshot id: {result.snapshot.snapshot_id}",
        f"- as of date: {result.snapshot.as_of_date}",
        f"- base currency: {result.snapshot.base_currency}",
        f"- snapshot age hours: {result.snapshot.snapshot_age_hours}",
        f"- max allowed snapshot age hours: {result.snapshot.max_allowed_snapshot_age_hours}",
        f"- investable cash EUR: {result.investable_cash_eur}",
        f"- protected cash EUR: {result.protected_cash_eur}",
        f"- holdings value EUR: {result.holdings_value_eur}",
        f"- total portfolio value EUR: {result.total_portfolio_value_eur}",
        "",
        "## Account Roles",
        "",
        "- required roles:",
    ]

    lines.extend(f"  - {role}" for role in result.required_account_roles)
    lines.append("- present roles:")
    lines.extend(f"  - {role}" for role in result.account_roles_present)

    lines.extend(["", "## Cash Buckets"])
    for bucket in result.snapshot.cash_buckets:
        lines.extend(
            [
                "",
                f"### {bucket.bucket_id}",
                f"- account id: {bucket.account_id}",
                f"- amount EUR: {bucket.amount_eur}",
                f"- protected: {bucket.protected}",
                f"- investable: {bucket.investable}",
                f"- reason: {bucket.reason}",
            ]
        )

    lines.extend(["", "## Holdings"])
    for holding in result.snapshot.holdings:
        lines.extend(
            [
                "",
                f"### {holding.asset_id}",
                f"- display name: {holding.display_name}",
                f"- asset class: {holding.asset_class}",
                f"- sleeve id: {holding.sleeve_id}",
                f"- account id: {holding.account_id}",
                f"- platform: {holding.platform}",
                f"- market value EUR: {holding.market_value_eur}",
                f"- manually entered: {holding.manually_entered}",
                f"- source fresh: {holding.source_fresh}",
            ]
        )

    lines.extend(["", "## Sleeve Weights"])
    for sleeve_id, weight in result.sleeve_weights_pct.items():
        lines.append(f"- {sleeve_id}: {weight}%")

    lines.extend(["", "## Issues"])
    if result.issues:
        for issue in result.issues:
            lines.append(f"- {issue.severity}: {issue.message}")
    else:
        lines.append("- none")

    lines.extend(["", "## Warnings"])
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")

    lines.extend(["", "## Blockers"])
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- local private data only: {result.local_private_data_only}",
            f"- operator confirmation required: {result.operator_confirmation_required}",
            (
                "- automatic import forbidden at this stage: "
                f"{result.automatic_import_forbidden_at_this_stage}"
            ),
            f"- broker API forbidden: {result.broker_api_forbidden}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- active policy mutated: {result.active_policy_mutated}",
            f"- creates buy request: {result.creates_buy_request}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_2_private_portfolio_snapshot_v2() -> str:
    return build_v6_2_private_portfolio_snapshot_v2_report(
        audit_v6_2_private_portfolio_snapshot_v2()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.2 private portfolio snapshot v2."
    )
    parser.parse_args()
    print(report_v6_2_private_portfolio_snapshot_v2())


if __name__ == "__main__":
    main()
