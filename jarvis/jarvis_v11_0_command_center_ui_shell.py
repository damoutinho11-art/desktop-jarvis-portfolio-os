"""J.A.R.V.I.S. v11.0 command center UI shell.

This stage renders the v10.1 unified operator runtime into a local static HTML
command-center shell.

It does not rebuild the operator runtime.
It does not rebuild recommendations, evidence packs, dashboards, action briefs,
data refresh, or voice.

Safety boundary:
- static local UI only;
- no web server started;
- no network listener;
- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- final real-world buy remains Diogo's only manual action.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jarvis_v10_1_unified_operator_runtime import (
    STATUS_READY as V10_1_STATUS_READY,
    audit_v10_1_unified_operator_runtime,
)


STATUS_READY = "JARVIS_V11_0_COMMAND_CENTER_UI_SHELL_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V11_0_COMMAND_CENTER_UI_SHELL_BLOCKED_SAFE"

UI_SHELL_READY = "COMMAND_CENTER_UI_SHELL_READY"
UI_SHELL_BLOCKED = "COMMAND_CENTER_UI_SHELL_BLOCKED"

NEXT_STAGE = "v12_0_voice_operator_interface_boundary"

DEFAULT_UI_OUTPUT_PATH = "jarvis/local/ui/jarvis_command_center.html"


@dataclass(frozen=True)
class CommandCenterUiSection:
    section_id: str
    title: str
    ready: bool
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "ready": self.ready,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class CommandCenterUiShellResult:
    status: str
    ui_shell_status: str
    recommended_next_stage: str
    runtime_status: str
    selected_candidate_id: str
    selected_sleeve_id: str
    output_path: str
    html_rendered: bool
    html_written: bool
    section_count: int
    ready_section_count: int
    blocked_section_count: int
    component_count: int
    voice_summary_ready: bool
    voice_interface_available: bool
    ui_sections: tuple[CommandCenterUiSection, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    command_center_ui_shell_ready: bool
    static_local_html_only: bool
    web_server_started: bool
    network_listener_started: bool
    external_asset_loading: bool
    runtime_rebuilt: bool
    recommendation_rebuilt: bool
    evidence_rebuilt: bool
    data_refresh_rebuilt: bool
    voice_interface_built: bool
    buy_button_disabled: bool
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
            "ui_shell_status": self.ui_shell_status,
            "recommended_next_stage": self.recommended_next_stage,
            "runtime_status": self.runtime_status,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "output_path": self.output_path,
            "html_rendered": self.html_rendered,
            "html_written": self.html_written,
            "section_count": self.section_count,
            "ready_section_count": self.ready_section_count,
            "blocked_section_count": self.blocked_section_count,
            "component_count": self.component_count,
            "voice_summary_ready": self.voice_summary_ready,
            "voice_interface_available": self.voice_interface_available,
            "ui_sections": [section.to_dict() for section in self.ui_sections],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "command_center_ui_shell_ready": self.command_center_ui_shell_ready,
            "static_local_html_only": self.static_local_html_only,
            "web_server_started": self.web_server_started,
            "network_listener_started": self.network_listener_started,
            "external_asset_loading": self.external_asset_loading,
            "runtime_rebuilt": self.runtime_rebuilt,
            "recommendation_rebuilt": self.recommendation_rebuilt,
            "evidence_rebuilt": self.evidence_rebuilt,
            "data_refresh_rebuilt": self.data_refresh_rebuilt,
            "voice_interface_built": self.voice_interface_built,
            "buy_button_disabled": self.buy_button_disabled,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def _get_bool(obj: Any, name: str, default: bool = False) -> bool:
    return bool(getattr(obj, name, default))


def _get_text(obj: Any, name: str, default: str = "") -> str:
    value = getattr(obj, name, default)
    return str(value if value is not None else default)


def _escape(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def build_command_center_ui_sections(runtime_result: Any) -> tuple[CommandCenterUiSection, ...]:
    return (
        CommandCenterUiSection(
            section_id="data_refresh",
            title="Data Refresh",
            ready=_get_bool(runtime_result, "data_refresh_integrated"),
            summary=(
                f"manifest_loaded={_get_bool(runtime_result, 'data_source_manifest_loaded')}; "
                f"autonomous_refresh_ready={_get_bool(runtime_result, 'autonomous_refresh_ready')}; "
                f"raw_public_data_refreshed={_get_bool(runtime_result, 'raw_public_data_refreshed')}; "
                f"recommendation_quality_current_data={_get_bool(runtime_result, 'recommendation_quality_current_data')}"
            ),
        ),
        CommandCenterUiSection(
            section_id="evidence",
            title="Evidence Pack",
            ready=_get_bool(runtime_result, "evidence_pack_integrated"),
            summary=f"status={_get_text(runtime_result, 'evidence_pack_status')}",
        ),
        CommandCenterUiSection(
            section_id="recommendation",
            title="Recommendation",
            ready=_get_bool(runtime_result, "recommendation_integrated"),
            summary=(
                f"status={_get_text(runtime_result, 'recommendation_status')}; "
                f"dashboard_status={_get_text(runtime_result, 'recommendation_dashboard_status')}"
            ),
        ),
        CommandCenterUiSection(
            section_id="dashboard",
            title="Dashboards",
            ready=_get_bool(runtime_result, "dashboard_integrated"),
            summary=f"public_market_dashboard_status={_get_text(runtime_result, 'public_market_dashboard_status')}",
        ),
        CommandCenterUiSection(
            section_id="action_brief",
            title="Action Brief",
            ready=_get_bool(runtime_result, "action_brief_integrated"),
            summary=f"status={_get_text(runtime_result, 'action_brief_status')}",
        ),
        CommandCenterUiSection(
            section_id="voice_summary",
            title="Voice-Ready Summary",
            ready=_get_bool(runtime_result, "voice_ready_summary_integrated")
            and _get_bool(runtime_result, "voice_summary_ready"),
            summary=(
                "voice-ready text summary exists; full voice interface is not built yet"
                if not _get_bool(runtime_result, "voice_interface_available")
                else "voice interface available"
            ),
        ),
        CommandCenterUiSection(
            section_id="manual_buy_boundary",
            title="Manual Final Buy Boundary",
            ready=_get_bool(runtime_result, "final_user_buy_action_required")
            and _get_bool(runtime_result, "broker_connection_forbidden")
            and _get_bool(runtime_result, "order_placement_forbidden")
            and _get_bool(runtime_result, "no_trades_executed"),
            summary="J.A.R.V.I.S. prepares; Diogo performs the final real-world buy outside the system.",
        ),
    )


def render_command_center_html(runtime_result: Any) -> str:
    sections = build_command_center_ui_sections(runtime_result)
    selected_candidate_id = _get_text(runtime_result, "selected_candidate_id", "unknown")
    selected_sleeve_id = _get_text(runtime_result, "selected_sleeve_id", "unknown")
    status = _get_text(runtime_result, "status", "unknown")
    runtime_status = _get_text(runtime_result, "runtime_status", "unknown")
    voice_summary = _get_text(runtime_result, "voice_summary", "")
    components = tuple(getattr(runtime_result, "components", ()) or ())

    section_cards = "\n".join(
        f"""
        <article class="card {'ready' if section.ready else 'blocked'}">
          <div class="card-kicker">{_escape(section.section_id)}</div>
          <h3>{_escape(section.title)}</h3>
          <p>{_escape(section.summary)}</p>
          <span class="pill">{'READY' if section.ready else 'WATCH'}</span>
        </article>
        """
        for section in sections
    )

    component_rows = "\n".join(
        f"""
        <tr>
          <td>{_escape(getattr(component, 'component_id', 'unknown'))}</td>
          <td>{_escape(getattr(component, 'status', 'unknown'))}</td>
          <td>{'Yes' if bool(getattr(component, 'ready', False)) else 'No'}</td>
          <td>{_escape(getattr(component, 'summary', ''))}</td>
        </tr>
        """
        for component in components
    )

    if not component_rows:
        component_rows = "<tr><td colspan='4'>No runtime components supplied.</td></tr>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>J.A.R.V.I.S. Command Center</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #06070a;
      --panel: #10141d;
      --panel-2: #151b26;
      --text: #eef2ff;
      --muted: #aeb8ca;
      --line: #2a3344;
      --ready: #4ade80;
      --watch: #facc15;
      --danger: #fb7185;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: radial-gradient(circle at top left, #172033, var(--bg) 42%);
      color: var(--text);
    }}
    header {{
      padding: 36px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 12px;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: 36px;
    }}
    .subtitle {{
      color: var(--muted);
      max-width: 920px;
      line-height: 1.6;
    }}
    main {{
      padding: 28px 36px 48px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin: 22px 0;
    }}
    .card {{
      background: linear-gradient(180deg, var(--panel), var(--panel-2));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 18px 40px rgba(0,0,0,.22);
    }}
    .card.ready {{ border-color: rgba(74, 222, 128, .5); }}
    .card.blocked {{ border-color: rgba(250, 204, 21, .55); }}
    .card-kicker {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .14em;
    }}
    h2 {{ margin-top: 34px; }}
    h3 {{ margin: 8px 0; }}
    p {{ color: var(--muted); line-height: 1.55; }}
    .pill {{
      display: inline-block;
      margin-top: 8px;
      padding: 5px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      font-size: 12px;
    }}
    .ready .pill {{ color: var(--ready); }}
    .blocked .pill {{ color: var(--watch); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
    }}
    th, td {{
      padding: 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    .voice {{
      background: #0d1320;
      border-left: 4px solid var(--ready);
      padding: 18px;
      border-radius: 14px;
      color: var(--text);
    }}
    .manual {{
      border-color: rgba(251, 113, 133, .65);
    }}
    .disabled-action {{
      width: 100%;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--danger);
      color: var(--danger);
      background: transparent;
      font-weight: 700;
      cursor: not-allowed;
    }}
    footer {{
      color: var(--muted);
      padding: 24px 36px;
      border-top: 1px solid var(--line);
    }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">J.A.R.V.I.S. Portfolio OS</div>
    <h1>Command Center</h1>
    <p class="subtitle">
      Runtime: {_escape(runtime_status)}. Status: {_escape(status)}.
      Selected candidate: <strong>{_escape(selected_candidate_id)}</strong>.
      Sleeve: <strong>{_escape(selected_sleeve_id)}</strong>.
    </p>
  </header>

  <main>
    <section>
      <h2>Operator Overview</h2>
      <div class="grid">
        {section_cards}
      </div>
    </section>

    <section>
      <h2>Runtime Components</h2>
      <table>
        <thead>
          <tr>
            <th>Component</th>
            <th>Status</th>
            <th>Ready</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {component_rows}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Voice-Ready Summary</h2>
      <p class="voice">{_escape(voice_summary)}</p>
    </section>

    <section>
      <h2>Final Action Boundary</h2>
      <article class="card manual">
        <h3>No execution inside J.A.R.V.I.S.</h3>
        <p>
          J.A.R.V.I.S. may refresh data, validate readiness, assemble evidence,
          prepare recommendations, render dashboards, and generate summaries.
          The final real-world buy remains manual and outside the system.
        </p>
        <button class="disabled-action" disabled>No broker / no order / no trade</button>
      </article>
    </section>
  </main>

  <footer>
    Static local UI shell. No server. No broker connection. No order placement. No trade execution.
  </footer>
</body>
</html>
"""


