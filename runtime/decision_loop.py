"""Continuous event-driven decision loop for Atlas Runtime v0.2."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from runtime.cognition.causal_inference import infer_causal_state
    from runtime.cognition.event_fusion_engine import EventFusionEngine
    from runtime.cognition.regime_memory import RegimeMemory
    from runtime.cognition.state_controller import AntiOverwriteStateController
    from runtime.event_stream import EVENT_HEARTBEAT, EventStream
    from runtime.logging import log_execution, utc_now_iso
    from runtime.orchestrator import run_state_runtime
    from runtime.state_machine import RuntimeStateMachine
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.cognition.causal_inference import infer_causal_state
    from runtime.cognition.event_fusion_engine import EventFusionEngine
    from runtime.cognition.regime_memory import RegimeMemory
    from runtime.cognition.state_controller import AntiOverwriteStateController
    from runtime.event_stream import EVENT_HEARTBEAT, EventStream
    from runtime.logging import log_execution, utc_now_iso
    from runtime.orchestrator import run_state_runtime
    from runtime.state_machine import RuntimeStateMachine
    from runtime.state_store import StateStore


@dataclass
class DecisionLoopConfig:
    sleep_interval_seconds: int = 60
    heartbeat_interval_seconds: int = 300
    max_events_per_cycle: int = 5
    log_path: Optional[str] = None
    db_path: Optional[str] = None
    inbox_dir: Optional[str] = None
    llm_model: str = "gpt-5.5"


class DecisionLoop:
    """Always-on event -> state -> orchestrator loop."""

    def __init__(self, config: Optional[DecisionLoopConfig] = None) -> None:
        self.config = config or DecisionLoopConfig()
        self.event_stream = EventStream(db_path=self.config.db_path, inbox_dir=self.config.inbox_dir)
        self.state_machine = RuntimeStateMachine(db_path=self.config.db_path)
        self.store = StateStore(db_path=self.config.db_path)
        self.fusion_engine = EventFusionEngine()
        self.regime_memory = RegimeMemory(db_path=self.config.db_path)
        self.state_controller = AntiOverwriteStateController()
        self._running = False
        self._last_heartbeat = 0.0

    def run_once(self) -> Dict[str, object]:
        """Run one event-loop cycle."""

        ingested = self.event_stream.listen_once()
        self._enqueue_heartbeat_if_due()
        events = self.event_stream.poll(limit=self.config.max_events_per_cycle)
        results: List[Dict[str, object]] = []

        if events:
            fusion = self.fusion_engine.fuse(events)
            memory_before = self.regime_memory.summary()
            causal = infer_causal_state(
                fusion=fusion,
                attention_liquidity=fusion.get("attention_liquidity", {}),
                memory_summary=memory_before,
            )
            previous_state = self.state_machine.current_state()
            transition = self.state_controller.decide(
                previous_state=previous_state,
                fusion=fusion,
                memory_summary=memory_before,
                causal=causal,
            )
            memory_after = self.regime_memory.record(
                transition["current_state"],
                fusion=fusion,
                causal=causal,
            )
            transition["memory_after"] = memory_after
            self.store.save_system_state(transition)
            self.store.append_state_transition(transition)
            self.store.set_state(
                "cognition_state",
                {
                    "fusion": fusion,
                    "causal": causal,
                    "controller": transition,
                    "memory": memory_after,
                },
            )
            fused_event = {
                "event_id": "fusion:" + ",".join(event["event_id"] for event in events),
                "event_type": "fused_market_reality",
                "priority": max(int(event.get("priority", 0)) for event in events),
                "payload": {
                    "cognition": {
                        "fusion": fusion,
                        "causal": causal,
                        "controller": transition,
                        "memory": memory_after,
                    }
                },
                "source": "event_fusion_engine",
                "created_at": utc_now_iso(),
            }
            result = run_state_runtime(
                system_state=transition["current_state"],
                event=fused_event,
                log_path=self.config.log_path,
                db_path=self.config.db_path,
                llm_model=self.config.llm_model,
            )
            for event in events:
                self.event_stream.acknowledge(event["event_id"], "handled")
            results.append(
                {
                    "event_ids": [event["event_id"] for event in events],
                    "event_types": [event["event_type"] for event in events],
                    "state": transition["current_state"],
                    "proposed_state": transition["proposed_state"],
                    "transition_allowed": transition["transition_allowed"],
                    "primary_driver": causal["primary_driver"],
                    "result_status": result["status"],
                    "decision_brief_id": result["run_id"],
                }
            )

        cycle_record = {
            "timestamp": utc_now_iso(),
            "trigger_type": "decision_loop_cycle",
            "events_ingested": ingested,
            "events_processed": len(results),
            "raw_events_processed": len(events),
            "results": results,
            "status": "success",
        }
        log_execution(cycle_record, log_path=self.config.log_path)
        self.store.append_system_log(cycle_record)
        return cycle_record

    def run_forever(self, max_cycles: Optional[int] = None) -> None:
        """Run until stopped or max_cycles is reached."""

        self._running = True
        cycles = 0
        while self._running:
            self.run_once()
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
            time.sleep(self.config.sleep_interval_seconds)

    def stop(self, *_args: object) -> None:
        self._running = False

    def _enqueue_heartbeat_if_due(self) -> None:
        now = time.time()
        if now - self._last_heartbeat < self.config.heartbeat_interval_seconds:
            return
        self.event_stream.enqueue_event(
            EVENT_HEARTBEAT,
            payload={"heartbeat_at": utc_now_iso()},
            source="decision_loop",
        )
        self._last_heartbeat = now
