"""Validate Atlas OS v1.0 Unified Market Intelligence Core behavior."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
from runtime.cognition.latent_market_structure_engine import infer_latent_market_structure
from runtime.cognition.market_law_emergence_engine import infer_market_law_emergence
from runtime.cognition.market_physics_constraint_engine import apply_market_physics_constraints
from runtime.cognition.unified_market_intelligence_core import (
    build_unified_market_state,
    co_evolution_dynamics,
    infer_unified_market_intelligence,
    interpret_unified_state,
    market_system_feedback_loop,
    self_referential_causality,
    system_self_adaptation,
)
from runtime.cognition.world_model_engine import simulate_market_world_model
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sample_layers(stress: int = 76, attention: int = 88, liquidity: int = 28) -> tuple[dict, dict, dict, dict, dict, dict]:
    fusion = {
        "attention_pressure": attention,
        "liquidity_score": liquidity,
        "volatility_regime": "High",
        "narrative_intensity": 82,
        "stress_score": stress,
        "proposed_state": "HIGH_VOLATILITY",
    }
    memory = {"dominant_state": "HIGH_VOLATILITY", "sequence_length": 5}
    causal = infer_causal_intelligence(
        fusion=fusion,
        attention_liquidity={"attention_index": attention, "liquidity_index": liquidity},
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
    laws = infer_market_law_emergence(
        latent_structure=latent,
        physics_constraints=physics,
        world_model=world_model,
        memory_summary=memory,
    )
    return fusion, causal, world_model, latent, physics, laws


def _run_loop_twice() -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        inbox_dir = str(root / "inbox")
        log_path = str(root / "runtime.jsonl")
        stream = EventStream(db_path=db_path, inbox_dir=inbox_dir)
        stream.enqueue_event(
            "attention_spike",
            payload={"attention": "extreme", "narrative": "crowded"},
            priority=88,
            source="v1.0_validation",
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
        stream.enqueue_event(
            "liquidity_shock",
            payload={"liquidity": "contracting", "keyword": "stress"},
            priority=92,
            source="v1.0_validation",
        )
        loop.run_once()
        return StateStore(db_path=db_path).get_state("cognition_state")


def main() -> None:
    fusion, causal, world_model, latent, physics, laws = _sample_layers()
    unified = infer_unified_market_intelligence(
        fusion=fusion,
        causal=causal,
        world_model=world_model,
        latent_structure=latent,
        physics_constraints=physics,
        market_laws=laws,
        memory_summary={"dominant_state": "HIGH_VOLATILITY", "sequence_length": 5},
    )

    state = unified["unified_market_state"]
    for key in (
        "event_state",
        "causal_state",
        "latent_structure_state",
        "physics_constraint_state",
        "emergent_law_state",
    ):
        _assert(key in state, f"UnifiedMarketState missing {key}")
    _assert(state["unified_state_space"] is True, "unified state space not marked")
    _assert(state["isolated_interpretation_layers"] is False, "layers remain isolated")

    feedback = unified["feedback_loop_design"]
    _assert(feedback["market_system_loop_closed"] is True, "closed loop missing")
    _assert(feedback["one_way_pipeline"] is False, "pipeline remains one-way")
    _assert(feedback["interpretation_frame_affects_next_input"] is True, "output does not influence next input")

    second = infer_unified_market_intelligence(
        fusion=fusion,
        causal=causal,
        world_model=world_model,
        latent_structure=latent,
        physics_constraints=physics,
        market_laws=laws,
        memory_summary={"dominant_state": "HIGH_VOLATILITY", "sequence_length": 6},
        previous_unified_state=unified,
    )
    _assert(
        second["self_reference"]["past_system_state_affects_current_reasoning"] is True,
        "past system state must affect current reasoning",
    )
    _assert(
        second["self_reference"]["interpretation_recursion_depth"]
        > unified["self_reference"]["interpretation_recursion_depth"],
        "recursion depth did not increase",
    )

    unified_state = build_unified_market_state(
        event_state=fusion,
        causal_state=causal,
        latent_structure_state=latent,
        physics_constraint_state=physics,
        emergent_law_state=laws,
        memory_state={"dominant_state": "HIGH_VOLATILITY", "sequence_length": 5},
        previous_unified_state=second,
    )
    loop = market_system_feedback_loop(unified_state, previous_unified_state=second)
    self_ref = self_referential_causality(unified_state, previous_unified_state=second)
    coevo = co_evolution_dynamics(unified_state, loop, self_ref, previous_unified_state=second)
    _assert(coevo["mutual_influence_loop"] is True, "co-evolution loop missing")
    _assert(coevo["system_and_market_evolve_together"] is True, "mutual evolution missing")

    interpretation = interpret_unified_state(
        unified_state,
        feedback_loop=loop,
        self_reference=self_ref,
        co_evolution=coevo,
    )
    for key in (
        "dominant_regime_structure",
        "causal_latent_alignment",
        "physics_constraint_pressure",
        "emergent_law_consistency",
    ):
        _assert(key in interpretation, f"unified interpretation missing {key}")
    _assert(interpretation["unified_state_only"] is True, "interpretation not derived from unified state")
    _assert(interpretation["external_final_truth_layer"] is False, "external final truth layer exists")

    adaptation = system_self_adaptation(unified_state, interpretation)
    _assert(adaptation["adapts_trading_weights"] is False, "trading weights must not adapt")
    _assert(adaptation["adapts_portfolio_weights"] is False, "portfolio weights must not adapt")

    for key in ("not_prediction_engine", "no_trade_action", "no_signal_generator", "interpretability_preserved"):
        _assert(unified[key] is True, f"UMIS boundary flag failed: {key}")
    _assert(unified["model_mode"] == "interpretable_unified_market_intelligence_non_ml", "bad model mode")

    cognition = _run_loop_twice()
    _assert("unified_intelligence" in cognition, "DecisionLoop did not persist unified_intelligence")
    persisted = cognition["unified_intelligence"]
    _assert(
        persisted["self_reference"]["past_system_state_affects_current_reasoning"] is True,
        "DecisionLoop did not carry previous UMIS state into the next cycle",
    )
    _assert(
        persisted["unified_interpretation"]["unified_state_only"] is True,
        "DecisionLoop persisted non-unified interpretation",
    )
    _assert(persisted["closed_loop_market_cognition"] is True, "DecisionLoop did not persist closed-loop cognition")

    print("Unified Market Intelligence Core v1.0 validation PASS")


if __name__ == "__main__":
    main()
