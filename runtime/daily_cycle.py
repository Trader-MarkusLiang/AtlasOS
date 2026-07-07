"""Autonomous daily operating cycle metadata for the runtime daemon.

This module labels each tick with the current operating phase and required
read-only checks. It does not execute trades, mutate portfolios, or bypass CDE.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    from runtime.forecast_ledger import list_forecasts
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.forecast_ledger import list_forecasts


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
