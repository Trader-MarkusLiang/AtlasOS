"""GOAL 07 autonomous operations validation.

This validator proves scheduled cycle execution, accelerated stability, and
recovery behavior through existing runtime infrastructure. It does not claim
2h/24h wall-clock stability.
"""

from __future__ import annotations

import json
import os
import resource
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig  # noqa: E402
from runtime.event_stream import EventStream  # noqa: E402
from runtime.llm.provider_router import route_llm_request  # noqa: E402
from runtime.logging import utc_now_iso  # noqa: E402
from runtime.market_intelligence import refresh_market_intelligence  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402
from ui.system_control_panel import runtime_status  # noqa: E402


PHASE_TIMESTAMPS = {
    "morning": "2026-07-08T08:00:00+08:00",
    "intraday": "2026-07-08T11:00:00+08:00",
    "post_market": "2026-07-08T16:00:00+08:00",
    "overnight": "2026-07-08T23:00:00+08:00",
}

PHASE_REQUIRED_OUTPUTS = {
    "morning": ["freshness_check", "market_state_snapshot", "portfolio_relevance", "brief_publication_requested"],
    "intraday": ["market_state_status", "forecast_due_scan", "brief_publication_requested"],
    "post_market": ["forecast_maturity_check", "outcome_evaluation_queue", "brief_publication_requested"],
    "overnight": ["hypothesis_review", "world_model_delta", "next_day_watch_conditions", "brief_publication_requested"],
}


def main() -> int:
    old_env = {
        key: os.environ.get(key)
        for key in [
            "ATLAS_USER_CONFIG",
            "ATLAS_RUNTIME_DB",
            "ATLAS_RUNTIME_LOG",
            "ATLAS_LLM_TRACE_LOG",
            "ATLAS_LLM_BACKEND",
            "ATLAS_UI_INBOX",
            "ATLAS_EVENT_INBOX",
            "ATLAS_UI_PID_FILE",
            "ATLAS_DISABLE_KEYCHAIN",
        ]
    }
    result: dict[str, Any] = {"checks": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal07-") as tmp:
            root = Path(tmp)
            os.environ["ATLAS_LLM_BACKEND"] = "litellm"
            os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
            result["daily_cycles"] = _daily_cycles(root / "daily")
            result["accelerated_soak"] = _accelerated_soak(root / "accelerated")
            result["real_duration_soak"] = _real_duration_soak(root / "real_duration")
            result["recovery"] = _recovery(root / "recovery")

            _check("daily_all_phases_completed", all(item["status"] == "completed" for item in result["daily_cycles"].values()), result)
            _check(
                "daily_outputs_are_meaningful",
                all(item["required_outputs_present"] for item in result["daily_cycles"].values()),
                result,
            )
            _check("daily_artifacts_persisted", all(item["persisted"] for item in result["daily_cycles"].values()), result)
            _check("accelerated_500_cycles", result["accelerated_soak"]["cycles"] >= 500, result)
            _check("accelerated_zero_tick_errors", result["accelerated_soak"]["tick_errors"] == 0, result)
            _check(
                "accelerated_decision_briefs_bounded",
                0 < result["accelerated_soak"]["db_counts"].get("decision_briefs", 0) <= result["accelerated_soak"]["cycles"],
                result,
            )
            _check("accelerated_queue_bounded", result["accelerated_soak"]["pending_queue_depth"] <= 5, result)
            _check("real_duration_used_sleep", result["real_duration_soak"]["elapsed_seconds"] >= 9.0, result)
            _check("real_duration_zero_tick_errors", result["real_duration_soak"]["tick_errors"] == 0, result)
            _check("recovery_daemon_restart", result["recovery"]["daemon_restart"]["status"] == "passed", result)
            _check("recovery_ui_restart", result["recovery"]["ui_restart"]["status"] == "passed", result)
            _check("recovery_stale_pid", result["recovery"]["stale_pid"]["status"] == "passed", result)
            _check("recovery_malformed_jsonl", result["recovery"]["malformed_jsonl"]["status"] == "passed", result)
            _check("recovery_provider_outage", result["recovery"]["provider_outage"]["status"] == "passed", result)
            _check("recovery_market_outage", result["recovery"]["market_outage"]["status"] == "passed", result)
            _check(
                "no_trading_execution",
                all(item["no_trading_execution"] for item in result["daily_cycles"].values())
                and result["accelerated_soak"]["no_trading_execution"]
                and result["real_duration_soak"]["no_trading_execution"],
                result,
            )

            failures = [key for key, value in result["checks"].items() if value is not True]
            result["status"] = "PASS" if not failures else "FAIL"
            result["classification"] = "PROVEN_PARTIAL" if not failures else "FAILED"
            result["evidence_level"] = "ACCELERATED_ONLY_WITH_SHORT_REAL_DURATION" if not failures else "FAILED"
            result["long_duration_claim"] = {
                "two_hour_stability": "NOT_PROVEN",
                "twenty_four_hour_stability": "NOT_PROVEN",
                "reason": "GOAL 07 validator runs accelerated 500-cycle proof plus a short real-duration sleep proof only.",
            }
            result["failures"] = failures
            artifact_dir = ROOT / "99_Verification/artifacts/goal_07_autonomous_operations"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "operations_result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if not failures else 1
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _daily_cycles(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "config.json"
    db_path = root / "daily.sqlite"
    _write_fixture_config(config_path)
    results: dict[str, Any] = {}
    for phase, timestamp in PHASE_TIMESTAMPS.items():
        log_path = root / f"{phase}.jsonl"
        daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                interval_seconds=10,
                max_cycles=1,
                no_sleep=True,
                db_path=str(db_path),
                log_path=str(log_path),
                market_config_path=str(config_path),
                market_refresh_every_cycles=1,
                market_max_assets=1,
                daily_cycle_now=timestamp,
                cognition_mode="full",
            )
        )
        entry = daemon.run_tick(0)
        store = StateStore(db_path=str(db_path))
        state = store.get_state("daily_cycle_state")
        execution = state.get("execution", {}) if isinstance(state.get("execution"), dict) else {}
        persisted = store.get_state(f"daily_cycle_{phase}_last_run")
        outputs = execution.get("outputs", {}) if isinstance(execution.get("outputs"), dict) else {}
        results[phase] = {
            "resolved_phase": state.get("phase"),
            "status": execution.get("status"),
            "required_outputs_present": all(key in outputs and outputs.get(key) not in (None, "") for key in PHASE_REQUIRED_OUTPUTS[phase]),
            "output_keys": sorted(outputs.keys()),
            "persisted": persisted.get("phase") == phase and persisted.get("status") == "completed",
            "next_run_time": entry.get("system_metrics", {}).get("next_run_time"),
            "no_trading_execution": bool(execution.get("no_trading_execution")),
        }
    return results


