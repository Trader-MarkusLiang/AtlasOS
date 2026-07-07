"""Autonomous daily operating cycle metadata for the runtime daemon.

This module labels each tick with the current operating phase and required
read-only checks. It does not execute trades, mutate portfolios, or bypass CDE.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

try:
    from runtime.forecast_ledger import list_forecasts
    from runtime.logging import utc_now_iso
    from runtime.portfolio_context import build_portfolio_context
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.forecast_ledger import list_forecasts
    from runtime.logging import utc_now_iso
    from runtime.portfolio_context import build_portfolio_context
    from runtime.state_store import StateStore


PHASE_TASKS = {
    "morning": [
        "data_freshness_check",
        "overnight_signal_scan",
        "portfolio_relevance_scan",
        "open_forecast_review",
        "morning_atlas_brief",
    ],
    "intraday": [
        "scheduled_market_refresh",
        "anomaly_detection",
        "attention_narrative_change_scan",
        "portfolio_relevance_trigger_scan",
    ],
    "post_market": [
        "closing_state_synthesis",
        "forecast_maturation_check",
        "outcome_evaluation_queue",
        "decision_brief_archive",
    ],
    "overnight": [
        "deeper_synthesis",
        "hypothesis_review",
        "world_model_delta_review",
        "prediction_bias_review",
        "next_day_watch_conditions",
    ],
}


def current_daily_cycle(
    *,
    now: datetime | None = None,
    timezone: str = "Asia/Shanghai",
    db_path: str | None = None,
) -> dict[str, Any]:
    """Return current daily operating phase and safe check list."""

    current = now or datetime.now(ZoneInfo(timezone))
    if current.tzinfo is None:
        current = current.replace(tzinfo=ZoneInfo(timezone))
    hour = current.hour
    if 7 <= hour < 10:
        phase = "morning"
    elif 10 <= hour < 15:
        phase = "intraday"
    elif 15 <= hour < 19:
        phase = "post_market"
    else:
        phase = "overnight"
    ledger = list_forecasts(db_path=db_path, limit=500)
    metrics = ledger.get("metrics", {})
    return {
        "timestamp": current.isoformat(),
        "timezone": timezone,
        "phase": phase,
        "tasks": PHASE_TASKS[phase],
        "forecast_review": {
            "open": metrics.get("open", 0),
            "evaluated": metrics.get("evaluated", 0),
            "minimum_sample_size_met": metrics.get("minimum_sample_size_met", False),
            "sample_warning": ledger.get("sample_warning"),
        },
        "read_only": True,
        "no_trading_execution": True,
    }


def run_daily_cycle_phase(
    phase: str,
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Execute one read-only daily-cycle phase and persist evidence."""

    clean_phase = str(phase or "").strip().lower()
    if clean_phase not in PHASE_TASKS:
        return {
            "status": "error",
            "error": "unknown_daily_cycle_phase",
            "phase": clean_phase or "unknown",
            "read_only": True,
            "no_trading_execution": True,
        }
    if clean_phase == "morning":
        return run_morning_cycle(config_path=config_path, db_path=db_path, now=now)
    if clean_phase == "intraday":
        return run_intraday_cycle(config_path=config_path, db_path=db_path, now=now)
    if clean_phase == "post_market":
        return run_post_market_cycle(config_path=config_path, db_path=db_path, now=now)
    return run_overnight_cycle(config_path=config_path, db_path=db_path, now=now)


