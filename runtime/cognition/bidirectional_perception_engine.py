"""Bidirectional Perception Engine for Atlas Runtime v1.2.

This module lets prior system state deform incoming event representation before
fusion. It is deterministic, bounded, and interpretable. It is not ML, a
prediction engine, trading execution, CDE override, or portfolio automation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


NO_DEFORM_EVENT_TYPES = {"heartbeat"}


def compute_perception_weight_field(
    *,
    cognition_state: Mapping[str, Any] | None = None,
    regime_memory: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compute bounded perception weights from current Atlas system state."""

    cognition = _mapping(cognition_state)
    memory = _memory_summary(regime_memory)
    if not cognition and not memory:
        return _neutral_weight_field()
    unified = _mapping(cognition.get("unified_intelligence"))
    unified_state = _mapping(unified.get("unified_market_state"))
    unified_interpretation = _mapping(unified.get("unified_interpretation"))
    self_reference = _mapping(unified.get("self_reference"))
    latent = _mapping(cognition.get("latent_structure")).get("latent_variables", {})
    physics = _mapping(cognition.get("physics_constraints")).get("system_stability_report", {})
    laws = _mapping(cognition.get("market_laws")).get("system_stability_evaluation", {})
    event_state = _mapping(unified_state.get("event_state"))

    attention_pressure = _clamp(
        event_state.get("attention_pressure", 0)
        or _mapping(cognition.get("fusion")).get("attention_pressure", 0)
        or _mapping(latent).get("attention_persistence_field", 0)
    )
    system_bias = _clamp(self_reference.get("system_induced_bias_field", 0))
    fragility = _clamp(_mapping(physics).get("regime_fragility_index", 0))
    law_instability = _clamp(_mapping(laws).get("instability_collapse_risk", 0))
    liquidity_pressure = _clamp(_mapping(latent).get("structural_liquidity_pressure", 0))
    memory_risk = 25 if memory.get("dominant_state") in {"CRASH_STRESS", "RISK_OFF", "HIGH_VOLATILITY"} else 0

    attention_bias = _bounded_modifier((attention_pressure - 50) * 0.28 + system_bias * 0.12)
    volatility_modifier = _bounded_modifier(fragility * 0.25 + memory_risk - 10)
    narrative_amplifier = _bounded_modifier(attention_pressure * 0.18 + law_instability * 0.12 - 10)
    liquidity_shift = _bounded_modifier(liquidity_pressure * 0.28 + memory_risk - 12)

    return {
        "attention_bias_map": {
            "attention_spike": attention_bias,
            "news_narrative_spike": _bounded_modifier(attention_bias + narrative_amplifier * 0.5),
            "market_event": _bounded_modifier(attention_bias * 0.35),
        },
        "volatility_sensitivity_modifier": volatility_modifier,
        "narrative_amplification_factor": narrative_amplifier,
        "liquidity_perception_shift": liquidity_shift,
        "source_state": {
            "attention_pressure": attention_pressure,
            "system_induced_bias_field": system_bias,
            "regime_fragility_index": fragility,
            "law_instability": law_instability,
            "memory_dominant_state": memory.get("dominant_state", "NORMAL"),
        },
        "bounded": True,
        "max_priority_adjustment": 25,
        "model_mode": "interpretable_bidirectional_perception_non_ml",
    }


