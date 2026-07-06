"""Validate Atlas OS Runtime Daemon v0.1 infrastructure."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.event_source import SimulatedMarketEventSource
from runtime.output_logger import RuntimeOutputLogger, read_runtime_log
from runtime.scheduler import RuntimeScheduleConfig, next_run_time


class FailingOnceEventSource:
    def __init__(self) -> None:
        self.calls = 0

    def get_event(self) -> dict:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("simulated event source failure")
        return {
            "timestamp": "2026-07-06T00:00:00+00:00",
            "type": "attention",
            "payload": {"attention": "rising"},
            "source": "simulated_failure_recovery",
        }


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        log_path = str(root / "atlas_runtime.log")
        db_path = str(root / "atlas_runtime.sqlite")
        inbox_dir = str(root / "inbox")

        schedule = RuntimeScheduleConfig(interval_seconds=10)
        _assert(next_run_time(schedule) > schedule.created_at, "next_run_time should be in the future")

        daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                interval_seconds=10,
                max_cycles=3,
                log_path=log_path,
                db_path=db_path,
                inbox_dir=inbox_dir,
                no_sleep=True,
            ),
            event_source=SimulatedMarketEventSource(),
        )
        daemon.run_forever()
        records = read_runtime_log(log_path=log_path, limit=3)
        _assert(len(records) == 3, "daemon should write three tick logs")
        for record in records:
            for key in ("timestamp", "event", "cognition_summary", "regime_state", "decision_brief", "system_metrics"):
                _assert(key in record, f"runtime log missing {key}")
            _assert(record["system_metrics"]["status"] == "success", "tick should succeed")
            _assert(record["decision_brief"]["available"] is True, "decision brief metadata missing")
            _assert(record["system_metrics"]["no_trading_execution"] is True, "daemon must not trade")

        failing_log = str(root / "failing_atlas_runtime.log")
        failing_daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                interval_seconds=10,
                max_cycles=2,
                log_path=failing_log,
                db_path=str(root / "failing.sqlite"),
                inbox_dir=str(root / "failing_inbox"),
                no_sleep=True,
            ),
            event_source=FailingOnceEventSource(),
        )
        failing_daemon.run_forever()
        failure_records = read_runtime_log(log_path=failing_log, limit=2)
        _assert(failure_records[0]["system_metrics"]["status"] == "failure", "first tick should log failure")
        _assert(failure_records[1]["system_metrics"]["status"] == "success", "daemon should recover on next tick")

    print("Runtime Daemon v0.1 validation PASS")


if __name__ == "__main__":
    main()
