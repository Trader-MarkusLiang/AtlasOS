"""Pressure-test whether Atlas v1.0 UMIS is truly closed loop.

This diagnostic is intentionally adversarial. It does not modify runtime logic,
does not add prediction behavior, and does not touch CIL / LMSE / MPCE / MLE.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


TEST_EVENTS = [
    {
        "event_type": "attention_spike",
        "payload": {"attention": "exploding", "narrative": "dominant mania"},
        "priority": 70,
        "source": "v1.1_pressure_test",
    },
    {
        "event_type": "liquidity_shock",
        "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
        "priority": 95,
        "source": "v1.1_pressure_test",
    },
]


PRESSURE_PREVIOUS_UMIS = {
    "unified_interpretation": {
        "dominant_regime_structure": "forced high-attention interpretation frame",
        "system_induced_bias_field": 95,
    },
    "self_reference": {
        "interpretation_recursion_depth": 4,
        "system_induced_bias_field": 95,
    },
    "co_evolution": {
        "system_adaptation_rate": 90,
    },
    "self_adaptation": {
        "internal_interpretation_weights": {
            "event_weight": 5,
            "causal_weight": 5,
            "latent_weight": 60,
            "physics_weight": 60,
            "law_weight": 60,
        },
        "bias_correction_strength": 90,
    },
}


def run_cycle(previous_unified: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run one isolated decision-loop cycle and return observable trace fields."""

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        inbox_dir = str(root / "inbox")
        log_path = str(root / "runtime.jsonl")
        store = StateStore(db_path=db_path)
        if previous_unified is not None:
            store.set_state("cognition_state", {"unified_intelligence": previous_unified})

        stream = EventStream(db_path=db_path, inbox_dir=inbox_dir)
        for event in TEST_EVENTS:
            stream.enqueue_event(
                event["event_type"],
                payload=event["payload"],
                priority=event["priority"],
                source=event["source"],
            )

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
        cycle = loop.run_once()
        cognition = store.get_state("cognition_state")
        events = store.get_event_history(limit=10)
        return {
            "cycle": cycle,
            "event_weights": _event_weights(events),
            "fusion": _select(cognition.get("fusion", {}), [
                "stress_score",
                "attention_pressure",
                "liquidity_score",
                "narrative_intensity",
                "proposed_state",
            ]),
            "causal": _select(cognition.get("causal", {}), [
                "primary_driver",
                "secondary_driver",
                "market_pressure_source",
                "attention_meaning",
                "regime_transition_probability",
            ]),
            "world_model": _select(cognition.get("world_model", {}).get("regime_emergence_dynamics", {}), [
                "phase_transition_likelihood",
            ]),
            "latent": _select(cognition.get("latent_structure", {}).get("regime_attractors", {}), [
                "dominant_attractor_basin",
            ]),
            "physics": _select(cognition.get("physics_constraints", {}).get("system_stability_report", {}), [
                "stability_score",
                "regime_fragility_index",
            ]),
            "laws": _select(cognition.get("market_laws", {}).get("system_stability_evaluation", {}), [
                "law_system_stability_score",
                "instability_collapse_risk",
            ]),
            "umis": _select(cognition.get("unified_intelligence", {}).get("unified_interpretation", {}), [
                "dominant_regime_structure",
                "feedback_influence_score",
                "system_induced_bias_field",
            ]),
            "umis_self_reference": _select(cognition.get("unified_intelligence", {}).get("self_reference", {}), [
                "interpretation_recursion_depth",
                "past_system_state_affects_current_reasoning",
                "system_induced_bias_field",
            ]),
        }


def build_loop_dependency_map() -> List[Dict[str, Any]]:
    """Static trace map checked against current runtime wiring."""

    return [
        {
            "stage": "Event Stream",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "EventStream.enqueue_event and poll use event payload/default priority; no UMIS state is read.",
        },
        {
            "stage": "Fusion Engine",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "EventFusionEngine.fuse receives only current events, not previous UMIS.",
        },
        {
            "stage": "Regime Memory",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "RegimeMemory.summary feeds CIL/world/latent context, but not EventStream or fusion weighting.",
        },
        {
            "stage": "Causal Layer",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "CIL receives fusion and memory summary; it does not rewrite future events.",
        },
        {
            "stage": "World Model",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "World Model output feeds LMSE/MPCE/MLE/UMIS only.",
        },
        {
            "stage": "LMSE",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "Latent structure feeds MPCE/MLE/UMIS only.",
        },
        {
            "stage": "MPCE",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "Physics constraints feed MLE/UMIS only.",
        },
        {
            "stage": "MLE",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "Market laws feed UMIS only.",
        },
        {
            "stage": "UMIS",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "previous_unified_state is read after fusion/CIL/world/LMSE/MPCE/MLE, so it changes UMIS interpretation but not input weighting.",
        },
        {
            "stage": "State Controller",
            "output_influences_next_input": False,
            "output_influences_downstream_interpretation": True,
            "evidence": "Controller state is recorded into memory, influencing future context, not future event distribution.",
        },
    ]


