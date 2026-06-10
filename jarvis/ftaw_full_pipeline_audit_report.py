"""FTAW full pipeline audit report.

This read-only audit summarizes the FTAW approval-control pipeline from source
facts through final registry apply execution preflight. It never mutates
registries, promotes evidence, approves assets, recommends allocations, creates
orders, or trades.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_candidate_readiness_pack import build_ftaw_candidate_readiness_pack
from .ftaw_explicit_manual_apply_command_contract import build_ftaw_explicit_manual_apply_command_contract_from_files
from .ftaw_human_approval_review_decision_recorder import build_ftaw_human_approval_review_decision_pack_from_files
from .ftaw_manual_approval_review_gate import build_ftaw_manual_approval_review_gate_from_files
from .ftaw_registry_apply_execution_review_pack import build_ftaw_registry_apply_execution_review_pack_from_files
from .ftaw_registry_update_apply_gate import build_ftaw_registry_update_apply_gate_from_files
from .ftaw_registry_update_dry_run_pack import build_ftaw_registry_update_dry_run_pack_from_files


@dataclass(frozen=True)
class FTAWFullPipelineAuditStage:
    stage_name: str
    status: str
    ready: bool
    blocked_reasons_count: int
    safety_flags: str


@dataclass(frozen=True)
class FTAWFullPipelineAuditPack:
    target_asset: str
    audit_status: str
    stage_count: int
    stages: tuple[FTAWFullPipelineAuditStage, ...]
    earliest_blocked_stage: str | None
    evidence_coverage_summary: str
    planned_promotion_coverage: str
    manual_approval_review_readiness: bool
    human_approval_review_decision_status: str
    registry_dry_run_status: str
    apply_gate_status: str
    explicit_command_contract_status: str
    execution_review_status: str
    final_preflight_ready: bool
    approved_asset: bool = False
    registry_mutation: bool = False
    verified_evidence_promotion: bool = False
    buy_signal: bool = False
    trade_execution: bool = False
    approvals_created: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _ready(status: str) -> bool:
    return status in {
        "READY",
        "identity_guard_passed",
        "READY_FOR_MANUAL_VERIFICATION",
        "DECISIONS_RECORDED",
        "PREVIEW_READY",
        "DRY_RUN_PLANNED",
        "READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION",
        "READY_FOR_MANUAL_APPROVAL_REVIEW",
        "READY_FOR_HUMAN_APPROVAL_REVIEW",
        "decision_recorded_for_registry_update_dry_run",
        "READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY",
        "READY_FOR_MANUAL_REGISTRY_APPLY_EXECUTION_REVIEW",
        "READY_FOR_FINAL_MANUAL_REGISTRY_APPLY_PREFLIGHT",
    }


def _stage(name: str, status: str, blocked_reasons_count: int = 0) -> FTAWFullPipelineAuditStage:
    return FTAWFullPipelineAuditStage(
        stage_name=name,
        status=status,
        ready=_ready(status),
        blocked_reasons_count=blocked_reasons_count,
        safety_flags="no approvals; no registry mutation; no recommendations; no orders; no trades",
    )


def _first_blocked(stages: tuple[FTAWFullPipelineAuditStage, ...]) -> str | None:
    for stage in stages:
        if not stage.ready:
            return stage.stage_name
    return None


def _audit_status(readiness_status: str, final_preflight_ready: bool) -> str:
    if final_preflight_ready:
        return "FINAL_PREFLIGHT_READY_SAFE"
    if readiness_status == "READY_FOR_MANUAL_VERIFIED_EVIDENCE_PROMOTION":
        return "PARTIAL_SAFE"
    return "BLOCKED_SAFE"


def build_ftaw_full_pipeline_audit_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
    approval_review_gate_config_path: str | Path,
    human_decision_config_path: str | Path,
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
) -> FTAWFullPipelineAuditPack:
    Path(full_pipeline_audit_config_path).read_text(encoding="utf-8")
    readiness = build_ftaw_candidate_readiness_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
    )
    approval_gate = build_ftaw_manual_approval_review_gate_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
    )
    human_decision = build_ftaw_human_approval_review_decision_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
    )
    registry_dry_run = build_ftaw_registry_update_dry_run_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
    )
    apply_gate = build_ftaw_registry_update_apply_gate_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
    )
    contract = build_ftaw_explicit_manual_apply_command_contract_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
    )
    execution = build_ftaw_registry_apply_execution_review_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
    )
    stages = (
        _stage("FTAW source fact intake", readiness.source_fact_status, int(readiness.source_fact_status not in {"READY"})),
        _stage("FTAW source identity guard", readiness.identity_guard_status, int(readiness.identity_guard_status != "identity_guard_passed")),
        _stage("FTAW identity-guarded verification queue", readiness.verification_queue_status, int(readiness.verification_queue_status != "READY_FOR_MANUAL_VERIFICATION")),
        _stage("FTAW manual verification decision recorder", readiness.manual_decision_status, int(readiness.manual_decision_status != "DECISIONS_RECORDED")),
        _stage("FTAW verified evidence preview bridge", readiness.preview_bridge_status, int(readiness.preview_bridge_status != "PREVIEW_READY")),
        _stage("FTAW verified evidence promotion dry-run pack", readiness.promotion_dry_run_status, int(readiness.promotion_dry_run_status != "DRY_RUN_PLANNED")),
        _stage("FTAW candidate readiness pack", readiness.candidate_readiness_status, len(readiness.blocked_reasons)),
        _stage("FTAW manual approval review gate", approval_gate.approval_review_gate_status, len(approval_gate.blocked_reasons)),
        _stage("FTAW human approval review decision recorder", human_decision.decision_status, human_decision.blocked_reason_count),
        _stage("FTAW registry update dry-run pack", registry_dry_run.registry_update_dry_run_status, len(registry_dry_run.blocked_reasons)),
        _stage("FTAW registry update apply gate", apply_gate.apply_gate_status, len(apply_gate.blocked_reasons)),
        _stage("FTAW explicit manual apply command contract", contract.contract_validation_status, len(contract.blocked_reasons)),
        _stage("FTAW registry apply execution review pack", execution.execution_review_status, len(execution.blocked_reasons)),
    )
    final_ready = execution.execution_review_status == "READY_FOR_FINAL_MANUAL_REGISTRY_APPLY_PREFLIGHT"
    planned = readiness.planned_promotion_evidence_types_count
    required = readiness.required_evidence_types_count
    return FTAWFullPipelineAuditPack(
        target_asset=readiness.target_asset,
        audit_status=_audit_status(readiness.candidate_readiness_status, final_ready),
        stage_count=len(stages),
        stages=stages,
        earliest_blocked_stage=_first_blocked(stages),
        evidence_coverage_summary=f"{planned} of {required} required evidence types have dry-run planned promotions.",
        planned_promotion_coverage=f"{planned} / {required}",
        manual_approval_review_readiness=readiness.ready_for_manual_approval_review,
        human_approval_review_decision_status=human_decision.decision_status,
        registry_dry_run_status=registry_dry_run.registry_update_dry_run_status,
        apply_gate_status=apply_gate.apply_gate_status,
        explicit_command_contract_status=contract.contract_validation_status,
        execution_review_status=execution.execution_review_status,
        final_preflight_ready=final_ready,
        approved_asset=False,
        registry_mutation=False,
        verified_evidence_promotion=False,
        buy_signal=False,
        trade_execution=False,
        approvals_created=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_full_pipeline_audit_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
    approval_review_gate_config_path: str | Path,
    human_decision_config_path: str | Path,
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
) -> str:
    pack = build_ftaw_full_pipeline_audit_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
        full_pipeline_audit_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Full Pipeline Audit Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"audit status: {pack.audit_status}",
        f"stage count: {pack.stage_count}",
        f"earliest blocked stage: {pack.earliest_blocked_stage or 'none'}",
        f"evidence coverage summary: {pack.evidence_coverage_summary}",
        f"planned promotion coverage: {pack.planned_promotion_coverage}",
        f"manual approval review readiness: {str(pack.manual_approval_review_readiness).lower()}",
        f"human approval review decision status: {pack.human_approval_review_decision_status}",
        f"registry dry-run status: {pack.registry_dry_run_status}",
        f"apply gate status: {pack.apply_gate_status}",
        f"explicit command contract status: {pack.explicit_command_contract_status}",
        f"execution review status: {pack.execution_review_status}",
        f"final preflight ready: {str(pack.final_preflight_ready).lower()}",
        f"approved_asset: {str(pack.approved_asset).lower()}",
        f"registry_mutation: {str(pack.registry_mutation).lower()}",
        f"verified_evidence_promotion: {str(pack.verified_evidence_promotion).lower()}",
        f"buy_signal: {str(pack.buy_signal).lower()}",
        f"trade_execution: {str(pack.trade_execution).lower()}",
        "stage table:",
        "stage name | status | ready | blocked reasons count | safety flags",
    ]
    for stage in pack.stages:
        lines.append(
            f"{stage.stage_name} | {stage.status} | {str(stage.ready).lower()} | "
            f"{stage.blocked_reasons_count} | {stage.safety_flags}"
        )
    lines.extend(
        [
            "full pipeline audit is not asset approval.",
            "full pipeline audit is not registry mutation.",
            "full pipeline audit is not verified evidence promotion.",
            "full pipeline audit is not allocation advice.",
            "full pipeline audit is not a buy/sell request.",
            "full pipeline audit is not trade execution.",
            "final preflight readiness still requires a separate future executor that does not exist in this version.",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW full pipeline audit report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    parser.add_argument("promotion_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json")
    parser.add_argument("readiness_config_path", nargs="?", default="jarvis/data/ftaw_candidate_readiness_pack.example.json")
    parser.add_argument("approval_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_manual_approval_review_gate.example.json")
    parser.add_argument("human_decision_config_path", nargs="?", default="jarvis/data/ftaw_human_approval_review_decision_recorder.example.json")
    parser.add_argument("registry_update_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_dry_run_pack.example.json")
    parser.add_argument("registry_update_apply_gate_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_apply_gate.example.json")
    parser.add_argument("explicit_manual_apply_command_config_path", nargs="?", default="jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json")
    parser.add_argument("execution_review_config_path", nargs="?", default="jarvis/data/ftaw_registry_apply_execution_review_pack.example.json")
    parser.add_argument("full_pipeline_audit_config_path", nargs="?", default="jarvis/data/ftaw_full_pipeline_audit_report.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_full_pipeline_audit_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
            args.preview_bridge_config_path,
            args.promotion_dry_run_config_path,
            args.readiness_config_path,
            args.approval_review_gate_config_path,
            args.human_decision_config_path,
            args.registry_update_dry_run_config_path,
            args.registry_update_apply_gate_config_path,
            args.explicit_manual_apply_command_config_path,
            args.execution_review_config_path,
            args.full_pipeline_audit_config_path,
        )
    )


if __name__ == "__main__":
    main()
