"""Minimal Atlas Runtime dashboard.

DEPRECATED (Runtime v1.6, 2026-07-19): the product UI is `ui/app_server.py`
(port 8765). This module remains only so historical validation scripts keep
importing `dashboard_payload`; do not run it as a server.

FastAPI is optional. If it is not installed, run:

    python3 web/app.py

This starts a standard-library HTTP dashboard on http://127.0.0.1:8765.
"""

from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

try:
    from runtime.adapter.data_fetch import data_source_status
    from runtime.adapter.input_router import router_diagnostics
    from runtime.llm_router import backend_status
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.adapter.data_fetch import data_source_status
    from runtime.adapter.input_router import router_diagnostics
    from runtime.llm_router import backend_status
    from runtime.state_store import StateStore


def dashboard_payload() -> Dict[str, Any]:
    store = StateStore()
    attention_signals = store.get_attention_history(limit=10)
    return {
        "system_state": store.get_system_state(),
        "cognition_state": store.get_state("cognition_state"),
        "event_stream": store.get_event_history(limit=20),
        "portfolio": store.get_latest_portfolio_snapshot(),
        "decision_brief": store.get_latest_decision_brief(),
        "regime_status": store.get_regime_state(),
        "attention_signals": attention_signals,
        "attention_heat_index": _attention_heat_index(attention_signals),
        "infrastructure": {
            "input_router": router_diagnostics(),
            "data_source": data_source_status(),
            "llm_backend": backend_status(),
        },
        "state_transitions": store.get_state_transitions(limit=20),
        "system_logs": store.get_system_logs(limit=20),
    }


def render_dashboard() -> str:
    payload = dashboard_payload()
    brief = payload["decision_brief"].get("content", "No runtime Decision Brief yet.")
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Atlas Runtime Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; }}
    section {{ border: 1px solid #ddd; padding: 16px; margin-bottom: 16px; border-radius: 6px; }}
    pre {{ white-space: pre-wrap; background: #f7f7f7; padding: 12px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>Atlas Runtime Dashboard</h1>
  <section><h2>Current System State</h2><pre>{html.escape(json.dumps(payload["system_state"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Cognition State</h2><pre>{html.escape(json.dumps(payload["cognition_state"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Live Event Stream</h2><pre>{html.escape(json.dumps(payload["event_stream"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Current Portfolio View</h2><pre>{html.escape(json.dumps(payload["portfolio"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Latest Decision Brief</h2><pre>{html.escape(brief)}</pre></section>
  <section><h2>Regime Status</h2><pre>{html.escape(json.dumps(payload["regime_status"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Attention Heat Index</h2><pre>{html.escape(json.dumps(payload["attention_heat_index"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Infrastructure Layer</h2><pre>{html.escape(json.dumps(payload["infrastructure"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>Attention Signals</h2><pre>{html.escape(json.dumps(payload["attention_signals"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>State Transitions</h2><pre>{html.escape(json.dumps(payload["state_transitions"], ensure_ascii=False, indent=2))}</pre></section>
  <section><h2>System Logs</h2><pre>{html.escape(json.dumps(payload["system_logs"], ensure_ascii=False, indent=2))}</pre></section>
</body>
</html>"""


def _attention_heat_index(signals: list[Dict[str, Any]]) -> Dict[str, Any]:
    if not signals:
        return {"level": "Data Missing", "score": 0, "confidence": "Low"}
    high_count = sum(1 for signal in signals if "High" in str(signal.get("attention_level", "")))
    score = min(100, high_count * 20)
    if score >= 60:
        level = "High"
    elif score >= 20:
        level = "Medium"
    else:
        level = "Low"
    return {"level": level, "score": score, "confidence": "Low / Runtime Derived"}


try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse

    app = FastAPI(title="Atlas Runtime Dashboard")

    @app.get("/")
    def index() -> HTMLResponse:
        return HTMLResponse(render_dashboard())

    @app.get("/api/state")
    def api_state() -> JSONResponse:
        return JSONResponse(dashboard_payload())
except ModuleNotFoundError:
    app = None


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/state":
            body = json.dumps(dashboard_payload(), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = render_dashboard().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), DashboardHandler)
    print("Atlas Runtime dashboard: http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
