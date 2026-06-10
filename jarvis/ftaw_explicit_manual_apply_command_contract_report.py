"""Readable report for FTAW explicit manual apply command contract."""

from __future__ import annotations

from pathlib import Path

from .ftaw_explicit_manual_apply_command_contract import build_ftaw_explicit_manual_apply_command_contract_from_files


def build_ftaw_explicit_manual_apply_command_contract_report(
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
) -> str:
    pack = build_ftaw_explicit_manual_apply_command_contract_from_files(
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
    lines = [
        "J.A.R.V.I.S. FTAW Explicit Manual Apply Command Contract Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"contract validation status: {pack.contract_validation_status}",
        f"apply gate status: {pack.apply_gate_status}",
        f"command file used: {pack.command_file_used}",
        f"command_type: {pack.command_type or 'none'}",
        f"asset_id match: {str(pack.asset_id_match).lower()}",
        f"current status match: {str(pack.current_status_match).lower()}",
        f"proposed status match: {str(pack.proposed_status_match).lower()}",
        f"dry_run fingerprint match: {str(pack.dry_run_fingerprint_match).lower()}",
        f"safety confirmations complete: {str(pack.safety_confirmations_complete).lower()}",
        f"explicit confirmation phrase match: {str(pack.explicit_confirmation_phrase_match).lower()}",
        f"replay protection fields present: {str(pack.replay_protection_fields_present).lower()}",
        f"apply_executed: {str(pack.apply_executed).lower()}",
        f"registry_file_written: {str(pack.registry_file_written).lower()}",
        f"approved_asset: {str(pack.approved_asset).lower()}",
        f"buy_signal: {str(pack.buy_signal).lower()}",
        "blocked reasons:",
    ]
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            "explicit manual apply command contract is not registry mutation.",
            "explicit manual apply command contract is not asset approval.",
            "explicit manual apply command contract is not verified evidence promotion.",
            "explicit manual apply command contract is not allocation advice.",
            "explicit manual apply command contract is not a buy/sell request.",
            "explicit manual apply command contract is not trade execution.",
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

    parser = argparse.ArgumentParser(description="Build FTAW explicit manual apply command contract report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_explicit_manual_apply_command_contract_report(
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
        )
    )


if __name__ == "__main__":
    main()
