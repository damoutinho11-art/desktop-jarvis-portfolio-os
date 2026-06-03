"""Deterministic local allocation engine for J.A.R.V.I.S. Portfolio OS v0."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from etf_scoring import ETF_SLEEVES, load_etf_universe, score_etf_universe


APPROVAL_NOTICE = "Manual approval required. No trades executed."


@dataclass(frozen=True)
class SleeveStatus:
    name: str
    current_value_cents: int
    current_weight: float
    target_weight: float
    gap: float


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def cents(value: float | int) -> int:
    return int(round(float(value) * 100))


def euros(value_cents: int) -> float:
    return round(value_cents / 100, 2)


def format_eur(value_cents: int) -> str:
    return f"€{euros(value_cents):,.2f}"


def allocations_to_euros(allocations_cents: dict[str, int]) -> dict[str, float]:
    return {
        name: euros(amount)
        for name, amount in sorted(allocations_cents.items())
        if amount > 0
    }


def validate_constitution(constitution: dict[str, Any]) -> None:
    required_flags = [
        ("manual_approval_required", True),
        ("no_auto_trading", True),
        ("no_broker_connections", True),
        ("no_api_keys", True),
        ("no_network_calls", True),
    ]
    for key, expected in required_flags:
        if constitution.get(key) is not expected:
            raise ValueError(f"Constitution safety flag must be {key}={expected}.")

    rules = constitution.get("rules", {})
    for key, value in rules.items():
        if value is not True:
            raise ValueError(f"Constitution rule must be true: {key}.")

    targets = constitution.get("target_weights", {})
    target_total = round(sum(float(weight) for weight in targets.values()), 6)
    if target_total != 1.0:
        raise ValueError(f"Target weights must sum to 1.0. Current sum: {target_total}.")

    routes = constitution.get("asset_routes", {})
    missing_routes = sorted(set(targets) - set(routes))
    if missing_routes:
        raise ValueError(f"Missing asset routes: {', '.join(missing_routes)}.")

    legacy_policy = constitution.get("legacy_holding_policy", {})
    for name, policy in legacy_policy.items():
        if policy.get("maps_to") not in targets:
            raise ValueError(f"Legacy holding {name} maps to an unknown sleeve.")
        if policy.get("new_buys_allowed") is not False:
            raise ValueError(f"Legacy holding {name} must not allow new buys.")
        if policy.get("sell_allowed_without_explicit_user_approval") is not False:
            raise ValueError(
                f"Legacy holding {name} must require explicit approval before selling."
            )


def investable_holdings(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> dict[str, int]:
    targets = constitution["target_weights"]
    holdings = portfolio_state.get("holdings", {})
    mapped_holdings = {name: cents(holdings.get(name, 0.0)) for name in targets}

    legacy_holdings = portfolio_state.get("legacy_holdings", {})
    legacy_policy = constitution.get("legacy_holding_policy", {})
    for name, value in legacy_holdings.items():
        if value is None:
            continue
        policy = legacy_policy.get(name)
        if not policy:
            continue
        mapped_holdings[policy["maps_to"]] += cents(value)

    return mapped_holdings


def legacy_holdings_status(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> list[dict[str, Any]]:
    legacy_holdings = portfolio_state.get("legacy_holdings", {})
    legacy_policy = constitution.get("legacy_holding_policy", {})
    statuses = []

    for name in sorted(legacy_policy):
        policy = legacy_policy[name]
        value = legacy_holdings.get(name)
        known_value_cents = None if value is None else cents(value)
        statuses.append(
            {
                "name": name,
                "value_cents": known_value_cents,
                "classification": policy["classification"],
                "maps_to": policy["maps_to"],
                "new_buys_allowed": policy["new_buys_allowed"],
                "sell_allowed_without_explicit_user_approval": policy[
                    "sell_allowed_without_explicit_user_approval"
                ],
            }
        )

    return statuses


def current_statuses(
    constitution: dict[str, Any], holdings_cents: dict[str, int]
) -> list[SleeveStatus]:
    targets = constitution["target_weights"]
    investable_total = sum(holdings_cents.values())

    statuses: list[SleeveStatus] = []
    for name, target_weight in targets.items():
        current_value = holdings_cents.get(name, 0)
        current_weight = current_value / investable_total if investable_total else 0.0
        statuses.append(
            SleeveStatus(
                name=name,
                current_value_cents=current_value,
                current_weight=current_weight,
                target_weight=float(target_weight),
                gap=float(target_weight) - current_weight,
            )
        )
    return statuses


def etf_scores_for_holdings(
    constitution: dict[str, Any],
    holdings_cents: dict[str, int],
    etf_universe_path: str | Path = "etf_universe.json",
) -> dict[str, dict[str, Any]]:
    total = sum(holdings_cents.values())
    current_weights = {
        name: (holdings_cents.get(name, 0) / total if total else 0.0)
        for name in constitution["target_weights"]
    }
    try:
        universe = load_etf_universe(etf_universe_path)
    except FileNotFoundError:
        return {}
    return score_etf_universe(universe, current_weights)


def platform_readiness_issues(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> list[str]:
    routes = constitution.get("asset_routes", {})
    platform_status = portfolio_state.get("platform_status", {})
    blocked_routes = []

    for route in sorted(set(routes.values())):
        if route in {"cash", "manual_review"}:
            continue
        if not route_is_ready(route, platform_status):
            blocked_routes.append(route)

    return blocked_routes


def legacy_cleanup_issues(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> tuple[bool, bool]:
    legacy_policy = constitution.get("legacy_holding_policy", {})
    legacy_holdings = portfolio_state.get("legacy_holdings", {})
    has_pending_value = False
    cleanup_incomplete = False

    for name in legacy_policy:
        value = legacy_holdings.get(name)
        if value is None:
            has_pending_value = True
            cleanup_incomplete = True
        elif cents(value) != 0:
            cleanup_incomplete = True

    return has_pending_value, cleanup_incomplete


def reserve_has_legacy_transition_reason(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> bool:
    legacy_cash_name = "lhv_growth_cash_pending_settlement"
    legacy_value = portfolio_state.get("legacy_holdings", {}).get(legacy_cash_name)
    policy = constitution.get("legacy_holding_policy", {}).get(legacy_cash_name, {})
    return legacy_value is None or (
        cents(legacy_value) > 0 and policy.get("classification") == "legacy_cash"
    )


def sleeve_band_issues(statuses: list[SleeveStatus]) -> list[str]:
    issues = []
    for status in statuses:
        if status.name == "tactical_reserve":
            max_weight = 0.10
        elif status.name == "discovery":
            max_weight = status.target_weight
        else:
            max_weight = status.target_weight + 0.05

        if status.current_weight > max_weight:
            issues.append(
                f"{status.name} is above its max band "
                f"({status.current_weight:.2%} vs {max_weight:.2%})"
            )

    return issues


def detect_portfolio_mode(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
    holdings: dict[str, int],
    statuses: list[SleeveStatus],
) -> dict[str, Any]:
    investable_total = sum(holdings.values())
    empty_sleeves = sum(1 for value in holdings.values() if value == 0)
    most_sleeves_empty = empty_sleeves > (len(holdings) / 2)

    blocked_routes = platform_readiness_issues(constitution, portfolio_state)
    has_pending_legacy, legacy_cleanup_incomplete = legacy_cleanup_issues(
        constitution, portfolio_state
    )
    tactical_value = holdings.get("tactical_reserve", 0)
    tactical_weight = tactical_value / investable_total if investable_total else 0.0
    reserve_transition_reason = reserve_has_legacy_transition_reason(
        constitution, portfolio_state
    )

    if investable_total < cents(500.0) or most_sleeves_empty:
        return {
            "mode": "construction_mode",
            "reasons": [
                "Investable value is below EUR 500 or most target sleeves are still empty."
            ],
            "guidance": "J.A.R.V.I.S. should focus on building core target exposure with manual approval.",
        }

    transition_reasons = []
    if tactical_weight > 0.10 and reserve_transition_reason:
        transition_reasons.append(
            "Tactical reserve is above 10% because legacy cash or pending settlement is still in the portfolio."
        )

    setup_reasons = []
    if blocked_routes:
        setup_reasons.append("platform routes are not ready: " + ", ".join(blocked_routes))
    if has_pending_legacy:
        setup_reasons.append("at least one legacy value is pending/null")
    if legacy_cleanup_incomplete:
        setup_reasons.append("legacy cleanup is not complete")
    if setup_reasons:
        transition_reasons.append("; ".join(setup_reasons).capitalize() + ".")

    if transition_reasons:
        return {
            "mode": "transition_mode",
            "reasons": transition_reasons,
            "guidance": "J.A.R.V.I.S. may recommend temporary tactical reserve buildup and throttled BTC fallback.",
        }

    crypto = crypto_risk_status(constitution, holdings, {}, 0)
    risk_rules = constitution.get("crypto_risk_rules", {})
    crypto_soft_max = float(risk_rules.get("btc_target", 0.10)) + 0.075
    rebalance_reasons = sleeve_band_issues(statuses)
    if crypto["total_crypto_weight"] > crypto_soft_max:
        rebalance_reasons.append(
            f"Total crypto is above soft max ({crypto['total_crypto_weight']:.2%} vs {crypto_soft_max:.2%})."
        )
    if tactical_weight > 0.10:
        rebalance_reasons.append(
            "Tactical reserve is above 10% without a transition reason."
        )

    if rebalance_reasons:
        return {
            "mode": "rebalance_watch_mode",
            "reasons": rebalance_reasons,
            "guidance": "J.A.R.V.I.S. should warn, but still not recommend automatic sells.",
        }

    return {
        "mode": "normal_weekly_mode",
        "reasons": [
            "All main platforms are ready, legacy cleanup is complete, and sleeves are within allowed bands."
        ],
        "guidance": "J.A.R.V.I.S. should allocate according to normal target gaps.",
    }


def route_is_ready(route: str, platform_status: dict[str, bool]) -> bool:
    if route in {"cash", "manual_review"}:
        return True
    return bool(platform_status.get(f"{route}_ready", False))


def route_label(route: str) -> str:
    labels = {
        "lightyear": "Lightyear",
        "lhv_crypto": "LHV Crypto",
        "kraken": "Kraken",
        "trade_republic": "Trade Republic",
        "manual_review": "Manual review",
        "cash": "Cash",
    }
    return labels.get(route, route.replace("_", " ").title())


def crypto_room_for_asset(
    asset: str,
    holdings: dict[str, int],
    executable: dict[str, int],
    final_total_cents: int,
    constitution: dict[str, Any],
) -> int:
    if asset not in {"btc", "hype", "tao"}:
        return final_total_cents

    risk_rules = constitution.get("crypto_risk_rules", {})
    btc_max = float(risk_rules.get("btc_max", 0.15))
    total_crypto_max = float(risk_rules.get("total_crypto_hard_max", 0.225))
    hype_tao_max = float(risk_rules.get("hype_tao_combined_max", 0.075))

    btc_value = holdings.get("btc", 0) + executable.get("btc", 0)
    hype_value = holdings.get("hype", 0) + executable.get("hype", 0)
    tao_value = holdings.get("tao", 0) + executable.get("tao", 0)
    total_crypto_value = btc_value + hype_value + tao_value
    hype_tao_value = hype_value + tao_value

    total_crypto_room = max(0, int(final_total_cents * total_crypto_max) - total_crypto_value)
    if asset == "btc":
        btc_room = max(0, int(final_total_cents * btc_max) - btc_value)
        return min(btc_room, total_crypto_room)

    hype_tao_room = max(0, int(final_total_cents * hype_tao_max) - hype_tao_value)
    return min(hype_tao_room, total_crypto_room)


def crypto_like_assets() -> set[str]:
    return {"btc", "hype", "tao", "discovery"}


def weekly_crypto_buy_room(
    asset: str,
    executable: dict[str, int],
    weekly_budget_cents: int,
    btc_fallback_allocated_cents: int,
    constitution: dict[str, Any],
) -> int:
    if asset not in crypto_like_assets():
        return weekly_budget_cents

    risk_rules = constitution.get("crypto_risk_rules", {})
    total_crypto_buy_cap = int(
        weekly_budget_cents
        * float(risk_rules.get("max_total_crypto_buy_fraction_of_weekly_budget", 0.50))
    )
    current_crypto_buys = sum(executable.get(name, 0) for name in crypto_like_assets())
    total_crypto_buy_room = max(0, total_crypto_buy_cap - current_crypto_buys)

    if asset != "btc":
        return total_crypto_buy_room

    btc_fallback_cap = int(
        weekly_budget_cents
        * float(risk_rules.get("max_btc_fallback_fraction_of_weekly_budget", 0.40))
    )
    btc_fallback_room = max(0, btc_fallback_cap - btc_fallback_allocated_cents)
    return min(total_crypto_buy_room, btc_fallback_room)


def executable_candidate_order(
    constitution: dict[str, Any],
    holdings: dict[str, int],
    executable: dict[str, int],
    final_total_cents: int,
) -> list[tuple[str, float, int]]:
    candidates = []
    for name, target_weight in constitution["target_weights"].items():
        if name == "tactical_reserve":
            continue
        current_value = holdings.get(name, 0) + executable.get(name, 0)
        target_value = int(round(final_total_cents * float(target_weight)))
        deficit = max(0, target_value - current_value)
        gap = float(target_weight) - (
            current_value / final_total_cents if final_total_cents else 0.0
        )
        if deficit > 0:
            candidates.append((name, gap, deficit))

    candidates.sort(key=lambda item: (-item[1], item[0]))
    return candidates


def allocate_fallback_pool(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
    holdings: dict[str, int],
    executable: dict[str, int],
    fallback_pool_cents: int,
    final_total_cents: int,
    weekly_budget_cents: int,
) -> tuple[int, list[dict[str, Any]]]:
    routes = constitution["asset_routes"]
    platform_status = portfolio_state.get("platform_status", {})
    minimums = {
        name: cents(value)
        for name, value in constitution.get("minimum_efficient_buys", {}).items()
    }
    notes = []
    remaining = fallback_pool_cents
    btc_fallback_allocated_cents = 0
    throttle_limited_assets = set()

    while remaining > 0:
        allocated_this_round = False
        for name, _gap, deficit in executable_candidate_order(
            constitution, holdings, executable, final_total_cents
        ):
            route = routes[name]
            if not route_is_ready(route, platform_status):
                continue

            risk_room = crypto_room_for_asset(
                name, holdings, executable, final_total_cents, constitution
            )
            weekly_room = weekly_crypto_buy_room(
                name,
                executable,
                weekly_budget_cents,
                btc_fallback_allocated_cents,
                constitution,
            )
            if weekly_room <= 0 and name in crypto_like_assets():
                throttle_limited_assets.add(name)

            amount = min(remaining, deficit, risk_room, weekly_room)
            minimum = minimums.get(name)
            if amount <= 0 or (minimum is not None and amount < minimum):
                continue

            executable[name] += amount
            if name == "btc":
                btc_fallback_allocated_cents += amount
            remaining -= amount
            allocated_this_round = True
            notes.append(
                {
                    "category": "fallback",
                    "asset": name,
                    "amount_cents": amount,
                    "reason": f"{name} fallback selected: {route_label(route)} is ready, {name.upper()} is underweight, and crypto risk limits allow it.",
                }
            )
            if name in crypto_like_assets() and weekly_room == amount and remaining > 0:
                throttle_limited_assets.add(name)
            break

        if not allocated_this_round:
            break

    if remaining > 0 and "btc" in throttle_limited_assets:
        notes.append(
            {
                "category": "reserve",
                "asset": "tactical_reserve",
                "amount_cents": remaining,
                "reason": f"btc fallback capped: weekly crypto throttle limited BTC buy to {format_eur(btc_fallback_allocated_cents)}. tactical_reserve used: remaining {format_eur(remaining)} held until ETF route is ready.",
            }
        )

    return remaining, notes


def calculate_ideal_allocations(
    constitution: dict[str, Any],
    holdings: dict[str, int],
    weekly_budget_cents: int,
    etf_scores: dict[str, dict[str, Any]] | None = None,
) -> dict[str, int]:
    after_total_cents = sum(holdings.values()) + weekly_budget_cents
    allocations = {name: 0 for name in constitution["target_weights"]}
    remaining = weekly_budget_cents

    deficits: list[tuple[str, float, int, float]] = []
    for status in current_statuses(constitution, holdings):
        target_value = int(round(after_total_cents * status.target_weight))
        deficit = max(0, target_value - status.current_value_cents)
        if deficit > 0:
            etf_score = 0.0
            if etf_scores and status.name in ETF_SLEEVES:
                score = etf_scores.get(status.name, {})
                if not score.get("enabled", False) or score.get("final_score", 0.0) <= 0:
                    continue
                etf_score = float(score["final_score"])
            deficits.append((status.name, status.gap, deficit, etf_score))

    deficits.sort(
        key=lambda item: (
            0 if item[0] in ETF_SLEEVES else 1,
            -item[3] if item[0] in ETF_SLEEVES else -item[1],
            item[0],
        )
    )

    for name, _gap, deficit, _etf_score in deficits:
        if remaining <= 0:
            break
        suggested = min(deficit, remaining)
        allocations[name] += suggested
        remaining -= suggested

    if remaining > 0:
        allocations["tactical_reserve"] += remaining

    return allocations


def component_driver_labels(components: dict[str, float]) -> list[str]:
    labels = {
        "allocation_gap_score": "allocation gap",
        "momentum_score": "momentum",
        "valuation_risk_score": "valuation/risk",
        "inverse_concentration_score": "concentration",
        "fee_liquidity_score": "fee/liquidity",
    }
    ranked = sorted(components.items(), key=lambda item: (-item[1], item[0]))
    return [labels[name] for name, value in ranked if value >= 70][:3]


def component_penalty_labels(score: dict[str, Any]) -> list[str]:
    components = score["score_components"]
    penalties = []
    if not score["enabled"]:
        penalties.append("disabled")
    if score["warnings"]:
        penalties.extend(score["warnings"])
    if components["allocation_gap_score"] == 0:
        penalties.append("at or above target allocation")
    if components["inverse_concentration_score"] < 50:
        penalties.append("concentration penalty")
    if components["valuation_risk_score"] < 60:
        penalties.append("valuation/risk input")
    if components["momentum_score"] < 60:
        penalties.append("momentum input")
    return penalties or ["no major scoring penalty"]


def build_etf_scoring_verdict(
    etf_scores: dict[str, dict[str, Any]],
    ideal_allocations: dict[str, int],
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
) -> dict[str, Any]:
    if not etf_scores:
        return {"selected_ideal_etf": None, "sleeves": []}

    ranked = sorted(
        etf_scores.values(), key=lambda item: (-item["final_score"], item["sleeve"])
    )
    rank_by_sleeve = {score["sleeve"]: index + 1 for index, score in enumerate(ranked)}
    selected = next(
        (
            name
            for name, amount in ideal_allocations.items()
            if name in ETF_SLEEVES and amount > 0
        ),
        None,
    )
    selected_score = etf_scores.get(selected, {}).get("final_score", 0.0)
    selected_text = (
        f"Selected ideal ETF sleeve: {selected}"
        if selected
        else "Selected ideal ETF sleeve: none"
    )

    routes = constitution.get("asset_routes", {})
    platform_status = portfolio_state.get("platform_status", {})
    sleeves = []
    for score in ranked:
        sleeve = score["sleeve"]
        route = routes.get(sleeve, "manual_review")
        route_ready = route_is_ready(route, platform_status)

        if sleeve == selected:
            reason = (
                f"{selected_text}. It has the strongest eligible ETF score after "
                "allocation gap, valuation/risk, concentration, and fee/liquidity inputs."
            )
            if not route_ready:
                reason += f" Execution is still blocked because {route_label(route)} is not ready."
        elif not score["enabled"]:
            reason = "Not selected: ETF sleeve is disabled."
        elif score["warnings"]:
            reason = "Not selected: " + "; ".join(score["warnings"])
        elif score["final_score"] < selected_score:
            reason = f"Not selected: lower score than {selected}."
        else:
            reason = "Not selected: lower allocation priority."

        if sleeve != selected and not route_ready:
            reason += f" Platform blocked: {route_label(route)} is not ready."

        sleeves.append(
            {
                "sleeve": sleeve,
                "final_score": score["final_score"],
                "rank": rank_by_sleeve[sleeve],
                "main_positive_drivers": component_driver_labels(
                    score["score_components"]
                ),
                "main_penalties": component_penalty_labels(score),
                "selected": sleeve == selected,
                "reason": reason,
            }
        )

    return {
        "selected_ideal_etf": selected,
        "selected_label": selected_text,
        "sleeves": sleeves,
    }


def calculate_executable_allocations(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
    holdings: dict[str, int],
    ideal_allocations: dict[str, int],
    weekly_budget_cents: int,
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    routes = constitution["asset_routes"]
    platform_status = portfolio_state.get("platform_status", {})
    minimums = {
        name: cents(value)
        for name, value in constitution.get("minimum_efficient_buys", {}).items()
    }

    executable = {name: 0 for name in constitution["target_weights"]}
    warnings = []
    fallback_pool_cents = 0
    final_total_cents = sum(holdings.values()) + weekly_budget_cents

    for name, amount in ideal_allocations.items():
        if amount <= 0:
            continue

        route = routes[name]
        if not route_is_ready(route, platform_status):
            fallback_pool_cents += amount
            warnings.append(
                {
                    "category": "blocked",
                    "asset": name,
                    "amount_cents": amount,
                    "reason": f"{name} blocked: {route_label(route)} platform is not ready.",
                }
            )
            continue

        minimum = minimums.get(name)
        if minimum is not None and amount < minimum:
            fallback_pool_cents += amount
            warnings.append(
                {
                    "category": "blocked",
                    "asset": name,
                    "amount_cents": amount,
                    "reason": f"{name} blocked: suggested buy is below {format_eur(minimum)} minimum efficient buy.",
                }
            )
            continue

        executable[name] += amount

    remaining_fallback, fallback_notes = allocate_fallback_pool(
        constitution,
        portfolio_state,
        holdings,
        executable,
        fallback_pool_cents,
        final_total_cents,
        weekly_budget_cents,
    )
    warnings.extend(fallback_notes)
    if remaining_fallback > 0:
        executable["tactical_reserve"] += remaining_fallback
        if not any(item.get("category") == "reserve" for item in fallback_notes):
            warnings.append(
                {
                    "category": "reserve",
                    "asset": "tactical_reserve",
                    "amount_cents": remaining_fallback,
                    "reason": f"tactical_reserve used: remaining {format_eur(remaining_fallback)} held until ETF route is ready.",
                }
            )

    return executable, warnings


def build_approval_ticket(
    portfolio_state: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    as_of = str(portfolio_state.get("as_of", "unknown"))
    portfolio_mode = result["portfolio_mode"]["mode"]

    blocked_actions = [
        {
            "asset": item["asset"],
            "amount": euros(item["amount_cents"]),
            "reason": item["reason"],
        }
        for item in result["warnings"]
        if item.get("category") == "blocked"
    ]
    fallback_actions = [
        {
            "asset": item["asset"],
            "amount": euros(item["amount_cents"]),
            "reason": item["reason"],
        }
        for item in result["warnings"]
        if item.get("category") == "fallback"
    ]
    reserve_actions = [
        {
            "asset": item["asset"],
            "amount": euros(item["amount_cents"]),
            "reason": item["reason"],
        }
        for item in result["warnings"]
        if item.get("category") == "reserve"
    ]

    return {
        "ticket_id": f"JARVIS-{as_of}-{portfolio_mode}",
        "timestamp": as_of,
        "as_of": as_of,
        "portfolio_mode": portfolio_mode,
        "weekly_budget": euros(result["weekly_budget_cents"]),
        "ideal_allocation": allocations_to_euros(result["ideal_allocations_cents"]),
        "executable_allocation": allocations_to_euros(
            result["executable_allocations_cents"]
        ),
        "etf_scoring_verdict": result["etf_scoring_verdict"],
        "blocked_actions": blocked_actions,
        "fallback_actions": fallback_actions,
        "reserve_actions": reserve_actions,
        "warnings": [item["reason"] for item in result["warnings"]],
        "safety_checks": [
            "Manual approval required. No trades executed.",
            "No broker connection.",
            "No API keys.",
            "No orders created.",
            "No automatic selling.",
        ],
        "approval_status": "pending_manual_approval",
        "trades_executed": False,
        "approval_notice": APPROVAL_NOTICE,
    }


def allocate_weekly_budget(
    constitution: dict[str, Any], portfolio_state: dict[str, Any]
) -> dict[str, Any]:
    validate_constitution(constitution)

    holdings = investable_holdings(constitution, portfolio_state)
    weekly_budget_cents = cents(portfolio_state["weekly_investment_budget"])
    emergency_fund_cents = cents(portfolio_state["emergency_fund"]["amount"])
    before_total_cents = sum(holdings.values())
    statuses_before = current_statuses(constitution, holdings)
    etf_scores = etf_scores_for_holdings(constitution, holdings)
    ideal_allocations = calculate_ideal_allocations(
        constitution, holdings, weekly_budget_cents, etf_scores
    )
    executable_allocations, warnings = calculate_executable_allocations(
        constitution, portfolio_state, holdings, ideal_allocations, weekly_budget_cents
    )

    ideal_projected_holdings = {
        name: holdings[name] + ideal_allocations[name] for name in holdings
    }
    executable_projected_holdings = {
        name: holdings[name] + executable_allocations[name] for name in holdings
    }

    result = {
        "currency": constitution.get("currency", "EUR"),
        "as_of": portfolio_state.get("as_of", "unknown"),
        "weekly_budget_cents": weekly_budget_cents,
        "emergency_fund_cents": emergency_fund_cents,
        "investable_before_cents": before_total_cents,
        "investable_after_cents": sum(executable_projected_holdings.values()),
        "portfolio_mode": detect_portfolio_mode(
            constitution, portfolio_state, holdings, statuses_before
        ),
        "etf_scores": etf_scores,
        "etf_scoring_verdict": build_etf_scoring_verdict(
            etf_scores, ideal_allocations, constitution, portfolio_state
        ),
        "statuses_before": statuses_before,
        "ideal_statuses_after": current_statuses(constitution, ideal_projected_holdings),
        "executable_statuses_after": current_statuses(
            constitution, executable_projected_holdings
        ),
        "ideal_allocations_cents": ideal_allocations,
        "executable_allocations_cents": executable_allocations,
        "legacy_holdings_status": legacy_holdings_status(
            constitution, portfolio_state
        ),
        "crypto_risk_status": crypto_risk_status(
            constitution, holdings, executable_allocations, weekly_budget_cents
        ),
        "transition_cash_warning": should_show_transition_cash_warning(
            constitution, portfolio_state, executable_projected_holdings
        ),
        "warnings": warnings,
        "approval_notice": APPROVAL_NOTICE,
    }
    result["approval_ticket"] = build_approval_ticket(portfolio_state, result)
    return result


def should_show_transition_cash_warning(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
    projected_holdings: dict[str, int],
) -> bool:
    total = sum(projected_holdings.values())
    if total <= 0:
        return False

    tactical_weight = projected_holdings.get("tactical_reserve", 0) / total
    if tactical_weight <= 0.10:
        return False

    legacy_cash_name = "lhv_growth_cash_pending_settlement"
    legacy_value = portfolio_state.get("legacy_holdings", {}).get(legacy_cash_name)
    policy = constitution.get("legacy_holding_policy", {}).get(legacy_cash_name, {})
    return legacy_value is None or policy.get("classification") == "legacy_cash"


def crypto_risk_status(
    constitution: dict[str, Any],
    holdings: dict[str, int],
    executable_allocations: dict[str, int],
    weekly_budget_cents: int,
) -> dict[str, Any]:
    final_total = sum(holdings.values()) + weekly_budget_cents
    risk_rules = constitution.get("crypto_risk_rules", {})
    btc_max = float(risk_rules.get("btc_max", 0.15))
    total_crypto_max = float(risk_rules.get("total_crypto_hard_max", 0.225))
    hype_tao_max = float(risk_rules.get("hype_tao_combined_max", 0.075))
    btc_fallback_fraction = float(
        risk_rules.get("max_btc_fallback_fraction_of_weekly_budget", 0.40)
    )
    total_crypto_buy_fraction = float(
        risk_rules.get("max_total_crypto_buy_fraction_of_weekly_budget", 0.50)
    )

    btc_value = holdings.get("btc", 0) + executable_allocations.get("btc", 0)
    hype_value = holdings.get("hype", 0) + executable_allocations.get("hype", 0)
    tao_value = holdings.get("tao", 0) + executable_allocations.get("tao", 0)
    total_crypto_value = btc_value + hype_value + tao_value
    hype_tao_value = hype_value + tao_value

    return {
        "btc_weight": btc_value / final_total if final_total else 0.0,
        "btc_max": btc_max,
        "btc_room_cents": max(0, int(final_total * btc_max) - btc_value),
        "total_crypto_weight": total_crypto_value / final_total if final_total else 0.0,
        "total_crypto_max": total_crypto_max,
        "total_crypto_room_cents": max(
            0, int(final_total * total_crypto_max) - total_crypto_value
        ),
        "hype_tao_weight": hype_tao_value / final_total if final_total else 0.0,
        "hype_tao_max": hype_tao_max,
        "btc_fallback_weekly_cap_cents": int(
            weekly_budget_cents * btc_fallback_fraction
        ),
        "total_crypto_buy_weekly_cap_cents": int(
            weekly_budget_cents * total_crypto_buy_fraction
        ),
    }


def classify(statuses: list[SleeveStatus]) -> tuple[list[SleeveStatus], list[SleeveStatus]]:
    underweight = [status for status in statuses if status.gap > 0.0001]
    overweight = [status for status in statuses if status.gap < -0.0001]
    underweight.sort(key=lambda status: (-status.gap, status.name))
    overweight.sort(key=lambda status: (status.gap, status.name))
    return underweight, overweight


def render_report(result: dict[str, Any]) -> str:
    before_underweight, before_overweight = classify(result["statuses_before"])

    lines = [
        "J.A.R.V.I.S. Weekly Allocation Report",
        "=" * 38,
        result["approval_notice"],
        "",
        f"Weekly budget: {format_eur(result['weekly_budget_cents'])}",
        f"Emergency fund tracked, excluded: {format_eur(result['emergency_fund_cents'])}",
        f"Investable value before allocation: {format_eur(result['investable_before_cents'])}",
        f"Projected investable value after allocation: {format_eur(result['investable_after_cents'])}",
        "",
        "Portfolio mode:",
        f"- {result['portfolio_mode']['mode']}",
    ]

    for reason in result["portfolio_mode"]["reasons"][:2]:
        lines.append(f"- {reason}")
    lines.append(f"- {result['portfolio_mode']['guidance']}")

    lines.extend(
        [
            "",
        "Ideal allocation:",
        ]
    )

    ideal_allocations = result["ideal_allocations_cents"]
    for name in sorted(ideal_allocations):
        amount = ideal_allocations[name]
        if amount > 0:
            lines.append(f"- {name}: {format_eur(amount)}")

    if not any(amount > 0 for amount in ideal_allocations.values()):
        lines.append("- No ideal buys recommended this week.")

    lines.extend(["", "Executable allocation:"])
    executable_allocations = result["executable_allocations_cents"]
    for name in sorted(executable_allocations):
        amount = executable_allocations[name]
        if amount > 0:
            lines.append(f"- {name}: {format_eur(amount)}")

    if not any(amount > 0 for amount in executable_allocations.values()):
        lines.append("- No executable buys recommended this week.")

    if result["etf_scores"]:
        lines.extend(["", "ETF scoring:"])
        for sleeve in sorted(result["etf_scores"]):
            score = result["etf_scores"][sleeve]
            components = score["score_components"]
            warnings = "; ".join(score["warnings"]) if score["warnings"] else "None."
            lines.append(
                f"- {sleeve}: current {score['current_weight']:.2%}, "
                f"target {score['target_weight']:.2%}, "
                f"gap {score['allocation_gap']:.2%}, "
                f"score {score['final_score']:.2f}, "
                f"enabled {score['enabled']}; "
                f"components gap={components['allocation_gap_score']:.2f}, "
                f"momentum={components['momentum_score']:.2f}, "
                f"valuation={components['valuation_risk_score']:.2f}, "
                f"inverse_concentration={components['inverse_concentration_score']:.2f}, "
                f"fee_liquidity={components['fee_liquidity_score']:.2f}; "
                f"warnings: {warnings}"
            )

    verdict = result.get("etf_scoring_verdict", {})
    if verdict.get("sleeves"):
        lines.extend(["", "ETF scoring verdict:", f"- {verdict['selected_label']}"])
        for item in sorted(verdict["sleeves"], key=lambda row: row["rank"]):
            drivers = ", ".join(item["main_positive_drivers"]) or "none"
            penalties = ", ".join(item["main_penalties"]) or "none"
            lines.append(
                f"- Rank {item['rank']} {item['sleeve']}: "
                f"score {item['final_score']:.2f}; "
                f"drivers: {drivers}; penalties: {penalties}; {item['reason']}"
            )

    lines.extend(["", "Legacy holdings status:"])
    if result["legacy_holdings_status"]:
        for item in result["legacy_holdings_status"]:
            value = (
                "unknown/pending"
                if item["value_cents"] is None
                else format_eur(item["value_cents"])
            )
            lines.append(
                f"- {item['name']}: {value}; legacy; "
                f"{item['classification']}; maps to {item['maps_to']}; "
                "new buys blocked; selling requires explicit user approval."
            )
    else:
        lines.append("- None.")

    lines.extend(["", "Underweight sleeves before allocation:"])
    for status in before_underweight:
        lines.append(
            f"- {status.name}: current {status.current_weight:.2%}, "
            f"target {status.target_weight:.2%}, gap {status.gap:.2%}"
        )

    lines.extend(["", "Overweight sleeves before allocation:"])
    if before_overweight:
        for status in before_overweight:
            lines.append(
                f"- {status.name}: current {status.current_weight:.2%}, "
                f"target {status.target_weight:.2%}, gap {status.gap:.2%}"
            )
    else:
        lines.append("- None.")

    if result["warnings"]:
        lines.extend(["", "Readiness, fallback, and minimum buy notes:"])
        for item in result["warnings"]:
            lines.append(
                f"- {item['asset']}: {format_eur(item['amount_cents'])}; "
                f"{item['reason']}"
            )

    crypto = result["crypto_risk_status"]
    lines.extend(
        [
            "",
            "Crypto risk status:",
            f"- BTC weight after executable allocation: {crypto['btc_weight']:.2%} "
            f"(max {crypto['btc_max']:.2%}); BTC buy room: {format_eur(crypto['btc_room_cents'])}.",
            f"- Total crypto weight: {crypto['total_crypto_weight']:.2%} "
            f"(hard max {crypto['total_crypto_max']:.2%}); total crypto room: {format_eur(crypto['total_crypto_room_cents'])}.",
            f"- HYPE + TAO weight: {crypto['hype_tao_weight']:.2%} "
            f"(max {crypto['hype_tao_max']:.2%}).",
            f"- Weekly BTC fallback cap: {format_eur(crypto['btc_fallback_weekly_cap_cents'])}; "
            f"weekly total crypto-like buy cap: {format_eur(crypto['total_crypto_buy_weekly_cap_cents'])}.",
        ]
    )

    if result["transition_cash_warning"]:
        lines.extend(
            [
                "",
                "Transition cash warning:",
                "Portfolio is in transition. Tactical reserve is temporarily high because legacy sale proceeds are awaiting deployment.",
            ]
        )

    lines.extend(
        [
            "",
            "Manual approval ticket:",
            json.dumps(result["approval_ticket"], indent=2, sort_keys=True),
        ]
    )

    lines.extend(
        [
            "",
            "Projected ideal weights after allocation:",
        ]
    )
    for status in sorted(result["ideal_statuses_after"], key=lambda item: item.name):
        lines.append(
            f"- {status.name}: {status.current_weight:.2%} "
            f"(target {status.target_weight:.2%})"
        )

    lines.extend(["", "Projected executable weights after allocation:"])
    for status in sorted(result["executable_statuses_after"], key=lambda item: item.name):
        lines.append(
            f"- {status.name}: {status.current_weight:.2%} "
            f"(target {status.target_weight:.2%})"
        )

    lines.extend(
        [
            "",
            "Safety checks:",
            "- Local calculation only.",
            "- No broker connection.",
            "- No API keys.",
            "- No orders created.",
            "- No automatic selling.",
            "",
            result["approval_notice"],
        ]
    )
    return "\n".join(lines)


def build_weekly_result(
    constitution_path: str | Path = "jarvis_constitution.json",
    portfolio_state_path: str | Path = "portfolio_state.json",
) -> dict[str, Any]:
    constitution = load_json(constitution_path)
    portfolio_state = load_json(portfolio_state_path)
    return allocate_weekly_budget(constitution, portfolio_state)


def build_weekly_report(
    constitution_path: str | Path = "jarvis_constitution.json",
    portfolio_state_path: str | Path = "portfolio_state.json",
) -> str:
    return render_report(build_weekly_result(constitution_path, portfolio_state_path))


def save_approval_ticket(
    ticket: dict[str, Any], output_dir: str | Path = "outputs"
) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    latest_path = output_path / "approval_ticket_latest.json"
    as_of = str(ticket.get("as_of", "unknown")).replace("/", "-")
    dated_path = output_path / f"approval_ticket_{as_of}.json"

    for path in [latest_path, dated_path]:
        with path.open("w", encoding="utf-8") as file:
            json.dump(ticket, file, indent=2, sort_keys=True)
            file.write("\n")

    return [latest_path, dated_path]


def decision_log_record(ticket: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": ticket["timestamp"],
        "as_of": ticket["as_of"],
        "ticket_id": ticket["ticket_id"],
        "portfolio_mode": ticket["portfolio_mode"],
        "weekly_budget": ticket["weekly_budget"],
        "ideal_allocation": ticket["ideal_allocation"],
        "executable_allocation": ticket["executable_allocation"],
        "approval_status": ticket["approval_status"],
        "trades_executed": ticket["trades_executed"],
        "main_warnings": ticket["warnings"][:3],
    }


def append_decision_log(
    ticket: dict[str, Any], path: str | Path = "outputs/decision_log.jsonl"
) -> Path:
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as file:
        json.dump(decision_log_record(ticket), file, sort_keys=True)
        file.write("\n")
    return log_path


def self_check() -> None:
    constitution = load_json("jarvis_constitution.json")
    portfolio_state = load_json("portfolio_state.json")
    result = allocate_weekly_budget(constitution, portfolio_state)

    ideal = result["ideal_allocations_cents"]
    executable = result["executable_allocations_cents"]
    warnings = result["warnings"]
    legacy_statuses = result["legacy_holdings_status"]
    portfolio_mode = result["portfolio_mode"]
    ticket = result["approval_ticket"]
    verdict = ticket["etf_scoring_verdict"]

    assert portfolio_mode["mode"] == "transition_mode"
    assert any("lightyear" in reason for reason in portfolio_mode["reasons"])
    assert any("kraken" in reason for reason in portfolio_mode["reasons"])
    assert any("legacy cleanup is not complete" in reason for reason in portfolio_mode["reasons"])
    assert any("Tactical reserve is above 10%" in reason for reason in portfolio_mode["reasons"])
    assert ideal["quality_etf"] > 0
    assert executable["global_core_etf"] == 0
    assert executable["growth_nasdaq_etf"] == 0
    assert executable["quality_etf"] == 0
    assert executable["btc"] == cents(41.54)
    assert executable["tactical_reserve"] == cents(62.31)
    assert any("quality_etf blocked: Lightyear platform is not ready." in item["reason"] for item in warnings)
    assert any("btc fallback selected: LHV Crypto is ready" in item["reason"] for item in warnings)
    assert any("btc fallback capped: weekly crypto throttle limited BTC buy to" in item["reason"] for item in warnings)
    assert result["crypto_risk_status"]["btc_weight"] <= result["crypto_risk_status"]["btc_max"]
    assert result["crypto_risk_status"]["btc_fallback_weekly_cap_cents"] == cents(41.54)
    assert result["crypto_risk_status"]["total_crypto_buy_weekly_cap_cents"] == cents(51.92)
    assert result["transition_cash_warning"] is True
    assert ticket["ticket_id"] == "JARVIS-2026-06-04-transition_mode"
    assert ticket["as_of"] == "2026-06-04"
    assert ticket["portfolio_mode"] == "transition_mode"
    assert ticket["weekly_budget"] == 103.85
    assert ticket["ideal_allocation"]["quality_etf"] == 103.85
    assert verdict["selected_ideal_etf"] == "quality_etf"
    assert verdict["selected_label"] == "Selected ideal ETF sleeve: quality_etf"
    assert verdict["sleeves"][0]["rank"] == 1
    assert verdict["sleeves"][0]["sleeve"] == "quality_etf"
    assert "strongest eligible ETF score" in verdict["sleeves"][0]["reason"]
    assert ticket["executable_allocation"]["btc"] == 41.54
    assert ticket["executable_allocation"]["tactical_reserve"] == 62.31
    assert ticket["blocked_actions"][0]["asset"] == "quality_etf"
    assert ticket["blocked_actions"][0]["amount"] == 103.85
    assert len(ticket["fallback_actions"]) == 1
    assert ticket["fallback_actions"][0]["asset"] == "btc"
    assert ticket["fallback_actions"][0]["amount"] == 41.54
    assert len(ticket["reserve_actions"]) == 1
    assert ticket["reserve_actions"][0]["asset"] == "tactical_reserve"
    assert ticket["reserve_actions"][0]["amount"] == 62.31
    assert ticket["approval_status"] == "pending_manual_approval"
    assert ticket["trades_executed"] is False
    assert ticket["approval_notice"] == APPROVAL_NOTICE
    assert "No broker connection." in ticket["safety_checks"]
    record = decision_log_record(ticket)
    assert record["ticket_id"] == ticket["ticket_id"]
    assert record["approval_status"] == "pending_manual_approval"
    assert record["trades_executed"] is False
    assert record["executable_allocation"]["btc"] == 41.54
    assert len(record["main_warnings"]) == 3
    assert len(legacy_statuses) == 4
    assert all(not item["new_buys_allowed"] for item in legacy_statuses)
    assert all(
        not item["sell_allowed_without_explicit_user_approval"]
        for item in legacy_statuses
    )
    assert result["approval_notice"] == APPROVAL_NOTICE

    numeric_legacy_state = deepcopy(portfolio_state)
    numeric_legacy_state["legacy_holdings"] = {
        "lhv_growth_sxr8": 50.0,
        "lhv_growth_iemm": 100.0,
        "lhv_growth_xcha": None,
        "lhv_growth_cash_pending_settlement": 25.0,
    }
    numeric_legacy_result = allocate_weekly_budget(constitution, numeric_legacy_state)
    numeric_before = {
        status.name: status.current_value_cents
        for status in numeric_legacy_result["statuses_before"]
    }
    assert numeric_before["global_core_etf"] == cents(150.0)
    assert numeric_before["tactical_reserve"] == cents(29.9)
