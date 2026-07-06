"""Validate Atlas OS v0.5 Causal Intelligence Layer behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import (
    compute_flow_propagation,
    counterfactual_test,
    infer_causal_intelligence,
    infer_regime_emergence,
    market_causal_graph,
    resolve_attention_meaning,
)
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_loop_once(events: list[dict]) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        inbox_dir = str(root / "inbox")
        log_path = str(root / "runtime.jsonl")
        stream = EventStream(db_path=db_path, inbox_dir=inbox_dir)
        for event in events:
            stream.enqueue_event(
                event["event_type"],
                payload=event.get("payload", {}),
                priority=event.get("priority"),
                source=event.get("source", "v0.5_validation"),
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
        loop.run_once()
        return StateStore(db_path=db_path).get_state("cognition_state")


def main() -> None:
    graph = market_causal_graph()
    _assert("Attention" in graph["nodes"], "causal graph missing Attention node")
    _assert("Retail Flow" in graph["nodes"], "causal graph missing Retail Flow node")
    _assert(
        any(edge["from"] == "Attention" and edge["to"] == "Retail Flow" for edge in graph["edges"]),
        "causal graph missing Attention -> Retail Flow edge",
    )

    high_liquidity_attention = resolve_attention_meaning(
        attention_spike=80,
        narrative_intensity=50,
        price_movement=1,
        volume_anomaly=70,
        liquidity_score=80,
        stress_score=20,
    )
    low_liquidity_attention = resolve_attention_meaning(
        attention_spike=80,
        narrative_intensity=50,
        price_movement=-1,
        volume_anomaly=70,
        liquidity_score=20,
        stress_score=70,
    )
    _assert(
        high_liquidity_attention == "liquidity-driven attention",
        "high-liquidity attention should mean liquidity-driven attention",
    )
    _assert(
        low_liquidity_attention == "panic-driven attention",
        "low-liquidity attention should mean panic-driven attention",
    )
    _assert(
        high_liquidity_attention != low_liquidity_attention,
        "same attention spike must resolve differently by liquidity context",
    )

    flow = compute_flow_propagation(
        attention_score=85,
        liquidity_score=35,
        narrative_intensity=75,
        volume_anomaly=60,
        stress_score=65,
    )
    _assert("retail_flow_strength" in flow, "flow propagation missing retail flow")
    _assert("institutional_flow_strength" in flow, "flow propagation missing institutional flow")
    _assert("latency_attention_to_flow" in flow, "flow propagation missing latency")
    _assert(
        "conversion_efficiency_attention_to_capital" in flow,
        "flow propagation missing conversion efficiency",
    )

    counterfactual = counterfactual_test(remove_node="Attention", fusion={"stress_score": 65}, flow_propagation=flow)
    _assert(
        counterfactual["adjusted"]["retail_flow_strength"] < counterfactual["baseline"]["retail_flow_strength"],
        "removing Attention should reduce retail flow",
    )
    _assert(
        counterfactual["adjusted"]["conversion_efficiency_attention_to_capital"]
        < counterfactual["baseline"]["conversion_efficiency_attention_to_capital"],
        "removing Attention should reduce conversion efficiency",
    )

    emergence = infer_regime_emergence(
        fusion={
            "stress_score": 55,
            "attention_pressure": 90,
            "liquidity_score": 25,
            "narrative_intensity": 80,
            "volatility_regime": "High",
        },
        attention_meaning="retail narrative attention",
        flow_propagation=flow,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    _assert(emergence["not_final_label"] is True, "regime emergence must not be final-label-only")
    _assert(emergence["formation_process"], "regime emergence missing formation process")
    _assert(emergence["dominant_causal_drivers"], "regime emergence missing causal drivers")
    _assert(emergence["structural_tension_map"], "regime emergence missing tension map")

    contradiction = infer_causal_intelligence(
        fusion={
            "stress_score": 45,
            "attention_pressure": 90,
            "liquidity_score": 25,
            "narrative_intensity": 70,
            "volatility_regime": "Medium",
            "proposed_state": "ATTENTION_EXPANSION",
        },
        attention_liquidity={"attention_index": 90, "liquidity_index": 25},
        memory_summary={"dominant_state": "NORMAL"},
    )
    tension = contradiction["regime_emergence"]["structural_tension_map"]
    _assert(tension["attention_vs_liquidity"]["level"] in {"High", "Severe"}, "contradiction collapsed")
    _assert(
        contradiction["regime_emergence"]["not_final_label"] is True,
        "contradictory signals must not collapse into one directional label",
    )
    _assert(
        contradiction["reasoning_mode"] == "symbolic_causal_non_ml",
        "CIL must remain symbolic non-ML reasoning",
    )

    cognition = _run_loop_once(
        [
            {
                "event_type": "attention_spike",
                "priority": 85,
                "payload": {"attention": "exploding", "evidence_quality": "unclear"},
            },
            {
                "event_type": "liquidity_shock",
                "priority": 80,
                "payload": {"liquidity": "contracting"},
            },
        ]
    )
    causal = cognition["causal"]
    for key in ("causal_graph", "attention_meaning", "flow_propagation", "regime_emergence", "counterfactuals"):
        _assert(key in causal, f"DecisionLoop cognition missing CIL key: {key}")
    _assert(causal["reasoning_mode"] == "symbolic_causal_non_ml", "DecisionLoop did not use CIL")

    print("Causal Intelligence Layer v0.5 validation PASS")


if __name__ == "__main__":
    main()
