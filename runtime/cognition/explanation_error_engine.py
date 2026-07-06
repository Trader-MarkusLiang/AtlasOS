"""Explanation error engine for Atlas Runtime v0.6.

This module turns explanation mismatch into bounded metadata. It does not train
models, rewrite causal definitions, or produce trading/prediction output.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Set


FACTOR_KEYWORDS = {
    "Attention": ("attention", "narrative", "retail", "mania", "panic"),
    "Liquidity": ("liquidity", "depth", "flow", "capital", "institutional"),
    "Volatility": ("volatility", "stress", "risk", "crash"),
    "Narrative Pressure": ("narrative", "story", "news"),
    "Retail Flow": ("retail", "participation"),
    "Institutional Flow": ("institutional", "repositioning"),
    "Price Momentum": ("momentum", "price"),
}


def compute_explanation_error(
    *,
    decision_explanation: Mapping[str, Any] | str,
    actual_outcome_state: Mapping[str, Any],
    causal_graph_prediction: Mapping[str, Any],
    observed_result: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compare explanation factors against observed outcome and causal result.

    The score is a bounded mismatch proxy:
    - missing observed causal factors increase error
    - overemphasized factors absent from observed state increase error
    - prediction-vs-observed causal mismatch increases error
    """

    explained = _extract_explained_factors(decision_explanation)
    observed = _extract_observed_factors(actual_outcome_state, observed_result)
    predicted = _extract_predicted_factors(causal_graph_prediction)
    if not observed:
        observed = set(predicted)
    if not explained:
        explained = set(predicted)

    missing = sorted(observed - explained - predicted)
    underestimated = sorted((observed - explained) | (observed - predicted))
    overestimated = sorted(explained - observed)
    prediction_gap = sorted(predicted ^ observed)

    raw_error = (
        len(missing) * 0.22
        + len(underestimated) * 0.14
        + len(overestimated) * 0.12
        + len(prediction_gap) * 0.08
    )
    score = _clamp01(raw_error)
    return {
        "explanation_error_score": round(score, 4),
        "missing_causal_links": missing,
        "overestimated_factors": overestimated,
        "underestimated_factors": underestimated,
        "prediction_observation_gap": prediction_gap,
        "explained_factors": sorted(explained),
        "observed_factors": sorted(observed),
        "predicted_factors": sorted(predicted),
        "bounded": True,
        "metadata_only": True,
    }


