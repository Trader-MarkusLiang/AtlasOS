"""Validate Atlas OS v0.6 Market World Model behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
from runtime.cognition.world_model_engine import (
    attention_to_liquidity,
    build_market_state,
    market_state_space_definition,
    simulate_counterfactual_market,
    simulate_market_world_model,
    simulate_regime_emergence,
    state_transition,
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
                source=event.get("source", "v0.6_validation"),
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
    state_space = market_state_space_definition()
    _assert(state_space["state_type"] == "continuous_market_state", "state space must be continuous")
    for field in (
        "attention_field",
        "liquidity_field",
        "volatility_field",
        "narrative_field",
        "institutional_flow_field",
        "retail_flow_field",
    ):
        _assert(field in state_space["fields"], f"missing state field: {field}")

    fusion = {
        "attention_pressure": 88,
        "liquidity_score": 32,
        "volatility_regime": "High",
        "narrative_intensity": 78,
        "stress_score": 65,
        "proposed_state": "ATTENTION_EXPANSION",
    }
    causal = infer_causal_intelligence(
        fusion=fusion,
        attention_liquidity={"attention_index": 88, "liquidity_index": 32},
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    base_state = build_market_state(
        fusion=fusion,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
    )
    trajectory = [base_state]
    current = base_state
    for _ in range(3):
        current = state_transition(
            current,
            causal_constraints=causal,
            external_shocks={"attention_shock": 88, "stress_shock": 65, "narrative_shock": 78},
        )
        trajectory.append(current)
    _assert(len(trajectory) == 4, "3-step simulation should include t0 through t3")
    _assert(
        len({state["liquidity_field"] for state in trajectory}) > 1
        or len({state["volatility_field"] for state in trajectory}) > 1,
        "market state did not evolve over time",
    )
    _assert(all(state["state_type"] == "continuous_market_state" for state in trajectory), "bad state type")

    high_liquidity = attention_to_liquidity(
        attention_field=85,
        liquidity_field=80,
        narrative_credibility=70,
        institutional_participation=75,
        market_regime="NORMAL",
    )
    low_liquidity = attention_to_liquidity(
        attention_field=85,
        liquidity_field=25,
        narrative_credibility=70,
        institutional_participation=25,
        market_regime="RISK_OFF",
    )
    _assert(
        high_liquidity["efficiency_score"] > low_liquidity["efficiency_score"],
        "attention conversion should differ by liquidity context",
    )
    _assert(high_liquidity["delay_factor"] < low_liquidity["delay_factor"], "delay should rise in weak liquidity")

    world_model = simulate_market_world_model(
        fusion=fusion,
        causal=causal,
        memory_summary={"dominant_state": "HIGH_VOLATILITY"},
        steps=3,
    )
    _assert(world_model["not_forecast"] is True, "world model must not present as forecast")
    _assert(world_model["no_trade_action"] is True, "world model must not contain trade action")
    _assert(len(world_model["baseline_trajectory"]) == 4, "baseline path missing 3-step evolution")
    _assert(
        set(world_model["scenario_paths"]) >= {"baseline", "without_attention_spike", "without_liquidity_shock"},
        "multiple scenario paths missing",
    )

    emergence = simulate_regime_emergence(world_model["baseline_trajectory"])
    _assert(emergence["regime_is_emergent"] is True, "regime must be emergent")
    _assert(emergence["final_label_only"] is False, "regime emergence must not be label-only")
    _assert(emergence["phase_transition_likelihood"] >= 0, "phase transition likelihood missing")
    _assert(emergence["structural_imbalance_fields"], "structural imbalance missing")

    counterfactual = simulate_counterfactual_market(
        base_state=base_state,
        causal_constraints=causal,
        external_shocks={"attention_shock": 88, "stress_shock": 65, "narrative_shock": 78},
        remove_variable="attention_spike",
        steps=3,
    )
    _assert(counterfactual["divergence_score"] > 0, "counterfactual should diverge from baseline")
    _assert(counterfactual["regime_sensitivity_index"] > 0, "sensitivity should be nonzero")

    cognition = _run_loop_once(
        [
            {
                "event_type": "attention_spike",
                "priority": 88,
                "payload": {"attention": "exploding", "retail_attention": "dominant"},
            },
            {
                "event_type": "liquidity_shock",
                "priority": 86,
                "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
            },
        ]
    )
    _assert("world_model" in cognition, "DecisionLoop did not persist world_model")
    persisted = cognition["world_model"]
    _assert(persisted["simulation_mode"] == "interpretable_deterministic_scenario", "bad simulation mode")
    _assert(persisted["regime_emergence_dynamics"]["regime_is_emergent"], "persisted emergence missing")
    _assert(persisted["counterfactuals"]["remove_attention_spike"]["divergence_score"] > 0, "persisted counterfactual missing")

    print("Market World Model v0.6 validation PASS")


if __name__ == "__main__":
    main()
