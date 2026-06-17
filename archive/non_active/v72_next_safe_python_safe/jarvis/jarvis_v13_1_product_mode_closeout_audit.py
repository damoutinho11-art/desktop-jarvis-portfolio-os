"""J.A.R.V.I.S. v13.1 product mode closeout audit.

This stage closes out the current product-mode stack:

- v10.0 autonomous public data refresh runtime;
- v10.1 unified operator runtime;
- v11.0 command-center UI shell;
- v12.0 voice operator boundary;
- v12.1 local typed voice I/O shell;
- v13.0 single command operator launcher.

It does not add features.

It confirms that the launcher operates as a safe local product surface:
runtime + UI + typed voice shell + blocked execution command.

Safety boundary:
- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- final real-world buy remains Diogo's manual action outside J.A.R.V.I.S.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v13_0_single_command_operator_launcher import (
    STATUS_READY as V13_0_STATUS_READY,
    SingleCommandOperatorLauncherResult,
    run_v13_0_single_command_operator_launcher,
)


STATUS_READY = "JARVIS_V13_1_PRODUCT_MODE_CLOSEOUT_AUDIT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V13_1_PRODUCT_MODE_CLOSEOUT_AUDIT_BLOCKED_SAFE"

CLOSEOUT_READY = "PRODUCT_MODE_CLOSEOUT_READY"
CLOSEOUT_BLOCKED = "PRODUCT_MODE_CLOSEOUT_BLOCKED"

NEXT_STAGE = "release_tag_product_mode_v13_1"

BLOCKED_EXECUTION_COMMAND = "Jarvis, buy BTC now."


@dataclass(frozen=True)
class ProductModeCloseoutAuditResult:
    status: str
    closeout_status: str
    recommended_next_stage: str
    launcher_status: str
    runtime_status: str
    ui_shell_status: str
    voice_shell_status: str
    selected_candidate_id: str
    selected_sleeve_id: str
    output_path: str
    ui_html_written: bool
    blocked_execution_command: str
    blocked_execution_command_processed: bool
    blocked_execution_command_blocked: bool
    blocked_execution_command_output: str
    blocker_count: int
    warning_count: int
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    product_mode_closeout_ready: bool
    launcher_ready: bool
    runtime_ready: bool
    ui_shell_ready: bool
    voice_shell_ready: bool
    local_ui_path_available: bool
    typed_voice_shell_available: bool
    blocked_buy_command_verified: bool
    no_feature_added: bool
    no_strategy_rebuild: bool
    no_recommendation_rebuild: bool
    no_evidence_rebuild: bool
    no_data_refresh_rebuild: bool
    no_ui_rebuild: bool
    no_voice_rebuild: bool
    static_local_html_only: bool
    typed_voice_shell_only: bool
    no_web_server_started: bool
    no_network_listener_started: bool
    no_external_asset_loading: bool
    no_microphone: bool
    no_speech_to_text: bool
    no_text_to_speech: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "closeout_status": self.closeout_status,
            "recommended_next_stage": self.recommended_next_stage,
            "launcher_status": self.launcher_status,
            "runtime_status": self.runtime_status,
            "ui_shell_status": self.ui_shell_status,
            "voice_shell_status": self.voice_shell_status,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "output_path": self.output_path,
            "ui_html_written": self.ui_html_written,
            "blocked_execution_command": self.blocked_execution_command,
            "blocked_execution_command_processed": self.blocked_execution_command_processed,
            "blocked_execution_command_blocked": self.blocked_execution_command_blocked,
            "blocked_execution_command_output": self.blocked_execution_command_output,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "product_mode_closeout_ready": self.product_mode_closeout_ready,
            "launcher_ready": self.launcher_ready,
            "runtime_ready": self.runtime_ready,
            "ui_shell_ready": self.ui_shell_ready,
            "voice_shell_ready": self.voice_shell_ready,
            "local_ui_path_available": self.local_ui_path_available,
            "typed_voice_shell_available": self.typed_voice_shell_available,
            "blocked_buy_command_verified": self.blocked_buy_command_verified,
            "no_feature_added": self.no_feature_added,
            "no_strategy_rebuild": self.no_strategy_rebuild,
            "no_recommendation_rebuild": self.no_recommendation_rebuild,
            "no_evidence_rebuild": self.no_evidence_rebuild,
            "no_data_refresh_rebuild": self.no_data_refresh_rebuild,
            "no_ui_rebuild": self.no_ui_rebuild,
            "no_voice_rebuild": self.no_voice_rebuild,
            "static_local_html_only": self.static_local_html_only,
            "typed_voice_shell_only": self.typed_voice_shell_only,
            "no_web_server_started": self.no_web_server_started,
            "no_network_listener_started": self.no_network_listener_started,
            "no_external_asset_loading": self.no_external_asset_loading,
            "no_microphone": self.no_microphone,
            "no_speech_to_text": self.no_speech_to_text,
            "no_text_to_speech": self.no_text_to_speech,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def _get_text(obj: Any, name: str, default: str = "") -> str:
    value = getattr(obj, name, default)
    return str(value if value is not None else default)


def _get_bool(obj: Any, name: str, default: bool = False) -> bool:
    return bool(getattr(obj, name, default))


def audit_v13_1_product_mode_closeout_audit(
    *,
    launcher_result: SingleCommandOperatorLauncherResult | None = None,
    write_ui: bool = False,
) -> ProductModeCloseoutAuditResult:
    launcher = launcher_result or run_v13_0_single_command_operator_launcher(
        write_ui=write_ui,
        voice_command_text=BLOCKED_EXECUTION_COMMAND,
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v13.1 is a product-mode closeout audit only.",
        "It adds no new product feature.",
        "It verifies the existing v10.1/v11.0/v12.1/v13.0 product stack.",
        "A release tag should be created after this audit and final validation.",
    ]

    launcher_status = _get_text(launcher, "status")
    runtime_status = _get_text(launcher, "runtime_status")
    ui_shell_status = _get_text(launcher, "ui_shell_status")
    voice_shell_status = _get_text(launcher, "voice_shell_status")

    launcher_ready = launcher_status == V13_0_STATUS_READY
    runtime_ready = bool(_get_bool(launcher, "runtime_launched"))
    ui_shell_ready = bool(_get_bool(launcher, "ui_shell_launched"))
    voice_shell_ready = bool(_get_bool(launcher, "voice_shell_launched"))

    if not launcher_ready:
        blockers.append(f"v13.0 launcher is not ready: {launcher_status}")
    if not runtime_ready:
        blockers.append(f"v10.1 runtime did not launch cleanly: {runtime_status}")
    if not ui_shell_ready:
        blockers.append(f"v11.0 UI shell did not launch cleanly: {ui_shell_status}")
    if not voice_shell_ready:
        blockers.append(f"v12.1 voice shell did not launch cleanly: {voice_shell_status}")

    output_path = _get_text(launcher, "output_path")
    local_ui_path_available = output_path.endswith("jarvis_command_center.html")
    if not local_ui_path_available:
        blockers.append(f"Local UI output path is not available: {output_path}")

    voice_command = getattr(launcher, "voice_command", None)
    blocked_command_processed = bool(_get_bool(launcher, "voice_command_processed"))
    blocked_command_blocked = bool(getattr(voice_command, "blocked", False)) if voice_command else False
    blocked_command_output = _get_text(voice_command, "output_text") if voice_command else ""

    blocked_buy_command_verified = (
        blocked_command_processed
        and blocked_command_blocked
        and "No execution action was taken" in blocked_command_output
    )

    if not blocked_buy_command_verified:
        blockers.append("Blocked buy command was not verified by the launcher.")

    safety_checks = {
        "static local HTML only": _get_bool(launcher, "static_local_html_only"),
        "typed voice shell only": _get_bool(launcher, "typed_voice_shell_only"),
        "no web server started": _get_bool(launcher, "no_web_server_started"),
        "no network listener started": _get_bool(launcher, "no_network_listener_started"),
        "no external asset loading": _get_bool(launcher, "no_external_asset_loading"),
        "no microphone": _get_bool(launcher, "no_microphone"),
        "no speech to text": _get_bool(launcher, "no_speech_to_text"),
        "no text to speech": _get_bool(launcher, "no_text_to_speech"),
        "final user buy action required": _get_bool(launcher, "final_user_buy_action_required"),
        "buy request deferred": _get_bool(launcher, "buy_request_deferred"),
        "broker connection forbidden": _get_bool(launcher, "broker_connection_forbidden"),
        "order placement forbidden": _get_bool(launcher, "order_placement_forbidden"),
        "no trades executed": _get_bool(launcher, "no_trades_executed"),
        "credentials forbidden": _get_bool(launcher, "credentials_forbidden"),
        "private account data ingestion forbidden": _get_bool(launcher, "private_account_data_ingestion_forbidden"),
    }

    for label, passed in safety_checks.items():
        if not passed:
            blockers.append(f"Safety check failed: {label}")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return ProductModeCloseoutAuditResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        closeout_status=CLOSEOUT_READY if ready else CLOSEOUT_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        launcher_status=launcher_status,
        runtime_status=runtime_status,
        ui_shell_status=ui_shell_status,
        voice_shell_status=voice_shell_status,
        selected_candidate_id=_get_text(launcher, "selected_candidate_id", "unknown"),
        selected_sleeve_id=_get_text(launcher, "selected_sleeve_id", "unknown"),
        output_path=output_path,
        ui_html_written=_get_bool(launcher, "ui_html_written"),
        blocked_execution_command=BLOCKED_EXECUTION_COMMAND,
        blocked_execution_command_processed=blocked_command_processed,
        blocked_execution_command_blocked=blocked_command_blocked,
        blocked_execution_command_output=blocked_command_output,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blockers=unique_blockers,
        warnings=unique_warnings,
        product_mode_closeout_ready=ready,
        launcher_ready=launcher_ready,
        runtime_ready=runtime_ready,
        ui_shell_ready=ui_shell_ready,
        voice_shell_ready=voice_shell_ready,
        local_ui_path_available=local_ui_path_available,
        typed_voice_shell_available=_get_bool(launcher, "typed_voice_shell_only"),
        blocked_buy_command_verified=blocked_buy_command_verified,
        no_feature_added=True,
        no_strategy_rebuild=True,
        no_recommendation_rebuild=True,
        no_evidence_rebuild=True,
        no_data_refresh_rebuild=True,
        no_ui_rebuild=True,
        no_voice_rebuild=True,
        static_local_html_only=_get_bool(launcher, "static_local_html_only"),
        typed_voice_shell_only=_get_bool(launcher, "typed_voice_shell_only"),
        no_web_server_started=_get_bool(launcher, "no_web_server_started"),
        no_network_listener_started=_get_bool(launcher, "no_network_listener_started"),
        no_external_asset_loading=_get_bool(launcher, "no_external_asset_loading"),
        no_microphone=_get_bool(launcher, "no_microphone"),
        no_speech_to_text=_get_bool(launcher, "no_speech_to_text"),
        no_text_to_speech=_get_bool(launcher, "no_text_to_speech"),
        final_user_buy_action_required=_get_bool(launcher, "final_user_buy_action_required"),
        buy_request_deferred=_get_bool(launcher, "buy_request_deferred"),
        broker_connection_forbidden=_get_bool(launcher, "broker_connection_forbidden"),
        order_placement_forbidden=_get_bool(launcher, "order_placement_forbidden"),
        no_trades_executed=_get_bool(launcher, "no_trades_executed"),
        credentials_forbidden=_get_bool(launcher, "credentials_forbidden"),
        private_account_data_ingestion_forbidden=_get_bool(launcher, "private_account_data_ingestion_forbidden"),
    )
