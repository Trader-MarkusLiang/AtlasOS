"""Global Atlas OS top bar."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.components.language_toggle import render_language_toggle
from ui.components.runtime_status_indicator import render_runtime_status_indicator
from ui.i18n.i18n import t


PAGE_TITLES = {
    "home": "page.home",
    "getting_started": "page.getting_started",
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
    "system_status": "page.system_status",
}


def render_global_topbar(active: str, state: Mapping[str, Any], lang: str) -> str:
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    provider_registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    provider = str(provider_registry.get("active_provider") or t("empty.context", lang))
    llm_summary = state.get("llm_trace_summary") if isinstance(state.get("llm_trace_summary"), Mapping) else {}
    inference = _inference_label(str(llm_summary.get("latest_inference_status") or "not_run"), lang)
    freshness = _freshness_label(market, lang)
    last_tick = _compact_value(state.get("tick_counter"), t("empty.signal", lang))
    tick_pill = "" if active == "home" else f'<span class="mini-pill">{escape(t("state.tick", lang))}: <strong data-tick-counter>{escape(last_tick)}</strong></span>'
    return f"""
    <header class="global-topbar">
      <div class="page-title-block">
        <strong>{escape(t(PAGE_TITLES.get(active, "app.title"), lang))}</strong>
        <span>{escape(t("app.guidance", lang))}</span>
      </div>
      <div class="topbar-controls">
        {render_runtime_status_indicator(state, lang)}
        <span class="mini-pill">{escape(t("model.active_provider", lang))}: <strong data-provider-name>{escape(provider)}</strong> · <em data-inference-status>{escape(inference)}</em></span>
        <span class="mini-pill">{escape(t("status.freshness", lang))}: <strong data-freshness>{escape(freshness)}</strong></span>
        {tick_pill}
        <a class="mini-pill topbar-link" href="/settings">{escape(t("nav.settings", lang))}</a>
        {render_language_toggle(lang)}
      </div>
    </header>
    """


def _freshness_label(market: Mapping[str, Any], lang: str) -> str:
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    if channels:
        live = sum(1 for value in channels.values() if str(value).upper() == "LIVE")
        failed = sum(1 for value in channels.values() if str(value).upper() in {"FAILED", "RATE_LIMITED"})
        missing = sum(1 for value in channels.values() if str(value).upper() == "NOT_CONFIGURED")
        available_assets = sum(1 for item in observations if isinstance(item, Mapping) and item.get("data_quality_status") in {"Available", "Partial"})
        partial_assets = sum(1 for item in observations if isinstance(item, Mapping) and item.get("data_quality_status") == "Partial")
        total_assets = len([item for item in observations if isinstance(item, Mapping)])
        if lang == "zh":
            prefix = f"价格 {available_assets}/{total_assets}" if total_assets else f"{live} 实时"
            suffix = "可用"
            if partial_assets:
                suffix = f"{partial_assets} 部分"
            if failed:
                suffix = f"{failed} 失败"
            elif missing:
                suffix = f"{missing} 未配置"
            return f"{prefix} · {suffix}"
        prefix = f"price {available_assets}/{total_assets}" if total_assets else f"{live} live"
        suffix = "available"
        if partial_assets:
            suffix = f"{partial_assets} partial"
        if failed:
            suffix = f"{failed} failed"
        elif missing:
            suffix = f"{missing} not configured"
        return f"{prefix} · {suffix}"
    status = str(market.get("status") or "")
    if status == "not_run":
        return t("empty.initializing", lang)
    return t("empty.context", lang)


def _compact_value(value: Any, fallback: str) -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _inference_label(status: str, lang: str) -> str:
    labels = {
        "succeeded": {"zh": "最近推理成功", "en": "latest inference succeeded"},
        "failed": {"zh": "最近推理失败", "en": "latest inference failed"},
        "not_run": {"zh": "尚未推理", "en": "inference not run"},
    }
    return labels.get(status, labels["not_run"])[lang]
