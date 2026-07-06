"""Hypothesis memory helpers for Atlas Runtime v0.7."""

from __future__ import annotations

from typing import Any, Dict, Mapping


MAX_HISTORY = 30


def update_hypothesis_memory(
    *,
    previous_memory: Mapping[str, Any] | None,
    selection_state: Mapping[str, Any],
    scored_hypotheses: Mapping[str, Any],
    regime_state: str,
    explanation_error: Mapping[str, Any],
) -> Dict[str, Any]:
    """Append one hypothesis selection record."""

    previous = previous_memory if isinstance(previous_memory, Mapping) else {}
    history = list(previous.get("history", [])) if isinstance(previous.get("history"), list) else []
    active = selection_state.get("active_hypothesis_id")
    ranking = scored_hypotheses.get("hypothesis_ranking", [])
    ranking = ranking if isinstance(ranking, list) else []
    rejected = selection_state.get("rejected_hypothesis_ids", [])
    record = {
        "selected_hypothesis_id": active,
        "rejected_hypothesis_ids": list(rejected) if isinstance(rejected, list) else [],
        "why_selected": selection_state.get("selection_reason", "unknown"),
        "why_rejected": {
            item.get("id"): _rejection_reason(item, active)
            for item in ranking
            if item.get("id") != active
        },
        "regime_context": regime_state,
        "explanation_error_score": explanation_error.get("explanation_error_score"),
        "score_distribution": scored_hypotheses.get("score_distribution", {}),
    }
    history.append(record)
    return {
        "active_hypothesis_id": active,
        "last_selection_reason": selection_state.get("selection_reason"),
        "history": history[-MAX_HISTORY:],
        "selection_count": int(previous.get("selection_count", 0)) + 1,
        "shadow_state_retained": True,
        "metadata_only": True,
    }


def summarize_hypothesis_memory(memory_state: Mapping[str, Any] | None) -> Dict[str, Any]:
    memory = memory_state if isinstance(memory_state, Mapping) else {}
    history = memory.get("history", []) if isinstance(memory.get("history"), list) else []
    return {
        "active_hypothesis_id": memory.get("active_hypothesis_id"),
        "selection_count": memory.get("selection_count", len(history)),
        "history_count": len(history),
        "last_selection_reason": memory.get("last_selection_reason"),
        "recent_regimes": [item.get("regime_context") for item in history[-5:]],
    }


def _rejection_reason(item: Mapping[str, Any], active: Any) -> str:
    if item.get("id") == active:
        return "selected"
    if float(item.get("score", 0.0) or 0.0) < 0.35:
        return "low_score"
    return "shadow_hypothesis_retained"

