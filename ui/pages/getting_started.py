"""Guided Start Center for first-time Atlas OS users.

This page is a UI-only orchestration surface over existing runtime APIs. It
does not import cognition modules, modify Decision Contract semantics, or
create trading behavior.
"""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


REQUIRED_INTERVALS = {10, 30, 60, 300}
ONLINE_HEALTH = {"healthy", "reachable"}
MARKET_SIGNAL_STATES = {"LIVE", "DELAYED", "CACHED", "SIMULATED"}


def build_getting_started_status(config: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any]:
    """Build a no-secret readiness projection from existing config and state."""

    lang = _config_language(config)
    registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    providers = registry.get("providers") if isinstance(registry.get("providers"), list) else []
    active_provider_id = str(registry.get("active_provider") or "")
    active_provider = _active_provider(providers, active_provider_id)
    provider_configured = _provider_configured(active_provider)
    provider_health = str(active_provider.get("health") or "unknown")
    provider_status = "READY" if provider_health in ONLINE_HEALTH else ("READY_DEGRADED" if provider_configured else "NEEDS_CONFIGURATION")

    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    channel_counts = _channel_counts(channels)
    market_has_signal = any(str(value).upper() in MARKET_SIGNAL_STATES for value in channels.values())
    market_status = "READY_DEGRADED" if not market_has_signal else ("READY_DEGRADED" if market.get("degraded") else "READY")

    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []
    portfolio_status = "READY" if positions else "OPTIONAL"

    system = config.get("system") if isinstance(config.get("system"), Mapping) else {}
    interval = _int(system.get("tick_interval"), 60)
    runtime_settings_status = "READY" if interval in REQUIRED_INTERVALS else "BLOCKED"
    runtime = state.get("runtime") if isinstance(state.get("runtime"), Mapping) else {}
    runtime_running = bool(runtime.get("running"))
    tick_counter = _int(state.get("tick_counter"), 0)
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    brief_id = str(state.get("last_decision_brief_id") or "")
    first_brief_status = "READY" if brief_id or packet else ("IN_PROGRESS" if runtime_running or tick_counter else "NEEDS_CONFIGURATION")

    steps = [
        _step("understand", "getting.step.understand", "READY", "getting.step.understand_note"),
        _step("language", "getting.step.language", "READY", "getting.step.language_note"),
        _step("provider", "getting.step.provider", provider_status, "getting.step.provider_note"),
        _step("market", "getting.step.market", market_status, "getting.step.market_note"),
        _step("portfolio", "getting.step.portfolio", portfolio_status, "getting.step.portfolio_note"),
        _step("runtime", "getting.step.runtime", runtime_settings_status, "getting.step.runtime_note"),
        _step("start", "getting.step.start", "READY" if runtime_running else ("READY_DEGRADED" if provider_configured and runtime_settings_status == "READY" else "NEEDS_CONFIGURATION"), "getting.step.start_note"),
        _step("brief", "getting.step.brief", first_brief_status, "getting.step.brief_note"),
    ]
    completed = sum(1 for item in steps if item["status"] == "READY")
    blocking = [item["id"] for item in steps if item["status"] in {"NEEDS_CONFIGURATION", "BLOCKED"} and item["id"] not in {"brief"}]
    if blocking:
        overall = "NEEDS_CONFIGURATION" if "provider" in blocking else "BLOCKED"
    elif any(item["status"] == "READY_DEGRADED" for item in steps):
        overall = "READY_DEGRADED"
    else:
        overall = "READY"

    return {
        "language": {"status": "READY", "value": lang},
        "provider": {
            "status": provider_status,
            "id": active_provider_id,
            "label": str(active_provider.get("label") or active_provider_id or ""),
            "health": provider_health,
            "latency_ms": active_provider.get("last_latency_ms"),
            "model": str(active_provider.get("model") or ""),
            "base_url_configured": bool(str(active_provider.get("base_url") or "")),
            "models_count": len(active_provider.get("available_models") if isinstance(active_provider.get("available_models"), list) else []),
        },
        "market_data": {
            "status": market_status,
            "timestamp": market.get("timestamp"),
            "channel_counts": channel_counts,
            "channels": dict(channels),
            "degraded": bool(market.get("degraded", True)),
        },
        "portfolio": {
            "status": portfolio_status,
            "position_count": len(positions),
            "exposure_sum_pct": portfolio.get("exposure_sum_pct"),
            "consistency": portfolio.get("portfolio_consistency") or "PASS",
        },
        "runtime": {
            "status": "READY" if runtime_running else runtime_settings_status,
            "running": runtime_running,
            "pid": runtime.get("pid"),
            "tick_interval": interval,
            "tick_counter": tick_counter,
        },
        "first_brief": {
            "status": first_brief_status,
            "brief_id": brief_id,
            "decision": packet.get("recommended_action") if packet else "",
            "confidence": packet.get("confidence") if packet else None,
            "risk_level": packet.get("risk_level") if packet else "",
        },
        "overall_readiness": {
            "status": overall,
            "completed_steps": completed,
            "total_steps": len(steps),
            "blocking_steps": blocking,
            "can_start": provider_configured and runtime_settings_status == "READY",
        },
        "steps": steps,
        "safe": {"no_secrets": True, "read_only_cognition": True, "no_trading_execution": True},
    }


