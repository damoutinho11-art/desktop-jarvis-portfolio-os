from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V123_0_AUTONOMOUS_ETF_IDENTITY_RESOLVER_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/etf_identity_resolver_latest.json"

DATA_PATHS = [
    Path("jarvis/data/candidate_assets.v2.example.json"),
    Path("jarvis/data/dynamic_approved_universe.example.json"),
    Path("jarvis/local/stock_fund_etf_instrument_universe.local.json"),
]

PROVIDER_SYMBOL_OVERRIDES = {
    "SXRV": "SXRV.DE",
    "SXR8": "SXR8.DE",
    "QDVE": "QDVE.DE",
    "IS3Q": "IS3Q.DE",
    "VWCE": "VWCE.DE",
    "XNAS": "XNAS.DE",
    "EQAC": "EQAC.DE",
}


@dataclass(frozen=True)
class ETFIdentityCandidate:
    asset_id: str
    symbol: str
    provider_symbol: str | None
    name: str
    isin: str | None
    source_files: list[str]
    currency: str | None
    platforms: list[str]
    provider: str | None
    index_tracked: str | None
    distribution_policy: str | None
    ter_or_fee: float | None
    evidence_score: float
    evidence_reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ETFIdentityResolverResult:
    status: str
    current_date: str
    query: str
    autonomous_identity_status: str
    best_candidate: dict[str, Any] | None
    candidates: list[dict[str, Any]]
    candidate_count: int
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_executed: bool
    auto_approval_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain_dicts(value: Any, source_file: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        candidate = dict(value)
        candidate["_source_file"] = source_file
        rows.append(candidate)
        for nested in value.values():
            rows.extend(_plain_dicts(nested, source_file))
    elif isinstance(value, list):
        for item in value:
            rows.extend(_plain_dicts(item, source_file))
    return rows


def _load_candidate_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in DATA_PATHS:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows.extend(_plain_dicts(payload, path.as_posix()))
    return rows


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _ticker(row: dict[str, Any]) -> str:
    raw = _norm(row.get("ticker") or row.get("symbol") or row.get("source_symbol")).upper()
    if raw.endswith(".DE"):
        return raw.split(".", 1)[0]
    return raw


def _isin(row: dict[str, Any]) -> str | None:
    value = _norm(row.get("isin_or_symbol") or row.get("isin") or row.get("ISIN"))
    if len(value) >= 8 and any(ch.isdigit() for ch in value):
        return value
    return None


def _provider_symbol(row: dict[str, Any], ticker: str) -> str | None:
    direct = _norm(row.get("symbol") or row.get("provider_symbol") or row.get("source_symbol"))
    if direct and "." in direct:
        return direct.upper()
    return PROVIDER_SYMBOL_OVERRIDES.get(ticker)


def _platforms(row: dict[str, Any]) -> list[str]:
    value = row.get("platforms") or []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value:
        return [str(value)]
    return []


def _as_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _is_growth_nasdaq_candidate(row: dict[str, Any]) -> bool:
    text = json.dumps(row, default=str).lower()
    ticker = _ticker(row)
    is_etf_like = "etf" in text or str(row.get("asset_type") or "").upper() == "ETF" or ticker in {"SXRV", "EQAC", "XNAS", "CNDX", "QDVE"}
    if not is_etf_like:
        return False
    return (
        "nasdaq" in text
        or "growth_innovation" in text
        or "growth candidate" in text
        or ticker in {"SXRV", "EQAC", "XNAS", "CNDX", "QDVE"}
    )


def _score_candidate(row: dict[str, Any], source_files: list[str]) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0
    ticker = _ticker(row)
    isin = _isin(row)
    text = json.dumps(row, default=str).lower()

    if ticker:
        score += 0.16
        reasons.append("ticker_present")
    if isin:
        score += 0.18
        reasons.append("isin_present")
    if "nasdaq-100" in text or "nasdaq 100" in text or "nasdaq" in text:
        score += 0.20
        reasons.append("nasdaq_index_evidence")
    if str(row.get("currency") or "").upper() == "EUR":
        score += 0.12
        reasons.append("eur_currency")
    if "accumulating" in text:
        score += 0.10
        reasons.append("accumulating_share_class")
    if any(platform.lower() == "lightyear" for platform in _platforms(row)):
        score += 0.10
        reasons.append("lightyear_platform_evidence")
    if len(set(source_files)) > 1:
        score += 0.12
        reasons.append("multiple_local_sources")
    if row.get("provider"):
        score += 0.06
        reasons.append("provider_present")
    ter = _as_float(row.get("ter_or_fee"))
    if ter is not None and ter <= 0.35:
        score += 0.06
        reasons.append("reasonable_ter")
    if row.get("priority_score") is not None:
        score += 0.10
        reasons.append("local_instrument_priority_score_present")
    if _provider_symbol(row, ticker):
        score += 0.10
        reasons.append("public_provider_symbol_present")
    if any("stock_fund_etf_instrument_universe.local.json" in item for item in source_files):
        score += 0.12
        reasons.append("local_instrument_universe_evidence")
    if ticker == "SXRV":
        score += 0.06
        reasons.append("sxrv_explicit_growth_candidate_in_local_universe")

    return round(min(score, 1.0), 4), reasons


def resolve_etf_identity(
    query: str = "GROWTH_NASDAQ_ETF",
    *,
    current_date: str = "2026-06-20",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ETFIdentityResolverResult:
    clean_query = query.upper().strip()
    rows = [row for row in _load_candidate_rows() if _is_growth_nasdaq_candidate(row)]

    grouped: dict[str, dict[str, Any]] = {}
    source_files: dict[str, set[str]] = {}

    for row in rows:
        ticker = _ticker(row)
        if not ticker:
            continue
        existing = grouped.get(ticker, {})
        merged = {**existing, **{k: v for k, v in row.items() if v not in (None, "", [])}}
        grouped[ticker] = merged
        source_files.setdefault(ticker, set()).add(str(row.get("_source_file") or "unknown"))

    candidates: list[ETFIdentityCandidate] = []
    for ticker, row in grouped.items():
        files = sorted(source_files.get(ticker, set()))
        score, reasons = _score_candidate(row, files)
        candidates.append(
            ETFIdentityCandidate(
                asset_id=_norm(row.get("asset_id") or ticker),
                symbol=ticker,
                provider_symbol=_provider_symbol(row, ticker),
                name=_norm(row.get("name") or ticker),
                isin=_isin(row),
                source_files=files,
                currency=_norm(row.get("currency")) or None,
                platforms=_platforms(row),
                provider=_norm(row.get("provider")) or None,
                index_tracked=_norm(row.get("index_tracked")) or None,
                distribution_policy=_norm(row.get("distribution_policy")) or None,
                ter_or_fee=_as_float(row.get("ter_or_fee")),
                evidence_score=score,
                evidence_reasons=reasons,
            )
        )

    candidates = sorted(candidates, key=lambda item: item.evidence_score, reverse=True)
    best = candidates[0].to_dict() if candidates else None

    blockers: list[str] = []
    if not best:
        blockers.append("no_growth_nasdaq_etf_identity_candidate_found")
    elif not best.get("provider_symbol"):
        blockers.append("best_growth_nasdaq_etf_candidate_has_no_public_quote_symbol")

    identity_status = (
        "AUTO_IDENTITY_CANDIDATE_SELECTED_FOR_PUBLIC_QUOTE_PROBE"
        if best and not blockers
        else "AUTO_IDENTITY_UNRESOLVED"
    )

    warnings = [
        "ETF identity resolver is autonomous and read-only",
        "candidate identity evidence comes from local public/universe records, not from broker execution",
        "final real-world buy remains manual outside J.A.R.V.I.S.",
    ]
    if clean_query == "GROWTH_NASDAQ_ETF" and best:
        warnings.append(
            f"GROWTH_NASDAQ_ETF resolved to candidate {best['symbol']} / {best.get('provider_symbol')} for quote probing; identity is not an execution approval."
        )

    result = ETFIdentityResolverResult(
        status=STATUS_READY,
        current_date=current_date,
        query=clean_query,
        autonomous_identity_status=identity_status,
        best_candidate=best,
        candidates=[candidate.to_dict() for candidate in candidates],
        candidate_count=len(candidates),
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        buy_sell_request_created=False,
        order_created=False,
        trade_executed=False,
        auto_approval_enabled=False,
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return result


def format_etf_identity_resolver(result: ETFIdentityResolverResult) -> str:
    lines = [
        "J.A.R.V.I.S. ETF IDENTITY RESOLVER",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"query: {result.query}",
        f"autonomous identity status: {result.autonomous_identity_status}",
        f"candidate count: {result.candidate_count}",
        "",
        "BEST CANDIDATE:",
    ]
    if result.best_candidate:
        best = result.best_candidate
        lines.append(
            f"- {best['symbol']} / {best.get('provider_symbol')}: {best['name']}; "
            f"ISIN={best.get('isin')}; score={best.get('evidence_score')}; "
            f"reasons={', '.join(best.get('evidence_reasons') or [])}"
        )
    else:
        lines.append("- none")

    lines.extend(["", "CANDIDATES:"])
    for candidate in result.candidates:
        lines.append(
            f"- {candidate['symbol']} / {candidate.get('provider_symbol')}: "
            f"{candidate['name']}; ISIN={candidate.get('isin')}; score={candidate.get('evidence_score')}"
        )

    lines.extend(["", "WARNINGS:"])
    lines.extend(f"- {warning}" for warning in result.warnings)
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {blocker}" for blocker in (result.blockers or ["none"]))
    lines.extend(
        [
            "",
            "SAFETY:",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- buy/sell request created: {result.buy_sell_request_created}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            f"- auto approval enabled: {result.auto_approval_enabled}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--etf-identity-resolver", action="store_true")
    parser.add_argument("--query", default="GROWTH_NASDAQ_ETF")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args, _unknown = parser.parse_known_args(argv)

    result = resolve_etf_identity(
        query=args.query,
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_etf_identity_resolver(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
