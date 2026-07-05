"""Validate Atlas Runtime v0.1 Step 1 scheduler and orchestrator backbone."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.scheduler import daily_run, event_trigger, weekly_run


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = str(Path(temp_dir) / "runtime_runs.jsonl")

        daily = daily_run(log_path=log_path)
        weekly = weekly_run(log_path=log_path)
        event = event_trigger("market_anomaly", log_path=log_path)

        _assert(daily["status"] == "success", "daily_run should succeed")
        _assert(daily["pipeline"] == "Live Analysis", "daily_run should route to Live Analysis")
        _assert("atlas-daily" in daily["modules_executed"], "daily_run should call atlas-daily boundary")

        _assert(weekly["status"] == "success", "weekly_run should succeed")
        _assert(weekly["pipeline"] == "Simulation Placeholder", "weekly_run should route to placeholder")
        _assert(
            "simulation_placeholder" in weekly["modules_executed"],
            "weekly_run must not implement a real simulation engine",
        )

        _assert(event["status"] == "success", "event_trigger should succeed")
        _assert(event["pipeline"] == "Risk Check", "event_trigger should route to Risk Check")
        _assert(
            "attention_summary_placeholder" in event["modules_executed"],
            "event_trigger must keep attention summary as placeholder only",
        )

        for result in (daily, weekly, event):
            brief = result["decision_brief"]
            _assert("Atlas Decision Brief (Runtime Generated)" in brief, "decision brief title missing")
            _assert("No automatic trading execution" in brief, "trading safety line missing")
            _assert("No portfolio modification" in brief, "portfolio safety line missing")
            _assert("No CDE logic change" in brief, "CDE safety line missing")
            _assert("Portfolio State:" in brief, "portfolio state block missing")

        records = [json.loads(line) for line in Path(log_path).read_text(encoding="utf-8").splitlines()]
        _assert(len(records) == 3, "expected three JSONL runtime records")
        _assert(
            [record["trigger_type"] for record in records] == ["daily_run", "weekly_run", "event_trigger"],
            "log trigger order mismatch",
        )
        _assert(
            all("decision_brief" not in record for record in records),
            "runtime log must not store full decision brief or private portfolio content",
        )

    print("Runtime v0.1 Step 1 validation PASS")


if __name__ == "__main__":
    main()
