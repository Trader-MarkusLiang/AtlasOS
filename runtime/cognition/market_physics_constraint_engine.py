"""Market Physics Constraint Engine for Atlas Runtime v0.8.

This module constrains market evolution with interpretable conservation,
entropy, invariant, and dynamic-system checks. It is not ML, forecasting,
trading execution, or portfolio automation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def market_conservation_laws() -> Dict[str, Any]:
    """Return the v0.8 market conservation law definitions."""

    return {
        "liquidity_conservation_law": {
            "formula": "Liquidity_inflow - Liquidity_outflow = DeltaLiquidity_state",
            "constraint": "Sudden liquidity changes require source attribution or transfer mechanism.",
        },
        "attention_conservation_soft_form": {
            "formula": "Attention_total ~= constant over short horizon",
            "constraint": "Attention redistributes and decays; it cannot expand without saturation cost.",
        },
        "flow_continuity_law": {
            "formula": "Flow(t) -> Flow(t+1) through intermediate structural states",
            "constraint": "No instantaneous structural jumps without instability marking.",
        },
    }


def check_conservation_laws(
    *,
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
    source_attribution: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Check liquidity, attention, and flow conservation constraints."""

    trajectory = _trajectory(world_model)
    sources = source_attribution or _infer_source_attribution(world_model, latent_structure)
    if len(trajectory) < 2:
        return {
            "liquidity_conservation": _law_result(False, "Insufficient trajectory data."),
            "attention_conservation": _law_result(False, "Insufficient trajectory data."),
            "flow_continuity": _law_result(False, "Insufficient trajectory data."),
            "source_attribution": sources,
        }

    first = trajectory[0]
    last = trajectory[-1]
    liquidity_delta = int(last.get("liquidity_field", 50)) - int(first.get("liquidity_field", 50))
    attention_delta = int(last.get("attention_field", 0)) - int(first.get("attention_field", 0))
    flow_delta = _flow_level(last) - _flow_level(first)

    liquidity_source_strength = int(sources.get("liquidity_source_strength", 0))
    attention_transfer_strength = int(sources.get("attention_transfer_strength", 0))
    flow_transfer_strength = int(sources.get("flow_transfer_strength", 0))

    liquidity_ok = abs(liquidity_delta) <= 18 or liquidity_source_strength >= abs(liquidity_delta)
    attention_ok = abs(attention_delta) <= 25 or attention_transfer_strength >= abs(attention_delta) * 0.7
    flow_ok = abs(flow_delta) <= 28 or flow_transfer_strength >= abs(flow_delta) * 0.8

    return {
        "liquidity_conservation": _law_result(
            liquidity_ok,
            "Liquidity change has source attribution." if liquidity_ok else "Liquidity appears without enough source attribution.",
            observed_delta=liquidity_delta,
            required_source=abs(liquidity_delta),
            source_strength=liquidity_source_strength,
        ),
        "attention_conservation": _law_result(
            attention_ok,
            "Attention redistribution remains bounded." if attention_ok else "Attention expands beyond short-horizon bound.",
            observed_delta=attention_delta,
            transfer_strength=attention_transfer_strength,
        ),
        "flow_continuity": _law_result(
            flow_ok,
            "Flow transition respects continuity." if flow_ok else "Flow jumps without intermediate structural support.",
            observed_delta=flow_delta,
            transfer_strength=flow_transfer_strength,
        ),
        "source_attribution": sources,
    }


def compute_market_entropy(
    *,
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
) -> Dict[str, int]:
    """Compute narrative, volatility, and liquidity entropy."""

    trajectory = _trajectory(world_model)
    latent = latent_structure.get("latent_variables", {}) if isinstance(latent_structure.get("latent_variables"), Mapping) else {}
    phase = latent_structure.get("phase_space_geometry", {}) if isinstance(latent_structure.get("phase_space_geometry"), Mapping) else {}

    if not trajectory:
        narrative_entropy = volatility_entropy = liquidity_entropy = 0
    else:
        narrative_values = [int(item.get("narrative_field", 0)) for item in trajectory]
        volatility_values = [int(item.get("volatility_field", 0)) for item in trajectory]
        liquidity_values = [int(item.get("liquidity_field", 50)) for item in trajectory]
        narrative_entropy = _clamp(_range(narrative_values) + int(latent.get("narrative_propagation_inertia", 0)) * 0.25)
        volatility_entropy = _clamp(_range(volatility_values) + int(latent.get("hidden_risk_compression", 0)) * 0.35)
        liquidity_entropy = _clamp(_range(liquidity_values) + int(phase.get("phase_curvature", 0)) * 0.25)

    total = _clamp((narrative_entropy * 0.34) + (volatility_entropy * 0.36) + (liquidity_entropy * 0.3))
    return {
        "narrative_entropy": narrative_entropy,
        "volatility_entropy": volatility_entropy,
        "liquidity_entropy": liquidity_entropy,
        "total_system_entropy": total,
    }


