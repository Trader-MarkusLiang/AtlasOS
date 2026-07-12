"""Normalized market intelligence ingestion backbone.

This module reuses existing market-data utilities and emits source-neutral
observations. It is not a crawler, forecast model, trading signal, or broker
adapter.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from runtime.adapter.input_router import route_to_runtime_event
from runtime.event_stream import EventStream
from runtime.logging import utc_now_iso
from runtime.market_evidence_sources import fetch_public_market_evidence
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

USABLE_DATA_STATUSES = {"Available", "Partial"}


def refresh_market_intelligence(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    enqueue: bool = False,
    max_assets: int = 12,
) -> dict[str, Any]:
    """Fetch configured asset observations and optionally enqueue events."""

    context = build_portfolio_context(config_path=config_path)
    fixtures = _load_market_fixtures(config_path)
    positions = context.get("positions", []) if isinstance(context, Mapping) else []
    observations = []
    events = []
    for item in positions[:max_assets]:
        observation = _observe_position(item, fixture=fixtures.get(str(item.get("asset") or "")))
        observations.append(observation)
        if observation.get("normalized_event_type"):
            events.append(market_observation_to_event(observation))
    evidence = fetch_public_market_evidence(
        [item for item in positions[:max_assets] if isinstance(item, Mapping)]
    )
    evidence_items = evidence.get("items", []) if isinstance(evidence, Mapping) else []
    for item in evidence_items:
        if isinstance(item, Mapping):
            events.append(market_evidence_to_event(item))
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
        "channels": channel_status(observations, evidence.get("channel_statuses", {})),
        "portfolio_context_status": context.get("status"),
        "observations": observations,
        "evidence_items": evidence_items,
        "source_errors": evidence.get("errors", {}),
        "events_prepared": len(events),
        "events_enqueued": enqueued,
        "degraded": not observations or any(item.get("data_quality_status") not in USABLE_DATA_STATUSES for item in observations),
        "proof_mode": _proof_mode(observations),
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


def market_evidence_to_event(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Return a source-neutral Signal event from one external evidence item."""

    return route_to_runtime_event(
        {
            "type": "market_event",
            "source": evidence.get("source") or "market_evidence",
            "timestamp": evidence.get("timestamp") or utc_now_iso(),
            "confidence": 0.85 if evidence.get("verification_status") == "VERIFIED_OFFICIAL_SOURCE" else 0.6,
            "payload": {
                "channel": evidence.get("channel"),
                "headline": evidence.get("headline"),
                "freshness": evidence.get("freshness"),
                "source_type": evidence.get("source_type"),
                "classification": evidence.get("classification"),
                "verification_status": evidence.get("verification_status"),
                "affected_assets": evidence.get("affected_assets", []),
                "affected_themes": evidence.get("affected_themes", []),
                "world_model_node": evidence.get("world_model_node"),
                "thesis_changed": evidence.get("thesis_changed", "UNASSESSED"),
                "source_url": evidence.get("source_url"),
                "details": evidence.get("details", {}),
            },
        }
    )


