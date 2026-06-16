"""Report CLI for J.A.R.V.I.S. v10.0 autonomous public data refresh runtime."""

from __future__ import annotations

import argparse

from .jarvis_public_data_fetcher import AUTHORIZATION_PHRASE
from .jarvis_v10_0_autonomous_public_data_refresh_runtime import (
    AutonomousPublicDataRefreshRuntimeResult,
    audit_v10_0_autonomous_public_data_refresh_runtime,
)


def build_v10_0_autonomous_public_data_refresh_runtime_report(
    result: AutonomousPublicDataRefreshRuntimeResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v10.0 Autonomous Public Data Refresh Runtime",
        "",
        f"status: {result.status}",
        f"runtime status: {result.runtime_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"roadmap lock status: {result.roadmap_lock_status}",
        f"source manifest path: {result.source_manifest_path}",
        f"source manifest loaded: {result.source_manifest_loaded}",
        f"demo manifest used: {result.demo_manifest_used}",
        f"execute fetch requested: {result.execute_fetch_requested}",
        f"authorization phrase valid: {result.authorization_phrase_valid}",
        f"fetcher overall status: {result.fetcher_overall_status}",
        f"source count: {result.source_count}",
        f"valid source count: {result.valid_source_count}",
        f"blocked source count: {result.blocked_source_count}",
        f"update plan count: {result.update_plan_count}",
        f"fetched file count: {result.fetched_file_count}",
        f"output directory: {result.output_directory}",
        "",
        "## Fetched Files",
    ]

    lines.extend(f"- {item}" for item in result.fetched_files) if result.fetched_files else lines.append("- none")

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Runtime",
            "",
            f"- runtime contract ready: {result.runtime_contract_ready}",
            f"- autonomous refresh ready: {result.autonomous_refresh_ready}",
            f"- raw public data refreshed: {result.raw_public_data_refreshed}",
            f"- ready for downstream normalization: {result.ready_for_downstream_normalization}",
            f"- ready for downstream source quality gate: {result.ready_for_downstream_source_quality_gate}",
            f"- recommendation quality current data: {result.recommendation_quality_current_data}",
            "",
            "## Safety",
            "",
            f"- local cache only: {result.local_cache_only}",
            f"- raw data unverified: {result.raw_data_unverified}",
            f"- source selection not repeated: {result.source_selection_not_repeated}",
            f"- dry-run planner not rebuilt: {result.dry_run_planner_not_rebuilt}",
            f"- provider registry not rebuilt: {result.provider_registry_not_rebuilt}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
            f"- private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}",
            f"- credentials forbidden: {result.credentials_forbidden}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v10_0_autonomous_public_data_refresh_runtime(
    *,
    manifest_path: str | None = None,
    execute_fetch: bool = False,
    authorization_phrase: str = "",
    fetch_date: str = "1970-01-01",
    root: str = ".",
) -> str:
    result = audit_v10_0_autonomous_public_data_refresh_runtime(
        manifest_path=manifest_path,
        execute_fetch=execute_fetch,
        authorization_phrase=authorization_phrase,
        fetch_date=fetch_date,
        root=root,
    )
    return build_v10_0_autonomous_public_data_refresh_runtime_report(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v10.0 autonomous public data refresh runtime."
    )
    parser.add_argument("--manifest", default=None, help="Optional local public data source manifest path.")
    parser.add_argument("--execute-fetch", action="store_true", help="Execute public fetch through existing safe boundary.")
    parser.add_argument("--authorization-phrase", default="", help="Exact authorization phrase for real local-cache fetch.")
    parser.add_argument("--fetch-date", default="1970-01-01", help="Fetch date prefix for local raw cache files.")
    parser.add_argument("--root", default=".", help="Repo root for local-cache path validation.")
    args = parser.parse_args()

    print(
        report_v10_0_autonomous_public_data_refresh_runtime(
            manifest_path=args.manifest,
            execute_fetch=args.execute_fetch,
            authorization_phrase=args.authorization_phrase,
            fetch_date=args.fetch_date,
            root=args.root,
        )
    )


if __name__ == "__main__":
    main()
