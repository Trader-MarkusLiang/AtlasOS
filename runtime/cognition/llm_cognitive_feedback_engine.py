"""LLM cognitive feedback engine for Atlas runtime v0.3.

The engine lets validated DecisionPackets influence future cognition through
bounded weight and sensitivity adjustments only. It never overrides regime
labels, executes trades, trains models, or bypasses the Decision Contract.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Dict, Optional


MAX_SIGNAL = 0.08
MAX_APPLIED_DELTA = 6
OSCILLATION_THRESHOLD = 0.06
AMPLIFICATION_THRESHOLD = 0.12
INSTABILITY_THRESHOLD = 0.16
_RANDOM = random.Random()


def extract_llm_cognitive_signals(
    *,
    decision_packet: Dict[str, Any],
    cognitive_state_snapshot: Dict[str, Any],
    llm_reasoning_output: str,
) -> Dict[str, Any]:
    """Extract bounded cognitive feedback signals from validated LLM output."""

    packet = decision_packet if isinstance(decision_packet, dict) else {}
    cognition = cognitive_state_snapshot if isinstance(cognitive_state_snapshot, dict) else {}
    fusion = _as_dict(cognition.get("fusion"))
    causal = _as_dict(cognition.get("causal"))
    text = " ".join(
        [
            str(packet.get("causal_summary", "")),
            str(packet.get("reasoning_trace", "")),
            str(llm_reasoning_output or ""),
        ]
    ).lower()
    confidence = _float(packet.get("confidence"), 0.0)
    risk = str(packet.get("risk_level", "unknown")).lower()
    action = str(packet.get("recommended_action", "neutral")).lower()
    jitter = _RANDOM.uniform(-0.012, 0.012)

    attention_base = 0.0
    if "attention" in text or "narrative" in text:
        attention_base += 0.03
    if risk in {"high", "severe"}:
        attention_base += 0.02
    if action == "neutral":
        attention_base -= 0.01

    risk_base = 0.0
    if risk == "severe":
        risk_base += 0.07
    elif risk == "high":
        risk_base += 0.05
    elif risk == "medium":
        risk_base += 0.025
    elif risk == "low":
        risk_base -= 0.02

    causal_base = 0.0
    primary_driver = str(causal.get("primary_driver", "")).lower()
    if "liquidity" in text or "liquidity" in primary_driver:
        causal_base += 0.035
    if "divergence" in text or "divergence" in primary_driver:
        causal_base += 0.025
    if confidence < 0.15:
        causal_base -= 0.015

    liquidity_base = 0.0
    liquidity_condition = str(fusion.get("liquidity_condition", "")).lower()
    if "tight" in liquidity_condition or "shock" in liquidity_condition:
        liquidity_base -= 0.04
    if "liquidity" in text and risk in {"high", "severe"}:
        liquidity_base -= 0.025

    return {
        "regime_reinterpretation_signal": _clamp_signal(risk_base + jitter),
        "attention_adjustment_signal": _clamp_signal(attention_base + jitter),
        "risk_recalibration_signal": _clamp_signal(risk_base + (confidence - 0.5) * 0.04),
        "causal_weight_shift_signal": _clamp_signal(causal_base + jitter),
        "liquidity_bias_signal": _clamp_signal(liquidity_base - jitter),
        "source": "validated_decision_packet",
        "direct_regime_override": False,
    }


def apply_llm_feedback_to_cognition(
    *,
    cognitive_state_snapshot: Dict[str, Any],
    llm_signals: Dict[str, Any],
    previous_feedback: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply feedback as bounded cognition modifiers without relabeling state."""

    snapshot = copy.deepcopy(cognitive_state_snapshot if isinstance(cognitive_state_snapshot, dict) else {})
    signals = llm_signals if isinstance(llm_signals, dict) else {}
    modifiers = {
        "attention_weight_delta": _clamp_signal(signals.get("attention_adjustment_signal")),
        "causal_edge_strength_delta": _clamp_signal(signals.get("causal_weight_shift_signal")),
        "risk_confidence_delta": _clamp_signal(signals.get("risk_recalibration_signal")),
        "liquidity_interpretation_bias_delta": _clamp_signal(signals.get("liquidity_bias_signal")),
        "regime_probability_distribution_delta": {
            "distribution_risk": _clamp_signal(signals.get("regime_reinterpretation_signal")),
            "data_insufficient": -abs(_clamp_signal(signals.get("risk_recalibration_signal"))) / 2,
        },
    }
    snapshot["llm_feedback_modifiers"] = modifiers
    snapshot["llm_feedback_policy"] = {
        "max_refinements_per_tick": 1,
        "bounded_update": True,
        "regime_label_override_allowed": False,
        "previous_freeze_remaining": int(_as_dict(previous_feedback).get("freeze_remaining", 0)),
    }
    return snapshot


