"""Validate Atlas OS UI Runtime Server v0.1."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.output_logger import read_runtime_log
from runtime.state_store import StateStore
from runtime.telemetry.replay_engine import replay_tick_sequence
from runtime.telemetry.state_snapshot import read_cognitive_snapshots
from ui.app_server import _StdlibHandler


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        ui_inbox = root / "runtime" / "inbox" / "user_event.jsonl"
        db_path = root / "runtime.sqlite"
        runtime_log = root / "runtime.log"
        snapshot_log = root / "snapshots.jsonl"
        decision_log = root / "decision.jsonl"
        llm_log = root / "llm.jsonl"
        ui_config = root / "ui_config.json"
        pid_file = root / "ui.pid"
        old_env = {
            "ATLAS_UI_INBOX": os.environ.get("ATLAS_UI_INBOX"),
            "ATLAS_UI_DB_PATH": os.environ.get("ATLAS_UI_DB_PATH"),
            "ATLAS_RUNTIME_LOG": os.environ.get("ATLAS_RUNTIME_LOG"),
            "ATLAS_COGNITIVE_SNAPSHOT_LOG": os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG"),
            "ATLAS_DECISION_TRACE_LOG": os.environ.get("ATLAS_DECISION_TRACE_LOG"),
            "ATLAS_LLM_TRACE_LOG": os.environ.get("ATLAS_LLM_TRACE_LOG"),
            "ATLAS_UI_CONFIG": os.environ.get("ATLAS_UI_CONFIG"),
            "ATLAS_UI_PID_FILE": os.environ.get("ATLAS_UI_PID_FILE"),
        }
        os.environ["ATLAS_UI_INBOX"] = str(ui_inbox)
        os.environ["ATLAS_UI_DB_PATH"] = str(db_path)
        os.environ["ATLAS_RUNTIME_LOG"] = str(runtime_log)
        os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = str(snapshot_log)
        os.environ["ATLAS_DECISION_TRACE_LOG"] = str(decision_log)
        os.environ["ATLAS_LLM_TRACE_LOG"] = str(llm_log)
        os.environ["ATLAS_UI_CONFIG"] = str(ui_config)
        os.environ["ATLAS_UI_PID_FILE"] = str(pid_file)

        server = ThreadingHTTPServer(("127.0.0.1", 0), _StdlibHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            chat_body = urlencode({"message": "What is the current regime and trust state?"}).encode("utf-8")
            chat_response = _request_json(
                Request(
                    f"{base_url}/chat/send",
                    data=chat_body,
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    method="POST",
                )
            )
            _assert(chat_response["status"] == "queued", "chat endpoint should queue user input")
            _assert(ui_inbox.exists(), "chat endpoint should write runtime/inbox/user_event.jsonl")
            lines = ui_inbox.read_text(encoding="utf-8").splitlines()
            _assert(lines, "ui inbox should contain one JSONL event")
            event = json.loads(lines[-1])
            _assert(event["type"] == "user_query", "chat event should use required type")
            _assert(event["source"] == "ui_chat", "chat event should use required source")

            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    interval_seconds=10,
                    max_cycles=3,
                    log_path=str(runtime_log),
                    db_path=str(db_path),
                    inbox_dir=str(root / "events"),
                    ui_inbox_path=str(ui_inbox),
                    no_sleep=True,
                )
            )
            daemon.run_forever()
            records = read_runtime_log(log_path=str(runtime_log), limit=20)
            tick_records = [record for record in records if isinstance(record.get("system_metrics"), dict)]
            _assert(len(tick_records) == 3, "daemon should produce three runtime cycles")
            _assert(tick_records[0]["system_metrics"]["ui_events_ingested"] == 1, "daemon should ingest chat event")
            history = StateStore(db_path=str(db_path)).get_event_history(limit=20)
            _assert(any(item.get("event_type") == "user_input_event" for item in history), "chat should appear in event stream")

            state = _request_json(Request(f"{base_url}/state"))
            snapshots = read_cognitive_snapshots(log_path=str(snapshot_log), limit=3)
            latest_snapshot = snapshots[-1]
            _assert(state["regime_state"] == latest_snapshot["system_state"].get("current_state"), "/state should match snapshot regime")
            _assert("structural_coevolution_state" in state, "/state should include structural co-evolution")
            _assert("last_decision_packet" in state, "/state should include last DecisionPacket")
            _assert("llm_trace_summary" in state, "/state should include LLM trace summary")

            replay_http = _request_json(Request(f"{base_url}/replay?start_tick=0&end_tick=2&format=json"))
            replay_direct = replay_tick_sequence(
                0,
                2,
                decision_trace_path=str(decision_log),
                snapshot_path=str(snapshot_log),
                llm_trace_path=str(llm_log),
            )
            _assert(
                len(replay_http["decision_timeline"]) == replay_direct["tick_count"],
                "replay endpoint should match stored telemetry replay",
            )

            interval_response = _request_json(
                Request(
                    f"{base_url}/control/set_interval",
                    data=urlencode({"interval_seconds": 30}).encode("utf-8"),
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    method="POST",
                )
            )
            provider_response = _request_json(
                Request(
                    f"{base_url}/control/set_llm_provider",
                    data=urlencode({"provider": "runtime", "model": "gpt-5.5"}).encode("utf-8"),
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    method="POST",
                )
            )
            _assert(interval_response["tick_interval_seconds"] == 30, "control interval should write config")
            _assert(provider_response["read_only_config"] is True, "LLM provider control should be config-only")
        finally:
            server.shutdown()
            server.server_close()
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    for source in [REPO_ROOT / "ui/app_server.py", *sorted((REPO_ROOT / "ui").glob("*.py"))]:
        text = source.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{source.name} must not import cognition modules")
        for forbidden in ("mutate_causal_graph", "apply_structural_drift", "run_self_organization_cycle"):
            _assert(forbidden not in text, f"{source.name} must not call {forbidden}")

    forbidden_core_files = [
        "runtime/cognition/causal_intelligence_layer.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/market_law_emergence_engine.py",
        "runtime/cognition/unified_market_intelligence_core.py",
        "runtime/cognition/self_organizing_engine.py",
        "runtime/cognition/decision_contract.py",
    ]
    for relative in forbidden_core_files:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        _assert("app_server" not in text, f"{relative} must not depend on UI server")

    print("UI Runtime Server v0.1 validation PASS")


def _request_json(request: Request) -> dict:
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
