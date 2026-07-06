"""Market World Model Engine for Atlas Runtime v0.6.

This module builds interpretable state trajectories from fused market reality
and causal constraints. It is deterministic scenario simulation, not ML, price
forecasting, trading execution, or portfolio automation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


MARKET_STATE_FIELDS = (
    "attention_field",
    "liquidity_field",
    "volatility_field",
    "narrative_field",
    "institutional_flow_field",
    "retail_flow_field",
)


def market_state_space_definition() -> Dict[str, Any]:
    """Return the v0.6 continuous market state vector definition."""

    return {
        "state_type": "continuous_market_state",
        "fields": list(MARKET_STATE_FIELDS),
        "interpretation": "Market is modeled as evolving field pressure, not isolated events.",
    }


def build_market_state(
    *,
    fusion: Mapping[str, Any],
    causal: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
    t: int = 0,
) -> Dict[str, Any]:
    """Create MarketState(t) from fused reality and v0.5 causal constraints."""

    flow = causal.get("flow_propagation", {}) if isinstance(causal.get("flow_propagation"), Mapping) else {}
    return {
        "t": t,
        "attention_field": _clamp(fusion.get("attention_pressure", 0)),
        "liquidity_field": _clamp(fusion.get("liquidity_score", 50)),
        "volatility_field": _level_to_score(str(fusion.get("volatility_regime", "Low"))),
        "narrative_field": _clamp(fusion.get("narrative_intensity", 0)),
        "institutional_flow_field": _clamp(flow.get("institutional_flow_strength", 0)),
        "retail_flow_field": _clamp(flow.get("retail_flow_strength", 0)),
        "memory_context": memory_summary.get("dominant_state", "NORMAL"),
        "state_type": "continuous_market_state",
    }


def attention_to_liquidity(
    *,
    attention_field: int | float,
    liquidity_field: int | float,
    narrative_credibility: int | float,
    institutional_participation: int | float,
    market_regime: str = "NORMAL",
) -> Dict[str, Any]:
    """Model how attention can convert into liquidity / flow support.

    Attention never directly equals flow. Conversion depends on liquidity depth,
    narrative credibility, institutional participation, and regime stress.
    """

    attention = _clamp(attention_field)
    liquidity = _clamp(liquidity_field)
    credibility = _clamp(narrative_credibility)
    institutional = _clamp(institutional_participation)
    regime = market_regime.upper()

    efficiency = (attention * 0.2) + (liquidity * 0.25) + (credibility * 0.2) + (institutional * 0.35)
    if liquidity <= 35:
        efficiency -= 18
    if regime in {"RISK_OFF", "CRASH_STRESS", "HIGH_VOLATILITY", "DISTRIBUTION"}:
        efficiency -= 12
    efficiency = _clamp(efficiency)

    if liquidity >= 65 and institutional >= 55:
        delay = 1
    elif liquidity <= 35 or regime in {"RISK_OFF", "CRASH_STRESS"}:
        delay = 4
    else:
        delay = 2

    amplification = round(0.6 + (efficiency / 100) + (max(0, attention - liquidity) / 180), 2)
    if liquidity <= 35:
        amplification = round(amplification * 0.85, 2)

    return {
        "efficiency_score": efficiency,
        "delay_factor": delay,
        "amplification_ratio": amplification,
        "interpretation": _conversion_interpretation(efficiency, delay),
    }


def state_transition(
    current_state: Mapping[str, Any],
    *,
    causal_constraints: Mapping[str, Any],
    external_shocks: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Approximate state_transition(S_t) -> S_t+1."""

    shocks = external_shocks or {}
    attention = _clamp(current_state.get("attention_field", 0))
    liquidity = _clamp(current_state.get("liquidity_field", 50))
    volatility = _clamp(current_state.get("volatility_field", 0))
    narrative = _clamp(current_state.get("narrative_field", 0))
    institutional = _clamp(current_state.get("institutional_flow_field", 0))
    retail = _clamp(current_state.get("retail_flow_field", 0))
    stress = _clamp(shocks.get("stress_shock", 0))
    regime = str(current_state.get("memory_context", "NORMAL"))

    conversion = attention_to_liquidity(
        attention_field=attention,
        liquidity_field=liquidity,
        narrative_credibility=max(0, 100 - narrative // 2),
        institutional_participation=institutional,
        market_regime=regime,
    )

    attention_next = attention + (narrative * 0.07) - (volatility * 0.05) + _clamp(shocks.get("attention_shock", 0)) * 0.05
    liquidity_next = liquidity + ((conversion["efficiency_score"] - 50) * 0.16) + (institutional * 0.08) - (volatility * 0.1) - (stress * 0.08)
    volatility_next = volatility + (max(0, 55 - liquidity) * 0.12) + (abs(attention - liquidity) * 0.06) + (stress * 0.08) - (institutional * 0.04)
    narrative_next = narrative + (attention * 0.05) - (conversion["efficiency_score"] * 0.03) + _clamp(shocks.get("narrative_shock", 0)) * 0.08
    institutional_next = institutional + (liquidity * 0.07) - (narrative * 0.04) - (stress * 0.06)
    retail_next = retail + (attention * 0.06) + (conversion["efficiency_score"] * 0.08) - (volatility * 0.05)

    next_state = {
        "t": int(current_state.get("t", 0)) + 1,
        "attention_field": _clamp(attention_next),
        "liquidity_field": _clamp(liquidity_next),
        "volatility_field": _clamp(volatility_next),
        "narrative_field": _clamp(narrative_next),
        "institutional_flow_field": _clamp(institutional_next),
        "retail_flow_field": _clamp(retail_next),
        "memory_context": regime,
        "state_type": "continuous_market_state",
        "conversion_efficiency": conversion,
        "transition_basis": "deterministic_interpretable_state_transition",
        "causal_primary_driver": causal_constraints.get("primary_driver", "Unknown"),
    }
    next_state["regime_pressure_shift"] = _pressure_shift(current_state, next_state)
    return next_state


def simulate_regime_emergence(trajectory: List[Mapping[str, Any]]) -> Dict[str, Any]:
    """Infer regime pressure from state dynamics, not direct labels."""

    if not trajectory:
        return {
            "regime_pressure_map": {},
            "instability_gradients": {},
            "phase_transition_likelihood": 0,
            "structural_imbalance_fields": {},
            "regime_is_emergent": True,
        }

    first = trajectory[0]
    last = trajectory[-1]
    attention_liquidity_gap = int(last["attention_field"]) - int(last["liquidity_field"])
    retail_institutional_gap = int(last["retail_flow_field"]) - int(last["institutional_flow_field"])
    volatility_liquidity_gap = int(last["volatility_field"]) - int(last["liquidity_field"])

    gradients = {
        "attention_gradient": int(last["attention_field"]) - int(first["attention_field"]),
        "liquidity_gradient": int(last["liquidity_field"]) - int(first["liquidity_field"]),
        "volatility_gradient": int(last["volatility_field"]) - int(first["volatility_field"]),
        "narrative_gradient": int(last["narrative_field"]) - int(first["narrative_field"]),
    }
    pressure_map = {
        "attention_expansion_pressure": _clamp(int(last["attention_field"]) + max(0, attention_liquidity_gap) * 0.4),
        "liquidity_stress_pressure": _clamp(100 - int(last["liquidity_field"]) + max(0, volatility_liquidity_gap) * 0.3),
        "volatility_instability_pressure": _clamp(int(last["volatility_field"]) + max(0, -gradients["liquidity_gradient"]) * 1.2),
        "retail_flow_pressure": _clamp(int(last["retail_flow_field"]) + max(0, retail_institutional_gap) * 0.5),
        "institutional_absorption_pressure": _clamp(int(last["institutional_flow_field"]) - max(0, retail_institutional_gap) * 0.3),
    }
    instability = max(
        abs(attention_liquidity_gap),
        abs(retail_institutional_gap),
        abs(volatility_liquidity_gap),
        abs(gradients["volatility_gradient"]),
    )
    return {
        "regime_pressure_map": pressure_map,
        "instability_gradients": gradients,
        "phase_transition_likelihood": _clamp(instability),
        "structural_imbalance_fields": {
            "attention_liquidity_gap": attention_liquidity_gap,
            "retail_institutional_gap": retail_institutional_gap,
            "volatility_liquidity_gap": volatility_liquidity_gap,
        },
        "regime_is_emergent": True,
        "final_label_only": False,
    }


def simulate_counterfactual_market(
    *,
    base_state: Mapping[str, Any],
    causal_constraints: Mapping[str, Any],
    external_shocks: Mapping[str, Any],
    remove_variable: str,
    steps: int = 3,
) -> Dict[str, Any]:
    """Simulate an alternative trajectory after removing one variable."""

    baseline = _simulate_path(base_state, causal_constraints=causal_constraints, external_shocks=external_shocks, steps=steps)
    adjusted_state = dict(base_state)
    adjusted_shocks = dict(external_shocks)
    variable = remove_variable.strip().lower()

    if variable in {"attention", "attention_spike"}:
        adjusted_state["attention_field"] = _clamp(int(adjusted_state.get("attention_field", 0)) * 0.35)
        adjusted_shocks["attention_shock"] = 0
    elif variable in {"liquidity", "liquidity_shock"}:
        adjusted_state["liquidity_field"] = 50
        adjusted_shocks["stress_shock"] = max(0, int(adjusted_shocks.get("stress_shock", 0)) - 35)
    elif variable in {"narrative", "narrative_burst"}:
        adjusted_state["narrative_field"] = _clamp(int(adjusted_state.get("narrative_field", 0)) * 0.4)
        adjusted_shocks["narrative_shock"] = 0

    alternative = _simulate_path(adjusted_state, causal_constraints=causal_constraints, external_shocks=adjusted_shocks, steps=steps)
    divergence = _trajectory_divergence(baseline, alternative)
    return {
        "removed_variable": remove_variable,
        "alternative_state_trajectory": alternative,
        "divergence_score": divergence,
        "regime_sensitivity_index": _clamp(divergence * 1.2),
        "baseline_reference": baseline,
    }


def simulate_market_world_model(
    *,
    fusion: Mapping[str, Any],
    causal: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
    steps: int = 3,
) -> Dict[str, Any]:
    """Return v0.6 world-model trajectories and interpretable dynamics."""

    initial_state = build_market_state(fusion=fusion, causal=causal, memory_summary=memory_summary)
    shocks = {
        "attention_shock": fusion.get("attention_pressure", 0),
        "stress_shock": fusion.get("stress_score", 0),
        "narrative_shock": fusion.get("narrative_intensity", 0),
    }
    baseline = _simulate_path(initial_state, causal_constraints=causal, external_shocks=shocks, steps=steps)
    emergence = simulate_regime_emergence(baseline)
    counterfactual_attention = simulate_counterfactual_market(
        base_state=initial_state,
        causal_constraints=causal,
        external_shocks=shocks,
        remove_variable="attention_spike",
        steps=steps,
    )
    counterfactual_liquidity = simulate_counterfactual_market(
        base_state=initial_state,
        causal_constraints=causal,
        external_shocks=shocks,
        remove_variable="liquidity_shock",
        steps=steps,
    )

    return {
        "market_state_space": market_state_space_definition(),
        "initial_state": initial_state,
        "baseline_trajectory": baseline,
        "scenario_paths": {
            "baseline": baseline,
            "without_attention_spike": counterfactual_attention["alternative_state_trajectory"],
            "without_liquidity_shock": counterfactual_liquidity["alternative_state_trajectory"],
        },
        "attention_liquidity_transformation": baseline[1].get("conversion_efficiency", {}) if len(baseline) > 1 else {},
        "regime_emergence_dynamics": emergence,
        "counterfactuals": {
            "remove_attention_spike": counterfactual_attention,
            "remove_liquidity_shock": counterfactual_liquidity,
        },
        "simulation_mode": "interpretable_deterministic_scenario",
        "not_forecast": True,
        "no_trade_action": True,
    }


def _simulate_path(
    base_state: Mapping[str, Any],
    *,
    causal_constraints: Mapping[str, Any],
    external_shocks: Mapping[str, Any],
    steps: int,
) -> List[Dict[str, Any]]:
    trajectory = [dict(base_state)]
    current = dict(base_state)
    for _ in range(max(0, steps)):
        current = state_transition(current, causal_constraints=causal_constraints, external_shocks=external_shocks)
        trajectory.append(current)
    return trajectory


def _trajectory_divergence(left: List[Mapping[str, Any]], right: List[Mapping[str, Any]]) -> int:
    if not left or not right:
        return 0
    last_left = left[-1]
    last_right = right[-1]
    total = 0
    for field in MARKET_STATE_FIELDS:
        total += abs(int(last_left.get(field, 0)) - int(last_right.get(field, 0)))
    return _clamp(total / len(MARKET_STATE_FIELDS))


def _pressure_shift(previous: Mapping[str, Any], current: Mapping[str, Any]) -> Dict[str, int]:
    return {
        "attention_shift": int(current["attention_field"]) - int(previous.get("attention_field", 0)),
        "liquidity_shift": int(current["liquidity_field"]) - int(previous.get("liquidity_field", 50)),
        "volatility_shift": int(current["volatility_field"]) - int(previous.get("volatility_field", 0)),
        "narrative_shift": int(current["narrative_field"]) - int(previous.get("narrative_field", 0)),
    }


def _conversion_interpretation(efficiency: int, delay: int) -> str:
    if efficiency >= 65 and delay <= 2:
        return "Attention can convert into flow efficiently under current constraints."
    if efficiency <= 35:
        return "Attention is unlikely to convert cleanly into flow under current constraints."
    if delay >= 4:
        return "Attention conversion is unstable or delayed by liquidity / regime constraints."
    return "Attention conversion is partial and requires confirmation."


def _level_to_score(value: str) -> int:
    levels = {"low": 20, "medium": 45, "high": 70, "severe": 90, "data missing": 20}
    return levels.get(value.lower(), 20)


def _clamp(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, int(number)))
