"""Language toggle component."""

from __future__ import annotations

from html import escape

from ui.i18n.i18n import t


def render_language_toggle(lang: str) -> str:
    return f"""
    <label class="language-toggle">
      <span>{escape(t("nav.language", lang))}</span>
      <select id="global-language-select" aria-label="{escape(t("nav.language", lang))}">
        <option value="en"{' selected' if lang == 'en' else ''}>EN</option>
        <option value="zh"{' selected' if lang == 'zh' else ''}>中文</option>
      </select>
    </label>
    """
