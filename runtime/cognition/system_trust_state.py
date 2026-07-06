"""System trust state helpers for Atlas Runtime v0.3.2."""

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.cognition.trust_score_engine import trust_decay_over_time


DEFAULT_SYSTEM_TRUST_STATE = {
    "rolling_trust_index": 0.5,
    "llm_provider_trust": {},
    "regime_trust_decay": 0.5,
    "feedback_stability_index": 0.5,
}


def update_system_trust_state(
    *,
    previous_state: Optional[Dict[str, Any]],
    trust_score: Dict[str, float],
    provider: str,
    feedback_delta: Dict[str, Any],
    regime_volatility: float = 0.0,
) -> Dict[str, Any]:
    """Return updated trust state without mutating cognition."""

    previous = previous_state if isinstance(previous_state, dict) else {}
    base = {**DEFAULT_SYSTEM_TRUST_STATE, **previous}
    decayed = trust_decay_over_time(
        previous_trust_state=base,
        current_trust_score=trust_score,
        feedback_delta=feedback_delta,
        regime_volatility=regime_volatility,
    )
    provider_key = provider or "unknown"
    old_provider_trust = _float(base.get("llm_provider_trust", {}).get(provider_key), 0.5)
    provider_trust = round(old_provider_trust * 0.75 + _float(trust_score.get("llm_trust"), 0.5) * 0.25, 4)
    llm_provider_trust = dict(base.get("llm_provider_trust", {}))
    llm_provider_trust[provider_key] = max(0.0, min(1.0, provider_trust))
    return {
        "rolling_trust_index": decayed["rolling_trust_index"],
        "llm_provider_trust": llm_provider_trust,
        "regime_trust_decay": decayed["regime_trust_decay"],
        "feedback_stability_index": decayed["feedback_stability_index"],
        "latest_trust_score": trust_score,
        "trust_direction": decayed["trust_direction"],
        "trust_adjustment_reason": decayed["trust_adjustment_reason"],
    }


def trust_state_summary(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    source = state if isinstance(state, dict) else DEFAULT_SYSTEM_TRUST_STATE
    return {
        "rolling_trust_index": source.get("rolling_trust_index", 0.5),
        "llm_provider_trust": source.get("llm_provider_trust", {}),
        "regime_trust_decay": source.get("regime_trust_decay", 0.5),
        "feedback_stability_index": source.get("feedback_stability_index", 0.5),
    }


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
