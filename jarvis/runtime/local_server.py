from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from jarvis.runtime.chat_interface_contract import (
    build_chat_interface_contract_result,
    format_chat_reply,
)
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.product_api import build_product_api_result

STATUS_READY = "JARVIS_V106_0_LOCAL_BROWSER_CHAT_PAGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V106_0_LOCAL_BROWSER_CHAT_PAGE_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/local_server_smoke_latest.json"

ROUTES = {
    "GET /health": "local server health and safety metadata",
    "GET /dashboard": "generated local static dashboard HTML",
    "GET /chat": "local browser chat page backed by POST /api/chat",
    "GET /api/status": "read-only product API payload",
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
        "warning": "local server shell is read-only and exposes no execution path",
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
    body { font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; background: #101216; color: #f2f4f8; }
    main { max-width: 880px; margin: 0 auto; padding: 32px 20px 48px; }
    .card { background: #171a21; border: 1px solid #2b303b; border-radius: 18px; padding: 22px; box-shadow: 0 18px 40px rgba(0,0,0,.28); }
    h1 { margin: 0 0 8px; font-size: 34px; }
    .muted { color: #aab2c0; line-height: 1.55; }
    .safety { margin: 18px 0; padding: 14px 16px; border-radius: 14px; background: #1f2a1f; border: 1px solid #3f6541; color: #d8f3d8; }
    textarea { width: 100%; min-height: 120px; border-radius: 14px; border: 1px solid #3a4150; background: #0f1117; color: #f2f4f8; padding: 14px; font-size: 16px; box-sizing: border-box; }
    button { margin-top: 12px; border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; cursor: pointer; background: #f2f4f8; color: #101216; }
    button:disabled { opacity: .55; cursor: not-allowed; }
    pre { white-space: pre-wrap; background: #0f1117; border: 1px solid #303744; border-radius: 14px; padding: 16px; min-height: 130px; line-height: 1.5; }
    .links a { color: #d8e7ff; margin-right: 14px; }
  </style>
</head>
<body>
  <main>
    <section class="card">
      <h1>J.A.R.V.I.S. Local Chat</h1>
      <p class="muted">Ask about today's plan, instruments, safety, blockers, or the dashboard.</p>
      <div class="safety">Read-only and manual-only. No broker, credentials, orders, trades, or auto-approval path is enabled.</div>
      <textarea id="question">what is my plan today?</textarea>
      <br>
      <button id="askButton" type="button">Ask J.A.R.V.I.S.</button>
      <p class="muted">Reply</p>
      <pre id="reply">Ready.</pre>
      <p class="links">
        <a href="/dashboard">Open dashboard</a>
        <a href="/health">Health</a>
        <a href="/api/status">API status</a>
      </p>
    </section>
  </main>
  <script>
    const question = document.getElementById("question");
    const reply = document.getElementById("reply");
    const button = document.getElementById("askButton");

    async function askJarvis() {
      button.disabled = true;
      reply.textContent = "Thinking...";
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
      }
    }

    button.addEventListener("click", askJarvis);
  </script>
</body>
</html>"""


def _chat_payload(*, query: str, current_date: str) -> dict[str, Any]:
    result = build_chat_interface_contract_result(query=query, current_date=current_date)
    payload = result.to_dict()
    payload["reply"] = format_chat_reply(result)
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

            if path == "/api/chat":
                chat_query = str((query.get("q") or [""])[0])
                _json_response(self, _chat_payload(query=chat_query, current_date=current_date))
                return

            if path == "/chat":
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
            f"- python .\\jarvis\\runtime\\local_server.py --host {result.host} --port {result.port}",
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
    print("Routes: /health, /chat, /dashboard, /api/status, /api/chat")
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
