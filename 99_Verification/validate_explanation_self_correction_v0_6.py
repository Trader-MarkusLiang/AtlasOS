"""Validate Atlas Runtime v0.6 explanation-driven self-correction."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.causal_intelligence_layer import market_causal_graph
from runtime.cognition.causal_self_correction_engine import apply_causal_self_correction
from runtime.cognition.explanation_error_engine import compute_explanation_error
from runtime.cognition.regime_explanation_alignment import align_regime_explanation
from runtime.cognition.structural_drift_controller import apply_structural_drift
from runtime.cognition.structural_evolution_controller import apply_structural_evolution
from runtime.output_logger import read_runtime_log
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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
    weak_explanation = {
        "causal_summary": "Attention narrative dominates.",
        "reasoning_trace": "Retail attention is the main visible force.",
        "risk_level": "medium",
    }
    actual = {
        "state": "HIGH_VOLATILITY",
        "fusion": {
            "attention_pressure": 72,
            "liquidity_score": 24,
            "stress_score": 82,
            "narrative_intensity": 68,
            "volatility_regime": "High",
        },
        "transition": {"current_state": "HIGH_VOLATILITY", "proposed_state": "HIGH_VOLATILITY"},
    }
    causal_prediction = {
        "causal_graph": graph,
        "primary_driver": "Attention pressure",
        "secondary_driver": "Retail Flow",
        "market_pressure_source": "Narrative Pressure",
    }
    error = compute_explanation_error(
        decision_explanation=weak_explanation,
        actual_outcome_state=actual,
        causal_graph_prediction=causal_prediction,
        observed_result={"state": "HIGH_VOLATILITY", "liquidity": 24, "stress": 82, "volatility": "High"},
    )
    _assert(error["explanation_error_score"] > 0, "wrong explanation should produce non-zero error")
    _assert("Liquidity" in error["underestimated_factors"], "liquidity mismatch should be underestimated")
    _assert("Volatility" in error["underestimated_factors"], "volatility mismatch should be underestimated")

    alignment = align_regime_explanation(
        regime_label="HIGH_VOLATILITY",
        decision_explanation=weak_explanation,
        causal_model=causal_prediction,
        actual_outcome_state={"state": "HIGH_VOLATILITY"},
    )
    _assert(alignment["alignment_score"] < 1.0, "weak explanation should not fully align")
    _assert(alignment["label_override"] is False, "alignment must not override regime label")

    correction = apply_causal_self_correction(
        explanation_error=error,
        causal_graph=graph,
        trust_score=_trust(0.82),
        regime_alignment=alignment,
    )
    _assert(correction["status"] in {"applied", "stable"}, "high trust correction should run")
    _assert(correction["edge_weight_updates"], "mismatch should adjust edge weights")
    _assert(correction["known_edges_only"] is True, "correction must use known causal edges only")
    _assert(correction["node_creation_allowed"] is False, "node creation must stay forbidden")
    for value in correction["edge_weight_updates"].values():
        _assert(abs(value) <= 0.035, "edge correction must remain capped")

    frozen = apply_causal_self_correction(
        explanation_error=error,
        causal_graph=graph,
        trust_score=_trust(0.2),
        regime_alignment=alignment,
        previous_correction=correction,
    )
    _assert(frozen["status"] == "frozen", "low trust should freeze causal correction")
    _assert(frozen["edge_weight_updates"] == {}, "low trust must not adjust edges")

    mutated = {
        "status": "proposed",
        "edge_weight_updates": {},
        "node_sensitivity_updates": {},
        "structural_shift_index": 0.0,
        "mutation_intensity": 0.0,
        "global_trust_index": 0.82,
        "graph_node_count": len(graph["nodes"]),
        "graph_edge_count": len(graph["edges"]),
        "topology_rewrite_applied": False,
        "node_creation_allowed": False,
    }
    topology = {
        "attractor_shift": 0.01,
        "basin_deformation": 0.01,
        "transition_barriers": {},
        "stability_landscape": {},
    }
    drift = apply_structural_drift(
        mutated_graph=mutated,
        regime_topology=topology,
        trust_score=_trust(0.82),
        explanation_correction=correction,
    )
    _assert(drift["status"] == "applied", "explanation correction should be accepted under trust")
    _assert(drift["explanation_feedback"]["applied"] is True, "drift should record explanation feedback")
    _assert(drift["applied_drift"]["edge_weights"], "explanation correction should update edge drift")

    low_drift = apply_structural_drift(
        mutated_graph=mutated,
        regime_topology=topology,
        previous_structural_state=drift,
        trust_score=_trust(0.2),
        explanation_correction=correction,
    )
    _assert(low_drift["status"] == "frozen", "low trust should freeze structural drift")
    _assert(
        low_drift["applied_drift"] == drift["applied_drift"],
        "low trust must preserve previous structural overlay",
    )

    evolved = apply_structural_evolution(
        proposed={"causal_reweight_delta": {}},
        trust_field_state={
            "trust_field": {"causal": 0.8, "regime": 0.8, "feedback": 0.8},
            "trust_field_evolution": 0.02,
        },
        explanation_feedback=correction,
    )
    _assert(evolved["explanation_feedback_applied"] is True, "structural evolution should accept explanation feedback")
    _assert(evolved["causal_reweight_delta"], "structural evolution should include explanation-driven causal delta")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
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
        cognition = store.get_state("cognition_state")
        structural = store.get_state("structural_coevolution_state")
        _assert(len(records) == 3, "daemon should write three runtime ticks")
        _assert("explanation_error" in cognition, "runtime cognition should persist explanation error")
        _assert("causal_self_correction" in cognition, "runtime cognition should persist causal self-correction")
        _assert("regime_explanation_alignment" in cognition, "runtime cognition should persist regime alignment")
        _assert("explanation_feedback" in structural, "structural state should persist explanation feedback")

    forbidden_sources = [
        "runtime/cognition/event_fusion_engine.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/market_law_emergence_engine.py",
        "runtime/cognition/decision_contract.py",
    ]
    for source in forbidden_sources:
        text = (REPO_ROOT / source).read_text(encoding="utf-8")
        _assert("explanation_error_engine" not in text, f"{source} must not import explanation error engine")
        _assert("causal_self_correction_engine" not in text, f"{source} must not import self-correction engine")

    print("Explanation Self-Correction v0.6 validation PASS")


if __name__ == "__main__":
    main()

