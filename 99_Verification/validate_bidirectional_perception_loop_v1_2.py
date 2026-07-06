"""Validate Atlas OS v1.2 Bidirectional Perception Loop behavior."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.bidirectional_perception_engine import (
    attention_influenced_observation,
    compute_perception_weight_field,
    deform_input_distribution,
    generate_biased_market_view,
    measure_system_market_coupling,
    perception_feedback_loop,
)
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


EVENT = {
    "event_type": "attention_spike",
    "payload": {"attention": "rising", "narrative": "theme expansion"},
    "priority": 70,
    "source": "v1.2_validation",
}


HIGH_STATE = {
    "fusion": {"attention_pressure": 92},
    "unified_intelligence": {
        "unified_market_state": {
            "event_state": {"attention_pressure": 92},
        },
        "self_reference": {"system_induced_bias_field": 85},
        "unified_interpretation": {"dominant_regime_structure": "attention-heavy structure"},
    },
    "latent_structure": {
        "latent_variables": {
            "attention_persistence_field": 90,
            "structural_liquidity_pressure": 72,
        }
    },
    "physics_constraints": {
        "system_stability_report": {"regime_fragility_index": 70}
    },
    "market_laws": {
        "system_stability_evaluation": {"instability_collapse_risk": 45}
    },
}


LOW_STATE = {
    "fusion": {"attention_pressure": 18},
    "unified_intelligence": {
        "unified_market_state": {
            "event_state": {"attention_pressure": 18},
        },
        "self_reference": {"system_induced_bias_field": 5},
        "unified_interpretation": {"dominant_regime_structure": "low-attention structure"},
    },
    "latent_structure": {
        "latent_variables": {
            "attention_persistence_field": 18,
            "structural_liquidity_pressure": 15,
        }
    },
    "physics_constraints": {
        "system_stability_report": {"regime_fragility_index": 15}
    },
    "market_laws": {
        "system_stability_evaluation": {"instability_collapse_risk": 5}
    },
}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_once_with_state(state: Dict[str, Any]) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        inbox_dir = str(root / "inbox")
        log_path = str(root / "runtime.jsonl")
        store = StateStore(db_path=db_path)
        store.set_state("cognition_state", state)
        store.set_state("regime_memory", {"summary": {"dominant_state": "HIGH_VOLATILITY", "sequence_length": 3}})
        stream = EventStream(db_path=db_path, inbox_dir=inbox_dir)
        stream.enqueue_event(EVENT["event_type"], payload=EVENT["payload"], priority=EVENT["priority"], source=EVENT["source"])
        queued = store.get_event_history(limit=5)[0]
        loop = DecisionLoop(
            DecisionLoopConfig(
                db_path=db_path,
                inbox_dir=inbox_dir,
                log_path=log_path,
                heartbeat_interval_seconds=9999999999,
                max_events_per_cycle=10,
                sleep_interval_seconds=0,
            )
        )
        loop.run_once()
        cognition = store.get_state("cognition_state")
        return {
            "queued_event": queued,
            "fusion": cognition.get("fusion", {}),
            "causal": cognition.get("causal", {}),
            "cognition": cognition,
        }


def main() -> None:
    high_field = compute_perception_weight_field(cognition_state=HIGH_STATE, regime_memory={"dominant_state": "HIGH_VOLATILITY"})
    low_field = compute_perception_weight_field(cognition_state=LOW_STATE, regime_memory={"dominant_state": "NORMAL"})
    _assert(high_field["attention_bias_map"]["attention_spike"] > low_field["attention_bias_map"]["attention_spike"], "high attention state must increase attention bias")

    high_event = deform_input_distribution(EVENT, high_field)
    low_event = deform_input_distribution(EVENT, low_field)
    _assert(high_event["priority"] != low_event["priority"], "same event must produce different interpreted distribution")
    _assert(high_event["priority"] > low_event["priority"], "high attention state should amplify the same attention event")
    _assert(abs(high_event["perception_priority_delta"]) <= 25, "high event deformation must be bounded")
    _assert(abs(low_event["perception_priority_delta"]) <= 25, "low event deformation must be bounded")

    observation_high = attention_influenced_observation(attention_state=90, base_signal_strength=50, anomaly_level=40)
    observation_low = attention_influenced_observation(attention_state=15, base_signal_strength=50, anomaly_level=40)
    _assert(observation_high["detection_probability"] > observation_low["detection_probability"], "attention must alter signal sensitivity")
    _assert(observation_high["anomaly_sensitivity"] > observation_low["anomaly_sensitivity"], "attention must alter anomaly sensitivity")

    loop = perception_feedback_loop(event=EVENT, cognition_state=HIGH_STATE, regime_memory={"dominant_state": "HIGH_VOLATILITY"})
    _assert(loop["feedback_loop_exists"] is True, "feedback loop must exist")
    _assert(loop["deformed_event"]["priority"] != EVENT["priority"], "feedback loop must alter input weighting")

    coupling = measure_system_market_coupling(raw_event=EVENT, deformed_event=high_event, perception_weight_field=high_field)
    _assert(coupling["perception_influence_strength"] > 0, "coupling strength must be non-zero")
    _assert(coupling["input_deformation_ratio"] > 0, "input deformation ratio must be non-zero")
    _assert(coupling["bounded"] is True, "coupling must remain bounded")

    view = generate_biased_market_view([EVENT], cognition_state=HIGH_STATE, regime_memory={"dominant_state": "HIGH_VOLATILITY"})
    _assert(view["perception_adjusted_regime_signals"]["distribution_delta"] != 0, "biased market view must show distribution change")
    _assert(view["interpretability_preserved"] is True, "interpretability must be preserved")

    high_run = _run_once_with_state(HIGH_STATE)
    low_run = _run_once_with_state(LOW_STATE)
    high_priority = high_run["queued_event"]["priority"]
    low_priority = low_run["queued_event"]["priority"]
    _assert(high_priority != low_priority, "EventStream priority must depend on system state")
    _assert(
        high_run["fusion"]["attention_pressure"] != low_run["fusion"]["attention_pressure"],
        "same event must produce different fusion representation after BMPL",
    )
    _assert(
        high_run["causal"]["attention_meaning"] != low_run["causal"]["attention_meaning"]
        or high_run["causal"]["regime_transition_probability"] != low_run["causal"]["regime_transition_probability"],
        "same event must produce different causal representation after BMPL",
    )

    result = {
        "perception_weight_field_design": high_field,
        "same_event_differential_analysis": {
            "high_state_priority": high_priority,
            "low_state_priority": low_priority,
            "high_attention_pressure": high_run["fusion"]["attention_pressure"],
            "low_attention_pressure": low_run["fusion"]["attention_pressure"],
        },
        "coupling_strength_metrics": coupling,
        "feedback_loop_structure": loop["loop_structure"],
        "system_stability_evaluation": {
            "bounded_priority_delta": True,
            "event_type_preserved": high_event["payload"]["perception_adjustment"]["event_type_preserved"],
            "no_prediction_engine": True,
            "no_trade_action": True,
        },
        "risk_analysis": {
            "feedback_amplification_risk": "bounded_by_priority_delta_cap",
            "instability_risk": "low_for_v1.2_validation_fixture",
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    print("Bidirectional Perception Loop v1.2 validation PASS")


if __name__ == "__main__":
    main()
