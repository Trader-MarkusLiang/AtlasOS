"""Top bar component for the Atlas OS system interface."""

from __future__ import annotations

from ui.i18n.i18n import current_language, t


def render_top_bar() -> str:
    lang = current_language()
    en_selected = " selected" if lang == "en" else ""
    zh_selected = " selected" if lang == "zh" else ""
    language_label = t("nav.language")
    return f"""
    <header class="top-bar" data-component="top-bar">
      <div class="brand-block">
        <div class="brand-mark">ATLAS</div>
        <div>
          <div class="brand-title">{t("app.title")}</div>
          <div class="brand-subtitle">{t("app.subtitle")}</div>
        </div>
      </div>
      <div class="runtime-controls" aria-label="Runtime controls">
        <nav class="nav-tabs" aria-label="Atlas UI tabs">
          <a class="nav-tab" href="/dashboard">{t("nav.dashboard")}</a>
          <a class="nav-tab" href="/workflow">{t("nav.workflow")}</a>
          <a class="nav-tab" href="/roadmap">{t("nav.roadmap")}</a>
          <a class="nav-tab" href="/settings">{t("nav.settings")}</a>
        </nav>
        <label class="language-switcher" title="{language_label}">
          <span>{language_label}</span>
          <select id="language-select">
            <option value="en"{en_selected}>EN</option>
            <option value="zh"{zh_selected}>中文</option>
          </select>
        </label>
        <span id="runtime-status-pill" class="status-pill status-unknown">INITIALIZING</span>
      </div>
    </header>
    """
