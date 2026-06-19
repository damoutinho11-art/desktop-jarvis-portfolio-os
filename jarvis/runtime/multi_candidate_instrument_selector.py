from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from jarvis.runtime.correlation_risk_model import build_correlation_risk_model_result
from jarvis.runtime.dynamic_quality_allocator import build_dynamic_quality_allocator_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.stock_specific_public_evidence import build_stock_specific_public_evidence_result
from jarvis.runtime.tradable_candidate_universe_gate import build_tradable_candidate_universe_gate_result

STATUS_READY = "JARVIS_V91_0_MULTI_CANDIDATE_INSTRUMENT_SELECTOR_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V91_0_MULTI_CANDIDATE_INSTRUMENT_SELECTOR_REVIEW_REQUIRED_SAFE"


@dataclass(frozen=True)
class SelectedInstrument:
    lane: str
    candidate_id: str
    symbol: str
    name: str
    amount_eur: float
    weight_in_lane: float
    source: str
    as_of: str | None
    rationale: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MultiCandidateInstrumentSelectorResult:
    status: str
    current_date: str
    selector_ready: bool
    monthly_contribution_eur: float
    emergency_top_up_eur: float
    crypto_lane_eur: float
    etf_fund_lane_eur: float
    individual_stock_lane_eur: float
    selections: list[SelectedInstrument]
    lane_totals: dict[str, float]
    blockers: list[str]
    warnings: list[str]
    safety_check_blocked_execution: bool
    approved_for_purchase: bool
    manual_approval_required: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["selections"] = [selection.to_dict() for selection in self.selections]
        return payload


CRYPTO_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "SOL": "Solana",
    "HYPE": "Hyperliquid",
    "LINK": "Chainlink",
    "AVAX": "Avalanche",
    "NEAR": "NEAR Protocol",
    "INJ": "Injective",
    "RENDER": "Render",
    "TAO": "Bittensor",
}

ETF_NAMES = {
    "GLOBAL_CORE_ETF": "Global Core ETF",
    "VWCE": "Vanguard FTSE All-World UCITS ETF",
    "VWCE:XETRA": "Vanguard FTSE All-World UCITS ETF",
    "SXR8": "iShares Core S&P 500 UCITS ETF",
    "SXR8:XETRA": "iShares Core S&P 500 UCITS ETF",
    "SP500_CORE_ETF": "S&P 500 Core ETF",
    "IS3Q.DE": "iShares Edge MSCI World Quality Factor UCITS ETF",
    "IS3Q": "iShares Edge MSCI World Quality Factor UCITS ETF",
    "QUALITY_ETF": "Quality Factor ETF",
    "GROWTH_NASDAQ_ETF": "Growth / Nasdaq ETF",
    "QDVE": "iShares S&P 500 Information Technology Sector UCITS ETF",
    "QDVE:XETRA": "iShares S&P 500 Information Technology Sector UCITS ETF",
    "TECHNOLOGY_TILT_ETF": "Technology Tilt ETF",
}


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _money(value: Any) -> float:
    try:
        return round(float(value), 2)
    except Exception:
        return 0.0


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = str(item).strip().upper()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def _first_available(candidates: list[str], preferred: list[str]) -> str | None:
    available = {candidate.upper(): candidate.upper() for candidate in candidates}
    for symbol in preferred:
        if symbol.upper() in available:
            return available[symbol.upper()]
    return candidates[0].upper() if candidates else None


def _candidate_id(symbol: str) -> str:
    return symbol.lower().replace(":", "_").replace(".", "_")


def _lane_total(selections: list[SelectedInstrument], lane: str) -> float:
    return round(sum(item.amount_eur for item in selections if item.lane == lane), 2)


def _add_selection(
    selections: list[SelectedInstrument],
    *,
    lane: str,
    symbol: str,
    name: str,
    amount: float,
    lane_amount: float,
    source: str,
    as_of: str | None,
    rationale: list[str],
    warnings: list[str],
) -> None:
    if amount <= 0:
        return

    weight = 0.0 if lane_amount <= 0 else round(amount / lane_amount, 4)
    selections.append(
        SelectedInstrument(
            lane=lane,
            candidate_id=_candidate_id(symbol),
            symbol=symbol,
            name=name,
            amount_eur=round(amount, 2),
            weight_in_lane=weight,
            source=source,
            as_of=as_of,
            rationale=rationale,
            warnings=warnings,
        )
    )



