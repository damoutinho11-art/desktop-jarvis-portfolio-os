from __future__ import annotations

import argparse
import http.client
import json
import threading
from contextlib import ExitStack
from dataclasses import asdict, dataclass, field
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from unittest.mock import patch

from jarvis.runtime import local_server

STATUS_READY = "JARVIS_V105_0_LOCAL_SERVER_LIVE_ENDPOINT_SMOKE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V105_0_LOCAL_SERVER_LIVE_ENDPOINT_SMOKE_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/local_server_live_endpoint_smoke_latest.json"


@dataclass(frozen=True)
class LocalServerLiveEndpointSmokeResult:
    status: str
    current_date: str
    live_endpoint_smoke_ready: bool
    host: str
    requested_port: int
    bound_port: int
    health_ready: bool
    dashboard_ready: bool
    api_status_ready: bool
    api_chat_ready: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    http_checks: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class _SafeFixtureChatResult:
    query: str
    status: str = "JARVIS_V105_SAFE_FIXTURE_CHAT_READY"
    chat_contract_ready: bool = True
    manual_only: bool = True
    detected_intent: str = "safety"
    response: str = (
        "Safety is active. Safety-check blocked execution: True. "
        "Manual approval required: True. Execution forbidden: True. "
        "Broker connection: False. Credentials used: False. "
        "Order created: False. Trade executed: False."
    )
    open_dashboard_command: str = "start .\\outputs\\dashboard_latest.html"
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=lambda: ["safe fixture chat payload for live endpoint smoke"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "chat_contract_ready": self.chat_contract_ready,
            "manual_only": self.manual_only,
            "query": self.query,
            "detected_intent": self.detected_intent,
            "response": self.response,
            "open_dashboard_command": self.open_dashboard_command,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass
class _SafeFixtureProductApiResult:
    api_ready: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "JARVIS_V105_SAFE_FIXTURE_PRODUCT_API_READY",
            "api_ready": True,
            "dashboard_ready": True,
            "chat_ready": True,
            "voice_ready": True,
            "product_recommendations_allowed": True,
            "safety_status": {
                "manual_approval_required": True,
                "execution_forbidden": True,
                "broker_connection": False,
                "credentials_used": False,
                "order_created": False,
                "trade_executed": False,
            },
            "blockers": [],
            "warnings": ["safe fixture product API payload for live endpoint smoke"],
        }


@dataclass
class _SafeFixtureDashboardContractResult:
    dashboard_contract_ready: bool = True
    manual_only: bool = True
    blockers: list[str] = field(default_factory=list)


def _safe_fixture_dashboard_contract(*args: Any, **kwargs: Any) -> _SafeFixtureDashboardContractResult:
    Path("outputs").mkdir(parents=True, exist_ok=True)
    Path("outputs/dashboard_latest.html").write_text(
        "<!doctype html><html><body><h1>J.A.R.V.I.S. Portfolio Dashboard</h1>"
        "<p>safe fixture dashboard for live endpoint smoke</p></body></html>",
        encoding="utf-8",
    )
    return _SafeFixtureDashboardContractResult()


def _safe_fixture_chat_contract(*, query: str = "", **kwargs: Any) -> _SafeFixtureChatResult:
    return _SafeFixtureChatResult(query=query)


def _safe_fixture_product_api(*args: Any, **kwargs: Any) -> _SafeFixtureProductApiResult:
    return _SafeFixtureProductApiResult()


def _request_json(
    *,
    host: str,
    port: int,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        payload = None
        headers: dict[str, str] = {}
        if body is not None:
            payload = json.dumps(body)
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=payload, headers=headers)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        return response.status, data if isinstance(data, dict) else {"value": data}
    finally:
        conn.close()


def _request_text(*, host: str, port: int, method: str, path: str) -> tuple[int, str]:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        return response.status, raw
    finally:
        conn.close()


