"""Atlas OS lightweight runtime scheduler entrypoints.

These functions can be called manually, by the host loop, or by launchd. They do
not execute trades, modify portfolio weights, or bypass CDE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from runtime.orchestrator import (
        TRIGGER_DAILY,
        TRIGGER_EVENT,
        TRIGGER_INTRADAY,
        TRIGGER_WEEKLY,
        run_runtime,
    )
except ModuleNotFoundError:  # pragma: no cover - supports direct script usage
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.orchestrator import (
        TRIGGER_DAILY,
        TRIGGER_EVENT,
        TRIGGER_INTRADAY,
        TRIGGER_WEEKLY,
        run_runtime,
    )


SUPPORTED_EVENT_TYPES = {
    "market_open",
    "market_close",
    "market_anomaly",
    "attention_spike",
    "volume_price_breakout",
    "news_narrative_spike",
    "portfolio_drawdown",
    "volatility_spike",
    "user_input_event",
}

SUPPORTED_TICK_INTERVALS = {10, 30, 60, 300}


@dataclass(frozen=True)
class RuntimeScheduleConfig:
    """Tick interval configuration for background runtime loops."""

    interval_seconds: int = 60
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.interval_seconds not in SUPPORTED_TICK_INTERVALS:
            raise ValueError("interval_seconds must be one of 10, 30, 60, or 300")


def next_run_time(
    config: RuntimeScheduleConfig | None = None,
    *,
    from_time: datetime | None = None,
) -> datetime:
    """Return the next scheduler tick time."""

    schedule = config or RuntimeScheduleConfig()
    base = from_time or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return base + timedelta(seconds=schedule.interval_seconds)


def daily_run(
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt-5.5",
) -> Dict[str, Any]:
    """Run the daily Atlas runtime route."""

    return run_runtime(TRIGGER_DAILY, log_path=log_path, db_path=db_path, llm_model=llm_model)


def intraday_run(
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "claude-sonnet",
) -> Dict[str, Any]:
    """Run the intraday Atlas runtime route."""

    return run_runtime(TRIGGER_INTRADAY, log_path=log_path, db_path=db_path, llm_model=llm_model)


def weekly_run(
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt-5.5",
) -> Dict[str, Any]:
    """Run the weekly Atlas runtime route with simulation placeholder only."""

    return run_runtime(TRIGGER_WEEKLY, log_path=log_path, db_path=db_path, llm_model=llm_model)


def event_trigger(
    event_type: str,
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt-5.5",
) -> Dict[str, Any]:
    """Run event-triggered Atlas runtime route."""

    if not event_type or not event_type.strip():
        raise ValueError("event_type is required")
    normalized = event_type.strip()
    if normalized not in SUPPORTED_EVENT_TYPES:
        raise ValueError(f"unsupported event_type: {normalized}")
    return run_runtime(
        TRIGGER_EVENT,
        event_type=normalized,
        log_path=log_path,
        db_path=db_path,
        llm_model=llm_model,
    )


if __name__ == "__main__":
    result = daily_run()
    print(result["decision_brief"])
