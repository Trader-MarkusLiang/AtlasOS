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
from runtime.llm.task_routing import load_task_routes, route_task_request, safe_task_routes_view
from runtime.portfolio_context import build_portfolio_context
from runtime.portfolio_valuation import build_local_portfolio_valuation
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
from ui.i18n.i18n import current_language, set_language, t, translation_payload
from ui.presentation.cognitive_localization import build_cognitive_presentation
from ui.presentation.home_intelligence import build_candidate_pool
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
    candidate_pool_content,
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
        return _product_shell("home", _home_content_with_setup_banner(state), state, include_inspector=False)

    @app.get("/home", response_class=HTMLResponse)
    async def home() -> Any:
        state = state_api()
        return _product_shell("home", _home_content_with_setup_banner(state), state, include_inspector=False)

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

    @app.get("/candidates", response_class=HTMLResponse)
    async def candidates() -> Any:
        state = state_api()
        return _product_shell("candidates", candidate_pool_content(state), state)

    @app.get("/research-candidates", response_class=HTMLResponse)
    async def research_candidates() -> Any:
        state = state_api()
        return _product_shell("candidates", candidate_pool_content(state), state)

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

    @app.get("/llm/task-routes")
    async def llm_task_routes() -> Any:
        return JSONResponse(_safe_task_routes())

    @app.post("/llm/task-route/test")
    async def llm_task_route_test(request: Request) -> Any:
        payload = await _request_payload(request)
        role = str(payload.get("task_role") or "").strip().lower()
        if role not in {"workhorse", "research", "decision"}:
            return JSONResponse({"status": "error", "error": "unsupported_task_role"}, status_code=400)
        result = route_task_request(
            role,
            _task_route_test_prompt(role),
            {
                "test": True,
                "runtime_context": {
                    "trigger_type": "settings_task_route_test",
                    "feedback_applied": False,
                },
            },
            config_path=_user_config_path(),
        )
        return JSONResponse(_safe_task_test_result(result))

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

    @app.get("/static/{filename}")
    async def static_file(filename: str) -> Any:
        path = _static_file_path(filename)
        if path is None:
            return JSONResponse({"status": "error", "error": "file_not_found"}, status_code=404)
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

    @app.get("/state/summary")
    async def state_summary() -> Any:
        return JSONResponse(state_summary_api())

    @app.get("/brief/current")
    async def brief_current() -> Any:
        return JSONResponse(brief_current_api())

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
    forecast_ledger = list_forecasts(db_path=_db_path(), limit=25)
    candidate_pool = build_candidate_pool(portfolio_context=portfolio_context)
    market_intelligence = _market_intelligence_state()
    latest_packet = metadata.get("decision_packet", {})
    llm_summary["latest_inference_status"] = _llm_inference_status(latest_packet)
    runtime = runtime_status(pid_file=_pid_file(), db_path=_db_path())
    user_config = load_user_config(_user_config_path())
    system_config = user_config.get("system", {}) if isinstance(user_config.get("system"), dict) else {}
    runtime["mode"] = str(system_config.get("runtime_mode") or "simulation")
    data_provenance = _build_data_provenance(
        market_intelligence=market_intelligence,
        portfolio_context=portfolio_context,
        llm_status=llm_summary.get("latest_inference_status", "not_run"),
        latest_packet=latest_packet,
    )
    payload = {
        "timestamp": utc_now_iso(),
        "regime_state": system_state.get("current_state", "Unknown"),
        "proposed_state": system_state.get("proposed_state", "Unknown"),
        "attention": fusion.get("attention_pressure"),
        "liquidity": fusion.get("liquidity_score"),
        "volatility": fusion.get("volatility_regime"),
        "trust_index": store.get_state("system_trust_state").get("rolling_trust_index"),
        "structural_coevolution_state": store.get_state("structural_coevolution_state"),
        "self_organization_state": store.get_state("self_organization_state"),
        "last_decision_packet": latest_packet,
        "last_decision_brief_id": latest_brief.get("id"),
        "portfolio_context": portfolio_context,
        "forecast_ledger": forecast_ledger,
        "candidate_pool": candidate_pool,
        "market_intelligence": market_intelligence,
        "data_provenance": data_provenance,
        "proactive_update_state": store.get_state("proactive_update_state"),
        "daily_cycle": store.get_state("daily_cycle_state"),
        "brief_runtime_state": store.get_state("current_brief_state"),
        "evidence_assessment_state": store.get_state("evidence_assessment_state"),
        "candidate_runtime_overlay": store.get_state("candidate_runtime_overlay"),
        "runtime": runtime,
        "llm_trace_summary": llm_summary,
        "llm_provider_registry": _safe_provider_registry(),
        "llm_task_routes": _safe_task_routes(),
        "llm_task_runtime_state": store.get_state("llm_task_runtime_state"),
        "last_event_summary": event_history[0] if event_history else {},
        "tick_counter": len(transitions),
        "dashboard": build_dashboard_state(
            db_path=_db_path(),
            decision_trace_path=_decision_trace_path(),
            snapshot_path=_snapshot_path(),
            limit=20,
        ),
    }
    payload["ui_presentation"] = build_cognitive_presentation(payload, current_language())
    return payload


