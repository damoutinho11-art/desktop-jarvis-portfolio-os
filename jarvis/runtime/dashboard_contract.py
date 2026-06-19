from __future__ import annotations

import argparse
import html
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.full_system_audit import build_full_system_audit_result
from jarvis.runtime.product_api import build_product_api_result

STATUS_READY = "JARVIS_V99_0_DASHBOARD_CONTRACT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V99_0_DASHBOARD_CONTRACT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/dashboard_contract_latest.json"
DEFAULT_DASHBOARD_PATH = "outputs/dashboard_latest.html"


@dataclass(frozen=True)
class DashboardContractResult:
    status: str
    current_date: str
    dashboard_contract_ready: bool
    dashboard_html_written: bool
    dashboard_path: str
    backend_ready: bool
    product_api_ready: bool
    full_audit_ready: bool
    product_recommendations_allowed: bool
    manual_only: bool
    sections: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _html_list(items: list[Any]) -> str:
    if not items:
        return "<li>none</li>"
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _build_sections(product_api: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    week = product_api.get("week_plan", {}) or {}
    data = product_api.get("data_readiness", {}) or {}
    news = product_api.get("news_coverage", {}) or {}
    safety = product_api.get("safety_status", {}) or {}

    return {
        "status": {
            "title": "System Status",
            "dashboard_ready": product_api.get("dashboard_ready"),
            "chat_ready": product_api.get("chat_ready"),
            "voice_ready": product_api.get("voice_ready"),
            "audit_verdict": audit.get("audit_verdict"),
            "blockers": list(audit.get("blockers", []) or []),
        },
        "week_plan": {
            "title": "Weekly Manual Plan",
            "monthly_contribution_eur": week.get("monthly_contribution_eur"),
            "emergency_top_up_eur": week.get("emergency_top_up_eur"),
            "crypto_eur": week.get("crypto_eur"),
            "etf_fund_eur": week.get("etf_fund_eur"),
            "individual_stock_eur": week.get("individual_stock_eur"),
            "selected_instruments": list(week.get("selected_instruments", []) or []),
        },
        "data": {
            "title": "Data Readiness",
            "data_readiness_ready": data.get("data_readiness_ready"),
            "missing_data": list(data.get("missing_data", []) or []),
            "missing_universe": list(data.get("missing_universe", []) or []),
            "crypto_candidates": data.get("crypto_candidate_count"),
            "etf_candidates": data.get("etf_candidate_count"),
            "stock_candidates": data.get("stock_candidate_count"),
        },
        "news": {
            "title": "News Coverage",
            "news_coverage_ready": news.get("news_coverage_ready"),
            "live_news_fetch_enabled": news.get("live_news_fetch_enabled"),
            "manual_review_required": news.get("manual_review_required"),
            "covered_categories": list(news.get("covered_categories", []) or []),
        },
        "safety": {
            "title": "Safety",
            "safety_check_blocked_execution": safety.get("safety_check_blocked_execution"),
            "manual_approval_required": safety.get("manual_approval_required"),
            "execution_forbidden": safety.get("execution_forbidden"),
            "broker_connection": safety.get("broker_connection"),
            "credentials_used": safety.get("credentials_used"),
            "order_created": safety.get("order_created"),
            "trade_executed": safety.get("trade_executed"),
        },
        "audit": {
            "title": "Full Audit",
            "formula_invariants_ready": audit.get("formula_invariants_ready"),
            "data_readiness_ready": audit.get("data_readiness_ready"),
            "news_coverage_ready": audit.get("news_coverage_ready"),
            "safety_ready": audit.get("safety_ready"),
            "speed_ready": audit.get("speed_ready"),
            "warnings": list(audit.get("warnings", []) or []),
        },
    }


def render_dashboard_html(result: DashboardContractResult) -> str:
    sections = result.sections
    status = sections["status"]
    week = sections["week_plan"]
    data = sections["data"]
    news = sections["news"]
    safety = sections["safety"]
    audit = sections["audit"]

    rows = []
    for item in week.get("selected_instruments", []) or []:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('lane', '')))}</td>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(_money(item.get('amount_eur')))}</td>"
            "</tr>"
        )
    selected_rows = "".join(rows) if rows else "<tr><td colspan='3'>none</td></tr>"
    selected_items = week.get("selected_instruments", []) or []

    def lane_summary(lane: str) -> str:
        labels = []
        for item in selected_items:
            if str(item.get("lane", "")) == lane:
                labels.append(f"{item.get('symbol', '')} {_money(item.get('amount_eur'))}")
        return ", ".join(labels) if labels else "none"

    crypto_summary = lane_summary("crypto")
    etf_summary = lane_summary("etf_fund")
    stock_summary = lane_summary("individual_stock")

    css = """
    body { margin:0; font-family:Segoe UI, Arial, sans-serif; background:#0b0f14; color:#edf3fb; }
    header, main { max-width:1180px; margin:0 auto; padding:24px; }
    h1 { margin-bottom:6px; }
    .subtitle { color:#9fb0c3; }
    main { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }
    .card { grid-column:span 6; background:#111823; border:1px solid #27364a; border-radius:18px; padding:20px; }
    .wide { grid-column:span 12; }
    .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
    .metric { background:#162131; border:1px solid #27364a; border-radius:14px; padding:14px; }
    .label { color:#9fb0c3; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
    .value { font-size:22px; font-weight:700; margin-top:5px; }
    .ok { color:#8ef0b0; }
    .warn { color:#ffd166; }
    table { width:100%; border-collapse:collapse; margin-top:14px; }
    th, td { text-align:left; padding:10px 8px; border-bottom:1px solid #27364a; }
    th { color:#9fb0c3; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
    ul { margin:0; padding-left:20px; color:#c7d3e2; }
    @media (max-width:820px) { .card { grid-column:span 12; } .grid { grid-template-columns:1fr; } }
    """

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>J.A.R.V.I.S. Portfolio Dashboard</title>
<style>{css}</style>
</head>
<body>
<header>
<h1>J.A.R.V.I.S. Portfolio Dashboard</h1>
<div class="subtitle">Generated locally from the read-only product API. Current date: {html.escape(result.current_date)}</div>
</header>
<main>
<section class="card wide">
<h2>Today's Manual Action Summary</h2>
<div class="grid">
<div class="metric"><div class="label">Emergency Top-up</div><div class="value">{_money(week.get("emergency_top_up_eur"))}</div></div>
<div class="metric"><div class="label">Crypto</div><div class="value">{_money(week.get("crypto_eur"))}</div></div>
<div class="metric"><div class="label">ETF/Fund</div><div class="value">{_money(week.get("etf_fund_eur"))}</div></div>
<div class="metric"><div class="label">Stock</div><div class="value">{_money(week.get("individual_stock_eur"))}</div></div>
<div class="metric"><div class="label">Safety</div><div class="value ok">{safety.get("safety_check_blocked_execution")}</div></div>
<div class="metric"><div class="label">Blockers</div><div class="value ok">{len(result.blockers)}</div></div>
</div>
<ul>
<li>Crypto checklist: {html.escape(crypto_summary)}</li>
<li>ETF/fund checklist: {html.escape(etf_summary)}</li>
<li>Stock checklist: {html.escape(stock_summary)}</li>
<li>Execution remains outside J.A.R.V.I.S.; this dashboard is read-only.</li>
</ul>
</section>