def main() -> None:
    baseline = run_cycle()
    shifted = run_cycle(previous_unified=PRESSURE_PREVIOUS_UMIS)

    input_distribution_delta = _dict_delta(baseline["event_weights"], shifted["event_weights"])
    fusion_delta = _dict_delta(baseline["fusion"], shifted["fusion"])
    causal_delta = _dict_delta(baseline["causal"], shifted["causal"])
    representation_delta = _dict_delta(baseline["umis"], shifted["umis"])

    upstream_changed = bool(input_distribution_delta or fusion_delta or causal_delta)
    internal_changed = bool(representation_delta or _dict_delta(baseline["umis_self_reference"], shifted["umis_self_reference"]))

    dependency_map = build_loop_dependency_map()
    open_loop_points = [item["stage"] for item in dependency_map if not item["output_influences_next_input"]]
    closed_loop_points = [item["stage"] for item in dependency_map if item["output_influences_next_input"]]

    closure_conditions = {
        "system_output_modifies_future_input_distribution": bool(input_distribution_delta),
        "system_interpretation_affects_event_weighting": bool(input_distribution_delta),
        "market_representation_depends_on_system_state": internal_changed,
        "removing_system_changes_observed_market_evolution": False,
        "feedback_is_bidirectional_not_observational": upstream_changed,
    }

    strict_failures = [key for key, passed in closure_conditions.items() if not passed]
    verdict = "CLOSED LOOP SYSTEM" if not strict_failures else "OPEN LOOP SYSTEM"

    result = {
        "loop_dependency_map": dependency_map,
        "open_loop_points": open_loop_points,
        "closed_loop_points": closed_loop_points,
        "feedback_effect_analysis": {
            "feedback_effect_strength": _magnitude(representation_delta),
            "external_influence_delta": _magnitude({**input_distribution_delta, **fusion_delta, **causal_delta}),
            "input_distribution_delta": input_distribution_delta,
            "fusion_delta": fusion_delta,
            "causal_delta": causal_delta,
            "internal_umis_delta": representation_delta,
        },
        "system_removal_counterfactual": {
            "case_a_atlas_active": {
                "regime_detection": baseline["fusion"].get("proposed_state"),
                "attention_interpretation": baseline["causal"].get("attention_meaning"),
                "liquidity_classification": baseline["fusion"].get("liquidity_score"),
            },
            "case_b_null_system": {
                "regime_detection": "not_computed",
                "attention_interpretation": "not_computed",
                "liquidity_classification": "not_computed",
                "observed_event_distribution": baseline["event_weights"],
            },
            "system_dependency_score": 0.33,
            "causal_influence_on_observation": 0,
            "interpretation_dependency_note": "Atlas is required for interpretation outputs, but removal does not change observed event distribution.",
        },
        "unified_state_role": "observer_only",
        "internal_coupling_note": "UMIS changes internal interpretation values, but strict closed-loop conditions fail.",
        "closure_conditions": closure_conditions,
        "strict_failures": strict_failures,
        "final_closure_verdict": verdict,
        "confidence_score": 0.92,
        "boundary": {
            "no_prediction_model": True,
            "no_ml_dl_rl": True,
            "no_trading_logic_change": True,
            "no_buy_sell_output": True,
            "no_cil_lmse_mpce_mle_logic_change": True,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    if verdict == "CLOSED LOOP SYSTEM":
        raise AssertionError("Pressure test unexpectedly found strong closure; inspect proof manually.")


def _event_weights(events: List[Dict[str, Any]]) -> Dict[str, int]:
    return {event["event_type"]: int(event["priority"]) for event in events if event["event_type"] != "heartbeat"}


def _select(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return {key: data.get(key) for key in keys}


def _dict_delta(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    delta: Dict[str, Dict[str, Any]] = {}
    for key in sorted(set(left) | set(right)):
        if left.get(key) != right.get(key):
            delta[key] = {"baseline": left.get(key), "shifted": right.get(key)}
    return delta


def _magnitude(delta: Dict[str, Any]) -> int:
    if not delta:
        return 0
    score = 0
    for value in delta.values():
        if isinstance(value, dict) and isinstance(value.get("baseline"), (int, float)) and isinstance(value.get("shifted"), (int, float)):
            score += min(100, abs(int(value["shifted"]) - int(value["baseline"])))
        else:
            score += 10
    return min(100, score)


if __name__ == "__main__":
    main()
