"""Bounded causal graph mutation overlay for Atlas Runtime v0.4.

This module does not rewrite the CIL graph. It computes reversible, trust-gated
edge and sensitivity deltas that can be stored as structural metadata.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


LOW_TRUST_THRESHOLD = 0.35
MAX_MUTATION_INTENSITY = 0.05
MAX_EDGE_UPDATES = 6
MAX_NODE_SENSITIVITY_DELTA = 0.04
KNOWN_EDGE_KEYS = (
    "Narrative Pressure->Attention",
    "Attention->Retail Flow",
    "Institutional Flow->Liquidity",
    "Liquidity->Volatility",
    "Retail Flow->Price Momentum",
    "Price Momentum->Attention",
)


def mutate_causal_graph(
    *,
    cil_causal_graph: Mapping[str, Any],
    latent_structure: Mapping[str, Any],
    physics_constraints: Mapping[str, Any],
    trust_score: Mapping[str, Any],
    feedback_delta: Mapping[str, Any],
    previous_graph_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Return a bounded structural mutation proposal.

    The result is an overlay only. Low trust freezes mutation, and topology
    rewrite remains disabled unless constraints explicitly approve it.
    """

    trust = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    graph = cil_causal_graph if isinstance(cil_causal_graph, Mapping) else {}
    nodes = list(graph.get("nodes", [])) if isinstance(graph.get("nodes"), list) else []
    edges = list(graph.get("edges", [])) if isinstance(graph.get("edges"), list) else []
    previous = previous_graph_state if isinstance(previous_graph_state, Mapping) else {}

    if trust < LOW_TRUST_THRESHOLD:
        return _frozen_result(
            reason="low_trust_freeze",
            trust=trust,
            node_count=len(nodes),
            edge_count=len(edges),
            previous=previous,
        )

    latent = _as_mapping(latent_structure.get("latent_variables"))
    stability = _as_mapping(physics_constraints.get("system_stability_report"))
    violations = _constraint_violations(physics_constraints)
    feedback = _feedback_magnitude(feedback_delta)
    stability_score = _float(stability.get("stability_score"), 50.0)
    constraint_penalty = min(0.5, len(violations) * 0.12 + max(0.0, 50.0 - stability_score) / 160.0)
    trust_window = max(0.0, trust - LOW_TRUST_THRESHOLD) / (1.0 - LOW_TRUST_THRESHOLD)
    intensity = _round4(MAX_MUTATION_INTENSITY * trust_window * max(0.15, 1.0 - feedback * 3.0 - constraint_penalty))

    if intensity <= 0:
        return _frozen_result(
            reason="constraint_or_feedback_freeze",
            trust=trust,
            node_count=len(nodes),
            edge_count=len(edges),
            previous=previous,
        )

    pressure = {
        "attention": _score(latent.get("attention_persistence_field")),
        "liquidity": _score(latent.get("structural_liquidity_pressure")),
        "risk": _score(latent.get("hidden_risk_compression")),
        "narrative": _score(latent.get("narrative_propagation_inertia")),
        "rotation": _score(latent.get("capital_rotation_tension")),
    }
    edge_weight_updates = {
        "Narrative Pressure->Attention": _delta(intensity, pressure["narrative"] + pressure["attention"]),
        "Attention->Retail Flow": _delta(intensity, pressure["attention"] - pressure["liquidity"] * 0.4),
        "Institutional Flow->Liquidity": _delta(intensity, -pressure["liquidity"] + pressure["rotation"] * 0.35),
        "Liquidity->Volatility": _delta(intensity, pressure["risk"] + pressure["liquidity"]),
        "Retail Flow->Price Momentum": _delta(intensity, pressure["attention"] + pressure["rotation"] * 0.25),
        "Price Momentum->Attention": _delta(intensity, pressure["attention"] + pressure["narrative"] * 0.5),
    }
    edge_weight_updates = _limit_updates(edge_weight_updates, MAX_EDGE_UPDATES)
    node_sensitivity_updates = {
        "Attention": _sensitivity_delta(intensity, pressure["attention"]),
        "Liquidity": _sensitivity_delta(intensity, pressure["liquidity"]),
        "Volatility": _sensitivity_delta(intensity, pressure["risk"]),
        "Narrative Pressure": _sensitivity_delta(intensity, pressure["narrative"]),
        "Institutional Flow": _sensitivity_delta(intensity, -pressure["liquidity"] + pressure["rotation"] * 0.4),
        "Retail Flow": _sensitivity_delta(intensity, pressure["attention"] + pressure["narrative"] * 0.3),
    }
    structural_shift = _round4(
        sum(abs(value) for value in edge_weight_updates.values())
        + sum(abs(value) for value in node_sensitivity_updates.values())
    )
    return {
        "edge_weight_updates": edge_weight_updates,
        "node_sensitivity_updates": node_sensitivity_updates,
        "structural_shift_index": structural_shift,
        "mutation_intensity": intensity,
        "status": "proposed",
        "trust_gate": "open",
        "global_trust_index": _round4(trust),
        "bounded": True,
        "topology_rewrite_allowed": _topology_rewrite_allowed(physics_constraints),
        "topology_rewrite_applied": False,
        "node_creation_allowed": False,
        "graph_node_count": len(nodes),
        "graph_edge_count": len(edges),
        "known_edges_only": set(edge_weight_updates).issubset(set(KNOWN_EDGE_KEYS)),
        "constraint_violations_seen": violations,
    }