def write_command_center_html(
    html_text: str,
    output_path: str | Path = DEFAULT_UI_OUTPUT_PATH,
    *,
    root: str | Path = ".",
) -> Path:
    target = Path(root) / output_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_text, encoding="utf-8")
    return target


def audit_v11_0_command_center_ui_shell(
    *,
    runtime_result: Any | None = None,
    write_file: bool = False,
    output_path: str | Path = DEFAULT_UI_OUTPUT_PATH,
    root: str | Path = ".",
) -> CommandCenterUiShellResult:
    effective_runtime = runtime_result or audit_v10_1_unified_operator_runtime()
    sections = build_command_center_ui_sections(effective_runtime)
    rendered_html = render_command_center_html(effective_runtime)

    blockers: list[str] = []
    warnings: list[str] = [
        "v11.0 is a static local UI shell over v10.1.",
        "It does not rebuild the unified operator runtime.",
        "It does not start a web server.",
        "It does not connect to brokers or create execution actions.",
        "The final real-world buy remains manual and outside J.A.R.V.I.S.",
    ]

    runtime_status = _get_text(effective_runtime, "status", "")
    if runtime_status != V10_1_STATUS_READY:
        blockers.append(f"v10.1 unified operator runtime is not ready: {runtime_status}")

    component_count = int(getattr(effective_runtime, "component_count", 0) or 0)
    if component_count <= 0:
        blockers.append("No runtime components available for UI rendering.")

    if not rendered_html.strip():
        blockers.append("Command-center HTML was not rendered.")

    if not _get_bool(effective_runtime, "final_user_buy_action_required", True):
        blockers.append("Final user buy action must remain required.")
    if not _get_bool(effective_runtime, "broker_connection_forbidden", True):
        blockers.append("Broker connection must remain forbidden.")
    if not _get_bool(effective_runtime, "order_placement_forbidden", True):
        blockers.append("Order placement must remain forbidden.")
    if not _get_bool(effective_runtime, "no_trades_executed", True):
        blockers.append("Trade execution must remain forbidden.")

    written = False
    if write_file and not blockers:
        write_command_center_html(rendered_html, output_path, root=root)
        written = True

    ready_sections = sum(1 for section in sections if section.ready)
    blocked_sections = len(sections) - ready_sections

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return CommandCenterUiShellResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        ui_shell_status=UI_SHELL_READY if ready else UI_SHELL_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        runtime_status=runtime_status,
        selected_candidate_id=_get_text(effective_runtime, "selected_candidate_id", "unknown"),
        selected_sleeve_id=_get_text(effective_runtime, "selected_sleeve_id", "unknown"),
        output_path=str(output_path),
        html_rendered=bool(rendered_html.strip()),
        html_written=written,
        section_count=len(sections),
        ready_section_count=ready_sections,
        blocked_section_count=blocked_sections,
        component_count=component_count,
        voice_summary_ready=_get_bool(effective_runtime, "voice_summary_ready"),
        voice_interface_available=_get_bool(effective_runtime, "voice_interface_available"),
        ui_sections=sections,
        blockers=unique_blockers,
        warnings=unique_warnings,
        command_center_ui_shell_ready=ready,
        static_local_html_only=True,
        web_server_started=False,
        network_listener_started=False,
        external_asset_loading=False,
        runtime_rebuilt=False,
        recommendation_rebuilt=False,
        evidence_rebuilt=False,
        data_refresh_rebuilt=False,
        voice_interface_built=False,
        buy_button_disabled=True,
        final_user_buy_action_required=True,
        buy_request_deferred=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
    )
