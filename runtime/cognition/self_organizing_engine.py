"""Self-organizing cognitive overlay for Atlas Runtime v0.5.

The engine makes structural drift endogenous by turning accumulated tension,
trust-field dynamics, and v0.4 structural overlays into bounded metadata. It
does not train models, rewrite deterministic cognition, or produce trade logic.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from runtime.cognition.structural_evolution_controller import apply_structural_evolution
from runtime.cognition.trust_field_dynamics import evolve_trust_field


KNOWN_CAUSAL_KEYS = (
    "Narrative Pressure->Attention",
    "Attention->Retail Flow",
    "Institutional Flow->Liquidity",
    "Liquidity->Volatility",
    "Retail Flow->Price Momentum",
    "Price Momentum->Attention",
)


def run_self_organization_cycle(
    *,
    cognitive_state: Mapping[str, Any],
    structural_coevolution_state: Mapping[str, Any],
    system_trust_state: Mapping[str, Any],
    trust_score: Mapping[str, Any],
    feedback_delta: Mapping[str, Any],
    previous_self_organization_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Run one bounded self-organization cycle."""

    previous = previous_self_organization_state if isinstance(previous_self_organization_state, Mapping) else {}
    tension = detect_structural_tension(cognitive_state, structural_coevolution_state, feedback_delta)
    trust_field_state = evolve_trust_field(
        previous_field=_as_mapping(previous.get("trust_field_state")).get("trust_field", {}),
        system_trust_state=system_trust_state,
        trust_score=trust_score,
        feedback_delta=feedback_delta,
        regime_volatility=_float(_as_mapping(cognitive_state.get("fusion")).get("stress_score"), 0.0),
        causal_consistency=tension["causal_consistency"],
    )
    proposed = {
        "causal_reweight_delta": _propose_causal_reweighting(structural_coevolution_state, tension),
        "regime_attractor_shift": _propose_regime_shift(structural_coevolution_state, tension),
    }
    explanation_feedback = _as_mapping(
        _as_mapping(_as_mapping(structural_coevolution_state).get("explanation_feedback")).get("causal_correction")
    )
    controlled = apply_structural_evolution(
        proposed=proposed,
        trust_field_state=trust_field_state,
        previous_state=previous,
        explanation_feedback=explanation_feedback,
    )
    return {
        "structural_shift_index": controlled["structural_shift_index"],
        "causal_reweight_delta": controlled["causal_reweight_delta"],
        "regime_attractor_shift": controlled["regime_attractor_shift"],
        "trust_field_evolution": controlled["trust_field_evolution"],
        "status": controlled["status"],
        "trust_gate": controlled["trust_gate"],
        "trust_gate_value": controlled["trust_gate_value"],
        "trust_field_state": trust_field_state,
        "structural_tension": tension,
        "applied_evolution": controlled["applied_evolution"],
        "reversible_delta_log": controlled["reversible_delta_log"],
        "bounded": controlled["bounded"],
        "reversible": controlled["reversible"],
        "metadata_only": True,
        "no_core_cognition_override": True,
        "no_trading_logic": True,
    }


def detect_structural_tension(
    cognitive_state: Mapping[str, Any],
    structural_coevolution_state: Mapping[str, Any],
    feedback_delta: Mapping[str, Any],
) -> Dict[str, float]:
    """Detect accumulated structural tension from existing runtime outputs."""

    cognition = _as_mapping(cognitive_state)
    fusion = _as_mapping(cognition.get("fusion"))
    latent = _as_mapping(_as_mapping(cognition.get("latent_structure")).get("latent_variables"))
    physics = _as_mapping(cognition.get("physics_constraints"))
    stability = _as_mapping(physics.get("system_stability_report"))
    structural = _as_mapping(structural_coevolution_state)
    drift = _as_mapping(structural.get("drift_summary"))
    mutation = _as_mapping(structural.get("mutation"))

    attention_liquidity_gap = abs(
        _float(latent.get("attention_persistence_field"), _float(fusion.get("attention_pressure"), 0.0))
        - _float(latent.get("structural_liquidity_pressure"), 50.0)
    ) / 100.0
    risk_compression = _float(latent.get("hidden_risk_compression"), 0.0) / 100.0
    constraint_load = len(_as_list(stability.get("constraint_violations"))) / 6.0
    structural_shift = _float(drift.get("structural_shift_index"), mutation.get("structural_shift_index", 0.0))
    feedback_load = _feedback_magnitude(feedback_delta)
    stability_score = _float(stability.get("stability_score"), 50.0)
    tension = max(
        attention_liquidity_gap,
        risk_compression,
        constraint_load,
        min(1.0, structural_shift * 3.0),
        min(1.0, feedback_load * 5.0),
    )
    causal_consistency = max(0.0, min(1.0, stability_score / 100.0 - constraint_load * 0.25))
    return {
        "tension_accumulation": round(min(1.0, tension), 4),
        "attention_liquidity_gap": round(attention_liquidity_gap, 4),
        "risk_compression": round(risk_compression, 4),
        "constraint_load": round(min(1.0, constraint_load), 4),
        "feedback_load": round(min(1.0, feedback_load), 4),
        "causal_consistency": round(causal_consistency, 4),
    }


def _propose_causal_reweighting(
    structural_coevolution_state: Mapping[str, Any],
    tension: Mapping[str, Any],
) -> Dict[str, float]:
    mutation = _as_mapping(_as_mapping(structural_coevolution_state).get("mutation"))
    source_edges = _as_mapping(mutation.get("edge_weight_updates"))
    tension_scale = _float(tension.get("tension_accumulation"), 0.0)
    if not source_edges:
        return {}
    return {
        key: round(_float(source_edges.get(key), 0.0) * min(1.0, tension_scale), 4)
        for key in KNOWN_CAUSAL_KEYS
        if key in source_edges
    }


def _propose_regime_shift(
    structural_coevolution_state: Mapping[str, Any],
    tension: Mapping[str, Any],
) -> float:
    topology = _as_mapping(_as_mapping(structural_coevolution_state).get("regime_topology"))
    base = abs(_float(topology.get("basin_deformation"), 0.0)) + abs(_float(topology.get("attractor_shift"), 0.0))
    return round(base * _float(tension.get("tension_accumulation"), 0.0), 4)


def _feedback_magnitude(feedback_delta: Mapping[str, Any]) -> float:
    values: list[float] = []
    for value in (_as_mapping(feedback_delta)).values():
        if isinstance(value, Mapping):
            values.extend(abs(_float(item, 0.0)) for item in value.values())
        else:
            values.append(abs(_float(value, 0.0)))
    return max(values, default=0.0)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
