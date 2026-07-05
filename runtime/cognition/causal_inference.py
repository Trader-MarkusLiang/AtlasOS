"""Causal market inference layer for Atlas Runtime v0.3."""

from __future__ import annotations

from typing import Any, Dict


def infer_causal_state(
    fusion: Dict[str, Any],
    attention_liquidity: Dict[str, Any],
    memory_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """Infer why the market regime is changing."""

    stress = int(fusion.get("stress_score", 0))
    attention = int(attention_liquidity.get("attention_index", 0))
    liquidity = int(attention_liquidity.get("liquidity_index", 50))
    narrative = int(fusion.get("narrative_intensity", 0))
    divergence = int(attention_liquidity.get("divergence_score", 0))

    liquidity_volatility_coupling = _clamp(stress + max(0, 50 - liquidity))
    attention_flow_probability = _clamp(attention_liquidity.get("flow_probability", 30))
    retail_flow_likelihood = _clamp((attention + narrative) // 2)

    if stress >= 80 and liquidity <= 35:
        primary = "Liquidity Stress"
        secondary = "Volatility Shock"
        pressure = "Liquidity -> Volatility"
    elif divergence >= 55 and attention >= 70:
        primary = "Attention-Liquidity Divergence"
        secondary = "Narrative Crowding"
        pressure = "Attention without confirmed flow"
    elif attention >= 70:
        primary = "Attention Momentum"
        secondary = "Retail Flow"
        pressure = "Narrative -> Retail Flow"
    elif stress >= 60:
        primary = "Market Stress"
        secondary = "Volatility"
        pressure = "Risk Repricing"
    else:
        primary = "Mixed / Low Signal"
        secondary = memory_summary.get("dominant_state", "NORMAL")
        pressure = "Data Insufficient"

    transition_probability = _clamp(
        max(stress, attention, liquidity_volatility_coupling, retail_flow_likelihood)
    )

    return {
        "primary_driver": primary,
        "secondary_driver": secondary,
        "market_pressure_source": pressure,
        "attention_flow_probability": attention_flow_probability,
        "liquidity_volatility_coupling": liquidity_volatility_coupling,
        "narrative_retail_flow_likelihood": retail_flow_likelihood,
        "regime_transition_probability": transition_probability,
        "memory_dominant_state": memory_summary.get("dominant_state", "NORMAL"),
    }


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(value)))