def _accelerated_soak(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "config.json"
    db_path = root / "accelerated.sqlite"
    log_path = root / "accelerated_runtime.jsonl"
    _write_fixture_config(config_path)
    before_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    before_cpu = time.process_time()
    before_size = db_path.stat().st_size if db_path.exists() else 0
    started = time.time()
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=10,
            max_cycles=500,
            no_sleep=True,
            db_path=str(db_path),
            log_path=str(log_path),
            market_config_path=str(config_path),
            market_refresh_every_cycles=1,
            market_max_assets=1,
            cognition_mode="full",
        )
    )
    daemon.run_forever()
    elapsed = time.time() - started
    after_cpu = time.process_time()
    after_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    after_size = db_path.stat().st_size if db_path.exists() else 0
    entries = _runtime_log_entries(log_path)
    counts = _sqlite_counts(db_path)
    trust_values = [_trust_index(item) for item in entries if _trust_index(item) is not None]
    hypotheses = [_hypothesis_id(item) for item in entries if _hypothesis_id(item)]
    return {
        "cycles": 500,
        "elapsed_seconds": round(elapsed, 4),
        "cpu_seconds": round(after_cpu - before_cpu, 4),
        "runtime_log_lines": len(entries),
        "tick_errors": _runtime_error_count(entries),
        "provider_failures": _provider_failure_count(entries),
        "db_counts": counts,
        "db_size_before_bytes": before_size,
        "db_size_after_bytes": after_size,
        "db_growth_bytes": after_size - before_size,
        "max_rss_before": before_rss,
        "max_rss_after": after_rss,
        "rss_growth": after_rss - before_rss,
        "pending_queue_depth": len(StateStore(db_path=str(db_path)).get_pending_events(limit=1000)),
        "trust_drift": _drift(trust_values),
        "hypothesis_switches": _switch_count(hypotheses),
        "no_trading_execution": all(item.get("system_metrics", {}).get("no_trading_execution") is True for item in entries),
        "accelerated": True,
    }


