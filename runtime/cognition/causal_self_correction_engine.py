"""Trust-gated causal self-correction for Atlas Runtime v0.6.

The engine emits edge-weight deltas only. It never creates nodes, rewrites the
graph topology, trains a model, or produces trading/prediction output.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


LOW_TRUST_THRESHOLD = 0.35
MAX_EDGE_DELTA = 0.035
MAX_TOTAL_ABS_DELTA = 0.12
KNOWN_EDGE_KEYS = (
    "Narrative Pressure->Attention",
    "Attention->Retail Flow",
    "Institutional Flow->Liquidity",
    "Liquidity->Volatility",
    "Retail Flow->Price Momentum",
    "Price Momentum->Attention",
)
FACTOR_TO_EDGES = {
    "Attention": ("Narrative Pressure->Attention", "Price Momentum->Attention"),
    "Retail Flow": ("Attention->Retail Flow",),
    "Liquidity": ("Institutional Flow->Liquidity", "Liquidity->Volatility"),
    "Institutional Flow": ("Institutional Flow->Liquidity",),
    "Volatility": ("Liquidity->Volatility",),
    "Narrative Pressure": ("Narrative Pressure->Attention",),
    "Price Momentum": ("Retail Flow->Price Momentum", "Price Momentum->Attention"),
}


def apply_causal_self_correction(
    *,
    explanation_error: Mapping[str, Any],
    causal_graph: Mapping[str, Any],
    trust_score: Mapping[str, Any],
    regime_alignment: Mapping[str, Any] | None = None,
    previous_correction: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Return bounded edge correction deltas from explanation error."""

    trust = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    graph_edges = _known_edges_in_graph(causal_graph)
    previous = previous_correction if isinstance(previous_correction, Mapping) else {}
    error_score = _clamp01(_float(explanation_error.get("explanation_error_score"), 0.0))
    alignment_score = _clamp01(_float(_as_mapping(regime_alignment).get("alignment_score"), 1.0))

    if trust < LOW_TRUST_THRESHOLD:
        return _frozen("low_trust_freeze", trust, graph_edges, previous)
    if error_score <= 0:
        return _frozen("no_explanation_error", trust, graph_edges, previous)

    trust_window = (trust - LOW_TRUST_THRESHOLD) / (1.0 - LOW_TRUST_THRESHOLD)
    intensity = min(MAX_EDGE_DELTA, error_score * 0.04 * trust_window * max(0.25, alignment_score))
    updates: Dict[str, float] = {}
    for factor in _as_list(explanation_error.get("underestimated_factors")):
        _add_factor_delta(updates, str(factor), intensity, graph_edges)
    for factor in _as_list(explanation_error.get("missing_causal_links")):
        _add_factor_delta(updates, str(factor), intensity * 1.25, graph_edges)
    for factor in _as_list(explanation_error.get("overestimated_factors")):
        _add_factor_delta(updates, str(factor), -intensity * 0.85, graph_edges)

    updates = _cap_total_abs(updates)
    return {
        "status": "applied" if updates else "stable",
        "edge_weight_updates": updates,
        "correction_intensity": round(intensity, 4),
        "explanation_error_score": round(error_score, 4),
        "alignment_score": round(alignment_score, 4),
        "trust_gate": "open",
        "global_trust_index": round(trust, 4),
        "known_edges_only": set(updates).issubset(set(KNOWN_EDGE_KEYS)),
        "node_creation_allowed": False,
        "topology_rewrite_applied": False,
        "previous_overlay_preserved": bool(previous),
        "bounded": True,
        "metadata_only": True,
    }


def _frozen(reason: str, trust: float, graph_edges: set[str], previous: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "status": "frozen",
        "reason": reason,
        "edge_weight_updates": {},
        "correction_intensity": 0.0,
        "trust_gate": "closed",
        "global_trust_index": round(trust, 4),
        "known_edges_only": True,
        "node_creation_allowed": False,
        "topology_rewrite_applied": False,
        "graph_edge_count": len(graph_edges),
        "previous_overlay_preserved": bool(previous),
        "bounded": True,
        "metadata_only": True,
    }


def _known_edges_in_graph(graph: Mapping[str, Any]) -> set[str]:
    edges = graph.get("edges", []) if isinstance(graph, Mapping) else []
    result = set()
    if isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, Mapping):
                result.add(f"{edge.get('from')}->{edge.get('to')}")
    return result or set(KNOWN_EDGE_KEYS)


def _add_factor_delta(updates: Dict[str, float], factor: str, delta: float, graph_edges: set[str]) -> None:
    for edge in FACTOR_TO_EDGES.get(factor, ()):
        if edge not in graph_edges and edge not in KNOWN_EDGE_KEYS:
            continue
        current = updates.get(edge, 0.0)
        updates[edge] = round(max(-MAX_EDGE_DELTA, min(MAX_EDGE_DELTA, current + delta)), 4)


def _cap_total_abs(updates: Dict[str, float]) -> Dict[str, float]:
    total = sum(abs(value) for value in updates.values())
    if total <= MAX_TOTAL_ABS_DELTA or total == 0:
        return dict(updates)
    scale = MAX_TOTAL_ABS_DELTA / total
    return {key: round(value * scale, 4) for key, value in updates.items()}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