def build_local_server_live_endpoint_smoke_result(
    *,
    current_date: str = "2026-06-18",
    host: str = "127.0.0.1",
    port: int = 0,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> LocalServerLiveEndpointSmokeResult:
    warnings = [
        "live endpoint smoke starts a short-lived local server on 127.0.0.1",
        "endpoint smoke uses safe fixture payloads to keep validation fast and execution-free",
        "no broker, credentials, order, trade, or auto-approval path is enabled",
    ]
    blockers: list[str] = []

    http_checks: dict[str, Any] = {}
    bound_port = 0

    with ExitStack() as stack:
        stack.enter_context(patch("jarvis.runtime.local_server.build_chat_interface_contract_result", _safe_fixture_chat_contract))
        stack.enter_context(patch("jarvis.runtime.local_server.build_dashboard_contract_result", _safe_fixture_dashboard_contract))
        stack.enter_context(patch("jarvis.runtime.local_server.build_product_api_result", _safe_fixture_product_api))

        handler = local_server.make_handler(host=host, port=port, current_date=current_date)
        server = ThreadingHTTPServer((host, port), handler)
        bound_port = int(server.server_address[1])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            health_status, health = _request_json(host=host, port=bound_port, method="GET", path="/health")
            api_status_code, api_status = _request_json(host=host, port=bound_port, method="GET", path="/api/status")
            api_chat_code, api_chat = _request_json(
                host=host,
                port=bound_port,
                method="POST",
                path="/api/chat",
                body={"query": "is this safe, can it trade?"},
            )
            dashboard_status, dashboard_html = _request_text(
                host=host,
                port=bound_port,
                method="GET",
                path="/dashboard",
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    health_ready = health_status == 200 and bool(health.get("local_server_ready"))
    api_status_ready = api_status_code == 200 and bool(api_status.get("api_ready"))
    api_chat_ready = (
        api_chat_code == 200
        and bool(api_chat.get("reply"))
        and (
            "Safety is active" in str(api_chat.get("reply", ""))
            or "I cannot create buy/sell requests" in str(api_chat.get("reply", ""))
        )
        and not bool(api_chat.get("order_created"))
        and not bool(api_chat.get("trade_executed"))
    )
    dashboard_ready = dashboard_status == 200 and "J.A.R.V.I.S. Portfolio Dashboard" in dashboard_html

    manual_only = bool(health.get("manual_only"))
    execution_forbidden = bool(health.get("execution_forbidden"))
    broker_connection = bool(health.get("broker_connection"))
    credentials_used = bool(health.get("credentials_used"))
    order_created = bool(health.get("order_created"))
    trade_executed = bool(health.get("trade_executed"))

    http_checks = {
        "GET /health": {"status": health_status, "ready": health_ready},
        "GET /api/status": {"status": api_status_code, "ready": api_status_ready},
        "POST /api/chat": {"status": api_chat_code, "ready": api_chat_ready},
        "GET /dashboard": {"status": dashboard_status, "ready": dashboard_ready},
    }

    if not health_ready:
        blockers.append("health_endpoint_not_ready")
    if not api_status_ready:
        blockers.append("api_status_endpoint_not_ready")
    if not api_chat_ready:
        blockers.append("api_chat_endpoint_not_ready")
    if not dashboard_ready:
        blockers.append("dashboard_endpoint_not_ready")
    if not manual_only:
        blockers.append("manual_only_not_confirmed")
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
    ready = not blockers

    result = LocalServerLiveEndpointSmokeResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        live_endpoint_smoke_ready=ready,
        host=host,
        requested_port=port,
        bound_port=bound_port,
        health_ready=health_ready,
        dashboard_ready=dashboard_ready,
        api_status_ready=api_status_ready,
        api_chat_ready=api_chat_ready,
        manual_only=manual_only,
        execution_forbidden=execution_forbidden,
        broker_connection=broker_connection,
        credentials_used=credentials_used,
        order_created=order_created,
        trade_executed=trade_executed,
        http_checks=http_checks,
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


def format_local_server_live_endpoint_smoke(result: LocalServerLiveEndpointSmokeResult) -> str:
    lines = [
        "J.A.R.V.I.S. LOCAL SERVER LIVE ENDPOINT SMOKE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"live endpoint smoke ready: {result.live_endpoint_smoke_ready}",
        f"host: {result.host}",
        f"requested port: {result.requested_port}",
        f"bound port: {result.bound_port}",
        "",
        "HTTP CHECKS:",
    ]
    lines.extend(
        f"- {name}: status {data.get('status')} ready {data.get('ready')}"
        for name, data in result.http_checks.items()
    )
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. local server live endpoint smoke.")
    parser.add_argument("--local-server-live-smoke", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_local_server_live_endpoint_smoke_result(
        current_date=args.current_date,
        host=args.host,
        port=args.port,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_local_server_live_endpoint_smoke(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "LocalServerLiveEndpointSmokeResult",
    "build_local_server_live_endpoint_smoke_result",
    "format_local_server_live_endpoint_smoke",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
