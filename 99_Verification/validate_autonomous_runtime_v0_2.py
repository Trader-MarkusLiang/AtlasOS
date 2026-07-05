"""Validate Atlas OS v0.2 autonomous runtime upgrade."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_machine import (
    STATE_ATTENTION_EXPANSION,
    STATE_RISK_OFF,
)
from runtime.state_store import StateStore
from web.app import dashboard_payload


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "atlas_runtime.sqlite")
        log_path = str(root / "runtime.jsonl")
        inbox_dir = root / "inbox"
        inbox_dir.mkdir()

        event_stream = EventStream(db_path=db_path, inbox_dir=str(inbox_dir))
        event_stream.enqueue_event(
            "attention_spike",
            payload={"theme": "AI infrastructure", "leadership_fragility": "low"},
            source="validation",
        )
        event_stream.enqueue_event(
            "portfolio_drawdown",
            payload={"scope": "redacted", "severity": "high"},
            source="validation",
        )

        loop = DecisionLoop(
            DecisionLoopConfig(
                sleep_interval_seconds=0,
                heartbeat_interval_seconds=999999,
                max_events_per_cycle=1,
                log_path=log_path,
                db_path=db_path,
                inbox_dir=str(inbox_dir),
            )
        )
        first = loop.run_once()
        store = StateStore(db_path=db_path)
        _assert(first["events_processed"] == 1, "first cycle should process one prioritized event")
        _assert(
            store.get_system_state().get("current_state") == STATE_RISK_OFF,
            "portfolio drawdown should transition to RISK_OFF first",
        )

        second = loop.run_once()
        _assert(second["events_processed"] == 1, "second cycle should process next event")
        _assert(
            store.get_system_state().get("current_state") == STATE_ATTENTION_EXPANSION,
            "attention spike should transition to ATTENTION_EXPANSION",
        )

        inbox_event = {
            "event_type": "volume_price_breakout",
            "priority": 80,
            "source": "validation_file",
            "payload": {"ticker": "redacted"},
        }
        (inbox_dir / "events.jsonl").write_text(json.dumps(inbox_event) + "\n", encoding="utf-8")
        third = loop.run_once()
        _assert(third["events_ingested"] == 1, "file listener should ingest inbox events")

        latest_brief = store.get_latest_decision_brief()
        _assert(latest_brief.get("content", "").startswith("# Atlas Decision Brief"), "brief missing")
        _assert(store.get_event_history(limit=10), "event history missing")
        _assert(store.get_state_transitions(limit=10), "state transition history missing")
        _assert(store.get_system_logs(limit=10), "system logs missing")

        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        _assert("events" in tables, "events table missing")
        _assert("state_transitions" in tables, "state transition table missing")

        log_records = [json.loads(line) for line in Path(log_path).read_text(encoding="utf-8").splitlines()]
        _assert(any(record.get("trigger_type") == "decision_loop_cycle" for record in log_records), "loop log missing")
        _assert(all("decision_brief" not in record for record in log_records), "logs must not store full brief")

    payload = dashboard_payload()
    _assert("system_state" in payload, "dashboard system state missing")
    _assert("event_stream" in payload, "dashboard event stream missing")
    _assert("attention_heat_index" in payload, "dashboard attention heat missing")

    llm_direct_refs = []
    for path in (REPO_ROOT / "runtime").glob("*.py"):
        if path.name == "llm_router.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "urlopen(" in text or "api.openai.com" in text or "anthropic.com" in text:
            llm_direct_refs.append(path.name)
    _assert(not llm_direct_refs, f"LLM API calls must go through llm_router only: {llm_direct_refs}")

    plist = REPO_ROOT / "deployment" / "atlas_os.plist"
    _assert(plist.exists(), "launchd plist missing")
    plist_text = plist.read_text(encoding="utf-8")
    _assert("KeepAlive" in plist_text and "RunAtLoad" in plist_text, "launchd restart settings missing")

    print("Autonomous Runtime v0.2 validation PASS")


if __name__ == "__main__":
    main()
