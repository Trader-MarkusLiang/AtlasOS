"""Validate Atlas OS v0.7 Latent Market Structure Engine behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
from runtime.cognition.latent_market_structure_engine import (
    attention_field_dynamics,
    compute_regime_attractors,
    infer_latent_market_structure,
    infer_latent_variables,
    latent_regime_space_definition,
    map_market_phase_space,
    simulate_structural_counterfactual,
    simulate_structural_evolution,
)
from runtime.cognition.world_model_engine import simulate_market_world_model
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sample_world_model() -> tuple[dict, dict]:
    fusion = {
        "attention_pressure": 86,
        "liquidity_score": 30,
        "volatility_regime": "High",
        "narrative_intensity": 76,
        "stress_score": 68,
        "proposed_state": "ATTENTION_EXPANSION",
    }
    causal = infer_causal_intelligence(
        fusion=fusion,
        attention_liquidity={"attention_index": 86, "liquidity_index": 30},
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    world_model = simulate_market_world_model(
        fusion=fusion,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
        steps=3,
    )
    return world_model, causal


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
                source=event.get("source", "v0.7_validation"),
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
    space = latent_regime_space_definition()
    for field in (
        "structural_liquidity_pressure",
        "attention_persistence_field",
        "narrative_propagation_inertia",
        "hidden_risk_compression",
        "capital_rotation_tension",
    ):
        _assert(field in space["latent_variables"], f"missing latent variable: {field}")
    _assert("attention" in space["observed_variables"], "observed attention missing")
    _assert("projections" in space["principle"], "observed variables must be projections")

    world_model, causal = _sample_world_model()
    latent = infer_latent_variables(world_model)
    _assert(all(0 <= value <= 100 for value in latent.values()), "latent variables out of range")

    attractors = compute_regime_attractors(latent)
    basins = attractors["basins"]
    _assert(len(basins) >= 4, "multiple regime basins missing")
    for basin in basins.values():
        for key in ("attractor_strength", "basin_depth", "transition_barrier", "structural_stability_index"):
            _assert(key in basin, f"basin missing {key}")
    _assert(attractors["multiple_regime_basins"] is True, "attractor model must expose multiple basins")
    _assert(attractors["regimes_are_labels"] is False, "regimes must not be labels")

    small_attention_change = dict(latent)
    small_attention_change["attention_persistence_field"] = min(100, small_attention_change["attention_persistence_field"] + 4)
    small_change_attractors = compute_regime_attractors(small_attention_change)
    _assert(
        small_change_attractors["dominant_attractor_basin"] == attractors["dominant_attractor_basin"],
        "small attention change should not immediately flip attractor basin",
    )

    phase_space = map_market_phase_space(latent_variables=latent, world_model=world_model)
    _assert(phase_space["geometry_not_time_series"] is True, "phase space must be geometry, not time series")
    _assert("phase_curvature" in phase_space, "phase curvature missing")
    _assert("trajectory_drift_vector" in phase_space, "drift vector missing")
    _assert("volatility_manifold_shape" in phase_space, "volatility manifold missing")
    _assert(
        any(value != 0 for value in phase_space["trajectory_drift_vector"].values())
        or phase_space["phase_curvature"] > 0,
        "phase space drift / curvature missing",
    )

    attention_field = attention_field_dynamics(
        attention_observed=82,
        narrative_inertia=latent["narrative_propagation_inertia"],
        liquidity_pressure=latent["structural_liquidity_pressure"],
        previous_persistence=latent["attention_persistence_field"],
    )
    _assert(attention_field["attention_is_field"] is True, "attention must be field")
    _assert(attention_field["attention_persistence"] > 0, "attention persistence missing")
    _assert("decay_rate" in attention_field, "attention decay missing")
    _assert("cross_asset_diffusion" in attention_field, "attention diffusion missing")

    structural = simulate_structural_evolution(latent, steps=3)
    _assert(len(structural) == 4, "structural evolution should include t0 through t3")
    observed_move = abs(
        world_model["baseline_trajectory"][-1]["attention_field"]
        - world_model["baseline_trajectory"][0]["attention_field"]
    )
    structural_move = abs(structural[-1]["attention_persistence_field"] - structural[0]["attention_persistence_field"])
    _assert(structural_move <= max(1, observed_move), "latent forces should evolve slower than observations")

    counterfactual = simulate_structural_counterfactual(
        latent,
        modify_variable="hidden_risk_compression",
        modifier=35,
        steps=3,
    )
    _assert(counterfactual["structural_divergence_score"] > 0, "structural counterfactual should diverge")
    _assert(counterfactual["phase_space_deformation"] > 0, "phase space deformation missing")
    _assert("regime_attractor_shift" in counterfactual, "attractor shift missing")

    lmse = infer_latent_market_structure(
        world_model=world_model,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    _assert(lmse["model_mode"] == "interpretable_latent_structure_non_ml", "bad model mode")
    _assert(lmse["not_prediction_engine"] is True, "LMSE must not be prediction engine")
    _assert(lmse["no_trade_action"] is True, "LMSE must not create trade action")
    _assert(
        lmse["observation_structure_decoupling"]["observed_spikes_define_regime"] is False,
        "observed spikes must not directly define regime",
    )

    cognition = _run_loop_once(
        [
            {
                "event_type": "attention_spike",
                "priority": 86,
                "payload": {"attention": "exploding", "retail_attention": "dominant"},
            },
            {
                "event_type": "liquidity_shock",
                "priority": 88,
                "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
            },
        ]
    )
    _assert("latent_structure" in cognition, "DecisionLoop did not persist latent_structure")
    persisted = cognition["latent_structure"]
    _assert(persisted["latent_regime_space"]["regime_definition"].endswith("not labels."), "bad persisted regime definition")
    _assert(persisted["regime_attractors"]["multiple_regime_basins"], "persisted attractors missing")
    _assert(persisted["attention_field_dynamics"]["attention_is_field"], "persisted attention field missing")

    print("Latent Market Structure Engine v0.7 validation PASS")


if __name__ == "__main__":
    main()
