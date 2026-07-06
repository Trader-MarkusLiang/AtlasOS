"""Strict DecisionPacket validation for Atlas runtime.

This module validates the LLM boundary only. It does not classify regimes,
create predictions, execute trades, or change CDE authority.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict


DECISION_PACKET_FIELDS = {
    "regime_state",
    "confidence",
    "risk_level",
    "attention_state",
    "liquidity_state",
    "causal_summary",
    "recommended_action",
    "reasoning_trace",
}

TEXT_FIELDS = {
    "regime_state",
    "risk_level",
    "attention_state",
    "liquidity_state",
    "causal_summary",
    "recommended_action",
    "reasoning_trace",
}

ALLOWED_RECOMMENDED_ACTIONS = {"observe", "reduce", "neutral"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high", "severe", "unknown"}
MAX_TEXT_LENGTH = 700
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_BLOCKED_DIRECTIVES = re.compile(
    r"\b(buy|sell|long|short|target_weight|target weight|broker|execute trade|place order)\b",
    re.IGNORECASE,
)


class DecisionPacketValidationError(ValueError):
    """Raised when a DecisionPacket violates the runtime contract."""


def validate_decision_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Return a sanitized DecisionPacket or raise validation error."""

    if not isinstance(packet, dict):
        raise DecisionPacketValidationError("DecisionPacket must be a dict")

    fields = set(packet)
    missing = DECISION_PACKET_FIELDS - fields
    extra = fields - DECISION_PACKET_FIELDS
    if missing:
        raise DecisionPacketValidationError(f"DecisionPacket missing fields: {sorted(missing)}")
    if extra:
        raise DecisionPacketValidationError(f"DecisionPacket has unsupported fields: {sorted(extra)}")

    confidence = packet["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise DecisionPacketValidationError("confidence must be a float")
    confidence_value = float(confidence)
    if not math.isfinite(confidence_value) or confidence_value < 0.0 or confidence_value > 1.0:
        raise DecisionPacketValidationError("confidence must be between 0.0 and 1.0")

    sanitized: Dict[str, Any] = {"confidence": confidence_value}
    for field in TEXT_FIELDS:
        value = packet[field]
        if not isinstance(value, str):
            raise DecisionPacketValidationError(f"{field} must be a string")
        sanitized[field] = sanitize_text(value)

    risk_level = sanitized["risk_level"].lower()
    if risk_level not in ALLOWED_RISK_LEVELS:
        raise DecisionPacketValidationError("risk_level is out of bounds")
    sanitized["risk_level"] = risk_level

    recommended_action = sanitized["recommended_action"].lower()
    if recommended_action not in ALLOWED_RECOMMENDED_ACTIONS:
        raise DecisionPacketValidationError("recommended_action is out of bounds")
    sanitized["recommended_action"] = recommended_action

    for field in ("causal_summary", "reasoning_trace"):
        if _BLOCKED_DIRECTIVES.search(sanitized[field]):
            raise DecisionPacketValidationError(f"{field} contains trading directive language")

    return {
        "regime_state": sanitized["regime_state"],
        "confidence": sanitized["confidence"],
        "risk_level": sanitized["risk_level"],
        "attention_state": sanitized["attention_state"],
        "liquidity_state": sanitized["liquidity_state"],
        "causal_summary": sanitized["causal_summary"],
        "recommended_action": sanitized["recommended_action"],
        "reasoning_trace": sanitized["reasoning_trace"],
    }


def sanitize_text(value: str) -> str:
    """Strip control characters and bound text length."""

    cleaned = _CONTROL_CHARS.sub(" ", value).strip()
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > MAX_TEXT_LENGTH:
        cleaned = cleaned[:MAX_TEXT_LENGTH].rstrip()
    return cleaned
