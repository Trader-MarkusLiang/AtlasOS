"""Attention vs liquidity separation model for Atlas Runtime v0.3."""

from __future__ import annotations

from typing import Any, Dict, Iterable


def compute_attention_liquidity(events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Separate hype-driven attention from liquidity / flow support."""

    attention = 0
    liquidity_support = 50
    evidence_quality = 50
    flow_probability = 30
    drivers: list[str] = []

    for event in events:
        event_type = event.get("event_type")
        payload = event.get("payload", {})

        if event_type == "attention_spike":
            attention += 60
            drivers.append(event_type)
        if event_type == "news_narrative_spike":
            attention += 45
            drivers.append(event_type)
        if event_type == "volume_price_breakout":
            attention += 20
            flow_probability += 20
            if _payload_matches(payload, {"volume": ["inconsistent", "weak", "low"]}):
                liquidity_support -= 20
                evidence_quality -= 15
            else:
                liquidity_support += 15
        if event_type in {"market_anomaly", "volatility_spike", "liquidity_shock", "portfolio_drawdown"}:
            attention += 15
            liquidity_support -= 30
            flow_probability -= 10
        if _payload_matches(payload, {"liquidity": ["contracting", "shock", "dry"]}):
            liquidity_support -= 35
        if _payload_matches(payload, {"retail_attention": ["dominant", "surge"], "attention": ["exploding"]}):
            attention += 25
        if _payload_matches(payload, {"evidence_quality": ["unclear", "weak", "limited"]}):
            evidence_quality -= 20

    attention_index = _clamp(attention)
    liquidity_index = _clamp(liquidity_support)
    divergence_score = _clamp(abs(attention_index - liquidity_index))

    if attention_index >= 70 and liquidity_index < 45:
        interpretation = "Attention high / liquidity weak"
    elif attention_index >= 70 and liquidity_index >= 60:
        interpretation = "Attention supported by liquidity"
    elif liquidity_index < 35:
        interpretation = "Liquidity stress dominates"
    else:
        interpretation = "Balanced or low-signal"

    return {
        "attention_index": attention_index,
        "liquidity_index": liquidity_index,
        "divergence_score": divergence_score,
        "flow_probability": _clamp(flow_probability),
        "evidence_quality": _clamp(evidence_quality),
        "interpretation": interpretation,
        "drivers": drivers,
    }


def _payload_matches(payload: Dict[str, Any], patterns: Dict[str, list[str]]) -> bool:
    for key, needles in patterns.items():
        value = str(payload.get(key, "")).lower()
        if any(needle in value for needle in needles):
            return True
    return False


def _clamp(value: int) -> int:
    return max(0, min(100, value))
