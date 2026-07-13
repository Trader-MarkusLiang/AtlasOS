"""GOAL 01 ordinary-user activation validation.

This validator uses temporary runtime state only. It proves the UI/config/runtime
path behind the browser journey without requiring real provider credentials.
"""

from __future__ import annotations

import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="atlas-goal01-"))
    env = _temp_env(temp_root)
    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, "-u", "-c", "from ui.app_server import run_server; run_server(port=%d)" % port],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    result: dict[str, Any] = {"temp_root": str(temp_root), "port": port, "checks": {}}
    try:
        _wait_http(base + "/setup")
        setup_html = _get(base + "/setup")
        _check("setup_renders", "Set up Atlas OS" in setup_html, result)
        _check("setup_has_direct_runtime_start", "Start Runtime" in setup_html, result)
        _check(
            "setup_no_portfolio_json_default",
            "Portfolio JSON" not in setup_html and 'id="portfolio-json"' not in setup_html,
            result,
        )

        payload = {
            "active_provider": "custom",
            "language": "zh",
            "model": "goal-01-validation-model",
            "base_url": "http://127.0.0.1:9/v1",
            "api_key": "goal01-validation-key",
            "market_data_mode": "configured_assets",
            "risk_preference": "balanced",
            "portfolio_json": json.dumps(
                {
                    "positions": [
                        {
                            "asset": "AAPL",
                            "market": "US",
                            "portfolio_percentage": 25,
                            "theme": "AI platform",
                            "role": "Core research exposure",
                            "thesis": "Goal 01 validation context.",
                            "risk_note": "Watch liquidity and attention shifts.",
                        }
                    ]
                }
            ),
        }
        saved = _post_json(base + "/settings", payload)
        _check("settings_saved", saved.get("status") == "saved", result)
        config_text = Path(env["ATLAS_USER_CONFIG"]).read_text(encoding="utf-8")
        _check("api_key_not_plaintext", "goal01-validation-key" not in config_text, result)
        _check("language_saved", json.loads(config_text).get("ui", {}).get("language") == "zh", result)

        provider_test = _post_json(base + "/llm/provider/test", {"provider_id": "custom"})
        _check("provider_test_returns_visible_status", provider_test.get("status") in {"error", "healthy", "reachable"}, result)
        _check("provider_test_uses_custom_provider", provider_test.get("provider") == "custom", result)

        setup_zh = _get(base + "/setup")
        _check("setup_zh_visible", "设置 Atlas OS" in setup_zh and "启动 Runtime" in setup_zh, result)

        started = _post_form(base + "/control/start", {})
        _check("runtime_start_visible", started.get("status") in {"started", "already_running"}, result)
        state = _wait_state_tick(base)
        _check("runtime_tick_produced", int(state.get("tick_counter") or 0) >= 1, result)
        _check("first_brief_visible_in_state", bool(state.get("last_decision_brief_id")), result)
        _check("portfolio_context_configured", state.get("portfolio_context", {}).get("status") == "configured", result)

        queued = _post_form(base + "/chat/send", {"message": "What changed after setup?"})
        _check("ask_atlas_queued", queued.get("status") == "queued", result)
        inbox_text = Path(env["ATLAS_UI_INBOX"]).read_text(encoding="utf-8")
        _check("chat_event_in_inbox", "What changed after setup?" in inbox_text, result)

        home = _get(base + "/")
        home_lower = home.lower()
        _check(
            "home_decision_brief_first",
            "data-home-layout=\"portfolio-first-investor-brief\"" in home_lower
            and "data-practical-section=\"action_today\"" in home_lower,
            result,
        )
        _check("home_portfolio_impact_visible", "组合影响" in home or "Portfolio Impact" in home, result)
        _check("home_no_raw_dict_default", "{&#x27;" not in home and "Exposure Map" not in home, result)

        for path in ["/portfolio", "/markets", "/predictions", "/learning"]:
            html = _get(base + path)
            _check(f"{path}_renders", "<html" in html.lower(), result)
            _check(f"{path}_no_raw_json_default", "<pre>{" not in html.replace(" ", ""), result)

        stopped = _post_form(base + "/control/stop", {})
        _check("runtime_stop_visible", stopped.get("status") in {"stopped", "stop_requested", "not_running", "stale_pid_removed"}, result)
        _wait_runtime_stopped(env)

        db_path = Path(env["ATLAS_RUNTIME_DB"])
        _check("runtime_db_exists", db_path.exists(), result)
        if db_path.exists():
            with sqlite3.connect(db_path) as con:
                _check("decision_brief_persisted", _count(con, "decision_briefs") >= 1, result)
                _check("forecast_registered", _count(con, "forecast_ledger") >= 1, result)

        failures = [key for key, value in result["checks"].items() if value is not True]
        result["status"] = "PASS" if not failures else "FAIL"
        result["failures"] = failures
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not failures else 1
    finally:
        _safe_stop_runtime(env)
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def _temp_env(temp_root: Path) -> dict[str, str]:
    config_path = temp_root / "runtime/config/user_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "llm_registry": {
                    "active_provider": "custom",
                    "fallback_chain": ["custom"],
                    "providers": [
                        {
                            "id": "custom",
                            "label": "Goal 01 Validation Provider",
                            "type": "custom",
                            "base_url": "http://127.0.0.1:9/v1",
                            "model": "goal-01-validation-model",
                            "enabled": True,
                        }
                    ],
                },
                "ui": {"language": "en"},
                "assets": {"portfolio_json": "{}", "asset_list": [], "weights": {}},
                "metadata": {"ui_only": True, "no_trading_execution": True},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for rel in ["runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (temp_root / rel).mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "ATLAS_USER_CONFIG": str(config_path),
            "ATLAS_RUNTIME_DB": str(temp_root / "runtime/state/atlas.sqlite"),
            "ATLAS_UI_INBOX": str(temp_root / "runtime/inbox/user_event.jsonl"),
            "ATLAS_EVENT_INBOX": str(temp_root / "runtime/events/inbox"),
            "ATLAS_UI_PID_FILE": str(temp_root / "runtime/state/atlas_ui_runtime.pid"),
            "ATLAS_RUNTIME_LOG": str(temp_root / "runtime/logs/atlas_runtime.log"),
            "ATLAS_UI_CONFIG": str(temp_root / "runtime/state/ui_runtime_config.json"),
            "ATLAS_DECISION_TRACE_LOG": str(temp_root / "runtime/logs/decision_traces.jsonl"),
            "ATLAS_COGNITIVE_SNAPSHOT_LOG": str(temp_root / "runtime/logs/cognitive_snapshots.jsonl"),
            "ATLAS_LLM_TRACE_LOG": str(temp_root / "runtime/logs/llm_traces.jsonl"),
        }
    )
    return env


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_http(url: str) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            _get(url)
            return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"server did not become ready: {url}")