<section class="card wide">
<h2>Readiness</h2>
<div class="grid">
<div class="metric"><div class="label">Dashboard</div><div class="value ok">{status.get("dashboard_ready")}</div></div>
<div class="metric"><div class="label">Chat</div><div class="value ok">{status.get("chat_ready")}</div></div>
<div class="metric"><div class="label">Voice</div><div class="value ok">{status.get("voice_ready")}</div></div>
<div class="metric"><div class="label">Audit</div><div class="value warn">{html.escape(str(status.get("audit_verdict")))}</div></div>
<div class="metric"><div class="label">Contract</div><div class="value ok">{result.dashboard_contract_ready}</div></div>
<div class="metric"><div class="label">Manual Only</div><div class="value ok">{result.manual_only}</div></div>
</div>
</section>

<section class="card wide">
<h2>Weekly Manual Plan</h2>
<div class="grid">
<div class="metric"><div class="label">Monthly</div><div class="value">{_money(week.get("monthly_contribution_eur"))}</div></div>
<div class="metric"><div class="label">Emergency</div><div class="value">{_money(week.get("emergency_top_up_eur"))}</div></div>
<div class="metric"><div class="label">Crypto</div><div class="value">{_money(week.get("crypto_eur"))}</div></div>
<div class="metric"><div class="label">ETF/Fund</div><div class="value">{_money(week.get("etf_fund_eur"))}</div></div>
<div class="metric"><div class="label">Stock</div><div class="value">{_money(week.get("individual_stock_eur"))}</div></div>
</div>
<table><thead><tr><th>Lane</th><th>Instrument</th><th>Amount</th></tr></thead><tbody>{selected_rows}</tbody></table>
</section>

