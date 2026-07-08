"""Global Atlas OS top bar."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.components.language_toggle import render_language_toggle
from ui.components.runtime_status_indicator import render_runtime_status_indicator
from ui.i18n.i18n import t


PAGE_TITLES = {
    "home": "page.home",
    "ask": "page.ask",
    "portfolio": "page.portfolio",
    "markets": "page.markets",
    "predictions": "page.predictions",
    "learning": "page.learning",
    "workflow": "page.workflow",
    "roadmap": "page.roadmap",
    "dev_registry": "page.dev_registry",
    "settings": "page.settings",
    "setup": "page.setup",
    "system_guide": "page.system_guide",
}


def render_global_topbar(active: str, state: Mapping[str, Any], lang: str) -> str:
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    provider_registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    provider = str(provider_registry.get("active_provider") or t("empty.context", lang))
    freshness = _freshness_label(market, lang)
    last_tick = _compact_value(state.get("tick_counter"), t("empty.signal", lang))
    return f"""
    <header class="global-topbar">
      <div class="page-title-block">
        <strong>{escape(t(PAGE_TITLES.get(active, "app.title"), lang))}</strong>
        <span>{escape(t("app.guidance", lang))}</span>
      </div>
      <div class="topbar-controls">
        {render_runtime_status_indicator(state, lang)}
        <span class="mini-pill">{escape(t("model.active_provider", lang))}: <strong data-provider-name>{escape(provider)}</strong></span>
        <span class="mini-pill">{escape(t("status.freshness", lang))}: <strong data-freshness>{escape(freshness)}</strong></span>
        <span class="mini-pill">{escape(t("state.tick", lang))}: <strong data-tick-counter>{escape(last_tick)}</strong></span>
        {render_language_toggle(lang)}
      </div>
    </header>
    """


def _freshness_label(market: Mapping[str, Any], lang: str) -> str:
    if market.get("timestamp"):
        return str(market.get("timestamp"))
    status = str(market.get("status") or "")
    if status == "not_run":
        return t("empty.initializing", lang)
    return t("empty.context", lang)


def _compact_value(value: Any, fallback: str) -> str:
    if value is None or value == "":
        return fallback
    return str(value)
