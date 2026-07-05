"""Validate Atlas OS v0.3 cognitive runtime layer."""

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
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_cycle(events: list[tuple[str, int, dict]], db_path: str, log_path: str, inbox_dir: str) -> dict:
    stream = EventStream(db_path=db_path, inbox_dir=inbox_dir)
    for event_type, priority, payload in events:
        stream.enqueue_event(event_type, priority=priority, payload=payload, source="v0.3_validation")
    loop = DecisionLoop(
        DecisionLoopConfig(
            db_path=db_path,
            log_path=log_path,
            inbox_dir=inbox_dir,
            heartbeat_interval_seconds=999999,
            max_events_per_cycle=10,
            sleep_interval_seconds=0,
        )
    )
    return loop.run_once()


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        log_path = str(root / "runtime.jsonl")
        inbox_dir = str(root / "inbox")

        crash_events = [
            ("market_anomaly", 90, {"index_drop_2h": -5, "volume": "panic_high", "liquidity": "contracting"}),
            ("volatility_spike", 85, {"volatility": "spike"}),
            ("attention_spike", 70, {"keywords": ["暴跌", "流动性危机", "外资撤离"], "attention": "exploding"}),
            ("news_narrative_spike", 65, {"news_sentiment": "extreme_negative"}),
        ]
        crash_cycle = _run_cycle(crash_events, db_path, log_path, inbox_dir)
        store = StateStore(db_path=db_path)
        crash_state = store.get_system_state()
        cognition = store.get_state("cognition_state")

        _assert(crash_cycle["events_processed"] == 1, "multiple events should fuse into one cognition cycle")
        _assert(crash_cycle["raw_events_processed"] >= 4, "raw events should be preserved before fusion")
        _assert(crash_state["current_state"] == "CRASH_STRESS", "crash must become CRASH_STRESS")
        _assert(
            cognition["fusion"]["liquidity_condition"] == "Liquidity Shock",
            "liquidity condition should identify shock",
        )
        _assert(
            cognition["fusion"]["attention_pressure"] >= 70,
            "attention pressure should remain visible inside fused state",
        )
        _assert(
            cognition["causal"]["primary_driver"] == "Liquidity Stress",
            "causal inference should identify liquidity stress as primary driver",
        )

        attention_after_crash = [
            ("attention_spike", 70, {"sector": "AI_semiconductor", "retail_attention": "dominant"}),
        ]
        second_cycle = _run_cycle(attention_after_crash, db_path, log_path, inbox_dir)
        after_crash_state = store.get_system_state()
        _assert(second_cycle["events_processed"] == 1, "second cycle should process fused attention event")
        _assert(
            after_crash_state["current_state"] == "CRASH_STRESS",
            "crash memory should block attention overwrite",
        )
        _assert(
            after_crash_state["transition_allowed"] is False,
            "attention overwrite should be rejected by state controller",
        )
        _assert(
            store.get_state("regime_memory")["summary"]["dominant_state"] == "CRASH_STRESS",
            "regime memory should persist crash dominance",
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        fresh_db_path = str(root / "fresh.sqlite")
        log_path = str(root / "fresh.jsonl")
        inbox_dir = str(root / "fresh_inbox")
        fresh_attention = [
            ("attention_spike", 70, {"sector": "AI_semiconductor", "retail_attention": "dominant"}),
        ]
        _run_cycle(fresh_attention, fresh_db_path, log_path, inbox_dir)
        fresh_state = StateStore(db_path=fresh_db_path).get_system_state()
        _assert(
            fresh_state["current_state"] == "ATTENTION_EXPANSION",
            "same attention event should become ATTENTION_EXPANSION without crash memory",
        )

        with sqlite3.connect(fresh_db_path) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        _assert("state_transitions" in tables, "state transition history must remain available")

    changed_forbidden = []
    for forbidden in ["runtime/atlas_host.py", "runtime/atlas_daemon.py", "runtime/scheduler.py"]:
        diff = _git_diff_name(forbidden)
        if diff:
            changed_forbidden.append(forbidden)
    _assert(not changed_forbidden, f"forbidden runtime host/scheduler files changed: {changed_forbidden}")

    print("Cognitive Runtime v0.3 validation PASS")


def _git_diff_name(path: str) -> bool:
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", "--", path],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


if __name__ == "__main__":
    main()
