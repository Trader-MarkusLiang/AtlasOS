"""Validate Atlas Runtime v0.4 structural co-evolution layer."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.causal_graph_mutation_engine import mutate_causal_graph
from runtime.cognition.causal_intelligence_layer import market_causal_graph
from runtime.cognition.regime_topology_engine import evolve_regime_topology
from runtime.cognition.structural_drift_controller import apply_structural_drift
from runtime.output_logger import read_runtime_log
from runtime.state_store import StateStore
from runtime.telemetry.state_snapshot import read_cognitive_snapshots


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _latent(attention: int = 78, liquidity_pressure: int = 72, risk: int = 70) -> dict:
    return {
        "latent_variables": {
            "structural_liquidity_pressure": liquidity_pressure,
            "attention_persistence_field": attention,
            "narrative_propagation_inertia": 68,
            "hidden_risk_compression": risk,
            "capital_rotation_tension": 62,
        },
        "regime_attractors": {
            "dominant_attractor_basin": "liquidity_stress_basin",
            "basins": {
                "liquidity_stress_basin": {"attractor_strength": 78, "basin_depth": 72},
                "attention_momentum_basin": {"attractor_strength": 70, "basin_depth": 60},
                "distribution_basin": {"attractor_strength": 67, "basin_depth": 58},
                "stabilization_basin": {"attractor_strength": 42, "basin_depth": 50},
            },
        },
        "phase_space_geometry": {
            "phase_curvature": 64,
            "trajectory_drift_vector": {"attention_liquidity_axis": 18},
        },
    }


def _physics(stability: int = 76, violations: list[str] | None = None) -> dict:
    return {
        "system_stability_report": {
            "stability_score": stability,
            "constraint_violations": violations or [],
        },
        "structural_invariants": {
            "constraint_violations": violations or [],
        },
    }


def _trust(value: float) -> dict:
    return {
        "llm_trust": value,
        "cognitive_trust": value,
        "regime_stability_trust": value,
        "feedback_consistency_trust": value,
        "global_trust_index": value,
    }


def main() -> None:
    graph = market_causal_graph()
    feedback = {"attention": 0.015, "causal": 0.02, "risk": 0.01}

    state = {}
    for _ in range(3):
        mutation = mutate_causal_graph(
            cil_causal_graph=graph,
            latent_structure=_latent(),
            physics_constraints=_physics(),
            trust_score=_trust(0.82),
            feedback_delta=feedback,
            previous_graph_state=state.get("mutation", {}),
        )
        topology = evolve_regime_topology(
            latent_structure=_latent(),
            mutation_state=mutation,
            trust_score=_trust(0.82),
            feedback_delta=feedback,
            previous_topology=state.get("regime_topology", {}),
        )
        state = apply_structural_drift(
            mutated_graph=mutation,
            regime_topology=topology,
            previous_structural_state=state,
            trust_score=_trust(0.82),
        )

    _assert(state["status"] == "applied", "repeated high-trust stress should apply structural drift")
    _assert(state["mutation"]["mutation_intensity"] > 0, "mutation intensity should be positive under high trust")
    _assert(state["mutation"]["structural_shift_index"] > 0, "structural shift should be non-zero")
    _assert(state["graph_node_count"] == len(graph["nodes"]), "graph node count must not expand")
    _assert(state["graph_edge_count"] == len(graph["edges"]), "graph edge count must not expand")
    _assert(state["no_node_creation"] is True, "node creation must remain forbidden")
    _assert(state["no_topology_rewrite"] is True, "topology rewrite must not be applied")
    for value in state["applied_drift"]["edge_weights"].values():
        _assert(abs(value) <= 0.15, "edge drift must remain capped")
    for value in state["applied_drift"]["node_sensitivity"].values():
        _assert(abs(value) <= 0.12, "node sensitivity drift must remain capped")

    low_mutation = mutate_causal_graph(
        cil_causal_graph=graph,
        latent_structure=_latent(),
        physics_constraints=_physics(),
        trust_score=_trust(0.2),
        feedback_delta=feedback,
    )
    low_topology = evolve_regime_topology(
        latent_structure=_latent(),
        mutation_state=low_mutation,
        trust_score=_trust(0.2),
        feedback_delta=feedback,
    )
    low_state = apply_structural_drift(
        mutated_graph=low_mutation,
        regime_topology=low_topology,
        previous_structural_state=state,
        trust_score=_trust(0.2),
    )
    _assert(low_mutation["status"] == "frozen", "low trust should freeze mutation")
    _assert(low_state["status"] == "frozen", "low trust should freeze structural drift")
    _assert(low_state["applied_drift"] == state["applied_drift"], "low trust must preserve previous overlay")

    topology_shift = evolve_regime_topology(
        latent_structure=_latent(attention=88, liquidity_pressure=82),
        mutation_state=mutation,
        trust_score=_trust(0.82),
        feedback_delta=feedback,
    )
    _assert(topology_shift["basin_deformation"] > 0, "attention + liquidity spread should deform basin")
    _assert(topology_shift["transition_barriers"], "transition barriers should be emitted")
    _assert(topology_shift["stability_landscape"]["label_override"] is False, "topology must not relabel regime")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        snapshot_log = str(root / "snapshots.jsonl")
        import os

        old_snapshot = os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG")
        os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = snapshot_log
        try:
            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    interval_seconds=10,
                    max_cycles=3,
                    log_path=str(root / "atlas_runtime.log"),
                    db_path=str(root / "runtime.sqlite"),
                    inbox_dir=str(root / "inbox"),
                    no_sleep=True,
                )
            )
            daemon.run_forever()
            records = read_runtime_log(log_path=str(root / "atlas_runtime.log"), limit=3)
            store = StateStore(db_path=str(root / "runtime.sqlite"))
            structural = store.get_state("structural_coevolution_state")
            snapshots = read_cognitive_snapshots(log_path=snapshot_log, limit=3)
            _assert(len(records) == 3, "daemon should write three runtime ticks")
            _assert(structural.get("bounded") is True, "runtime should persist bounded structural state")
            _assert(structural.get("reversible") is True, "runtime structural state should be reversible")
            _assert(
                any("structural_coevolution_state" in snapshot for snapshot in snapshots),
                "snapshots should expose structural co-evolution state",
            )
        finally:
            if old_snapshot is None:
                os.environ.pop("ATLAS_COGNITIVE_SNAPSHOT_LOG", None)
            else:
                os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = old_snapshot

    forbidden_sources = [
        "runtime/cognition/event_fusion_engine.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/decision_contract.py",
    ]
    for source in forbidden_sources:
        text = (REPO_ROOT / source).read_text(encoding="utf-8")
        _assert("causal_graph_mutation_engine" not in text, f"{source} must not import structural co-evolution")
        _assert("structural_drift_controller" not in text, f"{source} must not import structural drift")

    print("Structural Co-Evolution v0.4 validation PASS")


if __name__ == "__main__":
    main()
