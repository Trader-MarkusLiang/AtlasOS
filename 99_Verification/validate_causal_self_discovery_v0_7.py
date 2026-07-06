"""Validate Atlas Runtime v0.7 causal self-discovery layer."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.causal_hypothesis_engine import generate_causal_hypotheses
from runtime.cognition.causal_structure_selector import select_active_causal_structure
from runtime.cognition.explanation_error_engine import compute_multi_explanation_competition
from runtime.cognition.hypothesis_memory import update_hypothesis_memory
from runtime.cognition.hypothesis_scoring_engine import score_causal_hypotheses
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


def _sample_events() -> list[dict]:
    return [
        {
            "event_id": "test-attention",
            "event_type": "attention_spike",
            "priority": 7,
            "source": "validation",
            "payload": {"attention": 82, "narrative": 74},
        },
        {
            "event_id": "test-liquidity",
            "event_type": "liquidity_shock",
            "priority": 8,
            "source": "validation",
            "payload": {"liquidity": 24, "stress": 79},
        },
        {
            "event_id": "test-volatility",
            "event_type": "volatility_spike",
            "priority": 8,
            "source": "validation",
            "payload": {"stress": 83},
        },
    ]


def _sample_lmse() -> dict:
    return {
        "latent_variables": {
            "attention_persistence_field": 78,
            "structural_liquidity_pressure": 28,
            "hidden_risk_compression": 84,
            "narrative_propagation_inertia": 72,
        }
    }


def _manual_scoring(best_id: str) -> dict:
    ids = [
        "H_ATTENTION_FLOW",
        "H_LIQUIDITY_STRESS",
        "H_INSTITUTIONAL_ROTATION",
        "H_NARRATIVE_REFLEXIVITY",
    ]
    ranking = []
    for hid in ids:
        ranking.append({"id": hid, "score": 0.86 if hid == best_id else 0.58})
    ranking.sort(key=lambda item: item["score"], reverse=True)
    return {
        "best_hypothesis_id": ranking[0]["id"],
        "hypothesis_ranking": ranking,
        "score_distribution": {item["id"]: item["score"] for item in ranking},
    }


def main() -> None:
    explanation_errors = [
        {
            "explanation_error_score": 0.42,
            "underestimated_factors": ["Liquidity", "Volatility"],
            "overestimated_factors": ["Attention"],
        }
    ]
    generated = generate_causal_hypotheses(
        event_stream=_sample_events(),
        regime_state="HIGH_VOLATILITY",
        lmse_structure=_sample_lmse(),
        explanation_error_history=explanation_errors,
    )
    hypotheses = generated["hypotheses"]
    _assert(len(hypotheses) >= 3, "must generate at least three causal hypotheses")
    _assert(generated["multiple_explanations"] is True, "hypotheses must be plural by design")
    _assert(all(item.get("not_truth_claim") is True for item in hypotheses), "hypotheses must not be truth claims")

    signatures = {item.get("structural_signature") for item in hypotheses}
    _assert(len(signatures) == len(hypotheses), "hypotheses must differ structurally")
    edge_sets = {
        item["id"]: {
            f"{edge.get('from')}->{edge.get('to')}"
            for edge in item.get("causal_graph_variant", {}).get("edges", [])
        }
        for item in hypotheses
    }
    _assert(len({tuple(sorted(edges)) for edges in edge_sets.values()}) == len(hypotheses), "edge sets must differ")

    scoring = score_causal_hypotheses(
        hypotheses=hypotheses,
        explanation_error_history=explanation_errors,
        regime_state="HIGH_VOLATILITY",
        trust_score=_trust(0.82),
        hypothesis_memory_state={},
    )
    _assert(scoring["best_hypothesis_id"], "scoring must select a best hypothesis id")
    _assert(len(scoring["hypothesis_ranking"]) == len(hypotheses), "scoring must rank all hypotheses")
    _assert(set(scoring["score_distribution"]) == {item["id"] for item in hypotheses}, "score distribution must cover all hypotheses")

    initial = select_active_causal_structure(
        scored_hypotheses=scoring,
        hypotheses=hypotheses,
        previous_selection={},
        trust_score=_trust(0.82),
        regime_state="HIGH_VOLATILITY",
    )
    _assert(initial["active_hypothesis_id"] == scoring["best_hypothesis_id"], "initial selection should choose best hypothesis")
    _assert(initial["non_permanent_selection"] is True, "selection must remain non-permanent")
    _assert(len(initial["shadow_hypotheses"]) >= 2, "shadow hypotheses must be retained")

    switched = select_active_causal_structure(
        scored_hypotheses=_manual_scoring("H_LIQUIDITY_STRESS"),
        hypotheses=hypotheses,
        previous_selection={
            "active_hypothesis_id": "H_ATTENTION_FLOW",
            "active_age": 2,
            "regime_context": "ATTENTION_EXPANSION",
        },
        trust_score=_trust(0.82),
        regime_state="HIGH_VOLATILITY",
    )
    _assert(switched["active_hypothesis_id"] == "H_LIQUIDITY_STRESS", "high-trust regime shift should allow switching")
    _assert(switched["switch_allowed"] is True, "switch should be explicitly allowed")

    held_for_stability = select_active_causal_structure(
        scored_hypotheses=_manual_scoring("H_LIQUIDITY_STRESS"),
        hypotheses=hypotheses,
        previous_selection={
            "active_hypothesis_id": "H_ATTENTION_FLOW",
            "active_age": 0,
            "regime_context": "HIGH_VOLATILITY",
        },
        trust_score=_trust(0.82),
        regime_state="HIGH_VOLATILITY",
    )
    _assert(held_for_stability["active_hypothesis_id"] == "H_ATTENTION_FLOW", "selector must prevent one-tick oscillation")
    _assert(held_for_stability["selection_reason"] == "held_for_stability", "stability hold reason should be visible")

    low_trust = select_active_causal_structure(
        scored_hypotheses=_manual_scoring("H_LIQUIDITY_STRESS"),
        hypotheses=hypotheses,
        previous_selection={
            "active_hypothesis_id": "H_ATTENTION_FLOW",
            "active_age": 5,
            "regime_context": "ATTENTION_EXPANSION",
        },
        trust_score=_trust(0.2),
        regime_state="HIGH_VOLATILITY",
    )
    _assert(low_trust["active_hypothesis_id"] == "H_ATTENTION_FLOW", "low trust must reduce switching frequency")
    _assert(low_trust["trust_gate"] == "reduced_switching", "low trust gate should be explicit")
    _assert(low_trust["switch_allowed"] is False, "low trust must block switching")

    competition = compute_multi_explanation_competition(
        explanations=[
            {
                "causal_summary": item["id"],
                "reasoning_trace": " ".join(item.get("structural_assumptions", [])),
            }
            for item in hypotheses
        ],
        causal_graph_variants=[item["causal_graph_variant"] for item in hypotheses],
    )
    _assert(competition["multi_explanation_count"] == len(hypotheses), "competition layer must inspect all hypotheses")
    _assert(competition["structural_divergence_index"] > 0, "structural divergence must be measurable")
    _assert(competition["causal_conflict_score"] >= 0, "conflict score must be bounded metadata")

    memory = update_hypothesis_memory(
        previous_memory={},
        selection_state=switched,
        scored_hypotheses=_manual_scoring("H_LIQUIDITY_STRESS"),
        regime_state="HIGH_VOLATILITY",
        explanation_error=explanation_errors[-1],
    )
    _assert(memory["active_hypothesis_id"] == "H_LIQUIDITY_STRESS", "memory should persist active hypothesis")
    _assert(memory["history"], "memory should append selection history")
    _assert(memory["shadow_state_retained"] is True, "memory should retain shadow-state semantics")

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
        hypothesis_memory = store.get_state("causal_hypothesis_memory")
        _assert(len(records) == 3, "daemon should write three runtime ticks")
        _assert(cognition.get("causal_hypotheses", {}).get("hypothesis_count", 0) >= 3, "runtime should persist hypotheses")
        _assert("hypothesis_scoring" in cognition, "runtime should persist hypothesis scoring")
        _assert("active_causal_structure" in cognition, "runtime should persist active causal structure")
        _assert("multi_explanation_competition" in cognition, "runtime should persist competition metrics")
        _assert(hypothesis_memory.get("history"), "runtime should persist hypothesis memory")

    forbidden_sources = [
        "runtime/cognition/event_fusion_engine.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/market_law_emergence_engine.py",
        "runtime/cognition/decision_contract.py",
    ]
    forbidden_imports = [
        "causal_hypothesis_engine",
        "hypothesis_scoring_engine",
        "causal_structure_selector",
        "hypothesis_memory",
    ]
    for source in forbidden_sources:
        text = (REPO_ROOT / source).read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            _assert(forbidden not in text, f"{source} must not import {forbidden}")

    print("Causal Self-Discovery v0.7 validation PASS")


if __name__ == "__main__":
    main()
