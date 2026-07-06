"""Structural evolution controller for Atlas Runtime v0.5.

All v0.5 self-organization changes pass through this controller so adaptation
remains bounded, reversible, and trust-gated.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


LOW_TRUST_FIELD_THRESHOLD = 0.35
MAX_CAUSAL_DELTA = 0.025
MAX_REGIME_SHIFT = 0.035
MAX_TRUST_PROPAGATION = 0.08
MAX_HISTORY = 20


def apply_structural_evolution(
    *,
    proposed: Mapping[str, Any],
    trust_field_state: Mapping[str, Any],
    previous_state: Mapping[str, Any] | None = None,
    explanation_feedback: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Gate and bound a self-organization proposal."""

    trust_field = _as_mapping(trust_field_state.get("trust_field"))
    explanation = explanation_feedback if isinstance(explanation_feedback, Mapping) else {}
    previous = previous_state if isinstance(previous_state, Mapping) else {}
    previous_applied = _as_mapping(previous.get("applied_evolution"))
    gate = _trust_gate(trust_field)

    if gate < LOW_TRUST_FIELD_THRESHOLD:
        return {
            "status": "frozen",
            "reason": "low_trust_field_freeze",
            "trust_gate": "closed",
            "trust_gate_value": round(gate, 4),
            "structural_shift_index": 0.0,
            "causal_reweight_delta": {},
            "regime_attractor_shift": 0.0,
            "trust_field_evolution": _bounded(
                trust_field_state.get("trust_field_evolution"),
                MAX_TRUST_PROPAGATION,
            ),
            "applied_evolution": dict(previous_applied),
            "explanation_feedback_applied": False,
            "reversible_delta_log": list(previous.get("reversible_delta_log", []))[-MAX_HISTORY:],
            "bounded": True,
            "reversible": True,
        }

    scale = min(1.0, gate)
    proposed_causal = _merge_delta_maps(
        _as_mapping(proposed.get("causal_reweight_delta")),
        _as_mapping(explanation.get("edge_weight_updates")),
        MAX_CAUSAL_DELTA,
    )
    causal_delta = {
        str(key): _bounded(_float(value) * scale, MAX_CAUSAL_DELTA)
        for key, value in proposed_causal.items()
    }
    regime_shift = _bounded(_float(proposed.get("regime_attractor_shift"), 0.0) * scale, MAX_REGIME_SHIFT)
    trust_evolution = _bounded(_float(trust_field_state.get("trust_field_evolution"), 0.0), MAX_TRUST_PROPAGATION)
    structural_shift = round(
        min(0.12, sum(abs(value) for value in causal_delta.values()) + abs(regime_shift) + abs(trust_evolution) * 0.25),
        4,
    )
    applied = {
        "causal_reweight_delta": causal_delta,
        "regime_attractor_shift": regime_shift,
        "trust_field_evolution": trust_evolution,
    }
    delta_log = list(previous.get("reversible_delta_log", [])) if isinstance(previous.get("reversible_delta_log"), list) else []
    delta_log.append(
        {
            "applied": applied,
            "inverse": {
                "causal_reweight_delta": {key: round(-value, 4) for key, value in causal_delta.items()},
                "regime_attractor_shift": round(-regime_shift, 4),
                "trust_field_evolution": round(-trust_evolution, 4),
            },
        }
    )
    return {
        "status": "applied",
        "trust_gate": "open",
        "trust_gate_value": round(gate, 4),
        "structural_shift_index": structural_shift,
        "causal_reweight_delta": causal_delta,
        "regime_attractor_shift": regime_shift,
        "trust_field_evolution": trust_evolution,
        "applied_evolution": applied,
        "explanation_feedback_applied": bool(explanation.get("edge_weight_updates")),
        "reversible_delta_log": delta_log[-MAX_HISTORY:],
        "bounded": True,
        "reversible": True,
    }


def _trust_gate(trust_field: Mapping[str, Any]) -> float:
    if not trust_field:
        return 0.0
    values = [_clamp01(_float(value, 0.0)) for value in trust_field.values()]
    return min(values) if values else 0.0


def _bounded(value: Any, cap: float) -> float:
    number = _float(value, 0.0)
    return round(max(-cap, min(cap, number)), 4)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _merge_delta_maps(primary: Mapping[str, Any], secondary: Mapping[str, Any], cap: float) -> Dict[str, float]:
    merged = {str(key): _float(value) for key, value in primary.items()}
    for key, value in secondary.items():
        merged[str(key)] = _bounded(merged.get(str(key), 0.0) + _float(value), cap)
    return merged


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
