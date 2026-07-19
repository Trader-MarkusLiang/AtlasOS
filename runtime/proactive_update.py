"""Proactive update planner for Atlas Runtime.

This module is runtime infrastructure. It decides what existing information
channels should be refreshed next, based on portfolio context and current
market-intelligence freshness. It does not trade, forecast prices, crawl the
web directly, or modify cognition definitions.
"""

from __future__ import annotations

import uuid
from typing import Any, Mapping

from runtime.logging import utc_now_iso
from runtime.market_intelligence import NORMALIZED_CHANNELS
from runtime.portfolio_context import build_portfolio_context


DEFAULT_PROACTIVE_UPDATE_SECONDS = 7200


def build_proactive_update_plan(
    *,
    config_path: str | None = None,
    market_state: Mapping[str, Any] | None = None,
    daily_cycle_state: Mapping[str, Any] | None = None,
    cadence_seconds: int = DEFAULT_PROACTIVE_UPDATE_SECONDS,
) -> dict[str, Any]:
    """Build a read-only proactive update plan from existing Atlas context."""

    portfolio = build_portfolio_context(config_path=config_path)
    positions = [item for item in portfolio.get("positions", []) if isinstance(item, Mapping)]
    channels = market_state.get("channels", {}) if isinstance(market_state, Mapping) else {}
    exposure = portfolio.get("exposure_map", {}) if isinstance(portfolio.get("exposure_map"), Mapping) else {}
    top_assets = _top_assets(positions)
    top_themes = _top_map_items(exposure.get("theme_concentration"))
    degraded_channels = _degraded_channels(channels)
    refresh_channels = degraded_channels or list(NORMALIZED_CHANNELS[:4])
    focus = _research_focus(top_assets, top_themes, refresh_channels)
    cycle_id = f"proactive-{uuid.uuid4()}"
    timestamp = utc_now_iso()
    return {
        "status": "planned",
        "update_cycle_id": cycle_id,
        "timestamp": timestamp,
        "cadence_seconds": max(60, int(cadence_seconds or DEFAULT_PROACTIVE_UPDATE_SECONDS)),
        "portfolio_context_status": portfolio.get("status"),
        "portfolio_relevance_targets": top_assets,
        "theme_relevance_targets": top_themes,
        "market_channels_to_refresh": refresh_channels,
        "research_focus": focus,
        "daily_cycle_phase": _daily_phase(daily_cycle_state),
        "event_payload": {
            "update_cycle_id": cycle_id,
            "update_kind": "proactive_context_refresh",
            "portfolio_targets": top_assets,
            "theme_targets": top_themes,
            "channels_to_refresh": refresh_channels,
            "research_focus": focus,
            "read_only_update": True,
            "no_trading_execution": True,
        },
        "read_only": True,
        "no_trading_execution": True,
    }


def skipped_proactive_update_state(
    *,
    cadence_seconds: int,
    last_run_at: str | None,
    next_due_at: str | None,
) -> dict[str, Any]:
    """Return a log-only skipped status without replacing persisted plan state."""

    return {
        "status": "skipped_until_next_cadence",
        "cadence_seconds": max(60, int(cadence_seconds or DEFAULT_PROACTIVE_UPDATE_SECONDS)),
        "last_run_at": last_run_at,
        "next_due_at": next_due_at,
        "read_only": True,
        "no_trading_execution": True,
    }


def _top_assets(positions: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        positions,
        key=lambda item: _float(item.get("portfolio_percentage")),
        reverse=True,
    )
    return [
        {
            "asset": str(item.get("asset") or "Unknown")[:80],
            "market": str(item.get("market") or "Unknown")[:40],
            "theme": str(item.get("theme") or "Unspecified")[:80],
            "role": str(item.get("role") or "Unspecified")[:80],
            "portfolio_percentage": _float(item.get("portfolio_percentage")),
        }
        for item in ranked[:6]
    ]


def _top_map_items(value: Any) -> list[dict[str, Any]]:
    data = value if isinstance(value, Mapping) else {}
    ranked = sorted(data.items(), key=lambda pair: _float(pair[1]), reverse=True)
    return [
        {"name": str(name)[:80], "exposure_pct": _float(exposure)}
        for name, exposure in ranked[:5]
        if str(name).strip()
    ]


def _degraded_channels(channels: Mapping[str, Any]) -> list[str]:
    if not channels:
        return list(NORMALIZED_CHANNELS)
    stale_status = {"NOT_CONFIGURED", "FAILED", "RATE_LIMITED", "CACHED", "DELAYED"}
    degraded = [
        key
        for key in NORMALIZED_CHANNELS
        if str(channels.get(key, "NOT_CONFIGURED")).upper() in stale_status
    ]
    return degraded[:8]


def _research_focus(
    assets: list[Mapping[str, Any]],
    themes: list[Mapping[str, Any]],
    channels: list[str],
) -> list[str]:
    focus: list[str] = []
    for asset in assets[:4]:
        name = str(asset.get("asset") or "Unknown")
        market = str(asset.get("market") or "Unknown")
        focus.append(f"{name} ({market}) price, volume, liquidity, and announcement freshness")
    for theme in themes[:3]:
        focus.append(f"{theme.get('name')} narrative, macro, and attention change")
    if channels:
        focus.append("Refresh degraded channels: " + ", ".join(channels[:5]))
    if not focus:
        focus.append("No configured portfolio yet; refresh broad price, liquidity, volatility, and macro context")
    return focus[:8]


def _daily_phase(value: Mapping[str, Any] | None) -> str:
    if not isinstance(value, Mapping):
        return "unknown"
    return str(value.get("phase") or value.get("cycle_phase") or "unknown")


def _float(value: Any) -> float:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return 0.0