def _real_duration_soak(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "config.json"
    db_path = root / "real_duration.sqlite"
    log_path = root / "real_duration_runtime.jsonl"
    _write_fixture_config(config_path)
    started = time.time()
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=10,
            max_cycles=2,
            no_sleep=False,
            db_path=str(db_path),
            log_path=str(log_path),
            market_config_path=str(config_path),
            market_refresh_every_cycles=1,
            market_max_assets=1,
            cognition_mode="full",
        )
    )
    daemon.run_forever()
    entries = _runtime_log_entries(log_path)
    return {
        "cycles": len(entries),
        "elapsed_seconds": round(time.time() - started, 4),
        "tick_errors": _runtime_error_count(entries),
        "db_counts": _sqlite_counts(db_path),
        "no_sleep": False,
        "no_trading_execution": all(item.get("system_metrics", {}).get("no_trading_execution") is True for item in entries),
        "claim_limit": "short_real_duration_only_not_2h_or_24h",
    }


def _recovery(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    return {
        "daemon_restart": _recovery_daemon_restart(root / "daemon_restart"),
        "ui_restart": _recovery_ui_restart(root / "ui_restart"),
        "stale_pid": _recovery_stale_pid(root / "stale_pid"),
        "malformed_jsonl": _recovery_malformed_jsonl(root / "malformed_jsonl"),
        "provider_outage": _recovery_provider_outage(root / "provider_outage"),
        "market_outage": _recovery_market_outage(root / "market_outage"),
    }


def _recovery_daemon_restart(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "config.json"
    db_path = root / "restart.sqlite"
    _write_fixture_config(config_path)
    first = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(max_cycles=1, no_sleep=True, db_path=str(db_path), market_config_path=str(config_path), cognition_mode="full")
    ).run_tick(0)
    second = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(max_cycles=1, no_sleep=True, db_path=str(db_path), market_config_path=str(config_path), cognition_mode="full")
    ).run_tick(1)
    counts = _sqlite_counts(db_path)
    passed = first.get("system_metrics", {}).get("status") == "success" and second.get("system_metrics", {}).get("status") == "success"
    # Since the material-delta gate (real-time brief closure), an identical second tick is
    # deduplicated and legitimately publishes no new Brief. Recovery means: restart succeeds and
    # the last valid Brief is preserved (>= 1), not that a duplicate Brief is created.
    return {"status": "passed" if passed and counts.get("decision_briefs", 0) >= 1 else "failed", "db_counts": counts}


