"""Global Atlas OS sidebar."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import t


PRIMARY_NAV = [
    ("home", "/", "nav.home"),
    ("getting_started", "/getting-started", "nav.getting_started"),
    ("ask", "/dashboard", "nav.ask"),
    ("portfolio", "/portfolio", "nav.portfolio"),
    ("markets", "/markets", "nav.markets"),
    ("predictions", "/predictions", "nav.predictions"),
    ("learning", "/learning", "nav.learning"),
    ("workflow", "/workflow", "nav.workflow"),
    ("roadmap", "/roadmap", "nav.roadmap"),
]

SECONDARY_NAV = [
    ("dev_registry", "/dev-registry", "nav.dev_registry"),
    ("settings", "/settings", "nav.settings"),
    ("setup", "/setup", "nav.setup"),
    ("system_guide", "/system-guide", "nav.system_guide"),
    ("system_status", "/control", "nav.system_status"),
]


def render_global_sidebar(active: str, state: Mapping[str, Any], lang: str) -> str:
    provider_registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    active_provider = str(provider_registry.get("active_provider") or t("empty.context", lang))
    trust = state.get("trust_index")
    trust_text = f"{float(trust):.2f}" if isinstance(trust, (int, float)) else t("empty.signal", lang)
    return f"""
    <aside class="atlas-sidebar" aria-label="{escape(t("nav.primary", lang))}">
      <a class="atlas-brand" href="/">
        <span class="atlas-brand-mark">A</span>
        <span><strong>Atlas OS</strong><span>{escape(t("app.subtitle", lang))}</span></span>
      </a>
      <div class="sidebar-section">{escape(t("nav.primary", lang))}</div>
      <nav class="sidebar-nav">
        {_nav_links(PRIMARY_NAV, active, lang)}
      </nav>
      <div class="sidebar-section">{escape(t("nav.secondary", lang))}</div>
      <nav class="sidebar-nav">
        {_nav_links(SECONDARY_NAV, active, lang)}
      </nav>
      <div class="sidebar-status-card">
        <span>{escape(t("model.active_provider", lang))}</span>
        <strong data-provider-name>{escape(active_provider)}</strong>
      </div>
      <div class="sidebar-status-card">
        <span>{escape(t("state.trust_score", lang))}</span>
        <strong data-trust-index>{escape(trust_text)}</strong>
      </div>
    </aside>
    """


def _nav_links(items: list[tuple[str, str, str]], active: str, lang: str) -> str:
    return "\n".join(
        f'<a class="sidebar-link{" active" if key == active else ""}" href="{escape(href)}">'
        f'<span>{escape(t(label, lang))}</span><i class="sidebar-dot"></i></a>'
        for key, href, label in items
    )
