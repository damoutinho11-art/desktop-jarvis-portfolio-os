from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from jarvis.runtime.chat_interface_contract import (
    build_chat_interface_contract_result,
    format_chat_reply,
)
from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.voice_briefing import build_voice_briefing_result

STATUS_READY = "JARVIS_V107_0_BROWSER_CHAT_UX_POLISH_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V107_0_BROWSER_CHAT_UX_POLISH_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/local_server_smoke_latest.json"
MAX_JSON_BODY_BYTES = 32768

ROUTES = {
    "GET /health": "local server health and safety metadata",
    "GET /dashboard": "generated local static dashboard HTML artifact",
    "GET /chat": "local browser chat page backed by POST /api/chat",
    "GET /api/status": "read-only product API payload",
    "GET /api/finance-intelligence": "read-only finance intelligence core payload",
    "GET /api/voice-briefing": "read-only voice briefing text payload",
    "POST /api/chat": "read-only chat reply payload",
}


@dataclass(frozen=True)
class LocalServerSmokeResult:
    status: str
    current_date: str
    local_server_ready: bool
    host: str
    port: int
    routes: dict[str, str]
    manual_only: bool
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    chat_smoke_ready: bool
    dashboard_smoke_ready: bool
    product_api_smoke_ready: bool
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return value


def _json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, html: str, status: int = 200) -> None:
    body = html.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _error_response(handler: BaseHTTPRequestHandler, message: str, status: int = 404) -> None:
    _json_response(handler, {"error": message, "status": status}, status=status)


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError:
        length = 0

    if length <= 0:
        return {}
    if length > MAX_JSON_BODY_BYTES:
        return {"_error": "request_body_too_large"}

    body = handler.rfile.read(length).decode("utf-8")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {}

    return payload if isinstance(payload, dict) else {}


def _health_payload(*, host: str, port: int, current_date: str) -> dict[str, Any]:
    return {
        "status": STATUS_READY,
        "current_date": current_date,
        "local_server_ready": True,
        "host": host,
        "port": port,
        "routes": ROUTES,
        "manual_only": True,
        "execution_forbidden": True,
        "broker_connection": False,
        "credentials_used": False,
        "order_created": False,
        "trade_executed": False,
        "warning": "local server shell is read-only and exposes no execution path; /dashboard may generate a local HTML artifact",
    }


def _dashboard_html(*, current_date: str) -> str:
    dashboard_path = Path("outputs/dashboard_latest.html")
    build_dashboard_contract_result(current_date=current_date, write_dashboard=True)
    if dashboard_path.exists():
        return dashboard_path.read_text(encoding="utf-8")
    return "<!doctype html><html><body><h1>J.A.R.V.I.S. dashboard unavailable</h1></body></html>"


