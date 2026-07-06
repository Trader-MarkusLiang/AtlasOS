"""Market Law Emergence Engine for Atlas Runtime v0.9.

This module derives interpretable law candidates from repeated structural
patterns and constraint behavior. It is deterministic rule emergence, not ML,
black-box optimization, forecasting, trading execution, or portfolio automation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


LAW_TYPES = (
    "liquidity_attention_coupling",
    "entropy_fragility_coupling",
    "risk_compression_persistence",
    "flow_continuity_constraint",
    "attention_decay_redistribution",
)


def discover_market_laws(
    *,
    latent_patterns: Iterable[Mapping[str, Any]],
    physics_patterns: Iterable[Mapping[str, Any]],
    regime_transitions: Iterable[Mapping[str, Any]] | None = None,
    attention_flow_patterns: Iterable[Mapping[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Detect repeated structural invariants as emergent law candidates."""

    latent_list = list(latent_patterns)
    physics_list = list(physics_patterns)
    transition_list = list(regime_transitions or [])
    attention_flow_list = list(attention_flow_patterns or [])
    sample_count = max(1, len(latent_list), len(physics_list), len(transition_list), len(attention_flow_list))

    law_specs = {
        "liquidity_attention_coupling": _law_measure(
            _count_high_gap(latent_list, "attention_persistence_field", "structural_liquidity_pressure", threshold=28),
            _count_violations(physics_list, "liquidity_conservation_violation"),
            sample_count,
            "regime-dependent: attention mania / liquidity stress",
        ),
        "entropy_fragility_coupling": _law_measure(
            _count_high_entropy(physics_list, threshold=60),
            _count_instability_failures(physics_list),
            sample_count,
            "regime-dependent: distribution / crash stress",
        ),
        "risk_compression_persistence": _law_measure(
            _count_high_value(latent_list, "hidden_risk_compression", threshold=65),
            _count_low_value(latent_list, "hidden_risk_compression", threshold=35),
            sample_count,
            "regime-dependent: crash stress",
        ),
        "flow_continuity_constraint": _law_measure(
            _count_flow_continuity(physics_list),
            _count_violations(physics_list, "flow_continuity_violation"),
            sample_count,
            "regime-dependent: rotation / liquidity stress",
        ),
        "attention_decay_redistribution": _law_measure(
            _count_attention_decay(attention_flow_list),
            _count_high_value(latent_list, "attention_persistence_field", threshold=92),
            sample_count,
            "regime-dependent: attention mania",
        ),
    }

    laws: List[Dict[str, Any]] = []
    for law_type, measure in law_specs.items():
        recurrence = measure["recurrence_frequency"]
        violation = measure["violation_rate"]
        stability = _clamp((recurrence * 0.75) + ((100 - violation) * 0.25))
        if recurrence >= 25 or stability >= 45:
            laws.append(
                {
                    "law_type": law_type,
                    "stability_score": stability,
                    "recurrence_frequency": recurrence,
                    "violation_rate": violation,
                    "regime_dependency": measure["regime_dependency"],
                    "emergent": True,
                    "formation_basis": "repeated_structural_pattern",
                }
            )

    return sorted(laws, key=lambda item: (item["stability_score"], item["recurrence_frequency"]), reverse=True)