<section class="card"><h2>Data</h2><ul>
<li>Ready: {data.get("data_readiness_ready")}</li>
<li>Crypto candidates: {data.get("crypto_candidates")}</li>
<li>ETF/fund candidates: {data.get("etf_candidates")}</li>
<li>Stock candidates: {data.get("stock_candidates")}</li>
<li>Missing data: {html.escape(", ".join(data.get("missing_data") or []) or "none")}</li>
<li>Missing universe: {html.escape(", ".join(data.get("missing_universe") or []) or "none")}</li>
</ul></section>

<section class="card"><h2>News</h2><ul>
<li>Coverage ready: {news.get("news_coverage_ready")}</li>
<li>Live fetch enabled: {news.get("live_news_fetch_enabled")}</li>
<li>Manual review required: {news.get("manual_review_required")}</li>
<li>Covered: {html.escape(", ".join(news.get("covered_categories") or []) or "none")}</li>
</ul></section>

<section class="card"><h2>Safety</h2><ul>
<li>Safety-check blocked execution: {safety.get("safety_check_blocked_execution")}</li>
<li>Manual approval required: {safety.get("manual_approval_required")}</li>
<li>Execution forbidden: {safety.get("execution_forbidden")}</li>
<li>Broker connection: {safety.get("broker_connection")}</li>
<li>Credentials used: {safety.get("credentials_used")}</li>
<li>Order created: {safety.get("order_created")}</li>
<li>Trade executed: {safety.get("trade_executed")}</li>
</ul></section>

<section class="card"><h2>Audit</h2><ul>
<li>Formula invariants ready: {audit.get("formula_invariants_ready")}</li>
<li>Data readiness ready: {audit.get("data_readiness_ready")}</li>
<li>News coverage ready: {audit.get("news_coverage_ready")}</li>
<li>Safety ready: {audit.get("safety_ready")}</li>
<li>Speed ready: {audit.get("speed_ready")}</li>
</ul></section>

