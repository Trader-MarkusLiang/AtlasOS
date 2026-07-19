"""Minimal JSON observability dashboard for Atlas runtime telemetry.

DEPRECATED (Runtime v1.6, 2026-07-19): the product UI is `ui/app_server.py`.
This module remains only so historical validation scripts keep importing;
do not run it as a server.

Run with standard library only:

    python3 web/dashboard_observability.py

If FastAPI is installed, `app` exposes the same JSON endpoints.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

try:
    from runtime.telemetry.decision_trace_logger import read_decision_traces
    from runtime.telemetry.llm_trace_logger import read_llm_traces
    from runtime.telemetry.replay_engine import replay_tick_sequence
    from runtime.telemetry.state_snapshot import read_cognitive_snapshots
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.telemetry.decision_trace_logger import read_decision_traces
    from runtime.telemetry.llm_trace_logger import read_llm_traces
    from runtime.telemetry.replay_engine import replay_tick_sequence
    from runtime.telemetry.state_snapshot import read_cognitive_snapshots


def dashboard_payload(limit: int = 50) -> Dict[str, Any]:
    decisions = read_decision_traces(limit=limit)
    snapshots = read_cognitive_snapshots(limit=limit)
    llm_traces = read_llm_traces(limit=limit)
    return {
        "tick_timeline": [
            {
                "tick": item.get("tick"),
                "event": item.get("event"),
                "regime_state": item.get("regime_state"),
                "attention_state": item.get("attention_state"),
            }
            for item in decisions
        ],
        "regime_state_evolution": [
            {"tick": item.get("tick"), "regime_state": item.get("regime_state")}
            for item in decisions
        ],
        "attention_liquidity_volatility_trends": [
            {
                "tick": item.get("tick"),
                "attention": item.get("attention_state"),
                "liquidity": item.get("llm_decision_packet", {}).get("liquidity_state"),
                "volatility": item.get("snapshot", {}).get("cil_outputs", {}).get("volatility", "Data Missing"),
            }
            for item in _join_decision_snapshots(decisions, snapshots)
        ],
        "llm_call_count": len(llm_traces),
        "llm_call_count_per_tick": _llm_call_count_per_tick(decisions, llm_traces),
        "feedback_delta_heatmap": [
            {"tick": item.get("tick"), **(item.get("feedback_delta") or {})}
            for item in decisions
        ],
        "latest_snapshot": snapshots[-1] if snapshots else {},
    }


def replay_payload(start_tick: int, end_tick: int) -> Dict[str, Any]:
    return replay_tick_sequence(start_tick, end_tick)


try:  # pragma: no cover - optional dependency
    from fastapi import FastAPI

    app = FastAPI(title="Atlas Runtime Observability")

    @app.get("/")
    def root() -> Dict[str, Any]:
        return dashboard_payload()

    @app.get("/timeline")
    def timeline(limit: int = 50) -> Dict[str, Any]:
        return dashboard_payload(limit=limit)

    @app.get("/replay")
    def replay(start_tick: int = 0, end_tick: int = 10) -> Dict[str, Any]:
        return replay_payload(start_tick, end_tick)

except ModuleNotFoundError:  # pragma: no cover
    app = None


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib hook
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/replay":
            payload = replay_payload(
                int(query.get("start_tick", ["0"])[0]),
                int(query.get("end_tick", ["10"])[0]),
            )
        else:
            payload = dashboard_payload(limit=int(query.get("limit", ["50"])[0]))
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    HTTPServer((host, port), _Handler).serve_forever()


def _join_decision_snapshots(decisions: list[Dict[str, Any]], snapshots: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    snapshots_by_tick = {item.get("tick"): item for item in snapshots}
    joined = []
    for decision in decisions:
        item = dict(decision)
        item["snapshot"] = snapshots_by_tick.get(decision.get("tick"), {})
        joined.append(item)
    return joined


def _llm_call_count_per_tick(decisions: list[Dict[str, Any]], llm_traces: list[Dict[str, Any]]) -> Dict[str, int]:
    if not decisions:
        return {}
    if not llm_traces:
        return {str(item.get("tick")): 0 for item in decisions}
    # LLM traces do not carry tick directly, so expose total calls on latest tick
    # and zero on earlier ticks for a simple visualization-ready count.
    result = {str(item.get("tick")): 0 for item in decisions}
    result[str(decisions[-1].get("tick"))] = len(llm_traces)
    return result


if __name__ == "__main__":
    run_server()