def render_getting_started_page(
    config: Mapping[str, Any],
    state: Mapping[str, Any],
    readiness: Mapping[str, Any] | None = None,
) -> tuple[str, str]:
    """Render the Guided Start Center content and page script."""

    lang = current_language()
    status = dict(readiness or build_getting_started_status(config, state))
    registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    providers = registry.get("providers") if isinstance(registry.get("providers"), list) else []
    active = str(registry.get("active_provider") or "")
    active_provider = _active_provider(providers, active)
    system = config.get("system") if isinstance(config.get("system"), Mapping) else {}
    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []
    strings = _strings(lang)

    content = f"""
    <style>{GETTING_STARTED_CSS}</style>
    <section class="getting-shell" data-getting-started>
      <aside class="getting-stepper" aria-label="{escape(t("getting.stepper", lang))}">
        <div class="getting-progress">
          <span class="kicker">{escape(t("getting.progress", lang))}</span>
          <strong id="getting-progress-count">{escape(_progress_text(status, lang))}</strong>
          <div class="getting-progress-bar"><span id="getting-progress-bar" style="width: {_progress_width(status)}%;"></span></div>
        </div>
        <nav class="getting-step-list">
          {_stepper(status.get("steps", []), lang)}
        </nav>
      </aside>

      <main class="getting-main">
        <section class="hero-panel getting-hero">
          <span class="kicker">{escape(t("getting.kicker", lang))}</span>
          <h1 class="hero-title">{escape(t("getting.title", lang))}</h1>
          <p class="hero-copy">{escape(t("getting.subtitle", lang))}</p>
          <div class="getting-quick-card" data-overall-status="{escape(str(status.get("overall_readiness", {}).get("status", "")))}">
            <div>
              <span class="kicker">{escape(t("getting.quick_start", lang))}</span>
              <h2 id="quick-title">{escape(_quick_title(status, lang))}</h2>
              <p id="quick-copy">{escape(_quick_copy(status, lang))}</p>
            </div>
            <div class="button-row">
              <button class="primary-button" type="button" id="getting-quick-start">{escape(t("getting.start_atlas", lang))}</button>
              <a class="secondary-button" href="/">{escape(t("getting.open_home", lang))}</a>
            </div>
          </div>
        </section>

        <section id="understand" class="focus-card getting-section">
          <span class="getting-index">01</span>
          <h2>{escape(t("getting.understand_title", lang))}</h2>
          <p>{escape(t("getting.understand_body", lang))}</p>
          <div class="getting-meaning-grid">
            <div><strong>{escape(t("getting.unknown_label", lang))}</strong><span>{escape(t("getting.unknown_meaning", lang))}</span></div>
            <div><strong>{escape(t("getting.neutral_label", lang))}</strong><span>{escape(t("getting.neutral_meaning", lang))}</span></div>
            <div><strong>{escape(t("getting.no_trade_label", lang))}</strong><span>{escape(t("getting.no_trade_meaning", lang))}</span></div>
          </div>
          <div class="getting-concepts" style="margin-top:18px; display:grid; gap:10px; grid-template-columns:repeat(2,minmax(0,1fr));">
            <div class="getting-concept-card">
              <strong>{escape(t("getting.concept_decision_first", lang))}</strong>
              <span>{escape(t("getting.concept_decision_first_body", lang))}</span>
            </div>
            <div class="getting-concept-card">
              <strong>{escape(t("getting.concept_knowledge_pyramid", lang))}</strong>
              <span>{escape(t("getting.concept_knowledge_pyramid_body", lang))}</span>
            </div>
            <div class="getting-concept-card">
              <strong>{escape(t("getting.concept_cde", lang))}</strong>
              <span>{escape(t("getting.concept_cde_body", lang))}</span>
            </div>
            <div class="getting-concept-card">
              <strong>{escape(t("getting.concept_wealth_blind", lang))}</strong>
              <span>{escape(t("getting.concept_wealth_blind_body", lang))}</span>
            </div>
          </div>
          <button class="secondary-button" type="button" id="mark-understood">{escape(t("getting.mark_understood", lang))}</button>
        </section>

        <section id="language" class="focus-card getting-section">
          <span class="getting-index">02</span>
          <h2>{escape(t("getting.language_title", lang))}</h2>
          <p>{escape(t("getting.language_body", lang))}</p>
          <div class="button-row">
            <button class="secondary-button" type="button" data-language-choice="en">English</button>
            <button class="secondary-button" type="button" data-language-choice="zh">中文</button>
          </div>
        </section>

        <section id="provider" class="focus-card getting-section">
          <span class="getting-index">03</span>
          <h2>{escape(t("getting.provider_title", lang))}</h2>
          <p>{escape(t("getting.provider_body", lang))}</p>
          <div class="form-grid">
            <label>{escape(t("model.active_provider", lang))}
              <select id="getting-provider-select">{_provider_options(providers, active)}</select>
            </label>
            <label>{escape(t("model.model", lang))}
              <input id="getting-model" list="getting-model-options" value="{escape(str(active_provider.get("model") or ""))}" placeholder="{escape(t("provider.custom_model_placeholder", lang))}">
              <datalist id="getting-model-options">{_model_options(active_provider)}</datalist>
            </label>
          </div>
          <label>{escape(t("settings.base_url", lang))}
            <input id="getting-base-url" value="{escape(str(active_provider.get("base_url") or ""))}" placeholder="https://...">
          </label>
          <label>{escape(t("settings.api_key", lang))}
            <input id="getting-api-key" type="password" autocomplete="off" placeholder="{escape(t("setup.api_key_hint", lang))}">
          </label>
          <div class="button-row">
            <button class="secondary-button" type="button" id="getting-save-provider">{escape(t("getting.save_provider", lang))}</button>
            <button class="secondary-button" type="button" id="getting-test-provider">{escape(t("setup.test_connection", lang))}</button>
            <button class="secondary-button" type="button" id="getting-discover-models">{escape(t("getting.discover_models", lang))}</button>
          </div>
          <p class="getting-status" id="getting-provider-status" role="status">{escape(_provider_status_text(status, lang))}</p>
        </section>

        <section id="market" class="focus-card getting-section">
          <span class="getting-index">04</span>
          <h2>{escape(t("getting.market_title", lang))}</h2>
          <p>{escape(t("getting.market_body", lang))}</p>
          <div id="market-channel-matrix" class="getting-channel-grid">
            {_market_channels(status.get("market_data", {}).get("channels", {}), lang)}
          </div>
          <button class="secondary-button" type="button" id="refresh-market-readiness">{escape(t("getting.refresh_readiness", lang))}</button>
        </section>

        <section id="portfolio" class="focus-card getting-section">
          <span class="getting-index">05</span>
          <h2>{escape(t("getting.portfolio_title", lang))}</h2>
          <p>{escape(t("setup.assets_note", lang))}</p>
          <div id="getting-asset-rows" class="getting-asset-list">{_asset_rows(positions, lang)}</div>
          <div class="button-row">
            <button class="secondary-button" type="button" id="getting-add-asset">{escape(t("setup.add_asset", lang))}</button>
            <button class="secondary-button" type="button" id="getting-save-portfolio">{escape(t("getting.save_portfolio", lang))}</button>
          </div>
          <p class="getting-status" id="getting-portfolio-status">{escape(_portfolio_status_text(status, lang))}</p>
        </section>

        <section id="runtime" class="focus-card getting-section">
          <span class="getting-index">06</span>
          <h2>{escape(t("getting.runtime_title", lang))}</h2>
          <p>{escape(t("getting.runtime_body", lang))}</p>
          <div class="form-grid">
            <div class="metric-card">
              <span>{escape(t("system.tick_interval", lang))}</span>
              <strong>{escape(t("system.tick_interval_fixed", lang))}</strong>
              <p>{escape(t("system.tick_interval_note", lang))}</p>
              <input id="getting-interval" type="hidden" value="60">
            </div>
            <label>{escape(t("system.simulation_mode", lang))}
              <select id="getting-runtime-mode">
                <option value="simulation"{_selected(system.get("runtime_mode"), "simulation")}>{escape(t("getting.simulation", lang))}</option>
                <option value="live"{_selected(system.get("runtime_mode"), "live")}>{escape(t("getting.live_mode", lang))}</option>
              </select>
            </label>
          </div>
          <button class="secondary-button" type="button" id="getting-save-runtime">{escape(t("getting.save_runtime", lang))}</button>
        </section>

        <section id="start" class="focus-card getting-section">
          <span class="getting-index">07</span>
          <h2>{escape(t("getting.start_title", lang))}</h2>
          <p>{escape(t("getting.start_body", lang))}</p>
          <div class="button-row">
            <button class="primary-button" type="button" id="getting-start-runtime">{escape(t("getting.start_atlas", lang))}</button>
            <button class="secondary-button" type="button" id="getting-stop-runtime">{escape(t("system.stop", lang))}</button>
          </div>
          <ol class="getting-boot-list" id="getting-boot-list">
            <li>{escape(t("getting.boot.waiting", lang))}</li>
          </ol>
        </section>

        <section id="brief" class="focus-card getting-section">
          <span class="getting-index">08</span>
          <h2>{escape(t("getting.brief_title", lang))}</h2>
          <p>{escape(t("getting.brief_body", lang))}</p>
          <div class="section-grid">
            {_metric(t("state.tick", lang), str(status.get("runtime", {}).get("tick_counter", 0)), t("getting.first_tick", lang))}
            {_metric(t("state.active_decision", lang), _brief_value(status), t("getting.first_brief", lang))}
            {_metric(t("state.status", lang), _status_label(str(status.get("first_brief", {}).get("status")), lang), t("getting.resume_hint", lang))}
          </div>
          <div class="button-row" style="margin-top: 12px;">
            <a class="primary-button" href="/">{escape(t("getting.open_home", lang))}</a>
            <a class="secondary-button" href="/dashboard">{escape(t("setup.ask_atlas", lang))}</a>
          </div>
        </section>
      </main>

      <aside class="getting-summary">
        <section class="focus-card">
          <span class="kicker">{escape(t("getting.live_summary", lang))}</span>
          <dl class="getting-summary-list">
            <dt>{escape(t("model.active_provider", lang))}</dt><dd id="summary-provider">{escape(str(status.get("provider", {}).get("label") or t("empty.context", lang)))}</dd>
            <dt>{escape(t("provider.latency", lang))}</dt><dd id="summary-latency">{escape(_latency_text(status.get("provider", {}).get("latency_ms"), lang))}</dd>
            <dt>{escape(t("markets.data_health", lang))}</dt><dd id="summary-market">{escape(_market_summary(status, lang))}</dd>
            <dt>{escape(t("portfolio.positions", lang))}</dt><dd id="summary-portfolio">{escape(str(status.get("portfolio", {}).get("position_count", 0)))}</dd>
            <dt>{escape(t("state.status", lang))}</dt><dd id="summary-runtime">{escape(t("status.running" if status.get("runtime", {}).get("running") else "status.stopped", lang))}</dd>
          </dl>
        </section>
      </aside>
    </section>
    """
    script = f"""
    <script>
    window.ATLAS_GETTING_STARTED = {{
      registry: {json.dumps(registry, ensure_ascii=False)},
      strings: {json.dumps(strings, ensure_ascii=False)},
      status: {json.dumps(status, ensure_ascii=False)}
    }};
    {GETTING_STARTED_JS}
    </script>
    """
    return content, script


