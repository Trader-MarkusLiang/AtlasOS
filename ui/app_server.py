"""Atlas OS UI Runtime Server v0.1.

Thin FastAPI gateway over the UI modules, StateStore, and telemetry logs. This
server must not import cognitive-core modules or call mutation functions.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

if __package__ in {None, ""}:  # Support `python3 ui/app_server.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.logging import utc_now_iso
from runtime.forecast_ledger import create_forecast, evaluate_forecast, list_forecasts, mark_forecast_matured
from runtime.llm.provider_registry import health_check_provider, list_provider_models, load_provider_registry, safe_registry_view
from runtime.portfolio_context import build_portfolio_context
from runtime.state_store import StateStore
from runtime.telemetry.llm_trace_logger import read_llm_traces
from ui.components.app_shell import render_app_shell
from ui.chat_interface import render_chat_command_center
from ui.components.causal_graph_viewer import render_causal_graph_viewer
from ui.components.control_panel import render_control_panel
from ui.components.execution_timeline import render_execution_timeline
from ui.components.event_stream_panel import render_event_stream_panel
from ui.components.inspector_panel import render_inspector_panel
from ui.components.intelligence_panel import render_intelligence_panel
from ui.components.onboarding_overlay import render_onboarding_overlay
from ui.components.regime_transition_map import render_regime_transition_map
from ui.components.sidebar import render_sidebar
from ui.components.system_state_panel import render_system_state_panel
from ui.components.top_bar import render_top_bar
from ui.components.structural_drift_timeline import render_structural_drift_timeline
from ui.components.workflow_graph import infer_active_workflow_stage, render_workflow_graph
from ui.i18n.i18n import set_language, t, translation_payload
from ui.pages.dev_registry import load_roadmap, render_dev_registry_page, roadmap_api_payload
from ui.pages.getting_started import build_getting_started_status, render_getting_started_page
from ui.pages.home import render_home_page
from ui.pages.learning import render_learning_page
from ui.pages.markets import render_markets_page
from ui.pages.portfolio import render_portfolio_page
from ui.pages.predictions import render_predictions_page
from ui.pages.roadmap import render_roadmap_page
from ui.pages.settings import load_user_config, render_settings_page, save_user_config
from ui.pages.setup import render_setup_page
from ui.pages.system_guide import render_system_guide_page
from ui.pages.workflow import render_workflow_page
from ui.pages.product_views import (
    ask_content,
    control_content,
    dev_registry_content,
    home_content,
    learning_content,
    markets_content,
    portfolio_content,
    predictions_content,
    replay_content,
    roadmap_content,
    settings_content,
    setup_content,
    system_guide_content,
    workflow_content,
)
from ui.replay_console import replay_session
from ui.state_visual_dashboard import build_dashboard_state
from ui.system_control_panel import (
    adjust_tick_interval,
    control_panel_state,
    runtime_status,
    start_runtime_daemon,
    stop_runtime_daemon,
    switch_llm_provider,
)

try:  # pragma: no cover - fallback is for environments without FastAPI.
    from fastapi import FastAPI, Request
    from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
except ModuleNotFoundError:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    Request = object  # type: ignore[assignment]
    FileResponse = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]


DEFAULT_UI_INBOX = Path("runtime/inbox/user_event.jsonl")


def create_app() -> Any:
    """Create the FastAPI app."""

    if FastAPI is None:
        return _FallbackApp()

    app = FastAPI(title="Atlas OS UI Runtime Server", version="0.1")

    @app.get("/", response_class=HTMLResponse)
    async def landing() -> Any:
        state = state_api()
        return _product_shell("home", _home_content_with_setup_banner(state), state)

    @app.get("/home", response_class=HTMLResponse)
    async def home() -> Any:
        state = state_api()
        return _product_shell("home", _home_content_with_setup_banner(state), state)

    @app.get("/setup", response_class=HTMLResponse)
    async def setup() -> Any:
        state = state_api()
        content, script = setup_content(load_user_config(_user_config_path()))
        return _product_shell("setup", content, state, page_script=script)

    @app.get("/getting-started", response_class=HTMLResponse)
    async def getting_started() -> Any:
        state = state_api()
        config = load_user_config(_user_config_path())
        readiness = build_getting_started_status(config, state)
        content, script = render_getting_started_page(config, state, readiness)
        return _product_shell("getting_started", content, state, page_script=script)

    @app.get("/getting-started/status")
    async def getting_started_status() -> Any:
        return JSONResponse(getting_started_status_api())

    @app.get("/chat", response_class=HTMLResponse)
    async def chat_page() -> Any:
        state = state_api()
        content, script = ask_content(state)
        return _product_shell("ask", content, state, page_script=script)

    @app.post("/chat/send")
    async def chat_send(request: Request) -> Any:
        payload = await _request_payload(request)
        message = str(payload.get("message") or payload.get("content") or "").strip()
        if not message:
            return JSONResponse({"status": "error", "error": "message_required"}, status_code=400)
        event = append_chat_event(message, inbox_path=_ui_inbox_path())
        return JSONResponse({"status": "queued", "event": event})

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> Any:
        state = state_api()
        content, script = ask_content(state)
        return _product_shell("ask", content, state, page_script=script)

    @app.get("/portfolio", response_class=HTMLResponse)
    async def portfolio() -> Any:
        state = state_api()
        return _product_shell("portfolio", portfolio_content(state), state)

    @app.get("/markets", response_class=HTMLResponse)
    async def markets(format: str = "html") -> Any:
        data = _market_intelligence_state()
        if format.lower() == "json":
            return JSONResponse(data)
        state = state_api()
        return _product_shell("markets", markets_content(state), state)

    @app.get("/predictions", response_class=HTMLResponse)
    async def predictions(format: str = "html") -> Any:
        ledger = list_forecasts(db_path=_db_path())
        if format.lower() == "json":
            return JSONResponse(ledger)
        state = state_api()
        return _product_shell("predictions", predictions_content(ledger), state)

    @app.post("/predictions")
    async def predictions_create(request: Request) -> Any:
        payload = await _request_payload(request)
        return JSONResponse(create_forecast(payload, db_path=_db_path()))

    @app.post("/predictions/evaluate")
    async def predictions_evaluate(request: Request) -> Any:
        payload = await _request_payload(request)
        forecast_id = str(payload.get("forecast_id") or "")
        if not forecast_id:
            return JSONResponse({"status": "error", "error": "forecast_id_required"}, status_code=400)
        return JSONResponse(evaluate_forecast(forecast_id, payload, db_path=_db_path()))

    @app.post("/predictions/mature")
    async def predictions_mature(request: Request) -> Any:
        payload = await _request_payload(request)
        forecast_id = str(payload.get("forecast_id") or "")
        if not forecast_id:
            return JSONResponse({"status": "error", "error": "forecast_id_required"}, status_code=400)
        return JSONResponse(mark_forecast_matured(forecast_id, payload, db_path=_db_path()))

    @app.get("/learning", response_class=HTMLResponse)
    async def learning() -> Any:
        state = state_api()
        return _product_shell("learning", learning_content(list_forecasts(db_path=_db_path()), state), state)

    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page() -> Any:
        state = state_api()
        content, script = settings_content(load_user_config(_user_config_path()), state)
        return _product_shell("settings", content, state, page_script=script)

    @app.post("/settings")
    async def settings_save(request: Request) -> Any:
        payload = await _request_payload(request)
        result = save_user_config(payload, _user_config_path())
        return JSONResponse(result)

    @app.get("/llm/providers")
    async def llm_providers() -> Any:
        return JSONResponse(_safe_provider_registry())

    @app.post("/llm/provider/test")
    async def llm_provider_test(request: Request) -> Any:
        payload = await _request_payload(request)
        provider_id = str(payload.get("provider_id") or payload.get("provider") or "")
        if not provider_id:
            return JSONResponse({"status": "error", "error": "provider_required"}, status_code=400)
        return JSONResponse(health_check_provider(provider_id, path=_user_config_path()))

    @app.post("/llm/provider/models")
    async def llm_provider_models(request: Request) -> Any:
        payload = await _request_payload(request)
        provider_id = str(payload.get("provider_id") or payload.get("provider") or "")
        if not provider_id:
            return JSONResponse({"status": "error", "error": "provider_required"}, status_code=400)
        return JSONResponse(list_provider_models(provider_id, path=_user_config_path()))

    @app.post("/llm/providers/test_all")
    async def llm_providers_test_all() -> Any:
        registry = _safe_provider_registry()
        results = [
            health_check_provider(str(provider.get("id")), path=_user_config_path())
            for provider in registry.get("providers", [])
        ]
        refreshed = _safe_provider_registry()
        return JSONResponse(
            {
                "status": "checked",
                "results": results,
                "summary": _provider_registry_summary(refreshed),
                "registry": refreshed,
            }
        )

    @app.post("/ui/language")
    async def ui_language(request: Request) -> Any:
        payload = await _request_payload(request)
        return JSONResponse(set_language(str(payload.get("language") or "en"), _user_config_path()))

    @app.get("/ui/i18n")
    async def ui_i18n() -> Any:
        return JSONResponse(translation_payload())

    @app.get("/assets/{asset_name}")
    async def asset(asset_name: str) -> Any:
        path = _asset_file_path(asset_name)
        if path is None:
            return JSONResponse({"status": "error", "error": "asset_not_found"}, status_code=404)
        return FileResponse(path)

    @app.get("/workflow", response_class=HTMLResponse)
    async def workflow(stage: str = "event_stream") -> Any:
        state = state_api()
        content, script = workflow_content(state)
        return _product_shell("workflow", content, state, page_script=script)

    @app.get("/roadmap", response_class=HTMLResponse)
    async def roadmap(format: str = "html") -> Any:
        payload = roadmap_api_payload(_roadmap_path())
        if format.lower() == "json":
            return JSONResponse(payload)
        state = state_api()
        return _product_shell("roadmap", roadmap_content(payload), state)

    @app.get("/roadmap.json")
    async def roadmap_json() -> Any:
        return JSONResponse(roadmap_api_payload(_roadmap_path()))

    @app.get("/dev-registry", response_class=HTMLResponse)
    async def dev_registry() -> Any:
        state = state_api()
        return _product_shell("dev_registry", dev_registry_content(load_roadmap(_roadmap_path()), state), state)

    @app.get("/system-guide", response_class=HTMLResponse)
    async def system_guide() -> Any:
        state = state_api()
        return _product_shell("system_guide", system_guide_content(), state)

    @app.get("/state")
    async def state() -> Any:
        return JSONResponse(state_api())

    @app.get("/replay")
    async def replay(start_tick: int = 0, end_tick: int = 10, format: str = "html") -> Any:
        replay_data = replay_session(
            start_tick,
            end_tick,
            decision_trace_path=_decision_trace_path(),
            snapshot_path=_snapshot_path(),
            llm_trace_path=_llm_trace_path(),
        )
        if format.lower() == "json":
            return JSONResponse(replay_data)
        state = state_api()
        return _product_shell("workflow", replay_content(replay_data), state)

    @app.get("/control", response_class=HTMLResponse)
    async def control() -> Any:
        panel = control_panel_state(db_path=_db_path(), pid_file=_pid_file())
        state = state_api()
        return _product_shell("system_status", control_content(panel), state)

    @app.post("/control/start")
    async def control_start() -> Any:
        runtime_options = _configured_runtime_options()
        return JSONResponse(
            start_runtime_daemon(
                interval_seconds=runtime_options["tick_interval"],
                db_path=_db_path(),
                log_path=_runtime_log_path(),
                inbox_dir=_event_inbox_dir(),
                ui_inbox_path=_ui_inbox_path(),
                market_config_path=_user_config_path(),
                llm_model=runtime_options["llm_model"],
                proactive_update_enabled=runtime_options["proactive_update_enabled"],
                proactive_update_every_seconds=runtime_options["proactive_update_interval_seconds"],
                pid_file=_pid_file(),
            )
        )

    @app.post("/control/stop")
    async def control_stop() -> Any:
        return JSONResponse(stop_runtime_daemon(pid_file=_pid_file()))

    @app.post("/control/set_interval")
    async def control_set_interval(request: Request) -> Any:
        payload = await _request_payload(request)
        interval = int(payload.get("interval_seconds") or payload.get("interval") or 60)
        return JSONResponse(adjust_tick_interval(interval, config_path=_ui_config_path()))

    @app.post("/control/set_llm_provider")
    async def control_set_llm_provider(request: Request) -> Any:
        payload = await _request_payload(request)
        provider = str(payload.get("provider") or "runtime")
        model = payload.get("model")
        return JSONResponse(switch_llm_provider(provider, model=str(model) if model else None, config_path=_ui_config_path()))

    return app


def append_chat_event(message: str, *, inbox_path: Optional[str] = None) -> Dict[str, Any]:
    """Append one required-format chat event to runtime/inbox/user_event.jsonl."""

    clean = str(message or "").replace("\x00", " ").strip()[:2000]
    if not clean:
        raise ValueError("message_required")
    path = Path(inbox_path) if inbox_path else DEFAULT_UI_INBOX
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": utc_now_iso(),
        "type": "user_query",
        "content": clean,
        "source": "ui_chat",
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def state_api() -> Dict[str, Any]:
    """Return JSON-serializable system state for /state."""

    store = StateStore(db_path=_db_path())
    system_state = store.get_system_state()
    cognition = store.get_state("cognition_state")
    fusion = cognition.get("fusion", {}) if isinstance(cognition, dict) else {}
    latest_brief = store.get_latest_decision_brief()
    metadata = latest_brief.get("metadata", {}) if isinstance(latest_brief, dict) else {}
    event_history = store.get_event_history(limit=1)
    transitions = store.get_state_transitions(limit=1000)
    llm_summary = _llm_trace_summary(read_llm_traces(log_path=_llm_trace_path(), limit=100))
    portfolio_context = build_portfolio_context(config_path=_user_config_path())
    market_intelligence = _market_intelligence_state()
    return {
        "timestamp": utc_now_iso(),
        "regime_state": system_state.get("current_state", "Unknown"),
        "proposed_state": system_state.get("proposed_state", "Unknown"),
        "attention": fusion.get("attention_pressure"),
        "liquidity": fusion.get("liquidity_score"),
        "volatility": fusion.get("volatility_regime"),
        "trust_index": store.get_state("system_trust_state").get("rolling_trust_index"),
        "structural_coevolution_state": store.get_state("structural_coevolution_state"),
        "self_organization_state": store.get_state("self_organization_state"),
        "last_decision_packet": metadata.get("decision_packet", {}),
        "last_decision_brief_id": latest_brief.get("id"),
        "portfolio_context": portfolio_context,
        "market_intelligence": market_intelligence,
        "proactive_update_state": store.get_state("proactive_update_state"),
        "daily_cycle": store.get_state("daily_cycle_state"),
        "runtime": runtime_status(pid_file=_pid_file(), db_path=_db_path()),
        "llm_trace_summary": llm_summary,
        "llm_provider_registry": _safe_provider_registry(),
        "last_event_summary": event_history[0] if event_history else {},
        "tick_counter": len(transitions),
        "dashboard": build_dashboard_state(
            db_path=_db_path(),
            decision_trace_path=_decision_trace_path(),
            snapshot_path=_snapshot_path(),
            limit=20,
        ),
    }


def getting_started_status_api() -> Dict[str, Any]:
    """Return a no-secret readiness projection for the guided start center."""

    state = state_api()
    config = load_user_config(_user_config_path())
    return build_getting_started_status(config, state)


async def _request_payload(request: Request) -> Dict[str, Any]:
    content_type = request.headers.get("content-type", "") if hasattr(request, "headers") else ""
    raw = await request.body()
    if "application/json" in content_type:
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    parsed = parse_qs(raw.decode("utf-8"))
    return {key: values[-1] for key, values in parsed.items() if values}


def _llm_trace_summary(records: list[Dict[str, Any]]) -> Dict[str, Any]:
    providers = Counter(str(item.get("provider", "unknown")) for item in records)
    latest = records[-1] if records else {}
    return {
        "call_count": len(records),
        "providers": dict(providers),
        "latest_model": latest.get("model"),
        "latest_latency_ms": latest.get("latency_ms"),
        "latest_hallucination_risk_proxy": latest.get("hallucination_risk_proxy"),
    }


def _safe_provider_registry() -> Dict[str, Any]:
    """Return provider registry from the active UI config without exposing secrets."""

    return safe_registry_view(load_provider_registry(_user_config_path()))


def _provider_registry_summary(registry: Dict[str, Any]) -> Dict[str, Any]:
    providers = registry.get("providers", [])
    online = [item for item in providers if str(item.get("health")) in {"healthy", "reachable"}]
    fastest = sorted(
        (
            item
            for item in online
            if item.get("last_latency_ms") is not None
        ),
        key=lambda item: int(item.get("last_latency_ms") or 0),
    )
    return {
        "total_count": len(providers),
        "online_count": len(online),
        "fastest_provider": fastest[0].get("id") if fastest else None,
        "fastest_latency_ms": fastest[0].get("last_latency_ms") if fastest else None,
    }


def _market_intelligence_state() -> Dict[str, Any]:
    store = StateStore(db_path=_db_path())
    state = store.get_state("market_intelligence_state")
    if state:
        return state
    return {
        "timestamp": None,
        "status": "not_run",
        "channels": {
            "price_volume": "NOT_CONFIGURED",
            "market_breadth": "NOT_CONFIGURED",
            "volatility": "NOT_CONFIGURED",
            "liquidity_proxy": "NOT_CONFIGURED",
            "news_announcement": "NOT_CONFIGURED",
            "narrative_attention": "NOT_CONFIGURED",
            "macro_policy": "NOT_CONFIGURED",
            "portfolio_relevance": "NOT_CONFIGURED",
        },
        "observations": [],
        "events_enqueued": 0,
        "degraded": True,
        "read_only": True,
        "no_trading_execution": True,
    }


def _product_shell(
    active: str,
    content: str,
    state: Optional[Dict[str, Any]] = None,
    *,
    page_script: str = "",
    include_inspector: bool = True,
) -> str:
    display_state = state if isinstance(state, dict) else state_api()
    return render_app_shell(
        active=active,
        content=content,
        state=display_state,
        page_script=page_script,
        include_inspector=include_inspector,
    )


def _home_content_with_setup_banner(state: Dict[str, Any]) -> str:
    config = load_user_config(_user_config_path())
    readiness = build_getting_started_status(config, state)
    overall = readiness.get("overall_readiness", {}) if isinstance(readiness.get("overall_readiness"), dict) else {}
    if overall.get("can_start"):
        return home_content(state)
    lang = str(config.get("ui", {}).get("language") or "en") if isinstance(config.get("ui"), dict) else "en"
    banner = f"""
    <section class="focus-card" id="setup-incomplete-banner" data-setup-incomplete-banner>
      <span class="kicker">{_escape(t("getting.banner_kicker", lang))}</span>
      <h2>{_escape(t("getting.banner_title", lang))}</h2>
      <p>{_escape(t("getting.banner_body", lang))}</p>
      <div class="button-row">
        <a class="primary-button" href="/getting-started">{_escape(t("getting.continue_setup", lang))}</a>
        <button class="secondary-button" type="button" id="dismiss-setup-banner">{_escape(t("getting.dismiss", lang))}</button>
      </div>
    </section>
    <script>
    (function () {{
      var banner = document.getElementById("setup-incomplete-banner");
      if (!banner) return;
      if (localStorage.getItem("atlasSetupBannerDismissed") === "yes") banner.style.display = "none";
      var button = document.getElementById("dismiss-setup-banner");
      if (button) button.addEventListener("click", function () {{
        localStorage.setItem("atlasSetupBannerDismissed", "yes");
        banner.style.display = "none";
      }});
    }})();
    </script>
    """
    return banner + home_content(state)


def _system_interface_page() -> Any:
    display_state = state_api()
    shell = (
        '<div class="atlas-v2-shell">'
        + render_control_panel(display_state.get("llm_provider_registry"))
        + '<main class="atlas-v2-main">'
        + render_top_bar()
        + '<div class="atlas-v2-content">'
        + '<section class="atlas-v2-focus-zone">'
        + _render_primary_workspace(display_state)
        + "</section>"
        + render_intelligence_panel()
        + "</div>"
        + render_execution_timeline()
        + render_causal_graph_viewer()
        + render_regime_transition_map()
        + render_structural_drift_timeline()
        + render_onboarding_overlay()
        + "</main>"
        + "</div>"
    )
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas OS Control Interface</title>
<style>
:root {
  color-scheme: dark;
  --bg: #070a0f;
  --panel: rgba(15, 23, 35, 0.82);
  --panel-strong: rgba(18, 29, 45, 0.94);
  --line: rgba(148, 163, 184, 0.2);
  --line-strong: rgba(94, 234, 212, 0.38);
  --text: #e6edf3;
  --muted: #94a3b8;
  --accent: #5eead4;
  --warn: #f8d66d;
  --danger: #fb7185;
  --ok: #86efac;
}
* { box-sizing: border-box; }
html, body { min-height: 100%; }
body {
  margin: 0;
  min-width: 360px;
  background:
    radial-gradient(circle at 20% 0%, rgba(20, 184, 166, 0.16), transparent 30%),
    linear-gradient(135deg, #070a0f 0%, #101622 44%, #090d14 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: 0;
}
button, input, select, textarea { font: inherit; }
.control-plane-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 268px minmax(0, 1fr);
  background: #080b10;
}
.control-sidebar {
  min-height: 100vh;
  padding: 18px 14px;
  border-right: 1px solid var(--line);
  background: rgba(8, 13, 21, 0.96);
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 6px 18px;
}
.sidebar-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  color: var(--accent);
  font-weight: 850;
}
.sidebar-brand strong, .sidebar-brand span {
  display: block;
}
.sidebar-brand span, .sidebar-footer span {
  color: var(--muted);
  font-size: 0.78rem;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.sidebar-link {
  min-height: 38px;
  display: flex;
  align-items: center;
  padding: 9px 10px;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text);
  text-decoration: none;
}
.sidebar-link:hover {
  border-color: var(--line);
  background: rgba(148, 163, 184, 0.08);
}
.sidebar-footer {
  margin-top: 16px;
  padding: 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.52);
}
.sidebar-footer strong {
  display: block;
  margin-top: 4px;
  color: var(--accent);
}
.control-plane-main {
  min-width: 0;
  min-height: 100vh;
}
.control-plane-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(10, 16, 26, 0.72);
}
.mode-switcher {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.mode-switcher button,
.settings-link-button {
  min-height: 36px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.76);
  color: var(--text);
  text-decoration: none;
}
.mode-switcher button.active,
.settings-link-button {
  border-color: rgba(94, 234, 212, 0.48);
  background: rgba(94, 234, 212, 0.12);
}
.control-plane-workspace {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(420px, 1fr) 340px;
  gap: 12px;
  padding: 12px;
}
.workspace-primary {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.workspace-primary .center-panel {
  width: 100%;
  min-height: 520px;
}
.workspace-inspector {
  min-width: 0;
}
.workspace-inspector .right-panel {
  width: 100%;
  height: 100%;
}
.workflow-graph-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
}
.card-heading {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--line);
}
.card-heading h2 {
  margin: 2px 0 0;
  font-size: 1rem;
}
.workflow-graph {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 10px;
  padding: 14px;
}
.workflow-node {
  min-height: 64px;
  display: grid;
  place-items: center;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.48);
  color: var(--text);
  text-align: center;
  text-decoration: none;
}
.workflow-node.active {
  border-color: rgba(94, 234, 212, 0.6);
  background: rgba(94, 234, 212, 0.12);
  color: var(--accent);
}
.workflow-connectors {
  display: none;
}
.execution-timeline {
  margin: 0 12px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
}
.execution-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  padding: 0 14px 10px;
}
.execution-step {
  min-height: 58px;
  display: grid;
  place-items: center;
  padding: 8px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.45);
  color: #cbd5e1;
  text-align: center;
}
.top-bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(5, 9, 15, 0.88);
  backdrop-filter: blur(14px);
}
.brand-block, .runtime-controls, .decision-topline, .stream-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-mark {
  width: 74px;
  height: 36px;
  display: grid;
  place-items: center;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 800;
}
.brand-title { font-weight: 750; }
.brand-subtitle, .panel-kicker, .metric-label, .decision-grid span {
  color: var(--muted);
  font-size: 0.74rem;
  text-transform: uppercase;
}
.runtime-controls { flex-wrap: wrap; justify-content: flex-end; }
.language-switcher {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px 5px 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.045);
  color: #8c97a6;
  font-size: 0.78rem;
}
.global-help-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 8px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(2, 6, 12, 0.82);
  color: var(--muted);
  font-size: 0.84rem;
}
.global-help-bar a {
  color: var(--accent);
  text-decoration: none;
}
.nav-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: center;
}
.nav-tab {
  min-height: 32px;
  padding: 7px 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.72);
  color: var(--text);
  text-decoration: none;
  cursor: pointer;
}
button.nav-tab { font: inherit; }
.roadmap-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(8, 13, 21, 0.7);
}
.roadmap-strip strong {
  margin: 0 10px;
  color: var(--accent);
}
.roadmap-strip span {
  color: var(--muted);
}
.roadmap-strip-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}
.system-navigation-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 12px 12px 0;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.76);
}
.system-navigation-card h2 {
  margin: 0;
  font-size: 0.95rem;
}
.system-navigation-card p {
  margin: 4px 0 0;
  color: var(--muted);
}
.system-navigation-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
.system-navigation-links a {
  min-height: 34px;
  display: inline-flex;
  align-items: center;
  padding: 7px 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--text);
  text-decoration: none;
  background: rgba(2, 6, 12, 0.45);
}
.status-pill {
  min-width: 90px;
  padding: 7px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  text-align: center;
  font-size: 0.78rem;
  font-weight: 800;
}
.status-running { color: var(--ok); border-color: rgba(134, 239, 172, 0.42); }
.status-stopped { color: var(--danger); border-color: rgba(251, 113, 133, 0.42); }
.status-unknown { color: var(--warn); }
.control-button {
  height: 36px;
  padding: 0 14px;
  border: 1px solid rgba(94, 234, 212, 0.5);
  border-radius: 8px;
  background: rgba(20, 184, 166, 0.14);
  color: var(--text);
  cursor: pointer;
}
.control-button.secondary { border-color: var(--line); background: rgba(148, 163, 184, 0.08); }
.compact-field {
  height: 38px;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 9px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.72);
}
.compact-field span { color: var(--muted); font-size: 0.75rem; }
select, textarea {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #0b111a;
  color: var(--text);
}
select { height: 28px; padding: 0 6px; }
.workspace {
  min-height: 0;
  height: calc(100vh - 268px);
  min-height: 460px;
  display: flex;
  gap: 12px;
  padding: 12px;
}
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 18px 70px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(16px);
}
.left-panel, .right-panel {
  width: 292px;
  flex: 0 0 292px;
  overflow: auto;
}
.center-panel {
  min-width: 320px;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--line);
}
.panel-header h2, .inspector-section h3 {
  margin: 2px 0 0;
  font-size: 1rem;
}
.state-stack { padding: 14px; }
.metric, .decision-card, .inspector-section {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(8, 13, 21, 0.68);
}
.metric { padding: 12px; margin-bottom: 10px; }
.metric.primary strong { font-size: 1.28rem; color: var(--accent); }
.metric strong { display: block; margin-top: 6px; font-size: 1rem; overflow-wrap: anywhere; }
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.metric-grid .metric { margin: 0; min-height: 82px; }
.meter {
  height: 6px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
}
.meter span {
  display: block;
  width: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--danger), var(--warn), var(--accent));
  transition: width 250ms ease;
}
.decision-card { margin: 14px; padding: 14px; }
.decision-topline { justify-content: space-between; gap: 10px; }
.decision-action {
  color: var(--accent);
  font-size: 1.55rem;
  font-weight: 800;
  text-transform: uppercase;
}
.decision-confidence { color: var(--muted); }
.decision-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}
.decision-grid div {
  min-height: 58px;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.7);
}
.decision-grid strong { display: block; margin-top: 5px; overflow-wrap: anywhere; }
.decision-summary { margin: 12px 0 0; color: #cbd5e1; line-height: 1.45; }
.chat-console {
  min-height: 0;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  padding: 0 14px 14px;
}
.chat-messages {
  flex: 1 1 auto;
  min-height: 120px;
  overflow: auto;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(4, 8, 14, 0.72);
}
.chat-line {
  margin-bottom: 10px;
  padding: 9px 10px;
  border-left: 3px solid var(--line-strong);
  background: rgba(15, 23, 35, 0.65);
}
.chat-line.system { border-left-color: var(--warn); }
.chat-form {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.chat-form textarea {
  min-width: 0;
  flex: 1 1 auto;
  resize: vertical;
  padding: 10px;
}
.chat-form button { align-self: stretch; min-width: 82px; }
.inspector-section { margin: 14px; padding: 12px; }
.inline-facts {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 7px 10px;
  margin: 10px 0 0;
}
.inline-facts dt { color: var(--muted); }
.inline-facts dd { margin: 0; overflow-wrap: anywhere; }
.factor-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 10px;
}
.factor-chip {
  padding: 6px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(94, 234, 212, 0.1);
  color: #dbeafe;
  font-size: 0.78rem;
}
pre {
  max-height: 210px;
  overflow: auto;
  margin: 10px 0 0;
  padding: 10px;
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.7);
  color: #cbd5e1;
  white-space: pre-wrap;
}
.stream-panel {
  height: 190px;
  margin: 0 12px 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.stream-header { justify-content: space-between; padding: 10px 14px; }
.stream-clock { color: var(--muted); font-size: 0.78rem; }
.event-stream {
  flex: 1 1 auto;
  overflow: auto;
  padding: 10px 14px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.82rem;
}
.stream-line {
  display: flex;
  gap: 10px;
  padding: 5px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}
.stream-line time { flex: 0 0 86px; color: var(--muted); }
.stream-line span { overflow-wrap: anywhere; }
.explainability-overlay {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: rgba(3, 7, 12, 0.72);
  backdrop-filter: blur(12px);
}
.explainability-overlay.hidden { display: none; }
.overlay-panel {
  width: min(1120px, 100%);
  max-height: min(760px, calc(100vh - 36px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  background: rgba(10, 16, 26, 0.96);
  box-shadow: 0 26px 100px rgba(0, 0, 0, 0.48);
}
.overlay-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}
.overlay-header h2 { margin: 2px 0 0; font-size: 1.05rem; }
.overlay-body {
  min-height: 0;
  flex: 1 1 auto;
  padding: 14px;
  overflow: auto;
}
.graph-layout {
  display: flex;
  gap: 14px;
}
.explainability-svg {
  min-width: 0;
  flex: 1 1 auto;
  height: 430px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(3, 7, 12, 0.68);
}
.overlay-side {
  width: 270px;
  flex: 0 0 270px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.72);
}
.overlay-side h3 { margin: 0 0 10px; font-size: 0.95rem; }
.mini-list, .timeline-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mini-item, .timeline-item {
  padding: 8px 9px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.55);
  color: #cbd5e1;
  font-size: 0.82rem;
}
.mini-item.drifted { border-color: rgba(248, 214, 109, 0.58); color: #fde68a; }
.timeline-layout { display: flex; flex-direction: column; gap: 12px; }
.timeline-svg {
  width: 100%;
  height: 330px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(3, 7, 12, 0.68);
}
.onboarding-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: rgba(3, 7, 12, 0.78);
  backdrop-filter: blur(14px);
}
.onboarding-overlay.hidden { display: none; }
.onboarding-card {
  width: min(760px, 100%);
  max-height: min(820px, calc(100vh - 36px));
  overflow: auto;
  padding: 22px;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  background: rgba(10, 16, 26, 0.97);
  box-shadow: 0 26px 100px rgba(0, 0, 0, 0.48);
}
.onboarding-card h1 {
  margin: 6px 0 10px;
  font-size: 1.45rem;
}
.onboarding-card p {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.5;
}
.onboarding-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}
.onboarding-grid div, .boot-sequence {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.52);
}
.onboarding-grid div { padding: 12px; }
.onboarding-grid strong {
  display: block;
  color: var(--accent);
}
.onboarding-grid span {
  display: block;
  margin-top: 6px;
  color: #cbd5e1;
  line-height: 1.4;
}
.boot-sequence {
  margin-top: 14px;
  padding: 10px 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.boot-step {
  padding: 4px 0;
  color: var(--muted);
  opacity: 0.45;
}
.boot-step.active {
  color: var(--accent);
  opacity: 1;
}
.onboarding-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}
.onboarding-actions a {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}
.tour-highlight {
  outline: 2px solid var(--accent);
  outline-offset: 4px;
}
.atlas-v2-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), transparent 28%),
    #0b0f14;
  color: #f4f7fb;
}
.atlas-v2-main {
  min-width: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.v2-control-panel {
  min-height: 100vh;
  padding: 24px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(13, 18, 25, 0.78);
  backdrop-filter: blur(22px);
  overflow: auto;
}
.v2-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.v2-brand-mark {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
  font-weight: 760;
}
.v2-brand strong,
.v2-brand span {
  display: block;
}
.v2-brand span {
  margin-top: 2px;
  color: #8c97a6;
  font-size: 0.84rem;
}
.v2-control-section,
.v2-intelligence-card,
.v2-primary-workspace,
.v2-execution-timeline,
.v2-chat-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  background: rgba(18, 24, 32, 0.72);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(20px);
}
.v2-control-section {
  margin-bottom: 16px;
  padding: 16px;
}
.v2-provider-mini {
  display: grid;
  gap: 4px;
  margin-top: 12px;
  padding: 11px 12px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.045);
}
.v2-provider-mini span {
  color: #8c97a6;
  font-size: 0.75rem;
}
.v2-provider-mini strong {
  color: #f4f7fb;
  overflow-wrap: anywhere;
}
.v2-section-title,
.v2-kicker,
.v2-focus-kicker {
  color: #8c97a6;
  font-size: 0.74rem;
  font-weight: 680;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.v2-field {
  display: block;
  margin-top: 14px;
  color: #9aa5b3;
  font-size: 0.82rem;
}
.v2-field span {
  display: block;
  margin-bottom: 7px;
}
.v2-field input,
.v2-field select,
.v2-field textarea {
  width: 100%;
  min-height: 40px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(9, 13, 19, 0.86);
  color: #f4f7fb;
  outline: none;
}
.v2-field textarea {
  resize: vertical;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.82rem;
}
.v2-button-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}
.v2-primary-button,
.v2-secondary-button,
.v2-panel-link,
.nav-tab,
.settings-link-button {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 13px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  color: #f4f7fb;
  text-decoration: none;
  cursor: pointer;
}
.v2-primary-button {
  background: #f4f7fb;
  color: #0b0f14;
}
.v2-secondary-button,
.v2-panel-link,
.nav-tab {
  background: rgba(255, 255, 255, 0.06);
}
.v2-panel-link {
  width: 100%;
  margin-top: 12px;
}
.as-link {
  text-decoration: none;
}
.v2-toggle {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 14px;
  color: #a7b0bd;
  font-size: 0.85rem;
}
.v2-toggle input {
  width: 18px;
  height: 18px;
}
.top-bar {
  height: 72px;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(11, 15, 20, 0.7);
}
.brand-mark {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: #f4f7fb;
}
.brand-title {
  font-size: 1rem;
}
.brand-subtitle {
  color: #8c97a6;
  text-transform: none;
}
.nav-tabs {
  gap: 8px;
}
.status-pill {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.055);
}
.atlas-v2-content {
  min-height: 0;
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: minmax(520px, 1fr) 360px;
  gap: 16px;
  padding: 16px 24px 16px;
}
.atlas-v2-focus-zone {
  min-width: 0;
}
.v2-primary-workspace {
  min-height: min(620px, calc(100vh - 230px));
  padding: 22px;
  border-radius: 28px;
}
.v2-mode-switcher {
  display: inline-flex;
  gap: 6px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.045);
}
.v2-mode-switcher button {
  min-height: 34px;
  padding: 8px 14px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #9aa5b3;
  cursor: pointer;
}
.v2-mode-switcher button.active {
  background: rgba(255, 255, 255, 0.12);
  color: #f4f7fb;
}
.v2-mode-panel {
  display: none;
  padding-top: 42px;
}
.v2-mode-panel.active {
  display: block;
}
.v2-focus-kicker {
  margin-bottom: 8px;
}
.v2-regime-title {
  margin: 0;
  max-width: 920px;
  color: #f8fafc;
  font-size: clamp(3rem, 8vw, 7.5rem);
  line-height: 0.92;
  font-weight: 760;
  letter-spacing: 0;
}
.v2-trust-hero {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  margin-top: 36px;
}
.v2-trust-hero span,
.v2-system-summary span,
.v2-decision-meta span {
  color: #8c97a6;
  font-size: 0.78rem;
}
.v2-trust-hero strong {
  display: block;
  margin-top: 4px;
  color: #f4f7fb;
  font-size: 1.65rem;
}
.v2-trust-gauge {
  height: 16px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}
.v2-trust-gauge span {
  display: block;
  width: 0;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #64748b, #e2e8f0);
  transition: width 420ms ease;
}
.v2-active-decision {
  margin-top: 32px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
}
.v2-decision-line {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
}
.v2-decision-line strong {
  color: #f8fafc;
  font-size: 2rem;
  text-transform: uppercase;
}
.v2-decision-line span {
  color: #aab4c1;
}
.v2-active-decision p {
  max-width: 780px;
  margin: 12px 0 0;
  color: #cbd5e1;
  line-height: 1.55;
}
.v2-decision-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}
.v2-decision-meta span,
.v2-system-summary div {
  min-height: 54px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
}
.v2-decision-meta strong,
.v2-system-summary strong {
  display: block;
  margin-top: 4px;
  color: #f4f7fb;
  overflow-wrap: anywhere;
}
.v2-system-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.v2-chat-card {
  min-height: 470px;
  padding: 18px;
}
.chat-messages {
  min-height: 280px;
  border-color: rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}
.chat-form textarea {
  border-radius: 16px;
}
.v2-intelligence-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.v2-intelligence-card {
  padding: 16px;
}
.v2-intelligence-card.primary p {
  margin: 10px 0 0;
  color: #d7dde6;
  line-height: 1.5;
}
.v2-muted-copy {
  margin: 10px 0 0;
  color: #9aa5b3;
  line-height: 1.45;
}
.v2-causal-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.factor-chip {
  padding: 7px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.055);
  color: #dbe4ef;
}
.v2-fact-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px 12px;
  margin: 12px 0 0;
}
.v2-fact-grid dt {
  color: #8c97a6;
}
.v2-fact-grid dd {
  margin: 0;
  color: #f4f7fb;
  overflow-wrap: anywhere;
}
.v2-intelligence-card pre {
  max-height: 120px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.2);
}
.v2-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
.v2-execution-timeline {
  margin: 0 24px 24px;
  padding: 14px;
}
.v2-timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.v2-timeline-header h2 {
  margin: 2px 0 0;
  font-size: 0.96rem;
  font-weight: 650;
}
.v2-stream-clock {
  color: #8c97a6;
  font-size: 0.82rem;
}
.v2-timeline-chain {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}
.v2-timeline-node {
  min-height: 58px;
  padding: 10px 12px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.045);
}
.v2-timeline-node strong,
.v2-timeline-node span {
  display: block;
}
.v2-timeline-node span {
  margin-top: 3px;
  color: #8c97a6;
  font-size: 0.76rem;
}
.v2-compressed-stream {
  max-height: 76px;
  overflow: auto;
  margin-top: 10px;
  color: #9aa5b3;
  font-size: 0.8rem;
}
.stream-line {
  border-bottom: 0;
  padding: 3px 0;
}
.workflow-graph-card {
  border-color: rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  background: rgba(18, 24, 32, 0.72);
}
.workflow-graph {
  display: flex;
  align-items: stretch;
  gap: 8px;
  padding: 16px;
}
.workflow-node {
  min-height: 72px;
  flex: 1 1 0;
  border-color: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
  color: #f4f7fb;
}
.workflow-node.active-path {
  background: rgba(255, 255, 255, 0.075);
}
.workflow-node.active {
  border-color: rgba(255, 255, 255, 0.26);
  background: #f4f7fb;
  color: #0b0f14;
}
.workflow-node.inactive {
  opacity: 0.42;
}
.workflow-explanation {
  display: flex;
  gap: 10px;
  padding: 0 16px 16px;
  color: #9aa5b3;
}
.workflow-explanation strong {
  color: #f4f7fb;
}
.empty-pulse {
  animation: v2Pulse 2.8s ease-in-out infinite;
}
@keyframes v2Pulse {
  0%, 100% { opacity: 0.62; }
  50% { opacity: 1; }
}
@media (max-width: 1080px) {
  .control-plane-shell { grid-template-columns: 1fr; }
  .control-sidebar { min-height: 0; border-right: 0; border-bottom: 1px solid var(--line); }
  .sidebar-nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .control-plane-workspace { grid-template-columns: 1fr; }
  .workspace-inspector .right-panel { height: auto; }
  .workflow-graph { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .execution-steps { grid-template-columns: 1fr; }
  .workspace { height: auto; min-height: 0; flex-wrap: wrap; }
  .left-panel, .right-panel { flex: 1 1 280px; width: auto; }
  .center-panel { flex: 1 1 100%; order: 2; min-height: 520px; }
  .right-panel { order: 3; }
  .stream-panel { height: 220px; }
  .graph-layout { flex-direction: column; }
  .overlay-side { width: auto; flex-basis: auto; }
  .atlas-v2-shell { grid-template-columns: 1fr; }
  .v2-control-panel { min-height: 0; border-right: 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
  .atlas-v2-content { grid-template-columns: 1fr; }
  .v2-system-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .workflow-graph { flex-direction: column; }
}
@media (max-width: 680px) {
  .top-bar { height: auto; align-items: flex-start; flex-direction: column; }
  .runtime-controls { justify-content: flex-start; }
  .sidebar-nav { grid-template-columns: 1fr; }
  .control-plane-toolbar { align-items: flex-start; flex-direction: column; }
  .workflow-graph { grid-template-columns: 1fr; }
  .global-help-bar { align-items: flex-start; flex-direction: column; }
  .system-navigation-card { align-items: flex-start; flex-direction: column; }
  .system-navigation-links { justify-content: flex-start; }
  .onboarding-grid { grid-template-columns: 1fr; }
  .roadmap-strip { align-items: flex-start; flex-direction: column; }
  .roadmap-strip-actions { flex-wrap: wrap; white-space: normal; }
  .workspace { padding: 10px; }
  .metric-grid, .decision-grid { grid-template-columns: 1fr; }
  .chat-form { flex-direction: column; }
  .atlas-v2-content { padding: 12px; }
  .v2-regime-title { font-size: 3rem; }
  .v2-trust-hero,
  .v2-decision-meta,
  .v2-system-summary,
  .v2-timeline-chain { grid-template-columns: 1fr; }
  .v2-decision-line { align-items: flex-start; flex-direction: column; }
  .v2-execution-timeline { margin: 0 12px 12px; }
}
</style>
</head>
<body>
<div class="shell">
""" + shell + """
</div>
<script>
(function () {
  const pollMs = 1500;
  let lastTick = null;
  let stillPolls = 0;
  let lastStreamSignature = "";
  let latestReplay = null;

  function byId(id) { return document.getElementById(id); }
  function setText(id, value) {
    const node = byId(id);
    if (!node) return;
    const text = clean(value);
    node.textContent = text;
    if (text === "Waiting for cognitive signal") {
      node.title = "System has not yet converged on this metric.";
      node.classList.add("empty-pulse");
    } else if (text === "Insufficient system context" || text === "System initializing reasoning layer") {
      node.title = "Atlas needs more runtime context before this field becomes meaningful.";
      node.classList.add("empty-pulse");
    } else if (String(value || "").toLowerCase() === "neutral") {
      node.title = "No strong regime signal is active.";
      node.classList.remove("empty-pulse");
    } else {
      node.removeAttribute("title");
      node.classList.remove("empty-pulse");
    }
  }
  function clean(value) {
    if (value === null || value === undefined || value === "") return "System initializing reasoning layer";
    const textValue = String(value).trim();
    if (textValue.toUpperCase() === "UNKNOWN") return "Waiting for cognitive signal";
    if (textValue.toLowerCase() === "unknown") return "Insufficient system context";
    if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
    return String(value);
  }
  function packetFrom(state) {
    return state.last_decision_packet && typeof state.last_decision_packet === "object" ? state.last_decision_packet : {};
  }
  function dashboardFrom(state) {
    return state.dashboard && typeof state.dashboard === "object" ? state.dashboard : {};
  }
  function asObject(value) {
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  }
  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }
  function updateRuntimeStatus(tick) {
    const pill = byId("runtime-status-pill");
    if (!pill) return;
    if (lastTick === null) {
      pill.textContent = "RUNNING";
      pill.className = "status-pill status-running";
    } else if (tick === lastTick) {
      stillPolls += 1;
      if (stillPolls >= 3) {
        pill.textContent = "STOPPED";
        pill.className = "status-pill status-stopped";
      }
    } else {
      stillPolls = 0;
      pill.textContent = "RUNNING";
      pill.className = "status-pill status-running";
    }
    lastTick = tick;
  }
  function updateState(state) {
    const packet = packetFrom(state);
    setText("state-regime", state.regime_state);
    setText("state-trust", state.trust_index);
    setText("state-liquidity", state.liquidity);
    setText("state-attention", state.attention);
    setText("state-volatility", state.volatility);
    setText("state-tick", state.tick_counter || 0);
    setText("decision-action", packet.recommended_action || "neutral");
    setText("decision-confidence", "Confidence " + clean(packet.confidence || 0));
    setText("decision-risk", packet.risk_level || "unknown");
    setText("decision-attention", packet.attention_state || state.attention);
    setText("decision-liquidity", packet.liquidity_state || state.liquidity);
    setText("decision-summary", packet.causal_summary || "Waiting for DecisionPacket.");
    setText("causal-summary", packet.causal_summary || "Unknown");
    setText("llm-call-count", (state.llm_trace_summary || {}).call_count || 0);
    setText("llm-model", (state.llm_trace_summary || {}).latest_model);
    setText("llm-latency", clean((state.llm_trace_summary || {}).latest_latency_ms) + " ms");
    setText("focus-runtime-status", state.tick_counter ? "Runtime loop active" : "Initializing cognition layer");
    updateProviderMini(state.llm_provider_registry || {});

    const trust = typeof state.trust_index === "number" ? Math.max(0, Math.min(1, state.trust_index)) : 0;
    const meter = byId("trust-meter");
    if (meter) meter.style.width = (trust * 100).toFixed(1) + "%";
    setText("trust-trend", trust >= 0.7 ? "Stable trust field" : trust >= 0.4 ? "Moderate trust field" : "Low trust field");
    setText("stability-index", trust >= 0.7 ? "Stable" : trust >= 0.4 ? "Watchful" : "Insufficient system context");

    const decisionTrace = {
      tick: state.tick_counter || 0,
      brief_id: state.last_decision_brief_id || null,
      regime: state.regime_state || "Unknown",
      action: packet.recommended_action || "neutral",
      risk: packet.risk_level || "unknown"
    };
    const decisionNode = byId("decision-trace");
    if (decisionNode) {
      decisionNode.textContent = "tick " + decisionTrace.tick + ", regime " + clean(decisionTrace.regime) + ", decision " + clean(decisionTrace.action);
    }

    const structuralNode = byId("structural-state");
    if (structuralNode) {
      const structuralSummary = summarizeStructure(state.structural_coevolution_state || state.self_organization_state || {});
      structuralNode.textContent = structuralSummary;
    }
    updateHypothesisState(state);
    updateDecisionExplanation(state, packet);
    updateCausalGraph(state);
    updateRegimeMap(state);
    updateDriftTimeline(state);
    updateRuntimeStatus(state.tick_counter || 0);
    pushStream(state, packet);
  }
  function updateHypothesisState(state) {
    const structural = asObject(state.structural_coevolution_state || state.self_organization_state);
    const hypothesis = asObject(structural.hypothesis_state || structural.active_hypothesis || structural.causal_hypothesis);
    setText("active-hypothesis", hypothesis.id || hypothesis.name || structural.active_hypothesis_id || "Insufficient system context");
    const shadow = structural.shadow_hypothesis_count || structural.shadow_count || asArray(structural.shadow_hypotheses).length || 0;
    setText("shadow-hypothesis-count", shadow);
  }
  function summarizeStructure(value) {
    const structural = asObject(value);
    if (!Object.keys(structural).length) return "No structural drift summary yet";
    const mutation = asObject(structural.mutated_graph || structural.causal_graph_mutation || structural);
    const drift = asObject(structural.applied_drift || structural.drift_summary || structural);
    const pieces = [];
    if (mutation.structural_shift_index !== undefined) pieces.push("shift " + clean(mutation.structural_shift_index));
    if (mutation.mutation_intensity !== undefined) pieces.push("mutation " + clean(mutation.mutation_intensity));
    if (drift.bounded !== undefined) pieces.push(drift.bounded ? "bounded" : "needs review");
    return pieces.join(" · ") || "Structural state summarized";
  }
  function updateProviderMini(registry) {
    const providers = Array.isArray(registry.providers) ? registry.providers : [];
    const active = registry.active_provider || "openai";
    const provider = providers.find(function (item) { return item.id === active; }) || {};
    setText("active-provider-label", provider.label || active);
    setText("active-provider-model", provider.model || "System initializing reasoning layer");
    setText("active-provider-health", provider.health || "unknown");
  }
  function updateDecisionExplanation(state, packet) {
    const factors = dominantFactors(state, packet);
    const action = packet.recommended_action || "neutral";
    const regime = state.regime_state || "Unknown";
    const trust = typeof state.trust_index === "number" ? state.trust_index : null;
    const reason = packet.reasoning_trace || packet.causal_summary || "System initializing reasoning layer";
    setText("decision-why", action + " because " + reason);
    setText("regime-influence", regime + " -> " + action);
    setText("trust-impact", trust === null ? "Unknown" : (trust >= 0.7 ? "High trust supports explanation weight" : trust >= 0.4 ? "Medium trust tempers explanation weight" : "Low trust limits explanation weight"));
    const list = byId("dominant-causal-factors");
    if (list) {
      list.textContent = "";
      factors.forEach(function (factor) {
        const chip = document.createElement("span");
        chip.className = "factor-chip";
        chip.textContent = factor;
        list.appendChild(chip);
      });
    }
  }
  function dominantFactors(state, packet) {
    const factors = [];
    if (packet.risk_level) factors.push("risk:" + packet.risk_level);
    if (packet.attention_state || state.attention !== undefined) factors.push("attention:" + clean(packet.attention_state || state.attention));
    if (packet.liquidity_state || state.liquidity !== undefined) factors.push("liquidity:" + clean(packet.liquidity_state || state.liquidity));
    if (state.volatility !== undefined) factors.push("volatility:" + clean(state.volatility));
    if (state.trust_index !== undefined && state.trust_index !== null) factors.push("trust:" + clean(state.trust_index));
    return factors.slice(0, 3);
  }
  function extractCausalEdges(state) {
    const dashboard = dashboardFrom(state);
    const graph = asObject(dashboard.causal_graph_snapshot);
    const structural = asObject(state.structural_coevolution_state);
    const mutated = asObject(structural.mutated_graph || structural.causal_graph_mutation || structural);
    const edgeUpdates = asObject(mutated.edge_weight_updates);
    const edges = [];
    if (Array.isArray(graph.edges)) {
      graph.edges.forEach(function (edge) {
        if (!edge) return;
        edges.push({
          from: edge.from || edge.source || edge[0] || "Source",
          to: edge.to || edge.target || edge[1] || "Target",
          weight: Number(edge.weight || edge.value || 0.5),
          drift: Number(edge.drift || edge.delta || 0)
        });
      });
    }
    Object.keys(graph).forEach(function (key) {
      const value = graph[key];
      if (key.indexOf("->") > -1) {
        const parts = key.split("->");
        edges.push({ from: parts[0].trim(), to: parts[1].trim(), weight: Number(value || 0.5), drift: 0 });
      } else if (value && typeof value === "object" && !Array.isArray(value)) {
        Object.keys(value).forEach(function (target) {
          if (typeof value[target] === "number") edges.push({ from: key, to: target, weight: value[target], drift: 0 });
        });
      }
    });
    Object.keys(edgeUpdates).forEach(function (key) {
      const parts = key.indexOf("->") > -1 ? key.split("->") : key.split(":");
      edges.push({
        from: (parts[0] || "Source").trim(),
        to: (parts[1] || "Target").trim(),
        weight: Math.abs(Number(edgeUpdates[key] || 0)),
        drift: Number(edgeUpdates[key] || 0)
      });
    });
    if (!edges.length) {
      return [
        { from: "Narrative", to: "Attention", weight: 0.6, drift: 0.0 },
        { from: "Attention", to: "Retail Flow", weight: 0.55, drift: 0.0 },
        { from: "Liquidity", to: "Volatility", weight: 0.7, drift: 0.0 },
        { from: "Institutional Flow", to: "Liquidity", weight: 0.5, drift: 0.0 },
        { from: "Price Momentum", to: "Attention", weight: 0.45, drift: 0.0 }
      ];
    }
    return edges.slice(0, 14);
  }
  function updateCausalGraph(state) {
    const svg = byId("causal-graph-svg");
    const list = byId("causal-edge-list");
    if (!svg) return;
    const edges = extractCausalEdges(state);
    const nodes = Array.from(new Set(edges.flatMap(function (edge) { return [edge.from, edge.to]; }))).slice(0, 10);
    const centerX = 360, centerY = 210, radius = 145;
    const points = {};
    nodes.forEach(function (node, index) {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index / Math.max(nodes.length, 1));
      points[node] = { x: centerX + Math.cos(angle) * radius, y: centerY + Math.sin(angle) * radius };
    });
    svg.textContent = "";
    edges.forEach(function (edge) {
      const a = points[edge.from], b = points[edge.to];
      if (!a || !b) return;
      const line = svgEl("line", {
        x1: a.x, y1: a.y, x2: b.x, y2: b.y,
        stroke: Math.abs(edge.drift) > 0.08 ? "#f8d66d" : "#5eead4",
        "stroke-width": 1.2 + Math.min(4, Math.abs(edge.weight || 0.2) * 4),
        opacity: 0.72
      });
      svg.appendChild(line);
      const label = svgEl("text", { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 4, fill: "#cbd5e1", "font-size": "11", "text-anchor": "middle" });
      label.textContent = clean(edge.weight);
      svg.appendChild(label);
    });
    nodes.forEach(function (node) {
      const point = points[node];
      svg.appendChild(svgEl("circle", { cx: point.x, cy: point.y, r: 29, fill: "rgba(15, 23, 35, 0.95)", stroke: "#5eead4", "stroke-width": 1.4 }));
      const label = svgEl("text", { x: point.x, y: point.y + 4, fill: "#e6edf3", "font-size": "11", "text-anchor": "middle" });
      label.textContent = shortLabel(node);
      svg.appendChild(label);
    });
    if (list) {
      list.textContent = "";
      edges.forEach(function (edge) {
        const item = document.createElement("div");
        item.className = "mini-item" + (Math.abs(edge.drift) > 0.08 ? " drifted" : "");
        item.textContent = edge.from + " -> " + edge.to + " | weight " + clean(edge.weight) + " | drift " + clean(edge.drift);
        list.appendChild(item);
      });
    }
  }
  function updateRegimeMap(state) {
    const svg = byId("regime-map-svg");
    const list = byId("regime-transition-list");
    if (!svg) return;
    const replayTimeline = asArray(asObject(latestReplay).decision_timeline).map(function (item) {
      return { tick: item.tick, regime_state: item.regime_state };
    });
    const timeline = asArray(dashboardFrom(state).regime_state_timeline).concat(replayTimeline);
    const names = Array.from(new Set(timeline.map(function (item) { return item.regime_state || item.state; }).filter(Boolean)));
    if (!names.includes(state.regime_state || "Unknown")) names.push(state.regime_state || "Unknown");
    const regimes = (names.length ? names : ["NORMAL", "HIGH_VOLATILITY", "RISK_OFF", "ATTENTION_EXPANSION"]).slice(0, 7);
    const current = state.regime_state || regimes[0] || "Unknown";
    const transitions = {};
    for (let i = 1; i < timeline.length; i += 1) {
      const from = timeline[i - 1].regime_state || timeline[i - 1].state || "Unknown";
      const to = timeline[i].regime_state || timeline[i].state || "Unknown";
      transitions[from + "->" + to] = (transitions[from + "->" + to] || 0) + 1;
    }
    svg.textContent = "";
    const width = 720, baseY = 210, gap = width / Math.max(regimes.length + 1, 2);
    const points = {};
    regimes.forEach(function (name, index) {
      points[name] = { x: gap * (index + 1), y: baseY + (index % 2 === 0 ? -62 : 62) };
    });
    Object.keys(transitions).forEach(function (key) {
      const parts = key.split("->"), a = points[parts[0]], b = points[parts[1]];
      if (!a || !b) return;
      svg.appendChild(svgEl("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: "#f8d66d", "stroke-width": 1 + transitions[key], opacity: 0.6 }));
    });
    regimes.forEach(function (name) {
      const point = points[name];
      const active = name === current;
      svg.appendChild(svgEl("circle", { cx: point.x, cy: point.y, r: active ? 45 : 34, fill: active ? "rgba(94, 234, 212, 0.2)" : "rgba(15, 23, 35, 0.95)", stroke: active ? "#5eead4" : "#94a3b8", "stroke-width": active ? 2 : 1 }));
      const label = svgEl("text", { x: point.x, y: point.y + 4, fill: "#e6edf3", "font-size": "11", "text-anchor": "middle" });
      label.textContent = shortLabel(name);
      svg.appendChild(label);
      const basin = svgEl("text", { x: point.x, y: point.y + 61, fill: "#94a3b8", "font-size": "10", "text-anchor": "middle" });
      basin.textContent = active ? "active basin" : "stability basin";
      svg.appendChild(basin);
    });
    if (list) {
      list.textContent = "";
      const keys = Object.keys(transitions);
      (keys.length ? keys : [current + "->" + current]).forEach(function (key) {
        const item = document.createElement("div");
        item.className = "mini-item";
        item.textContent = key + " | weight " + clean(transitions[key] || 1);
        list.appendChild(item);
      });
    }
  }
  function updateDriftTimeline(state) {
    const svg = byId("drift-timeline-svg");
    const list = byId("drift-timeline-list");
    if (!svg) return;
    const trustCurve = asArray(dashboardFrom(state).trust_field_evolution_curve);
    const replayTimeline = asArray(asObject(latestReplay).cognitive_state_evolution).map(function (item) {
      return { tick: item.tick, trust_field_evolution: asObject(item.trust_state).feedback_stability_index, regime_state: asObject(item.system_state).current_state };
    });
    const timeline = asArray(dashboardFrom(state).regime_state_timeline).concat(replayTimeline);
    const points = trustCurve.length ? trustCurve : timeline.map(function (item, index) {
      return { tick: item.tick || index, trust_field_evolution: 0.5, regime_state: item.regime_state };
    });
    svg.textContent = "";
    const usable = points.slice(-18);
    const maxTick = Math.max(1, usable.length - 1);
    const values = usable.map(function (item) {
      const raw = item.trust_field_evolution;
      return typeof raw === "number" ? raw : (typeof state.trust_index === "number" ? state.trust_index : 0.5);
    });
    let path = "";
    values.forEach(function (value, index) {
      const x = 40 + index * (840 / Math.max(maxTick, 1));
      const y = 270 - Math.max(0, Math.min(1, value)) * 220;
      path += (index === 0 ? "M " : " L ") + x + " " + y;
      svg.appendChild(svgEl("circle", { cx: x, cy: y, r: 4, fill: "#5eead4" }));
    });
    svg.appendChild(svgEl("path", { d: path || "M 40 160 L 880 160", fill: "none", stroke: "#5eead4", "stroke-width": 2.4 }));
    svg.appendChild(svgEl("text", { x: 40, y: 28, fill: "#cbd5e1", "font-size": "12" })).textContent = "trust field evolution";
    svg.appendChild(svgEl("line", { x1: 40, y1: 270, x2: 880, y2: 270, stroke: "#334155", "stroke-width": 1 }));
    svg.appendChild(svgEl("line", { x1: 40, y1: 50, x2: 40, y2: 270, stroke: "#334155", "stroke-width": 1 }));
    if (list) {
      list.textContent = "";
      usable.slice(-8).forEach(function (item, index) {
        const row = document.createElement("div");
        row.className = "timeline-item";
        row.textContent = "tick " + clean(item.tick || index) + " | trust=" + clean(values[Math.max(0, values.length - usable.slice(-8).length + index)]) + " | regime=" + clean(item.regime_state || state.regime_state);
        list.appendChild(row);
      });
    }
  }
  function shortLabel(value) {
    const text = String(value || "Unknown").replace(/_/g, " ");
    return text.length > 18 ? text.slice(0, 16) + ".." : text;
  }
  function svgEl(name, attrs) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.keys(attrs || {}).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    return node;
  }
  function pushStream(state, packet) {
    const stream = byId("event-stream");
    if (!stream) return;
    const tick = state.tick_counter || 0;
    const action = packet.recommended_action || "neutral";
    const signature = [tick, state.regime_state, state.trust_index, action].join("|");
    if (signature === lastStreamSignature) return;
    lastStreamSignature = signature;
    const line = document.createElement("div");
    line.className = "stream-line";
    const now = new Date();
    const time = document.createElement("time");
    time.textContent = now.toLocaleTimeString();
    const msg = document.createElement("span");
    msg.textContent = "tick=" + tick + " regime=" + clean(state.regime_state) + " trust=" + clean(state.trust_index) + " decision=" + action;
    line.appendChild(time);
    line.appendChild(msg);
    stream.prepend(line);
    while (stream.children.length > 80) stream.removeChild(stream.lastChild);
    setText("stream-clock", now.toLocaleTimeString());
  }
  async function refreshState() {
    try {
      const response = await fetch("/state", { cache: "no-store" });
      if (!response.ok) throw new Error("state request failed");
      const state = await response.json();
      updateState(state);
      refreshReplay(state.tick_counter || 0);
    } catch (error) {
      const pill = byId("runtime-status-pill");
      if (pill) {
        pill.textContent = "STOPPED";
        pill.className = "status-pill status-stopped";
      }
      addChatLine("system", "State refresh failed: " + error.message);
    }
  }
  async function refreshReplay(tick) {
    const endTick = Math.max(1, Number(tick || 1));
    const startTick = Math.max(0, endTick - 20);
    try {
      const response = await fetch("/replay?start_tick=" + startTick + "&end_tick=" + endTick + "&format=json", { cache: "no-store" });
      if (response.ok) latestReplay = await response.json();
    } catch (error) {
      latestReplay = latestReplay || null;
    }
  }
  function addChatLine(kind, text) {
    const box = byId("chat-messages");
    if (!box) return;
    const line = document.createElement("div");
    line.className = "chat-line " + (kind || "system");
    line.textContent = text;
    box.prepend(line);
    while (box.children.length > 40) box.removeChild(box.lastChild);
  }
  async function postForm(url, values) {
    const body = new URLSearchParams(values || {});
    const response = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body
    });
    return response.json();
  }
  function bindControls() {
    bindOnboarding();
    bindModeSwitcher();
    bindWorkflowExplanation();
    document.querySelectorAll("[data-open-overlay]").forEach(function (button) {
      button.addEventListener("click", function () {
        const target = byId(button.getAttribute("data-open-overlay"));
        if (target) target.classList.remove("hidden");
      });
    });
    document.querySelectorAll("[data-close-overlay]").forEach(function (button) {
      button.addEventListener("click", function () {
        const overlay = button.closest(".explainability-overlay");
        if (overlay) overlay.classList.add("hidden");
      });
    });
    document.querySelectorAll(".explainability-overlay").forEach(function (overlay) {
      overlay.addEventListener("click", function (event) {
        if (event.target === overlay) overlay.classList.add("hidden");
      });
    });
    const form = byId("chat-form");
    if (form) {
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const input = byId("chat-input");
        const message = input ? input.value.trim() : "";
        if (!message) return;
        addChatLine("user", "You: " + message);
        if (input) input.value = "";
        try {
          const result = await postForm("/chat/send", { message });
          addChatLine("system", "Queued: " + clean(result.status));
          refreshState();
        } catch (error) {
          addChatLine("system", "Queue failed: " + error.message);
        }
      });
    }
    const start = byId("runtime-start");
    if (start) start.addEventListener("click", async function () {
      try {
        const result = await postForm("/control/start", {});
        addChatLine("system", "Start: " + clean(result.status));
        await refreshState();
      }
      catch (error) { addChatLine("system", "Start failed: " + error.message); }
    });
    const stop = byId("runtime-stop");
    if (stop) stop.addEventListener("click", async function () {
      try {
        const result = await postForm("/control/stop", {});
        addChatLine("system", "Stop: " + clean(result.status));
        const pill = byId("runtime-status-pill");
        if (pill) {
          pill.textContent = "STOPPED";
          pill.className = "status-pill status-stopped";
        }
        await refreshState();
      }
      catch (error) { addChatLine("system", "Stop failed: " + error.message); }
    });
    const interval = byId("tick-interval");
    if (interval) interval.addEventListener("change", async function () {
      try { addChatLine("system", "Tick interval saved: " + clean((await postForm("/control/set_interval", { interval_seconds: interval.value })).tick_interval_seconds) + "s"); }
      catch (error) { addChatLine("system", "Interval update failed: " + error.message); }
    });
    const language = byId("language-select");
    if (language) language.addEventListener("change", async function () {
      try {
        await postForm("/ui/language", { language: language.value });
        window.location.reload();
      } catch (error) {
        addChatLine("system", "Language update failed: " + error.message);
      }
    });
  }
  function bindModeSwitcher() {
    document.querySelectorAll("[data-v2-mode]").forEach(function (button) {
      button.addEventListener("click", function () {
        const mode = button.getAttribute("data-v2-mode");
        document.querySelectorAll("[data-v2-mode]").forEach(function (item) { item.classList.toggle("active", item === button); });
        document.querySelectorAll("[data-mode-panel]").forEach(function (panel) {
          panel.classList.toggle("active", panel.getAttribute("data-mode-panel") === mode);
        });
      });
    });
  }
  function bindWorkflowExplanation() {
    document.querySelectorAll("[data-workflow-node]").forEach(function (node) {
      node.addEventListener("click", function (event) {
        event.preventDefault();
        const panel = byId("workflow-node-explanation");
        if (!panel) return;
        document.querySelectorAll("[data-workflow-node]").forEach(function (item) { item.classList.remove("active"); });
        node.classList.add("active");
        panel.innerHTML = "<strong>" + node.textContent.trim() + "</strong><span>" + (node.getAttribute("data-explanation") || "") + "</span>";
      });
    });
  }
  function bindOnboarding() {
    const overlay = byId("onboarding-overlay");
    if (!overlay) return;
    overlay.classList.remove("hidden");
    runBootSequence();
    const enter = byId("enter-dashboard");
    if (enter) enter.addEventListener("click", function () {
      overlay.classList.add("hidden");
    });
    const tour = byId("start-system-tour");
    if (tour) tour.addEventListener("click", function () {
      overlay.classList.add("hidden");
      const target = byId("system-navigation-card") || document.querySelector(".nav-tabs");
      if (target) {
        target.classList.add("tour-highlight");
        target.scrollIntoView({ behavior: "smooth", block: "center" });
        window.setTimeout(function () { target.classList.remove("tour-highlight"); }, 4200);
      }
      addChatLine("system", "Tour started: use System State for live regime, Roadmap for lifecycle, Dev Registry for history, and System Guide for state meanings.");
    });
  }
  function runBootSequence() {
    const steps = Array.from(document.querySelectorAll(".boot-step"));
    steps.forEach(function (step) { step.classList.remove("active"); });
    steps.forEach(function (step, index) {
      window.setTimeout(function () {
        steps.forEach(function (item) { item.classList.remove("active"); });
        step.classList.add("active");
      }, index * 2500);
    });
  }
  bindControls();
  refreshState();
  window.setInterval(refreshState, pollMs);
})();
</script>
</body>
</html>"""
    return HTMLResponse(html) if HTMLResponse is not None else html