def evolve_constraints(
    laws: Iterable[Mapping[str, Any]],
    *,
    previous_constraint_graph: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Evolve constraints based on law stability and contradictions."""

    previous = previous_constraint_graph or {}
    updated: Dict[str, Dict[str, Any]] = {}
    drift: Dict[str, int] = {}

    for law in laws:
        law_type = str(law.get("law_type", "unknown_law"))
        stability = _clamp(law.get("stability_score", 0))
        violation = _clamp(law.get("violation_rate", 0))
        previous_weight = _clamp(previous.get(law_type, {}).get("weight", 50) if isinstance(previous.get(law_type), Mapping) else 50)

        if stability >= 70 and violation <= 35:
            new_weight = _clamp(previous_weight + 12)
            action = "strengthen"
        elif violation >= 55 and stability < 60:
            new_weight = _clamp(previous_weight - 14)
            action = "decay"
        elif violation >= 45 and stability >= 55:
            new_weight = previous_weight
            action = "split_into_sub_laws"
        else:
            new_weight = _clamp(previous_weight + (stability - 50) * 0.15)
            action = "minor_drift"

        updated[law_type] = {
            "weight": new_weight,
            "evolution_action": action,
            "stability_score": stability,
            "violation_rate": violation,
        }
        drift[law_type] = new_weight - previous_weight

        if action == "split_into_sub_laws":
            updated[f"{law_type}:stable_context"] = {
                "weight": _clamp(new_weight + 8),
                "evolution_action": "birth_from_contradiction",
                "parent_law": law_type,
            }
            updated[f"{law_type}:unstable_context"] = {
                "weight": _clamp(new_weight - 8),
                "evolution_action": "birth_from_contradiction",
                "parent_law": law_type,
            }

    return {
        "updated_constraint_graph": updated,
        "constraint_stability_weights": {key: value["weight"] for key, value in updated.items()},
        "evolutionary_drift_map": drift,
        "constraints_are_static": False,
    }


def regime_conditioned_laws(
    laws: Iterable[Mapping[str, Any]],
    *,
    regimes: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Return regime-specific law variants."""

    regime_list = list(regimes or ["liquidity_expansion", "crash_stress", "attention_mania", "distribution"])
    variants: Dict[str, Dict[str, Any]] = {}
    for law in laws:
        law_type = str(law.get("law_type", "unknown_law"))
        stability = _clamp(law.get("stability_score", 0))
        variants[law_type] = {}
        for regime in regime_list:
            deformation = _regime_deformation(law_type, regime)
            variants[law_type][regime] = {
                "regime_specific_behavior": _regime_behavior(law_type, regime),
                "constraint_deformation_factor": deformation,
                "stability_shift_index": _clamp(stability + deformation - 50),
            }
    return {
        "law_variants": variants,
        "same_law_varies_by_regime": True,
    }


def simulate_meta_dynamics(
    laws: Iterable[Mapping[str, Any]],
    evolved_constraints: Mapping[str, Any],
) -> Dict[str, Any]:
    """Model how law candidates evolve over time."""

    law_list = list(laws)
    drift_map = evolved_constraints.get("evolutionary_drift_map", {}) if isinstance(evolved_constraints.get("evolutionary_drift_map"), Mapping) else {}
    graph = evolved_constraints.get("updated_constraint_graph", {}) if isinstance(evolved_constraints.get("updated_constraint_graph"), Mapping) else {}
    birth_events = [key for key, value in graph.items() if isinstance(value, Mapping) and "birth" in str(value.get("evolution_action", ""))]
    decay_events = [law.get("law_type", "unknown_law") for law in law_list if _clamp(law.get("violation_rate", 0)) >= 55]
    mutation_events = [key for key, drift in drift_map.items() if abs(int(drift)) >= 8]
    drift_velocity = _clamp(sum(abs(int(value)) for value in drift_map.values()) / max(1, len(drift_map)))
    mutation_rate = _clamp((len(mutation_events) + len(birth_events) + len(decay_events)) * 14)
    organization = _clamp(
        (sum(_clamp(law.get("stability_score", 0)) for law in law_list) / max(1, len(law_list))) - mutation_rate * 0.25
    )
    return {
        "law_drift_velocity": drift_velocity,
        "structural_mutation_rate": mutation_rate,
        "constraint_birth_death_events": {
            "birth": birth_events,
            "decay": decay_events,
            "mutation": mutation_events,
        },
        "system_self_organization_index": organization,
    }


def check_law_consistency(laws: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Preserve contradictions as coexistence zones instead of forcing resolution."""

    law_list = list(laws)
    clusters: List[Dict[str, Any]] = []
    by_type = {str(law.get("law_type", "")): law for law in law_list}

    if "liquidity_attention_coupling" in by_type and "attention_decay_redistribution" in by_type:
        clusters.append(
            {
                "cluster": ["liquidity_attention_coupling", "attention_decay_redistribution"],
                "contradiction": "attention can amplify flow while also redistributing / decaying",
            }
        )
    if "entropy_fragility_coupling" in by_type and "risk_compression_persistence" in by_type:
        clusters.append(
            {
                "cluster": ["entropy_fragility_coupling", "risk_compression_persistence"],
                "contradiction": "entropy can disperse structure while risk compression can persist",
            }
        )

    ambiguity = _clamp(len(clusters) * 25)
    consistency = _clamp(100 - ambiguity - _average_violation(law_list) * 0.25)
    return {
        "consistency_score": consistency,
        "contradiction_clusters": clusters,
        "regime_ambiguity_index": ambiguity,
        "multi_law_coexistence_zone": bool(clusters),
        "forced_resolution": False,
    }


def infer_market_law_emergence(
    *,
    latent_structure: Mapping[str, Any],
    physics_constraints: Mapping[str, Any],
    world_model: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return the full v0.9 Market Law Emergence output."""

    latent_patterns = _build_latent_pattern_history(latent_structure)
    physics_patterns = _build_physics_pattern_history(physics_constraints)
    attention_flow_patterns = _build_attention_flow_patterns(world_model, latent_structure)
    transition_patterns = _build_transition_patterns(memory_summary)

    laws = discover_market_laws(
        latent_patterns=latent_patterns,
        physics_patterns=physics_patterns,
        regime_transitions=transition_patterns,
        attention_flow_patterns=attention_flow_patterns,
    )
    evolved = evolve_constraints(laws)
    conditioned = regime_conditioned_laws(laws)
    meta = simulate_meta_dynamics(laws, evolved)
    consistency = check_law_consistency(laws)
    stability = _system_stability(laws, meta, consistency)

    return {
        "discovered_market_laws": laws,
        "constraint_evolution": evolved,
        "regime_dependent_law_behavior": conditioned,
        "meta_dynamics_report": meta,
        "contradiction_analysis": consistency,
        "system_stability_evaluation": stability,
        "law_emergence_basis": "repeated_interpretable_structural_patterns",
        "constraints_are_static": False,
        "model_mode": "interpretable_market_law_emergence_non_ml",
        "not_prediction_engine": True,
        "no_trade_action": True,
    }


def _law_measure(recurrence_count: int, violation_count: int, sample_count: int, regime_dependency: str) -> Dict[str, Any]:
    return {
        "recurrence_frequency": _clamp((recurrence_count / max(1, sample_count)) * 100),
        "violation_rate": _clamp((violation_count / max(1, sample_count)) * 100),
        "regime_dependency": regime_dependency,
    }


def _build_latent_pattern_history(latent_structure: Mapping[str, Any]) -> List[Dict[str, Any]]:
    latent = latent_structure.get("latent_variables", {}) if isinstance(latent_structure.get("latent_variables"), Mapping) else {}
    trajectory = latent_structure.get("structural_evolution", [])
    history = [dict(item) for item in trajectory] if isinstance(trajectory, list) else []
    if latent:
        history.append(dict(latent))
    return history or [{}]


def _build_physics_pattern_history(physics_constraints: Mapping[str, Any]) -> List[Dict[str, Any]]:
    stability = physics_constraints.get("system_stability_report", {})
    entropy = physics_constraints.get("entropy_state", {})
    invariants = physics_constraints.get("structural_invariants", {})
    conservation = physics_constraints.get("conservation_state", {})
    return [
        {
            "total_system_entropy": entropy.get("total_system_entropy", 0),
            "regime_fragility_index": stability.get("regime_fragility_index", 0),
            "constraint_violations": invariants.get("constraint_violations", []),
            "flow_continuity_satisfied": conservation.get("flow_continuity", {}).get("satisfied", True)
            if isinstance(conservation.get("flow_continuity", {}), Mapping)
            else True,
        }
    ]


def _build_attention_flow_patterns(
    world_model: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    trajectory = world_model.get("baseline_trajectory", [])
    attention = latent_structure.get("attention_field_dynamics", {})
    patterns = [dict(item) for item in trajectory] if isinstance(trajectory, list) else []
    if isinstance(attention, Mapping):
        patterns.append(dict(attention))
    return patterns or [{}]


def _build_transition_patterns(memory_summary: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "dominant_state": memory_summary.get("dominant_state", "NORMAL"),
            "sequence_length": memory_summary.get("sequence_length", 0),
        }
    ]


def _count_high_gap(items: List[Mapping[str, Any]], left: str, right: str, *, threshold: int) -> int:
    return sum(1 for item in items if abs(int(item.get(left, 0)) - int(item.get(right, 0))) >= threshold)


def _count_high_entropy(items: List[Mapping[str, Any]], *, threshold: int) -> int:
    return sum(1 for item in items if int(item.get("total_system_entropy", 0)) >= threshold)


def _count_instability_failures(items: List[Mapping[str, Any]]) -> int:
    return sum(1 for item in items if int(item.get("regime_fragility_index", 0)) >= 70)


def _count_high_value(items: List[Mapping[str, Any]], key: str, *, threshold: int) -> int:
    return sum(1 for item in items if int(item.get(key, 0)) >= threshold)


def _count_low_value(items: List[Mapping[str, Any]], key: str, *, threshold: int) -> int:
    return sum(1 for item in items if int(item.get(key, 0)) <= threshold)


def _count_flow_continuity(items: List[Mapping[str, Any]]) -> int:
    return sum(1 for item in items if item.get("flow_continuity_satisfied", True))


def _count_violations(items: List[Mapping[str, Any]], violation_name: str) -> int:
    count = 0
    for item in items:
        violations = item.get("constraint_violations", [])
        if isinstance(violations, list) and violation_name in violations:
            count += 1
    return count


def _count_attention_decay(items: List[Mapping[str, Any]]) -> int:
    count = 0
    for item in items:
        if "decay_rate" in item and int(item.get("decay_rate", 0)) > 0:
            count += 1
        elif int(item.get("attention_field", 0)) >= 50:
            count += 1
    return count


def _regime_deformation(law_type: str, regime: str) -> int:
    table = {
        "liquidity_expansion": {
            "liquidity_attention_coupling": 18,
            "flow_continuity_constraint": 10,
        },
        "crash_stress": {
            "entropy_fragility_coupling": 22,
            "risk_compression_persistence": 25,
        },
        "attention_mania": {
            "attention_decay_redistribution": 24,
            "liquidity_attention_coupling": 14,
        },
        "distribution": {
            "entropy_fragility_coupling": 16,
            "flow_continuity_constraint": 13,
        },
    }
    return table.get(regime, {}).get(law_type, 0)


def _regime_behavior(law_type: str, regime: str) -> str:
    return f"{law_type} deforms under {regime} conditions"


def _average_violation(laws: List[Mapping[str, Any]]) -> int:
    if not laws:
        return 0
    return _clamp(sum(_clamp(law.get("violation_rate", 0)) for law in laws) / len(laws))


def _system_stability(
    laws: List[Mapping[str, Any]],
    meta: Mapping[str, Any],
    consistency: Mapping[str, Any],
) -> Dict[str, Any]:
    average_stability = 0 if not laws else sum(_clamp(law.get("stability_score", 0)) for law in laws) // len(laws)
    instability = _clamp(
        int(meta.get("structural_mutation_rate", 0)) * 0.35
        + int(consistency.get("regime_ambiguity_index", 0)) * 0.4
        + max(0, 50 - average_stability)
    )
    return {
        "law_system_stability_score": _clamp(100 - instability),
        "over_evolution_risk": int(meta.get("structural_mutation_rate", 0)) >= 55,
        "instability_collapse_risk": instability,
        "interpretability_preserved": True,
    }


def _clamp(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, int(number)))
