"""Read-only state visualization data for Atlas UI v0.1."""

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.state_store import StateStore
from runtime.telemetry.decision_trace_logger import read_decision_traces
from runtime.telemetry.state_snapshot import read_cognitive_snapshots


def build_dashboard_state(
    *,
    db_path: Optional[str] = None,
    decision_trace_path: Optional[str] = None,
    snapshot_path: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Return visualization-ready runtime state without cognition imports."""

    store = StateStore(db_path=db_path)
    cognition = store.get_state("cognition_state")
    snapshots = read_cognitive_snapshots(log_path=snapshot_path, limit=limit)
    decisions = read_decision_traces(log_path=decision_trace_path, limit=limit)
    return {
        "system_state": store.get_system_state(),
        "regime_state_timeline": [
            {
                "tick": item.get("tick"),
                "regime_state": item.get("regime_state"),
                "timestamp": item.get("timestamp"),
            }
            for item in decisions
        ],
        "attention_liquidity_charts": [
            {
                "tick": item.get("tick"),
                "attention": item.get("event_stream_state", {}).get("latest_event", {}).get("payload", {}).get("attention_pressure"),
                "liquidity": item.get("event_stream_state", {}).get("latest_event", {}).get("payload", {}).get("liquidity_score"),
            }
            for item in snapshots
        ],
        "causal_graph_snapshot": cognition.get("causal", {}).get("causal_graph", {}),
        "trust_field_evolution_curve": [
            {
                "tick": item.get("tick"),
                "trust_field_evolution": _as_dict(item.get("self_organization_state")).get("trust_field_evolution"),
                "trust_field": _as_dict(
                    _as_dict(item.get("self_organization_state")).get("trust_field_state")
                ).get("trust_field", {}),
            }
            for item in snapshots
        ],
        "latest_trust": store.get_state("system_trust_state"),
        "latest_self_organization": store.get_state("self_organization_state"),
        "read_only": True,
    }


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def dashboard_summary(**kwargs: Any) -> Dict[str, Any]:
    state = build_dashboard_state(**kwargs)
    return {
        "current_state": state.get("system_state", {}).get("current_state", "Unknown"),
        "timeline_points": len(state.get("regime_state_timeline", [])),
        "trust_curve_points": len(state.get("trust_field_evolution_curve", [])),
        "has_causal_graph_snapshot": bool(state.get("causal_graph_snapshot")),
        "read_only": True,
    }