def _ordered_available(candidates: list[str], preferred: list[str]) -> list[str]:
    available = _dedupe(candidates)
    ordered: list[str] = []

    for symbol in preferred:
        clean = symbol.upper()
        if clean in available and clean not in ordered:
            ordered.append(clean)

    for symbol in available:
        if symbol not in ordered:
            ordered.append(symbol)

    return ordered


def _profile_weights(count: int, profile: str) -> list[float]:
    if count <= 1:
        return [1.0]

    if profile == "etf_fund":
        core_weight = 0.80
        satellite_count = count - 1
        satellite_raw = [0.70 ** index for index in range(satellite_count)]
        satellite_total = sum(satellite_raw)
        return [core_weight] + [
            round((1.0 - core_weight) * raw / satellite_total, 8)
            for raw in satellite_raw
        ]

    decay = 2.0 / 3.0 if profile == "crypto" else 0.55
    raw_weights = [decay ** index for index in range(count)]
    total = sum(raw_weights)
    return [round(raw / total, 8) for raw in raw_weights]


def _split_by_weights(amount: float, weights: list[float]) -> list[float]:
    if not weights:
        return []

    pieces: list[float] = []
    for weight in weights[:-1]:
        pieces.append(round(amount * weight, 2))
    pieces.append(round(amount - sum(pieces), 2))
    return pieces


def _decide_candidate_count(
    *,
    amount: float,
    candidates: list[str],
    profile: str,
    minimum_practical_amount_eur: float,
) -> int:
    if amount <= 0 or not candidates:
        return 0

    chosen_count = 1
    for possible_count in range(1, len(candidates) + 1):
        weights = _profile_weights(possible_count, profile)
        pieces = _split_by_weights(amount, weights)
        if pieces and min(pieces) >= minimum_practical_amount_eur:
            chosen_count = possible_count
        else:
            break

    return chosen_count


def _select_crypto(
    *,
    amount: float,
    candidates: list[str],
    current_date: str,
) -> tuple[list[SelectedInstrument], list[str]]:
    selections: list[SelectedInstrument] = []
    blockers: list[str] = []

    ordered = _ordered_available(
        candidates,
        ["BTC", "ETH", "SOL", "LINK", "HYPE", "AVAX", "NEAR", "INJ", "RENDER", "TAO"],
    )
    if amount <= 0:
        return selections, blockers
    if not ordered:
        return selections, ["crypto_lane_has_amount_but_no_candidates"]

    target_count = _decide_candidate_count(
        amount=amount,
        candidates=ordered,
        profile="crypto",
        minimum_practical_amount_eur=25.0,
    )

    selected_symbols = ordered[:target_count]
    weights = _profile_weights(len(selected_symbols), "crypto")
    amounts = _split_by_weights(amount, weights)

    for index, symbol in enumerate(selected_symbols):
        role = "core crypto exposure" if index == 0 else "diversifying crypto exposure"
        _add_selection(
            selections,
            lane="crypto",
            symbol=symbol,
            name=CRYPTO_NAMES.get(symbol, symbol),
            amount=amounts[index],
            lane_amount=amount,
            source="public crypto evidence + tradable candidate universe",
            as_of=current_date,
            rationale=[
                f"{symbol} is selected as {role}",
                "candidate count is decided dynamically from ranked availability, lane size, and minimum practical buy size",
            ],
            warnings=[
                "crypto lane remains capped at 20% of monthly contribution",
                "crypto remains volatile and manual approval is required",
            ],
        )

    return selections, blockers


