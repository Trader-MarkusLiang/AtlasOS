"""Latent Market Structure Engine for Atlas Runtime v0.7.

This module interprets observed market states as projections of slower latent
structure. It is deterministic market-physics reasoning, not ML, forecasting,
trading execution, or portfolio automation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


LATENT_VARIABLES = (
    "structural_liquidity_pressure",
    "attention_persistence_field",
    "narrative_propagation_inertia",
    "hidden_risk_compression",
    "capital_rotation_tension",
)


def latent_regime_space_definition() -> Dict[str, Any]:
    """Return observed and latent variable definitions."""

    return {
        "observed_variables": ["attention", "liquidity", "volatility", "narrative", "flows"],
        "latent_variables": list(LATENT_VARIABLES),
        "principle": "Observed variables are projections of latent market structure.",
        "regime_definition": "Regimes are attractor basins in latent market space, not labels.",
    }


def infer_latent_variables(world_model: Mapping[str, Any]) -> Dict[str, int]:
    """Infer slow latent structure from v0.6 world-model trajectories."""

    trajectory = _trajectory(world_model)
    if not trajectory:
        return {name: 0 for name in LATENT_VARIABLES}

    first = trajectory[0]
    last = trajectory[-1]
    attention = int(last.get("attention_field", 0))
    liquidity = int(last.get("liquidity_field", 50))
    volatility = int(last.get("volatility_field", 0))
    narrative = int(last.get("narrative_field", 0))
    institutional = int(last.get("institutional_flow_field", 0))
    retail = int(last.get("retail_flow_field", 0))

    attention_gradient = attention - int(first.get("attention_field", 0))
    liquidity_gradient = liquidity - int(first.get("liquidity_field", 50))
    volatility_gradient = volatility - int(first.get("volatility_field", 0))
    narrative_gradient = narrative - int(first.get("narrative_field", 0))

    return {
        "structural_liquidity_pressure": _clamp((100 - liquidity) + max(0, -liquidity_gradient) * 1.5),
        "attention_persistence_field": _clamp(attention * 0.65 + max(0, attention_gradient) * 1.2),
        "narrative_propagation_inertia": _clamp(narrative * 0.7 + max(0, narrative_gradient) * 1.1),
        "hidden_risk_compression": _clamp(volatility * 0.55 + max(0, volatility_gradient) * 1.5 + max(0, 45 - liquidity)),
        "capital_rotation_tension": _clamp(abs(retail - institutional) + abs(attention - liquidity) * 0.45),
    }


def compute_regime_attractors(latent_variables: Mapping[str, Any]) -> Dict[str, Any]:
    """Compute attractor basins from latent structure."""

    liquidity_pressure = _clamp(latent_variables.get("structural_liquidity_pressure", 0))
    attention_persistence = _clamp(latent_variables.get("attention_persistence_field", 0))
    narrative_inertia = _clamp(latent_variables.get("narrative_propagation_inertia", 0))
    risk_compression = _clamp(latent_variables.get("hidden_risk_compression", 0))
    rotation_tension = _clamp(latent_variables.get("capital_rotation_tension", 0))

    basins = {
        "liquidity_stress_basin": _basin(
            liquidity_pressure * 0.5 + risk_compression * 0.35 + rotation_tension * 0.15
        ),
        "attention_momentum_basin": _basin(
            attention_persistence * 0.45 + narrative_inertia * 0.3 + max(0, 100 - liquidity_pressure) * 0.25
        ),
        "distribution_basin": _basin(
            attention_persistence * 0.28 + narrative_inertia * 0.28 + risk_compression * 0.28 + rotation_tension * 0.16
        ),
        "stabilization_basin": _basin(
            max(0, 100 - liquidity_pressure) * 0.45 + max(0, 100 - risk_compression) * 0.35
            + max(0, 100 - rotation_tension) * 0.2
        ),
    }
    dominant = max(basins, key=lambda name: basins[name]["attractor_strength"])
    return {
        "basins": basins,
        "dominant_attractor_basin": dominant,
        "multiple_regime_basins": True,
        "regimes_are_labels": False,
    }


def map_market_phase_space(
    *,
    latent_variables: Mapping[str, Any],
    world_model: Mapping[str, Any],
) -> Dict[str, Any]:
    """Map market behavior as phase-space geometry."""

    trajectory = _trajectory(world_model)
    latent = {key: _clamp(value) for key, value in latent_variables.items()}
    if len(trajectory) < 2:
        drift = {"attention_liquidity_axis": 0, "volatility_flow_axis": 0, "narrative_rotation_axis": 0}
    else:
        first = trajectory[0]
        last = trajectory[-1]
        drift = {
            "attention_liquidity_axis": int(last.get("attention_field", 0))
            - int(last.get("liquidity_field", 50))
            - (int(first.get("attention_field", 0)) - int(first.get("liquidity_field", 50))),
            "volatility_flow_axis": int(last.get("volatility_field", 0))
            - (int(last.get("institutional_flow_field", 0)) + int(last.get("retail_flow_field", 0))) // 2,
            "narrative_rotation_axis": int(last.get("narrative_field", 0))
            - int(first.get("narrative_field", 0))
            + latent["capital_rotation_tension"] // 5,
        }

    curvature = _clamp(
        abs(drift["attention_liquidity_axis"]) * 0.7
        + latent["hidden_risk_compression"] * 0.25
        + latent["capital_rotation_tension"] * 0.25
    )
    return {
        "phase_curvature": curvature,
        "trajectory_drift_vector": drift,
        "volatility_manifold_shape": _manifold_shape(curvature, latent["hidden_risk_compression"]),
        "liquidity_gradient_field": {
            "pressure": latent["structural_liquidity_pressure"],
            "direction": "contracting" if latent["structural_liquidity_pressure"] >= 55 else "neutral / supportive",
        },
        "geometry_not_time_series": True,
    }


def attention_field_dynamics(
    *,
    attention_observed: int | float,
    narrative_inertia: int | float,
    liquidity_pressure: int | float,
    previous_persistence: int | float = 0,
) -> Dict[str, Any]:
    """Treat attention as a persistent field rather than a single spike."""

    attention = _clamp(attention_observed)
    narrative = _clamp(narrative_inertia)
    liquidity = _clamp(liquidity_pressure)
    previous = _clamp(previous_persistence)
    persistence = _clamp(previous * 0.55 + attention * 0.3 + narrative * 0.15)
    decay = _clamp(42 - narrative * 0.18 + liquidity * 0.12)
    reinforcement = _clamp(attention * 0.35 + narrative * 0.35 + max(0, 70 - liquidity) * 0.18)
    diffusion = _clamp((persistence + reinforcement) * 0.45)
    return {
        "attention_persistence": persistence,
        "decay_rate": decay,
        "reinforcement_loops": reinforcement,
        "cross_asset_diffusion": diffusion,
        "attention_is_field": True,
    }


def simulate_structural_evolution(
    latent_variables: Mapping[str, Any],
    *,
    steps: int = 3,
    shock: Mapping[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Simulate structure(t) -> structure(t+1), slower than observed states."""

    current = {key: _clamp(latent_variables.get(key, 0)) for key in LATENT_VARIABLES}
    trajectory = [dict(current, t=0, evolution_basis="latent_structure")]
    structural_shock = shock or {}
    for step in range(1, max(0, steps) + 1):
        next_state = {
            "structural_liquidity_pressure": _clamp(
                current["structural_liquidity_pressure"] * 0.88
                + current["hidden_risk_compression"] * 0.08
                + _clamp(structural_shock.get("liquidity_pressure", 0)) * 0.04
            ),
            "attention_persistence_field": _clamp(
                current["attention_persistence_field"] * 0.93
                + current["narrative_propagation_inertia"] * 0.03
                + _clamp(structural_shock.get("attention_persistence", 0)) * 0.02
            ),
            "narrative_propagation_inertia": _clamp(
                current["narrative_propagation_inertia"] * 0.92
                + current["attention_persistence_field"] * 0.03
            ),
            "hidden_risk_compression": _clamp(
                current["hidden_risk_compression"] * 0.9
                + current["structural_liquidity_pressure"] * 0.06
                + _clamp(structural_shock.get("risk_compression", 0)) * 0.08
            ),
            "capital_rotation_tension": _clamp(
                current["capital_rotation_tension"] * 0.84
                + abs(current["attention_persistence_field"] - current["structural_liquidity_pressure"]) * 0.08
            ),
        }
        current = next_state
        trajectory.append(dict(current, t=step, evolution_basis="latent_structure"))
    return trajectory