def run_cognitive_refinement_cycle(
    *,
    decision_packet: Dict[str, Any],
    cognitive_state_snapshot: Dict[str, Any],
    llm_reasoning_output: str = "",
    previous_feedback: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run one bounded LLM feedback refinement cycle."""

    stability = check_feedback_stability(previous_feedback=previous_feedback, current_signals={})
    if stability["freeze_feedback"]:
        return {
            "status": "frozen",
            "llm_signals": {},
            "adjusted_cognition": cognitive_state_snapshot,
            "modifiers": {},
            "stability": stability,
            "freeze_remaining": 0,
            "refinement_count": 0,
        }

    signals = extract_llm_cognitive_signals(
        decision_packet=decision_packet,
        cognitive_state_snapshot=cognitive_state_snapshot,
        llm_reasoning_output=llm_reasoning_output,
    )
    stability = check_feedback_stability(previous_feedback=previous_feedback, current_signals=signals)
    if stability["freeze_feedback"]:
        return {
            "status": "frozen",
            "llm_signals": signals,
            "adjusted_cognition": cognitive_state_snapshot,
            "modifiers": {},
            "stability": stability,
            "freeze_remaining": 1,
            "refinement_count": 0,
        }

    adjusted = apply_llm_feedback_to_cognition(
        cognitive_state_snapshot=cognitive_state_snapshot,
        llm_signals=signals,
        previous_feedback=previous_feedback,
    )
    return {
        "status": "applied",
        "llm_signals": signals,
        "adjusted_cognition": adjusted,
        "modifiers": adjusted.get("llm_feedback_modifiers", {}),
        "stability": stability,
        "freeze_remaining": 0,
        "refinement_count": 1,
    }


def check_feedback_stability(
    *,
    previous_feedback: Optional[Dict[str, Any]],
    current_signals: Dict[str, Any],
) -> Dict[str, Any]:
    """Detect oscillation or runaway feedback and request one-tick freeze."""

    previous = _as_dict(previous_feedback)
    if int(previous.get("freeze_remaining", 0)) > 0:
        return {
            "freeze_feedback": True,
            "reason": "cooldown_active",
            "amplification": 0.0,
            "oscillation_detected": False,
            "regime_instability_delta": 0.0,
        }

    signals = _numeric_signals(current_signals)
    amplification = max((abs(value) for value in signals.values()), default=0.0)
    previous_signals = _numeric_signals(_as_dict(previous.get("llm_signals")))
    oscillation = False
    for key, value in signals.items():
        old = previous_signals.get(key, 0.0)
        if abs(value) >= OSCILLATION_THRESHOLD and abs(old) >= OSCILLATION_THRESHOLD and (value * old) < 0:
            oscillation = True
            break

    instability = abs(signals.get("regime_reinterpretation_signal", 0.0)) + abs(
        signals.get("risk_recalibration_signal", 0.0)
    )
    freeze = oscillation or amplification > AMPLIFICATION_THRESHOLD or instability > INSTABILITY_THRESHOLD
    reason = "stable"
    if oscillation:
        reason = "oscillation_detected"
    elif amplification > AMPLIFICATION_THRESHOLD:
        reason = "feedback_amplification_exceeded"
    elif instability > INSTABILITY_THRESHOLD:
        reason = "regime_instability_increased"

    return {
        "freeze_feedback": freeze,
        "reason": reason,
        "amplification": round(amplification, 4),
        "oscillation_detected": oscillation,
        "regime_instability_delta": round(instability, 4),
    }


def apply_pending_feedback_to_fusion(
    fusion: Dict[str, Any],
    previous_feedback: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Project previous LLM feedback onto post-fusion numeric fields."""

    adjusted = copy.deepcopy(fusion if isinstance(fusion, dict) else {})
    previous = _as_dict(previous_feedback)
    if previous.get("status") != "applied":
        return adjusted
    modifiers = _as_dict(previous.get("modifiers"))
    if not modifiers:
        return adjusted

    attention_delta = int(round(_float(modifiers.get("attention_weight_delta"), 0.0) * 100))
    liquidity_delta = int(round(_float(modifiers.get("liquidity_interpretation_bias_delta"), 0.0) * 100))
    risk_delta = int(round(_float(modifiers.get("risk_confidence_delta"), 0.0) * 100))
    adjusted["attention_pressure"] = _clamp_score(
        int(adjusted.get("attention_pressure", 0)) + _clamp_int(attention_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA)
    )
    adjusted["liquidity_score"] = _clamp_score(
        int(adjusted.get("liquidity_score", 50)) + _clamp_int(liquidity_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA)
    )
    adjusted["stability_score"] = _clamp_score(
        int(adjusted.get("stability_score", 40)) - abs(_clamp_int(risk_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA))
    )
    adjusted["llm_feedback_projection"] = {
        "source": "previous_tick_feedback",
        "attention_delta": _clamp_int(attention_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA),
        "liquidity_delta": _clamp_int(liquidity_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA),
        "risk_delta": _clamp_int(risk_delta, -MAX_APPLIED_DELTA, MAX_APPLIED_DELTA),
        "regime_label_changed": False,
    }
    return adjusted


def attach_trust_weighting(
    feedback_state: Dict[str, Any],
    trust_score: Dict[str, Any],
) -> Dict[str, Any]:
    """Attach trust metadata without changing feedback computation."""

    annotated = copy.deepcopy(feedback_state if isinstance(feedback_state, dict) else {})
    annotated["trust_weighting"] = {
        "global_trust_index": _float(trust_score.get("global_trust_index"), 0.5),
        "feedback_consistency_trust": _float(trust_score.get("feedback_consistency_trust"), 0.5),
        "metadata_only": True,
        "feedback_delta_modified": False,
    }
    return annotated


def _numeric_signals(signals: Dict[str, Any]) -> Dict[str, float]:
    return {
        key: _float(value, 0.0)
        for key, value in signals.items()
        if key.endswith("_signal") and isinstance(value, (int, float))
    }


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_signal(value: Any) -> float:
    return round(max(-MAX_SIGNAL, min(MAX_SIGNAL, _float(value, 0.0))), 4)


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))
