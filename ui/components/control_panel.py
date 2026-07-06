"""Left control and configuration panel for Atlas OS UI v2.0."""

from __future__ import annotations


def render_control_panel() -> str:
    """Render UI-only controls without importing or mutating cognition."""

    return """
    <aside class="v2-control-panel" data-component="control-panel">
      <div class="v2-brand">
        <div class="v2-brand-mark">A</div>
        <div>
          <strong>Atlas OS</strong>
          <span>Cognitive Control Center</span>
        </div>
      </div>

      <section class="v2-control-section">
        <div class="v2-section-title">System Control</div>
        <div class="v2-button-row">
          <button id="runtime-start" class="v2-primary-button" type="button">Start</button>
          <button id="runtime-stop" class="v2-secondary-button" type="button">Stop</button>
        </div>
        <label class="v2-field">
          <span>Tick interval</span>
          <select id="tick-interval" name="tick_interval">
            <option value="10">10 seconds</option>
            <option value="30">30 seconds</option>
            <option value="60" selected>60 seconds</option>
            <option value="300">5 minutes</option>
          </select>
        </label>
        <label class="v2-toggle">
          <input id="simulation-mode" type="checkbox" checked>
          <span>Simulation mode</span>
        </label>
      </section>

      <section class="v2-control-section">
        <div class="v2-section-title">Model Config</div>
        <label class="v2-field">
          <span>LLM provider</span>
          <select id="llm-provider" name="provider">
            <option>OpenAI</option>
            <option>Claude</option>
            <option>Ollama</option>
            <option>Custom API</option>
          </select>
        </label>
        <label class="v2-field">
          <span>API key</span>
          <input id="llm-api-key" name="api_key" type="password" placeholder="Stored from Settings">
        </label>
        <label class="v2-field">
          <span>Base URL</span>
          <input id="llm-base-url" name="base_url" placeholder="https://api.example.com">
        </label>
        <label class="v2-field">
          <span>Model</span>
          <input id="llm-model-input" name="model" placeholder="gpt-5.5">
        </label>
        <a class="v2-panel-link" href="/settings#llm-config">Open full model settings</a>
      </section>

      <section class="v2-control-section">
        <div class="v2-section-title">Asset Config</div>
        <label class="v2-field">
          <span>Portfolio / assets JSON</span>
          <textarea id="asset-json-editor" name="portfolio_json" rows="5" spellcheck="false">{}</textarea>
        </label>
        <div class="v2-button-row">
          <a class="v2-secondary-button as-link" href="/settings#asset-config">Load</a>
          <a class="v2-primary-button as-link" href="/settings#asset-config">Save Config</a>
        </div>
      </section>
    </aside>
    """