def state_summary_api() -> Dict[str, Any]:
    """Return the bounded state required by global polling and Brief revision checks."""

    store = StateStore(db_path=_db_path())
    system_state = store.get_system_state()
    latest_brief = store.get_latest_decision_brief()
    metadata = latest_brief.get("metadata", {}) if isinstance(latest_brief, dict) else {}
    packet = metadata.get("decision_packet", {}) if isinstance(metadata, dict) else {}
    packet = packet if isinstance(packet, dict) else {}
    market = _market_intelligence_state()
    observations = market.get("observations", []) if isinstance(market.get("observations"), list) else []
    usable = [item for item in observations if isinstance(item, dict) and item.get("data_quality_status") in {"Available", "Partial"}]
    partial = [item for item in usable if item.get("data_quality_status") == "Partial"]
    last_close = [item for item in usable if item.get("market_session_status") == "LAST_MARKET_CLOSE"]
    portfolio = build_portfolio_context(config_path=_user_config_path())
    llm_summary = _llm_trace_summary(read_llm_traces(log_path=_llm_trace_path(), limit=100))
    llm_summary["latest_inference_status"] = _llm_inference_status(packet)
    runtime = runtime_status(pid_file=_pid_file(), db_path=_db_path())
    user_config = load_user_config(_user_config_path())
    system_config = user_config.get("system", {}) if isinstance(user_config.get("system"), dict) else {}
    runtime["mode"] = str(system_config.get("runtime_mode") or "simulation")
    events = store.get_event_history(limit=1)
    return {
        "timestamp": utc_now_iso(),
        "regime_state": system_state.get("current_state", "Unknown"),
        "proposed_state": system_state.get("proposed_state", "Unknown"),
        "trust_index": store.get_state("system_trust_state").get("rolling_trust_index"),
        "tick_counter": store.count_state_transitions(),
        "market_intelligence": {
            "status": market.get("status"),
            "degraded": market.get("degraded", True),
            "channels": market.get("channels", {}),
            "observation_count": len(observations),
            "usable_observation_count": len(usable),
            "partial_observation_count": len(partial),
            "last_market_close_count": len(last_close),
            "last_market_close_at": max(
                (str(item.get("market_session_timestamp") or item.get("timestamp") or "") for item in last_close),
                default=None,
            ),
            "timestamp": market.get("timestamp"),
        },
        "portfolio_context": {
            "status": portfolio.get("status"),
            "exposure_sum_pct": portfolio.get("exposure_sum_pct"),
        },
        "llm_trace_summary": llm_summary,
        "llm_provider_registry": _safe_provider_registry(),
        "last_decision_packet": {
            "recommended_action": packet.get("recommended_action"),
            "confidence": packet.get("confidence"),
            "risk_level": packet.get("risk_level"),
            "causal_summary": packet.get("causal_summary"),
        },
        "last_decision_brief_id": latest_brief.get("id"),
        "brief_runtime_state": store.get_state("current_brief_state"),
        "runtime": runtime,
        "proactive_update_state": store.get_state("proactive_update_state"),
        "daily_cycle": store.get_state("daily_cycle_state"),
        "last_event_summary": events[0] if events else {},
    }


