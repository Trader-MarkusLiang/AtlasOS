"""Atlas OS minimal runtime scheduler entrypoints.

These functions can be called manually, by cron, or by a future scheduler. They
do not execute trades, modify portfolio weights, or bypass CDE.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    from runtime.orchestrator import TRIGGER_DAILY, TRIGGER_EVENT, TRIGGER_WEEKLY, run_runtime
except ModuleNotFoundError:  # pragma: no cover - supports direct script usage
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.orchestrator import TRIGGER_DAILY, TRIGGER_EVENT, TRIGGER_WEEKLY, run_runtime


def daily_run(log_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the daily Atlas runtime route."""

    return run_runtime(TRIGGER_DAILY, log_path=log_path)


def weekly_run(log_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the weekly Atlas runtime route with simulation placeholder only."""

    return run_runtime(TRIGGER_WEEKLY, log_path=log_path)


def event_trigger(event_type: str, log_path: Optional[str] = None) -> Dict[str, Any]:
    """Run event-triggered Atlas runtime route."""

    if not event_type or not event_type.strip():
        raise ValueError("event_type is required")
    return run_runtime(TRIGGER_EVENT, event_type=event_type.strip(), log_path=log_path)


if __name__ == "__main__":
    result = daily_run()
    print(result["decision_brief"])
