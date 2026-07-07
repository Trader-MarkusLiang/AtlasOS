"""Normalized market intelligence ingestion backbone.

This module reuses existing market-data utilities and emits source-neutral
observations. It is not a crawler, forecast model, trading signal, or broker
adapter.
"""

from __future__ import annotations

from typing import Any, Mapping

from runtime.adapter.input_router import route_to_runtime_event
from runtime.event_stream import EventStream
from runtime.logging import utc_now_iso
from runtime.portfolio_context import build_portfolio_context


NORMALIZED_CHANNELS = [
    "price_volume",
    "market_breadth",
    "volatility",
    "liquidity_proxy",
    "news_announcement",
    "narrative_attention",
    "macro_policy",
    "portfolio_relevance",
]


def refresh_market_intelligence(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    enqueue: bool = False,
    max_assets: int = 12,
) -> dict[str, Any]:
    """Fetch configured asset observations and optionally enqueue events."""

    context = build_portfolio_context(config_path=config_path)
    positions = context.get("positions", []) if isinstance(context, Mapping) else []
    observations = []
    events = []
    for item in positions[:max_assets]:
        observation = _observe_position(item)
        observations.append(observation)
        if observation.get("normalized_event_type"):
            events.append(market_observation_to_event(observation))
    enqueued = 0
    if enqueue and events:
        stream = EventStream(db_path=db_path)
        for event in events:
            stream.enqueue_event(
                event["event_type"],
                payload=event.get("payload", {}),
                priority=event.get("priority"),
                source=event.get("source", "market_intelligence"),
                created_at=event.get("created_at"),
            )
            enqueued += 1
    return {
        "timestamp": utc_now_iso(),
        "status": "ok" if observations else "no_configured_assets",
        "channels": channel_status(observations),
        "portfolio_context_status": context.get("status"),
        "observations": observations,
        "events_prepared": len(events),
        "events_enqueued": enqueued,
        "degraded": not observations or any(item.get("data_quality_status") != "Available" for item in observations),
        "read_only": True,
        "no_trading_execution": True,
    }


def market_observation_to_event(observation: Mapping[str, Any]) -> dict[str, Any]:
    """Return an Input Router-compatible runtime event from one observation."""

    routed = route_to_runtime_event(
        {
            "type": observation.get("normalized_event_type") or "market_event",
            "source": observation.get("source") or "market_intelligence",
            "timestamp": observation.get("timestamp"),
            "confidence": observation.get("confidence", 0.0),
            "payload": {
                "asset": observation.get("asset"),
                "theme": observation.get("theme"),
                "market": observation.get("market"),
                "freshness": observation.get("freshness"),
                "data_quality_status": observation.get("data_quality_status"),
                "source_type": observation.get("source_type"),
                "raw_reference": observation.get("raw_reference"),
                "change_5d_pct": observation.get("change_5d_pct"),
                "change_20d_pct": observation.get("change_20d_pct"),
                "volume": observation.get("volume"),
            },
        }
    )
    return routed


def channel_status(observations: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Report which mandated channels are real vs missing."""

    price_available = any(item.get("channel") == "price_volume" for item in observations)
    portfolio_available = any(item.get("portfolio_relevant") for item in observations)
    return {
        "price_volume": "available" if price_available else "missing_or_unconfigured",
        "market_breadth": "not_implemented",
        "volatility": "partial_from_price_history" if price_available else "missing_or_unconfigured",
        "liquidity_proxy": "partial_from_volume" if price_available else "missing_or_unconfigured",
        "news_announcement": "not_implemented",
        "narrative_attention": "not_implemented",
        "macro_policy": "not_implemented",
        "portfolio_relevance": "available" if portfolio_available else "missing_or_unconfigured",
    }


def _observe_position(position: Mapping[str, Any]) -> dict[str, Any]:
    asset = str(position.get("asset") or "").strip()
    market = str(position.get("market") or "Unknown")
    try:
        from tools.market_data.market_data_provider import get_market_snapshot

        snapshot = get_market_snapshot(asset, market)
    except Exception as exc:
        snapshot = {
            "ticker": asset,
            "market": market,
            "source": None,
            "timestamp": None,
            "data_status": "Unavailable",
            "missing_fields": ["provider_exception"],
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    status = str(snapshot.get("data_status") or "Unavailable")
    source = snapshot.get("source") or "none"
    confidence = 0.75 if status == "Available" else 0.45 if status == "Partial" else 0.1
    event_type = "price_breakout" if snapshot.get("latest_price") is not None else "market_event"
    return {
        "timestamp": snapshot.get("timestamp") or utc_now_iso(),
        "source": source,
        "source_type": "market_data_provider",
        "asset": asset,
        "theme": position.get("theme") or "Unspecified",
        "market": market,
        "freshness": _freshness(snapshot),
        "confidence": confidence,
        "raw_reference": {
            "provider": source,
            "ticker": snapshot.get("ticker") or asset,
            "missing_fields": snapshot.get("missing_fields", []),
            "errors": snapshot.get("errors", []),
        },
        "normalized_event_type": event_type,
        "data_quality_status": status,
        "channel": "price_volume",
        "portfolio_relevant": True,
        "latest_price_available": snapshot.get("latest_price") is not None,
        "daily_change_pct": snapshot.get("daily_change_pct"),
        "change_5d_pct": snapshot.get("change_5d_pct"),
        "change_20d_pct": snapshot.get("change_20d_pct"),
        "change_60d_pct": snapshot.get("change_60d_pct"),
        "volume": snapshot.get("volume"),
        "turnover": snapshot.get("turnover"),
    }


def _freshness(snapshot: Mapping[str, Any]) -> str:
    if snapshot.get("data_freshness"):
        return str(snapshot.get("data_freshness"))
    if snapshot.get("timestamp"):
        return "Available"
    return "Unknown"
