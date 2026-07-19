"""Runtime control panel helpers for Atlas UI v0.1.

Controls are process/config oriented. They do not import cognition modules or
call mutation functions.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.state_store import StateStore


DEFAULT_PID_FILE = Path("runtime/state/atlas_ui_runtime.pid")
DEFAULT_UI_CONFIG = Path("runtime/state/ui_runtime_config.json")
ALLOWED_INTERVALS = {10, 30, 60, 300}
ALLOWED_VERBOSITY = {"minimal", "normal", "verbose"}


def start_runtime_daemon(
    *,
    interval_seconds: int = 60,
    db_path: Optional[str] = None,
    log_path: Optional[str] = None,
    inbox_dir: Optional[str] = None,
    ui_inbox_path: Optional[str] = None,
    market_config_path: Optional[str] = None,
    llm_model: str = "gpt5.5",
    proactive_update_enabled: bool = True,
    proactive_update_every_seconds: int = 7200,
    pid_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Start the runtime daemon as a background process."""

    interval = _validate_interval(interval_seconds)
    pid_path = _pid_path(pid_file)
    existing = runtime_status(pid_file=pid_file)
    if existing["running"]:
        return {"status": "already_running", **existing}

    cmd = [
        sys.executable,
        "runtime/atlas_runtime_daemon.py",
        "--interval",
        str(interval),
        "--llm-model",
        str(llm_model),
    ]
    if db_path:
        cmd.extend(["--db-path", db_path])
    if log_path:
        cmd.extend(["--log-path", log_path])
    if inbox_dir:
        cmd.extend(["--inbox-dir", inbox_dir])
    if ui_inbox_path:
        cmd.extend(["--ui-inbox-path", ui_inbox_path])
    if market_config_path:
        cmd.extend(["--market-config-path", market_config_path])
    if not proactive_update_enabled:
        cmd.append("--disable-proactive-update")
    cmd.extend(["--proactive-update-every-seconds", str(max(60, int(proactive_update_every_seconds or 7200)))])
    env = os.environ.copy()
    if market_config_path:
        env["ATLAS_USER_CONFIG"] = market_config_path
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, start_new_session=True)
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(process.pid), encoding="utf-8")
    return {"status": "started", "pid": process.pid, "command": cmd, "pid_file": str(pid_path)}


def stop_runtime_daemon(*, pid_file: Optional[str] = None) -> Dict[str, Any]:
    """Request daemon shutdown via SIGTERM."""

    pid_path = _pid_path(pid_file)
    if not pid_path.exists():
        return {"status": "not_running", "running": False}
    pid = int(pid_path.read_text(encoding="utf-8").strip())
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pid_path.unlink(missing_ok=True)
        return {"status": "stale_pid_removed", "running": False, "pid": pid}
    stopped = _wait_for_process_exit(pid)
    if stopped:
        pid_path.unlink(missing_ok=True)
        return {"status": "stopped", "running": False, "pid": pid}
    return {"status": "stop_requested", "running": _process_is_running(pid), "pid": pid}


def runtime_status(
    *,
    pid_file: Optional[str] = None,
    db_path: Optional[str] = None,
    discover: bool = True,
) -> Dict[str, Any]:
    pid_path = _pid_path(pid_file)
    running = False
    pid = None
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
            running = _process_is_running(pid)
        except (OSError, ValueError):
            running = False
        if not running:
            pid_path.unlink(missing_ok=True)
    if not running and discover:
        discovered = _discover_runtime_pid()
        if discovered is not None:
            pid = discovered
            running = True
            pid_path.parent.mkdir(parents=True, exist_ok=True)
            pid_path.write_text(str(pid), encoding="utf-8")
    trust = StateStore(db_path=db_path).get_state("system_trust_state")
    return {
        "running": running,
        "pid": pid,
        "pid_file": str(pid_path),
        "rolling_trust_index": trust.get("rolling_trust_index"),
        "feedback_stability_index": trust.get("feedback_stability_index"),
    }


def adjust_tick_interval(interval_seconds: int, *, config_path: Optional[str] = None) -> Dict[str, Any]:
    interval = _validate_interval(interval_seconds)
    config = _read_config(config_path)
    config["tick_interval_seconds"] = interval
    _write_config(config, config_path)
    return {"status": "saved_for_next_start", "tick_interval_seconds": interval}


def switch_llm_provider(provider: str, *, model: Optional[str] = None, config_path: Optional[str] = None) -> Dict[str, Any]:
    """Store a read-only provider preference for the next runtime start."""

    clean_provider = str(provider or "").strip()[:80] or "runtime"
    config = _read_config(config_path)
    config["llm_provider_preference"] = clean_provider
    if model:
        config["llm_model_preference"] = str(model).strip()[:120]
    _write_config(config, config_path)
    return {
        "status": "saved_for_next_start",
        "llm_provider_preference": clean_provider,
        "llm_model_preference": config.get("llm_model_preference"),
        "read_only_config": True,
    }


def toggle_observability_verbosity(level: str, *, config_path: Optional[str] = None) -> Dict[str, Any]:
    clean = str(level or "normal").strip().lower()
    if clean not in ALLOWED_VERBOSITY:
        raise ValueError(f"unsupported verbosity: {level}")
    config = _read_config(config_path)
    config["observability_verbosity"] = clean
    _write_config(config, config_path)
    return {"status": "saved", "observability_verbosity": clean}


def control_panel_state(*, db_path: Optional[str] = None, pid_file: Optional[str] = None) -> Dict[str, Any]:
    store = StateStore(db_path=db_path)
    return {
        "runtime": runtime_status(pid_file=pid_file, db_path=db_path),
        "system_state": store.get_system_state(),
        "system_trust_state": store.get_state("system_trust_state"),
        "self_organization_state": store.get_state("self_organization_state"),
        "ui_config": _read_config(None),
    }


def _validate_interval(value: int) -> int:
    interval = int(value)
    if interval not in ALLOWED_INTERVALS:
        raise ValueError(f"interval must be one of {sorted(ALLOWED_INTERVALS)}")
    return interval


def _pid_path(pid_file: Optional[str]) -> Path:
    return Path(pid_file) if pid_file else DEFAULT_PID_FILE


def _config_path(config_path: Optional[str]) -> Path:
    return Path(config_path) if config_path else DEFAULT_UI_CONFIG


def _read_config(config_path: Optional[str]) -> Dict[str, Any]:
    path = _config_path(config_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "invalid_config_ignored"}


def _write_config(config: Dict[str, Any], config_path: Optional[str]) -> None:
    path = _config_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        status = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat="],
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        ).stdout.strip()
    except Exception:
        return True
    if not status:
        return False
    return not status.upper().startswith("Z")


def _wait_for_process_exit(pid: int, timeout_seconds: float = 3.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not _process_is_running(pid):
            return True
        time.sleep(0.1)
    return not _process_is_running(pid)


def _discover_runtime_pid() -> Optional[int]:
    try:
        output = subprocess.run(
            ["pgrep", "-f", "runtime/atlas_runtime_daemon.py"],
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        ).stdout
    except Exception:
        return None
    pids = []
    for line in output.splitlines():
        try:
            candidate = int(line.strip())
        except ValueError:
            continue
        if _process_is_running(candidate):
            pids.append(candidate)
    return max(pids) if pids else None