def simulate_structural_counterfactual(
    latent_variables: Mapping[str, Any],
    *,
    modify_variable: str,
    modifier: int | float,
    steps: int = 3,
) -> Dict[str, Any]:
    """Test how changing latent structure deforms future trajectory."""

    baseline = simulate_structural_evolution(latent_variables, steps=steps)
    adjusted = {key: _clamp(latent_variables.get(key, 0)) for key in LATENT_VARIABLES}
    key = _normalize_variable(modify_variable)
    if key in adjusted:
        adjusted[key] = _clamp(adjusted[key] + modifier)
    shock = {}
    if key == "hidden_risk_compression":
        shock["risk_compression"] = abs(modifier)
    elif key == "structural_liquidity_pressure":
        shock["liquidity_pressure"] = abs(modifier)
    elif key == "attention_persistence_field":
        shock["attention_persistence"] = abs(modifier)
    alternative = simulate_structural_evolution(adjusted, steps=steps, shock=shock)
    divergence = _structural_divergence(baseline, alternative)
    return {
        "modified_variable": key or modify_variable,
        "modifier": int(modifier),
        "alternative_structural_trajectory": alternative,
        "structural_divergence_score": divergence,
        "regime_attractor_shift": _attractor_shift(baseline, alternative),
        "phase_space_deformation": _clamp(divergence * 1.25),
    }


