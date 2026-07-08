"""First-run setup wizard for ordinary Atlas users."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping


def render_setup_page(config: Mapping[str, Any]) -> str:
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
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Setup</title>
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
<h1>Set up Atlas OS</h1>
<p>Configure only what Atlas needs to run locally. API keys are never displayed after storage.</p>
<form id="setup-form">
  <section class="step"><h2>1. Welcome</h2><p>Atlas runs a non-binding cognitive loop. It observes, explains, and records accountability; it does not execute trades.</p></section>
  <section class="step"><h2>2. Language</h2><select name="language"><option value="en">English</option><option value="zh">中文</option></select></section>
  <section class="step"><h2>3. LLM Provider</h2><div class="row"><label>Provider<select name="active_provider">{provider_options}</select></label><label>Model<input name="model" value="{escape(default_model)}" placeholder="gpt-5.5 / claude / local model"></label></div><label>Base URL<input name="base_url" value="{escape(default_base_url)}" placeholder="Provider endpoint"></label><label>API key<input name="api_key" type="password" autocomplete="off" placeholder="Leave blank to keep existing key"></label><button type="button" id="test-provider">Test Connection</button></section>
  <section class="step"><h2>4. Market Data Mode</h2><select name="market_data_mode"><option value="configured_assets">Configured assets only</option><option value="simulation">Simulation fallback</option></select></section>
  <section class="step"><h2>5. Assets / Portfolio Percentages</h2><p class="muted">Add percentages only. Atlas does not need account value, cost basis, broker data, or exact holdings amount.</p><div id="asset-rows"></div><button type="button" id="add-asset">Add Asset</button></section>
  <section class="step"><h2>6. Risk Preference</h2><select name="risk_preference"><option value="balanced">Balanced</option><option value="conservative">Conservative</option><option value="research_only">Research only</option></select></section>
  <section class="step"><h2>7. Start</h2><button type="submit">Save Setup</button> <a href="/">Show first brief</a></section>
</form>
<div id="setup-result" class="result" role="status">Waiting for setup.</div>
</main>
<script>
const providerMeta = {json.dumps({str(item.get("id")): {"base_url": str(item.get("base_url") or ""), "model": str(item.get("model") or "")} for item in providers if isinstance(item, Mapping)}, ensure_ascii=False)};
function rowTemplate() {{
  return `<div class="step asset-row">
    <div class="asset-grid">
      <label>Asset<input data-asset-field="asset" placeholder="AAPL"></label>
      <label>Market<select data-asset-field="market"><option value="US">US</option><option value="HK">HK</option><option value="A-share">A-share</option><option value="ETF">ETF</option></select></label>
      <label>Percentage<input data-asset-field="portfolio_percentage" type="number" min="0" max="100" step="0.1" placeholder="12"></label>
      <label>Theme<input data-asset-field="theme" placeholder="AI / Memory / Platform"></label>
    </div>
    <div class="asset-extra">
      <label>Role<input data-asset-field="role" placeholder="Core / Watch / Hedge"></label>
      <label>Risk note<input data-asset-field="risk_note" placeholder="What should Atlas watch?"></label>
    </div>
    <label>Thesis<textarea data-asset-field="thesis" rows="2" placeholder="Why this asset matters to your portfolio"></textarea></label>
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
  if (data.status === "saved") return "Setup saved. Atlas can now use this configuration.";
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
  document.getElementById('setup-result').textContent = statusText(data, "Setup saved.");
}});
document.getElementById('test-provider').addEventListener('click', async () => {{
  const setupResult = document.getElementById('setup-result');
  const body = currentPayload();
  setupResult.textContent = "Saving current values before provider test...";
  const saved = await fetch('/settings', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body) }});
  const savedData = await saved.json();
  if (savedData.status !== "saved") {{
    setupResult.textContent = statusText(savedData, "Could not save setup before provider test.");
    return;
  }}
  const response = await fetch('/llm/provider/test', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify({{provider_id: body.active_provider}}) }});
  const data = await response.json();
  setupResult.textContent = statusText(data, "Provider test complete.");
}});
</script></body></html>"""
