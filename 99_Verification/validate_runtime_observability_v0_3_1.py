"""Validate Atlas Runtime v0.3.1 observability layer."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.output_logger import read_runtime_log
from runtime.telemetry.decision_trace_logger import read_decision_traces
from runtime.telemetry.llm_trace_logger import read_llm_traces
from runtime.telemetry.replay_engine import replay_tick_sequence
from runtime.telemetry.state_snapshot import read_cognitive_snapshots
from web.dashboard_observability import dashboard_payload, replay_payload


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        runtime_log = str(root / "atlas_runtime.log")
        llm_trace_log = str(root / "llm_traces.jsonl")
        decision_trace_log = str(root / "decision_traces.jsonl")
        snapshot_log = str(root / "cognitive_snapshots.jsonl")
        old_env = {
            "ATLAS_LLM_TRACE_LOG": os.environ.get("ATLAS_LLM_TRACE_LOG"),
            "ATLAS_DECISION_TRACE_LOG": os.environ.get("ATLAS_DECISION_TRACE_LOG"),
            "ATLAS_COGNITIVE_SNAPSHOT_LOG": os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG"),
        }
        os.environ["ATLAS_LLM_TRACE_LOG"] = llm_trace_log
        os.environ["ATLAS_DECISION_TRACE_LOG"] = decision_trace_log
        os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = snapshot_log
        try:
            started = time.time()
            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    interval_seconds=10,
                    max_cycles=3,
                    log_path=runtime_log,
                    db_path=str(root / "runtime.sqlite"),
                    inbox_dir=str(root / "inbox"),
                    no_sleep=True,
                )
            )
            daemon.run_forever()
            elapsed_ms = int((time.time() - started) * 1000)

            runtime_records = read_runtime_log(log_path=runtime_log, limit=3)
            llm_traces = read_llm_traces(log_path=llm_trace_log, limit=10)
            decision_traces = read_decision_traces(log_path=decision_trace_log, limit=10)
            snapshots = read_cognitive_snapshots(log_path=snapshot_log, limit=10)

            _assert(len(runtime_records) == 3, "runtime should produce three logs")
            _assert(len(llm_traces) >= 3, "each LLM call should appear in telemetry log")
            _assert(len(decision_traces) == 3, "each tick should produce one decision trace")
            _assert(len(snapshots) == 3, "each tick should produce one cognitive snapshot")
            for trace in llm_traces[-3:]:
                for key in (
                    "timestamp",
                    "provider",
                    "model",
                    "prompt_hash",
                    "input_summary",
                    "output_raw",
                    "latency_ms",
                    "decision_packet_id",
                    "feedback_applied",
                ):
                    _assert(key in trace, f"LLM trace missing {key}")
                _assert("sk-" not in trace["output_raw"], "LLM trace must not expose raw API key pattern")

            for index, decision in enumerate(decision_traces):
                runtime_record = runtime_records[index]
                _assert(decision["tick"] == runtime_record["system_metrics"]["tick_index"], "tick mismatch")
                _assert(
                    decision["regime_state"] == runtime_record["regime_state"]["system_state"],
                    "observability changed or mismatched regime state",
                )
                _assert(
                    decision["causal_summary"]
                    == runtime_record["cognition_summary"]["causal"].get("primary_driver", "Unknown"),
                    "observability changed or mismatched causal output",
                )

            replay = replay_tick_sequence(
                0,
                2,
                decision_trace_path=decision_trace_log,
                snapshot_path=snapshot_log,
                llm_trace_path=llm_trace_log,
            )
            _assert(replay["tick_count"] == 3, "replay should reconstruct three ticks")
            _assert(all(item["snapshot_match"] for item in replay["replayed_ticks"]), "replay should match snapshots")

            dashboard = dashboard_payload(limit=3)
            _assert(len(dashboard["tick_timeline"]) == 3, "dashboard timeline should expose three ticks")
            _assert("feedback_delta_heatmap" in dashboard, "dashboard should expose feedback heatmap")
            replay_view = replay_payload(0, 2)
            _assert(replay_view["tick_count"] == 3, "dashboard replay endpoint should reconstruct three ticks")

            event_fusion_source = (REPO_ROOT / "runtime/cognition/event_fusion_engine.py").read_text(encoding="utf-8")
            _assert("runtime.telemetry" not in event_fusion_source, "Event Fusion must not import telemetry")
            contract_source = (REPO_ROOT / "runtime/cognition/decision_contract.py").read_text(encoding="utf-8")
            _assert("contract_version\": \"decision_packet_v0.2" in contract_source, "Decision Contract semantics changed")
            _assert(elapsed_ms < 10000, "observability logging should not block runtime loop")
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    print("Runtime Observability v0.3.1 validation PASS")


if __name__ == "__main__":
    main()
