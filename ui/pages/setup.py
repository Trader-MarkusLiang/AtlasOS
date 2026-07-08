"""First-run setup wizard for ordinary Atlas users."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_setup_page(config: Mapping[str, Any]) -> str:
    ui_config = config.get("ui") if isinstance(config.get("ui"), Mapping) else {}
    configured_lang = str(ui_config.get("language") or "").lower()
    lang = configured_lang if configured_lang in {"en", "zh"} else current_language()
    registry = config.get("llm_registry") if isinstance(config.get("llm_registry"), Mapping) else {}
    providers = registry.get("providers") if isinstance(registry.get("providers"), list) else []
    active = str(registry.get("active_provider") or config.get("active_provider") or config.get("llm_provider") or "openai")
    provider_options = "\n".join(
        f'<option value="{escape(str(item.get("id")))}" {"selected" if item.get("id") == active else ""}>{escape(str(item.get("label") or item.get("id")))}</option>'
        for item in providers
        if isinstance(item, Mapping)
    )
    if not provider_options:
        provider_options = '<option value="openai">OpenAI-compatible</option><option value="claude">Anthropic</option><option value="ollama">Ollama</option><option value="custom">Custom</option>'
    active_provider = next((item for item in providers if isinstance(item, Mapping) and str(item.get("id")) == active), {})
    default_model = str(active_provider.get("model") or config.get("model") or "")
    default_base_url = str(active_provider.get("base_url") or "")
    ui_text = {
        "saving_before_test": t("setup.saving_before_test", lang),
        "saved": t("setup.saved", lang),
        "save_failed": t("setup.save_failed", lang),
        "test_complete": t("setup.test_complete", lang),
        "starting": t("setup.starting", lang),
        "start_failed": t("setup.start_failed", lang),
    }
    return f"""<!doctype html>
