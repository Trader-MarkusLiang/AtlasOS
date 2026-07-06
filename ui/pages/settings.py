"""Settings page and local config storage for Atlas OS UI."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any, Mapping

from runtime.llm.provider_registry import (
    default_provider_registry,
    safe_registry_view,
    update_provider_registry,
)
from ui.i18n.i18n import current_language, set_language, t, translation_payload


DEFAULT_CONFIG_PATH = Path("runtime/config/user_config.json")


DEFAULT_CONFIG: dict[str, Any] = {
    "llm": {
        "provider": "OpenAI",
        "api_key": "",
        "base_url": "",
        "model": "gpt-5.5",
    },
    "llm_registry": default_provider_registry(),
    "ui": {"language": "en"},
    "system": {
        "tick_interval": 60,
        "runtime_mode": "simulation",
        "trust_threshold": 0.45,
        "hypothesis_switching_sensitivity": 0.08,
    },
    "assets": {
        "portfolio_json": "{}",
        "asset_list": [],
        "weights": {},
    },
    "metadata": {
        "ui_only": True,
        "no_runtime_reload": True,
        "no_trading_execution": True,
    },
}


def load_user_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_CONFIG))
    return _merge_defaults(data if isinstance(data, dict) else {})


def save_user_config(payload: Mapping[str, Any], path: str | None = None) -> dict[str, Any]:
    """Save UI-only config to local JSON."""

    target = Path(path) if path else DEFAULT_CONFIG_PATH
    config = _config_from_payload(payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = load_user_config(str(target))
    existing.update(config)
    target.write_text(json.dumps(existing, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_provider_registry(existing.get("llm_registry", {}), str(target))
    if config.get("ui", {}).get("language"):
        set_language(str(config["ui"]["language"]), str(target))
    return {"status": "saved", "config": _masked_config(load_user_config(str(target))), "path": str(target)}


def render_settings_page(config: Mapping[str, Any] | None = None) -> str:
    data = _merge_defaults(dict(config or load_user_config()))
    registry = safe_registry_view(data.get("llm_registry", default_provider_registry()))
    system = data["system"]
    assets = data["assets"]
    lang = current_language()
    strings = translation_payload(lang)
    provider_cards = "\n".join(_provider_card(provider, registry["active_provider"]) for provider in registry["providers"])
    return f"""<!doctype html>
<html lang="{escape(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(t("settings.title", lang))}</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #0b0f14;
  --panel: rgba(18, 24, 32, 0.74);
  --panel-soft: rgba(255, 255, 255, 0.05);
  --line: rgba(255, 255, 255, 0.08);
  --text: #f4f7fb;
  --muted: #8c97a6;
  --accent: #f4f7fb;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-width: 360px;
  background:
    radial-gradient(circle at 24% 0%, rgba(148, 163, 184, 0.11), transparent 32%),
    linear-gradient(180deg, rgba(255,255,255,0.04), transparent 24%),
    var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