def _select_etf_fund(
    *,
    amount: float,
    candidates: list[str],
    current_date: str,
) -> tuple[list[SelectedInstrument], list[str]]:
    selections: list[SelectedInstrument] = []
    blockers: list[str] = []

    ordered = _ordered_available(
        candidates,
        [
            "GLOBAL_CORE_ETF",
            "VWCE",
            "VWCE:XETRA",
            "SXR8",
            "SXR8:XETRA",
            "SP500_CORE_ETF",
            "QUALITY_ETF",
            "IS3Q.DE",
            "IS3Q",
            "QDVE",
            "QDVE:XETRA",
            "GROWTH_NASDAQ_ETF",
            "TECHNOLOGY_TILT_ETF",
        ],
    )
    if amount <= 0:
        return selections, blockers
    if not ordered:
        return selections, ["etf_fund_lane_has_amount_but_no_candidates"]

    target_count = _decide_candidate_count(
        amount=amount,
        candidates=ordered,
        profile="etf_fund",
        minimum_practical_amount_eur=50.0,
    )

    selected_symbols = ordered[:target_count]
    weights = _profile_weights(len(selected_symbols), "etf_fund")
    amounts = _split_by_weights(amount, weights)

    for index, symbol in enumerate(selected_symbols):
        role = "core ETF/fund base allocation" if index == 0 else "controlled ETF/fund satellite"
        _add_selection(
            selections,
            lane="etf_fund",
            symbol=symbol,
            name=ETF_NAMES.get(symbol, symbol),
            amount=amounts[index],
            lane_amount=amount,
            source="public ETF/fund universe + freshness gate",
            as_of=current_date,
            rationale=[
                f"{symbol} is selected as {role}",
                "candidate count is decided dynamically from ranked availability, lane size, and minimum practical buy size",
            ],
            warnings=[
                "manual platform/instrument check still required before any buy",
                "ETF/fund satellites should not override the core allocation",
            ],
        )

    return selections, blockers


def _select_stock(
    *,
    amount: float,
    candidates: list[str],
    stock_evidence: Mapping[str, Any],
) -> tuple[list[SelectedInstrument], list[str]]:
    selections: list[SelectedInstrument] = []
    blockers: list[str] = []

    if amount <= 0:
        return selections, blockers

    top_symbol = stock_evidence.get("top_stock_symbol")
    ordered = _ordered_available(
        ([str(top_symbol)] if top_symbol else []) + list(candidates),
        ["MSFT", "META", "AAPL", "NVDA", "GOOGL", "AMZN", "AVGO", "ASML", "AMD", "JPM"],
    )
    if not ordered:
        return selections, ["individual_stock_lane_has_amount_but_no_candidate"]

    target_count = _decide_candidate_count(
        amount=amount,
        candidates=ordered,
        profile="stock",
        minimum_practical_amount_eur=45.0,
    )

    selected_symbols = ordered[:target_count]
    weights = _profile_weights(len(selected_symbols), "stock")
    amounts = _split_by_weights(amount, weights)

    for index, symbol in enumerate(selected_symbols):
        name = str(stock_evidence.get("top_stock_name") or symbol) if index == 0 else symbol
        as_of = stock_evidence.get("public_as_of")

        _add_selection(
            selections,
            lane="individual_stock",
            symbol=symbol,
            name=name,
            amount=amounts[index],
            lane_amount=amount,
            source="stock-specific public evidence + ranked public candidate universe",
            as_of=str(as_of) if as_of else None,
            rationale=[
                "stock candidate count is decided dynamically from ranked availability, lane size, and minimum practical buy size",
                "the current small stock sleeve can stay at one candidate, while larger future stock sleeves can split naturally",
            ],
            warnings=[
                "manual approval required",
                "equity and US large-cap exposure are already high, so stock sizing stays conservative",
            ],
        )

    return selections, blockers



@dataclass(frozen=True)
class CandidateScore:
    lane: str
    symbol: str
    name: str
    score: float
    source: str
    as_of: str | None
    components: dict[str, float]
    rationale: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductInstrumentSummary:
    current_date: str
    selections: list[SelectedInstrument]
    lane_totals: dict[str, float]
    candidate_scores: list[CandidateScore]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_date": self.current_date,
            "selections": [item.to_dict() for item in self.selections],
            "lane_totals": dict(self.lane_totals),
            "candidate_scores": [item.to_dict() for item in self.candidate_scores],
            "warnings": list(self.warnings),
        }


STOCK_NAMES = {
    "MSFT": "Microsoft Corporation",
    "META": "Meta Platforms",
    "AAPL": "Apple",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "AVGO": "Broadcom",
    "ASML": "ASML Holding",
    "AMD": "Advanced Micro Devices",
    "JPM": "JPMorgan Chase",
}

