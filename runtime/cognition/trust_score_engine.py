"""Trust score engine for Atlas Runtime v0.3.2.

This module computes meta-confidence over existing cognition. It does not
change cognitive outputs, regime labels, LLM behavior, feedback deltas, or CDE.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def compute_trust_score(
    cognitive_state: Dict[str, Any],
    llm_output: Dict[str, Any],
    feedback_delta: Dict[str, Any],
) -> Dict[str, float]:
    """Compute bounded trust scores from existing runtime outputs."""

    cognition = cognitive_state if isinstance(cognitive_state, dict) else {}
    packet = llm_output if isinstance(llm_output, dict) else {}
    feedback = feedback_delta if isinstance(feedback_delta, dict) else {}

    llm_confidence = _clamp01(_float(packet.get("confidence"), 0.0))
    llm_trust = _clamp01(0.35 + llm_confidence * 0.55 - _hallucination_penalty(packet))

    cognitive_trust = _clamp01(
        0.5
        + _score_component(cognition.get("fusion", {}).get("stability_score"), center=50, scale=100)
        + _score_component(
            cognition.get("physics_constraints", {}).get("system_stability_report", {}).get("stability_score"),
            center=50,
            scale=140,
        )
    )

    regime_stability_trust = _clamp01(
        0.65
        - abs(_float(cognition.get("fusion", {}).get("stress_score"), 0.0)) / 300
        - _transition_penalty(cognition.get("controller", {}))
    )

    feedback_consistency_trust = _clamp01(1.0 - min(0.7, _feedback_magnitude(feedback) * 4.0))
    global_trust_index = _clamp01(
        llm_trust * 0.25
        + cognitive_trust * 0.3
        + regime_stability_trust * 0.25
        + feedback_consistency_trust * 0.2
    )
    return {
        "llm_trust": round(llm_trust, 4),
        "cognitive_trust": round(cognitive_trust, 4),
        "regime_stability_trust": round(regime_stability_trust, 4),
        "feedback_consistency_trust": round(feedback_consistency_trust, 4),
        "global_trust_index": round(global_trust_index, 4),
    }


def trust_decay_over_time(
    *,
    previous_trust_state: Optional[Dict[str, Any]],
    current_trust_score: Dict[str, float],
    feedback_delta: Dict[str, Any],
    regime_volatility: float = 0.0,
) -> Dict[str, Any]:
    """Update rolling trust without changing cognition."""

    previous = previous_trust_state if isinstance(previous_trust_state, dict) else {}
    previous_rolling = _clamp01(_float(previous.get("rolling_trust_index"), 0.5))
    current = _clamp01(_float(current_trust_score.get("global_trust_index"), 0.5))
    feedback_magnitude = _feedback_magnitude(feedback_delta)
    volatility_penalty = min(0.12, abs(_float(regime_volatility, 0.0)) / 500)
    instability_penalty = min(0.12, feedback_magnitude * 1.5)
    alignment_bonus = 0.03 if current >= previous_rolling and feedback_magnitude < 0.04 else 0.0
    rolling = _clamp01(previous_rolling * 0.7 + current * 0.3 + alignment_bonus - volatility_penalty - instability_penalty)
    decay = _clamp01(1.0 - rolling)
    return {
        "rolling_trust_index": round(rolling, 4),
        "regime_trust_decay": round(decay, 4),
        "feedback_stability_index": round(_clamp01(1.0 - feedback_magnitude * 4.0), 4),
        "trust_direction": "improving" if rolling >= previous_rolling else "decaying",
        "trust_adjustment_reason": _reason(alignment_bonus, volatility_penalty, instability_penalty),
    }


def calibrate_confidence(confidence: Any, trust_score: Dict[str, Any]) -> Dict[str, float]:
    """Return calibrated confidence metadata without mutating DecisionPacket."""

    base = _clamp01(_float(confidence, 0.0))
    factor = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    return {
        "calibrated_confidence": round(base * factor, 4),
        "confidence_adjustment_factor": round(factor, 4),
    }


def _hallucination_penalty(packet: Dict[str, Any]) -> float:
    text = " ".join(str(packet.get(key, "")) for key in ("causal_summary", "reasoning_trace")).lower()
    penalty = 0.0
    for term in ("guaranteed", "certain", "must", "target weight", "execute"):
        if term in text:
            penalty += 0.08
    if packet.get("recommended_action") not in {"observe", "reduce", "neutral"}:
        penalty += 0.2
    return min(0.4, penalty)


def _transition_penalty(controller: Dict[str, Any]) -> float:
    if not isinstance(controller, dict):
        return 0.05
    if controller.get("transition_allowed") is False:
        return 0.08
    return 0.0


def _feedback_magnitude(feedback_delta: Dict[str, Any]) -> float:
    if not isinstance(feedback_delta, dict):
        return 0.0
    values = []
    for value in feedback_delta.values():
        if isinstance(value, dict):
            values.extend(abs(_float(item, 0.0)) for item in value.values())
        else:
            values.append(abs(_float(value, 0.0)))
    return max(values, default=0.0)


def _score_component(value: Any, *, center: float, scale: float) -> float:
    return (_float(value, center) - center) / scale


def _reason(alignment_bonus: float, volatility_penalty: float, instability_penalty: float) -> str:
    if volatility_penalty > 0:
        return "regime_volatility_decay"
    if instability_penalty > 0:
        return "feedback_instability_decay"
    if alignment_bonus > 0:
        return "consistent_alignment_bonus"
    return "rolling_blend"


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
