"""Unified Market Intelligence Core for Atlas Runtime v1.0.

This module projects event, causal, latent, physics, and law-emergence layers
into one interpretable closed-loop representation. It is not ML, black-box
prediction, trading execution, signal generation, CDE override, or portfolio
automation.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


def build_unified_market_state(
    *,
    event_state: Mapping[str, Any],
    causal_state: Mapping[str, Any],
    latent_structure_state: Mapping[str, Any],
    physics_constraint_state: Mapping[str, Any],
    emergent_law_state: Mapping[str, Any],
    memory_state: Mapping[str, Any] | None = None,
    previous_unified_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Project all cognition layers into one state object."""

    latent = _mapping(latent_structure_state.get("latent_variables"))
    physics_stability = _mapping(physics_constraint_state.get("system_stability_report"))
    law_stability = _mapping(emergent_law_state.get("system_stability_evaluation"))
    laws = emergent_law_state.get("discovered_market_laws", [])
    prior_interpretation = _mapping(previous_unified_state.get("unified_interpretation")) if previous_unified_state else {}
    prior_adaptation = _mapping(previous_unified_state.get("self_adaptation")) if previous_unified_state else {}

    unified = {
        "event_state": {
            "stress_level": _clamp(event_state.get("stress_score", event_state.get("stress_level", 0))),
            "attention_pressure": _clamp(event_state.get("attention_pressure", 0)),
            "liquidity_condition": _clamp(event_state.get("liquidity_score", 50)),
            "volatility_regime": event_state.get("volatility_regime", "Unknown"),
            "narrative_intensity": _clamp(event_state.get("narrative_intensity", 0)),
        },
        "causal_state": {
            "primary_driver": causal_state.get("primary_driver", "Unknown"),
            "secondary_driver": causal_state.get("secondary_driver", "Unknown"),
            "market_pressure_source": causal_state.get("market_pressure_source", "Unknown"),
            "regime_transition_probability": _clamp(causal_state.get("regime_transition_probability", 0)),
        },
        "latent_structure_state": {
            "dominant_attractor_basin": _mapping(latent_structure_state.get("regime_attractors")).get(
                "dominant_attractor_basin", "Unknown"
            ),
            "structural_liquidity_pressure": _clamp(latent.get("structural_liquidity_pressure", 0)),
            "attention_persistence_field": _clamp(latent.get("attention_persistence_field", 0)),
            "hidden_risk_compression": _clamp(latent.get("hidden_risk_compression", 0)),
            "capital_rotation_tension": _clamp(latent.get("capital_rotation_tension", 0)),
        },
        "physics_constraint_state": {
            "stability_score": _clamp(physics_stability.get("stability_score", 0)),
            "regime_fragility_index": _clamp(physics_stability.get("regime_fragility_index", 0)),
            "constraint_violations": list(physics_stability.get("constraint_violations", [])),
            "instability_zone": bool(physics_stability.get("instability_zone", False)),
        },
        "emergent_law_state": {
            "law_count": len(laws) if isinstance(laws, list) else 0,
            "law_system_stability_score": _clamp(law_stability.get("law_system_stability_score", 0)),
            "over_evolution_risk": bool(law_stability.get("over_evolution_risk", False)),
            "instability_collapse_risk": _clamp(law_stability.get("instability_collapse_risk", 0)),
            "multi_law_coexistence_zone": bool(
                _mapping(emergent_law_state.get("contradiction_analysis")).get("multi_law_coexistence_zone", False)
            ),
        },
        "memory_state": {
            "dominant_state": (memory_state or {}).get("dominant_state", "Unknown"),
            "sequence_length": _clamp((memory_state or {}).get("sequence_length", 0)),
        },
        "previous_system_interpretation": {
            "dominant_regime_structure": prior_interpretation.get("dominant_regime_structure", "None"),
            "interpretation_bias_carryover": _clamp(prior_adaptation.get("bias_correction_strength", 0)),
        },
        "unified_state_space": True,
        "isolated_interpretation_layers": False,
    }
    unified["coherence_score"] = _coherence_score(unified)
    return unified


