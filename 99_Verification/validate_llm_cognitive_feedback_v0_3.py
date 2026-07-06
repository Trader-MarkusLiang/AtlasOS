"""Validate Atlas Runtime v0.3 LLM cognitive feedback integration."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.decision_validator import validate_decision_packet
from runtime.cognition.llm_cognitive_feedback_engine import (
    apply_pending_feedback_to_fusion,
    check_feedback_stability,
    extract_llm_cognitive_signals,
    run_cognitive_refinement_cycle,
)
from runtime.output_logger import read_runtime_log


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _packet() -> dict:
    return validate_decision_packet(
        {
            "regime_state": "ATTENTION_EXPANSION",
            "confidence": 0.46,
            "risk_level": "medium",
            "attention_state": "rising",
            "liquidity_state": "mixed",
            "causal_summary": "Attention and liquidity divergence requires recalibration.",
            "recommended_action": "observe",
            "reasoning_trace": "Attention narrative is stronger than liquidity confirmation.",
        }
    )


def _cognition() -> dict:
    return {
        "fusion": {
            "proposed_state": "ATTENTION_EXPANSION",
            "attention_pressure": 70,
            "liquidity_condition": "Neutral",
            "liquidity_score": 50,
            "stability_score": 70,
        },
        "causal": {
            "primary_driver": "Attention-Liquidity Divergence",
            "regime_transition_probability": 65,
        },
        "controller": {
            "current_state": "ATTENTION_EXPANSION",
            "proposed_state": "ATTENTION_EXPANSION",
            "transition_allowed": True,
        },
    }


def main() -> None:
    packet = _packet()
    cognition = _cognition()

    feedback = run_cognitive_refinement_cycle(
        decision_packet=packet,
        cognitive_state_snapshot=cognition,
        llm_reasoning_output=packet["reasoning_trace"],
        previous_feedback={},
    )
    modifiers = feedback["modifiers"]
    _assert(feedback["status"] == "applied", "feedback should apply for stable input")
    _assert(
        any(abs(float(value)) > 0 for key, value in modifiers.items() if key.endswith("_delta")),
        "feedback should affect at least one cognitive weight",
    )
    _assert(
        feedback["adjusted_cognition"]["controller"]["current_state"] == cognition["controller"]["current_state"],
        "LLM feedback must not directly set regime label",
    )
    _assert(
        feedback["adjusted_cognition"]["llm_feedback_policy"]["regime_label_override_allowed"] is False,
        "regime label override must remain forbidden",
    )

    signals = [
        extract_llm_cognitive_signals(
            decision_packet=packet,
            cognitive_state_snapshot=cognition,
            llm_reasoning_output=packet["reasoning_trace"],
        )["attention_adjustment_signal"]
        for _ in range(3)
    ]
    _assert(len(set(signals)) > 1, "same input should produce slight bounded feedback variation")

    unstable = check_feedback_stability(
        previous_feedback={
            "llm_signals": {
                "attention_adjustment_signal": 0.08,
                "risk_recalibration_signal": 0.08,
            }
        },
        current_signals={
            "attention_adjustment_signal": -0.08,
            "risk_recalibration_signal": 0.08,
        },
    )
    _assert(unstable["freeze_feedback"] is True, "oscillation should freeze feedback")

    projected = apply_pending_feedback_to_fusion(cognition["fusion"], feedback)
    _assert(projected["proposed_state"] == cognition["fusion"]["proposed_state"], "projection must not relabel state")
    _assert("llm_feedback_projection" in projected, "pending feedback should project onto fusion copy")

    event_fusion_source = (REPO_ROOT / "runtime/cognition/event_fusion_engine.py").read_text(encoding="utf-8")
    _assert("llm_cognitive_feedback" not in event_fusion_source, "Event Fusion logic must remain unchanged")
    contract_source = (REPO_ROOT / "runtime/cognition/decision_contract.py").read_text(encoding="utf-8")
    _assert("validate_decision_packet" in contract_source, "Decision Contract must remain validation-backed")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        daemon_log = str(root / "atlas_runtime.log")
        daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                interval_seconds=10,
                max_cycles=3,
                log_path=daemon_log,
                db_path=str(root / "runtime.sqlite"),
                inbox_dir=str(root / "inbox"),
                no_sleep=True,
            )
        )
        daemon.run_forever()
        records = read_runtime_log(log_path=daemon_log, limit=3)
        _assert(len(records) == 3, "daemon should write three feedback tick logs")
        deltas = []
        for record in records:
            tick = record["cognition_summary"]["tick_result"]
            _assert(tick.get("llm_feedback_status") in {"applied", "frozen"}, "feedback status missing")
            _assert("llm_feedback_freeze" in tick, "feedback freeze flag missing")
            deltas.append(tick.get("llm_feedback_attention_delta"))
        _assert(any(delta is not None for delta in deltas), "runtime example should expose feedback delta")

    print("LLM Cognitive Feedback v0.3 validation PASS")


if __name__ == "__main__":
    main()