FAST_CRYPTO_CANDIDATES = ["BTC", "ETH", "SOL", "LINK", "HYPE", "AVAX", "NEAR", "INJ", "RENDER", "TAO"]
FAST_ETF_CANDIDATES = ["GLOBAL_CORE_ETF", "VWCE", "SXR8", "IS3Q.DE", "QUALITY_ETF", "QDVE", "GROWTH_NASDAQ_ETF"]
FAST_STOCK_CANDIDATES = ["MSFT", "META", "AAPL", "NVDA", "GOOGL", "AMZN", "AVGO", "ASML", "AMD", "JPM"]


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _candidate_name_for_lane(lane: str, symbol: str) -> str:
    clean = symbol.upper()
    if lane == "crypto":
        return CRYPTO_NAMES.get(clean, clean)
    if lane == "etf_fund":
        return ETF_NAMES.get(clean, clean)
    return STOCK_NAMES.get(clean, clean)


def _feature_score(lane: str, symbol: str, rank_index: int, lane_amount: float) -> CandidateScore:
    clean = symbol.upper()

    if lane == "crypto":
        profiles = {
            "BTC": {"core": 1.00, "liquidity": 1.00, "maturity": 1.00, "diversification": 0.75, "risk": 0.15},
            "ETH": {"core": 0.88, "liquidity": 0.95, "maturity": 0.88, "diversification": 0.88, "risk": 0.25},
            "SOL": {"core": 0.55, "liquidity": 0.80, "maturity": 0.55, "diversification": 0.78, "risk": 0.45},
            "LINK": {"core": 0.42, "liquidity": 0.70, "maturity": 0.60, "diversification": 0.82, "risk": 0.50},
            "HYPE": {"core": 0.35, "liquidity": 0.62, "maturity": 0.35, "diversification": 0.90, "risk": 0.65},
        }
        f = profiles.get(clean, {"core": 0.30, "liquidity": 0.50, "maturity": 0.35, "diversification": 0.60, "risk": 0.65})
        score = (
            0.34 * f["core"]
            + 0.24 * f["liquidity"]
            + 0.20 * f["maturity"]
            + 0.17 * f["diversification"]
            - 0.12 * f["risk"]
        )
        rationale = [
            "crypto candidate is scored from core role, liquidity, maturity, diversification value, and risk",
            "candidate order is score-driven, not a fixed BTC/ETH-only rule",
        ]
        warnings = ["crypto remains capped at the lane level and requires manual approval"]
        source = "fast public crypto candidate scoring model"

    elif lane == "etf_fund":
        profiles = {
            "GLOBAL_CORE_ETF": {"broadness": 1.00, "core": 1.00, "practicality": 0.95, "tilt": 0.40, "overlap": 0.15},
            "VWCE": {"broadness": 0.98, "core": 0.95, "practicality": 0.95, "tilt": 0.35, "overlap": 0.18},
            "SXR8": {"broadness": 0.70, "core": 0.75, "practicality": 0.92, "tilt": 0.45, "overlap": 0.50},
            "IS3Q.DE": {"broadness": 0.78, "core": 0.60, "practicality": 0.85, "tilt": 0.75, "overlap": 0.38},
            "QUALITY_ETF": {"broadness": 0.72, "core": 0.55, "practicality": 0.82, "tilt": 0.80, "overlap": 0.40},
            "QDVE": {"broadness": 0.45, "core": 0.35, "practicality": 0.75, "tilt": 0.85, "overlap": 0.70},
            "GROWTH_NASDAQ_ETF": {"broadness": 0.50, "core": 0.40, "practicality": 0.72, "tilt": 0.82, "overlap": 0.68},
        }
        f = profiles.get(clean, {"broadness": 0.50, "core": 0.40, "practicality": 0.65, "tilt": 0.50, "overlap": 0.55})
        score = (
            0.35 * f["broadness"]
            + 0.28 * f["core"]
            + 0.17 * f["practicality"]
            + 0.14 * f["tilt"]
            - 0.10 * f["overlap"]
        )
        rationale = [
            "ETF/fund candidate is scored from broadness, core suitability, practicality, tilt usefulness, and overlap risk",
            "core exposure is favored, but quality/growth tilts can earn allocation when the lane amount supports them",
        ]
        warnings = ["manual platform and exact instrument check remains required"]
        source = "fast public ETF/fund candidate scoring model"

    else:
        rank_score = max(0.0, 1.0 - (rank_index * 0.055))
        profiles = {
            "MSFT": {"quality": 0.96, "liquidity": 0.98, "evidence": 0.95, "single_name_risk": 0.35},
            "META": {"quality": 0.90, "liquidity": 0.96, "evidence": 0.88, "single_name_risk": 0.42},
            "AAPL": {"quality": 0.88, "liquidity": 0.98, "evidence": 0.86, "single_name_risk": 0.40},
            "NVDA": {"quality": 0.92, "liquidity": 0.98, "evidence": 0.88, "single_name_risk": 0.58},
            "GOOGL": {"quality": 0.88, "liquidity": 0.96, "evidence": 0.86, "single_name_risk": 0.42},
        }
        f = profiles.get(clean, {"quality": 0.75, "liquidity": 0.80, "evidence": 0.72, "single_name_risk": 0.50})
        score = (
            0.30 * rank_score
            + 0.28 * f["quality"]
            + 0.20 * f["evidence"]
            + 0.12 * f["liquidity"]
            - 0.14 * f["single_name_risk"]
        )
        rationale = [
            "stock candidate is scored from rank quality, public evidence, business quality, liquidity, and single-name risk",
            "small stock lanes stay concentrated unless the amount supports practical diversification",
        ]
        warnings = ["single-stock exposure requires manual approval and remains conservative"]
        source = "fast stock-specific public evidence scoring model"

    components = {key: round(float(value), 4) for key, value in f.items()}
    components["rank_position_score"] = round(max(0.0, 1.0 - (rank_index * 0.055)), 4)

    return CandidateScore(
        lane=lane,
        symbol=clean,
        name=_candidate_name_for_lane(lane, clean),
        score=_clamp_score(score),
        source=source,
        as_of=None,
        components=components,
        rationale=rationale,
        warnings=warnings,
    )


