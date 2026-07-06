"""Causal Intelligence Layer for Atlas Runtime v0.5.

This module is symbolic causal reasoning, not statistical regression, ML, or a
trading model. It explains how market forces interact before state control.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


CAUSAL_GRAPH: Dict[str, Any] = {
    "nodes": [
        "Attention",
        "Liquidity",
        "Price Momentum",
        "Volatility",
        "Narrative Pressure",
        "Institutional Flow",
        "Retail Flow",
    ],
    "edges": [
        {"from": "Narrative Pressure", "to": "Attention", "relationship": "amplifies"},
        {"from": "Attention", "to": "Retail Flow", "relationship": "raises participation probability"},
        {"from": "Institutional Flow", "to": "Liquidity", "relationship": "adds or withdraws depth"},
        {"from": "Liquidity", "to": "Volatility", "relationship": "buffers or amplifies"},
        {"from": "Retail Flow", "to": "Price Momentum", "relationship": "can accelerate"},
        {"from": "Price Momentum", "to": "Attention", "relationship": "feedback loop"},
    ],
}


def market_causal_graph() -> Dict[str, Any]:
    """Return the symbolic causal graph definition."""

    return CAUSAL_GRAPH


def resolve_attention_meaning(
    *,
    attention_spike: int | float = 0,
    narrative_intensity: int | float = 0,
    price_movement: int | float = 0,
    volume_anomaly: int | float = 0,
    liquidity_score: int | float = 50,
    stress_score: int | float = 0,
) -> str:
    """Classify what attention means in context.

    Attention is treated as a causal symptom, not a direct signal.
    """

    attention = _clamp(attention_spike)
    narrative = _clamp(narrative_intensity)
    price = float(price_movement)
    volume = _clamp(volume_anomaly)
    liquidity = _clamp(liquidity_score)
    stress = _clamp(stress_score)

    if attention >= 55 and liquidity <= 35 and (stress >= 55 or price < 0):
        return "panic-driven attention"
    if attention >= 55 and liquidity >= 65 and volume >= 45 and price >= 0:
        return "liquidity-driven attention"
    if attention >= 55 and narrative >= 55 and liquidity < 60:
        return "retail narrative attention"
    if attention >= 35 and volume >= 55 and narrative < 45 and liquidity >= 45:
        return "institutional repositioning attention"
    if attention >= 55:
        return "retail narrative attention"
    return "attention not dominant"


def compute_flow_propagation(
    *,
    attention_score: int | float,
    liquidity_score: int | float,
    narrative_intensity: int | float,
    volume_anomaly: int | float = 0,
    stress_score: int | float = 0,
) -> Dict[str, Any]:
    """Model symbolic propagation from attention into flow and volatility."""

    attention = _clamp(attention_score)
    liquidity = _clamp(liquidity_score)
    narrative = _clamp(narrative_intensity)
    volume = _clamp(volume_anomaly)
    stress = _clamp(stress_score)

    retail_flow = _clamp((attention * 0.45) + (narrative * 0.35) + max(0, liquidity - 45) * 0.2)
    institutional_flow = _clamp((liquidity * 0.45) + (volume * 0.35) - (narrative * 0.15) - max(0, stress - 50) * 0.2)
    conversion = _clamp((retail_flow * 0.45) + (institutional_flow * 0.45) + (liquidity * 0.1))
    volatility_expansion = _clamp((stress * 0.55) + (attention * 0.25) + max(0, 50 - liquidity) * 0.35)

    if liquidity >= 65 and volume >= 50:
        latency = "Short"
    elif liquidity <= 35 or stress >= 65:
        latency = "Unstable / delayed"
    else:
        latency = "Medium"

    return {
        "retail_flow_strength": retail_flow,
        "institutional_flow_strength": institutional_flow,
        "latency_attention_to_flow": latency,
        "conversion_efficiency_attention_to_capital": conversion,
        "volatility_expansion_pressure": volatility_expansion,
    }


def infer_regime_emergence(
    *,
    fusion: Mapping[str, Any],
    attention_meaning: str,
    flow_propagation: Mapping[str, Any],
    memory_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Infer how regime formation is emerging instead of labeling it directly."""

    stress = int(fusion.get("stress_score", 0))
    attention = int(fusion.get("attention_pressure", 0))
    liquidity = int(fusion.get("liquidity_score", 50))
    narrative = int(fusion.get("narrative_intensity", 0))
    volatility = _level_to_score(str(fusion.get("volatility_regime", "Low")))
    retail = int(flow_propagation.get("retail_flow_strength", 0))
    institutional = int(flow_propagation.get("institutional_flow_strength", 0))

    drivers: List[str] = []
    if liquidity <= 35:
        drivers.append("Liquidity contraction")
    if attention >= 65:
        drivers.append("Attention pressure")
    if narrative >= 60:
        drivers.append("Narrative pressure")
    if volatility >= 65 or stress >= 65:
        drivers.append("Volatility / stress feedback")
    if institutional >= 60:
        drivers.append("Institutional flow support")
    if not drivers:
        drivers.append("Low-signal mixed forces")

    tension = {
        "attention_vs_liquidity": _tension(attention, liquidity),
        "retail_vs_institutional_flow": _tension(retail, institutional),
        "narrative_vs_liquidity": _tension(narrative, liquidity),
        "stress_vs_memory": {
            "current_stress": stress,
            "memory_dominant_state": memory_summary.get("dominant_state", "NORMAL"),
        },
    }
    formation_probability = _clamp(
        max(stress, attention, narrative, volatility, abs(retail - institutional), 100 - liquidity)
    )

    process = _formation_process(attention_meaning, liquidity, stress, retail, institutional)
    return {
        "formation_process": process,
        "dominant_causal_drivers": drivers,
        "structural_tension_map": tension,
        "regime_formation_probability": formation_probability,
        "not_final_label": True,
    }


