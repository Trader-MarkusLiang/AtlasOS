"""GOAL 05 forecast accountability validation.

This validator uses supported runtime/UI API paths. It proves that forecasts
are recorded before outcomes, matured, evaluated, assigned error/calibration
metadata, and listed without creating trading authority.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig  # noqa: E402
from runtime.forecast_ledger import list_forecasts  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402


CASES = [
    ("goal05_hit", "breakout", "breakout confirmed", 0.7, None),
    ("goal05_miss", "liquidity stress", "risk appetite improved", 0.6, "INVALIDATED"),
    ("goal05_inconclusive", "attention expansion", "mixed evidence", 0.5, "INCONCLUSIVE"),
    ("goal05_high_confidence_miss", "risk off", "risk appetite improved", 0.95, "INVALIDATED"),
    ("goal05_low_confidence_hit", "attention", "attention expansion confirmed", 0.2, None),
]


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
        ]
    }
    server: subprocess.Popen[str] | None = None
    result: dict[str, Any] = {"checks": {}, "cases": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal05-") as tmp:
            root = Path(tmp)
            env = _temp_env(root)
            os.environ.update(env)
            os.environ["ATLAS_LLM_BACKEND"] = "litellm"

            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    max_cycles=1,
                    no_sleep=True,
                    db_path=env["ATLAS_RUNTIME_DB"],
                    log_path=env["ATLAS_RUNTIME_LOG"],
                    inbox_dir=env["ATLAS_EVENT_INBOX"],
                    market_refresh_enabled=False,
                    llm_model="gpt-5.5",
                )
            )
            tick = daemon.run_tick(0)
            store = StateStore(db_path=env["ATLAS_RUNTIME_DB"])
            runtime_forecasts = list_forecasts(db_path=env["ATLAS_RUNTIME_DB"], limit=10).get("forecasts", [])
            runtime_forecast = next((item for item in runtime_forecasts if str(item.get("forecast_id", "")).startswith("runtime-")), {})
            _check("daemon_tick_success", tick.get("system_metrics", {}).get("status") == "success", result)
            _check("runtime_forecast_created_open", runtime_forecast.get("status") == "OPEN", result)
            _check("runtime_forecast_has_lineage", bool(runtime_forecast.get("runtime_lineage", {}).get("decision_brief_id")), result)

            port = _free_port()
            server = _start_ui_server(env, port)
            base = f"http://127.0.0.1:{port}"
            _wait_http(base + "/predictions?format=json")

            evaluated = []
            for forecast_id, expected, actual, confidence, forced_status in CASES:
                created = _post_json(
                    base + "/predictions",
                    {
                        "forecast_id": forecast_id,
                        "horizon": "goal-05-controlled-window",
                        "subject": "goal_05_accountability",
                        "forecast_statement": f"{forecast_id} expected {expected}",
                        "expected_direction_state": expected,
                        "confidence": confidence,
                        "active_hypothesis": "H_GOAL_05_ACCOUNTABILITY",
                        "causal_drivers": ["attention", "liquidity"],
                        "invalidation_conditions": ["opposite outcome observed"],
                    },
                )
                matured = _post_json(
                    base + "/predictions/mature",
                    {"forecast_id": forecast_id, "maturity_reason": "goal_05_window_closed"},
                )
                outcome_payload = {"forecast_id": forecast_id, "actual_outcome": actual}
                if forced_status:
                    outcome_payload["status"] = forced_status
                evaluated_record = _post_json(base + "/predictions/evaluate", outcome_payload)
                result["cases"][forecast_id] = {
                    "created_status": created.get("status"),
                    "matured_status": matured.get("status"),
                    "final_status": evaluated_record.get("status"),
                    "prediction_error": evaluated_record.get("prediction_error"),
                    "calibration_error": evaluated_record.get("calibration_error"),
                    "lineage_events": [item.get("event") for item in evaluated_record.get("lineage", [])],
                }
                evaluated.append(evaluated_record)
                _check(f"{forecast_id}_created_open", created.get("status") == "OPEN", result)
                _check(f"{forecast_id}_matured", matured.get("status") == "MATURED", result)
                _check(f"{forecast_id}_evaluated", evaluated_record.get("status") in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}, result)
                _check(f"{forecast_id}_fields_present", _required_fields_present(evaluated_record), result)
                _check(f"{forecast_id}_lineage_complete", {"created", "matured", "evaluated"}.issubset(set(result["cases"][forecast_id]["lineage_events"])), result)

            ledger = json.loads(_get(base + "/predictions?format=json"))
            predictions_html = _get(base + "/predictions")
            statuses = {item.get("forecast_id"): item.get("status") for item in evaluated}
            _check("hit_verified", statuses.get("goal05_hit") == "VERIFIED", result)
            _check("miss_invalidated", statuses.get("goal05_miss") == "INVALIDATED", result)
            _check("inconclusive_recorded", statuses.get("goal05_inconclusive") == "INCONCLUSIVE", result)
            _check("high_confidence_miss_error", next(item for item in evaluated if item["forecast_id"] == "goal05_high_confidence_miss").get("calibration_error", 0) >= 0.9, result)
            _check("low_confidence_hit_recorded", statuses.get("goal05_low_confidence_hit") == "VERIFIED", result)
            _check("ledger_metrics_evaluated", ledger.get("metrics", {}).get("evaluated", 0) >= 5, result)
            _check("predictions_ui_visible", "goal05_hit" in predictions_html and "goal05_high_confidence_miss" in predictions_html, result)
            _check("no_trading_execution", ledger.get("no_trading_execution") is True, result)
            serialized = json.dumps({"ledger": ledger, "cases": result["cases"]}, ensure_ascii=False)
            _check("no_buy_sell_language", "Buy" not in serialized and "Sell" not in serialized, result)

            result["runtime_forecast"] = {
                "forecast_id": runtime_forecast.get("forecast_id"),
                "status": runtime_forecast.get("status"),
                "decision_brief_id": runtime_forecast.get("runtime_lineage", {}).get("decision_brief_id"),
            }
            result["metrics"] = ledger.get("metrics")
            failures = [key for key, value in result["checks"].items() if value is not True]
            result["status"] = "PASS" if not failures else "FAIL"
            result["failures"] = failures
            artifact_dir = ROOT / "99_Verification/artifacts/goal_05_forecast_accountability"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "lifecycle_result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if not failures else 1
    finally:
        if server:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _required_fields_present(record: dict[str, Any]) -> bool:
    return all(
        record.get(key) not in (None, "")
        for key in [
            "forecast_id",
            "created_at",
            "horizon",
            "subject",
            "expected_direction_state",
            "confidence",
            "active_hypothesis",
            "causal_drivers",
            "invalidation_conditions",
            "actual_outcome",
            "prediction_error",
            "calibration_error",
        ]
    )


def _temp_env(root: Path) -> dict[str, str]:
    for rel in ["runtime/config", "runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    config = root / "runtime/config/user_config.json"
    config.write_text(json.dumps({"assets": {"portfolio_json": "[]"}}, indent=2) + "\n", encoding="utf-8")
    return {
        "ATLAS_USER_CONFIG": str(config),
        "ATLAS_RUNTIME_DB": str(root / "runtime/state/atlas.sqlite"),
        "ATLAS_RUNTIME_LOG": str(root / "runtime/logs/atlas_runtime.log"),
        "ATLAS_LLM_TRACE_LOG": str(root / "runtime/logs/llm_traces.jsonl"),
        "ATLAS_UI_INBOX": str(root / "runtime/inbox/user_event.jsonl"),
        "ATLAS_EVENT_INBOX": str(root / "runtime/events/inbox"),
        "ATLAS_UI_PID_FILE": str(root / "runtime/state/atlas_ui_runtime.pid"),
    }


def _start_ui_server(env: dict[str, str], port: int) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-u", "-c", f"from ui.app_server import run_server; run_server(port={port})"],
        cwd=str(ROOT),
        env={**os.environ, **env},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def _wait_http(url: str) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            _get(url)
            return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"server did not become ready: {url}")


def _get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=8) as response:
        return response.read().decode("utf-8", errors="replace")


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
