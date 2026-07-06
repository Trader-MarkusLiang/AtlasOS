"""Replay helpers for Atlas runtime observability logs.

Replay reconstructs the recorded decision path from telemetry logs. It does
not re-run cognition and therefore cannot change runtime behavior.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.telemetry.decision_trace_logger import read_decision_traces
from runtime.telemetry.llm_trace_logger import read_llm_traces
from runtime.telemetry.state_snapshot import read_cognitive_snapshots


def replay_tick_sequence(
    start_tick: int,
    end_tick: int,
    *,
    decision_trace_path: Optional[str] = None,
    snapshot_path: Optional[str] = None,
    llm_trace_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Return deterministic reconstruction for a tick range."""

    decisions = [
        record
        for record in read_decision_traces(log_path=decision_trace_path, limit=10000)
        if start_tick <= int(record.get("tick", -1)) <= end_tick
    ]
    snapshots = [
        record
        for record in read_cognitive_snapshots(log_path=snapshot_path, limit=10000)
        if start_tick <= int(record.get("tick", -1)) <= end_tick
    ]
    llm_traces = read_llm_traces(log_path=llm_trace_path, limit=10000)
    snapshots_by_tick = {int(record.get("tick", -1)): record for record in snapshots}
    replayed_ticks = []
    for decision in decisions:
        tick = int(decision.get("tick", -1))
        snapshot = snapshots_by_tick.get(tick, {})
        packet = decision.get("llm_decision_packet", {})
        replayed_ticks.append(
            {
                "tick": tick,
                "event": decision.get("event"),
                "regime_state": decision.get("regime_state"),
                "attention_state": decision.get("attention_state"),
                "causal_summary": decision.get("causal_summary"),
                "llm_decision_packet": packet,
                "feedback_delta": decision.get("feedback_delta", {}),
                "snapshot_match": _snapshot_matches_decision(snapshot, decision),
                "snapshot": snapshot,
            }
        )
    return {
        "start_tick": int(start_tick),
        "end_tick": int(end_tick),
        "tick_count": len(replayed_ticks),
        "replayed_ticks": replayed_ticks,
        "llm_call_count": len(llm_traces),
        "llm_output_comparison": compare_llm_outputs(llm_traces),
        "visualization_ready": True,
    }


def compare_llm_outputs(llm_traces: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Group observed LLM outputs by prompt hash for comparison."""

    grouped: Dict[str, set[str]] = {}
    for trace in llm_traces:
        prompt_hash = str(trace.get("prompt_hash", "missing"))
        grouped.setdefault(prompt_hash, set()).add(str(trace.get("output_raw", "")))
    return {
        prompt_hash: {
            "variant_count": len(outputs),
            "outputs": sorted(outputs),
        }
        for prompt_hash, outputs in grouped.items()
    }


def _snapshot_matches_decision(snapshot: Dict[str, Any], decision: Dict[str, Any]) -> bool:
    if not snapshot:
        return False
    snapshot_packet = snapshot.get("decision_packet_last_output", {})
    decision_packet = decision.get("llm_decision_packet", {})
    return snapshot_packet == decision_packet and snapshot.get("system_state", {}).get("current_state") == decision.get("regime_state")
