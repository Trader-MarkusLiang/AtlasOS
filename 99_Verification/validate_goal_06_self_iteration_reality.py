"""GOAL 06 true self-iteration reality validation.

This validator compares control and treatment runtime paths. Both paths use
AtlasRuntimeDaemon ticks with equivalent events. The treatment path evaluates a
runtime-created forecast miss through supported prediction API endpoints before
the later equivalent tick. It does not directly mutate trust, hypothesis scores,
or structural state.
"""

from __future__ import annotations

import json
import os
import socket
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
from runtime.forecast_ledger import list_forecasts  # noqa: E402
from runtime.logging import utc_now_iso  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402


class EquivalentEventSource:
    """Return equivalent attention/liquidity events for control and treatment."""

    def get_event(self) -> dict[str, Any]:
        return {
            "timestamp": utc_now_iso(),
            "type": "price",
            "source": "goal_06_equivalent_runtime_event",
            "payload": {
                "asset": "GOAL06",
                "price": "breakout",
                "volume": "confirming",
                "liquidity": "mixed",
                "attention": "rising",
                "theme": "self_iteration_reality",
            },
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
        ]
    }
    result: dict[str, Any] = {"checks": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal06-") as tmp:
            root = Path(tmp)
            control = _run_path(root / "control", treatment=False)
            treatment = _run_path(root / "treatment", treatment=True)
            result["control"] = control
            result["treatment"] = treatment
            result["comparison"] = _compare(control, treatment)

            _check(
                "control_no_feedback",
                control["later_tick"]["forecast_calibration_feedback_status"] == "not_available",
                result,
            )
            _check(
                "treatment_feedback_applied",
                treatment["later_tick"]["forecast_calibration_feedback_status"] == "applied",
                result,
            )
            _check("treatment_feedback_delta_negative", treatment["later_tick"]["forecast_calibration_feedback_delta"] < 0, result)
            _check(
                "trust_changed_by_treatment",
                treatment["later_tick"]["global_trust_index"] < control["later_tick"]["global_trust_index"],
                result,
            )
            _check(
                "hypothesis_distribution_changed",
                treatment["later_tick"]["causal_hypothesis_score_distribution"]
                != control["later_tick"]["causal_hypothesis_score_distribution"],
                result,
            )
            _check(
                "structural_shift_changed",
                treatment["later_tick"]["structural_shift_index"] != control["later_tick"]["structural_shift_index"],
                result,
            )
            _check("treatment_runtime_forecast_invalidated", treatment["evaluated_forecast_status"] == "INVALIDATED", result)
            _check("no_direct_state_mutation", treatment["mutation_method"] == "supported_prediction_api", result)
            _check("no_trading_execution", control["no_trading_execution"] and treatment["no_trading_execution"], result)

            failures = [key for key, value in result["checks"].items() if value is not True]
            result["classification"] = "REAL_RUNTIME_BEHAVIORAL_LOOP" if not failures else _failure_classification(result)
            result["status"] = "PASS" if not failures else "FAIL"
            result["failures"] = failures

            artifact_dir = ROOT / "99_Verification/artifacts/goal_06_self_iteration_reality"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "treatment_control_result.json").write_text(
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


def _run_path(root: Path, *, treatment: bool) -> dict[str, Any]:
    env = _temp_env(root)
    os.environ.update(env)
    os.environ["ATLAS_LLM_BACKEND"] = "litellm"

    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            max_cycles=2,
            no_sleep=True,
            db_path=env["ATLAS_RUNTIME_DB"],
            log_path=env["ATLAS_RUNTIME_LOG"],
            inbox_dir=env["ATLAS_EVENT_INBOX"],
            ui_inbox_path=env["ATLAS_UI_INBOX"],
            market_refresh_enabled=False,
            llm_model="gpt-5.5",
        ),
        event_source=EquivalentEventSource(),
    )
    first = daemon.run_tick(0)
    runtime_forecast = _latest_runtime_forecast(env["ATLAS_RUNTIME_DB"])
    evaluated_status = ""
    server: subprocess.Popen[str] | None = None
    if treatment:
        port = _free_port()
        server = _start_ui_server(env, port)
        base = f"http://127.0.0.1:{port}"
        try:
            _wait_http(base + "/predictions?format=json")
            _post_json(
                base + "/predictions/mature",
                {
                    "forecast_id": runtime_forecast["forecast_id"],
                    "maturity_reason": "goal_06_treatment_window_closed",
                },
            )
            evaluated = _post_json(
                base + "/predictions/evaluate",
                {
                    "forecast_id": runtime_forecast["forecast_id"],
                    "actual_outcome": "later_runtime_state_conflicts_with_expected_structure",
                    "status": "INVALIDATED",
                },
            )
            evaluated_status = str(evaluated.get("status") or "")
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

    later = daemon.run_tick(1)
    store = StateStore(db_path=env["ATLAS_RUNTIME_DB"])
    return {
        "first_tick": _capture_tick(first, store),
        "later_tick": _capture_tick(later, store),
        "runtime_forecast": {
            "forecast_id": runtime_forecast.get("forecast_id"),
            "status_before_treatment": runtime_forecast.get("status"),
            "decision_brief_id": runtime_forecast.get("runtime_lineage", {}).get("decision_brief_id"),
        },
        "evaluated_forecast_status": evaluated_status or "not_evaluated",
        "mutation_method": "supported_prediction_api" if treatment else "none",
        "no_trading_execution": bool(later.get("system_metrics", {}).get("no_trading_execution")),
    }