def check_structural_invariants(
    *,
    conservation: Mapping[str, Any],
    entropy: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
) -> Dict[str, Any]:
    """Check invariant constraints without forcing a regime label."""

    latent = latent_structure.get("latent_variables", {}) if isinstance(latent_structure.get("latent_variables"), Mapping) else {}
    violations: List[str] = []

    if int(entropy.get("total_system_entropy", 0)) >= 70:
        violations.append("entropy_explosion")
    if int(latent.get("attention_persistence_field", 0)) > 92:
        violations.append("attention_persistence_limit")
    if int(latent.get("structural_liquidity_pressure", 0)) > 92:
        violations.append("liquidity_redistribution_bound")
    if int(latent.get("hidden_risk_compression", 0)) > 92:
        violations.append("regime_stability_bound")

    for law_name in ("liquidity_conservation", "attention_conservation", "flow_continuity"):
        law = conservation.get(law_name, {})
        if isinstance(law, Mapping) and not law.get("satisfied", True):
            violations.append(f"{law_name}_violation")

    unstable = bool(violations)
    return {
        "regime_stability_bounds": "VIOLATED" if "regime_stability_bound" in violations else "OK",
        "liquidity_redistribution_bounds": "VIOLATED" if "liquidity_redistribution_bound" in violations else "OK",
        "attention_persistence_limits": "VIOLATED" if "attention_persistence_limit" in violations else "OK",
        "flow_conservation_consistency": "VIOLATED" if any("conservation" in item for item in violations) else "OK",
        "constraint_violations": violations,
        "unstable_regime_transition_zone": unstable,
        "forced_regime_label": None,
    }


def formulate_dynamic_system(
    *,
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
    conservation: Mapping[str, Any],
    entropy: Mapping[str, Any],
) -> Dict[str, Any]:
    """Represent dS/dt = F(S, constraints, latent_structure)."""

    trajectory = _trajectory(world_model)
    first = trajectory[0] if trajectory else {}
    last = trajectory[-1] if trajectory else {}
    latent = latent_structure.get("latent_variables", {}) if isinstance(latent_structure.get("latent_variables"), Mapping) else {}
    violation_count = _violation_count(conservation)
    entropy_load = int(entropy.get("total_system_entropy", 0))
    constraint_drag = _clamp((violation_count * 18) + entropy_load * 0.28)

    unconstrained = {
        "attention_velocity": int(last.get("attention_field", 0)) - int(first.get("attention_field", 0)),
        "liquidity_velocity": int(last.get("liquidity_field", 50)) - int(first.get("liquidity_field", 50)),
        "volatility_velocity": int(last.get("volatility_field", 0)) - int(first.get("volatility_field", 0)),
    }
    constrained = {
        "attention_velocity": _apply_drag(unconstrained["attention_velocity"], constraint_drag),
        "liquidity_velocity": _apply_drag(unconstrained["liquidity_velocity"], constraint_drag),
        "volatility_velocity": _apply_drag(
            unconstrained["volatility_velocity"] + int(latent.get("hidden_risk_compression", 0)) // 12,
            max(0, constraint_drag - 12),
        ),
    }
    divergence = _clamp(
        abs(unconstrained["attention_velocity"] - constrained["attention_velocity"])
        + abs(unconstrained["liquidity_velocity"] - constrained["liquidity_velocity"])
        + abs(unconstrained["volatility_velocity"] - constrained["volatility_velocity"])
    )
    return {
        "equation": "dS/dt = F(S, constraints, latent_structure)",
        "unconstrained_evolution": unconstrained,
        "constrained_evolution": constrained,
        "constraint_drag": constraint_drag,
        "structural_divergence": divergence,
        "constraints_modify_trajectory": divergence > 0,
        "constraints_override_state_directly": False,
    }


def infer_constraint_regime_emergence(
    *,
    conservation: Mapping[str, Any],
    entropy: Mapping[str, Any],
    invariants: Mapping[str, Any],
    dynamic_system: Mapping[str, Any],
) -> Dict[str, Any]:
    """Infer regime emergence under constraint stress, not event thresholds."""

    violations = list(invariants.get("constraint_violations", []))
    entropy_load = int(entropy.get("total_system_entropy", 0))
    drag = int(dynamic_system.get("constraint_drag", 0))
    tension = {
        "liquidity_constraint_tension": 0 if conservation.get("liquidity_conservation", {}).get("satisfied") else 85,
        "attention_constraint_tension": 0 if conservation.get("attention_conservation", {}).get("satisfied") else 65,
        "flow_constraint_tension": 0 if conservation.get("flow_continuity", {}).get("satisfied") else 70,
        "entropy_tension": entropy_load,
        "invariant_tension": _clamp(len(violations) * 22),
    }
    stability_boundary = _clamp(max(tension.values()) + drag * 0.25)
    collapse_risk = _clamp((entropy_load * 0.35) + (len(violations) * 18) + drag * 0.25)
    return {
        "constraint_tension_map": tension,
        "stability_boundary_proximity": stability_boundary,
        "phase_transition_likelihood": _clamp((stability_boundary + collapse_risk) / 2),
        "structural_collapse_risk_index": collapse_risk,
        "emergence_basis": "constraint_stress",
        "event_threshold_regime": False,
        "forced_regime_label": None,
    }


