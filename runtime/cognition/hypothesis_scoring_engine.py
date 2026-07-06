"""Causal hypothesis scoring for Atlas Runtime v0.7."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


def score_causal_hypotheses(
    *,
    hypotheses: Iterable[Mapping[str, Any]],
    explanation_error_history: Iterable[Mapping[str, Any]],
    regime_state: str,
    trust_score: Mapping[str, Any],
    hypothesis_memory_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Score hypotheses without training or prediction."""

    items = list(hypotheses or [])
    errors = list(explanation_error_history or [])
    memory = hypothesis_memory_state if isinstance(hypothesis_memory_state, Mapping) else {}
    trust = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    prior_active = str(memory.get("active_hypothesis_id", ""))
    ranking = []
    for item in items:
        hid = str(item.get("id", "unknown"))
        graph = _as_mapping(item.get("causal_graph_variant"))
        edges = graph.get("edges", []) if isinstance(graph.get("edges"), list) else []
        confidence = _clamp01(_float(item.get("confidence"), 0.0))
        historical = _historical_consistency(hid, memory)
        error_reduction = _error_reduction_proxy(item, errors)
        stability = _regime_stability_score(hid, regime_state)
        trust_alignment = trust * confidence
        simplicity = _simplicity_score(len(edges))
        score = (
            historical * 0.18
            + error_reduction * 0.24
            + stability * 0.2
            + trust_alignment * 0.22
            + simplicity * 0.16
        )
        if hid == prior_active:
            score += 0.04
        ranking.append(
            {
                "id": hid,
                "score": round(_clamp01(score), 4),
                "historical_prediction_consistency": round(historical, 4),
                "explanation_error_reduction": round(error_reduction, 4),
                "regime_stability": round(stability, 4),
                "trust_alignment": round(trust_alignment, 4),
                "simplicity_accuracy_tradeoff": round(simplicity, 4),
            }
        )
    ranking.sort(key=lambda item: item["score"], reverse=True)
    distribution = {item["id"]: item["score"] for item in ranking}
    return {
        "best_hypothesis_id": ranking[0]["id"] if ranking else None,
        "hypothesis_ranking": ranking,
        "score_distribution": distribution,
        "trust_index_used": round(trust, 4),
        "metadata_only": True,
    }


def _historical_consistency(hypothesis_id: str, memory: Mapping[str, Any]) -> float:
    records = memory.get("history", []) if isinstance(memory.get("history"), list) else []
    relevant = [item for item in records[-12:] if item.get("selected_hypothesis_id") == hypothesis_id]
    if not relevant:
        return 0.5
    selected = len(relevant)
    rejected = sum(1 for item in records[-12:] if hypothesis_id in item.get("rejected_hypothesis_ids", []))
    return _clamp01(0.45 + selected * 0.08 - rejected * 0.05)


def _error_reduction_proxy(hypothesis: Mapping[str, Any], errors: list[Mapping[str, Any]]) -> float:
    if not errors:
        return _clamp01(_float(hypothesis.get("confidence"), 0.5))
    assumptions = " ".join(str(item) for item in hypothesis.get("structural_assumptions", [])).lower()
    latest = errors[-1]
    underestimated = " ".join(str(item) for item in latest.get("underestimated_factors", [])).lower()
    overlap = sum(1 for token in ("attention", "liquidity", "volatility", "narrative", "flow") if token in assumptions and token in underestimated)
    base = 1.0 - _float(latest.get("explanation_error_score"), 0.0)
    return _clamp01(base * 0.55 + min(0.45, overlap * 0.15))


def _regime_stability_score(hypothesis_id: str, regime: str) -> float:
    label = str(regime or "").upper()
    if label in {"HIGH_VOLATILITY", "RISK_OFF"} and hypothesis_id == "H_LIQUIDITY_STRESS":
        return 0.82
    if label == "ATTENTION_EXPANSION" and hypothesis_id in {"H_ATTENTION_FLOW", "H_NARRATIVE_REFLEXIVITY"}:
        return 0.78
    if label == "DISTRIBUTION" and hypothesis_id == "H_INSTITUTIONAL_ROTATION":
        return 0.76
    if label == "NORMAL":
        return 0.62
    return 0.5


def _simplicity_score(edge_count: int) -> float:
    return _clamp01(1.0 - max(0, edge_count - 3) * 0.12)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