def counterfactual_test(
    *,
    remove_node: str,
    fusion: Mapping[str, Any],
    flow_propagation: Mapping[str, Any],
) -> Dict[str, Any]:
    """Run lightweight symbolic node removal."""

    node = remove_node.strip().lower()
    baseline = dict(flow_propagation)
    adjusted = dict(flow_propagation)
    explanation = "No material causal node removed."

    if node == "attention":
        adjusted["retail_flow_strength"] = _clamp(int(baseline.get("retail_flow_strength", 0)) * 0.45)
        adjusted["conversion_efficiency_attention_to_capital"] = _clamp(
            int(baseline.get("conversion_efficiency_attention_to_capital", 0)) * 0.65
        )
        explanation = "Removing attention lowers retail flow and attention-to-capital conversion."
    elif node == "liquidity":
        adjusted["institutional_flow_strength"] = _clamp(int(baseline.get("institutional_flow_strength", 0)) * 0.5)
        adjusted["volatility_expansion_pressure"] = _clamp(
            max(int(baseline.get("volatility_expansion_pressure", 0)), int(fusion.get("stress_score", 0)))
        )
        explanation = "Removing liquidity support weakens institutional flow and keeps volatility pressure high."
    elif node == "narrative":
        adjusted["retail_flow_strength"] = _clamp(int(baseline.get("retail_flow_strength", 0)) * 0.7)
        explanation = "Removing narrative pressure reduces retail flow but may not fix liquidity stress."

    return {
        "removed_node": remove_node,
        "baseline": baseline,
        "adjusted": adjusted,
        "effect": explanation,
    }