def compute_multi_explanation_competition(
    *,
    explanations: list[Mapping[str, Any] | str],
    causal_graph_variants: list[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Compute divergence and contradiction among competing explanations."""

    factor_sets = [_extract_explained_factors(item) for item in explanations]
    edge_sets = [_edge_set(variant) for variant in causal_graph_variants]
    factor_divergence = _average_jaccard_distance(factor_sets)
    structural_divergence = _average_jaccard_distance(edge_sets)
    contradictions = _contradiction_clusters(factor_sets, edge_sets)
    conflict_score = _clamp01((factor_divergence * 0.45) + (structural_divergence * 0.45) + min(0.1, len(contradictions) * 0.03))
    instability = _clamp01(conflict_score * 0.7 + abs(len(explanations) - len(causal_graph_variants)) * 0.05)
    return {
        "explanation_divergence_index": round(factor_divergence, 4),
        "structural_divergence_index": round(structural_divergence, 4),
        "causal_conflict_score": round(conflict_score, 4),
        "model_instability_pressure": round(instability, 4),
        "contradiction_clusters": contradictions,
        "multi_explanation_count": len(explanations),
        "metadata_only": True,
    }


def _extract_explained_factors(value: Mapping[str, Any] | str) -> Set[str]:
    if isinstance(value, Mapping):
        text = " ".join(
            str(value.get(key, ""))
            for key in ("causal_summary", "reasoning_trace", "risk_level", "attention_state", "liquidity_state")
        )
    else:
        text = str(value or "")
    return _factors_from_text(text)


def _extract_predicted_factors(causal: Mapping[str, Any]) -> Set[str]:
    result: Set[str] = set()
    for key in ("primary_driver", "secondary_driver", "market_pressure_source"):
        result.update(_factors_from_text(str(causal.get(key, ""))))
    emergence = _as_mapping(causal.get("regime_emergence_state") or causal.get("regime_emergence"))
    drivers = emergence.get("dominant_causal_drivers", [])
    if isinstance(drivers, list):
        for item in drivers:
            result.update(_factors_from_text(str(item)))
    return result


def _extract_observed_factors(
    actual: Mapping[str, Any],
    observed_result: Mapping[str, Any] | None,
) -> Set[str]:
    source = actual if isinstance(actual, Mapping) else {}
    fusion = _as_mapping(source.get("fusion"))
    transition = _as_mapping(source.get("transition") or source.get("controller"))
    observed = _as_mapping(observed_result)
    result: Set[str] = set()

    state_text = " ".join(
        str(item)
        for item in (
            transition.get("current_state"),
            transition.get("proposed_state"),
            observed.get("state"),
            observed.get("regime_state"),
        )
    )
    result.update(_factors_from_text(state_text))

    attention = _float(fusion.get("attention_pressure"), _float(observed.get("attention"), 0.0))
    liquidity = _float(fusion.get("liquidity_score"), _float(observed.get("liquidity"), 50.0))
    stress = _float(fusion.get("stress_score"), _float(observed.get("stress"), 0.0))
    narrative = _float(fusion.get("narrative_intensity"), _float(observed.get("narrative"), 0.0))
    volatility = str(fusion.get("volatility_regime", observed.get("volatility", ""))).lower()

    if attention >= 55:
        result.add("Attention")
        result.add("Retail Flow")
    if liquidity <= 40 or liquidity >= 65:
        result.add("Liquidity")
        result.add("Institutional Flow")
    if stress >= 55 or "high" in volatility:
        result.add("Volatility")
    if narrative >= 55:
        result.add("Narrative Pressure")
    return result


def _factors_from_text(text: str) -> Set[str]:
    lower = str(text or "").replace("_", " ").lower()
    result: Set[str] = set()
    for factor, keywords in FACTOR_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            result.add(factor)
    return result


def _edge_set(graph: Mapping[str, Any]) -> Set[str]:
    edges = graph.get("edges", []) if isinstance(graph, Mapping) else []
    result: Set[str] = set()
    if isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, Mapping):
                result.add(f"{edge.get('from')}->{edge.get('to')}")
    return result


def _average_jaccard_distance(sets: list[Set[str]]) -> float:
    if len(sets) < 2:
        return 0.0
    distances: list[float] = []
    for index, left in enumerate(sets):
        for right in sets[index + 1 :]:
            union = left | right
            if not union:
                distances.append(0.0)
            else:
                distances.append(1.0 - len(left & right) / len(union))
    return sum(distances) / max(1, len(distances))


def _contradiction_clusters(factor_sets: list[Set[str]], edge_sets: list[Set[str]]) -> list[Dict[str, Any]]:
    clusters: list[Dict[str, Any]] = []
    attention_count = sum("Attention" in factors for factors in factor_sets)
    liquidity_count = sum("Liquidity" in factors for factors in factor_sets)
    volatility_count = sum("Volatility" in factors for factors in factor_sets)
    if attention_count and liquidity_count and attention_count != liquidity_count:
        clusters.append({"type": "attention_vs_liquidity", "attention_models": attention_count, "liquidity_models": liquidity_count})
    if volatility_count and attention_count and volatility_count != attention_count:
        clusters.append({"type": "volatility_vs_attention", "volatility_models": volatility_count, "attention_models": attention_count})
    if _average_jaccard_distance(edge_sets) > 0.55:
        clusters.append({"type": "structural_edge_divergence", "edge_divergence": round(_average_jaccard_distance(edge_sets), 4)})
    return clusters


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