def infer_latent_market_structure(
    *,
    world_model: Mapping[str, Any],
    causal: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return the full v0.7 latent market structure output."""

    latent = infer_latent_variables(world_model)
    attractors = compute_regime_attractors(latent)
    phase_space = map_market_phase_space(latent_variables=latent, world_model=world_model)
    attention = attention_field_dynamics(
        attention_observed=_last_observed(world_model, "attention_field"),
        narrative_inertia=latent["narrative_propagation_inertia"],
        liquidity_pressure=latent["structural_liquidity_pressure"],
        previous_persistence=latent["attention_persistence_field"],
    )
    structural_trajectory = simulate_structural_evolution(latent, steps=3)
    counterfactual = simulate_structural_counterfactual(
        latent,
        modify_variable="hidden_risk_compression",
        modifier=25,
        steps=3,
    )
    observed_spike_sensitivity = _clamp(_last_observed(world_model, "attention_field") * 0.25)

    return {
        "latent_regime_space": latent_regime_space_definition(),
        "latent_variables": latent,
        "regime_attractors": attractors,
        "phase_space_geometry": phase_space,
        "attention_field_dynamics": attention,
        "structural_evolution": structural_trajectory,
        "structural_counterfactuals": {
            "risk_compression_up": counterfactual,
        },
        "observation_structure_decoupling": {
            "observed_spike_sensitivity": observed_spike_sensitivity,
            "dominant_attractor_basin": attractors["dominant_attractor_basin"],
            "observed_spikes_define_regime": False,
            "memory_context": memory_summary.get("dominant_state", "NORMAL"),
            "causal_primary_driver": causal.get("primary_driver", "Unknown"),
        },
        "model_mode": "interpretable_latent_structure_non_ml",
        "not_prediction_engine": True,
        "no_trade_action": True,
    }


def _trajectory(world_model: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    trajectory = world_model.get("baseline_trajectory", [])
    return trajectory if isinstance(trajectory, list) else []


def _last_observed(world_model: Mapping[str, Any], field: str) -> int:
    trajectory = _trajectory(world_model)
    if not trajectory:
        return 0
    return _clamp(trajectory[-1].get(field, 0))


def _basin(value: float) -> Dict[str, int]:
    strength = _clamp(value)
    depth = _clamp(strength * 0.72)
    barrier = _clamp(100 - strength * 0.55)
    stability = _clamp((depth + barrier) / 2)
    return {
        "attractor_strength": strength,
        "basin_depth": depth,
        "transition_barrier": barrier,
        "structural_stability_index": stability,
    }


def _manifold_shape(curvature: int, risk_compression: int) -> str:
    if curvature >= 70 and risk_compression >= 60:
        return "folded / stress-compressed"
    if curvature >= 45:
        return "curved / transitional"
    return "flat / stable"


def _structural_divergence(left: List[Mapping[str, Any]], right: List[Mapping[str, Any]]) -> int:
    if not left or not right:
        return 0
    total = 0
    for key in LATENT_VARIABLES:
        total += abs(int(left[-1].get(key, 0)) - int(right[-1].get(key, 0)))
    return _clamp(total / len(LATENT_VARIABLES))


def _attractor_shift(left: List[Mapping[str, Any]], right: List[Mapping[str, Any]]) -> Dict[str, Any]:
    left_attractors = compute_regime_attractors(left[-1] if left else {})
    right_attractors = compute_regime_attractors(right[-1] if right else {})
    return {
        "from": left_attractors["dominant_attractor_basin"],
        "to": right_attractors["dominant_attractor_basin"],
        "changed": left_attractors["dominant_attractor_basin"] != right_attractors["dominant_attractor_basin"],
    }


def _normalize_variable(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_")
    aliases = {
        "risk_compression": "hidden_risk_compression",
        "liquidity_pressure": "structural_liquidity_pressure",
        "attention_persistence": "attention_persistence_field",
        "narrative_inertia": "narrative_propagation_inertia",
        "rotation_tension": "capital_rotation_tension",
    }
    return aliases.get(normalized, normalized)


def _clamp(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, int(number)))
