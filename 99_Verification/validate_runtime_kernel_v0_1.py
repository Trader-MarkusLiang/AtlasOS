"""Validate Atlas OS Lightweight Execution Kernel v0.1."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_host import AtlasHost, HostConfig
from runtime.llm_router import supported_models
from runtime.scheduler import event_trigger, intraday_run
from runtime.state_store import StateStore
from web.app import dashboard_payload


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = str(Path(temp_dir) / "runtime_runs.jsonl")
        db_path = str(Path(temp_dir) / "atlas_runtime.sqlite")

        host = AtlasHost(
            HostConfig(
                sleep_interval_seconds=0,
                daily_interval_seconds=0,
                intraday_interval_seconds=0,
                log_path=log_path,
                db_path=db_path,
            )
        )
        host_status = host.run_once()
        _assert(host_status["executed_count"] == 2, "host should execute daily and intraday jobs")

        intraday = intraday_run(log_path=log_path, db_path=db_path)
        _assert(intraday["status"] == "success", "intraday route should succeed")
        _assert(intraday["pipeline"] == "Intraday Runtime Check", "intraday route mismatch")

        event = event_trigger("attention_spike", log_path=log_path, db_path=db_path)
        _assert(event["status"] == "success", "event route should succeed")
        _assert(event["pipeline"] == "Risk Check", "event route mismatch")

        models = supported_models()
        _assert("gpt-5.5" in models, "GPT provider alias missing")
        _assert("claude-sonnet" in models, "Claude provider alias missing")
        _assert(len(models) >= 2, "at least two LLM providers must be supported")

        store = StateStore(db_path=db_path)
        latest = store.get_latest_decision_brief()
        _assert(latest.get("content", "").startswith("# Atlas Decision Brief"), "latest brief missing")
        _assert(store.get_regime_state(), "regime state should persist")
        _assert(store.get_latest_portfolio_snapshot().get("privacy") == "redacted", "portfolio must be redacted")
        _assert(store.get_system_logs(limit=10), "system logs should persist in SQLite")

        log_records = [json.loads(line) for line in Path(log_path).read_text(encoding="utf-8").splitlines()]
        _assert(log_records, "JSONL runtime logs missing")
        _assert(all("decision_brief_id" in record for record in log_records), "brief id missing from logs")
        _assert(all("llm_model_used" in record for record in log_records), "LLM model missing from logs")
        _assert(all("decision_brief" not in record for record in log_records), "logs must not store full brief")

        with sqlite3.connect(db_path) as conn:
            tables = {
                row[0]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            }
        _assert(
            {"kv_state", "decision_briefs", "attention_history", "system_logs"}.issubset(tables),
            "SQLite schema incomplete",
        )

    payload = dashboard_payload()
    _assert("portfolio" in payload, "dashboard portfolio section missing")
    _assert("decision_brief" in payload, "dashboard decision brief section missing")
    _assert("regime_status" in payload, "dashboard regime section missing")
    _assert("attention_signals" in payload, "dashboard attention section missing")
    _assert("system_logs" in payload, "dashboard logs section missing")

    print("Runtime Kernel v0.1 validation PASS")


if __name__ == "__main__":
    main()
