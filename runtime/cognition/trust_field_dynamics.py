"""Trust field dynamics for Atlas Runtime v0.5.

Trust is represented as a bounded field over runtime components. The field is
metadata for structural governance; it does not override cognition outputs.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


DEFAULT_TRUST_FIELD = {
    "event_fusion": 0.5,
    "causal_graph": 0.5,
    "regime_topology": 0.5,
    "llm_feedback": 0.5,
    "structural_evolution": 0.5,
    "decision_contract": 0.5,
}
MAX_FIELD_STEP = 0.08


def evolve_trust_field(
    *,
    previous_field: Mapping[str, Any] | None,
    system_trust_state: Mapping[str, Any],
    trust_score: Mapping[str, Any],
    feedback_delta: Mapping[str, Any],
    regime_volatility: float = 0.0,
    causal_consistency: float = 0.5,
) -> Dict[str, Any]:
    """Evolve component trust smoothly from existing reliability signals."""

    previous = {**DEFAULT_TRUST_FIELD, **(_as_mapping(previous_field))}
    global_trust = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    feedback_trust = _clamp01(_float(trust_score.get("feedback_consistency_trust"), 0.5))
    cognitive_trust = _clamp01(_float(trust_score.get("cognitive_trust"), 0.5))
    rolling_trust = _clamp01(_float(system_trust_state.get("rolling_trust_index"), global_trust))
    feedback_stability = _clamp01(_float(system_trust_state.get("feedback_stability_index"), feedback_trust))
    volatility_penalty = min(0.22, abs(_float(regime_volatility, 0.0)) / 260.0)
    feedback_penalty = min(0.18, _feedback_magnitude(feedback_delta) * 2.0)
    consistency = _clamp01(causal_consistency)

    targets = {
        "event_fusion": cognitive_trust - volatility_penalty * 0.4,
        "causal_graph": (cognitive_trust * 0.55 + consistency * 0.45) - feedback_penalty * 0.25,
        "regime_topology": (rolling_trust * 0.55 + cognitive_trust * 0.45) - volatility_penalty * 0.5,
        "llm_feedback": feedback_trust * 0.6 + feedback_stability * 0.4 - feedback_penalty,
        "structural_evolution": global_trust * 0.5 + rolling_trust * 0.35 + consistency * 0.15 - volatility_penalty * 0.35,
        "decision_contract": _clamp01(_float(trust_score.get("llm_trust"), global_trust)),
    }
    field = {
        key: _smooth(previous.get(key, 0.5), _clamp01(target))
        for key, target in targets.items()
    }
    deltas = {key: round(field[key] - _float(previous.get(key), 0.5), 4) for key in field}
    evolution = max((abs(value) for value in deltas.values()), default=0.0)
    return {
        "trust_field": field,
        "trust_field_delta": deltas,
        "trust_field_evolution": round(evolution, 4),
        "field_stability": round(_clamp01(1.0 - evolution / MAX_FIELD_STEP), 4),
        "smooth_update": True,
        "max_step": MAX_FIELD_STEP,
        "metadata_only": True,
    }


def trust_field_summary(state: Mapping[str, Any] | None) -> Dict[str, Any]:
    source = _as_mapping(state)
    field = _as_mapping(source.get("trust_field")) or DEFAULT_TRUST_FIELD
    return {
        "trust_field": dict(field),
        "trust_field_evolution": _float(source.get("trust_field_evolution"), 0.0),
        "field_stability": _float(source.get("field_stability"), 0.5),
    }


def _smooth(previous: Any, target: float) -> float:
    old = _clamp01(_float(previous, 0.5))
    delta = max(-MAX_FIELD_STEP, min(MAX_FIELD_STEP, target - old))
    return round(_clamp01(old + delta), 4)


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


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
