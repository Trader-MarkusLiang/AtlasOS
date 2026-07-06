"""Validate Atlas Runtime v0.3.2 trust calibration layer."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.llm_cognitive_feedback_engine import attach_trust_weighting
from runtime.cognition.system_trust_state import update_system_trust_state
from runtime.cognition.trust_score_engine import compute_trust_score, trust_decay_over_time
from runtime.output_logger import read_runtime_log
from runtime.telemetry.decision_trace_logger import log_decision_trace, read_decision_traces
from runtime.telemetry.llm_trace_logger import log_llm_trace, read_llm_traces
from runtime.telemetry.state_snapshot import read_cognitive_snapshots


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _cognition() -> dict:
    return {
        "fusion": {"stability_score": 78, "stress_score": 20, "proposed_state": "ATTENTION_EXPANSION"},
        "causal": {"primary_driver": "Attention-Liquidity Divergence"},
        "controller": {"current_state": "ATTENTION_EXPANSION", "transition_allowed": True},
        "physics_constraints": {"system_stability_report": {"stability_score": 72}},
    }


def _packet(confidence: float = 0.7, text: str = "Aligned reasoning") -> dict:
    return {
        "regime_state": "ATTENTION_EXPANSION",
        "confidence": confidence,
        "risk_level": "medium",
        "attention_state": "rising",
        "liquidity_state": "mixed",
        "causal_summary": text,
        "recommended_action": "observe",
        "reasoning_trace": text,
    }


def main() -> None:
    cognition = _cognition()
    cognition_before = copy.deepcopy(cognition)
    stable_packet = _packet()
    unstable_packet = _packet(confidence=0.15, text="Guaranteed certain target weight execute")
    small_feedback = {"attention": 0.01, "causal": 0.01, "risk": 0.0}
    large_feedback = {"attention": 0.08, "causal": -0.08, "risk": 0.08}

    stable_score = compute_trust_score(cognition, stable_packet, small_feedback)
    unstable_score = compute_trust_score(cognition, unstable_packet, large_feedback)
    _assert(unstable_score["global_trust_index"] < stable_score["global_trust_index"], "inconsistent LLM output should reduce trust")
    _assert(cognition == cognition_before, "trust score must not mutate cognitive state")

    improved = trust_decay_over_time(
        previous_trust_state={"rolling_trust_index": 0.45},
        current_trust_score=stable_score,
        feedback_delta=small_feedback,
        regime_volatility=0,
    )
    _assert(improved["rolling_trust_index"] > 0.45, "stable repeated alignment should increase rolling trust")

    decayed = update_system_trust_state(
        previous_state={"rolling_trust_index": 0.8, "llm_provider_trust": {"runtime": 0.8}},
        trust_score=stable_score,
        provider="runtime",
        feedback_delta=large_feedback,
        regime_volatility=80,
    )
    _assert(decayed["rolling_trust_index"] < 0.8, "high oscillation / volatility should decay trust")

    feedback = {"modifiers": {"attention_weight_delta": 0.04, "causal_edge_strength_delta": 0.02}}
    annotated = attach_trust_weighting(feedback, stable_score)
    _assert(annotated["modifiers"] == feedback["modifiers"], "trust weighting must not alter feedback delta")
    _assert(annotated["trust_weighting"]["metadata_only"] is True, "trust weighting must be metadata-only")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        llm_log = str(root / "llm.jsonl")
        decision_log = str(root / "decision.jsonl")
        snapshot_log = str(root / "snapshots.jsonl")
        log_llm_trace(
            provider="test",
            model="test-model",
            prompt="same prompt",
            context={"contract_version": "decision_packet_v0.2"},
            output_raw=json.dumps(stable_packet, sort_keys=True),
            latency_ms=1,
            log_path=llm_log,
        )
        log_llm_trace(
            provider="test",
            model="test-model",
            prompt="same prompt",
            context={"contract_version": "decision_packet_v0.2"},
            output_raw=json.dumps(stable_packet, sort_keys=True),
            latency_ms=1,
            log_path=llm_log,
        )
        llm_records = read_llm_traces(log_path=llm_log, limit=2)
        for record in llm_records:
            for key in ("output_stability_score", "hallucination_risk_proxy", "response_consistency_index"):
                _assert(key in record, f"LLM trace missing {key}")

        log_decision_trace(
            tick=0,
            event={"type": "test"},
            regime_state="ATTENTION_EXPANSION",
            attention_state=70,
            causal_summary="test",
            llm_decision_packet=stable_packet,
            feedback_delta=small_feedback,
            calibrated_confidence=0.42,
            confidence_adjustment_factor=0.6,
            log_path=decision_log,
        )
        decision = read_decision_traces(log_path=decision_log, limit=1)[0]
        _assert(decision["calibrated_confidence"] == 0.42, "decision trace calibrated confidence missing")
        _assert(decision["confidence_adjustment_factor"] == 0.6, "decision trace adjustment factor missing")

        old_env = {
            "ATLAS_LLM_TRACE_LOG": os.environ.get("ATLAS_LLM_TRACE_LOG"),
            "ATLAS_DECISION_TRACE_LOG": os.environ.get("ATLAS_DECISION_TRACE_LOG"),
            "ATLAS_COGNITIVE_SNAPSHOT_LOG": os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG"),
        }
        os.environ["ATLAS_LLM_TRACE_LOG"] = str(root / "daemon_llm.jsonl")
        os.environ["ATLAS_DECISION_TRACE_LOG"] = str(root / "daemon_decision.jsonl")
        os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = snapshot_log
        try:
            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    interval_seconds=10,
                    max_cycles=3,
                    log_path=str(root / "runtime.log"),
                    db_path=str(root / "runtime.sqlite"),
                    inbox_dir=str(root / "inbox"),
                    no_sleep=True,
                )
            )
            daemon.run_forever()
            runtime_records = read_runtime_log(log_path=str(root / "runtime.log"), limit=3)
            snapshots = read_cognitive_snapshots(log_path=snapshot_log, limit=3)
            _assert(len(runtime_records) == 3, "daemon should produce three runtime ticks")
            _assert(len(snapshots) == 3, "daemon should produce three trust snapshots")
            _assert(
                all("trust_state" in snapshot and snapshot["trust_state"] for snapshot in snapshots),
                "snapshot should include trust_state",
            )
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    event_fusion_source = (REPO_ROOT / "runtime/cognition/event_fusion_engine.py").read_text(encoding="utf-8")
    _assert("trust_score_engine" not in event_fusion_source, "Event Fusion must not depend on trust calibration")
    decision_contract_source = (REPO_ROOT / "runtime/cognition/decision_contract.py").read_text(encoding="utf-8")
    _assert("DecisionPacket = {" not in decision_contract_source, "Decision Contract structure should not be rewritten")

    print("Trust Calibration v0.3.2 validation PASS")


if __name__ == "__main__":
    main()