def evaluate_system_stability(
    *,
    entropy: Mapping[str, Any],
    invariants: Mapping[str, Any],
    dynamic_system: Mapping[str, Any],
    regime_emergence: Mapping[str, Any],
) -> Dict[str, Any]:
    """Detect overextension, imbalance, entropy explosion, and inconsistency."""

    violations = list(invariants.get("constraint_violations", []))
    entropy_load = int(entropy.get("total_system_entropy", 0))
    fragility = _clamp(
        int(regime_emergence.get("structural_collapse_risk_index", 0)) * 0.45
        + entropy_load * 0.35
        + len(violations) * 12
    )
    stability = _clamp(100 - fragility)
    return {
        "stability_score": stability,
        "constraint_violations": violations,
        "regime_fragility_index": fragility,
        "instability_zone": bool(violations) or fragility >= 60,
        "diagnostics": {
            "overextension_of_liquidity": "liquidity_redistribution_bound" in violations,
            "attention_imbalance": "attention_persistence_limit" in violations,
            "entropy_explosion": entropy_load >= 70,
            "structural_inconsistency": bool(violations) or dynamic_system.get("constraint_drag", 0) >= 50,
        },
    }


def apply_market_physics_constraints(
    *,
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
    causal: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return the full v0.8 market physics constraint output."""

    source = _infer_source_attribution(world_model, latent_structure)
    conservation = check_conservation_laws(
        world_model=world_model,
        latent_structure=latent_structure,
        source_attribution=source,
    )
    entropy = compute_market_entropy(world_model=world_model, latent_structure=latent_structure)
    invariants = check_structural_invariants(
        conservation=conservation,
        entropy=entropy,
        latent_structure=latent_structure,
    )
    dynamic = formulate_dynamic_system(
        world_model=world_model,
        latent_structure=latent_structure,
        conservation=conservation,
        entropy=entropy,
    )
    emergence = infer_constraint_regime_emergence(
        conservation=conservation,
        entropy=entropy,
        invariants=invariants,
        dynamic_system=dynamic,
    )
    stability = evaluate_system_stability(
        entropy=entropy,
        invariants=invariants,
        dynamic_system=dynamic,
        regime_emergence=emergence,
    )
    return {
        "market_conservation_laws": market_conservation_laws(),
        "conservation_state": conservation,
        "entropy_state": entropy,
        "structural_invariants": invariants,
        "dynamic_system": dynamic,
        "constraint_driven_regime_emergence": emergence,
        "system_stability_report": stability,
        "context": {
            "causal_primary_driver": causal.get("primary_driver", "Unknown"),
            "memory_dominant_state": memory_summary.get("dominant_state", "NORMAL"),
        },
        "model_mode": "interpretable_constraint_system_non_ml",
        "not_forecasting_engine": True,
        "no_trade_action": True,
    }


def _infer_source_attribution(world_model: Mapping[str, Any], latent_structure: Mapping[str, Any]) -> Dict[str, int]:
    transformation = world_model.get("attention_liquidity_transformation", {})
    latent = latent_structure.get("latent_variables", {}) if isinstance(latent_structure.get("latent_variables"), Mapping) else {}
    return {
        "liquidity_source_strength": _clamp(
            int(transformation.get("efficiency_score", 0)) * 0.45
            + int(latent.get("structural_liquidity_pressure", 0)) * 0.15
        ),
        "attention_transfer_strength": _clamp(int(latent.get("attention_persistence_field", 0)) * 0.55),
        "flow_transfer_strength": _clamp(int(latent.get("capital_rotation_tension", 0)) * 0.45),
    }


def _trajectory(world_model: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    trajectory = world_model.get("baseline_trajectory", [])
    return trajectory if isinstance(trajectory, list) else []


def _flow_level(state: Mapping[str, Any]) -> int:
    return (int(state.get("institutional_flow_field", 0)) + int(state.get("retail_flow_field", 0))) // 2


def _range(values: List[int]) -> int:
    return max(values) - min(values) if values else 0


def _law_result(satisfied: bool, message: str, **metadata: Any) -> Dict[str, Any]:
    result = {"satisfied": bool(satisfied), "message": message}
    result.update(metadata)
    return result


def _violation_count(conservation: Mapping[str, Any]) -> int:
    count = 0
    for key in ("liquidity_conservation", "attention_conservation", "flow_continuity"):
        value = conservation.get(key, {})
        if isinstance(value, Mapping) and not value.get("satisfied", True):
            count += 1
    return count


def _apply_drag(value: int, drag: int) -> int:
    multiplier = max(0.25, 1 - drag / 140)
    return int(value * multiplier)


def _clamp(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, int(number)))
