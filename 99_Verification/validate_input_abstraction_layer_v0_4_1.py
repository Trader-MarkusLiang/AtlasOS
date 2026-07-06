"""Validate Atlas OS v0.4.1 Input Abstraction Layer decoupling."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.adapter.input_router import route_input, route_to_runtime_event
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_events(events: list[dict], use_inbox: bool = False) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = str(root / "state.sqlite")
        log_path = str(root / "runtime.jsonl")
        inbox_dir = root / "inbox"
        inbox_dir.mkdir()
        if use_inbox:
            (inbox_dir / "events.jsonl").write_text(
                "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
                encoding="utf-8",
            )
        else:
            stream = EventStream(db_path=db_path, inbox_dir=str(inbox_dir))
            for event in events:
                stream.enqueue_event(
                    event["event_type"],
                    payload=event.get("payload", {}),
                    priority=event.get("priority"),
                    source=event.get("source", "validation"),
                )
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
            "state": store.get_system_state(),
            "cognition": store.get_state("cognition_state"),
            "memory": store.get_state("regime_memory"),
            "events": store.get_event_history(limit=20),
        }


def main() -> None:
    event_stream_text = (REPO_ROOT / "runtime" / "event_stream.py").read_text(encoding="utf-8")
    _assert("dsa_bridge" not in event_stream_text, "EventStream must not import dsa_bridge")
    for path in (REPO_ROOT / "runtime" / "cognition").glob("*.py"):
        _assert("runtime.adapter" not in path.read_text(encoding="utf-8"), f"cognition imports adapter: {path.name}")

    poison = {
        "type": "stock_signal",
        "symbol": "AAPL",
        "action": "BUY",
        "confidence": 0.92,
        "strategy": "MA_CROSS",
        "target_weight": 0.3,
    }
    routed = route_input(poison)
    runtime_event = route_to_runtime_event(poison)
    _assert(routed["type"] == "market_event", "poisoned stock signal must become neutral market_event")
    _assert(routed["intensity"] == 0.0, "poisoned event must not carry signal intensity")
    payload_text = json.dumps(runtime_event["payload"], ensure_ascii=False).lower()
    for forbidden in ["buy", "strategy", "target_weight", "ma_cross"]:
        _assert(forbidden not in payload_text, f"illegal field leaked: {forbidden}")

    absent = _run_events(
        [
            {
                "event_type": "market_anomaly",
                "priority": 90,
                "source": "native",
                "payload": {"liquidity": "contracting", "keyword": "panic crisis"},
            },
            {
                "event_type": "attention_spike",
                "priority": 70,
                "source": "native",
                "payload": {"attention": "exploding"},
            },
        ]
    )
    _assert(absent["state"]["current_state"] in {"RISK_OFF", "CRASH_STRESS"}, "native cognition failed without DSA")
    _assert(absent["cognition"]["fusion"], "event fusion missing without DSA")
    _assert(absent["memory"]["summary"]["sequence_length"] == 1, "regime memory missing without DSA")
    _assert(absent["cognition"]["causal"], "causal inference missing without DSA")

    malicious = route_to_runtime_event(
        {
            "type": "social_sentiment",
            "source": "dsa",
            "intensity": 0.9,
            "metadata": {
                "buy_signal": True,
                "sell_signal": True,
                "strategy": "MA_CROSS",
                "alpha_score": 9.9,
                "target_weight": 0.3,
                "topic": "AI",
            },
        }
    )
    _assert(malicious["event_type"] == "market_event", "malicious metadata must be neutralized")
    payload_text = json.dumps(malicious["payload"], ensure_ascii=False).lower()
    for forbidden in ["buy_signal", "sell_signal", "strategy", "alpha_score", "target_weight", "ma_cross"]:
        _assert(forbidden not in payload_text, f"malicious metadata leaked: {forbidden}")
    malicious_result = _run_events([malicious], use_inbox=True)
    _assert(
        malicious_result["state"]["current_state"] == "NORMAL",
        "neutralized malicious event must not influence regime state",
    )

    native = _run_events(
        [
            {
                "event_type": "attention_spike",
                "priority": 82,
                "source": "native",
                "payload": {"keywords": ["AI", "attention"], "evidence_quality": "unclear"},
            }
        ]
    )
    adapted = _run_events(
        [
            {
                "type": "social_sentiment",
                "timestamp": int(time.time()),
                "source": "dsa",
                "intensity": 0.82,
                "metadata": {"keywords": ["AI", "attention"], "evidence_quality": "unclear"},
            }
        ],
        use_inbox=True,
    )
    _assert(native["state"]["current_state"] == adapted["state"]["current_state"], "state differs by source")
    _assert(
        native["memory"]["summary"]["dominant_state"] == adapted["memory"]["summary"]["dominant_state"],
        "memory differs by source",
    )
    _assert(
        native["cognition"]["causal"]["primary_driver"] == adapted["cognition"]["causal"]["primary_driver"],
        "causal inference differs by source",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        copied = Path(temp_dir) / "AtlasOS_copy"
        shutil.copytree(
            REPO_ROOT,
            copied,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "runtime/state/*.sqlite", "runtime/logs/*"),
        )
        bridge = copied / "runtime" / "adapter" / "dsa_bridge.py"
        if bridge.exists():
            bridge.unlink()
        code = f"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, {str(copied)!r})
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.state_store import StateStore
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    db = str(root / "state.sqlite")
    inbox = str(root / "inbox")
    stream = EventStream(db_path=db, inbox_dir=inbox)
    stream.enqueue_event("market_anomaly", payload={{"liquidity": "contracting", "keyword": "panic crisis"}}, priority=90)
    loop = DecisionLoop(DecisionLoopConfig(db_path=db, inbox_dir=inbox, log_path=str(root / "runtime.jsonl"), heartbeat_interval_seconds=9999999999))
    loop.run_once()
    state = StateStore(db_path=db).get_state("cognition_state")
    assert state["fusion"]
"""
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        _assert(result.returncode == 0, f"runtime failed without dsa_bridge: {result.stderr}")

    print("Input Abstraction Layer v0.4.1 validation PASS")


if __name__ == "__main__":
    main()