def _strings(lang: str) -> dict[str, str]:
    keys = [
        "getting.saved",
        "getting.save_failed",
        "getting.testing_provider",
        "getting.provider_test_complete",
        "getting.provider_test_failed",
        "getting.loading_models",
        "getting.models_loaded",
        "getting.models_unavailable",
        "getting.saving_runtime",
        "getting.runtime_saved",
        "getting.starting_runtime",
        "getting.runtime_running",
        "getting.runtime_stopped",
        "getting.runtime_failed",
        "getting.boot.save",
        "getting.boot.start",
        "getting.boot.poll",
        "getting.boot.running",
        "getting.boot.tick",
        "getting.boot.brief",
        "getting.boot.waiting",
        "getting.understood_saved",
        "getting.status.ready",
        "getting.status.ready_degraded",
        "getting.status.needs_configuration",
        "getting.status.blocked",
        "getting.status.optional",
        "getting.status.in_progress",
        "provider.never_checked",
        "empty.signal",
        "empty.context",
    ]
    return {key: t(key, lang) for key in keys}


def _step(step_id: str, title_key: str, status: str, note_key: str) -> dict[str, str]:
    return {"id": step_id, "title_key": title_key, "status": status, "note_key": note_key}


def _config_language(config: Mapping[str, Any]) -> str:
    ui = config.get("ui") if isinstance(config.get("ui"), Mapping) else {}
    lang = str(ui.get("language") or current_language()).lower()
    return lang if lang in {"en", "zh"} else "en"