def infer_causal_intelligence(
    fusion: Dict[str, Any],
    attention_liquidity: Dict[str, Any],
    memory_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """Return CIL output plus compatibility fields used by the state controller."""

    attention = int(attention_liquidity.get("attention_index", fusion.get("attention_pressure", 0)))
    liquidity = int(attention_liquidity.get("liquidity_index", fusion.get("liquidity_score", 50)))
    narrative = int(fusion.get("narrative_intensity", 0))
    stress = int(fusion.get("stress_score", 0))
    volume = _level_to_score(str(fusion.get("volatility_regime", "Low")))
    price_movement = _infer_price_movement(fusion)

    attention_meaning = resolve_attention_meaning(
        attention_spike=attention,
        narrative_intensity=narrative,
        price_movement=price_movement,
        volume_anomaly=volume,
        liquidity_score=liquidity,
        stress_score=stress,
    )
    flow = compute_flow_propagation(
        attention_score=attention,
        liquidity_score=liquidity,
        narrative_intensity=narrative,
        volume_anomaly=volume,
        stress_score=stress,
    )
    emergence = infer_regime_emergence(
        fusion=fusion,
        attention_meaning=attention_meaning,
        flow_propagation=flow,
        memory_summary=memory_summary,
    )
    counterfactuals = {
        "remove_attention": counterfactual_test(remove_node="Attention", fusion=fusion, flow_propagation=flow),
        "remove_liquidity": counterfactual_test(remove_node="Liquidity", fusion=fusion, flow_propagation=flow),
    }

    primary, secondary, pressure = _compatibility_drivers(attention_meaning, fusion, flow)
    transition_probability = int(emergence["regime_formation_probability"])
    return {
        "primary_driver": primary,
        "secondary_driver": secondary,
        "market_pressure_source": pressure,
        "attention_flow_probability": int(flow["retail_flow_strength"]),
        "liquidity_volatility_coupling": int(flow["volatility_expansion_pressure"]),
        "narrative_retail_flow_likelihood": _clamp((attention + narrative) // 2),
        "regime_transition_probability": transition_probability,
        "memory_dominant_state": memory_summary.get("dominant_state", "NORMAL"),
        "causal_graph": market_causal_graph(),
        "attention_meaning": attention_meaning,
        "flow_propagation": flow,
        "regime_emergence": emergence,
        "counterfactuals": counterfactuals,
        "reasoning_mode": "symbolic_causal_non_ml",
    }


def _compatibility_drivers(
    attention_meaning: str,
    fusion: Mapping[str, Any],
    flow: Mapping[str, Any],
) -> tuple[str, str, str]:
    stress = int(fusion.get("stress_score", 0))
    liquidity = int(fusion.get("liquidity_score", 50))
    if stress >= 80 and liquidity <= 35:
        return "Liquidity Stress", "Volatility Shock", "Liquidity -> Volatility"
    if attention_meaning == "panic-driven attention":
        return "Liquidity Stress", "Panic Attention", "Liquidity stress -> Attention symptom"
    if attention_meaning == "liquidity-driven attention":
        return "Liquidity-Supported Attention", "Flow Confirmation", "Liquidity -> Flow -> Attention"
    if attention_meaning == "institutional repositioning attention":
        return "Institutional Repositioning", "Volume / Flow Shift", "Institutional flow -> Price / Attention"
    if attention_meaning == "retail narrative attention":
        return "Attention-Liquidity Divergence", "Narrative Crowding", "Narrative -> Retail Flow"
    if int(flow.get("volatility_expansion_pressure", 0)) >= 60:
        return "Market Stress", "Volatility", "Risk Repricing"
    return "Mixed / Low Signal", "NORMAL", "Data Insufficient"


def _formation_process(
    attention_meaning: str,
    liquidity: int,
    stress: int,
    retail: int,
    institutional: int,
) -> str:
    if liquidity <= 35 and stress >= 65:
        return "Liquidity withdrawal is amplifying volatility while attention reacts as a symptom."
    if attention_meaning == "liquidity-driven attention":
        return "Liquidity support is converting attention into flow with shorter latency."
    if attention_meaning == "retail narrative attention":
        return "Narrative pressure is lifting retail participation without enough institutional confirmation."
    if retail > institutional + 25:
        return "Retail flow dominates institutional flow, creating fragile participation structure."
    if institutional > retail + 20:
        return "Institutional flow is absorbing attention and stabilizing regime formation."
    return "Multiple weak forces are interacting without one dominant formation path."


def _tension(left: int, right: int) -> Dict[str, Any]:
    gap = left - right
    if abs(gap) >= 45:
        level = "Severe"
    elif abs(gap) >= 25:
        level = "High"
    elif abs(gap) >= 10:
        level = "Medium"
    else:
        level = "Low"
    return {"left": left, "right": right, "gap": gap, "level": level}


def _infer_price_movement(fusion: Mapping[str, Any]) -> int:
    proposed = str(fusion.get("proposed_state", "NORMAL"))
    stress = int(fusion.get("stress_score", 0))
    if proposed in {"CRASH_STRESS", "RISK_OFF"} or stress >= 75:
        return -1
    if proposed in {"BREAKOUT", "ATTENTION_EXPANSION"}:
        return 1
    return 0


def _level_to_score(value: str) -> int:
    levels = {"low": 20, "medium": 45, "high": 70, "severe": 90}
    return levels.get(value.lower(), 20)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(value)))

