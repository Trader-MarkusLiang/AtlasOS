"""Replay console for Atlas UI v0.1."""

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.telemetry.replay_engine import replay_tick_sequence


def replay_session(
    start_tick: int,
    end_tick: int,
    *,
    decision_trace_path: Optional[str] = None,
    snapshot_path: Optional[str] = None,
    llm_trace_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Reconstruct a recorded runtime session without re-running cognition."""

    replay = replay_tick_sequence(
        start_tick,
        end_tick,
        decision_trace_path=decision_trace_path,
        snapshot_path=snapshot_path,
        llm_trace_path=llm_trace_path,
    )
    return {
        "decision_timeline": [
            {
                "tick": tick.get("tick"),
                "regime_state": tick.get("regime_state"),
                "decision_packet": tick.get("llm_decision_packet", {}),
                "feedback_delta": tick.get("feedback_delta", {}),
            }
            for tick in replay.get("replayed_ticks", [])
        ],
        "llm_trace_summary": {
            "llm_call_count": replay.get("llm_call_count", 0),
            "llm_output_comparison": replay.get("llm_output_comparison", {}),
        },
        "cognitive_state_evolution": [
            {
                "tick": tick.get("tick"),
                "snapshot_match": tick.get("snapshot_match"),
                "system_state": tick.get("snapshot", {}).get("system_state", {}),
                "trust_state": tick.get("snapshot", {}).get("trust_state", {}),
                "self_organization_state": tick.get("snapshot", {}).get("self_organization_state", {}),
            }
            for tick in replay.get("replayed_ticks", [])
        ],
        "read_only_replay": True,
    }

