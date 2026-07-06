"""Validate Atlas Runtime v0.2 Decision Contract + LLM Router boundary."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.decision_contract import parse_decision_packet
from runtime.cognition.decision_validator import (
    DecisionPacketValidationError,
    validate_decision_packet,
)
from runtime.llm_router import call_llm_raw
from runtime.output_logger import read_runtime_log
from runtime.orchestrator import run_state_runtime


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _valid_packet() -> dict:
    return {
        "regime_state": "ATTENTION_EXPANSION",
        "confidence": 0.42,
        "risk_level": "medium",
        "attention_state": "rising",
        "liquidity_state": "mixed",
        "causal_summary": "Attention is rising while liquidity confirmation is incomplete.",
        "recommended_action": "observe",
        "reasoning_trace": "Contract-only runtime reasoning.",
    }


def main() -> None:
    packet = validate_decision_packet(_valid_packet())
    _assert(set(packet) == set(_valid_packet()), "validated packet should preserve exact schema")

    hallucinated = dict(_valid_packet())
    hallucinated["target_weight"] = 0.3
    try:
        validate_decision_packet(hallucinated)
    except DecisionPacketValidationError:
        pass
    else:
        raise AssertionError("hallucinated fields must be rejected")

    malformed = parse_decision_packet('{"recommended_action": "observe"}')
    _assert(malformed["recommended_action"] == "neutral", "malformed LLM output must fail safe")
    _assert(malformed["risk_level"] == "unknown", "failsafe risk must be unknown")
    _assert(malformed["confidence"] == 0.0, "failsafe confidence must be 0.0")

    old_ollama_host = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = "http://127.0.0.1:9"
    try:
        for model in ("gpt-5.5", "claude-sonnet", "ollama"):
            raw = call_llm_raw(model, "Return DecisionPacket JSON.", {"test": "provider_swap"})
            _assert(isinstance(raw, str), f"{model} router output must be raw text")
            parsed = parse_decision_packet(raw)
            _assert(set(parsed) == set(_valid_packet()), f"{model} output schema mismatch")
    finally:
        if old_ollama_host is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = old_ollama_host

    decision_loop_source = (REPO_ROOT / "runtime/decision_loop.py").read_text(encoding="utf-8")
    _assert("from runtime.llm_router" not in decision_loop_source, "DecisionLoop must not import llm_router")
    _assert("call_llm_raw(" not in decision_loop_source, "DecisionLoop must not call LLM directly")
    _assert("call_llm(" not in decision_loop_source, "DecisionLoop must not call LLM directly")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        event = {
            "event_id": "validation:fused",
            "event_type": "fused_market_reality",
            "priority": 80,
            "payload": {
                "cognition": {
                    "fusion": {
                        "proposed_state": "ATTENTION_EXPANSION",
                        "attention_pressure": 85,
                        "liquidity_condition": "mixed",
                    },
                    "causal": {
                        "primary_driver": "Attention-Liquidity Divergence",
                        "attention_meaning": "retail narrative attention",
                    },
                    "controller": {
                        "current_state": "ATTENTION_EXPANSION",
                        "proposed_state": "ATTENTION_EXPANSION",
                        "transition_allowed": True,
                    },
                }
            },
            "source": "validation",
            "created_at": "2026-07-06T00:00:00+00:00",
        }
        result = run_state_runtime(
            system_state="ATTENTION_EXPANSION",
            event=event,
            log_path=str(root / "runtime_runs.jsonl"),
            db_path=str(root / "runtime.sqlite"),
            llm_model="gpt-5.5",
        )
        decision_packet = result["decision_packet"]
        _assert(set(decision_packet) == set(_valid_packet()), "run_state_runtime must return DecisionPacket")
        _assert(result["status"] == "success", "LLM failure must not crash runtime route")

        daemon_log = str(root / "atlas_runtime.log")
        daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                interval_seconds=10,
                max_cycles=3,
                log_path=daemon_log,
                db_path=str(root / "daemon.sqlite"),
                inbox_dir=str(root / "inbox"),
                no_sleep=True,
            )
        )
        daemon.run_forever()
        records = read_runtime_log(log_path=daemon_log, limit=3)
        _assert(len(records) == 3, "daemon should write three v0.2 contract tick logs")
        for record in records:
            tick_result = record["cognition_summary"]["tick_result"]
            _assert(record["system_metrics"]["status"] == "success", "daemon tick should succeed")
            _assert(tick_result.get("decision_packet_action") in {"neutral", "observe", "reduce"}, "packet action missing")
            _assert("decision_packet_confidence" in tick_result, "packet confidence missing")

    print("Decision Contract + LLM Router v0.2 validation PASS")


if __name__ == "__main__":
    main()