def _frozen_result(
    *,
    reason: str,
    trust: float,
    node_count: int,
    edge_count: int,
    previous: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "edge_weight_updates": {},
        "node_sensitivity_updates": {},
        "structural_shift_index": 0.0,
        "mutation_intensity": 0.0,
        "status": "frozen",
        "reason": reason,
        "trust_gate": "closed",
        "global_trust_index": _round4(trust),
        "bounded": True,
        "topology_rewrite_allowed": False,
        "topology_rewrite_applied": False,
        "node_creation_allowed": False,
        "graph_node_count": node_count,
        "graph_edge_count": edge_count,
        "previous_overlay_preserved": bool(previous),
    }


def _constraint_violations(physics_constraints: Mapping[str, Any]) -> list[str]:
    stability = _as_mapping(physics_constraints.get("system_stability_report"))
    invariants = _as_mapping(physics_constraints.get("structural_invariants"))
    values = stability.get("constraint_violations", invariants.get("constraint_violations", []))
    return [str(item) for item in values] if isinstance(values, list) else []


def _topology_rewrite_allowed(physics_constraints: Mapping[str, Any]) -> bool:
    stability = _as_mapping(physics_constraints.get("system_stability_report"))
    return bool(stability.get("constraint_approved_topology_rewrite", False))


def _limit_updates(values: Dict[str, float], limit: int) -> Dict[str, float]:
    ranked = sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)
    return dict(ranked[:limit])


def _delta(intensity: float, pressure: float) -> float:
    return _round4(max(-MAX_MUTATION_INTENSITY, min(MAX_MUTATION_INTENSITY, intensity * pressure)))


def _sensitivity_delta(intensity: float, pressure: float) -> float:
    raw = intensity * pressure * 0.8
    return _round4(max(-MAX_NODE_SENSITIVITY_DELTA, min(MAX_NODE_SENSITIVITY_DELTA, raw)))


def _score(value: Any) -> float:
    return (_float(value, 50.0) - 50.0) / 50.0


def _feedback_magnitude(feedback_delta: Mapping[str, Any]) -> float:
    values: list[float] = []
    for value in (feedback_delta if isinstance(feedback_delta, Mapping) else {}).values():
        if isinstance(value, Mapping):
            values.extend(abs(_float(item, 0.0)) for item in value.values())
        else:
            values.append(abs(_float(value, 0.0)))
    return max(values, default=0.0)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _round4(value: float) -> float:
    return round(float(value), 4)
