"""Active causal structure selection for Atlas Runtime v0.7."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


LOW_TRUST_SWITCH_THRESHOLD = 0.45
MIN_SWITCH_MARGIN = 0.08
LOW_TRUST_MIN_AGE = 3
NORMAL_MIN_AGE = 2


def select_active_causal_structure(
    *,
    scored_hypotheses: Mapping[str, Any],
    hypotheses: Iterable[Mapping[str, Any]],
    previous_selection: Mapping[str, Any] | None = None,
    trust_score: Mapping[str, Any] | None = None,
    regime_state: str = "UNKNOWN",
) -> Dict[str, Any]:
    """Select a non-permanent active causal hypothesis."""

    previous = previous_selection if isinstance(previous_selection, Mapping) else {}
    trust = _clamp01(_float((trust_score or {}).get("global_trust_index"), 0.5))
    ranking = scored_hypotheses.get("hypothesis_ranking", [])
    ranking = ranking if isinstance(ranking, list) else []
    best = ranking[0] if ranking else {}
    best_id = best.get("id")
    previous_id = previous.get("active_hypothesis_id")
    age = int(previous.get("active_age", 0)) + 1 if previous_id else 1
    min_age = LOW_TRUST_MIN_AGE if trust < LOW_TRUST_SWITCH_THRESHOLD else NORMAL_MIN_AGE
    previous_score = _score_for(ranking, previous_id)
    best_score = _float(best.get("score"), 0.0)
    margin = best_score - previous_score
    can_switch = (
        bool(best_id)
        and best_id != previous_id
        and age >= min_age
        and (margin >= MIN_SWITCH_MARGIN or _regime_shift(previous, regime_state))
        and trust >= LOW_TRUST_SWITCH_THRESHOLD
    )
    active_id = best_id if (not previous_id or can_switch) else previous_id
    selected = _find_hypothesis(hypotheses, active_id)
    shadow = [item for item in hypotheses if item.get("id") != active_id]
    rejected_ids = [str(item.get("id")) for item in shadow]
    return {
        "active_hypothesis_id": active_id,
        "active_causal_structure": selected.get("causal_graph_variant", {}),
        "shadow_hypotheses": shadow,
        "selection_reason": "switched_on_regime_or_score" if can_switch else ("initial_selection" if not previous_id else "held_for_stability"),
        "switch_allowed": bool(can_switch),
        "active_age": 1 if can_switch or not previous_id else age,
        "switch_margin": round(margin, 4),
        "trust_gate": "open" if trust >= LOW_TRUST_SWITCH_THRESHOLD else "reduced_switching",
        "rejected_hypothesis_ids": rejected_ids,
        "regime_context": regime_state,
        "non_permanent_selection": True,
        "metadata_only": True,
    }


def _score_for(ranking: list[Mapping[str, Any]], hypothesis_id: Any) -> float:
    for item in ranking:
        if item.get("id") == hypothesis_id:
            return _float(item.get("score"), 0.0)
    return 0.0


def _find_hypothesis(hypotheses: Iterable[Mapping[str, Any]], hypothesis_id: Any) -> Mapping[str, Any]:
    for item in hypotheses:
        if item.get("id") == hypothesis_id:
            return item
    return {}


def _regime_shift(previous: Mapping[str, Any], regime: str) -> bool:
    return bool(previous.get("regime_context") and previous.get("regime_context") != regime)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

