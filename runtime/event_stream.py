"""SQLite-backed event stream for Atlas autonomous runtime.

Events are ingested into a queue, prioritized, consumed by the decision loop,
and retained as append-only history. File ingestion watches JSON / JSONL files
in `runtime/events/inbox` so external tools can submit events without importing
Atlas internals.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from runtime.adapter.input_router import route_to_runtime_event
    from runtime.cognition.bidirectional_perception_engine import perception_feedback_loop
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.adapter.input_router import route_to_runtime_event
    from runtime.cognition.bidirectional_perception_engine import perception_feedback_loop
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore


EVENT_MARKET_ANOMALY = "market_anomaly"
EVENT_ATTENTION_SPIKE = "attention_spike"
EVENT_VOLUME_PRICE_BREAKOUT = "volume_price_breakout"
EVENT_NEWS_NARRATIVE_SPIKE = "news_narrative_spike"
EVENT_PORTFOLIO_DRAWDOWN = "portfolio_drawdown"
EVENT_LIQUIDITY_SHOCK = "liquidity_shock"
EVENT_HEARTBEAT = "heartbeat"
EVENT_MARKET_EVENT = "market_event"

SUPPORTED_EVENT_TYPES = {
    EVENT_MARKET_ANOMALY,
    EVENT_ATTENTION_SPIKE,
    EVENT_VOLUME_PRICE_BREAKOUT,
    EVENT_NEWS_NARRATIVE_SPIKE,
    EVENT_PORTFOLIO_DRAWDOWN,
    EVENT_LIQUIDITY_SHOCK,
    EVENT_HEARTBEAT,
    EVENT_MARKET_EVENT,
    "market_open",
    "market_close",
    "volatility_spike",
    "user_input_event",
}

DEFAULT_PRIORITY = {
    EVENT_PORTFOLIO_DRAWDOWN: 100,
    EVENT_LIQUIDITY_SHOCK: 95,
    EVENT_MARKET_ANOMALY: 90,
    "volatility_spike": 85,
    EVENT_VOLUME_PRICE_BREAKOUT: 80,
    EVENT_ATTENTION_SPIKE: 70,
    EVENT_NEWS_NARRATIVE_SPIKE: 65,
    "user_input_event": 60,
    "market_open": 40,
    "market_close": 40,
    EVENT_HEARTBEAT: 10,
}


@dataclass
class RuntimeEvent:
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: Optional[int] = None
    source: str = "runtime"
    event_id: str = field(default_factory=lambda: f"event-{uuid.uuid4()}")
    created_at: str = field(default_factory=utc_now_iso)

    def normalized_priority(self) -> int:
        if self.priority is not None:
            return self.priority
        return DEFAULT_PRIORITY.get(self.event_type, 50)

    def to_record(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "priority": self.normalized_priority(),
            "source": self.source,
            "created_at": self.created_at,
        }


class EventStream:
    """Priority event queue plus lightweight file listener."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        inbox_dir: Optional[str] = None,
    ) -> None:
        self.store = StateStore(db_path=db_path)
        configured = inbox_dir or os.environ.get("ATLAS_EVENT_INBOX")
        self.inbox_dir = Path(configured) if configured else Path("runtime/events/inbox")
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.store.ensure_event_schema()

    def enqueue(self, event: RuntimeEvent) -> str:
        if event.event_type not in SUPPORTED_EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {event.event_type}")
        self.store.append_event(event.to_record(), status="pending")
        return event.event_id

    def enqueue_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        source: str = "runtime",
        created_at: Optional[str] = None,
    ) -> str:
        routed = route_to_runtime_event(
            {
                "event_type": event_type,
                "payload": payload or {},
                "priority": priority if priority is not None else DEFAULT_PRIORITY.get(event_type, 50),
                "source": source,
                "created_at": created_at or utc_now_iso(),
            }
        )
        perception = perception_feedback_loop(
            event={
                "event_type": routed["event_type"],
                "payload": routed.get("payload", {}),
                "priority": routed.get("priority"),
                "source": routed.get("source", source),
                "created_at": routed.get("created_at", created_at or utc_now_iso()),
            },
            cognition_state=self.store.get_state("cognition_state"),
            regime_memory=self.store.get_state("regime_memory"),
        )
        deformed = perception["deformed_event"]
        payload_with_perception = dict(deformed.get("payload", {}))
        payload_with_perception["perception_coupling_metrics"] = perception["coupling_metrics"]
        return self.enqueue(
            RuntimeEvent(
                event_type=deformed["event_type"],
                payload=payload_with_perception,
                priority=deformed.get("priority"),
                source=deformed.get("source", source),
                created_at=deformed.get("created_at", created_at or utc_now_iso()),
            )
        )

    def poll(self, limit: int = 10) -> List[Dict[str, Any]]:
        events = self.store.get_pending_events(limit=limit)
        for event in events:
            self.store.update_event_status(event["event_id"], "processing")
        return events

    def acknowledge(self, event_id: str, status: str = "handled") -> None:
        self.store.update_event_status(event_id, status)

    def listen_once(self) -> int:
        """Ingest JSON / JSONL files from the inbox directory."""

        count = 0
        for path in sorted(self.inbox_dir.glob("*")):
            if path.suffix.lower() not in {".json", ".jsonl"}:
                continue
            for item in _read_event_file(path):
                event = route_to_runtime_event(item)
                self.enqueue_event(
                    event_type=event["event_type"],
                    payload=event.get("payload", {}),
                    priority=event.get("priority"),
                    source=event.get("source", f"file:{path.name}"),
                    created_at=event.get("created_at"),
                )
                count += 1
            processed_path = path.with_suffix(path.suffix + ".processed")
            path.rename(processed_path)
        return count

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.store.get_event_history(limit=limit)


def _read_event_file(path: Path) -> Iterable[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    if isinstance(data, list):
        return data
    return [data]