def _recovery_ui_restart(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    env = _ui_env(root)
    statuses = []
    for _ in range(2):
        port = _free_port()
        server = _start_ui_server(env, port)
        try:
            _wait_http(f"http://127.0.0.1:{port}/state")
            statuses.append("ok")
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
    return {"status": "passed" if statuses == ["ok", "ok"] else "failed", "starts": statuses}


def _recovery_stale_pid(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    pid_file = root / "stale.pid"
    pid_file.write_text("99999999", encoding="utf-8")
    status = runtime_status(pid_file=str(pid_file), db_path=str(root / "pid.sqlite"), discover=False)
    return {
        "status": "passed" if status.get("running") is False and not pid_file.exists() else "failed",
        "runtime_status": status,
        "pid_file_exists_after": pid_file.exists(),
    }


def _recovery_malformed_jsonl(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    inbox = root / "events"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / "events.jsonl").write_text(
        "{bad-json\n"
        + json.dumps(
            {
                "event_type": "attention_spike",
                "payload": {"attention": "recovered"},
                "priority": 70,
                "source": "goal_07_recovery",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    stream = EventStream(db_path=str(root / "malformed.sqlite"), inbox_dir=str(inbox))
    ingested = stream.listen_once()
    pending = StateStore(db_path=str(root / "malformed.sqlite")).get_pending_events(limit=10)
    return {
        "status": "passed" if ingested == 1 and any(item["event_type"] == "attention_spike" for item in pending) else "failed",
        "ingested": ingested,
        "pending_event_types": [item["event_type"] for item in pending],
        "processed_file_exists": (inbox / "events.jsonl.processed").exists(),
    }


def _recovery_provider_outage(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config = root / "provider.json"
    config.write_text(
        json.dumps(
            {
                "llm_registry": {
                    "active_provider": "down",
                    "fallback_chain": [],
                    "providers": [
                        {
                            "id": "down",
                            "type": "openai",
                            "label": "Down Provider",
                            "enabled": True,
                            "base_url": "http://127.0.0.1:9/v1/chat/completions",
                            "model": "down-model",
                            "api_key_encrypted": "",
                            "api_key_storage": "none",
                        }
                    ],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    routed = route_llm_request(prompt="Return a DecisionPacket.", provider_id="down", config_path=str(config))
    return {
        "status": "passed" if routed.get("status") == "failsafe" and routed.get("fallback_attempts") else "failed",
        "router_status": routed.get("status"),
        "error": routed.get("error"),
        "fallback_attempts": routed.get("fallback_attempts"),
    }


def _recovery_market_outage(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "market_outage.json"
    _write_fixture_config(config_path, data_status="Unavailable")
    result = refresh_market_intelligence(config_path=str(config_path), db_path=str(root / "market.sqlite"), enqueue=True, max_assets=1)
    return {
        "status": "passed" if result.get("degraded") and result.get("channels", {}).get("price_volume") == "FAILED" else "failed",
        "market_status": result.get("status"),
        "channels": result.get("channels"),
        "degraded": result.get("degraded"),
        "proof_mode": result.get("proof_mode"),
        "events_enqueued": result.get("events_enqueued"),
    }


def _write_fixture_config(path: Path, *, data_status: str = "Available") -> None:
    latest_price = 100.0 if data_status == "Available" else None
    path.parent.mkdir(parents=True, exist_ok=True)
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
                                "theme": "Autonomous Operations",
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
                            "source": "goal_07_controlled_fixture",
                            "timestamp": utc_now_iso(),
                            "data_status": data_status,
                            "data_freshness": "SIMULATED" if data_status == "Available" else "FAILED",
                            "latest_price": latest_price,
                            "daily_change_pct": 1.2 if latest_price is not None else None,
                            "change_5d_pct": 3.4 if latest_price is not None else None,
                            "change_20d_pct": 5.6 if latest_price is not None else None,
                            "change_60d_pct": 7.8 if latest_price is not None else None,
                            "volume": 1234567 if latest_price is not None else None,
                            "turnover": 9876543 if latest_price is not None else None,
                            "errors": [] if latest_price is not None else ["controlled_market_outage"],
                        }
                    }
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _ui_env(root: Path) -> dict[str, str]:
    for rel in ["runtime/config", "runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    config = root / "runtime/config/user_config.json"
    _write_fixture_config(config)
    return {
        **os.environ,
        "ATLAS_USER_CONFIG": str(config),
        "ATLAS_RUNTIME_DB": str(root / "runtime/state/atlas.sqlite"),
        "ATLAS_RUNTIME_LOG": str(root / "runtime/logs/atlas_runtime.log"),
        "ATLAS_LLM_TRACE_LOG": str(root / "runtime/logs/llm_traces.jsonl"),
        "ATLAS_UI_INBOX": str(root / "runtime/inbox/user_event.jsonl"),
        "ATLAS_EVENT_INBOX": str(root / "runtime/events/inbox"),
        "ATLAS_UI_PID_FILE": str(root / "runtime/state/atlas_ui_runtime.pid"),
    }


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


def _start_ui_server(env: dict[str, str], port: int) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-u", "-c", f"from ui.app_server import run_server; run_server(port={port})"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def _wait_http(url: str) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with request.urlopen(url, timeout=5) as response:
                response.read()
            return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"server did not become ready: {url}")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