def _html_page(title: str, body: str) -> Any:
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{_escape(title)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; max-width: 980px; }}
nav a {{ margin-right: 1rem; }}
pre {{ background: #f6f8fa; padding: 1rem; overflow: auto; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #d0d7de; padding: 0.4rem; text-align: left; }}
button, input, textarea {{ font: inherit; margin: 0.25rem 0; }}
</style></head><body>{body}</body></html>"""
    return HTMLResponse(html) if HTMLResponse is not None else html


def _render_primary_workspace(display_state: Dict[str, Any]) -> str:
    active_stage = infer_active_workflow_stage(display_state)
    chat_placeholder = t("chat.placeholder")
    chat_send = t("chat.send")
    return f"""
    <section class="v2-primary-workspace" data-component="primary-workspace">
      <div class="v2-mode-switcher" aria-label="Workspace mode switcher">
        <button class="active" type="button" data-v2-mode="system">{t("workspace.system")}</button>
        <button type="button" data-v2-mode="chat">{t("workspace.chat")}</button>
        <button type="button" data-v2-mode="workflow">{t("workspace.workflow")}</button>
      </div>

      <div id="mode-system" class="v2-mode-panel active" data-mode-panel="system">
        <div class="v2-focus-kicker">{t("state.current_regime")}</div>
        <h1 id="state-regime" class="v2-regime-title">{t("empty.initializing")}</h1>

        <section class="v2-trust-hero" aria-label="Trust score gauge">
          <div>
            <span>{t("state.trust_score")}</span>
            <strong id="state-trust">{t("empty.signal")}</strong>
          </div>
          <div class="v2-trust-gauge"><span id="trust-meter"></span></div>
        </section>

        <section class="v2-active-decision">
          <span class="v2-kicker">{t("state.active_decision")}</span>
          <div class="v2-decision-line">
            <strong id="decision-action">neutral</strong>
            <span id="decision-confidence">{t("state.confidence")} 0.00</span>
          </div>
          <p id="decision-summary">{t("empty.initializing")}</p>
          <div class="v2-decision-meta">
            <span>{t("state.risk")} <strong id="decision-risk">{t("empty.context")}</strong></span>
            <span>{t("state.attention")} <strong id="decision-attention">{t("empty.signal")}</strong></span>
            <span>{t("state.liquidity")} <strong id="decision-liquidity">{t("empty.signal")}</strong></span>
          </div>
        </section>

        <section class="v2-system-summary">
          <div><span>{t("state.status")}</span><strong id="focus-runtime-status">{t("empty.initializing")}</strong></div>
          <div><span>{t("state.tick")}</span><strong id="state-tick">0</strong></div>
          <div><span>{t("state.liquidity")}</span><strong id="state-liquidity">{t("empty.signal")}</strong></div>
          <div><span>{t("state.attention")}</span><strong id="state-attention">{t("empty.signal")}</strong></div>
          <div><span>{t("state.volatility")}</span><strong id="state-volatility">{t("empty.signal")}</strong></div>
        </section>
      </div>

      <div id="mode-chat" class="v2-mode-panel" data-mode-panel="chat">
        <section class="v2-chat-card">
          <div class="v2-section-title">{t("workspace.chat")}</div>
          <div id="chat-messages" class="chat-messages" aria-live="polite"></div>
          <form id="chat-form" class="chat-form">
            <textarea id="chat-input" name="message" rows="3" maxlength="2000" placeholder="{chat_placeholder}"></textarea>
            <button class="v2-primary-button" type="submit">{chat_send}</button>
          </form>
        </section>
      </div>

      <div id="mode-workflow" class="v2-mode-panel" data-mode-panel="workflow">
        {render_workflow_graph(active_stage)}
      </div>
    </section>
    """


def _workflow_page(active_stage: str = "event_stream") -> Any:
    return render_workflow_page(active_stage)


def _render_control_plane_toolbar() -> str:
    return """
    <section class="control-plane-toolbar" data-component="mode-switcher">
      <div class="mode-switcher" aria-label="Workspace mode switcher">
        <button class="active" type="button" data-mode="chat">Chat Mode</button>
        <button type="button" data-mode="system">System Mode</button>
        <button type="button" data-mode="workflow">Workflow Mode</button>
        <button type="button" data-mode="architecture">Architecture Mode</button>
      </div>
      <a class="settings-link-button" href="/" aria-label="Open Home">Home</a>
      <a class="settings-link-button" href="/settings" aria-label="Open Settings">Settings</a>
    </section>
    """


def _render_execution_timeline() -> str:
    return """
    <section class="execution-timeline" data-component="execution-timeline">
      <div class="stream-header">
        <div>
          <span class="panel-kicker">Execution Timeline</span>
          <h2>Event -> Cognition -> Decision -> Explanation -> Feedback</h2>
        </div>
        <span id="stream-clock" class="stream-clock">Waiting</span>
      </div>
      <div class="execution-steps" aria-label="Execution timeline stages">
        <div class="execution-step">Event</div>
        <div class="execution-step">Cognition</div>
        <div class="execution-step">Decision</div>
        <div class="execution-step">Explanation</div>
        <div class="execution-step">Feedback</div>
      </div>
      <div id="event-stream" class="event-stream" aria-live="polite"></div>
    </section>
    """


def _render_roadmap_strip() -> str:
    roadmap = roadmap_api_payload(_roadmap_path())
    completed = roadmap.get("completed_layers", [])
    planned = roadmap.get("planned_layers", [])
    return f"""
    <section class="roadmap-strip" data-component="roadmap-strip">
      <div>
        <span class="panel-kicker">Roadmap</span>
        <strong>{_escape(str(roadmap.get("current_version", "Unknown")))}</strong>
        <span>{_escape(str(roadmap.get("next_stage", "Unknown")))}</span>
      </div>
      <div class="roadmap-strip-actions">
        <span>{len(completed)} completed</span>
        <span>{len(planned)} planned</span>
        <a class="control-button secondary" href="/dev-registry">Dev Registry</a>
      </div>
    </section>
    """


def _render_system_navigation_card() -> str:
    return """
    <section id="system-navigation-card" class="system-navigation-card" data-component="system-navigation-card">
      <div>
        <span class="panel-kicker">System Navigation</span>
        <h2>Choose the surface you need</h2>
        <p>Start with Dashboard for live state, Roadmap for lifecycle, or System Guide for state meanings.</p>
      </div>
      <nav class="system-navigation-links" aria-label="System navigation">
        <a href="/dashboard">Dashboard</a>
        <a href="/roadmap">Roadmap</a>
        <a href="/dev-registry">Dev Registry</a>
        <a href="/system-guide">System Guide</a>
      </nav>
    </section>
    """


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _db_path() -> Optional[str]:
    return os.environ.get("ATLAS_UI_DB_PATH") or os.environ.get("ATLAS_RUNTIME_DB")


def _ui_inbox_path() -> str:
    return os.environ.get("ATLAS_UI_INBOX") or str(DEFAULT_UI_INBOX)


def _event_inbox_dir() -> Optional[str]:
    return os.environ.get("ATLAS_EVENT_INBOX")


def _runtime_log_path() -> Optional[str]:
    return os.environ.get("ATLAS_RUNTIME_LOG")


def _decision_trace_path() -> Optional[str]:
    return os.environ.get("ATLAS_DECISION_TRACE_LOG")


def _snapshot_path() -> Optional[str]:
    return os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG")


def _llm_trace_path() -> Optional[str]:
    return os.environ.get("ATLAS_LLM_TRACE_LOG")


def _roadmap_path() -> Optional[str]:
    return os.environ.get("ATLAS_ROADMAP_PATH") or "docs/atlas_roadmap.json"


def _asset_file_path(asset_name: str) -> Path | None:
    if not asset_name or "/" in asset_name or "\\" in asset_name:
        return None
    if Path(asset_name).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        return None
    root = Path("docs/assets").resolve()
    path = (root / Path(asset_name).name).resolve()
    if root not in path.parents or not path.is_file():
        return None
    return path


def _user_config_path() -> Optional[str]:
    return os.environ.get("ATLAS_USER_CONFIG") or "runtime/config/user_config.json"


def _pid_file() -> Optional[str]:
    return os.environ.get("ATLAS_UI_PID_FILE")


def _ui_config_path() -> Optional[str]:
    return os.environ.get("ATLAS_UI_CONFIG")


def _configured_interval() -> int:
    user_config = load_user_config(_user_config_path())
    system = user_config.get("system") if isinstance(user_config.get("system"), dict) else {}
    if system.get("tick_interval") is not None:
        try:
            interval = int(system.get("tick_interval"))
            if interval in {10, 30, 60, 300}:
                return interval
        except (TypeError, ValueError):
            pass
    path = _ui_config_path()
    if not path or not Path(path).exists():
        return 60
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8")).get("tick_interval_seconds", 60)
        interval = int(value)
        return interval if interval in {10, 30, 60, 300} else 60
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return 60


def _configured_runtime_options() -> Dict[str, Any]:
    config = load_user_config(_user_config_path())
    system = config.get("system") if isinstance(config.get("system"), dict) else {}
    registry = load_provider_registry(_user_config_path())
    active = str(registry.get("active_provider") or "morecode")
    provider = next((item for item in registry.get("providers", []) if item.get("id") == active), {})
    return {
        "tick_interval": _configured_interval(),
        "llm_model": str(provider.get("model") or "gpt5.5"),
        "proactive_update_enabled": bool(system.get("proactive_update_enabled", True)),
        "proactive_update_interval_seconds": _positive_int(system.get("proactive_update_interval_seconds"), 7200),
    }


def _positive_int(value: Any, fallback: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(60, number)


class _FallbackApp:
    """Import-safe placeholder when FastAPI is not installed."""

    framework = "stdlib_http_fallback"


app = create_app()


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the UI server with FastAPI+uvicorn when available, else stdlib."""

    if FastAPI is not None:
        try:
            import uvicorn  # type: ignore

            uvicorn.run(app, host=host, port=port)
            return
        except ModuleNotFoundError:
            pass
    server = ThreadingHTTPServer((host, port), _StdlibHandler)
    server.serve_forever()


class _StdlibHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items() if values}
        if parsed.path == "/":
            state = state_api()
            self._send_html(_product_shell("home", _home_content_with_setup_banner(state), state))
        elif parsed.path == "/home":
            state = state_api()
            self._send_html(_product_shell("home", _home_content_with_setup_banner(state), state))
        elif parsed.path == "/setup":
            state = state_api()
            content, script = setup_content(load_user_config(_user_config_path()))
            self._send_html(_product_shell("setup", content, state, page_script=script))
        elif parsed.path == "/getting-started":
            state = state_api()
            config = load_user_config(_user_config_path())
            readiness = build_getting_started_status(config, state)
            content, script = render_getting_started_page(config, state, readiness)
            self._send_html(_product_shell("getting_started", content, state, page_script=script))
        elif parsed.path == "/getting-started/status":
            self._send_json(getting_started_status_api())
        elif parsed.path == "/chat":
            state = state_api()
            content, script = ask_content(state)
            self._send_html(_product_shell("ask", content, state, page_script=script))
        elif parsed.path == "/dashboard":
            state = state_api()
            content, script = ask_content(state)
            self._send_html(_product_shell("ask", content, state, page_script=script))
        elif parsed.path == "/portfolio":
            state = state_api()
            self._send_html(_product_shell("portfolio", portfolio_content(state), state))
        elif parsed.path == "/markets":
            data = _market_intelligence_state()
            if query.get("format") == "json":
                self._send_json(data)
            else:
                state = state_api()
                self._send_html(_product_shell("markets", markets_content(state), state))
        elif parsed.path == "/predictions":
            data = list_forecasts(db_path=_db_path())
            if query.get("format") == "json":
                self._send_json(data)
            else:
                state = state_api()
                self._send_html(_product_shell("predictions", predictions_content(data), state))
        elif parsed.path == "/learning":
            state = state_api()
            self._send_html(_product_shell("learning", learning_content(list_forecasts(db_path=_db_path()), state), state))
        elif parsed.path == "/settings":
            state = state_api()
            content, script = settings_content(load_user_config(_user_config_path()), state)
            self._send_html(_product_shell("settings", content, state, page_script=script))
        elif parsed.path == "/llm/providers":
            self._send_json(_safe_provider_registry())
        elif parsed.path.startswith("/assets/"):
            path = _asset_file_path(parsed.path.rsplit("/", 1)[-1])
            if path is None:
                self.send_error(404)
            else:
                self._send_file(path)
        elif parsed.path == "/workflow":
            state = state_api()
            content, script = workflow_content(state)
            self._send_html(_product_shell("workflow", content, state, page_script=script))
        elif parsed.path == "/roadmap":
            payload = roadmap_api_payload(_roadmap_path())
            if query.get("format", "").lower() == "json":
                self._send_json(payload)
            else:
                state = state_api()
                self._send_html(_product_shell("roadmap", roadmap_content(payload), state))
        elif parsed.path == "/roadmap.json":
            self._send_json(roadmap_api_payload(_roadmap_path()))
        elif parsed.path == "/dev-registry":
            state = state_api()
            self._send_html(_product_shell("dev_registry", dev_registry_content(load_roadmap(_roadmap_path()), state), state))
        elif parsed.path == "/system-guide":
            state = state_api()
            self._send_html(_product_shell("system_guide", system_guide_content(), state))
        elif parsed.path == "/state":
            self._send_json(state_api())
        elif parsed.path == "/replay":
            start = int(query.get("start_tick", 0))
            end = int(query.get("end_tick", 10))
            data = replay_session(
                start,
                end,
                decision_trace_path=_decision_trace_path(),
                snapshot_path=_snapshot_path(),
                llm_trace_path=_llm_trace_path(),
            )
            if query.get("format") == "json":
                self._send_json(data)
            else:
                state = state_api()
                self._send_html(_product_shell("workflow", replay_content(data), state))
        elif parsed.path == "/control":
            state = state_api()
            self._send_html(_product_shell("system_status", control_content(control_panel_state(db_path=_db_path(), pid_file=_pid_file())), state))
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("content-length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        payload = {key: values[-1] for key, values in parse_qs(raw).items() if values}
        if not payload and raw:
            try:
                decoded = json.loads(raw)
                payload = decoded if isinstance(decoded, dict) else {}
            except json.JSONDecodeError:
                payload = {}
        if parsed.path == "/chat/send":
            message = str(payload.get("message") or payload.get("content") or "").strip()
            if not message:
                self._send_json({"status": "error", "error": "message_required"}, status=400)
                return
            self._send_json({"status": "queued", "event": append_chat_event(message, inbox_path=_ui_inbox_path())})
        elif parsed.path == "/control/stop":
            self._send_json(stop_runtime_daemon(pid_file=_pid_file()))
        elif parsed.path == "/control/set_interval":
            self._send_json(adjust_tick_interval(int(payload.get("interval_seconds") or 60), config_path=_ui_config_path()))
        elif parsed.path == "/control/set_llm_provider":
            self._send_json(
                switch_llm_provider(
                    str(payload.get("provider") or "runtime"),
                    model=str(payload.get("model")) if payload.get("model") else None,
                    config_path=_ui_config_path(),
                )
            )
        elif parsed.path == "/control/start":
            runtime_options = _configured_runtime_options()
            self._send_json(
                start_runtime_daemon(
                    interval_seconds=runtime_options["tick_interval"],
                    db_path=_db_path(),
                    log_path=_runtime_log_path(),
                    inbox_dir=_event_inbox_dir(),
                    ui_inbox_path=_ui_inbox_path(),
                    market_config_path=_user_config_path(),
                    llm_model=runtime_options["llm_model"],
                    proactive_update_enabled=runtime_options["proactive_update_enabled"],
                    proactive_update_every_seconds=runtime_options["proactive_update_interval_seconds"],
                    pid_file=_pid_file(),
                )
            )
        elif parsed.path == "/settings":
            self._send_json(save_user_config(payload, _user_config_path()))
        elif parsed.path == "/predictions":
            self._send_json(create_forecast(payload, db_path=_db_path()))
        elif parsed.path == "/predictions/evaluate":
            forecast_id = str(payload.get("forecast_id") or "")
            if not forecast_id:
                self._send_json({"status": "error", "error": "forecast_id_required"}, status=400)
                return
            self._send_json(evaluate_forecast(forecast_id, payload, db_path=_db_path()))
        elif parsed.path == "/predictions/mature":
            forecast_id = str(payload.get("forecast_id") or "")
            if not forecast_id:
                self._send_json({"status": "error", "error": "forecast_id_required"}, status=400)
                return
            self._send_json(mark_forecast_matured(forecast_id, payload, db_path=_db_path()))
        elif parsed.path == "/llm/provider/test":
            provider_id = str(payload.get("provider_id") or payload.get("provider") or "")
            if not provider_id:
                self._send_json({"status": "error", "error": "provider_required"}, status=400)
                return
            self._send_json(health_check_provider(provider_id, path=_user_config_path()))
        elif parsed.path == "/llm/provider/models":
            provider_id = str(payload.get("provider_id") or payload.get("provider") or "")
            if not provider_id:
                self._send_json({"status": "error", "error": "provider_required"}, status=400)
                return
            self._send_json(list_provider_models(provider_id, path=_user_config_path()))
        elif parsed.path == "/llm/providers/test_all":
            registry = _safe_provider_registry()
            results = [
                health_check_provider(str(provider.get("id")), path=_user_config_path())
                for provider in registry.get("providers", [])
            ]
            refreshed = _safe_provider_registry()
            self._send_json(
                {
                    "status": "checked",
                    "results": results,
                    "summary": _provider_registry_summary(refreshed),
                    "registry": refreshed,
                }
            )
        elif parsed.path == "/ui/language":
            self._send_json(set_language(str(payload.get("language") or "en"), _user_config_path()))
        else:
            self.send_error(404)

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, value: Any, status: int = 200) -> None:
        body = str(value.body.decode("utf-8") if hasattr(value, "body") else value).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, status: int = 200) -> None:
        body = path.read_bytes()
        content_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
        }.get(path.suffix.lower(), "application/octet-stream")
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    run_server()
