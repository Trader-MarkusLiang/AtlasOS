"""Validate Atlas OS v0.8 Market Physics Constraint Engine behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
from runtime.cognition.latent_market_structure_engine import infer_latent_market_structure
from runtime.cognition.market_physics_constraint_engine import (
    apply_market_physics_constraints,
    check_conservation_laws,
    check_structural_invariants,
    compute_market_entropy,
    evaluate_system_stability,
    formulate_dynamic_system,
    infer_constraint_regime_emergence,
    market_conservation_laws,
)
from runtime.cognition.world_model_engine import simulate_market_world_model
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sample_layers() -> tuple[dict, dict, dict]:
    fusion = {
        "attention_pressure": 88,
        "liquidity_score": 28,
        "volatility_regime": "High",
        "narrative_intensity": 82,
        "stress_score": 72,
        "proposed_state": "HIGH_VOLATILITY",
    }
    causal = infer_causal_intelligence(
        fusion=fusion,
        attention_liquidity={"attention_index": 88, "liquidity_index": 28},
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    world_model = simulate_market_world_model(
        fusion=fusion,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
        steps=3,
    )
    latent = infer_latent_market_structure(
        world_model=world_model,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    return world_model, latent, causal


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
                source=event.get("source", "v0.8_validation"),
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
    laws = market_conservation_laws()
    _assert("liquidity_conservation_law" in laws, "liquidity law missing")
    _assert("attention_conservation_soft_form" in laws, "attention conservation missing")
    _assert("flow_continuity_law" in laws, "flow continuity missing")

    world_model, latent, causal = _sample_layers()
    no_source = check_conservation_laws(
        world_model=world_model,
        latent_structure=latent,
        source_attribution={
            "liquidity_source_strength": 0,
            "attention_transfer_strength": 0,
            "flow_transfer_strength": 0,
        },
    )
    _assert(
        no_source["liquidity_conservation"]["satisfied"] is False,
        "liquidity spike without origin must violate conservation",
    )
    with_source = check_conservation_laws(
        world_model=world_model,
        latent_structure=latent,
        source_attribution={
            "liquidity_source_strength": 100,
            "attention_transfer_strength": 100,
            "flow_transfer_strength": 100,
        },
    )
    _assert(with_source["liquidity_conservation"]["satisfied"] is True, "liquidity origin trace not accepted")

    entropy = compute_market_entropy(world_model=world_model, latent_structure=latent)
    high_entropy = dict(entropy)
    high_entropy["total_system_entropy"] = 92
    invariants = check_structural_invariants(
        conservation=no_source,
        entropy=high_entropy,
        latent_structure={
            "latent_variables": {
                "attention_persistence_field": 96,
                "structural_liquidity_pressure": 98,
                "hidden_risk_compression": 97,
            }
        },
    )
    _assert(invariants["unstable_regime_transition_zone"] is True, "invariant break must mark instability zone")
    _assert(invariants["forced_regime_label"] is None, "invariant break must not force regime label")
    _assert("entropy_explosion" in invariants["constraint_violations"], "entropy violation missing")

    dynamic = formulate_dynamic_system(
        world_model=world_model,
        latent_structure=latent,
        conservation=no_source,
        entropy=high_entropy,
    )
    _assert(dynamic["constraints_modify_trajectory"] is True, "constraints should modify trajectory")
    _assert(dynamic["constraints_override_state_directly"] is False, "constraints must not override state")
    _assert(dynamic["structural_divergence"] > 0, "constrained and unconstrained evolution must diverge")

    emergence = infer_constraint_regime_emergence(
        conservation=no_source,
        entropy=high_entropy,
        invariants=invariants,
        dynamic_system=dynamic,
    )
    _assert(emergence["emergence_basis"] == "constraint_stress", "emergence must depend on constraints")
    _assert(emergence["event_threshold_regime"] is False, "emergence must not be event threshold")
    _assert(emergence["forced_regime_label"] is None, "emergence must not force regime label")

    unstable_report = evaluate_system_stability(
        entropy=high_entropy,
        invariants=invariants,
        dynamic_system=dynamic,
        regime_emergence=emergence,
    )
    stable_report = evaluate_system_stability(
        entropy={"total_system_entropy": 15},
        invariants={
            "constraint_violations": [],
            "unstable_regime_transition_zone": False,
        },
        dynamic_system={"constraint_drag": 0},
        regime_emergence={"structural_collapse_risk_index": 5},
    )
    _assert(unstable_report["regime_fragility_index"] > stable_report["regime_fragility_index"], "entropy should raise fragility")
    _assert(unstable_report["stability_score"] < stable_report["stability_score"], "entropy should reduce stability")

    physics = apply_market_physics_constraints(
        world_model=world_model,
        latent_structure=latent,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    for key in (
        "market_conservation_laws",
        "conservation_state",
        "entropy_state",
        "structural_invariants",
        "dynamic_system",
        "constraint_driven_regime_emergence",
        "system_stability_report",
    ):
        _assert(key in physics, f"MPCE output missing {key}")
    _assert(physics["model_mode"] == "interpretable_constraint_system_non_ml", "bad MPCE mode")
    _assert(physics["not_forecasting_engine"] is True, "MPCE must not be forecasting engine")
    _assert(physics["no_trade_action"] is True, "MPCE must not create trade action")

    cognition = _run_loop_once(
        [
            {
                "event_type": "attention_spike",
                "priority": 88,
                "payload": {"attention": "exploding", "retail_attention": "dominant"},
            },
            {
                "event_type": "liquidity_shock",
                "priority": 92,
                "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
            },
        ]
    )
    _assert("physics_constraints" in cognition, "DecisionLoop did not persist physics_constraints")
    persisted = cognition["physics_constraints"]
    _assert(persisted["system_stability_report"], "persisted stability report missing")
    _assert(persisted["constraint_driven_regime_emergence"]["emergence_basis"] == "constraint_stress", "bad persisted emergence basis")

    print("Market Physics Constraint Engine v0.8 validation PASS")


if __name__ == "__main__":
    main()
