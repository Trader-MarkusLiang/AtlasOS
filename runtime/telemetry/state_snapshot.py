"""Cognitive state snapshot capture for Atlas runtime observability."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore


DEFAULT_SNAPSHOT_PATH = Path("runtime/logs/cognitive_snapshots.jsonl")


def capture_cognitive_snapshot(
    *,
    tick: int,
    event: Dict[str, Any],
    db_path: Optional[str] = None,
    log_path: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Capture one append-only cognitive snapshot and never raise to callers."""

    store = StateStore(db_path=db_path)
    cognition = store.get_state("cognition_state")
    system_state = store.get_system_state()
    latest_brief = store.get_latest_decision_brief()
    latest_metadata = latest_brief.get("metadata", {}) if isinstance(latest_brief, dict) else {}
    llm_feedback = store.get_state("llm_feedback_state")
    system_trust_state = store.get_state("system_trust_state")
    structural_coevolution = store.get_state("structural_coevolution_state")
    self_organization = store.get_state("self_organization_state")
    event_history = store.get_event_history(limit=10)
    transition_history = store.get_state_transitions(limit=5)
    snapshot = {
        "timestamp": utc_now_iso(),
        "tick": int(tick),
        "event_stream_state": {
            "latest_event": event,
            "recent_events": event_history,
        },
        "regime_memory_state": _select(cognition.get("memory", {}), ["states", "weighted_state", "memory_depth", "decay"]),
        "system_state": system_state,
        "cil_outputs": _select(
            cognition.get("causal", {}),
            ["primary_driver", "secondary_driver", "attention_meaning", "regime_transition_probability"],
        ),
        "lmse_latent_structure_summary": _select(
            cognition.get("latent_structure", {}).get("regime_attractors", {}),
            ["dominant_attractor_basin", "structural_stability_index", "transition_barrier"],
        ),
        "mpce_constraint_violations": _select(
            cognition.get("physics_constraints", {}).get("constraint_violations", {}),
            ["violations", "violation_count", "severity"],
        ),
        "mle_law_state_summary": _select(
            cognition.get("market_laws", {}).get("system_stability_evaluation", {}),
            ["law_system_stability_score", "dominant_law", "multi_law_coexistence"],
        ),
        "llm_feedback_weights": _select(llm_feedback.get("modifiers", {}), [
            "attention_weight_delta",
            "causal_edge_strength_delta",
            "risk_confidence_delta",
            "liquidity_interpretation_bias_delta",
            "regime_probability_distribution_delta",
        ]),
        "llm_feedback_state": _select(llm_feedback, ["status", "stability", "freeze_remaining", "refinement_count"]),
        "trust_state": _select(
            system_trust_state,
            [
                "rolling_trust_index",
                "llm_provider_trust",
                "regime_trust_decay",
                "feedback_stability_index",
                "latest_trust_score",
                "trust_direction",
                "trust_adjustment_reason",
            ],
        ),
        "structural_coevolution_state": _select(
            structural_coevolution,
            [
                "status",
                "trust_gate",
                "bounded",
                "reversible",
                "graph_node_count",
                "graph_edge_count",
                "drift_summary",
                "regime_topology",
            ],
        ),
        "self_organization_state": _select(
            self_organization,
            [
                "status",
                "trust_gate",
                "trust_gate_value",
                "structural_shift_index",
                "causal_reweight_delta",
                "regime_attractor_shift",
                "trust_field_evolution",
                "trust_field_state",
                "structural_tension",
                "bounded",
                "reversible",
            ],
        ),
        "decision_packet_last_output": latest_metadata.get("decision_packet", {}),
        "decision_brief_id": latest_brief.get("id"),
        "state_transition_history": transition_history,
        "extra": extra or {},
    }
    _append_snapshot(snapshot, log_path=log_path)
    return snapshot


def read_cognitive_snapshots(log_path: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
    path = _resolve_path(log_path)
    if not path.exists():
        return []
    records: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append({"timestamp": utc_now_iso(), "status": "invalid_log_record"})
    return records


def _append_snapshot(snapshot: Dict[str, Any], log_path: Optional[str]) -> Path:
    path = _resolve_path(log_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, ensure_ascii=False, sort_keys=True) + "\n")
    except Exception:
        return path
    return path


def _resolve_path(log_path: Optional[str]) -> Path:
    configured = log_path or os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG")
    return Path(configured) if configured else DEFAULT_SNAPSHOT_PATH


def _select(value: Any, keys: list[str]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: value.get(key) for key in keys}
