"""Validate Atlas OS v0.4 DSA adapter integration boundary."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.adapter.data_fetch import fetch_market_data
from runtime.adapter.dsa_bridge import normalize_dsa_signal, normalize_external_event
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore
from web.app import dashboard_payload


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_inbox_event(item: dict) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        log_path = str(root / "runtime.jsonl")
        inbox_dir = root / "inbox"
        inbox_dir.mkdir()
        (inbox_dir / "dsa.jsonl").write_text(json.dumps(item, ensure_ascii=False) + "\n", encoding="utf-8")
        loop = DecisionLoop(
            DecisionLoopConfig(
                db_path=db_path,
                log_path=log_path,
                inbox_dir=str(inbox_dir),
                heartbeat_interval_seconds=9999999999,
                max_events_per_cycle=10,
                sleep_interval_seconds=0,
            )
        )
        cycle = loop.run_once()
        store = StateStore(db_path=db_path)
        return {
            "cycle": cycle,
            "system_state": store.get_system_state(),
            "cognition": store.get_state("cognition_state"),
        }


def main() -> None:
    dsa_signal = {
        "type": "social_sentiment",
        "timestamp": int(time.time()),
        "source": "dsa",
        "intensity": 0.82,
        "metadata": {
            "keywords": ["AI", "attention"],
            "evidence_quality": "unclear",
        },
    }
    unified = normalize_dsa_signal(dsa_signal)
    _assert(set(unified.keys()) == {"type", "timestamp", "source", "intensity", "metadata"}, "bad unified schema")
    _assert(unified["type"] == "attention_spike", "DSA social sentiment should map to attention_spike")

    runtime_event = normalize_external_event(dsa_signal)
    _assert(runtime_event["event_type"] == "attention_spike", "runtime event type mismatch")
    _assert(runtime_event["priority"] == 82, "intensity should map to priority")

    native = _run_inbox_event(
        {
            "event_type": "attention_spike",
            "priority": 82,
            "source": "native_test",
            "payload": {"keywords": ["AI", "attention"], "evidence_quality": "unclear"},
        }
    )
    adapted = _run_inbox_event(dsa_signal)
    _assert(native["system_state"]["current_state"] == adapted["system_state"]["current_state"], "DSA/native mismatch")
    _assert(adapted["cycle"]["events_ingested"] == 1, "DSA event should be ingested from inbox")
    _assert(adapted["cycle"]["events_processed"] == 1, "DSA event should be processed")
    _assert(
        "attention_spike" in adapted["cognition"]["fusion"]["source_event_types"],
        "cognition should consume adapted event",
    )

    crash_result = _run_inbox_event(
        {
            "type": "liquidity",
            "timestamp": int(time.time()),
            "source": "dsa",
            "intensity": 0.95,
            "metadata": {"liquidity": "contracting", "keyword": "panic crisis"},
        }
    )
    _assert(crash_result["system_state"]["current_state"] in {"RISK_OFF", "CRASH_STRESS"}, "risk event not routed")

    neutralized = normalize_external_event({"type": "attention", "intensity": 0.9, "metadata": {"buy": "now"}})
    _assert(neutralized["event_type"] == "market_event", "adapter must neutralize DSA trading/business logic")
    _assert("buy" not in neutralized["payload"], "adapter must strip trading fields")

    data_status = fetch_market_data(["GLW"])
    _assert(data_status["status"] == "not_configured", "DSA data fetch should be optional when unavailable")

    dashboard = dashboard_payload()
    _assert("infrastructure" in dashboard, "dashboard infrastructure status missing")
    _assert(dashboard["infrastructure"]["input_router"]["status"] == "available", "input router status missing")

    forbidden_changed = []
    for path in [
        "runtime/cognition/event_fusion_engine.py",
        "runtime/cognition/regime_memory.py",
        "runtime/cognition/causal_inference.py",
        "runtime/cognition/state_controller.py",
    ]:
        if _git_diff_name(path):
            forbidden_changed.append(path)
    _assert(not forbidden_changed, f"cognitive core files changed: {forbidden_changed}")

    print("DSA Adapter v0.4 validation PASS")


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