def run_morning_cycle(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    market = _safe_market_refresh(config_path=config_path, db_path=db_path)
    portfolio = build_portfolio_context(config_path=config_path)
    ledger = list_forecasts(db_path=db_path, limit=500)
    outputs = {
        "freshness_check": market.get("channels", {}),
        "overnight_signal_synthesis": _market_synthesis(market),
        "portfolio_relevance": _portfolio_relevance(portfolio),
        "open_forecast_count": ledger.get("metrics", {}).get("open", 0),
        "produced_brief_id": _brief_id("morning"),
    }
    return _persist_cycle("morning", outputs, market=market, portfolio=portfolio, ledger=ledger, db_path=db_path, now=now)


def run_intraday_cycle(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    market = _safe_market_refresh(config_path=config_path, db_path=db_path)
    outputs = {
        "refresh_status": market.get("status"),
        "anomaly_check": "degraded" if market.get("degraded") else "clear",
        "attention_regime_update": _attention_update(market),
        "portfolio_relevance_triggers": _portfolio_event_count(market),
        "produced_brief_id": _brief_id("intraday"),
    }
    return _persist_cycle("intraday", outputs, market=market, db_path=db_path, now=now)


def run_post_market_cycle(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    ledger = list_forecasts(db_path=db_path, limit=500)
    metrics = ledger.get("metrics", {})
    outputs = {
        "closing_state_synthesis": "forecast_review_only",
        "forecast_maturity_check": {
            "open": metrics.get("open", 0),
            "matured": metrics.get("matured", 0),
            "evaluated": metrics.get("evaluated", 0),
        },
        "outcome_evaluation_queue": metrics.get("matured", 0),
        "produced_brief_id": _brief_id("post_market"),
    }
    return _persist_cycle("post_market", outputs, ledger=ledger, db_path=db_path, now=now)


def run_overnight_cycle(
    *,
    config_path: str | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    store = StateStore(db_path=db_path)
    hypothesis = store.get_state("causal_hypothesis_memory")
    cognition = store.get_state("cognition_state")
    outputs = {
        "hypothesis_review": {
            "active_hypothesis_id": hypothesis.get("active_hypothesis_id"),
            "history_count": len(hypothesis.get("history", [])) if isinstance(hypothesis.get("history"), list) else 0,
            "forecast_outcome_count": len(hypothesis.get("forecast_outcome_history", []))
            if isinstance(hypothesis.get("forecast_outcome_history"), list)
            else 0,
        },
        "world_model_delta": _world_model_delta(cognition),
        "next_day_watch_conditions": _next_day_watch_conditions(cognition),
        "produced_brief_id": _brief_id("overnight"),
    }
    return _persist_cycle("overnight", outputs, db_path=db_path, now=now)


def dispatch_current_daily_cycle(
    *,
    now: datetime | None = None,
    timezone: str = "Asia/Shanghai",
    config_path: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Determine the current phase, execute it, and return persisted evidence."""

    metadata = current_daily_cycle(now=now, timezone=timezone, db_path=db_path)
    execution = run_daily_cycle_phase(
        str(metadata.get("phase")),
        config_path=config_path,
        db_path=db_path,
        now=now,
    )
    return {**metadata, "execution": execution}


def _persist_cycle(
    phase: str,
    outputs: Mapping[str, Any],
    *,
    market: Mapping[str, Any] | None = None,
    portfolio: Mapping[str, Any] | None = None,
    ledger: Mapping[str, Any] | None = None,
    db_path: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    started = utc_now_iso()
    completed = utc_now_iso()
    degraded = _degraded_capabilities(market or {})
    record = {
        "status": "completed",
        "phase": phase,
        "started_at": started,
        "completed_at": completed,
        "inputs": {
            "market_status": (market or {}).get("status", "not_run"),
            "portfolio_status": (portfolio or {}).get("status", "not_loaded"),
            "forecast_metrics": (ledger or {}).get("metrics", {}),
            "timestamp": now.isoformat() if now else started,
        },
        "outputs": dict(outputs),
        "errors": [],
        "degraded_capabilities": degraded,
        "produced_brief_id": outputs.get("produced_brief_id"),
        "read_only": True,
        "no_trading_execution": True,
    }
    store = StateStore(db_path=db_path)
    store.set_state(f"daily_cycle_{phase}_last_run", record)
    store.set_state("daily_cycle_last_execution", record)
    store.append_system_log({"trigger_type": "daily_cycle_execution", **record})
    return record


def _safe_market_refresh(config_path: str | None, db_path: str | None) -> dict[str, Any]:
    try:
        from runtime.market_intelligence import refresh_market_intelligence

        return refresh_market_intelligence(config_path=config_path, db_path=db_path, enqueue=False)
    except Exception as exc:
        return {
            "status": "FAILED",
            "error": str(exc)[:240],
            "channels": {},
            "observations": [],
            "degraded": True,
        }


def _market_synthesis(market: Mapping[str, Any]) -> dict[str, Any]:
    observations = market.get("observations", []) if isinstance(market.get("observations"), list) else []
    return {
        "observation_count": len(observations),
        "events_prepared": market.get("events_prepared", 0),
        "proof_mode": market.get("proof_mode", "UNKNOWN"),
    }


def _portfolio_relevance(portfolio: Mapping[str, Any]) -> dict[str, Any]:
    exposure = portfolio.get("exposure_map", {}) if isinstance(portfolio.get("exposure_map"), Mapping) else {}
    return {
        "status": portfolio.get("status", "missing"),
        "exposure_sum_pct": portfolio.get("exposure_sum_pct", 0),
        "portfolio_relevance_score": exposure.get("portfolio_relevance_score", 0),
        "regime_sensitivity": exposure.get("regime_sensitivity", "unknown"),
    }


def _attention_update(market: Mapping[str, Any]) -> dict[str, Any]:
    channels = market.get("channels", {}) if isinstance(market.get("channels"), Mapping) else {}
    return {
        "narrative_attention_status": channels.get("narrative_attention", "NOT_CONFIGURED"),
        "volatility_status": channels.get("volatility", "NOT_CONFIGURED"),
        "liquidity_status": channels.get("liquidity_proxy", "NOT_CONFIGURED"),
    }


def _portfolio_event_count(market: Mapping[str, Any]) -> int:
    return int(market.get("events_prepared", 0) or 0)


def _world_model_delta(cognition: Mapping[str, Any]) -> str:
    world = cognition.get("world_model", {}) if isinstance(cognition.get("world_model"), Mapping) else {}
    if not world:
        return "No World Model Change Today"
    return "World model state reviewed from latest runtime cognition."


def _next_day_watch_conditions(cognition: Mapping[str, Any]) -> list[str]:
    fusion = cognition.get("fusion", {}) if isinstance(cognition.get("fusion"), Mapping) else {}
    conditions = []
    if fusion.get("liquidity_condition"):
        conditions.append(f"Liquidity: {fusion.get('liquidity_condition')}")
    if fusion.get("volatility_regime"):
        conditions.append(f"Volatility: {fusion.get('volatility_regime')}")
    return conditions or ["Waiting for sufficient cognitive signal"]


def _degraded_capabilities(market: Mapping[str, Any]) -> dict[str, str]:
    channels = market.get("channels", {}) if isinstance(market.get("channels"), Mapping) else {}
    return {key: value for key, value in channels.items() if value not in {"LIVE", "DELAYED", "CACHED"}}


def _brief_id(phase: str) -> str:
    return f"daily-cycle-{phase}-{utc_now_iso()}"