<section class="card wide"><h2>Warnings & Manual Review Notes</h2><details open><summary>Review dashboard warnings</summary><ul>{_html_list(result.warnings)}</ul></details></section>
<section class="card wide"><h2>Blockers</h2><ul>{_html_list(result.blockers)}</ul></section>
<section class="card wide"><h2>Manual QA Checklist</h2><ul>
<li>Confirm the weekly manual plan total matches the contribution.</li>
<li>Confirm BTC, ETH, ETF/fund, and stock rows are visible.</li>
<li>Confirm news coverage is ready, while live news fetch remains disabled.</li>
<li>Confirm safety shows no broker, credentials, orders, or trades.</li>
<li>Open command: start .\\outputs\\dashboard_latest.html</li>
</ul></section>
</main>
</body>
</html>
"""


def build_dashboard_contract_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    dashboard_path: str | Path = DEFAULT_DASHBOARD_PATH,
    write_report: bool = False,
    write_dashboard: bool = False,
) -> DashboardContractResult:
    product_api = _plain(build_product_api_result(current_date=current_date))
    audit = _plain(build_full_system_audit_result(current_date=current_date))
    sections = _build_sections(product_api, audit)
    safety = sections["safety"]

    manual_only = bool(
        safety.get("manual_approval_required")
        and safety.get("execution_forbidden")
        and safety.get("safety_check_blocked_execution")
        and not safety.get("broker_connection")
        and not safety.get("credentials_used")
        and not safety.get("order_created")
        and not safety.get("trade_executed")
    )
    backend_ready = bool(
        product_api.get("dashboard_ready")
        and product_api.get("chat_ready")
        and product_api.get("voice_ready")
        and audit.get("dashboard_chat_voice_backend_ready")
    )

    blockers = []
    blockers.extend(str(item) for item in (product_api.get("blockers") or []))
    blockers.extend(str(item) for item in (audit.get("blockers") or []))
    if not backend_ready:
        blockers.append("dashboard_backend_not_ready")
    if not manual_only:
        blockers.append("manual_only_safety_not_ready")
    blockers = _dedupe(blockers)

    warnings = _dedupe(
        ["dashboard contract is local/static and does not start a web server"]
        + [str(item) for item in (product_api.get("warnings") or [])]
        + [str(item) for item in (audit.get("warnings") or [])]
    )

    ready = not blockers
    result = DashboardContractResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        dashboard_contract_ready=ready,
        dashboard_html_written=bool(write_dashboard),
        dashboard_path=str(dashboard_path),
        backend_ready=backend_ready,
        product_api_ready=bool(product_api.get("api_ready")),
        full_audit_ready=not bool(audit.get("blockers")),
        product_recommendations_allowed=bool(product_api.get("product_recommendations_allowed")),
        manual_only=manual_only,
        sections=sections,
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if write_dashboard:
        Path(dashboard_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dashboard_path).write_text(render_dashboard_html(result), encoding="utf-8")

    return result


def format_dashboard_contract(result: DashboardContractResult) -> str:
    dashboard_open_path = result.dashboard_path.replace("/", "\\")
    lines = [
        "J.A.R.V.I.S. DASHBOARD CONTRACT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"dashboard contract ready: {result.dashboard_contract_ready}",
        f"backend ready: {result.backend_ready}",
        f"product API ready: {result.product_api_ready}",
        f"full audit ready: {result.full_audit_ready}",
        f"product recommendations allowed: {result.product_recommendations_allowed}",
        f"manual-only safety: {result.manual_only}",
        f"dashboard html written: {result.dashboard_html_written}",
        f"dashboard path: {result.dashboard_path}",
        "",
        "OPEN DASHBOARD:",
        f"- start .\\{dashboard_open_path}",
        "",
        "QA CHECKLIST:",
        "- verify Weekly Manual Plan is visible",
        "- verify BTC, ETH, ETF/fund, and MSFT rows are visible",
        "- verify News and Safety sections are visible",
        "- verify Blockers is none before manual action",
        "",
        "SECTIONS:",
    ]
    lines.extend(f"- {key}: {value.get('title')}" for key, value in result.sections.items())
    lines.append("")
    lines.append("WARNINGS:")
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build J.A.R.V.I.S. dashboard contract.")
    parser.add_argument("--dashboard-contract", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-dashboard", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--dashboard-path", default=DEFAULT_DASHBOARD_PATH)
    args = parser.parse_args(argv)

    result = build_dashboard_contract_result(
        current_date=args.current_date,
        output_path=args.output_path,
        dashboard_path=args.dashboard_path,
        write_report=args.write_report,
        write_dashboard=args.write_dashboard,
    )
    print(format_dashboard_contract(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DashboardContractResult",
    "build_dashboard_contract_result",
    "render_dashboard_html",
    "format_dashboard_contract",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
