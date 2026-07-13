"""GOAL 03 market intelligence validation.

This validator uses live market-data providers for non-private test tickers,
then routes the observation through the normal daemon/EventStream/DecisionLoop
path and verifies UI-visible freshness. It does not execute trades, mutate
portfolio holdings, or label missing data as zero signal.
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
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402
from tools.market_data.market_data_provider import get_market_snapshot  # noqa: E402


ALLOWED_CHANNEL_STATES = {
    "LIVE",
    "DELAYED",
    "CACHED",
    "SIMULATED",
    "NOT_CONFIGURED",
    "RATE_LIMITED",
    "FAILED",
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
    server: subprocess.Popen[str] | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal03-") as tmp:
            root = Path(tmp)
            live_candidates = _discover_live_candidates()
            result["candidate_probe"] = live_candidates
            live = next((item for item in live_candidates if item.get("status") == "Available"), None)
            _check("live_candidate_available", live is not None, result)
            if not live:
                result["status"] = "FAIL"
                result["failure_reason"] = "external_market_provider_unavailable"
                print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
                return 1

            paths = _prepare_temp_paths(root)
            os.environ.update(paths["env"])
            os.environ["ATLAS_LLM_BACKEND"] = "litellm"
            config_path = Path(paths["env"]["ATLAS_USER_CONFIG"])
            _write_market_config(config_path, live)

            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    max_cycles=1,
                    no_sleep=True,
                    db_path=paths["env"]["ATLAS_RUNTIME_DB"],
                    log_path=paths["env"]["ATLAS_RUNTIME_LOG"],
                    inbox_dir=paths["env"]["ATLAS_EVENT_INBOX"],
                    market_config_path=str(config_path),
                    market_refresh_every_cycles=1,
                    market_max_assets=4,
                    llm_model="gpt-5.5",
                )
            )
            entry = daemon.run_tick(0)
            store = StateStore(db_path=paths["env"]["ATLAS_RUNTIME_DB"])
            market_state = store.get_state("market_intelligence_state")
            latest_brief = store.get_latest_decision_brief()
            events = _event_rows(paths["env"]["ATLAS_RUNTIME_DB"])

            channels = market_state.get("channels", {}) if isinstance(market_state, dict) else {}
            observations = market_state.get("observations", []) if isinstance(market_state, dict) else []
            live_observations = [
                item
                for item in observations
                if item.get("data_quality_status") == "Available"
                and item.get("source_type") == "market_data_provider"
                and item.get("latest_price_available")
                and item.get("volume") is not None
            ]
            degraded_observations = [item for item in observations if item.get("data_quality_status") != "Available"]

            _check("daemon_tick_success", entry.get("system_metrics", {}).get("status") == "success", result)
            _check("market_refresh_ok", entry.get("system_metrics", {}).get("market_refresh_status") == "ok", result)
            _check("channels_allowed", set(channels.values()).issubset(ALLOWED_CHANNEL_STATES), result)
            _check("price_volume_freshness_honest", channels.get("price_volume") in {"LIVE", "DELAYED", "CACHED"}, result)
            _check("attention_channel_attempted", channels.get("narrative_attention") in {"LIVE", "DELAYED", "CACHED", "FAILED"}, result)
            _check("live_observation_present", bool(live_observations), result)
            _check("live_event_enqueued", any(row["event_type"] == "volume_price_breakout" and row["source"] != "controlled_fixture" for row in events), result)
            _check("freshness_present", any(item.get("freshness") not in {"", None, "Unknown"} and item.get("timestamp") for item in live_observations), result)
            _check("degraded_not_zero_signal", bool(degraded_observations) and any(item.get("raw_reference", {}).get("errors") for item in degraded_observations), result)
            _check("decision_brief_persisted", bool(latest_brief.get("id")), result)

            server = _start_ui_server(paths["env"], paths["port"])
            base = f"http://127.0.0.1:{paths['port']}"
            _wait_http(base + "/state")
            state = json.loads(_get(base + "/state"))
            markets_html = _get(base + "/markets")
            state_market = state.get("market_intelligence", {})
            _check("state_api_market_observed", state_market.get("channels", {}).get("price_volume") in {"LIVE", "DELAYED", "CACHED"}, result)
            _check("state_api_freshness_visible", bool(state_market.get("timestamp")), result)
            _check("markets_page_freshness_visible", "LIVE" in markets_html and str(live.get("ticker")) in markets_html, result)

            result["runtime_summary"] = {
                "tick_status": entry.get("system_metrics", {}).get("status"),
                "market_refresh_status": entry.get("system_metrics", {}).get("market_refresh_status"),
                "market_events_enqueued": entry.get("system_metrics", {}).get("market_events_enqueued"),
                "channels": channels,
                "proof_mode": market_state.get("proof_mode"),
                "live_observations": [
                    {
                        "asset": item.get("asset"),
                        "market": item.get("market"),
                        "source": item.get("source"),
                        "timestamp": item.get("timestamp"),
                        "freshness": item.get("freshness"),
                    }
                    for item in live_observations
                ],
                "degraded_observation_count": len(degraded_observations),
                "event_rows": events[:8],
                "brief_id": latest_brief.get("id"),
            }
            failures = [key for key, value in result["checks"].items() if value is not True]
            result["status"] = "PASS" if not failures else "FAIL"
            result["failures"] = failures
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


def _discover_live_candidates() -> list[dict[str, Any]]:
    candidates = [("002409", "A-share"), ("000001", "A-share"), ("AAPL", "US"), ("SPY", "US")]
    rows: list[dict[str, Any]] = []
    for ticker, market in candidates:
        started = time.time()
        try:
            snapshot = get_market_snapshot(ticker, market)
            rows.append(
                {
                    "ticker": ticker,
                    "market": market,
                    "status": snapshot.get("data_status"),
                    "source": snapshot.get("source"),
                    "timestamp": snapshot.get("timestamp"),
                    "latest_price_available": snapshot.get("latest_price") is not None,
                    "volume_available": snapshot.get("volume") is not None,
                    "errors": list(snapshot.get("errors", []))[:2],
                    "latency_ms": int((time.time() - started) * 1000),
                }
            )
        except Exception as exc:  # provider exceptions are evidence, not crashes
            rows.append(
                {
                    "ticker": ticker,
                    "market": market,
                    "status": "Unavailable",
                    "source": None,
                    "timestamp": None,
                    "latest_price_available": False,
                    "volume_available": False,
                    "errors": [f"{type(exc).__name__}: {exc}"],
                    "latency_ms": int((time.time() - started) * 1000),
                }
            )
    return rows


def _prepare_temp_paths(root: Path) -> dict[str, Any]:
    for rel in ["runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    port = _free_port()
    env = {
        "ATLAS_USER_CONFIG": str(root / "runtime/config/user_config.json"),
        "ATLAS_RUNTIME_DB": str(root / "runtime/state/atlas.sqlite"),
        "ATLAS_RUNTIME_LOG": str(root / "runtime/logs/atlas_runtime.log"),
        "ATLAS_LLM_TRACE_LOG": str(root / "runtime/logs/llm_traces.jsonl"),
        "ATLAS_UI_INBOX": str(root / "runtime/inbox/user_event.jsonl"),
        "ATLAS_EVENT_INBOX": str(root / "runtime/events/inbox"),
        "ATLAS_UI_PID_FILE": str(root / "runtime/state/atlas_ui_runtime.pid"),
    }
    Path(env["ATLAS_USER_CONFIG"]).parent.mkdir(parents=True, exist_ok=True)
    return {"env": env, "port": port}


def _write_market_config(path: Path, live: dict[str, Any]) -> None:
    positions = [
        {
            "asset": live["ticker"],
            "market": live["market"],
            "portfolio_percentage": 10,
            "theme": "GOAL 03 live market probe",
            "role": "live observation",
            "thesis": "Non-private live provider validation asset.",
            "risk_note": "Validation only; no trading execution.",
        },
        {
            "asset": "GOAL03_BAD_SYMBOL",
            "market": "US",
            "portfolio_percentage": 3,
            "theme": "GOAL 03 degraded provider probe",
            "role": "failure visibility",
            "thesis": "Expected to degrade honestly because the symbol is invalid.",
            "risk_note": "Validation only; no trading execution.",
        },
    ]
    path.write_text(
        json.dumps(
            {
                "assets": {"portfolio_json": json.dumps(positions)},
                "metadata": {"goal": "GOAL_03_MARKET_INTELLIGENCE", "no_trading_execution": True},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _event_rows(db_path: str) -> list[dict[str, Any]]:
    with sqlite3.connect(db_path) as con:
        rows = con.execute("select event_type, source, priority from events order by id").fetchall()
    return [{"event_type": row[0], "source": row[1], "priority": row[2]} for row in rows]


def _start_ui_server(env: dict[str, str], port: int) -> subprocess.Popen[str]:
    env["ATLAS_GOAL03_UI_PORT"] = str(port)
    process = subprocess.Popen(
        [sys.executable, "-u", "-c", f"from ui.app_server import run_server; run_server(port={port})"],
        cwd=str(ROOT),
        env={**os.environ, **env},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return process


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


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
