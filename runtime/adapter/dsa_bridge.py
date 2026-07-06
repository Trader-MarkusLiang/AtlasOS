"""DSA infrastructure bridge for Atlas Runtime v0.4.

Compatibility wrapper for DSA-style inputs. EventStream depends on
`runtime.adapter.input_router`, not this source-specific module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from runtime.adapter.input_router import (
    ILLEGAL_EXACT_KEYS,
    route_input,
    route_to_runtime_event,
    router_diagnostics,
)

FORBIDDEN_BUSINESS_KEYS = ILLEGAL_EXACT_KEYS


@dataclass(frozen=True, init=False)
class AtlasUnifiedEvent:
    """Backward-compatible wrapper for the v0.4 unified event name."""

    type: str
    timestamp: int
    source: str
    intensity: float
    metadata: Dict[str, Any]

    def __init__(
        self,
        type: str,
        timestamp: int,
        source: str,
        intensity: float,
        metadata: Dict[str, Any] | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "type", type)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "intensity", intensity)
        object.__setattr__(self, "metadata", metadata if metadata is not None else payload or {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "intensity": self.intensity,
            "metadata": self.metadata,
        }


def normalize_dsa_signal(signal: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize DSA-style infrastructure output into Atlas unified schema."""

    routed = route_input(signal)
    return {
        "type": routed["type"],
        "timestamp": routed["timestamp"],
        "source": routed["source"],
        "intensity": routed["intensity"],
        "metadata": routed["payload"],
    }


def normalize_external_event(item: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize native Atlas, unified, or DSA-style events to runtime records."""

    return route_to_runtime_event(item)


def runtime_event_from_unified(event: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert Atlas unified event schema to EventStream runtime schema."""

    item = dict(event)
    if "metadata" in item and "payload" not in item:
        item["payload"] = item["metadata"]
    return route_to_runtime_event(item)


def adapter_diagnostics() -> Dict[str, Any]:
    """Return DSA adapter status without importing DSA business logic."""

    diagnostics = router_diagnostics()
    return {
        "adapter": "dsa_bridge",
        "status": "available",
        "input_router": diagnostics,
        "forbidden_business_keys": sorted(FORBIDDEN_BUSINESS_KEYS),
    }