def render_chat_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>J.A.R.V.I.S. Local Chat</title>
  <style>
    :root { color-scheme: dark; }
    body { font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; background: #0f1218; color: #f4f7fb; }
    main { max-width: 960px; margin: 0 auto; padding: 32px 20px 48px; }
    .shell { display: grid; gap: 18px; }
    .card { background: #171b24; border: 1px solid #2a3343; border-radius: 8px; padding: 22px; box-shadow: 0 18px 40px rgba(0,0,0,.26); }
    .hero-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
    h1 { margin: 0 0 8px; font-size: 32px; letter-spacing: 0; }
    h2 { margin: 0 0 12px; font-size: 17px; letter-spacing: 0; }
    .muted { color: #aeb8c8; line-height: 1.55; }
    .safety { margin: 18px 0; padding: 14px 16px; border-radius: 8px; background: #18261f; border: 1px solid #365c45; color: #dcf8e6; }
    .badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
    .badge { border: 1px solid #3b4658; background: #111722; color: #d7e2f4; border-radius: 999px; padding: 7px 10px; font-size: 13px; font-weight: 700; }
    .badge.safe { border-color: #3c714e; color: #dffbe9; background: #122117; }
    .preset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(178px, 1fr)); gap: 10px; margin: 16px 0; }
    .preset { border: 1px solid #3a4659; background: #101622; color: #eef4ff; border-radius: 8px; padding: 11px 12px; font-weight: 700; cursor: pointer; text-align: left; }
    .preset:hover, .preset:focus { border-color: #7898d8; outline: none; }
    textarea { width: 100%; min-height: 122px; border-radius: 8px; border: 1px solid #3a4150; background: #0d1119; color: #f2f4f8; padding: 14px; font-size: 16px; box-sizing: border-box; line-height: 1.45; }
    .actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 12px; }
    .primary { border: 0; border-radius: 8px; padding: 12px 18px; font-weight: 800; cursor: pointer; background: #f2f6ff; color: #101216; }
    .voice-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: 12px; }
    .voice-button { border: 1px solid #476184; border-radius: 8px; padding: 10px 12px; background: #111a28; color: #eef4ff; font-weight: 800; cursor: pointer; }
    .voice-button:hover, .voice-button:focus { border-color: #91ace0; outline: none; }
    .voice-status { min-height: 22px; color: #aeb8c8; font-size: 14px; line-height: 1.45; }
    button:disabled { opacity: .55; cursor: not-allowed; }
    .dashboard-link { display: inline-block; border: 1px solid #5876aa; border-radius: 8px; padding: 11px 14px; color: #e7f0ff; text-decoration: none; font-weight: 800; }
    .reply-card { background: #101622; border: 1px solid #303b4d; border-radius: 8px; padding: 16px; min-height: 168px; }
    .reply-head { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 10px; color: #c9d4e5; font-weight: 800; }
    .loading { color: #ffd98a; visibility: hidden; }
    .loading.active { visibility: visible; }
    pre { white-space: pre-wrap; margin: 0; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; line-height: 1.5; color: #f5f8ff; }
    .links a { color: #d8e7ff; margin-right: 14px; }
    .jarvis-orb { position: relative; width: 86px; height: 86px; flex: 0 0 auto; border-radius: 999px; background: radial-gradient(circle at 38% 32%, #f8fbff 0 7%, #7ee7d4 10% 24%, #2e8ccc 38%, #17233a 68%); box-shadow: 0 0 24px rgba(126,231,212,.28), inset 0 0 22px rgba(255,255,255,.14); overflow: hidden; animation: orbPulse 3.6s ease-in-out infinite; }
    .jarvis-orb::before, .jarvis-orb::after { content: ""; position: absolute; inset: 10px; border-radius: inherit; border: 1px solid rgba(248,251,255,.28); animation: orbRing 2.6s ease-in-out infinite; }
    .jarvis-orb::after { inset: 20px; border-color: rgba(255,217,138,.36); animation-delay: .55s; }
    .orb-core { position: absolute; inset: 31px; border-radius: 999px; background: #f8fbff; box-shadow: 0 0 18px rgba(255,255,255,.8); }
    .orb-status { position: absolute; left: 50%; bottom: 9px; width: 38px; height: 4px; transform: translateX(-50%); border-radius: 999px; background: rgba(248,251,255,.62); }
    .jarvis-orb.state-idle { filter: saturate(1); }
    .jarvis-orb.state-listening { animation-duration: 1.8s; box-shadow: 0 0 34px rgba(126,231,212,.46), inset 0 0 24px rgba(255,255,255,.18); }
    .jarvis-orb.state-thinking { animation-duration: 1.2s; background: radial-gradient(circle at 38% 32%, #f8fbff 0 7%, #ffd98a 10% 24%, #3bb5b5 38%, #17233a 68%); }
    .jarvis-orb.state-speaking { animation-duration: .78s; box-shadow: 0 0 42px rgba(255,217,138,.5), inset 0 0 24px rgba(255,255,255,.18); }
    @keyframes orbPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.045); } }
    @keyframes orbRing { 0% { opacity: .18; transform: scale(.86); } 50% { opacity: .8; transform: scale(1.04); } 100% { opacity: .18; transform: scale(.86); } }
    @media (max-width: 640px) { .hero-row { align-items: flex-start; } .jarvis-orb { width: 64px; height: 64px; } .orb-core { inset: 23px; } }
  </style>
</head>
<body>
  <main>
    <div class="shell">
      <section class="card">
        <div class="hero-row">
          <div>
            <h1>J.A.R.V.I.S. Local Chat</h1>
            <p class="muted">Ask about today's plan, instruments, safety, blockers, or the dashboard.</p>
          </div>
          <div id="jarvisOrb" class="jarvis-orb state-idle" data-state="idle" aria-label="J.A.R.V.I.S. voice state">
            <span class="orb-core"></span>
            <span class="orb-status"></span>
          </div>
        </div>
        <div class="safety">Read-only and manual-only. No broker, credentials, orders, trades, or auto-approval path is enabled.</div>
        <div class="badges" aria-label="Safety and status badges">
          <span class="badge safe">manual-only</span>
          <span class="badge safe">read-only</span>
          <span class="badge safe">no broker</span>
          <span class="badge safe">no credentials</span>
          <span class="badge safe">no orders</span>
          <span class="badge safe">no trades</span>
          <span class="badge safe">no auto-approval</span>
        </div>
      </section>

      <section class="card">
        <h2>Presets</h2>
        <div class="preset-grid" aria-label="Preset questions">
          <button class="preset" type="button" data-question="What is my plan today?">What is my plan today?</button>
          <button class="preset" type="button" data-question="What happened today?">What happened today?</button>
          <button class="preset" type="button" data-question="What changed since last time?">What changed since last time?</button>
          <button class="preset" type="button" data-question="Why these instruments?">Why these instruments?</button>
          <button class="preset" type="button" data-question="Can I trust this data?">Can I trust this data?</button>
          <button class="preset" type="button" data-question="What news matters to my portfolio?">What news matters?</button>
          <button class="preset" type="button" data-question="Is this safe?">Is this safe?</button>
          <button class="preset" type="button" data-question="What are the blockers?">What are the blockers?</button>
          <button class="preset" type="button" data-action="dashboard">Open dashboard</button>
        </div>
        <textarea id="question">What is my plan today?</textarea>
        <div class="actions">
          <button id="askButton" class="primary" type="button">Ask J.A.R.V.I.S.</button>
          <a class="dashboard-link" href="/dashboard">Open dashboard</a>
        </div>
        <div class="voice-actions" aria-label="Voice controls">
          <button id="voiceDraftButton" class="voice-button" type="button">Voice input</button>
          <button id="readBriefingButton" class="voice-button" type="button">Read briefing aloud</button>
          <button id="speakReplyButton" class="voice-button" type="button">Speak reply</button>
          <button id="stopVoiceButton" class="voice-button" type="button">Stop voice</button>
        </div>
        <div id="audioStatus" class="voice-status" role="status">Voice is output-only until you press Ask manually.</div>
      </section>

      <section class="card">
        <div class="reply-card" aria-live="polite">
          <div class="reply-head">
            <span>Reply</span>
            <span id="loadingState" class="loading">Loading...</span>
          </div>
          <pre id="reply">Ready.</pre>
        </div>
        <p class="links">
          <a href="/dashboard">Dashboard</a>
          <a href="/health">Health</a>
          <a href="/api/status">API status</a>
        </p>
      </section>
    </div>
  </main>
  <script>
    const question = document.getElementById("question");
    const reply = document.getElementById("reply");
    const button = document.getElementById("askButton");
    const loading = document.getElementById("loadingState");
    const audioStatus = document.getElementById("audioStatus");
    const readBriefingButton = document.getElementById("readBriefingButton");
    const speakReplyButton = document.getElementById("speakReplyButton");
    const stopVoiceButton = document.getElementById("stopVoiceButton");
    const voiceDraftButton = document.getElementById("voiceDraftButton");
    const jarvisOrb = document.getElementById("jarvisOrb");
    const canSpeak = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;

    function setAudioStatus(message) {
      audioStatus.textContent = message;
    }

    function setOrbState(state) {
      const allowed = ["idle", "listening", "thinking", "speaking"];
      const nextState = allowed.includes(state) ? state : "idle";
      jarvisOrb.dataset.state = nextState;
      jarvisOrb.className = "jarvis-orb state-" + nextState;
    }

    function speakText(text) {
      if (!canSpeak) {
        setAudioStatus("Audio unavailable in this browser. Text remains available.");
        setOrbState("idle");
        return;
      }
      const cleanText = (text || "").trim();
      if (!cleanText) {
        setAudioStatus("Nothing to read yet.");
        setOrbState("idle");
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.onstart = () => {
        setAudioStatus("Speaking...");
        setOrbState("speaking");
      };
      utterance.onend = () => {
        setAudioStatus("Voice ready.");
        setOrbState("idle");
      };
      utterance.onerror = () => {
        setAudioStatus("Audio unavailable. Text remains available.");
        setOrbState("idle");
      };
      window.speechSynthesis.speak(utterance);
    }

    function stopVoice() {
      if (canSpeak) {
        window.speechSynthesis.cancel();
      }
      if (recognition) {
        recognition.stop();
      }
      setOrbState("idle");
      setAudioStatus("Voice stopped.");
    }

    async function readBriefingAloud() {
      setOrbState("thinking");
      try {
        const response = await fetch("/api/voice-briefing");
        const payload = await response.json();
        const briefing = payload.text || "";
        reply.textContent = briefing || "Briefing text unavailable.";
        speakText(briefing);
      } catch (error) {
        setAudioStatus("Audio unavailable. Briefing text could not be loaded.");
        setOrbState("idle");
      }
    }

    function startVoiceDraft() {
      if (!SpeechRecognition) {
        setAudioStatus("Microphone input unavailable in this browser.");
        return;
      }
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";
      recognition.onstart = () => {
        setAudioStatus("Listening...");
        setOrbState("listening");
      };
      recognition.onresult = (event) => {
        const transcript = event.results && event.results[0] && event.results[0][0]
          ? event.results[0][0].transcript
          : "";
        question.value = transcript;
        setAudioStatus("Voice draft ready. Press Ask J.A.R.V.I.S. manually.");
        setOrbState("idle");
      };
      recognition.onerror = () => {
        setAudioStatus("Microphone input unavailable in this browser.");
        setOrbState("idle");
      };
      recognition.onend = () => {
        recognition = null;
        if (jarvisOrb.dataset.state === "listening") {
          setOrbState("idle");
        }
      };
      recognition.start();
    }

    async function askJarvis() {
      button.disabled = true;
      loading.classList.add("active");
      reply.textContent = "Loading reply...";
      setOrbState("thinking");
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({query: question.value})
        });
        const payload = await response.json();
        reply.textContent = payload.reply || payload.response || JSON.stringify(payload, null, 2);
      } catch (error) {
        reply.textContent = "Local chat error: " + error;
      } finally {
        button.disabled = false;
        loading.classList.remove("active");
        if (jarvisOrb.dataset.state === "thinking") {
          setOrbState("idle");
        }
      }
    }

    button.addEventListener("click", askJarvis);
    readBriefingButton.addEventListener("click", readBriefingAloud);
    speakReplyButton.addEventListener("click", () => speakText(reply.textContent));
    stopVoiceButton.addEventListener("click", stopVoice);
    voiceDraftButton.addEventListener("click", startVoiceDraft);
    document.querySelectorAll(".preset").forEach((preset) => {
      preset.addEventListener("click", () => {
        if (preset.dataset.action === "dashboard") {
          window.location.href = "/dashboard";
          return;
        }
        question.value = preset.dataset.question || preset.textContent;
        askJarvis();
      });
    });
  </script>
</body>
</html>"""


def _chat_payload(*, query: str, current_date: str) -> dict[str, Any]:
    result = build_assistant_router_result(query=query, current_date=current_date)
    payload = result.to_dict()
    payload["response"] = result.reply
    payload["reply"] = result.reply
    return payload


def make_handler(*, host: str, port: int, current_date: str) -> type[BaseHTTPRequestHandler]:
    class JarvisLocalServerHandler(BaseHTTPRequestHandler):
        server_version = "JarvisLocalServer/104.0"

        def log_message(self, format: str, *args: Any) -> None:
            # Keep console output clean; this is a local operator shell.
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)

            if path == "/health":
                _json_response(self, _health_payload(host=host, port=port, current_date=current_date))
                return

            if path == "/api/status":
                product = build_product_api_result(current_date=current_date)
                _json_response(self, _plain(product))
                return

            if path == "/api/finance-intelligence":
                finance = build_finance_intelligence_core_result(current_date=current_date)
                _json_response(self, _plain(finance))
                return

            if path == "/api/voice-briefing":
                briefing = build_voice_briefing_result(current_date=current_date)
                _json_response(self, _plain(briefing))
                return

            if path == "/api/chat":
                chat_query = str((query.get("q") or [""])[0])
                _json_response(self, _chat_payload(query=chat_query, current_date=current_date))
                return

            if path in {"/", "/chat"}:
                _html_response(self, render_chat_page())
                return

            if path == "/dashboard":
                _html_response(self, _dashboard_html(current_date=current_date))
                return

            _error_response(self, f"unknown route: {path}", status=404)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/chat":
                _error_response(self, f"unknown route: {parsed.path}", status=404)
                return

            payload = _read_json_body(self)
            if payload.get("_error") == "request_body_too_large":
                _error_response(self, "request body too large", status=413)
                return
            query = str(payload.get("query") or payload.get("q") or "")
            _json_response(self, _chat_payload(query=query, current_date=current_date))

    return JarvisLocalServerHandler


def build_local_server_smoke_result(
    *,
    current_date: str = "2026-06-18",
    host: str = "127.0.0.1",
    port: int = 8765,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> LocalServerSmokeResult:
    chat = build_chat_interface_contract_result(
        query="is this safe, can it trade?",
        current_date=current_date,
    )
    dashboard = build_dashboard_contract_result(current_date=current_date)
    product_api = build_product_api_result(current_date=current_date)

    safety_text = chat.response
    manual_only = bool(chat.manual_only and dashboard.manual_only)
    execution_forbidden = "Execution forbidden: True" in safety_text
    broker_connection = "Broker connection: True" in safety_text
    credentials_used = "Credentials used: True" in safety_text
    order_created = "Order created: True" in safety_text
    trade_executed = "Trade executed: True" in safety_text

    blockers: list[str] = []
    if not chat.chat_contract_ready:
        blockers.append("chat_contract_not_ready")
    if not dashboard.dashboard_contract_ready:
        blockers.append("dashboard_contract_not_ready")
    if not bool(getattr(product_api, "api_ready", False)):
        blockers.append("product_api_not_ready")
    if not manual_only:
        blockers.append("manual_only_not_ready")
    if not execution_forbidden:
        blockers.append("execution_forbidden_not_confirmed")
    if broker_connection:
        blockers.append("broker_connection_enabled")
    if credentials_used:
        blockers.append("credentials_used")
    if order_created:
        blockers.append("order_created")
    if trade_executed:
        blockers.append("trade_executed")

    blockers = list(dict.fromkeys(item for item in blockers if item))

    warnings = [
        "local server shell is read-only and local-only by default",
        "server endpoints expose product, dashboard, and chat payloads only",
        "no broker, credentials, order, trade, or auto-approval path is enabled",
        "POST /api/chat returns a reply; it does not execute actions",
    ]

    ready = not blockers

    result = LocalServerSmokeResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        local_server_ready=ready,
        host=host,
        port=port,
        routes=dict(ROUTES),
        manual_only=manual_only,
        execution_forbidden=execution_forbidden,
        broker_connection=broker_connection,
        credentials_used=credentials_used,
        order_created=order_created,
        trade_executed=trade_executed,
        chat_smoke_ready=bool(chat.chat_contract_ready),
        dashboard_smoke_ready=bool(dashboard.dashboard_contract_ready),
        product_api_smoke_ready=bool(getattr(product_api, "api_ready", False)),
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def format_local_server_smoke(result: LocalServerSmokeResult) -> str:
    lines = [
        "J.A.R.V.I.S. LOCAL SERVER SHELL",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"local server ready: {result.local_server_ready}",
        f"host: {result.host}",
        f"port: {result.port}",
        "",
        "ROUTES:",
    ]
    lines.extend(f"- {route}: {description}" for route, description in result.routes.items())
    lines.extend(
        [
            "",
            "SAFETY:",
            f"- manual-only: {result.manual_only}",
            f"- execution forbidden: {result.execution_forbidden}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "",
            "SMOKE:",
            f"- chat ready: {result.chat_smoke_ready}",
            f"- dashboard ready: {result.dashboard_smoke_ready}",
            f"- product API ready: {result.product_api_smoke_ready}",
            "",
            "RUN SERVER:",
            f"- python -m jarvis.runtime.local_server --local-server --host {result.host} --port {result.port}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def run_server(*, host: str = "127.0.0.1", port: int = 8765, current_date: str = "2026-06-18") -> None:
    handler = make_handler(host=host, port=port, current_date=current_date)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"J.A.R.V.I.S. local server running at http://{host}:{port}")
    print("Routes: /health, /chat, /dashboard, /api/status, /api/finance-intelligence, /api/chat")
    print("Safety: read-only, manual-only, no broker/credentials/orders/trades.")
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. local server shell.")
    parser.add_argument("--local-server", action="store_true")
    parser.add_argument("--local-server-smoke", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    if args.local_server:
        run_server(host=args.host, port=args.port, current_date=args.current_date)
        return 0

    result = build_local_server_smoke_result(
        current_date=args.current_date,
        host=args.host,
        port=args.port,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_local_server_smoke(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "ROUTES",
    "LocalServerSmokeResult",
    "build_local_server_smoke_result",
    "format_local_server_smoke",
    "render_chat_page",
    "make_handler",
    "run_server",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