<html lang="{escape(lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(t("setup.title", lang))}</title>
<style>
body {{ margin:0; background:#0b0f14; color:#edf2f7; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
.wrap {{ max-width:980px; margin:0 auto; padding:34px 22px; }}
.step {{ margin:14px 0; padding:18px; border:1px solid rgba(255,255,255,.12); border-radius:18px; background:rgba(255,255,255,.06); }}
label {{ display:grid; gap:7px; margin:10px 0; color:#aab4c3; }}
input, select, textarea, button {{ font:inherit; border-radius:12px; border:1px solid rgba(255,255,255,.14); background:#101722; color:#edf2f7; padding:10px 12px; }}
button {{ background:#dbeafe; color:#0b0f14; cursor:pointer; }}
.row {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.asset-grid {{ display:grid; grid-template-columns:1.1fr .8fr .7fr 1fr; gap:10px; }}
.asset-extra {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }}
.muted {{ color:#9aa7b8; line-height:1.5; }}
.result {{ margin-top:14px; padding:12px 14px; border-radius:14px; background:rgba(255,255,255,.06); color:#dbeafe; min-height:44px; white-space:normal; }}
@media(max-width:720px) {{ .row {{ grid-template-columns:1fr; }} }}
@media(max-width:820px) {{ .asset-grid, .asset-extra {{ grid-template-columns:1fr; }} }}
</style></head><body><main class="wrap">
<h1>{escape(t("setup.title", lang))}</h1>
<p>{escape(t("setup.subtitle", lang))}</p>
<form id="setup-form">
  <section class="step"><h2>{escape(t("setup.welcome_title", lang))}</h2><p>{escape(t("setup.welcome_body", lang))}</p></section>
  <section class="step"><h2>{escape(t("setup.language_title", lang))}</h2><select name="language"><option value="en" {"selected" if lang == "en" else ""}>English</option><option value="zh" {"selected" if lang == "zh" else ""}>中文</option></select></section>
  <section class="step"><h2>{escape(t("setup.provider_title", lang))}</h2><div class="row"><label>{escape(t("setup.provider", lang))}<select name="active_provider">{provider_options}</select></label><label>{escape(t("setup.model", lang))}<input name="model" value="{escape(default_model)}" placeholder="gpt-5.5 / claude / local model"></label></div><label>{escape(t("setup.base_url", lang))}<input name="base_url" value="{escape(default_base_url)}" placeholder="Provider endpoint"></label><label>{escape(t("setup.api_key", lang))}<input name="api_key" type="password" autocomplete="off" placeholder="{escape(t("setup.api_key_hint", lang))}"></label><button type="button" id="test-provider">{escape(t("setup.test_connection", lang))}</button></section>
  <section class="step"><h2>{escape(t("setup.market_mode_title", lang))}</h2><select name="market_data_mode"><option value="configured_assets">{escape(t("setup.configured_assets", lang))}</option><option value="simulation">{escape(t("setup.simulation_fallback", lang))}</option></select></section>
  <section class="step"><h2>{escape(t("setup.assets_title", lang))}</h2><p class="muted">{escape(t("setup.assets_note", lang))}</p><div id="asset-rows"></div><button type="button" id="add-asset">{escape(t("setup.add_asset", lang))}</button></section>
  <section class="step"><h2>{escape(t("setup.risk_title", lang))}</h2><select name="risk_preference"><option value="balanced">{escape(t("setup.balanced", lang))}</option><option value="conservative">{escape(t("setup.conservative", lang))}</option><option value="research_only">{escape(t("setup.research_only", lang))}</option></select></section>
  <section class="step"><h2>{escape(t("setup.start_title", lang))}</h2><button type="submit">{escape(t("setup.save", lang))}</button> <button type="button" id="start-runtime">{escape(t("setup.start_runtime", lang))}</button> <a href="/">{escape(t("setup.show_brief", lang))}</a> <a href="/dashboard">{escape(t("setup.ask_atlas", lang))}</a></section>
</form>
<div id="setup-result" class="result" role="status">{escape(t("setup.waiting", lang))}</div>
</main>
<script>
const providerMeta = {json.dumps({str(item.get("id")): {"base_url": str(item.get("base_url") or ""), "model": str(item.get("model") or "")} for item in providers if isinstance(item, Mapping)}, ensure_ascii=False)};
const uiText = {json.dumps(ui_text, ensure_ascii=False)};
function rowTemplate() {{
  return `<div class="step asset-row">
    <div class="asset-grid">
      <label>{escape(t("setup.asset", lang))}<input data-asset-field="asset" placeholder="AAPL"></label>
      <label>{escape(t("setup.market", lang))}<select data-asset-field="market"><option value="US">US</option><option value="HK">HK</option><option value="A-share">A-share</option><option value="ETF">ETF</option></select></label>
      <label>{escape(t("setup.percentage", lang))}<input data-asset-field="portfolio_percentage" type="number" min="0" max="100" step="0.1" placeholder="12"></label>
      <label>{escape(t("setup.theme", lang))}<input data-asset-field="theme" placeholder="AI / Memory / Platform"></label>
    </div>
    <div class="asset-extra">
      <label>{escape(t("setup.role", lang))}<input data-asset-field="role" placeholder="Core / Watch / Hedge"></label>
      <label>{escape(t("setup.risk_note", lang))}<input data-asset-field="risk_note" placeholder="What should Atlas watch?"></label>
    </div>
    <label>{escape(t("setup.thesis", lang))}<textarea data-asset-field="thesis" rows="2" placeholder="Why this asset matters to your portfolio"></textarea></label>
  </div>`;
}}
function addAssetRow() {{
  document.getElementById("asset-rows").insertAdjacentHTML("beforeend", rowTemplate());
}}
function collectAssets() {{
  return Array.from(document.querySelectorAll(".asset-row")).map(row => {{
    const item = {{}};
    row.querySelectorAll("[data-asset-field]").forEach(input => item[input.dataset.assetField] = input.value.trim());
    item.portfolio_percentage = Number(item.portfolio_percentage || 0);
    return item;
  }}).filter(item => item.asset);
}}
function currentPayload() {{
  const form = new FormData(document.getElementById('setup-form'));
  const provider = String(form.get('active_provider') || 'openai');
  return {{
    active_provider: provider,
    language: form.get('language'),
    model: form.get('model'),
    base_url: form.get('base_url'),
    api_key: form.get('api_key'),
    market_data_mode: form.get('market_data_mode'),
    risk_preference: form.get('risk_preference'),
    portfolio_json: JSON.stringify({{ positions: collectAssets() }})
  }};
}}
function statusText(data, fallback) {{
  if (!data || typeof data !== "object") return fallback;
  if (data.status === "saved") return uiText.saved;
  if (data.status) return `Status: ${{data.status}}${{data.error ? " · " + data.error : ""}}${{data.latency_ms !== undefined ? " · " + data.latency_ms + "ms" : ""}}`;
  return fallback;
}}
document.querySelector('[name="active_provider"]').addEventListener('change', event => {{
  const meta = providerMeta[event.target.value] || {{}};
  if (meta.base_url) document.querySelector('[name="base_url"]').value = meta.base_url;
  if (meta.model) document.querySelector('[name="model"]').value = meta.model;
}});
document.getElementById('add-asset').addEventListener('click', addAssetRow);
addAssetRow();
document.getElementById('setup-form').addEventListener('submit', async (event) => {{
  event.preventDefault();
  const body = currentPayload();
  const response = await fetch('/settings', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body) }});
  const data = await response.json();
  document.getElementById('setup-result').textContent = statusText(data, uiText.saved);
}});
document.getElementById('test-provider').addEventListener('click', async () => {{
  const setupResult = document.getElementById('setup-result');
  const body = currentPayload();
  setupResult.textContent = uiText.saving_before_test;
  const saved = await fetch('/settings', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body) }});
  const savedData = await saved.json();
  if (savedData.status !== "saved") {{
    setupResult.textContent = statusText(savedData, uiText.save_failed);
    return;
  }}
  const response = await fetch('/llm/provider/test', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify({{provider_id: body.active_provider}}) }});
  const data = await response.json();
  setupResult.textContent = statusText(data, uiText.test_complete);
}});
document.getElementById('start-runtime').addEventListener('click', async () => {{
  const setupResult = document.getElementById('setup-result');
  const body = currentPayload();
  setupResult.textContent = uiText.starting;
  const saved = await fetch('/settings', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body) }});
  const savedData = await saved.json();
  if (savedData.status !== "saved") {{
    setupResult.textContent = statusText(savedData, uiText.save_failed);
    return;
  }}
  const response = await fetch('/control/start', {{ method:'POST' }});
  const data = await response.json();
  setupResult.textContent = statusText(data, uiText.start_failed);
}});
</script></body></html>"""
