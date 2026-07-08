"""GOAL 04 portfolio cognition validation.

This validator proves the UI-configured portfolio path changes normal runtime
output without enabling trading. It uses temporary config/database/UI state and
a fixed event source so all portfolio cases see the same market event.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402


class FixedEventSource:
    def get_event(self) -> dict[str, Any]:
        return {
            "timestamp": "2026-07-08T00:00:00+00:00",
            "type": "attention",
            "payload": {
                "value": 72,
                "narrative": "same market state for portfolio differential",
                "liquidity": "mixed",
            },
            "source": "goal_04_fixed_event",
        }


CASES = {
    "portfolio_a_ai_hardware": [
        {
            "asset": "NVDA",
            "market": "US",
            "portfolio_percentage": 45,
            "theme": "AI Hardware",
            "role": "Core research exposure",
            "thesis": "AI accelerator platform exposure.",
            "risk_note": "Watch attention/liquidity divergence.",
        },
        {
            "asset": "TSM",
            "market": "US",
            "portfolio_percentage": 20,
            "theme": "AI Hardware",
            "role": "Supply chain exposure",
            "thesis": "Manufacturing bottleneck exposure.",
            "risk_note": "Watch regional liquidity.",
        },
    ],
    "portfolio_b_cash_proxy": [
        {
            "asset": "BIL",
            "market": "US",
            "portfolio_percentage": 8,
            "theme": "Cash Proxy",
            "role": "Defensive ballast",
            "thesis": "Low market beta context.",
            "risk_note": "Opportunity cost if risk appetite rises.",
        }
    ],
    "portfolio_c_single_theme": [
        {
            "asset": "AI1",
            "market": "US",
            "portfolio_percentage": 70,
            "theme": "Single Theme",
            "role": "Speculative research exposure",
            "thesis": "Concentrated single-theme validation case.",
            "risk_note": "High concentration and regime sensitivity.",
        }
    ],
    "no_portfolio": [],
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
    server: subprocess.Popen[str] | None = None
    result: dict[str, Any] = {"checks": {}, "cases": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal04-") as tmp:
            root = Path(tmp)
            env = _temp_env(root)
            os.environ.update(env)
            os.environ["ATLAS_LLM_BACKEND"] = "litellm"
            port = _free_port()
            server = _start_ui_server(env, port)
            base = f"http://127.0.0.1:{port}"
            _wait_http(base + "/state")

            for index, (case_name, positions) in enumerate(CASES.items()):
                save = _post_json(
                    base + "/settings",
                    {
                        "active_provider": "custom",
                        "language": "en",
                        "model": "goal-04-no-live-llm",
                        "base_url": "http://127.0.0.1:9/v1",
                        "api_key": "",
                        "portfolio_json": json.dumps({"positions": positions}),
                    },
                )
                _check(f"{case_name}_ui_save", save.get("status") == "saved", result)
                daemon = AtlasRuntimeDaemon(
                    AtlasRuntimeDaemonConfig(
                        max_cycles=1,
                        no_sleep=True,
                        db_path=env["ATLAS_RUNTIME_DB"],
                        log_path=env["ATLAS_RUNTIME_LOG"],
                        inbox_dir=env["ATLAS_EVENT_INBOX"],
                        market_refresh_enabled=False,
                        llm_model="gpt-5.5",
                    ),
                    event_source=FixedEventSource(),
                )
                entry = daemon.run_tick(index)
                store = StateStore(db_path=env["ATLAS_RUNTIME_DB"])
                latest = store.get_latest_decision_brief()
                state = json.loads(_get(base + "/state"))
                portfolio_page = _get(base + "/portfolio")
                context = state.get("portfolio_context", {})
                exposure = context.get("exposure_map", {}) if isinstance(context, dict) else {}
                brief = str(latest.get("content", ""))
                result["cases"][case_name] = {
                    "tick_status": entry.get("system_metrics", {}).get("status"),
                    "context_status": context.get("status"),
                    "exposure_sum_pct": context.get("exposure_sum_pct"),
                    "theme_concentration": exposure.get("theme_concentration"),
                    "market_concentration": exposure.get("market_concentration"),
                    "liquidity_sensitivity": exposure.get("liquidity_sensitivity"),
                    "regime_sensitivity": exposure.get("regime_sensitivity"),
                    "portfolio_relevance_score": exposure.get("portfolio_relevance_score"),
                    "risk_cluster_count": len(exposure.get("correlated_risk_clusters") or []),
                    "brief_id": latest.get("id"),
                    "brief_portfolio_line_present": "Portfolio State:" in brief,
                    "portfolio_page_visible": "Portfolio" in portfolio_page and str(context.get("status")) in portfolio_page,
                }
                _check(f"{case_name}_runtime_success", entry.get("system_metrics", {}).get("status") == "success", result)
                _check(f"{case_name}_brief_persisted", bool(latest.get("id")), result)
                _check(f"{case_name}_brief_mentions_portfolio", "Portfolio State:" in brief, result)
                _check(f"{case_name}_ui_portfolio_visible", result["cases"][case_name]["portfolio_page_visible"], result)
                if positions:
                    _check(f"{case_name}_required_outputs", _has_required_outputs(exposure), result)

            cases = result["cases"]
            relevance_values = [cases[name]["portfolio_relevance_score"] for name in CASES]
            regime_values = [cases[name]["regime_sensitivity"] for name in CASES]
            exposure_values = [cases[name]["exposure_sum_pct"] for name in CASES]
            _check("portfolio_outputs_differ", len({json.dumps(cases[name], sort_keys=True) for name in CASES}) == len(CASES), result)
            _check("relevance_differs", len(set(relevance_values)) >= 3, result)
            _check("regime_sensitivity_differs", len(set(regime_values)) >= 2, result)
            _check("no_portfolio_missing", cases["no_portfolio"]["context_status"] == "missing", result)
            _check("exposure_values_differ", exposure_values[:3] == [65.0, 8.0, 70.0] and exposure_values[3] == 0, result)

            config_text = Path(env["ATLAS_USER_CONFIG"]).read_text(encoding="utf-8")
            serialized = json.dumps(result, ensure_ascii=False) + config_text
            _check("no_private_amounts", not any(token in serialized.lower() for token in ["account_value", "cost_basis", "broker", "net_worth", "$"]), result)
            _check("no_buy_sell_language", "Buy" not in serialized and "Sell" not in serialized, result)

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


def _has_required_outputs(exposure: dict[str, Any]) -> bool:
    return all(
        key in exposure
        for key in [
            "asset_concentration",
            "theme_concentration",
            "market_concentration",
            "liquidity_sensitivity",
            "regime_sensitivity",
            "correlated_risk_clusters",
            "portfolio_relevance_score",
        ]
    )


def _temp_env(root: Path) -> dict[str, str]:
    for rel in ["runtime/config", "runtime/state", "runtime/logs", "runtime/inbox", "runtime/events/inbox"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    return {
        "ATLAS_USER_CONFIG": str(root / "runtime/config/user_config.json"),
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