def _active_provider(providers: list[Any], active: str) -> dict[str, Any]:
    for provider in providers:
        if isinstance(provider, Mapping) and str(provider.get("id")) == active:
            return dict(provider)
    for provider in providers:
        if isinstance(provider, Mapping):
            return dict(provider)
    return {}


def _provider_configured(provider: Mapping[str, Any]) -> bool:
    if not provider:
        return False
    provider_type = str(provider.get("type") or provider.get("id") or "")
    base_url = bool(str(provider.get("base_url") or "").strip())
    has_key = bool(str(provider.get("api_key") or "").strip())
    if provider_type == "ollama":
        return base_url
    if provider_type in {"custom", "morecode"}:
        return base_url
    return base_url and has_key


def _channel_counts(channels: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in channels.values():
        key = str(value or "NOT_CONFIGURED").upper()
        counts[key] = counts.get(key, 0) + 1
    return counts


def _stepper(steps: Any, lang: str) -> str:
    rows = []
    for index, item in enumerate(steps if isinstance(steps, list) else [], start=1):
        if not isinstance(item, Mapping):
            continue
        status = str(item.get("status") or "NEEDS_CONFIGURATION")
        title = t(str(item.get("title_key") or ""), lang)
        rows.append(
            f'<a class="getting-step status-{escape(status.lower())}" href="#{escape(str(item.get("id") or ""))}" data-step-id="{escape(str(item.get("id") or ""))}">'
            f'<span>{index:02d}</span><strong>{escape(title)}</strong><em data-step-status>{escape(_status_label(status, lang))}</em></a>'
        )
    return "\n".join(rows)


def _progress_text(status: Mapping[str, Any], lang: str) -> str:
    overall = status.get("overall_readiness") if isinstance(status.get("overall_readiness"), Mapping) else {}
    return t("getting.progress_value", lang).format(
        completed=overall.get("completed_steps", 0),
        total=overall.get("total_steps", 8),
    )


def _progress_width(status: Mapping[str, Any]) -> int:
    overall = status.get("overall_readiness") if isinstance(status.get("overall_readiness"), Mapping) else {}
    total = max(1, _int(overall.get("total_steps"), 8))
    completed = max(0, min(total, _int(overall.get("completed_steps"), 0)))
    return round(completed / total * 100)


def _quick_title(status: Mapping[str, Any], lang: str) -> str:
    runtime = status.get("runtime") if isinstance(status.get("runtime"), Mapping) else {}
    overall = status.get("overall_readiness") if isinstance(status.get("overall_readiness"), Mapping) else {}
    if runtime.get("running"):
        return t("getting.quick_running", lang)
    if overall.get("can_start"):
        return t("getting.quick_ready", lang)
    return t("getting.quick_blocked", lang).format(count=len(overall.get("blocking_steps") or []))


def _quick_copy(status: Mapping[str, Any], lang: str) -> str:
    overall = status.get("overall_readiness") if isinstance(status.get("overall_readiness"), Mapping) else {}
    if overall.get("can_start"):
        return t("getting.quick_ready_copy", lang)
    return t("getting.quick_blocked_copy", lang)


def _provider_status_text(status: Mapping[str, Any], lang: str) -> str:
    provider = status.get("provider") if isinstance(status.get("provider"), Mapping) else {}
    health = _status_label(str(provider.get("status") or "NEEDS_CONFIGURATION"), lang)
    latency = _latency_text(provider.get("latency_ms"), lang)
    return f"{health} · {latency}"


def _portfolio_status_text(status: Mapping[str, Any], lang: str) -> str:
    portfolio = status.get("portfolio") if isinstance(status.get("portfolio"), Mapping) else {}
    count = portfolio.get("position_count", 0)
    exposure = portfolio.get("exposure_sum_pct")
    return t("getting.portfolio_summary", lang).format(count=count, exposure=exposure if exposure is not None else 0)


def _market_summary(status: Mapping[str, Any], lang: str) -> str:
    market = status.get("market_data") if isinstance(status.get("market_data"), Mapping) else {}
    counts = market.get("channel_counts") if isinstance(market.get("channel_counts"), Mapping) else {}
    if not counts:
        return t("empty.context", lang)
    live = sum(_int(counts.get(key), 0) for key in MARKET_SIGNAL_STATES)
    return t("getting.market_summary", lang).format(live=live, total=sum(_int(value, 0) for value in counts.values()))


def _market_channels(channels: Any, lang: str) -> str:
    if not isinstance(channels, Mapping) or not channels:
        return f'<div class="getting-channel">{escape(t("empty.context", lang))}</div>'
    rows = []
    for key, value in channels.items():
        label = _friendly_status(str(value), lang)
        css = str(value or "not_configured").lower()
        rows.append(
            f'<div class="getting-channel signal-{escape(css)}"><span>{escape(str(key).replace("_", " ").title())}</span><strong>{escape(label)}</strong></div>'
        )
    return "\n".join(rows)


def _friendly_status(value: str, lang: str) -> str:
    normalized = str(value or "").strip().upper()
    keys = {
        "LIVE": "getting.market.live",
        "DELAYED": "getting.market.delayed",
        "CACHED": "getting.market.cached",
        "SIMULATED": "getting.market.simulated",
        "NOT_CONFIGURED": "getting.market.not_configured",
        "RATE_LIMITED": "getting.market.rate_limited",
        "FAILED": "getting.market.failed",
    }
    return t(keys.get(normalized, "empty.context"), lang)


def _provider_options(providers: list[Any], active: str) -> str:
    if not providers:
        return '<option value="openai">OpenAI</option>'
    return "\n".join(
        f'<option value="{escape(str(item.get("id")))}"{_selected(item.get("id"), active)}>{escape(str(item.get("label") or item.get("id")))}</option>'
        for item in providers
        if isinstance(item, Mapping)
    )


def _model_options(provider: Mapping[str, Any]) -> str:
    models = provider.get("available_models") if isinstance(provider.get("available_models"), list) else []
    return "\n".join(f'<option value="{escape(str(model))}"></option>' for model in models if str(model).strip())


def _asset_rows(positions: list[Any], lang: str) -> str:
    rows = positions or [{}, {}]
    return "\n".join(_asset_row(item if isinstance(item, Mapping) else {}, lang) for item in rows)


def _asset_row(item: Mapping[str, Any], lang: str) -> str:
    return f"""
    <div class="getting-asset-row" data-asset-row>
      <label>{escape(t("setup.asset", lang))}<input data-asset-field="asset" value="{escape(str(item.get("asset") or ""))}" placeholder="AAPL"></label>
      <label>{escape(t("setup.market", lang))}<input data-asset-field="market" value="{escape(str(item.get("market") or ""))}" placeholder="US / HK / A-share"></label>
      <label>{escape(t("setup.percentage", lang))}<input data-asset-field="portfolio_percentage" type="number" min="0" max="100" step="0.1" value="{escape(str(item.get("portfolio_percentage") or ""))}" placeholder="12"></label>
      <label>{escape(t("setup.theme", lang))}<input data-asset-field="theme" value="{escape(str(item.get("theme") or ""))}" placeholder="AI"></label>
      <label>{escape(t("setup.role", lang))}<input data-asset-field="role" value="{escape(str(item.get("role") or ""))}" placeholder="Core"></label>
      <label>{escape(t("setup.risk_note", lang))}<input data-asset-field="risk_note" value="{escape(str(item.get("risk_note") or ""))}" placeholder="{escape(t("empty.context", lang))}"></label>
      <label class="wide">{escape(t("setup.thesis", lang))}<textarea data-asset-field="thesis" rows="2">{escape(str(item.get("user_thesis") or item.get("thesis") or ""))}</textarea></label>
      <button class="ghost-button" type="button" data-remove-asset>{escape(t("settings.remove", lang))}</button>
    </div>
    """


def _interval_options(selected: int) -> str:
    return "\n".join(f'<option value="{value}"{_selected(value, selected)}>{value}s</option>' for value in (10, 30, 60, 300))


def _metric(label: str, value: str, note: str) -> str:
    return f'<article class="metric-card"><span>{escape(label)}</span><strong>{escape(value)}</strong><p>{escape(note)}</p></article>'


def _brief_value(status: Mapping[str, Any]) -> str:
    brief = status.get("first_brief") if isinstance(status.get("first_brief"), Mapping) else {}
    return str(brief.get("decision") or brief.get("brief_id") or "Waiting for cognitive signal")


def _latency_text(value: Any, lang: str) -> str:
    if value is None or value == "":
        return t("provider.never_checked", lang)
    return f"{value}ms"


def _status_label(status: str, lang: str) -> str:
    return {
        "READY": t("getting.status.ready", lang),
        "READY_DEGRADED": t("getting.status.ready_degraded", lang),
        "NEEDS_CONFIGURATION": t("getting.status.needs_configuration", lang),
        "BLOCKED": t("getting.status.blocked", lang),
        "OPTIONAL": t("getting.status.optional", lang),
        "IN_PROGRESS": t("getting.status.in_progress", lang),
    }.get(str(status).upper(), t("empty.context", lang))


def _selected(value: Any, selected: Any) -> str:
    return " selected" if str(value) == str(selected) else ""


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


GETTING_STARTED_CSS = """
.getting-shell {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr) 300px;
  gap: 16px;
  align-items: start;
}
.getting-stepper, .getting-summary {
  position: sticky;
  top: 88px;
  display: grid;
  gap: 12px;
}
.getting-progress {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface-muted);
}
.getting-progress strong {
  display: block;
  margin-top: 8px;
  font-size: 1.1rem;
}
.getting-progress-bar {
  height: 7px;
  margin-top: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
}
.getting-progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}
.getting-step-list {
  display: grid;
  gap: 7px;
}
.getting-step {
  min-height: 58px;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 3px 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: var(--surface-muted);
}
.getting-step span {
  grid-row: 1 / span 2;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  color: var(--muted);
  font-size: 0.72rem;
}
.getting-step strong { font-size: 0.88rem; }
.getting-step em {
  color: var(--muted);
  font-size: 0.76rem;
  font-style: normal;
}
.getting-step.status-ready { border-color: rgba(158, 230, 184, 0.28); }
.getting-step.status-ready_degraded { border-color: rgba(246, 215, 122, 0.32); }
.getting-step.status-needs_configuration, .getting-step.status-blocked { border-color: rgba(244, 165, 179, 0.32); }
.getting-main {
  display: grid;
  gap: 16px;
}
.getting-hero { min-height: 420px; }
.getting-quick-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  margin-top: 24px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.045);
}
.getting-quick-card h2, .getting-section h2 { margin: 6px 0 8px; }
.getting-quick-card p, .getting-status { color: var(--subtle); line-height: 1.48; }
.getting-section {
  position: relative;
  scroll-margin-top: 96px;
}
.getting-index {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  margin-bottom: 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
}
.getting-meaning-grid, .getting-channel-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0;
}
.getting-meaning-grid div, .getting-channel, .getting-concept-card {
  min-height: 86px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.035);
}
.getting-concept-card strong { display:block; color:var(--accent); font-size:.82rem; margin-bottom:6px; }
.getting-concept-card span { display:block; color:var(--subtle, #cbd5e1); font-size:.82rem; line-height:1.4; }
.getting-meaning-grid strong, .getting-channel span, .getting-summary-list dt {
  display: block;
  color: var(--muted);
  font-size: 0.78rem;
}
.getting-meaning-grid span, .getting-channel strong {
  display: block;
  margin-top: 8px;
}
.getting-channel.signal-live strong, .getting-channel.signal-delayed strong, .getting-channel.signal-cached strong { color: var(--positive); }
.getting-channel.signal-simulated strong, .getting-channel.signal-not_configured strong, .getting-channel.signal-rate_limited strong { color: var(--warning); }
.getting-channel.signal-failed strong { color: var(--danger); }
.getting-asset-list {
  display: grid;
  gap: 10px;
  margin: 12px 0;
}
.getting-asset-row {
  display: grid;
  grid-template-columns: 1fr 0.8fr 0.7fr 1fr;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.035);
}
.getting-asset-row .wide {
  grid-column: 1 / -2;
}
.getting-asset-row [data-remove-asset] {
  align-self: end;
}
.getting-boot-list {
  margin: 12px 0 0;
  padding-left: 22px;
  color: var(--subtle);
}
.getting-summary-list {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 9px 12px;
  margin: 12px 0 0;
}
.getting-summary-list dd {
  margin: 0;
  text-align: right;
  overflow-wrap: anywhere;
}
@media (max-width: 1180px) {
  .getting-shell { grid-template-columns: 220px minmax(0, 1fr); }
  .getting-summary { position: static; grid-column: 2; }
}
@media (max-width: 860px) {
  .getting-shell { grid-template-columns: 1fr; }
  .getting-stepper, .getting-summary { position: static; }
  .getting-quick-card, .getting-meaning-grid, .getting-channel-grid, .getting-asset-row { grid-template-columns: 1fr; }
  .getting-summary { grid-column: auto; }
  .getting-asset-row .wide { grid-column: auto; }
}
"""


GETTING_STARTED_JS = """
(function () {
  const boot = document.getElementById("getting-boot-list");
  const state = window.ATLAS_GETTING_STARTED || {};
  const strings = state.strings || {};
  let registry = JSON.parse(JSON.stringify(state.registry || { providers: [], fallback_chain: [] }));

  function tx(key) { return strings[key] || key; }
  function statusLabel(value) {
    const key = "getting.status." + String(value || "").toLowerCase();
    return tx(key);
  }
  function provider() {
    const id = document.getElementById("getting-provider-select").value;
    return (registry.providers || []).find(item => item.id === id) || {};
  }
  function cloneRegistry() {
    const copy = JSON.parse(JSON.stringify(registry || { providers: [], fallback_chain: [] }));
    const id = document.getElementById("getting-provider-select").value;
    copy.active_provider = id;
    copy.fallback_chain = Array.from(new Set([id].concat(copy.fallback_chain || []))).filter(Boolean);
    let item = (copy.providers || []).find(provider => provider.id === id);
    if (!item) {
      item = { id, type: id, label: id, enabled: true };
      copy.providers = (copy.providers || []).concat([item]);
    }
    item.model = document.getElementById("getting-model").value.trim();
    item.base_url = document.getElementById("getting-base-url").value.trim();
    const key = document.getElementById("getting-api-key").value.trim();
    if (key) item.api_key = key;
    return copy;
  }
  function assets() {
    return Array.from(document.querySelectorAll("#getting-asset-rows [data-asset-row]")).map(row => {
      const item = {};
      row.querySelectorAll("[data-asset-field]").forEach(field => item[field.dataset.assetField] = field.value.trim());
      item.portfolio_percentage = Number(item.portfolio_percentage || 0);
      return item;
    }).filter(item => item.asset);
  }
  function payload() {
    const rows = assets();
    return {
      ui: { language: document.documentElement.lang || "en" },
      llm_registry: cloneRegistry(),
      system: {
        tick_interval: Number(document.getElementById("getting-interval").value || 60),
        runtime_mode: document.getElementById("getting-runtime-mode").value,
        trust_threshold: 0.45,
        hypothesis_switching_sensitivity: 0.08
      },
      assets: {
        portfolio_json: JSON.stringify({ positions: rows }),
        asset_list: rows.map(item => item.asset),
        weights: Object.fromEntries(rows.map(item => [item.asset, item.portfolio_percentage]))
      },
      metadata: { ui_only: true, no_runtime_reload: true, no_trading_execution: true }
    };
  }
  async function saveAll() {
    const response = await fetch("/settings", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload())
    });
    const data = await response.json();
    if (data.status !== "saved") throw new Error("save_failed");
    registry = data.config && data.config.llm_registry ? data.config.llm_registry : cloneRegistry();
    await fetch("/control/set_interval", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ interval_seconds: Number(document.getElementById("getting-interval").value || 60) })
    });
    return data;
  }
  function addBoot(text) {
    const li = document.createElement("li");
    li.textContent = text;
    boot.appendChild(li);
  }
  function setStatus(id, text) {
    const node = document.getElementById(id);
    if (node) node.textContent = text;
  }
  function applyProviderFields() {
    const item = provider();
    document.getElementById("getting-model").value = item.model || "";
    document.getElementById("getting-base-url").value = item.base_url || "";
    const datalist = document.getElementById("getting-model-options");
    datalist.innerHTML = "";
    (item.available_models || []).forEach(model => {
      const option = document.createElement("option");
      option.value = model;
      datalist.appendChild(option);
    });
  }
  function assetTemplate() {
    const row = document.querySelector("#getting-asset-rows [data-asset-row]");
    return row.outerHTML
      .replace(/value="[^"]*"/g, 'value=""')
      .replace(/>[^<]*<\\/textarea>/g, '></textarea>');
  }
  async function refreshStatus() {
    const response = await fetch("/getting-started/status", { cache: "no-store" });
    const data = await response.json();
    state.status = data;
    const overall = data.overall_readiness || {};
    let completed = Number(overall.completed_steps || 0);
    if (localStorage.getItem("atlasGettingStartedUnderstood") === "yes") completed = Math.max(completed, 1);
    const total = Number(overall.total_steps || 8);
    document.getElementById("getting-progress-count").textContent = document.documentElement.lang === "zh"
      ? `${completed} / ${total} 步已完成`
      : `${completed} of ${total} steps completed`;
    document.getElementById("getting-progress-bar").style.width = Math.round(completed / total * 100) + "%";
    setStatus("summary-provider", data.provider?.label || tx("empty.context"));
    setStatus("summary-latency", data.provider?.latency_ms == null ? tx("provider.never_checked") : data.provider.latency_ms + "ms");
    setStatus("summary-portfolio", String(data.portfolio?.position_count || 0));
    setStatus("summary-runtime", data.runtime?.running ? tx("getting.runtime_running") : tx("getting.runtime_stopped"));
    setStatus("getting-provider-status", statusLabel(data.provider?.status) + (data.provider?.health ? " · " + data.provider.health.replace(/_/g, " ") : ""));
    setStatus("getting-portfolio-status", document.documentElement.lang === "zh"
      ? `${data.portfolio?.position_count || 0} 个资产 · 暴露 ${data.portfolio?.exposure_sum_pct || 0}%`
      : `${data.portfolio?.position_count || 0} assets · ${data.portfolio?.exposure_sum_pct || 0}% exposure`);
    return data;
  }
  async function pollRuntime() {
    for (let index = 0; index < 14; index += 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const data = await refreshStatus();
      if (data.runtime && data.runtime.running) addBoot(tx("getting.boot.running"));
      if (data.runtime && data.runtime.tick_counter > 0) addBoot(tx("getting.boot.tick"));
      if (data.first_brief && data.first_brief.status === "READY") {
        addBoot(tx("getting.boot.brief"));
        return data;
      }
    }
    return state.status;
  }

  document.getElementById("getting-provider-select").addEventListener("change", applyProviderFields);
  document.getElementById("getting-save-provider").addEventListener("click", async () => {
    setStatus("getting-provider-status", tx("getting.saved"));
    try { await saveAll(); await refreshStatus(); } catch (error) { setStatus("getting-provider-status", tx("getting.save_failed")); }
  });
  document.getElementById("getting-test-provider").addEventListener("click", async () => {
    setStatus("getting-provider-status", tx("getting.testing_provider"));
    try {
      await saveAll();
      const id = document.getElementById("getting-provider-select").value;
      const response = await fetch("/llm/provider/test", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ provider_id: id })
      });
      const data = await response.json();
      setStatus("getting-provider-status", tx("getting.provider_test_complete") + " · " + (data.status || ""));
      await refreshStatus();
    } catch (error) {
      setStatus("getting-provider-status", tx("getting.provider_test_failed"));
    }
  });
  document.getElementById("getting-discover-models").addEventListener("click", async () => {
    setStatus("getting-provider-status", tx("getting.loading_models"));
    try {
      await saveAll();
      const id = document.getElementById("getting-provider-select").value;
      const response = await fetch("/llm/provider/models", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ provider_id: id })
      });
      const data = await response.json();
      const datalist = document.getElementById("getting-model-options");
      datalist.innerHTML = "";
      (data.models || []).forEach(model => {
        const option = document.createElement("option");
        option.value = model;
        datalist.appendChild(option);
      });
      setStatus("getting-provider-status", data.status === "ok" ? tx("getting.models_loaded") + " · " + (data.models || []).length : tx("getting.models_unavailable"));
      await refreshStatus();
    } catch (error) {
      setStatus("getting-provider-status", tx("getting.models_unavailable"));
    }
  });
  document.getElementById("getting-add-asset").addEventListener("click", () => {
    document.getElementById("getting-asset-rows").insertAdjacentHTML("beforeend", assetTemplate());
  });
  document.addEventListener("click", event => {
    if (event.target && event.target.matches("[data-remove-asset]")) {
      const rows = document.querySelectorAll("#getting-asset-rows [data-asset-row]");
      if (rows.length > 1) event.target.closest("[data-asset-row]").remove();
    }
  });
  document.getElementById("getting-save-portfolio").addEventListener("click", async () => {
    try { await saveAll(); await refreshStatus(); } catch (error) { setStatus("getting-portfolio-status", tx("getting.save_failed")); }
  });
  document.getElementById("getting-save-runtime").addEventListener("click", async () => {
    addBoot(tx("getting.saving_runtime"));
    try { await saveAll(); addBoot(tx("getting.runtime_saved")); await refreshStatus(); } catch (error) { addBoot(tx("getting.runtime_failed")); }
  });
  async function startRuntime() {
    boot.innerHTML = "";
    addBoot(tx("getting.boot.save"));
    try {
      await saveAll();
      addBoot(tx("getting.boot.start"));
      const response = await fetch("/control/start", { method: "POST" });
      const data = await response.json();
      addBoot(data.status || tx("getting.starting_runtime"));
      addBoot(tx("getting.boot.poll"));
      await pollRuntime();
    } catch (error) {
      addBoot(tx("getting.runtime_failed"));
    }
  }
  document.getElementById("getting-start-runtime").addEventListener("click", startRuntime);
  document.getElementById("getting-quick-start").addEventListener("click", startRuntime);
  document.getElementById("getting-stop-runtime").addEventListener("click", async () => {
    try {
      const response = await fetch("/control/stop", { method: "POST" });
      const data = await response.json();
      addBoot(data.status || tx("getting.runtime_stopped"));
      await refreshStatus();
    } catch (error) {
      addBoot(tx("getting.runtime_failed"));
    }
  });
  document.getElementById("refresh-market-readiness").addEventListener("click", refreshStatus);
  document.querySelectorAll("[data-language-choice]").forEach(button => {
    button.addEventListener("click", async () => {
      await fetch("/ui/language", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ language: button.dataset.languageChoice })
      });
      window.location.reload();
    });
  });
  document.getElementById("mark-understood").addEventListener("click", () => {
    localStorage.setItem("atlasGettingStartedUnderstood", "yes");
    document.getElementById("mark-understood").textContent = tx("getting.understood_saved");
    refreshStatus();
  });
  if (localStorage.getItem("atlasGettingStartedUnderstood") === "yes") {
    document.getElementById("mark-understood").textContent = tx("getting.understood_saved");
  }
  refreshStatus();
})();
"""