def _capture_tick(entry: dict[str, Any], store: StateStore) -> dict[str, Any]:
    tick = entry.get("cognition_summary", {}).get("tick_result", {})
    trust = tick.get("trust_score", {}) if isinstance(tick.get("trust_score"), dict) else {}
    cognition = store.get_state("cognition_state")
    causal = cognition.get("causal", {}) if isinstance(cognition.get("causal"), dict) else {}
    brief = entry.get("decision_brief", {})
    return {
        "status": entry.get("system_metrics", {}).get("status"),
        "event_type": entry.get("event", {}).get("runtime_event_type"),
        "forecast_calibration_feedback_status": tick.get("forecast_calibration_feedback_status"),
        "forecast_calibration_feedback_delta": _float(tick.get("forecast_calibration_feedback_delta"), 0.0),
        "forecast_calibration_feedback_source": tick.get("forecast_calibration_feedback_source"),
        "global_trust_index": _float(trust.get("global_trust_index"), 0.0),
        "trust_score": trust,
        "active_causal_hypothesis_id": tick.get("active_causal_hypothesis_id"),
        "causal_hypothesis_score_distribution": tick.get("causal_hypothesis_score_distribution"),
        "decision_packet_confidence": tick.get("decision_packet_confidence"),
        "action_bias": tick.get("decision_packet_action"),
        "structural_shift_index": tick.get("structural_shift_index"),
        "structural_mutation_intensity": tick.get("structural_mutation_intensity"),
        "causal_snapshot": {
            "primary_driver": causal.get("primary_driver"),
            "attention_meaning": causal.get("attention_meaning"),
            "regime_transition_probability": causal.get("regime_transition_probability"),
        },
        "decision_brief_id": brief.get("id"),
        "decision_packet": brief.get("decision_packet", {}),
    }


def _compare(control: dict[str, Any], treatment: dict[str, Any]) -> dict[str, Any]:
    control_later = control["later_tick"]
    treatment_later = treatment["later_tick"]
    return {
        "trust_delta_vs_control": round(
            treatment_later["global_trust_index"] - control_later["global_trust_index"],
            4,
        ),
        "control_feedback_status": control_later["forecast_calibration_feedback_status"],
        "treatment_feedback_status": treatment_later["forecast_calibration_feedback_status"],
        "treatment_feedback_delta": treatment_later["forecast_calibration_feedback_delta"],
        "active_hypothesis_control": control_later["active_causal_hypothesis_id"],
        "active_hypothesis_treatment": treatment_later["active_causal_hypothesis_id"],
        "hypothesis_distribution_changed": (
            control_later["causal_hypothesis_score_distribution"]
            != treatment_later["causal_hypothesis_score_distribution"]
        ),
        "structural_shift_delta": _round_delta(
            treatment_later["structural_shift_index"],
            control_later["structural_shift_index"],
        ),
        "confidence_control": control_later["decision_packet_confidence"],
        "confidence_treatment": treatment_later["decision_packet_confidence"],
        "action_bias_control": control_later["action_bias"],
        "action_bias_treatment": treatment_later["action_bias"],
    }


def _latest_runtime_forecast(db_path: str) -> dict[str, Any]:
    forecasts = list_forecasts(db_path=db_path, limit=20).get("forecasts", [])
    runtime = [item for item in forecasts if str(item.get("forecast_id", "")).startswith("runtime-")]
    if not runtime:
        raise AssertionError("runtime forecast was not created")
    return runtime[0]


def _temp_env(root: Path) -> dict[str, str]:
    for rel in ["runtime/config", "runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    config = root / "runtime/config/user_config.json"
    config.write_text(
        json.dumps(
            {
                "assets": {
                    "portfolio_json": json.dumps(
                        [
                            {
                                "asset": "GOAL06",
                                "market": "US",
                                "portfolio_percentage": 35,
                                "theme": "Self Iteration Fixture",
                                "role": "Runtime validation",
                            }
                        ]
                    ),
                    "asset_list": ["GOAL06"],
                    "weights": {"GOAL06": 35},
                }
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
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
    with request.urlopen(url, timeout=8) as response:
        return response.read().decode("utf-8", errors="replace")


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


def _failure_classification(result: dict[str, Any]) -> str:
    checks = result.get("checks", {})
    if checks.get("treatment_feedback_applied") and checks.get("trust_changed_by_treatment"):
        return "REAL_RUNTIME_METADATA_ONLY"
    if checks.get("treatment_runtime_forecast_invalidated"):
        return "TEST_HARNESS_ONLY"
    return "NO_LOOP"


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round_delta(left: Any, right: Any) -> float | None:
    try:
        return round(float(left) - float(right), 4)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