def score_lane_candidates(lane: str, candidates: list[str], lane_amount: float) -> list[CandidateScore]:
    scored = [
        _feature_score(lane, symbol, index, lane_amount)
        for index, symbol in enumerate(_dedupe(candidates))
    ]
    return sorted(scored, key=lambda item: item.score, reverse=True)


def _weights_from_candidate_scores(scored: list[CandidateScore]) -> list[float]:
    if not scored:
        return []
    raw = [max(0.01, item.score) ** 2 for item in scored]
    total = sum(raw)
    return [round(value / total, 8) for value in raw]


def _dynamic_count_from_scores(
    *,
    amount: float,
    scored: list[CandidateScore],
    minimum_practical_amount_eur: float,
    minimum_relative_score: float,
) -> int:
    if amount <= 0 or not scored:
        return 0

    chosen = 1
    top_score = scored[0].score
    for count in range(1, len(scored) + 1):
        subset = scored[:count]
        if subset[-1].score < top_score * minimum_relative_score:
            break
        pieces = _split_by_weights(amount, _weights_from_candidate_scores(subset))
        if pieces and min(pieces) >= minimum_practical_amount_eur:
            chosen = count
        else:
            break
    return chosen


def _add_scored_lane_selections(
    selections: list[SelectedInstrument],
    *,
    lane: str,
    amount: float,
    scored: list[CandidateScore],
    current_date: str,
    minimum_practical_amount_eur: float,
    minimum_relative_score: float,
) -> None:
    count = _dynamic_count_from_scores(
        amount=amount,
        scored=scored,
        minimum_practical_amount_eur=minimum_practical_amount_eur,
        minimum_relative_score=minimum_relative_score,
    )
    chosen = scored[:count]
    amounts = _split_by_weights(amount, _weights_from_candidate_scores(chosen))

    for index, item in enumerate(chosen):
        _add_selection(
            selections,
            lane=lane,
            symbol=item.symbol,
            name=item.name,
            amount=amounts[index],
            lane_amount=amount,
            source=item.source,
            as_of=current_date,
            rationale=[
                *item.rationale,
                f"candidate score {item.score:.0%}; selected count is dynamic from score, lane size, and minimum practical buy size",
            ],
            warnings=item.warnings,
        )