def brief_current_api() -> Dict[str, Any]:
    """Return the coherent current Brief and renderable Home sections on demand."""

    state = state_api()
    brief = state.get("brief_runtime_state") if isinstance(state.get("brief_runtime_state"), dict) else {}
    return {
        "status": "available" if brief else "initializing",
        "brief_revision": int(brief.get("brief_revision", 0) or 0),
        "published_at": brief.get("published_at"),
        "trigger_reason": brief.get("trigger_reason"),
        "changed_sections": brief.get("changed_sections", []),
        "sections": brief.get("sections", {}),
        "review_summary": brief.get("review_summary", {}),
        "home_html": _home_content_with_setup_banner(state),
        "no_trading_execution": True,
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
    roles = Counter(str(item.get("task_role", "legacy")) for item in records)
    latest = records[-1] if records else {}
    return {
        "call_count": len(records),
        "providers": dict(providers),
        "task_roles": dict(roles),
        "latest_model": latest.get("model"),
        "latest_latency_ms": latest.get("latency_ms"),
        "latest_hallucination_risk_proxy": latest.get("hallucination_risk_proxy"),
    }


def _llm_inference_status(packet: Any) -> str:
    if not isinstance(packet, dict) or not packet:
        return "not_run"
    trace = str(packet.get("reasoning_trace") or "").lower()
    summary = str(packet.get("causal_summary") or "").lower()
    if any(marker in trace for marker in ("all_providers_failed", "invalid_llm_output", "provider_error")):
        return "failed"
    if "unavailable" in summary or "invalid" in summary:
        return "failed"
    return "succeeded"


def _build_data_provenance(
    *,
    market_intelligence: Dict[str, Any],
    portfolio_context: Dict[str, Any],
    llm_status: str,
    latest_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a standardized provenance verdict for each data category.

    Each entry reports whether the data is fresh/valid versus merely present,
    so UI components never conflate "data exists" with "data is trustworthy."
    """
    market_observations = market_intelligence.get("observations") if isinstance(market_intelligence.get("observations"), list) else []
    usable_quality = {"Available", "Partial"}
    usable_observations = [
        item for item in market_observations
        if isinstance(item, dict) and str(item.get("data_quality_status", "") or "") in usable_quality
    ]
    market_verdict = "fresh" if usable_observations else (
        "degraded" if market_observations else (
            "unconfigured" if market_intelligence.get("status") in ("not_run", "no_configured_assets") else "missing"
        )
    )
    portfolio_status = str(portfolio_context.get("status") or "").lower()
    portfolio_verdict = "configured" if portfolio_status == "configured" else (
        "stale" if portfolio_status in ("partial", "limited") else "missing"
    )
    inference_verdict = llm_status if llm_status in ("succeeded", "failed") else "not_run"
    packet_reasoning = str(latest_packet.get("reasoning_trace") or "")
    packet_verdict = "succeeded" if packet_reasoning and not any(
        m in packet_reasoning.lower() for m in ("all_providers_failed", "invalid_llm_output", "provider_error")
    ) else "failed" if packet_reasoning else "not_run"
    degraded_channels = [
        key for key, value in (market_intelligence.get("channels") or {}).items()
        if str(value).upper() in ("FAILED", "RATE_LIMITED")
    ]
    missing_channels = [
        key for key, value in (market_intelligence.get("channels") or {}).items()
        if str(value).upper() in ("NOT_CONFIGURED",)
    ]
    return {
        "market_intelligence": {
            "verdict": market_verdict,
            "observation_count": len(market_observations),
            "usable_count": len(usable_observations),
            "degraded": market_intelligence.get("degraded", True),
            "degraded_channels": degraded_channels,
            "missing_channels": missing_channels,
        },
        "portfolio": {
            "verdict": portfolio_verdict,
            "status": portfolio_status,
        },
        "llm_inference": {
            "verdict": inference_verdict,
        },
        "last_decision_packet": {
            "verdict": packet_verdict,
        },
        "summary": _data_provenance_summary(market_verdict, portfolio_verdict, inference_verdict),
    }


def _data_provenance_summary(market: str, portfolio: str, inference: str) -> str:
    parts = []
    if market == "fresh":
        parts.append("market=fresh")
    elif market in ("degraded", "missing"):
        parts.append(f"market={market}")
    else:
        parts.append("market=unconfigured")
    parts.append(f"portfolio={portfolio}")
    parts.append(f"inference={inference}")
    verdicts = [market, portfolio, inference]
    if all(v == "fresh" or (v == "configured") for v in verdicts):
        return "all_fresh"
    if any(v in ("degraded", "failed", "missing", "stale") for v in verdicts):
        return "degraded_" + "_".join(v for v in verdicts if v in ("degraded", "failed", "missing", "stale"))
    return "; ".join(parts)


def _safe_provider_registry() -> Dict[str, Any]:
    """Return provider registry from the active UI config without exposing secrets."""

    return safe_registry_view(load_provider_registry(_user_config_path()))


def _safe_task_routes() -> Dict[str, Any]:
    registry = load_provider_registry(_user_config_path())
    return safe_task_routes_view(load_task_routes(_user_config_path()), registry)


def _task_route_test_prompt(role: str) -> str:
    if role == "workhorse":
        return 'Return JSON only: {"status":"ok","query_intent":"route test","signals":[],"unknowns":[]}.'
    if role == "research":
        return 'Return JSON only with status, summary, portfolio_relevance, causal_factors, counter_evidence, hypotheses, uncertainties.'
    return (
        'Return a valid Atlas DecisionPacket JSON with regime_state, confidence, risk_level, attention_state, '
        'liquidity_state, causal_summary, recommended_action, and reasoning_trace. Use neutral and confidence 0.'
    )


def _safe_task_test_result(result: Dict[str, Any]) -> Dict[str, Any]:
    usage = result.get("usage", {}) if isinstance(result.get("usage"), dict) else {}
    return {
        "status": result.get("status"),
        "task_role": result.get("task_role"),
        "route_status": result.get("route_status"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "latency_ms": result.get("latency_ms"),
        "usage": usage,
        "estimated_cost": result.get("estimated_cost", "Unknown"),
        "cost_status": result.get("cost_status", "Unknown"),
        "cache_status": result.get("cache_status"),
        "fallback_attempts": result.get("fallback_attempts", []),
        "error": result.get("error", ""),
        "output_received": bool(str(result.get("content") or "").strip()),
    }


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
    home_state = dict(state)
    home_state["local_portfolio_valuation"] = build_local_portfolio_valuation(
        config=config,
        market_intelligence=state.get("market_intelligence") if isinstance(state.get("market_intelligence"), dict) else {},
    )
    readiness = build_getting_started_status(config, state)
    overall = readiness.get("overall_readiness", {}) if isinstance(readiness.get("overall_readiness"), dict) else {}
    if overall.get("can_start"):
        return home_content(home_state)
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
    return banner + home_content(home_state)


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
    ui_lang = current_language()
    html = f"""<!doctype html>
	<html lang="{ui_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas OS Control Interface</title>
<link rel="stylesheet" href="/static/atlas_shell.css">
</head>
<body>
<div class="shell">
""" + shell + """
</div>
<script src="/static/atlas_shell.js">
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


def _static_file_path(filename: str) -> Path | None:
    if not filename or "/" in filename or "\\" in filename:
        return None
    allowed_suffixes = {".css", ".js"}
    if Path(filename).suffix.lower() not in allowed_suffixes:
        return None
    root = Path("ui/static").resolve()
    path = (root / Path(filename).name).resolve()
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
            self._send_html(_product_shell("home", _home_content_with_setup_banner(state), state, include_inspector=False))
        elif parsed.path == "/home":
            state = state_api()
            self._send_html(_product_shell("home", _home_content_with_setup_banner(state), state, include_inspector=False))
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
        elif parsed.path in {"/candidates", "/research-candidates"}:
            state = state_api()
            self._send_html(_product_shell("candidates", candidate_pool_content(state), state))
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
        elif parsed.path == "/llm/task-routes":
            self._send_json(_safe_task_routes())
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
        elif parsed.path == "/state/summary":
            self._send_json(state_summary_api())
        elif parsed.path == "/brief/current":
            self._send_json(brief_current_api())
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
        elif parsed.path == "/llm/task-route/test":
            role = str(payload.get("task_role") or "").strip().lower()
            if role not in {"workhorse", "research", "decision"}:
                self._send_json({"status": "error", "error": "unsupported_task_role"}, status=400)
                return
            result = route_task_request(
                role,
                _task_route_test_prompt(role),
                {"test": True, "runtime_context": {"trigger_type": "settings_task_route_test", "feedback_applied": False}},
                config_path=_user_config_path(),
            )
            self._send_json(_safe_task_test_result(result))
        elif parsed.path == "/ui/language":
            self._send_json(set_language(str(payload.get("language") or "en"), _user_config_path()))
        else:
            self.send_error(404)

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, value: Any, status: int = 200) -> None:
        body = str(value.body.decode("utf-8") if hasattr(value, "body") else value).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("cache-control", "no-store")
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