def market_system_feedback_loop(
    unified_state: Mapping[str, Any],
    *,
    previous_unified_state: Mapping[str, Any] | None = None,
    market_feedback: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Model a closed interpretation feedback loop without trading effects."""

    event = _mapping(unified_state.get("event_state"))
    previous_interpretation = _mapping(previous_unified_state.get("unified_interpretation")) if previous_unified_state else {}
    feedback = market_feedback or {}
    stress = _clamp(event.get("stress_level", 0))
    attention = _clamp(event.get("attention_pressure", 0))
    prior_bias = _clamp(previous_interpretation.get("system_induced_bias_field", 0))
    feedback_delta = abs(_clamp(feedback.get("realized_stress", stress)) - stress)

    influence = _clamp(prior_bias * 0.35 + feedback_delta * 0.45 + max(0, attention - 70) * 0.2)
    return {
        "loop": [
            "market_to_atlas_observation",
            "atlas_observation_to_interpretation",
            "interpretation_to_state_update",
            "state_update_to_next_market_feedback_probe",
        ],
        "market_system_loop_closed": True,
        "one_way_pipeline": False,
        "feedback_influence_score": influence,
        "interpretation_frame_affects_next_input": True,
        "market_reaction_model": "observed_next_cycle_feedback_not_trade_execution",
        "feedback_basis": "prior_interpretation_and_realized_market_response",
    }


def self_referential_causality(
    unified_state: Mapping[str, Any],
    *,
    previous_unified_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Measure how previous Atlas interpretation shapes current interpretation."""

    event = _mapping(unified_state.get("event_state"))
    causal = _mapping(unified_state.get("causal_state"))
    latent = _mapping(unified_state.get("latent_structure_state"))
    prior = _mapping(previous_unified_state.get("self_reference")) if previous_unified_state else {}
    prior_depth = _clamp(prior.get("interpretation_recursion_depth", 0))
    attention_gap = abs(_clamp(event.get("attention_pressure", 0)) - _clamp(latent.get("attention_persistence_field", 0)))
    causal_pressure = _clamp(causal.get("regime_transition_probability", 0))
    recursion_depth = min(5, 1 + prior_depth)
    bias = _clamp(attention_gap * 0.35 + causal_pressure * 0.25 + prior.get("system_induced_bias_field", 0) * 0.35)
    return {
        "feedback_influence_score": _clamp(bias * 0.8),
        "interpretation_recursion_depth": recursion_depth,
        "system_induced_bias_field": bias,
        "past_system_state_affects_current_reasoning": previous_unified_state is not None,
        "self_reference_present": True,
        "causality_mode": "self_referential_interpretation_not_external_truth",
    }


def co_evolution_dynamics(
    unified_state: Mapping[str, Any],
    feedback_loop: Mapping[str, Any],
    self_reference: Mapping[str, Any],
    *,
    previous_unified_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Describe mutual adaptation between market representation and Atlas state."""

    event = _mapping(unified_state.get("event_state"))
    physics = _mapping(unified_state.get("physics_constraint_state"))
    law = _mapping(unified_state.get("emergent_law_state"))
    previous_coevolution = _mapping(previous_unified_state.get("co_evolution")) if previous_unified_state else {}
    prior_adaptation = _clamp(previous_coevolution.get("system_adaptation_rate", 0))

    market_shift = _clamp(
        event.get("stress_level", 0) * 0.3
        + event.get("attention_pressure", 0) * 0.2
        + physics.get("regime_fragility_index", 0) * 0.25
        + law.get("instability_collapse_risk", 0) * 0.25
    )
    adaptation_rate = _clamp(
        prior_adaptation * 0.35
        + self_reference.get("system_induced_bias_field", 0) * 0.3
        + feedback_loop.get("feedback_influence_score", 0) * 0.35
    )
    sensitivity = _clamp(market_shift * 0.55 + adaptation_rate * 0.45)
    return {
        "co_evolution_trajectory": [
            {"actor": "market_state", "movement": market_shift},
            {"actor": "atlas_interpretation_state", "movement": adaptation_rate},
            {"actor": "next_cycle_joint_context", "movement": sensitivity},
        ],
        "system_adaptation_rate": adaptation_rate,
        "market_sensitivity_to_system_state": sensitivity,
        "mutual_influence_loop": True,
        "system_and_market_evolve_together": True,
    }


def interpret_unified_state(
    unified_state: Mapping[str, Any],
    *,
    feedback_loop: Mapping[str, Any] | None = None,
    self_reference: Mapping[str, Any] | None = None,
    co_evolution: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Generate interpretation only from the unified state representation."""

    event = _mapping(unified_state.get("event_state"))
    causal = _mapping(unified_state.get("causal_state"))
    latent = _mapping(unified_state.get("latent_structure_state"))
    physics = _mapping(unified_state.get("physics_constraint_state"))
    law = _mapping(unified_state.get("emergent_law_state"))
    feedback = feedback_loop or {}
    self_ref = self_reference or {}
    coevo = co_evolution or {}

    causal_latent_alignment = _clamp(
        100
        - abs(_clamp(causal.get("regime_transition_probability", 0)) - _clamp(latent.get("hidden_risk_compression", 0)))
        - abs(_clamp(event.get("attention_pressure", 0)) - _clamp(latent.get("attention_persistence_field", 0))) * 0.25
    )
    constraint_pressure = _clamp(
        physics.get("regime_fragility_index", 0) * 0.45
        + len(physics.get("constraint_violations", [])) * 16
        + (100 - _clamp(physics.get("stability_score", 0))) * 0.25
    )
    law_consistency = _clamp(
        law.get("law_system_stability_score", 0)
        - law.get("instability_collapse_risk", 0) * 0.25
        - (18 if law.get("multi_law_coexistence_zone") else 0)
    )
    bias = _clamp(self_ref.get("system_induced_bias_field", 0))
    dominant = _dominant_structure(latent, constraint_pressure, law_consistency, feedback, coevo)
    return {
        "dominant_regime_structure": dominant,
        "causal_latent_alignment": causal_latent_alignment,
        "physics_constraint_pressure": constraint_pressure,
        "emergent_law_consistency": law_consistency,
        "feedback_influence_score": _clamp(feedback.get("feedback_influence_score", 0)),
        "system_induced_bias_field": bias,
        "unified_state_only": True,
        "external_final_truth_layer": False,
        "interpretation_mode": "recursive_adaptive_closed_loop",
    }


def system_self_adaptation(
    unified_state: Mapping[str, Any],
    interpretation: Mapping[str, Any],
    *,
    previous_weights: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Adapt internal interpretation weights, never portfolio or trading weights."""

    weights = {
        "event_weight": 25,
        "causal_weight": 25,
        "latent_weight": 20,
        "physics_weight": 15,
        "law_weight": 15,
    }
    if previous_weights:
        weights.update({key: _clamp(value) for key, value in previous_weights.items() if key in weights})

    event = _mapping(unified_state.get("event_state"))
    physics = _mapping(unified_state.get("physics_constraint_state"))
    law = _mapping(unified_state.get("emergent_law_state"))
    mismatch = _clamp(
        abs(_clamp(event.get("stress_level", 0)) - _clamp(physics.get("regime_fragility_index", 0))) * 0.45
        + (100 - _clamp(interpretation.get("causal_latent_alignment", 0))) * 0.35
        + law.get("instability_collapse_risk", 0) * 0.2
    )

    if mismatch >= 55:
        weights["event_weight"] = _clamp(weights["event_weight"] - 4)
        weights["latent_weight"] = _clamp(weights["latent_weight"] + 3)
        weights["physics_weight"] = _clamp(weights["physics_weight"] + 2)
        adaptation = "increase_structure_weights_after_mismatch"
    elif law.get("over_evolution_risk"):
        weights["law_weight"] = _clamp(weights["law_weight"] - 3)
        weights["causal_weight"] = _clamp(weights["causal_weight"] + 2)
        adaptation = "dampen_law_weight_after_instability"
    else:
        weights["causal_weight"] = _clamp(weights["causal_weight"] + 1)
        adaptation = "minor_causal_weight_reinforcement"

    return {
        "internal_interpretation_weights": weights,
        "structural_prediction_error_proxy": mismatch,
        "regime_mismatch_signal": mismatch >= 45,
        "law_instability_pattern": bool(law.get("over_evolution_risk")),
        "bias_correction_strength": _clamp(mismatch * 0.45),
        "adaptation_action": adaptation,
        "adapts_trading_weights": False,
        "adapts_portfolio_weights": False,
    }


def infer_unified_market_intelligence(
    *,
    fusion: Mapping[str, Any],
    causal: Mapping[str, Any],
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
    physics_constraints: Mapping[str, Any],
    market_laws: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
    previous_unified_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Return full v1.0 Unified Market Intelligence output."""

    unified_state = build_unified_market_state(
        event_state=fusion,
        causal_state=causal,
        latent_structure_state=latent_structure,
        physics_constraint_state=physics_constraints,
        emergent_law_state=market_laws,
        memory_state=memory_summary,
        previous_unified_state=previous_unified_state,
    )
    feedback = market_system_feedback_loop(unified_state, previous_unified_state=previous_unified_state)
    self_reference = self_referential_causality(unified_state, previous_unified_state=previous_unified_state)
    co_evolution = co_evolution_dynamics(
        unified_state,
        feedback,
        self_reference,
        previous_unified_state=previous_unified_state,
    )
    interpretation = interpret_unified_state(
        unified_state,
        feedback_loop=feedback,
        self_reference=self_reference,
        co_evolution=co_evolution,
    )
    previous_weights = _mapping(_mapping(previous_unified_state.get("self_adaptation")).get("internal_interpretation_weights")) if previous_unified_state else {}
    adaptation = system_self_adaptation(unified_state, interpretation, previous_weights=previous_weights)

    return {
        "unified_market_state": unified_state,
        "feedback_loop_design": feedback,
        "self_reference": self_reference,
        "co_evolution": co_evolution,
        "unified_interpretation": interpretation,
        "self_adaptation": adaptation,
        "world_model_context": {
            "phase_transition_likelihood": _clamp(
                _mapping(world_model.get("regime_emergence_dynamics")).get("phase_transition_likelihood", 0)
            ),
            "state_is_context_not_final_truth": True,
        },
        "closed_loop_market_cognition": True,
        "no_external_final_truth_layer": True,
        "model_mode": "interpretable_unified_market_intelligence_non_ml",
        "not_prediction_engine": True,
        "no_trade_action": True,
        "no_signal_generator": True,
        "interpretability_preserved": True,
    }


def _dominant_structure(
    latent: Mapping[str, Any],
    constraint_pressure: int,
    law_consistency: int,
    feedback: Mapping[str, Any],
    co_evolution: Mapping[str, Any],
) -> str:
    basin = str(latent.get("dominant_attractor_basin", "Unknown"))
    feedback_pressure = _clamp(feedback.get("feedback_influence_score", 0))
    sensitivity = _clamp(co_evolution.get("market_sensitivity_to_system_state", 0))
    if constraint_pressure >= 70:
        return "constraint-dominated closed-loop stress"
    if feedback_pressure >= 55 or sensitivity >= 65:
        return "self-referential transition formation"
    if law_consistency < 45:
        return "unstable law-coexistence formation"
    return f"{basin} unified structure"


def _coherence_score(unified: Mapping[str, Any]) -> int:
    event = _mapping(unified.get("event_state"))
    causal = _mapping(unified.get("causal_state"))
    physics = _mapping(unified.get("physics_constraint_state"))
    law = _mapping(unified.get("emergent_law_state"))
    event_causal_gap = abs(_clamp(event.get("stress_level", 0)) - _clamp(causal.get("regime_transition_probability", 0)))
    physics_law_gap = abs(_clamp(physics.get("stability_score", 0)) - _clamp(law.get("law_system_stability_score", 0)))
    return _clamp(100 - event_causal_gap * 0.35 - physics_law_gap * 0.25)


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _clamp(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, int(number)))
