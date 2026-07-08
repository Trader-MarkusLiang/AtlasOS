"""Run GOAL 07 long real-duration daemon soak.

This script starts the Atlas runtime daemon as a subprocess, lets it run with
real scheduler sleep, samples process/resource metrics, and writes a compact
summary artifact. Raw runtime logs and SQLite state stay in a temporary
directory and are not committed.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "99_Verification/artifacts/goal_07_autonomous_operations/long_soak_2h_result.json"


def main() -> int:
    args = _parser().parse_args()
    interval = int(args.interval)
    cycles = int(args.cycles)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="atlas-goal07-long-soak-") as tmp:
        root = Path(tmp)
        config_path = root / "runtime/config/user_config.json"
        db_path = root / "runtime/state/atlas_long_soak.sqlite"
        log_path = root / "runtime/logs/atlas_long_soak.jsonl"
        inbox_dir = root / "runtime/events/inbox"
        ui_inbox = root / "runtime/inbox/user_event.jsonl"
        for path in [config_path.parent, db_path.parent, log_path.parent, inbox_dir, ui_inbox.parent]:
            path.mkdir(parents=True, exist_ok=True)
        _write_fixture_config(config_path)
        env = {
            **os.environ,
            "ATLAS_USER_CONFIG": str(config_path),
            "ATLAS_RUNTIME_DB": str(db_path),
            "ATLAS_RUNTIME_LOG": str(log_path),
            "ATLAS_LLM_TRACE_LOG": str(root / "runtime/logs/llm_traces.jsonl"),
            "ATLAS_UI_INBOX": str(ui_inbox),
            "ATLAS_EVENT_INBOX": str(inbox_dir),
            "ATLAS_LLM_BACKEND": "litellm",
            "ATLAS_DISABLE_KEYCHAIN": "1",
        }
        cmd = [
            sys.executable,
            "runtime/atlas_runtime_daemon.py",
            "--interval",
            str(interval),
            "--max-cycles",
            str(cycles),
            "--db-path",
            str(db_path),
            "--log-path",
            str(log_path),
            "--inbox-dir",
            str(inbox_dir),
            "--ui-inbox-path",
            str(ui_inbox),
            "--market-config-path",
            str(config_path),
            "--market-refresh-every-cycles",
            "1",
            "--market-max-assets",
            "1",
        ]
        started = time.time()
        started_at = _now()
        process = subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        samples: list[dict[str, Any]] = []
        interrupted = False
        try:
            while process.poll() is None:
                samples.append(_process_sample(process.pid, started))
                _print_progress(process.pid, started, log_path, samples[-1])
                time.sleep(float(args.sample_every))
        except KeyboardInterrupt:
            interrupted = True
            process.send_signal(signal.SIGTERM)
        try:
            returncode = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            returncode = process.wait(timeout=30)
        ended = time.time()
        all_entries = _runtime_log_entries(log_path)
        entries = _runtime_tick_entries(all_entries)
        no_trading_execution = all(item.get("system_metrics", {}).get("no_trading_execution") is True for item in entries)
        passed = (
            returncode == 0
            and not interrupted
            and _runtime_error_count(entries) == 0
            and len(entries) >= cycles
            and no_trading_execution
        )
        summary = {
            "status": "PASS" if passed else "FAIL",
            "classification": "REAL_DURATION_2H_PROVEN"
            if ended - started >= float(args.min_seconds) and passed
            else "REAL_DURATION_SHORT_OR_FAILED",
            "started_at": started_at,
            "ended_at": _now(),
            "pid": process.pid,
            "command": cmd,
            "runtime_root": str(root),
            "interval_seconds": interval,
            "target_cycles": cycles,
            "min_seconds": float(args.min_seconds),
            "elapsed_seconds": round(ended - started, 4),
            "returncode": returncode,
            "interrupted": interrupted,
            "raw_log_lines": len(all_entries),
            "runtime_log_lines": len(entries),
            "tick_errors": _runtime_error_count(entries),
            "provider_failures": _provider_failure_count(entries),
            "market_failure_ticks": _market_failure_count(entries),
            "db_counts": _sqlite_counts(db_path),
            "db_size_bytes": db_path.stat().st_size if db_path.exists() else 0,
            "pending_queue_depth": len(_pending_events(db_path)),
            "trust_drift": _drift([value for value in (_trust_index(item) for item in entries) if value is not None]),
            "hypothesis_switches": _switch_count([value for value in (_hypothesis_id(item) for item in entries) if value]),
            "daily_cycle_phases": _phase_counts(entries),
            "no_trading_execution": no_trading_execution,
            "samples": samples,
            "sample_count": len(samples),
            "max_rss_kb": max((int(item.get("rss_kb") or 0) for item in samples), default=0),
            "max_cpu_pct": max((float(item.get("cpu_pct") or 0.0) for item in samples), default=0.0),
            "raw_logs_committed": False,
        }
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if summary["status"] == "PASS" else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GOAL 07 long real-duration soak")
    parser.add_argument("--interval", type=int, default=10, choices=[10, 30, 60, 300])
    parser.add_argument("--cycles", type=int, default=721)
    parser.add_argument("--min-seconds", type=float, default=7200.0)
    parser.add_argument("--sample-every", type=float, default=30.0)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser


def _write_fixture_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "assets": {
                    "portfolio_json": json.dumps(
                        [
                            {
                                "asset": "GOAL07",
                                "market": "US",
                                "portfolio_percentage": 40,
                                "theme": "Long Soak",
                                "role": "Runtime validation",
                            }
                        ]
                    ),
                    "asset_list": ["GOAL07"],
                    "weights": {"GOAL07": 40},
                },
                "market_intelligence": {
                    "fixtures": {
                        "GOAL07": {
                            "source": "goal_07_long_soak_fixture",
                            "timestamp": _now(),
                            "data_status": "Available",
                            "data_freshness": "SIMULATED",
                            "latest_price": 100.0,
                            "daily_change_pct": 1.2,
                            "change_5d_pct": 3.4,
                            "change_20d_pct": 5.6,
                            "change_60d_pct": 7.8,
                            "volume": 1234567,
                            "turnover": 9876543,
                        }
                    }
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _process_sample(pid: int, started: float) -> dict[str, Any]:
    sample = {"elapsed_seconds": round(time.time() - started, 2), "timestamp": _now(), "pid": pid}
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "rss=", "-o", "%cpu=", "-o", "etime="],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
        parts = result.stdout.strip().split(None, 2)
        if len(parts) >= 2:
            sample["rss_kb"] = int(float(parts[0]))
            sample["cpu_pct"] = float(parts[1])
        if len(parts) == 3:
            sample["etime"] = parts[2].strip()
    except Exception as exc:
        sample["sample_error"] = str(exc)[:160]
    return sample


def _print_progress(pid: int, started: float, log_path: Path, sample: dict[str, Any]) -> None:
    elapsed = time.time() - started
    log_lines = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    print(
        json.dumps(
            {
                "progress": "goal07_long_soak",
                "pid": pid,
                "elapsed_seconds": round(elapsed, 1),
                "runtime_log_lines": log_lines,
                "rss_kb": sample.get("rss_kb"),
                "cpu_pct": sample.get("cpu_pct"),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )


def _runtime_log_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            entries.append({"system_metrics": {"status": "invalid_json"}})
            continue
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _runtime_tick_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in entries
        if isinstance(item.get("system_metrics"), dict)
        and item.get("system_metrics", {}).get("tick_index") is not None
    ]


def _runtime_error_count(entries: list[dict[str, Any]]) -> int:
    return sum(
        1
        for item in entries
        if item.get("system_metrics", {}).get("status") != "success" or item.get("system_metrics", {}).get("error")
    )


def _provider_failure_count(entries: list[dict[str, Any]]) -> int:
    count = 0
    for item in entries:
        packet = item.get("decision_brief", {}).get("decision_packet", {})
        trace = str(packet.get("reasoning_trace", "")) if isinstance(packet, dict) else ""
        if "not_installed" in trace or "provider" in trace or "failed" in trace:
            count += 1
    return count


def _market_failure_count(entries: list[dict[str, Any]]) -> int:
    count = 0
    for item in entries:
        channels = item.get("system_metrics", {}).get("market_channels", {})
        if isinstance(channels, dict) and any(value == "FAILED" for value in channels.values()):
            count += 1
    return count


def _sqlite_counts(db_path: Path) -> dict[str, int]:
    if not db_path.exists():
        return {}
    with sqlite3.connect(db_path) as conn:
        tables = [
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if not str(row[0]).startswith("sqlite_")
        ]
        return {table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in tables}


def _pending_events(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("SELECT event_id FROM events WHERE status = 'pending' LIMIT 10000").fetchall()
        except sqlite3.Error:
            return []
    return [dict(row) for row in rows]


def _trust_index(entry: dict[str, Any]) -> float | None:
    trust = entry.get("cognition_summary", {}).get("tick_result", {}).get("trust_score", {})
    if not isinstance(trust, dict):
        return None
    try:
        return float(trust.get("global_trust_index"))
    except (TypeError, ValueError):
        return None


def _hypothesis_id(entry: dict[str, Any]) -> str:
    value = entry.get("cognition_summary", {}).get("tick_result", {}).get("active_causal_hypothesis_id")
    return str(value or "")


def _drift(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"available": False}
    return {
        "available": True,
        "first": values[0],
        "last": values[-1],
        "min": min(values),
        "max": max(values),
        "delta": round(values[-1] - values[0], 4),
    }


def _switch_count(values: list[str]) -> int:
    return sum(1 for left, right in zip(values, values[1:]) if left != right)


def _phase_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in entries:
        phase = (
            item.get("system_metrics", {})
            .get("daily_cycle", {})
            .get("phase")
        )
        if phase:
            counts[str(phase)] = counts.get(str(phase), 0) + 1
    return counts


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
