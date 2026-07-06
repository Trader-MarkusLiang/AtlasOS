"""Regime explanation alignment checks for Atlas Runtime v0.6."""

from __future__ import annotations

from typing import Any, Dict, Mapping


REGIME_HINTS = {
    "RISK_OFF": ("risk", "stress", "volatility", "liquidity", "crash"),
    "HIGH_VOLATILITY": ("volatility", "stress", "risk"),
    "ATTENTION_EXPANSION": ("attention", "narrative", "retail"),
    "DISTRIBUTION": ("liquidity", "institutional", "rotation"),
    "BREAKOUT": ("momentum", "attention", "flow"),
    "NORMAL": ("stable", "neutral", "observe"),
}


def align_regime_explanation(
    *,
    regime_label: str,
    decision_explanation: Mapping[str, Any] | str,
    causal_model: Mapping[str, Any],
    actual_outcome_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Score consistency among regime label, explanation, and causal model."""

    label = str(regime_label or "UNKNOWN").upper()
    text = _explanation_text(decision_explanation)
    causal_text = " ".join(
        str(causal_model.get(key, ""))
        for key in ("primary_driver", "secondary_driver", "market_pressure_source")
    ).lower()
    outcome_text = str(_as_mapping(actual_outcome_state).get("state", "")).lower()
    hints = REGIME_HINTS.get(label, ())
    explanation_match = any(hint in text for hint in hints) if hints else False
    causal_match = any(hint in causal_text for hint in hints) if hints else False
    outcome_match = label.lower() in outcome_text or not outcome_text

    conflicts = []
    if hints and not explanation_match:
        conflicts.append("regime_not_explained")
    if hints and not causal_match:
        conflicts.append("causal_driver_not_aligned")
    if not outcome_match:
        conflicts.append("outcome_state_mismatch")

    score = 1.0 - min(0.8, len(conflicts) * 0.25)
    if explanation_match and causal_match:
        score = min(1.0, score + 0.1)
    return {
        "alignment_score": round(max(0.0, min(1.0, score)), 4),
        "regime_label": label,
        "explanation_match": explanation_match,
        "causal_match": causal_match,
        "outcome_match": outcome_match,
        "alignment_conflicts": conflicts,
        "label_override": False,
        "metadata_only": True,
    }


def _explanation_text(value: Mapping[str, Any] | str) -> str:
    if isinstance(value, Mapping):
        return " ".join(
            str(value.get(key, ""))
            for key in ("causal_summary", "reasoning_trace", "risk_level", "attention_state", "liquidity_state")
        ).lower()
    return str(value or "").lower()


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