a {{ color: inherit; text-decoration: none; }}
.settings-shell {{
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
}}
.settings-sidebar {{
  padding: 24px;
  border-right: 1px solid var(--line);
  background: rgba(11, 15, 20, 0.78);
  backdrop-filter: blur(24px);
}}
.settings-sidebar h1 {{ margin: 0 0 8px; font-size: 1.15rem; }}
.settings-sidebar p {{ margin: 0 0 22px; color: var(--muted); line-height: 1.45; }}
.settings-link {{
  display: flex;
  min-height: 42px;
  align-items: center;
  padding: 9px 12px;
  margin-bottom: 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel-soft);
}}
.settings-main {{ padding: 28px; }}
.settings-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}}
.settings-header h2 {{ margin: 0; font-size: 1.8rem; letter-spacing: 0; }}
.settings-header p {{ margin: 6px 0 0; color: var(--muted); }}
.settings-actions {{ display: flex; align-items: center; gap: 10px; }}
.settings-grid {{
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
  gap: 16px;
}}
.settings-card {{
  border: 1px solid var(--line);
  border-radius: 22px;
  background: var(--panel);
  backdrop-filter: blur(20px);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
  overflow: hidden;
}}
.settings-card-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--line);
}}
.settings-card-header h3 {{ margin: 0; font-size: 1rem; }}
.settings-card-body {{ padding: 16px 18px 18px; }}
.provider-list {{ display: grid; gap: 10px; }}
.provider-card {{
  display: grid;
  grid-template-columns: 1.1fr 0.9fr 0.9fr auto;
  gap: 10px;
  align-items: end;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
}}
label {{ display: block; color: var(--muted); font-size: 0.8rem; }}
input, select, textarea {{
  width: 100%;
  margin-top: 6px;
  min-height: 40px;
  padding: 9px 11px;
  border: 1px solid var(--line);
  border-radius: 13px;
  background: rgba(9, 13, 19, 0.86);
  color: var(--text);
  outline: none;
}}
textarea {{
  min-height: 128px;
  resize: vertical;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.84rem;
}}
.compact-row {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
.wide-row {{ display: grid; gap: 12px; }}
button {{
  min-height: 40px;
  padding: 9px 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.07);
  color: var(--text);
  cursor: pointer;
}}
button.primary {{ background: var(--text); color: var(--bg); }}
button.danger {{ color: #fecdd3; }}
.provider-status {{
  color: var(--muted);
  font-size: 0.78rem;
}}
.notice {{
  margin-top: 14px;
  color: var(--muted);
  line-height: 1.45;
}}
@media (max-width: 1100px) {{
  .settings-shell {{ grid-template-columns: 1fr; }}
  .settings-sidebar {{ border-right: 0; border-bottom: 1px solid var(--line); }}
  .settings-grid {{ grid-template-columns: 1fr; }}
  .provider-card {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="settings-shell">
  <aside class="settings-sidebar">
    <h1>Atlas OS</h1>
    <p>{escape(t("settings.subtitle", lang))}</p>
    <a class="settings-link" href="/dashboard">{escape(t("nav.dashboard", lang))}</a>
    <a class="settings-link" href="/workflow">{escape(t("nav.workflow", lang))}</a>
    <a class="settings-link" href="/roadmap">{escape(t("nav.roadmap", lang))}</a>
  </aside>
  <main class="settings-main">
    <div class="settings-header">
      <div>
        <h2>{escape(t("settings.title", lang))}</h2>
        <p>{escape(t("settings.notice", lang))}</p>
      </div>
      <div class="settings-actions">
        <label>{escape(t("nav.language", lang))}
          <select id="settings-language">
            <option value="en"{_selected(lang, "en")}>EN</option>
            <option value="zh"{_selected(lang, "zh")}>中文</option>
          </select>
        </label>
        <button id="save-settings" class="primary" type="button">{escape(t("settings.save", lang))}</button>
      </div>
    </div>

    <div class="settings-grid">
      <section id="llm-config" class="settings-card">
        <div class="settings-card-header">
          <h3>{escape(t("settings.providers", lang))}</h3>
          <button id="add-provider" type="button">{escape(t("settings.add_provider", lang))}</button>
        </div>
        <div class="settings-card-body">
          <label>{escape(t("model.active_provider", lang))}
            <select id="active-provider">{_provider_options(registry["providers"], registry["active_provider"])}</select>
          </label>
          <div id="provider-list" class="provider-list">{provider_cards}</div>
          <label>{escape(t("settings.fallback", lang))}
            <input id="fallback-chain" value="{escape(", ".join(registry["fallback_chain"]))}">
          </label>
          <p class="notice">API keys are stored locally in encrypted form inside ignored runtime config.</p>
        </div>
      </section>

      <div class="wide-row">
        <section id="system-config" class="settings-card">
          <div class="settings-card-header"><h3>{escape(t("settings.system", lang))}</h3></div>
          <div class="settings-card-body compact-row">
            <label>{escape(t("system.tick_interval", lang))}
              <input id="tick-interval-setting" type="number" min="10" step="1" value="{escape(str(system.get("tick_interval", 60)))}">
            </label>
            <label>Runtime mode
              <select id="runtime-mode-setting">
                <option value="simulation"{_selected(system.get("runtime_mode"), "simulation")}>simulation</option>
                <option value="live"{_selected(system.get("runtime_mode"), "live")}>live</option>
              </select>
            </label>
            <label>Trust threshold
              <input id="trust-threshold-setting" type="number" min="0" max="1" step="0.01" value="{escape(str(system.get("trust_threshold", 0.45)))}">
            </label>
            <label>Hypothesis sensitivity
              <input id="hypothesis-sensitivity-setting" type="number" min="0" max="1" step="0.01" value="{escape(str(system.get("hypothesis_switching_sensitivity", 0.08)))}">
            </label>
          </div>
        </section>

        <section id="asset-config" class="settings-card">
          <div class="settings-card-header"><h3>{escape(t("settings.assets", lang))}</h3></div>
          <div class="settings-card-body wide-row">
            <label>Portfolio JSON
              <textarea id="portfolio-json">{escape(str(assets.get("portfolio_json", "{}")))}</textarea>
            </label>
            <label>Asset list
              <textarea id="asset-list" placeholder="AAPL&#10;MSFT">{escape(_asset_list_text(assets.get("asset_list")))}</textarea>
            </label>
            <label>Weights JSON
              <textarea id="weights-json">{escape(json.dumps(assets.get("weights", {}), ensure_ascii=False, indent=2))}</textarea>
            </label>
          </div>
        </section>
      </div>
    </div>
    <p id="settings-result" class="notice" role="status"></p>
  </main>
</div>
<script>
const I18N = {json.dumps(strings, ensure_ascii=False)};
const providerTypes = {json.dumps(registry["supported_provider_types"], ensure_ascii=False)};

function providerTemplate(id, type, label, baseUrl, model) {{
  return `
    <div class="provider-card" data-provider-card>
      <label>ID<input data-provider-field="id" value="${{escapeHtml(id)}}" readonly></label>
      <label>Type
        <select data-provider-field="type">
          ${{Object.keys(providerTypes).map(key => `<option value="${{key}}" ${{key === type ? "selected" : ""}}>${{providerTypes[key].label}}</option>`).join("")}}
        </select>
      </label>
      <label>{escape(t("model.model", lang))}<input data-provider-field="model" value="${{escapeHtml(model || "")}}"></label>
      <div>
        <label>{escape(t("settings.api_key", lang))}<input data-provider-field="api_key" type="password" placeholder="••••••"></label>
        <span class="provider-status" data-provider-status>${{escapeHtml(label || id)}}</span>
      </div>
      <label style="grid-column: 1 / -2;">{escape(t("settings.base_url", lang))}<input data-provider-field="base_url" value="${{escapeHtml(baseUrl || "")}}"></label>
      <div>
        <button type="button" data-test-provider>{escape(t("settings.test", lang))}</button>
        <button class="danger" type="button" data-remove-provider>{escape(t("settings.remove", lang))}</button>
      </div>
    </div>`;
}}
function escapeHtml(value) {{
  return String(value || "").replace(/[&<>"']/g, ch => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[ch]));
}}
function collectProviders() {{
  return Array.from(document.querySelectorAll("[data-provider-card]")).map(card => {{
    const item = {{}};
    card.querySelectorAll("[data-provider-field]").forEach(input => {{
      item[input.getAttribute("data-provider-field")] = input.value;
    }});
    item.label = providerTypes[item.type]?.label || item.id;
    item.enabled = true;
    return item;
  }});
}}
function payload() {{
  let weights = {{}};
  try {{ weights = JSON.parse(document.getElementById("weights-json").value || "{{}}"); }} catch (error) {{ weights = {{}}; }}
  return {{
    ui: {{ language: document.getElementById("settings-language").value }},
    llm_registry: {{
      active_provider: document.getElementById("active-provider").value,
      fallback_chain: document.getElementById("fallback-chain").value.split(",").map(x => x.trim()).filter(Boolean),
      providers: collectProviders()
    }},
    system: {{
      tick_interval: Number(document.getElementById("tick-interval-setting").value || 60),
      runtime_mode: document.getElementById("runtime-mode-setting").value,
      trust_threshold: Number(document.getElementById("trust-threshold-setting").value || 0.45),
      hypothesis_switching_sensitivity: Number(document.getElementById("hypothesis-sensitivity-setting").value || 0.08)
    }},
    assets: {{
      portfolio_json: document.getElementById("portfolio-json").value || "{{}}",
      asset_list: document.getElementById("asset-list").value.split("\\n").map(x => x.trim()).filter(Boolean),
      weights
    }},
    metadata: {{ ui_only: true, no_runtime_reload: true, no_trading_execution: true }}
  }};
}}
async function saveSettings() {{
  const result = document.getElementById("settings-result");
  const response = await fetch("/settings", {{
    method: "POST",
    headers: {{ "content-type": "application/json" }},
    body: JSON.stringify(payload())
  }});
  const data = await response.json();
  result.textContent = data.status === "saved" ? "Saved." : JSON.stringify(data);
}}
async function testProvider(card) {{
  const id = card.querySelector('[data-provider-field="id"]').value;
  const status = card.querySelector("[data-provider-status]");
  status.textContent = "Testing...";
  await saveSettings();
  const response = await fetch("/llm/provider/test", {{
    method: "POST",
    headers: {{ "content-type": "application/json" }},
    body: JSON.stringify({{ provider_id: id }})
  }});
  const data = await response.json();
  status.textContent = `${{data.status}} · ${{data.latency_ms}}ms${{data.error ? " · " + data.error : ""}}`;
}}
function bindProviderControls() {{
  document.getElementById("add-provider").addEventListener("click", () => {{
    const type = "custom";
    const id = "custom_" + Date.now();
    const meta = providerTypes[type];
    document.getElementById("provider-list").insertAdjacentHTML("beforeend", providerTemplate(id, type, meta.label, meta.base_url, meta.model));
  }});
  document.addEventListener("click", event => {{
    const card = event.target.closest("[data-provider-card]");
    if (!card) return;
    if (event.target.matches("[data-remove-provider]")) card.remove();
    if (event.target.matches("[data-test-provider]")) testProvider(card);
  }});
}}
document.getElementById("save-settings").addEventListener("click", saveSettings);
document.getElementById("settings-language").addEventListener("change", async () => {{
  await saveSettings();
  window.location.reload();
}});
bindProviderControls();
</script>
</body>
</html>"""


def _provider_card(provider: Mapping[str, Any], active_provider: str) -> str:
    provider_id = str(provider.get("id") or "custom")
    provider_type = str(provider.get("type") or provider_id)
    health = str(provider.get("health") or "unknown")
    latency = provider.get("last_latency_ms")
    status = health + (f" · {latency}ms" if latency is not None else "")
    api_placeholder = "saved" if provider.get("api_key") else "••••••"
    remove_disabled = " disabled" if provider_id == active_provider else ""
    return f"""
    <div class="provider-card" data-provider-card>
      <label>ID<input data-provider-field="id" value="{escape(provider_id)}" readonly></label>
      <label>Type<select data-provider-field="type">{_provider_type_options(provider_type)}</select></label>
      <label>{escape(t("model.model"))}<input data-provider-field="model" value="{escape(str(provider.get("model") or ""))}"></label>
      <div>
        <label>{escape(t("settings.api_key"))}<input data-provider-field="api_key" type="password" placeholder="{escape(api_placeholder)}"></label>
        <span class="provider-status" data-provider-status>{escape(status)}</span>
      </div>
      <label style="grid-column: 1 / -2;">{escape(t("settings.base_url"))}<input data-provider-field="base_url" value="{escape(str(provider.get("base_url") or ""))}"></label>
      <div>
        <button type="button" data-test-provider>{escape(t("settings.test"))}</button>
        <button class="danger" type="button" data-remove-provider{remove_disabled}>{escape(t("settings.remove"))}</button>
      </div>
    </div>
    """


def _config_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if "system" in payload or "assets" in payload or "llm_registry" in payload:
        system = payload.get("system", {}) if isinstance(payload.get("system"), Mapping) else {}
        assets = payload.get("assets", {}) if isinstance(payload.get("assets"), Mapping) else {}
        ui = payload.get("ui", {}) if isinstance(payload.get("ui"), Mapping) else {}
        registry = payload.get("llm_registry", default_provider_registry())
        return {
            "ui": {"language": str(ui.get("language") or current_language())},
            "llm_registry": registry,
            "system": {
                "tick_interval": _int(system.get("tick_interval"), 60),
                "runtime_mode": str(system.get("runtime_mode") or "simulation"),
                "trust_threshold": _float(system.get("trust_threshold"), 0.45),
                "hypothesis_switching_sensitivity": _float(system.get("hypothesis_switching_sensitivity"), 0.08),
            },
            "assets": {
                "portfolio_json": str(assets.get("portfolio_json", "{}") or "{}"),
                "asset_list": assets.get("asset_list", []) if isinstance(assets.get("asset_list"), list) else [],
                "weights": assets.get("weights", {}) if isinstance(assets.get("weights"), dict) else {},
            },
            "metadata": {"ui_only": True, "no_runtime_reload": True, "no_trading_execution": True},
        }
    portfolio_json = str(payload.get("portfolio_json", "{}") or "{}")
    asset_text = str(payload.get("asset_list", "") or "")
    weights_text = str(payload.get("weights", "{}") or "{}")
    try:
        weights = json.loads(weights_text)
        if not isinstance(weights, dict):
            weights = {}
    except json.JSONDecodeError:
        weights = {}
    registry = default_provider_registry()
    registry["active_provider"] = str(payload.get("provider") or "openai").lower()
    for provider in registry["providers"]:
        if provider.get("id") == registry["active_provider"]:
            provider["api_key"] = str(payload.get("api_key") or "")
            provider["base_url"] = str(payload.get("base_url") or provider.get("base_url") or "")
            provider["model"] = str(payload.get("model") or provider.get("model") or "")
    return {
        "llm_registry": registry,
        "ui": {"language": str(payload.get("language") or current_language())},
        "system": {
            "tick_interval": _int(payload.get("tick_interval"), 60),
            "runtime_mode": str(payload.get("runtime_mode") or "simulation"),
            "trust_threshold": _float(payload.get("trust_threshold"), 0.45),
            "hypothesis_switching_sensitivity": _float(payload.get("hypothesis_switching_sensitivity"), 0.08),
        },
        "assets": {
            "portfolio_json": portfolio_json,
            "asset_list": [line.strip() for line in asset_text.splitlines() if line.strip()],
            "weights": weights,
        },
        "metadata": {"ui_only": True, "no_runtime_reload": True, "no_trading_execution": True},
    }


def _merge_defaults(value: Mapping[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for section, section_value in value.items():
        if isinstance(section_value, Mapping) and isinstance(merged.get(section), dict):
            merged[section].update(section_value)
        else:
            merged[section] = section_value
    return merged


def _masked_config(config: Mapping[str, Any]) -> dict[str, Any]:
    masked = _merge_defaults(config)
    registry = safe_registry_view(masked.get("llm_registry", default_provider_registry()))
    masked["llm_registry"] = registry
    return masked


def _provider_options(providers: list[Mapping[str, Any]], selected: str) -> str:
    return "\n".join(
        f'<option value="{escape(str(provider.get("id")))}"{_selected(provider.get("id"), selected)}>{escape(str(provider.get("label") or provider.get("id")))}</option>'
        for provider in providers
    )


def _provider_type_options(selected: str) -> str:
    from runtime.llm.provider_registry import SUPPORTED_PROVIDER_TYPES

    return "\n".join(
        f'<option value="{escape(provider_type)}"{_selected(provider_type, selected)}>{escape(meta["label"])}</option>'
        for provider_type, meta in SUPPORTED_PROVIDER_TYPES.items()
    )


def _selected(value: Any, selected: Any) -> str:
    return " selected" if str(value) == str(selected) else ""


def _asset_list_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value or "")


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
