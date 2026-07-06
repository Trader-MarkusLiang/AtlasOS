"""Left control and configuration panel for Atlas OS UI v2.0."""

from __future__ import annotations

from ui.i18n.i18n import t


def render_control_panel(provider_summary: dict | None = None) -> str:
    """Render UI-only controls without importing or mutating cognition."""

    summary = provider_summary or {}
    active = summary.get("active_provider", "openai")
    provider = next((item for item in summary.get("providers", []) if item.get("id") == active), {})
    provider_label = provider.get("label") or active
    provider_model = provider.get("model") or "gpt-5.5"
    provider_health = provider.get("health") or "unknown"
    return f"""
    <aside class="v2-control-panel" data-component="control-panel">
      <div class="v2-brand">
        <div class="v2-brand-mark">A</div>
        <div>
          <strong>Atlas OS</strong>
          <span>{t("app.title")}</span>
        </div>
      </div>

      <section class="v2-control-section">
        <div class="v2-section-title">{t("system.control")}</div>
        <div class="v2-button-row">
          <button id="runtime-start" class="v2-primary-button" type="button">{t("system.start")}</button>
          <button id="runtime-stop" class="v2-secondary-button" type="button">{t("system.stop")}</button>
        </div>
        <label class="v2-field">
          <span>{t("system.tick_interval")}</span>
          <select id="tick-interval" name="tick_interval">
            <option value="10">10 seconds</option>
            <option value="30">30 seconds</option>
            <option value="60" selected>60 seconds</option>
            <option value="300">5 minutes</option>
          </select>
        </label>
        <label class="v2-toggle">
          <input id="simulation-mode" type="checkbox" checked>
          <span>{t("system.simulation_mode")}</span>
        </label>
      </section>

      <section class="v2-control-section">
        <div class="v2-section-title">{t("model.config")}</div>
        <div class="v2-provider-mini">
          <span>{t("model.active_provider")}</span>
          <strong id="active-provider-label">{provider_label}</strong>
        </div>
        <div class="v2-provider-mini">
          <span>{t("model.model")}</span>
          <strong id="active-provider-model">{provider_model}</strong>
        </div>
        <div class="v2-provider-mini">
          <span>{t("model.health")}</span>
          <strong id="active-provider-health">{provider_health}</strong>
        </div>
        <a class="v2-panel-link" href="/settings#llm-config">{t("model.open_settings")}</a>
      </section>

      <section class="v2-control-section">
        <div class="v2-section-title">{t("asset.config")}</div>
        <label class="v2-field">
          <span>{t("asset.editor")}</span>
          <textarea id="asset-json-editor" name="portfolio_json" rows="5" spellcheck="false">{{}}</textarea>
        </label>
        <div class="v2-button-row">
          <a class="v2-secondary-button as-link" href="/settings#asset-config">{t("asset.load")}</a>
          <a class="v2-primary-button as-link" href="/settings#asset-config">{t("asset.save")}</a>
        </div>
      </section>
    </aside>
    """
