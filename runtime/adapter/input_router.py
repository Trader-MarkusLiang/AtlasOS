"""Input Abstraction Layer for Atlas Runtime v0.4.1.

External systems enter Atlas through this module. The router produces a
source-neutral event shape and strips strategy / trading fields before data can
reach EventStream or cognition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple


ILLEGAL_EXACT_KEYS = {
    "action",
    "allocation",
    "alpha_score",
    "buy",
    "buy_signal",
    "entry_price",
    "exit_price",
    "ma_cross",
    "ma_signal",
    "position_size",
    "recommendation",
    "score",
    "sell",
    "sell_pressure",
    "sell_signal",
    "strategy",
    "target_price",
    "target_weight",
    "trade",
    "weight",
}

ILLEGAL_KEY_FRAGMENTS = (
    "buy_signal",
    "sell_signal",
    "target_weight",
    "alpha_score",
    "recommendation",
    "ma_cross",
)

TYPE_MAP = {
    "attention": "attention_spike",
    "attention_spike": "attention_spike",
    "correlation": "market_anomaly",
    "drawdown": "portfolio_drawdown",
    "heartbeat": "heartbeat",
    "liquidity": "liquidity_shock",
    "liquidity_shock": "liquidity_shock",
    "market_anomaly": "market_anomaly",
    "market_close": "market_close",
    "market_event": "market_event",
    "market_open": "market_open",
    "news": "news_narrative_spike",
    "news_narrative": "news_narrative_spike",
    "news_narrative_spike": "news_narrative_spike",
    "portfolio_drawdown": "portfolio_drawdown",
    "price_breakout": "volume_price_breakout",
    "search": "attention_spike",
    "sentiment": "attention_spike",
    "social": "attention_spike",
    "social_sentiment": "attention_spike",
    "stock_signal": "market_event",
    "user_input_event": "user_input_event",
    "volatility": "volatility_spike",
    "volatility_spike": "volatility_spike",
    "volume_price_breakout": "volume_price_breakout",
}


@dataclass(frozen=True)
class RoutedInputEvent:
    type: str = "market_event"
    timestamp: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    source: str = "external"
    intensity: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)
    stripped_fields: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "intensity": self.intensity,
            "payload": self.payload,
        }


def route_input(item: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize any external input into the unified Atlas event schema."""

    if not isinstance(item, Mapping):
        raise TypeError("input item must be a mapping")

    payload_source: Dict[str, Any] = {}
    if isinstance(item.get("payload"), Mapping):
        payload_source.update(item["payload"])
    if isinstance(item.get("metadata"), Mapping):
        payload_source.update(item["metadata"])
    for key in ("ticker", "symbol", "keyword", "keywords", "market", "sector", "value", "change", "headline"):
        if key in item and key not in payload_source:
            payload_source[key] = item[key]

    clean_payload, stripped_payload = sanitize_payload(payload_source)
    _, stripped_top = sanitize_payload({key: value for key, value in item.items() if key not in {"payload", "metadata"}})
    stripped = tuple(sorted(set(stripped_payload + stripped_top)))

    raw_type = str(
        item.get("type")
        or item.get("event_type")
        or item.get("signal_type")
        or item.get("kind")
        or "market_event"
    )
    event_type = _map_type(raw_type)
    intensity = _intensity(item)
    if stripped:
        event_type = "market_event"
        intensity = 0.0

    return RoutedInputEvent(
        type=event_type,
        timestamp=_timestamp(item.get("timestamp") or item.get("created_at")),
        source=str(item.get("source") or "external"),
        intensity=intensity,
        payload=clean_payload,
        stripped_fields=stripped,
    ).to_dict()


def route_to_runtime_event(item: Mapping[str, Any]) -> Dict[str, Any]:
    """Return an EventStream-compatible record from routed input."""

    routed = route_input(item)
    payload = dict(routed["payload"])
    payload["routed_type"] = routed["type"]
    payload["routed_intensity"] = routed["intensity"]
    return {
        "event_type": routed["type"],
        "payload": payload,
        "priority": max(1, min(100, round(float(routed["intensity"]) * 100))),
        "source": routed["source"],
        "created_at": _iso_from_epoch(int(routed["timestamp"])),
    }


def sanitize_payload(value: Any) -> tuple[Any, tuple[str, ...]]:
    """Remove illegal fields recursively and report stripped key names."""

    stripped: list[str] = []
    if isinstance(value, Mapping):
        clean: Dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _is_illegal_key(key_text):
                stripped.append(key_text)
                continue
            child, child_stripped = sanitize_payload(item)
            stripped.extend(child_stripped)
            clean[key_text] = child
        return clean, tuple(stripped)
    if isinstance(value, list):
        clean_list = []
        for item in value:
            child, child_stripped = sanitize_payload(item)
            stripped.extend(child_stripped)
            clean_list.append(child)
        return clean_list, tuple(stripped)
    return value, tuple()


def router_diagnostics() -> Dict[str, Any]:
    return {
        "router": "input_router",
        "status": "available",
        "schema": {
            "type": "string",
            "timestamp": "int",
            "source": "string",
            "intensity": "float",
            "payload": "dict",
        },
        "illegal_exact_keys": sorted(ILLEGAL_EXACT_KEYS),
    }


def _is_illegal_key(key: str) -> bool:
    normalized = key.strip().lower()
    compact = normalized.replace("-", "_").replace(" ", "_")
    if compact in ILLEGAL_EXACT_KEYS:
        return True
    return any(fragment in compact for fragment in ILLEGAL_KEY_FRAGMENTS)


def _map_type(raw_type: str) -> str:
    return TYPE_MAP.get(raw_type.strip().lower(), "market_event")


def _intensity(signal: Mapping[str, Any]) -> float:
    for key in ("intensity", "severity", "confidence", "magnitude"):
        if key in signal:
            return _clamp_float(signal[key])
    if "priority" in signal:
        return _clamp_float(float(signal["priority"]) / 100)
    return 0.5


def _clamp_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.5
    if number > 1:
        number = number / 100
    return max(0.0, min(1.0, number))


def _timestamp(value: Any) -> int:
    if value is None:
        return _now_epoch()
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(float(str(value)))
    except ValueError:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp())


def _iso_from_epoch(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _now_epoch() -> int:
    return int(datetime.now(timezone.utc).timestamp())
