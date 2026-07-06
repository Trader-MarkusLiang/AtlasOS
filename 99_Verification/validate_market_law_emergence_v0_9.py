"""Validate Atlas OS v0.9 Market Law Emergence Engine behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
from runtime.cognition.latent_market_structure_engine import infer_latent_market_structure
from runtime.cognition.market_law_emergence_engine import (
    check_law_consistency,
    discover_market_laws,
    evolve_constraints,
    infer_market_law_emergence,
    regime_conditioned_laws,
    simulate_meta_dynamics,
)
from runtime.cognition.market_physics_constraint_engine import apply_market_physics_constraints
from runtime.cognition.world_model_engine import simulate_market_world_model
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sample_layers() -> tuple[dict, dict, dict, dict]:
    fusion = {
        "attention_pressure": 90,
        "liquidity_score": 26,
        "volatility_regime": "High",
        "narrative_intensity": 84,
        "stress_score": 74,
        "proposed_state": "HIGH_VOLATILITY",
    }
    memory = {"dominant_state": "HIGH_VOLATILITY", "sequence_length": 4}
    causal = infer_causal_intelligence(
        fusion=fusion,
        attention_liquidity={"attention_index": 90, "liquidity_index": 26},
        memory_summary=memory,
    )
    world_model = simulate_market_world_model(fusion=fusion, causal=causal, memory_summary=memory, steps=3)
    latent = infer_latent_market_structure(world_model=world_model, causal=causal, memory_summary=memory)
    physics = apply_market_physics_constraints(
        world_model=world_model,
        latent_structure=latent,
        causal=causal,
        memory_summary=memory,
    )
    return world_model, latent, physics, memory


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
                source=event.get("source", "v0.9_validation"),
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
    latent_patterns = [
        {
            "attention_persistence_field": 82,
            "structural_liquidity_pressure": 42,
            "hidden_risk_compression": 76,
        },
        {
            "attention_persistence_field": 84,
            "structural_liquidity_pressure": 44,
            "hidden_risk_compression": 78,
        },
        {
            "attention_persistence_field": 86,
            "structural_liquidity_pressure": 45,
            "hidden_risk_compression": 80,
        },
    ]
    physics_patterns = [
        {
            "total_system_entropy": 72,
            "regime_fragility_index": 74,
            "constraint_violations": ["flow_continuity_violation"],
            "flow_continuity_satisfied": False,
        },
        {
            "total_system_entropy": 70,
            "regime_fragility_index": 72,
            "constraint_violations": ["flow_continuity_violation"],
            "flow_continuity_satisfied": False,
        },
        {
            "total_system_entropy": 68,
            "regime_fragility_index": 66,
            "constraint_violations": [],
            "flow_continuity_satisfied": True,
        },
    ]
    attention_flow_patterns = [
        {"decay_rate": 20, "attention_persistence": 78},
        {"decay_rate": 22, "attention_persistence": 80},
        {"decay_rate": 24, "attention_persistence": 82},
    ]

    laws = discover_market_laws(
        latent_patterns=latent_patterns,
        physics_patterns=physics_patterns,
        regime_transitions=[{"dominant_state": "HIGH_VOLATILITY"}] * 3,
        attention_flow_patterns=attention_flow_patterns,
    )
    _assert(laws, "repeated patterns must generate emergent laws")
    _assert(max(law["stability_score"] for law in laws) > 50, "emergent law stability below threshold")
    for law in laws:
        for key in ("law_type", "stability_score", "recurrence_frequency", "violation_rate", "regime_dependency"):
            _assert(key in law, f"law missing {key}")

    evolved = evolve_constraints(
        laws,
        previous_constraint_graph={law["law_type"]: {"weight": 50} for law in laws},
    )
    drift = evolved["evolutionary_drift_map"]
    _assert(evolved["constraints_are_static"] is False, "constraints must not be static")
    _assert(any(value != 0 for value in drift.values()), "at least one constraint must evolve")

    variants = regime_conditioned_laws(laws)
    first_law = laws[0]["law_type"]
    behavior = variants["law_variants"][first_law]
    _assert(
        behavior["crash_stress"] != behavior["liquidity_expansion"],
        "same law must behave differently by regime",
    )

    contradictory_laws = [
        {
            "law_type": "liquidity_attention_coupling",
            "stability_score": 72,
            "recurrence_frequency": 80,
            "violation_rate": 30,
        },
        {
            "law_type": "attention_decay_redistribution",
            "stability_score": 68,
            "recurrence_frequency": 75,
            "violation_rate": 35,
        },
    ]
    consistency = check_law_consistency(contradictory_laws)
    _assert(consistency["multi_law_coexistence_zone"] is True, "contradictions must coexist")
    _assert(consistency["forced_resolution"] is False, "contradictions must not be forced resolved")

    meta = simulate_meta_dynamics(
        [
            *laws,
            {"law_type": "unstable_test_law", "stability_score": 35, "recurrence_frequency": 50, "violation_rate": 70},
        ],
        evolve_constraints(
            [
                *laws,
                {
                    "law_type": "contradictory_test_law",
                    "stability_score": 62,
                    "recurrence_frequency": 70,
                    "violation_rate": 50,
                },
                {"law_type": "unstable_test_law", "stability_score": 35, "recurrence_frequency": 50, "violation_rate": 70},
            ],
            previous_constraint_graph={},
        ),
    )
    events = meta["constraint_birth_death_events"]
    _assert(events["birth"], "meta dynamics must show law birth")
    _assert(events["decay"], "meta dynamics must show law decay")
    _assert(events["mutation"], "meta dynamics must show law mutation")

    world_model, latent, physics, memory = _sample_layers()
    market_laws = infer_market_law_emergence(
        latent_structure=latent,
        physics_constraints=physics,
        world_model=world_model,
        memory_summary=memory,
    )
    for key in (
        "discovered_market_laws",
        "constraint_evolution",
        "regime_dependent_law_behavior",
        "meta_dynamics_report",
        "contradiction_analysis",
        "system_stability_evaluation",
    ):
        _assert(key in market_laws, f"MLE output missing {key}")
    _assert(market_laws["constraints_are_static"] is False, "MLE must evolve constraints")
    _assert(market_laws["model_mode"] == "interpretable_market_law_emergence_non_ml", "bad model mode")
    _assert(market_laws["not_prediction_engine"] is True, "MLE must not be prediction engine")
    _assert(market_laws["no_trade_action"] is True, "MLE must not create trade action")

    cognition = _run_loop_once(
        [
            {
                "event_type": "attention_spike",
                "priority": 90,
                "payload": {"attention": "exploding", "retail_attention": "dominant"},
            },
            {
                "event_type": "liquidity_shock",
                "priority": 94,
                "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
            },
        ]
    )
    _assert("market_laws" in cognition, "DecisionLoop did not persist market_laws")
    persisted = cognition["market_laws"]
    _assert(persisted["law_emergence_basis"] == "repeated_interpretable_structural_patterns", "bad emergence basis")
    _assert(persisted["system_stability_evaluation"]["interpretability_preserved"] is True, "interpretability lost")

    print("Market Law Emergence Engine v0.9 validation PASS")


if __name__ == "__main__":
    main()
