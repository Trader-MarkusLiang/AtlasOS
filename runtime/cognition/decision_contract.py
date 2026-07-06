"""Decision Contract boundary between Atlas cognition and LLM reasoning.

The contract converts deterministic cognition output into a strict prompt
context, then accepts only a validated DecisionPacket back from the LLM layer.
Malformed or unavailable LLM output becomes a neutral failsafe packet.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from runtime.cognition.decision_validator import (
    DecisionPacketValidationError,
    validate_decision_packet,
)


DecisionPacket = Dict[str, Any]


def build_decision_contract_context(
    *,
    cognitive_output: Dict[str, Any],
    market_state: Dict[str, Any],
    regime_state: Dict[str, Any],
    risk_level: str,
    action_bias: str,
    runtime_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the strict context sent to the LLM router."""

    fusion = _as_dict(cognitive_output.get("fusion"))
    causal = _as_dict(cognitive_output.get("causal"))
    controller = _as_dict(cognitive_output.get("controller"))
    unified = _as_dict(cognitive_output.get("unified_intelligence"))
    unified_interpretation = _as_dict(unified.get("unified_interpretation"))
    return {
        "contract_version": "decision_packet_v0.2",
        "market_state": _small_dict(market_state),
        "regime_state": _small_dict(regime_state),
        "risk_level": str(risk_level),
        "action_bias": str(action_bias),
        "cognition": {
            "fusion": _small_dict(
                fusion,
                keys=[
                    "proposed_state",
                    "stress_level",
                    "stress_score",
                    "attention_pressure",
                    "liquidity_condition",
                    "liquidity_score",
                    "narrative_intensity",
                ],
            ),
            "causal": _small_dict(
                causal,
                keys=[
                    "primary_driver",
                    "secondary_driver",
                    "attention_meaning",
                    "market_pressure_source",
                    "regime_transition_probability",
                ],
            ),
            "controller": _small_dict(
                controller,
                keys=["current_state", "proposed_state", "transition_allowed"],
            ),
            "unified": _small_dict(
                unified_interpretation,
                keys=["dominant_regime_structure", "system_market_coupling"],
            ),
        },
        "runtime_context": _small_dict(runtime_context or {}),
        "safety": {
            "trading_execution": "forbidden",
            "portfolio_modification": "forbidden",
            "cde_bypass": "forbidden",
            "prediction_engine": "forbidden",
            "allowed_recommended_action": ["observe", "reduce", "neutral"],
        },
    }


def build_decision_contract_prompt(context: Dict[str, Any]) -> str:
    """Return a prompt that permits only a DecisionPacket JSON object."""

    return "\n".join(
        [
            "You are Atlas OS runtime reasoning boundary.",
            "Return ONLY a valid JSON object. No Markdown. No prose outside JSON.",
            "The JSON object must contain exactly these fields:",
            "regime_state: string",
            "confidence: float between 0.0 and 1.0",
            "risk_level: one of low, medium, high, severe, unknown",
            "attention_state: string",
            "liquidity_state: string",
            "causal_summary: string",
            "recommended_action: one of observe, reduce, neutral",
            "reasoning_trace: string",
            "Do not output trading instructions, broker instructions, target weights, or Buy/Sell language.",
            "Context:",
            json.dumps(context, ensure_ascii=False, sort_keys=True),
        ]
    )


def parse_decision_packet(raw_text: str) -> DecisionPacket:
    """Parse and validate raw LLM text into a DecisionPacket."""

    try:
        parsed = json.loads(_extract_json_object(raw_text))
        return validate_decision_packet(parsed)
    except (json.JSONDecodeError, DecisionPacketValidationError, TypeError, ValueError) as exc:
        return failsafe_decision_packet(f"invalid_llm_output: {exc}")


def deterministic_packet_from_context(context: Dict[str, Any]) -> DecisionPacket:
    """Create a valid local packet when no external reasoning is available."""

    risk = str(context.get("risk_level", "unknown")).lower()
    if risk not in {"low", "medium", "high", "severe", "unknown"}:
        risk = "unknown"
    cognition = _as_dict(context.get("cognition"))
    fusion = _as_dict(cognition.get("fusion"))
    causal = _as_dict(cognition.get("causal"))
    controller = _as_dict(cognition.get("controller"))
    action = "reduce" if risk in {"high", "severe"} else "observe"
    packet = {
        "regime_state": str(
            controller.get("current_state")
            or controller.get("proposed_state")
            or fusion.get("proposed_state")
            or "unknown"
        ),
        "confidence": 0.0 if risk == "unknown" else 0.35,
        "risk_level": risk,
        "attention_state": str(fusion.get("attention_pressure", "unknown")),
        "liquidity_state": str(fusion.get("liquidity_condition") or fusion.get("liquidity_score") or "unknown"),
        "causal_summary": str(causal.get("primary_driver", "Unknown causal driver")),
        "recommended_action": action,
        "reasoning_trace": "Deterministic local packet generated because LLM reasoning was unavailable.",
    }
    return validate_decision_packet(packet)


def failsafe_decision_packet(reason: str = "llm_failure") -> DecisionPacket:
    """Return the required neutral packet when LLM output fails validation."""

    return {
        "regime_state": "unknown",
        "confidence": 0.0,
        "risk_level": "unknown",
        "attention_state": "unknown",
        "liquidity_state": "unknown",
        "causal_summary": "LLM reasoning unavailable or invalid.",
        "recommended_action": "neutral",
        "reasoning_trace": str(reason)[:200],
    }


def _extract_json_object(raw_text: str) -> str:
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found")
    return text[start : end + 1]


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _small_dict(value: Dict[str, Any], keys: Optional[list[str]] = None) -> Dict[str, Any]:
    source = _as_dict(value)
    if keys is None:
        keys = list(source.keys())
    return {key: source.get(key) for key in keys if key in source}