def deform_input_distribution(
    event: Mapping[str, Any],
    perception_weight_field: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a system-weighted event record without changing event identity."""

    event_type = str(event.get("event_type", "market_event"))
    if event_type in NO_DEFORM_EVENT_TYPES:
        return dict(event, perception_adjusted=False)

    base_priority = _clamp(event.get("priority", 50), low=1)
    modifier = _event_modifier(event_type, perception_weight_field)
    adjusted_priority = _clamp(base_priority + modifier, low=1)
    payload = dict(event.get("payload", {})) if isinstance(event.get("payload"), Mapping) else {}
    payload["perception_adjustment"] = {
        "original_priority": base_priority,
        "adjusted_priority": adjusted_priority,
        "priority_delta": adjusted_priority - base_priority,
        "event_type_preserved": True,
        "deformation_reason": _deformation_reason(event_type, modifier),
        "bounded": True,
    }
    payload["perception_weight_field"] = {
        "attention_bias_map": perception_weight_field.get("attention_bias_map", {}),
        "volatility_sensitivity_modifier": perception_weight_field.get("volatility_sensitivity_modifier", 0),
        "narrative_amplification_factor": perception_weight_field.get("narrative_amplification_factor", 0),
        "liquidity_perception_shift": perception_weight_field.get("liquidity_perception_shift", 0),
    }
    _apply_payload_perception_markers(payload, event_type, modifier)

    return {
        **dict(event),
        "payload": payload,
        "priority": adjusted_priority,
        "perception_adjusted": True,
        "perception_priority_delta": adjusted_priority - base_priority,
    }


def perception_feedback_loop(
    *,
    event: Mapping[str, Any],
    cognition_state: Mapping[str, Any] | None = None,
    regime_memory: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Apply System State -> Perception Field -> Input Deformation."""

    field = compute_perception_weight_field(cognition_state=cognition_state, regime_memory=regime_memory)
    deformed = deform_input_distribution(event, field)
    coupling = measure_system_market_coupling(raw_event=event, deformed_event=deformed, perception_weight_field=field)
    return {
        "perception_weight_field": field,
        "deformed_event": deformed,
        "coupling_metrics": coupling,
        "loop_structure": [
            "system_state",
            "perception_weight_field",
            "input_deformation",
            "event_stream_modified_weighting",
            "cognitive_layers",
            "updated_system_state",
        ],
        "feedback_loop_exists": coupling["perception_influence_strength"] > 0,
    }


def attention_influenced_observation(
    *,
    attention_state: int | float,
    base_signal_strength: int | float,
    anomaly_level: int | float = 0,
) -> Dict[str, Any]:
    """Estimate how system attention changes observation sensitivity."""

    attention = _clamp(attention_state)
    signal = _clamp(base_signal_strength)
    anomaly = _clamp(anomaly_level)
    detection = _clamp(signal + max(0, attention - 50) * 0.25 - max(0, 45 - attention) * 0.2)
    granularity = _clamp(40 + attention * 0.45 + anomaly * 0.15)
    anomaly_sensitivity = _clamp(anomaly + attention * 0.25)
    suppression = _clamp(max(0, 45 - attention) * 0.6)
    return {
        "detection_probability": detection,
        "observation_granularity": granularity,
        "anomaly_sensitivity": anomaly_sensitivity,
        "weak_signal_suppression": suppression,
        "attention_shapes_observation": True,
    }


def generate_biased_market_view(
    events: Iterable[Mapping[str, Any]],
    *,
    cognition_state: Mapping[str, Any] | None = None,
    regime_memory: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Generate a system-weighted event stream and perception diagnostics."""

    field = compute_perception_weight_field(cognition_state=cognition_state, regime_memory=regime_memory)
    raw_events = [dict(event) for event in events]
    deformed_events = [deform_input_distribution(event, field) for event in raw_events]
    total_raw = sum(_clamp(event.get("priority", 50), low=1) for event in raw_events)
    total_deformed = sum(_clamp(event.get("priority", 50), low=1) for event in deformed_events)
    return {
        "system_weighted_event_stream": deformed_events,
        "perception_adjusted_regime_signals": {
            "raw_priority_total": total_raw,
            "deformed_priority_total": total_deformed,
            "distribution_delta": total_deformed - total_raw,
        },
        "bias_adjusted_volatility_interpretation": field.get("volatility_sensitivity_modifier", 0),
        "perception_weight_field": field,
        "interpretability_preserved": True,
    }


def measure_system_market_coupling(
    *,
    raw_event: Mapping[str, Any],
    deformed_event: Mapping[str, Any],
    perception_weight_field: Mapping[str, Any],
) -> Dict[str, Any]:
    """Quantify how strongly system state changed the observation layer."""

    raw_priority = _clamp(raw_event.get("priority", 50), low=1)
    deformed_priority = _clamp(deformed_event.get("priority", 50), low=1)
    delta = abs(deformed_priority - raw_priority)
    max_adjustment = max(1, int(perception_weight_field.get("max_priority_adjustment", 25)))
    deformation_ratio = round(delta / max_adjustment, 3)
    influence = _clamp(deformation_ratio * 100)
    return {
        "perception_influence_strength": influence,
        "input_deformation_ratio": deformation_ratio,
        "feedback_loop_intensity": _clamp(influence * 0.7),
        "raw_priority": raw_priority,
        "deformed_priority": deformed_priority,
        "bounded": True,
        "stability_guardrail": "priority_delta_bounded_to_25",
    }


def _event_modifier(event_type: str, field: Mapping[str, Any]) -> int:
    attention_map = field.get("attention_bias_map", {}) if isinstance(field.get("attention_bias_map"), Mapping) else {}
    if event_type in attention_map:
        modifier = attention_map.get(event_type, 0)
    elif event_type in {"volatility_spike", "market_anomaly", "portfolio_drawdown"}:
        modifier = field.get("volatility_sensitivity_modifier", 0)
    elif event_type == "liquidity_shock":
        modifier = field.get("liquidity_perception_shift", 0)
    elif event_type == "volume_price_breakout":
        modifier = (field.get("attention_bias_map", {}).get("market_event", 0) if isinstance(field.get("attention_bias_map"), Mapping) else 0) // 2
    else:
        modifier = 0
    return _bounded_modifier(modifier)


def _neutral_weight_field() -> Dict[str, Any]:
    return {
        "attention_bias_map": {
            "attention_spike": 0,
            "news_narrative_spike": 0,
            "market_event": 0,
        },
        "volatility_sensitivity_modifier": 0,
        "narrative_amplification_factor": 0,
        "liquidity_perception_shift": 0,
        "source_state": {
            "attention_pressure": 0,
            "system_induced_bias_field": 0,
            "regime_fragility_index": 0,
            "law_instability": 0,
            "memory_dominant_state": "NONE",
        },
        "bounded": True,
        "max_priority_adjustment": 25,
        "model_mode": "interpretable_bidirectional_perception_non_ml",
    }


def _deformation_reason(event_type: str, modifier: int) -> str:
    if modifier > 0:
        return f"{event_type} amplified by current system perception state"
    if modifier < 0:
        return f"{event_type} suppressed by current system perception state"
    return f"{event_type} left neutral by current system perception state"


def _apply_payload_perception_markers(payload: Dict[str, Any], event_type: str, modifier: int) -> None:
    """Add bounded markers that existing fusion logic can interpret."""

    if modifier >= 8 and event_type in {"attention_spike", "news_narrative_spike"}:
        if "attention" in payload and "raw_attention" not in payload:
            payload["raw_attention"] = payload["attention"]
        payload["attention"] = "exploding"
        payload["retail_attention"] = "surge"
        payload["perception_marker"] = "attention_amplified"
    elif modifier <= -8 and event_type in {"attention_spike", "news_narrative_spike", "market_event"}:
        payload["evidence_quality"] = "weak"
        payload["perception_marker"] = "weak_signal_suppressed"

    if modifier >= 8 and event_type in {"liquidity_shock", "market_anomaly", "volatility_spike"}:
        payload.setdefault("liquidity", "contracting")
        payload["perception_marker"] = "risk_sensitivity_amplified"


def _memory_summary(regime_memory: Mapping[str, Any] | None) -> Dict[str, Any]:
    memory = _mapping(regime_memory)
    if isinstance(memory.get("summary"), Mapping):
        return dict(memory["summary"])
    return memory


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bounded_modifier(value: Any) -> int:
    return max(-25, min(25, int(float(value or 0))))


def _clamp(value: Any, *, low: int = 0, high: int = 100) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = low
    return max(low, min(high, int(number)))