def channel_status(
    observations: list[Mapping[str, Any]],
    external_statuses: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Report which mandated channels are real vs missing."""

    price_observations = [item for item in observations if item.get("channel") == "price_volume"]
    price_available = any(item.get("data_quality_status") in USABLE_DATA_STATUSES for item in price_observations)
    price_fixture = any(item.get("source_type") == "controlled_fixture" for item in price_observations)
    price_failed = bool(price_observations) and not price_available
    portfolio_available = any(item.get("portfolio_relevant") for item in observations)
    if price_available and price_fixture:
        price_status = "SIMULATED"
    elif price_available:
        freshness = {str(item.get("freshness") or "").upper() for item in price_observations if item.get("data_quality_status") in USABLE_DATA_STATUSES}
        price_status = "LIVE" if freshness & {"LIVE", "FRESH", "AVAILABLE"} else "DELAYED" if "DELAYED" in freshness else "CACHED"
    elif price_failed:
        price_status = "FAILED"
    else:
        price_status = "NOT_CONFIGURED"
    external = external_statuses if isinstance(external_statuses, Mapping) else {}
    derived_status = "DELAYED" if price_available and not price_fixture else "SIMULATED" if price_fixture else "NOT_CONFIGURED"
    return {
        "price_volume": price_status,
        "market_breadth": str(external.get("market_breadth") or "NOT_CONFIGURED"),
        "volatility": derived_status,
        "liquidity_proxy": derived_status,
        "news_announcement": str(external.get("news_announcement") or "NOT_CONFIGURED"),
        "narrative_attention": "NOT_CONFIGURED",
        "macro_policy": str(external.get("macro_policy") or "NOT_CONFIGURED"),
        "portfolio_relevance": "LIVE" if portfolio_available and not price_fixture else ("SIMULATED" if portfolio_available else "NOT_CONFIGURED"),
    }


def _observe_position(position: Mapping[str, Any], fixture: Mapping[str, Any] | None = None) -> dict[str, Any]:
    asset = str(position.get("asset") or "").strip()
    market = str(position.get("market") or "Unknown")
    source_type = "market_data_provider"
    if isinstance(fixture, Mapping):
        snapshot = {
            "ticker": asset,
            "market": market,
            "source": fixture.get("source", "controlled_fixture"),
            "timestamp": fixture.get("timestamp") or utc_now_iso(),
            "data_status": fixture.get("data_status", "Available"),
            "missing_fields": fixture.get("missing_fields", []),
            "errors": fixture.get("errors", []),
            "latest_price": fixture.get("latest_price"),
            "daily_change_pct": fixture.get("daily_change_pct"),
            "change_5d_pct": fixture.get("change_5d_pct"),
            "change_20d_pct": fixture.get("change_20d_pct"),
            "change_60d_pct": fixture.get("change_60d_pct"),
            "volume": fixture.get("volume"),
            "turnover": fixture.get("turnover"),
            "data_freshness": fixture.get("data_freshness", "SIMULATED"),
        }
        source_type = "controlled_fixture"
    else:
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
        "source_type": source_type,
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
        "latest_price": snapshot.get("latest_price"),
        "source_url": _market_source_url(source),
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
        try:
            observed = datetime.fromisoformat(str(snapshot.get("timestamp")).replace("Z", "+00:00"))
            if observed.tzinfo is None:
                observed = observed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
            age_seconds = max(0.0, (datetime.now(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds())
            if age_seconds <= 900:
                return "LIVE"
            if age_seconds <= 86400:
                return "DELAYED"
            return "CACHED"
        except ValueError:
            return "Unknown"
    return "Unknown"


def _market_source_url(source: str) -> str:
    return {
        "tencent_quote": "https://qt.gtimg.cn/",
        "tencent_kline": "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
        "sina_quote": "https://hq.sinajs.cn/",
        "eastmoney_quote": "https://quote.eastmoney.com/",
        "eastmoney_kline": "https://quote.eastmoney.com/",
        "yahoo_chart": "https://finance.yahoo.com/",
        "yfinance": "https://finance.yahoo.com/",
        "akshare": "https://akshare.akfamily.xyz/",
    }.get(source, "")


def _load_market_fixtures(config_path: str | None) -> dict[str, Mapping[str, Any]]:
    if not config_path:
        return {}
    target = Path(config_path)
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    market = data.get("market_intelligence") if isinstance(data, Mapping) else {}
    fixtures = market.get("fixtures") if isinstance(market, Mapping) else {}
    if not isinstance(fixtures, Mapping):
        return {}
    return {str(key): value for key, value in fixtures.items() if isinstance(value, Mapping)}


def _proof_mode(observations: list[Mapping[str, Any]]) -> str:
    if not observations:
        return "NO_CONFIGURED_ASSETS"
    if any(item.get("source_type") == "controlled_fixture" for item in observations):
        return "CONTROLLED_FIXTURE_PROOF"
    if any(item.get("data_quality_status") in USABLE_DATA_STATUSES for item in observations):
        return "LIVE_OR_PROVIDER_PROOF"
    return "DEGRADED_PROVIDER_PROOF"