def _wait_state_tick(base: str) -> dict[str, Any]:
    deadline = time.time() + 15
    latest: dict[str, Any] = {}
    while time.time() < deadline:
        latest = json.loads(_get(base + "/state"))
        if int(latest.get("tick_counter") or 0) >= 1 and latest.get("last_decision_brief_id"):
            return latest
        time.sleep(0.5)
    return latest


def _wait_runtime_stopped(env: dict[str, str]) -> None:
    pid_path = Path(env["ATLAS_UI_PID_FILE"])
    deadline = time.time() + 8
    while time.time() < deadline:
        if not pid_path.exists():
            return
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return
        if not _process_is_running(pid):
            return
        time.sleep(0.3)
    raise RuntimeError("runtime did not stop")


def _safe_stop_runtime(env: dict[str, str]) -> None:
    pid_path = Path(env.get("ATLAS_UI_PID_FILE", ""))
    if not pid_path.exists():
        return
    try:
        os.kill(int(pid_path.read_text(encoding="utf-8").strip()), 15)
    except (OSError, ValueError):
        return


def _process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    status = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat="],
        check=False,
        capture_output=True,
        text=True,
        timeout=1,
    ).stdout.strip()
    return bool(status) and not status.upper().startswith("Z")


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
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode("utf-8") or "{}")


def _post_form(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"content-type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def _count(con: sqlite3.Connection, table: str) -> int:
    return int(con.execute(f"select count(*) from {table}").fetchone()[0])


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
