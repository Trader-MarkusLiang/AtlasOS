"""First-run setup wizard for ordinary Atlas users."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_setup_page(config: Mapping[str, Any]) -> str:
    providers = config.get("providers") if isinstance(config.get("providers"), list) else []
    active = str(config.get("active_provider") or config.get("llm_provider") or "openai")
    provider_options = "\n".join(
        f'<option value="{escape(str(item.get("id")))}" {"selected" if item.get("id") == active else ""}>{escape(str(item.get("label") or item.get("id")))}</option>'
        for item in providers
        if isinstance(item, Mapping)
    )
    if not provider_options:
        provider_options = '<option value="openai">OpenAI-compatible</option><option value="claude">Anthropic</option><option value="ollama">Ollama</option><option value="custom">Custom</option>'
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
@media(max-width:720px) {{ .row {{ grid-template-columns:1fr; }} }}
</style></head><body><main class="wrap">
<h1>Set up Atlas OS</h1>
<p>Configure only what Atlas needs to run locally. API keys are never displayed after storage.</p>
<form id="setup-form">
  <section class="step"><h2>1. Welcome</h2><p>Atlas runs a non-binding cognitive loop. It observes, explains, and records accountability; it does not execute trades.</p></section>
  <section class="step"><h2>2. Language</h2><select name="language"><option value="en">English</option><option value="zh">中文</option></select></section>
  <section class="step"><h2>3. LLM Provider</h2><div class="row"><label>Provider<select name="active_provider">{provider_options}</select></label><label>Model<input name="model" value="{escape(str(config.get("model") or ""))}" placeholder="gpt-5.5 / claude / local model"></label></div><label>API key<input name="api_key" type="password" autocomplete="off" placeholder="Leave blank to keep existing key"></label><button type="button" id="test-provider">Test Connection</button></section>
  <section class="step"><h2>4. Market Data Mode</h2><select name="market_data_mode"><option value="configured_assets">Configured assets only</option><option value="simulation">Simulation fallback</option></select></section>
  <section class="step"><h2>5. Assets / Portfolio Percentages</h2><textarea name="portfolio_json" rows="8" placeholder='[{{"asset":"AAPL","market":"US","portfolio_percentage":12,"theme":"AI","role":"Core"}}]'></textarea></section>
  <section class="step"><h2>6. Risk Preference</h2><select name="risk_preference"><option value="balanced">Balanced</option><option value="conservative">Conservative</option><option value="research_only">Research only</option></select></section>
  <section class="step"><h2>7. Start</h2><button type="submit">Save Setup</button> <a href="/">Show first brief</a></section>
</form>
<pre id="setup-result"></pre>
</main>
<script>
document.getElementById('setup-form').addEventListener('submit', async (event) => {{
  event.preventDefault();
  const form = new FormData(event.target);
  const body = {{ active_provider: form.get('active_provider'), language: form.get('language'), model: form.get('model'), market_data_mode: form.get('market_data_mode'), risk_preference: form.get('risk_preference'), portfolio_json: form.get('portfolio_json') }};
  const response = await fetch('/settings', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body) }});
  document.getElementById('setup-result').textContent = JSON.stringify(await response.json(), null, 2);
}});
document.getElementById('test-provider').addEventListener('click', async () => {{
  const provider = new FormData(document.getElementById('setup-form')).get('active_provider');
  const response = await fetch('/llm/provider/test', {{ method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify({{provider_id: provider}}) }});
  document.getElementById('setup-result').textContent = JSON.stringify(await response.json(), null, 2);
}});
</script></body></html>"""
