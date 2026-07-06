"""Controlled structural drift controller for Atlas Runtime v0.4.

The controller applies bounded, reversible structural overlays. It preserves a
delta log so drift can be audited or rolled back by future tooling.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


LOW_TRUST_THRESHOLD = 0.35
EDGE_CUMULATIVE_CAP = 0.15
SENSITIVITY_CUMULATIVE_CAP = 0.12
TOPOLOGY_CUMULATIVE_CAP = 0.18
MAX_DELTA_LOG = 20


def apply_structural_drift(
    *,
    mutated_graph: Mapping[str, Any],
    regime_topology: Mapping[str, Any],
    previous_structural_state: Mapping[str, Any] | None = None,
    trust_score: Mapping[str, Any] | None = None,
    explanation_correction: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Apply slow, reversible drift to the structural overlay state."""

    trust = _clamp01(_float((trust_score or {}).get("global_trust_index"), mutated_graph.get("global_trust_index", 0.5)))
    explanation = explanation_correction if isinstance(explanation_correction, Mapping) else {}
    previous = previous_structural_state if isinstance(previous_structural_state, Mapping) else {}
    previous_drift = _as_mapping(previous.get("applied_drift"))
    previous_edges = dict(_as_mapping(previous_drift.get("edge_weights")))
    previous_sensitivity = dict(_as_mapping(previous_drift.get("node_sensitivity")))
    previous_topology = dict(_as_mapping(previous_drift.get("regime_boundaries")))
    previous_log = list(previous.get("reversible_delta_log", [])) if isinstance(previous.get("reversible_delta_log"), list) else []

    if trust < LOW_TRUST_THRESHOLD or mutated_graph.get("status") == "frozen":
        return {
            "status": "frozen",
            "reason": mutated_graph.get("reason", "low_trust_freeze"),
            "mutation": dict(mutated_graph),
            "regime_topology": dict(regime_topology),
            "explanation_feedback": {
                "causal_correction": dict(explanation),
                "applied": False,
            },
            "applied_drift": {
                "edge_weights": previous_edges,
                "node_sensitivity": previous_sensitivity,
                "regime_boundaries": previous_topology,
            },
            "reversible_delta_log": previous_log[-MAX_DELTA_LOG:],
            "bounded": True,
            "reversible": True,
            "trust_gate": "closed",
            "graph_node_count": int(mutated_graph.get("graph_node_count", 0)),
            "graph_edge_count": int(mutated_graph.get("graph_edge_count", 0)),
        }

    edge_delta = _merge_delta_maps(
        _as_mapping(mutated_graph.get("edge_weight_updates")),
        _as_mapping(explanation.get("edge_weight_updates")),
        EDGE_CUMULATIVE_CAP,
    )
    sensitivity_delta = _as_mapping(mutated_graph.get("node_sensitivity_updates"))
    next_edges = _merge_bounded(previous_edges, edge_delta, EDGE_CUMULATIVE_CAP)
    next_sensitivity = _merge_bounded(previous_sensitivity, sensitivity_delta, SENSITIVITY_CUMULATIVE_CAP)
    topology_delta = {
        "attractor_shift": _float(regime_topology.get("attractor_shift"), 0.0),
        "basin_deformation": _float(regime_topology.get("basin_deformation"), 0.0),
    }
    next_topology = _merge_bounded(previous_topology, topology_delta, TOPOLOGY_CUMULATIVE_CAP)
    delta_record = {
        "edge_weight_updates": dict(edge_delta),
        "node_sensitivity_updates": dict(sensitivity_delta),
        "explanation_edge_weight_updates": dict(_as_mapping(explanation.get("edge_weight_updates"))),
        "regime_topology_updates": topology_delta,
        "inverse": {
            "edge_weight_updates": {key: round(-_float(value), 4) for key, value in edge_delta.items()},
            "node_sensitivity_updates": {key: round(-_float(value), 4) for key, value in sensitivity_delta.items()},
            "regime_topology_updates": {key: round(-_float(value), 4) for key, value in topology_delta.items()},
        },
    }
    shift = _float(mutated_graph.get("structural_shift_index"), 0.0)
    deformation = abs(topology_delta["attractor_shift"]) + abs(topology_delta["basin_deformation"])
    return {
        "status": "applied",
        "mutation": dict(mutated_graph),
        "regime_topology": dict(regime_topology),
        "explanation_feedback": {
            "causal_correction": dict(explanation),
            "applied": bool(edge_delta and explanation.get("status") == "applied"),
        },
        "applied_drift": {
            "edge_weights": next_edges,
            "node_sensitivity": next_sensitivity,
            "regime_boundaries": next_topology,
        },
        "reversible_delta_log": (previous_log + [delta_record])[-MAX_DELTA_LOG:],
        "drift_summary": {
            "structural_shift_index": round(shift, 4),
            "topology_deformation_index": round(deformation, 4),
            "cumulative_edge_abs_sum": round(sum(abs(_float(value)) for value in next_edges.values()), 4),
            "cumulative_sensitivity_abs_sum": round(sum(abs(_float(value)) for value in next_sensitivity.values()), 4),
        },
        "bounded": True,
        "reversible": True,
        "trust_gate": "open",
        "graph_node_count": int(mutated_graph.get("graph_node_count", 0)),
        "graph_edge_count": int(mutated_graph.get("graph_edge_count", 0)),
        "no_topology_rewrite": not bool(mutated_graph.get("topology_rewrite_applied")),
        "no_node_creation": not bool(mutated_graph.get("node_creation_allowed")),
    }


def _merge_bounded(base: Mapping[str, Any], delta: Mapping[str, Any], cap: float) -> Dict[str, float]:
    merged = {str(key): _float(value) for key, value in base.items()}
    for key, value in delta.items():
        merged[str(key)] = round(max(-cap, min(cap, merged.get(str(key), 0.0) + _float(value))), 4)
    return merged


def _merge_delta_maps(primary: Mapping[str, Any], secondary: Mapping[str, Any], cap: float) -> Dict[str, float]:
    merged = {str(key): _float(value) for key, value in primary.items()}
    for key, value in secondary.items():
        merged[str(key)] = round(max(-cap, min(cap, merged.get(str(key), 0.0) + _float(value))), 4)
    return merged


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