def build_fast_product_instrument_summary(
    *,
    crypto_lane_eur: float,
    etf_fund_lane_eur: float,
    individual_stock_lane_eur: float,
    current_date: str = "2026-06-18",
) -> ProductInstrumentSummary:
    candidate_scores: list[CandidateScore] = []
    selections: list[SelectedInstrument] = []

    crypto_scores = score_lane_candidates("crypto", FAST_CRYPTO_CANDIDATES, crypto_lane_eur)
    etf_scores = score_lane_candidates("etf_fund", FAST_ETF_CANDIDATES, etf_fund_lane_eur)
    stock_scores = score_lane_candidates("individual_stock", FAST_STOCK_CANDIDATES, individual_stock_lane_eur)

    candidate_scores.extend(crypto_scores)
    candidate_scores.extend(etf_scores)
    candidate_scores.extend(stock_scores)

    _add_scored_lane_selections(
        selections,
        lane="crypto",
        amount=round(float(crypto_lane_eur or 0.0), 2),
        scored=crypto_scores,
        current_date=current_date,
        minimum_practical_amount_eur=25.0,
        minimum_relative_score=0.70,
    )
    _add_scored_lane_selections(
        selections,
        lane="etf_fund",
        amount=round(float(etf_fund_lane_eur or 0.0), 2),
        scored=etf_scores,
        current_date=current_date,
        minimum_practical_amount_eur=60.0,
        minimum_relative_score=0.62,
    )
    _add_scored_lane_selections(
        selections,
        lane="individual_stock",
        amount=round(float(individual_stock_lane_eur or 0.0), 2),
        scored=stock_scores,
        current_date=current_date,
        minimum_practical_amount_eur=45.0,
        minimum_relative_score=0.72,
    )

    return ProductInstrumentSummary(
        current_date=current_date,
        selections=selections,
        lane_totals={
            "crypto": _lane_total(selections, "crypto"),
            "etf_fund": _lane_total(selections, "etf_fund"),
            "individual_stock": _lane_total(selections, "individual_stock"),
        },
        candidate_scores=candidate_scores,
        warnings=[
            "fast product summary uses dynamic candidate scoring and does not rebuild heavy runtime gates",
            "manual approval remains required; no order or trade is created",
        ],
    )




