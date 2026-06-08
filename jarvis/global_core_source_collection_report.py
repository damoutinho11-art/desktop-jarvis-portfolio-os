"""Readable report for the global core source collection planner."""

from __future__ import annotations

from pathlib import Path

from .global_core_source_collection_planner import build_global_core_source_collection_plan_from_files


def build_global_core_source_collection_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
) -> str:
    plan = build_global_core_source_collection_plan_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
    )
    lines = [
        "J.A.R.V.I.S. Global Core Source Collection Plan Report",
        "Read-only manual collection plan. No fetching, verification, approval, allocation, or trading.",
        f"collection plan status: {plan.collection_plan_status}",
        f"target candidates count: {len(plan.target_candidates)}",
        f"total collection tasks: {len(plan.tasks)}",
        "tasks by candidate:",
    ]
    lines.extend(
        f"- {asset_id}: {count}" for asset_id, count in plan.tasks_by_candidate.items()
    ) if plan.tasks_by_candidate else lines.append("- none")
    lines.append("tasks by collection mode:")
    lines.extend(
        f"- {mode}: {count}" for mode, count in plan.tasks_by_collection_mode.items()
    ) if plan.tasks_by_collection_mode else lines.append("- none")
    lines.append("top next collection tasks:")
    if plan.top_next_collection_tasks:
        lines.extend(
            f"- {task.collection_task_id}: {task.asset_id} {task.evidence_type} "
            f"({task.collection_mode}, priority {task.collection_priority})"
            for task in plan.top_next_collection_tasks
        )
    else:
        lines.append("- none")
    lines.extend(
        [
            f"account-specific manual tasks count: {plan.account_specific_manual_tasks_count}",
            f"manual tax review tasks count: {plan.manual_tax_review_tasks_count}",
            f"auto-fetch allowed count: {plan.auto_fetch_allowed_count}",
            "already reviewed skipped:",
        ]
    )
    lines.extend(f"- {asset_id}" for asset_id in plan.already_reviewed_skipped) if plan.already_reviewed_skipped else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in plan.warnings) if plan.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in plan.blockers) if plan.blockers else lines.append("- none")
    lines.extend(
        [
            "manual verification required: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build global core source collection plan report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    parser.add_argument("expander_config_path", nargs="?", default="jarvis/data/global_core_source_template_expander.example.json")
    parser.add_argument("planner_config_path", nargs="?", default="jarvis/data/global_core_source_collection_planner.example.json")
    args = parser.parse_args()
    print(
        build_global_core_source_collection_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
            args.expander_config_path,
            args.planner_config_path,
        )
    )


if __name__ == "__main__":
    main()
