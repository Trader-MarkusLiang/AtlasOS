"""Runtime event source for Atlas macOS background daemon.

Default mode is deterministic simulated market events. This module is an
infrastructure hook only; it does not fetch broker data, trade, or change CDE.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from runtime.logging import utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso


EVENT_TYPE_TO_RUNTIME = {
    "attention": "attention_spike",
    "price": "volume_price_breakout",
    "liquidity": "liquidity_shock",
    "narrative": "news_narrative_spike",
}


@dataclass
class SimulatedMarketEventSource:
    """Small deterministic event source for daemon smoke runs."""

    mode: str = "simulated"
    _index: int = 0

    def get_event(self) -> Dict[str, Any]:
        """Return one event in the user-requested source shape."""

        event = _SIMULATED_EVENTS[self._index % len(_SIMULATED_EVENTS)]
        self._index += 1
        return {
            "timestamp": utc_now_iso(),
            "type": event["type"],
            "payload": dict(event["payload"]),
            "source": self.mode,
        }

    def get_runtime_event(self) -> Dict[str, Any]:
        """Return an EventStream-compatible event derived from get_event()."""

        event = self.get_event()
        event_type = EVENT_TYPE_TO_RUNTIME.get(str(event["type"]), "market_event")
        return {
            "event_type": event_type,
            "payload": event["payload"],
            "priority": _priority_for_type(event["type"]),
            "source": event["source"],
            "created_at": event["timestamp"],
            "raw_event": event,
        }


class ExternalEventSourceHook:
    """Future API hook placeholder.

    Subclasses can override get_event() without changing the daemon. The base
    class intentionally raises so missing external integrations fail visibly.
    """

    def get_event(self) -> Dict[str, Any]:
        raise NotImplementedError("external event source is not configured")


def event_to_runtime_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a source event into EventStream-compatible fields."""

    event_type = EVENT_TYPE_TO_RUNTIME.get(str(event.get("type", "")), "market_event")
    return {
        "event_type": event_type,
        "payload": dict(event.get("payload", {})),
        "priority": _priority_for_type(str(event.get("type", ""))),
        "source": str(event.get("source", "simulated")),
        "created_at": str(event.get("timestamp", utc_now_iso())),
        "raw_event": dict(event),
    }


def _priority_for_type(event_type: str) -> int:
    return {
        "attention": 70,
        "price": 80,
        "liquidity": 95,
        "narrative": 65,
    }.get(event_type, 50)


_SIMULATED_EVENTS: List[Dict[str, Any]] = [
    {
        "type": "attention",
        "payload": {"attention": "rising", "retail_attention": "surge", "theme": "simulated_attention"},
    },
    {
        "type": "price",
        "payload": {"price": "breakout", "volume": "confirming", "theme": "simulated_price"},
    },
    {
        "type": "liquidity",
        "payload": {"liquidity": "contracting", "keyword": "stress", "theme": "simulated_liquidity"},
    },
    {
        "type": "narrative",
        "payload": {"headline": "narrative acceleration", "attention": "expanding", "theme": "simulated_narrative"},
    },
]