def build_multi_candidate_instrument_selector_result(
    current_date: str = "2026-06-18",
) -> MultiCandidateInstrumentSelectorResult:
    allocator = _plain(build_dynamic_quality_allocator_result(current_date=current_date))
    universe = _plain(build_tradable_candidate_universe_gate_result(current_date=current_date))
    stock_evidence = _plain(build_stock_specific_public_evidence_result(current_date=current_date))
    correlation = _plain(build_correlation_risk_model_result(current_date=current_date))

    safety = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety and "No execution action was taken" in safety

    monthly = _money(allocator.get("monthly_contribution_eur"))
    emergency = _money(allocator.get("emergency_top_up_eur"))
    crypto_amount = _money(allocator.get("crypto_eur"))
    etf_amount = _money(allocator.get("etf_fund_eur"))
    stock_amount = _money(allocator.get("individual_stock_eur"))

    blockers: list[str] = []
    if not allocator.get("allocator_ready"):
        blockers.append("dynamic_quality_allocator_not_ready")
    if not universe.get("universe_gate_ready"):
        blockers.append("tradable_candidate_universe_not_ready")
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    selections: list[SelectedInstrument] = []

    crypto_selections, crypto_blockers = _select_crypto(
        amount=crypto_amount,
        candidates=list(universe.get("crypto_candidates", []) or []),
        current_date=current_date,
    )
    selections.extend(crypto_selections)
    blockers.extend(crypto_blockers)

    etf_selections, etf_blockers = _select_etf_fund(
        amount=etf_amount,
        candidates=list(universe.get("etf_candidates", []) or []),
        current_date=current_date,
    )
    selections.extend(etf_selections)
    blockers.extend(etf_blockers)

    stock_selections, stock_blockers = _select_stock(
        amount=stock_amount,
        candidates=list(universe.get("stock_candidates", []) or []),
        stock_evidence=stock_evidence,
    )
    selections.extend(stock_selections)
    blockers.extend(stock_blockers)

    lane_totals = {
        "crypto": _lane_total(selections, "crypto"),
        "etf_fund": _lane_total(selections, "etf_fund"),
        "individual_stock": _lane_total(selections, "individual_stock"),
    }

    if round(lane_totals["crypto"], 2) != round(crypto_amount, 2):
        blockers.append("crypto_selection_total_mismatch")
    if round(lane_totals["etf_fund"], 2) != round(etf_amount, 2):
        blockers.append("etf_fund_selection_total_mismatch")
    if round(lane_totals["individual_stock"], 2) != round(stock_amount, 2):
        blockers.append("individual_stock_selection_total_mismatch")

    crypto_policy_cap = round(monthly * 0.20, 2)
    if crypto_amount > crypto_policy_cap:
        blockers.append("crypto_selection_exceeds_twenty_percent_cap")

    exposure = correlation.get("exposure_weights", {}) or {}
    equity_weight = float(exposure.get("equity", 0.0) or 0.0)
    us_large_cap_weight = float(exposure.get("us_large_cap", 0.0) or 0.0)

    warnings = [
        "recommendation only; no purchase is approved",
        "manual approval remains required before any real-world buy",
        "no broker, credentials, buy request, order, or trade path is enabled",
    ]
    if equity_weight >= 0.90:
        warnings.append("equity exposure is already high; stock sleeve remains conservative")
    if us_large_cap_weight >= 0.60:
        warnings.append("US large-cap exposure is already high; avoid aggressive single-stock sizing")

    ready = not blockers

    return MultiCandidateInstrumentSelectorResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        selector_ready=ready,
        monthly_contribution_eur=monthly,
        emergency_top_up_eur=emergency,
        crypto_lane_eur=crypto_amount,
        etf_fund_lane_eur=etf_amount,
        individual_stock_lane_eur=stock_amount,
        selections=selections,
        lane_totals=lane_totals,
        blockers=list(dict.fromkeys(blockers)),
        warnings=list(dict.fromkeys(warnings)),
        safety_check_blocked_execution=safety_blocked,
        approved_for_purchase=False,
        manual_approval_required=True,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
    )


def format_multi_candidate_instrument_selector(
    result: MultiCandidateInstrumentSelectorResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. MULTI-CANDIDATE INSTRUMENT SELECTOR",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"selector ready: {result.selector_ready}",
        f"monthly contribution EUR: {result.monthly_contribution_eur:.2f}",
        f"emergency top-up EUR: {result.emergency_top_up_eur:.2f}",
        "lane amounts:",
        f"- crypto EUR: {result.crypto_lane_eur:.2f}",
        f"- ETF/fund EUR: {result.etf_fund_lane_eur:.2f}",
        f"- individual stock EUR: {result.individual_stock_lane_eur:.2f}",
        "selected manual instruments:",
    ]

    if result.selections:
        for item in result.selections:
            lines.append(
                f"- {item.lane}: {item.symbol} / {item.name} -> EUR {item.amount_eur:.2f} "
                f"({item.weight_in_lane:.0%} of lane)"
            )
            lines.append(f"  source: {item.source}")
            lines.append(f"  as of: {item.as_of or 'not available'}")
            for reason in item.rationale:
                lines.append(f"  rationale: {reason}")
            for warning in item.warnings:
                lines.append(f"  warning: {warning}")
    else:
        lines.append("- none")

    lines.append("lane totals:")
    for lane, total in result.lane_totals.items():
        lines.append(f"- {lane}: EUR {total:.2f}")

    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings or ["none"])
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.extend(
        [
            "Safety:",
            f"- approved for purchase: {result.approved_for_purchase}",
            f"- manual approval required: {result.manual_approval_required}",
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--multi-candidate-instrument-selector", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    args = parser.parse_args(argv)

    result = build_multi_candidate_instrument_selector_result(current_date=args.current_date)
    print(format_multi_candidate_instrument_selector(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
