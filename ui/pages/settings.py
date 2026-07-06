"""Settings page and local config storage for Atlas OS UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CONFIG_PATH = Path("runtime/config/user_config.json")


DEFAULT_CONFIG: dict[str, Any] = {
    "llm": {
        "provider": "OpenAI",
        "api_key": "",
        "base_url": "",
        "model": "gpt-5.5",
    },
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
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "saved", "config": _masked_config(config), "path": str(target)}


def render_settings_page(config: Mapping[str, Any] | None = None) -> str:
    data = _merge_defaults(dict(config or load_user_config()))
    llm = data["llm"]
    system = data["system"]
    assets = data["assets"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas OS Settings</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #0B0F14;
  --panel: rgba(18, 24, 32, 0.76);
  --panel-soft: rgba(255, 255, 255, 0.045);
  --line: rgba(255, 255, 255, 0.08);
  --text: #f4f7fb;
  --muted: #8c97a6;
  --accent: #f4f7fb;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.035), transparent 28%),
    var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
a {{ color: var(--accent); text-decoration: none; }}
.settings-shell {{
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 100vh;
}}
.settings-sidebar {{
  padding: 18px;
  border-right: 1px solid var(--line);
  background: rgba(13, 18, 25, 0.78);
  backdrop-filter: blur(22px);
}}
.settings-sidebar h1 {{ margin: 0 0 8px; font-size: 1.05rem; }}
.settings-sidebar p {{ margin: 0 0 18px; color: var(--muted); }}
.settings-sidebar a {{
  display: block;
  margin-bottom: 8px;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel-soft);
}}
.settings-main {{ padding: 20px; }}
.settings-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}}
.settings-header h2 {{ margin: 0; }}
.config-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}}
.config-card {{
  border: 1px solid var(--line);
  border-radius: 20px;
  backdrop-filter: blur(18px);
  background: var(--panel);
  overflow: hidden;
}}
.config-card h3 {{
  margin: 0;
  padding: 13px 14px;
  border-bottom: 1px solid var(--line);
  font-size: 0.96rem;
}}
.config-body {{ padding: 14px; }}
label {{ display: block; margin-bottom: 11px; color: var(--muted); font-size: 0.82rem; }}
input, select, textarea {{
  width: 100%;
  margin-top: 5px;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: rgba(9, 13, 19, 0.86);
  color: var(--text);
  font: inherit;
}}
textarea {{ min-height: 118px; resize: vertical; }}
button {{
  padding: 10px 14px;
  border: 1px solid rgba(94, 234, 212, 0.48);
  border-radius: 999px;
  background: var(--text);
  color: var(--bg);
  cursor: pointer;
}}
.notice {{
  margin-top: 14px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel-soft);
  color: var(--muted);
}}
@media (max-width: 980px) {{
  .settings-shell {{ grid-template-columns: 1fr; }}
  .settings-sidebar {{ border-right: 0; border-bottom: 1px solid var(--line); }}
  .config-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="settings-shell">
  <aside class="settings-sidebar">
    <h1>Atlas Settings</h1>
    <p>Local UI configuration. Saving does not reload runtime or execute trades.</p>
    <a href="/dashboard">Dashboard</a>
    <a href="/workflow">Workflow</a>
    <a href="/system-guide">System Guide</a>
  </aside>
  <main class="settings-main">
    <div class="settings-header">
      <h2>Control Plane Configuration</h2>
      <button form="settings-form" type="submit">Save Settings</button>
    </div>
    <form id="settings-form" class="config-grid" method="post" action="/settings">
      <section id="llm-config" class="config-card">
        <h3>LLM Config</h3>
        <div class="config-body">
          <label>Provider
            <select name="provider">
              {_option("OpenAI", llm.get("provider"))}
              {_option("Claude", llm.get("provider"))}
              {_option("Ollama", llm.get("provider"))}
              {_option("Custom API", llm.get("provider"))}
            </select>
          </label>
          <label>API Key
            <input name="api_key" type="password" value="{_escape(str(llm.get("api_key", "")))}" autocomplete="off">
          </label>
          <label>Base URL
            <input name="base_url" value="{_escape(str(llm.get("base_url", "")))}" placeholder="https://api.example.com">
          </label>
          <label>Model
            <input name="model" value="{_escape(str(llm.get("model", "")))}" placeholder="gpt-5.5">
          </label>
        </div>
      </section>
      <section id="system-config" class="config-card">
        <h3>Atlas System Config</h3>
        <div class="config-body">
          <label>Tick Interval
            <input name="tick_interval" type="number" min="10" step="1" value="{_escape(str(system.get("tick_interval", 60)))}">
          </label>
          <label>Runtime Mode
            <select name="runtime_mode">
              {_option("simulation", system.get("runtime_mode"))}
              {_option("live", system.get("runtime_mode"))}
            </select>
          </label>
          <label>Trust Threshold
            <input name="trust_threshold" type="number" min="0" max="1" step="0.01" value="{_escape(str(system.get("trust_threshold", 0.45)))}">
          </label>
          <label>Hypothesis Switching Sensitivity
            <input name="hypothesis_switching_sensitivity" type="number" min="0" max="1" step="0.01" value="{_escape(str(system.get("hypothesis_switching_sensitivity", 0.08)))}">
          </label>
        </div>
      </section>
      <section id="asset-config" class="config-card">
        <h3>User Assets Config</h3>
        <div class="config-body">
          <label>Portfolio JSON
            <textarea name="portfolio_json">{_escape(str(assets.get("portfolio_json", "{}")))}</textarea>
          </label>
          <label>Asset List
            <textarea name="asset_list" placeholder="AAPL&#10;MSFT">{_escape(_asset_list_text(assets.get("asset_list")))}</textarea>
          </label>
          <label>Optional Weights JSON
            <textarea name="weights">{_escape(json.dumps(assets.get("weights", {}), ensure_ascii=False, indent=2))}</textarea>
          </label>
        </div>
      </section>
    </form>
    <div class="notice">Config is UI-only metadata stored in <code>runtime/config/user_config.json</code>. It does not perform trading, portfolio mutation, or runtime reload.</div>
  </main>
</div>
</body>
</html>"""


def _config_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    portfolio_json = str(payload.get("portfolio_json", "{}") or "{}")
    asset_text = str(payload.get("asset_list", "") or "")
    weights_text = str(payload.get("weights", "{}") or "{}")
    try:
        weights = json.loads(weights_text)
        if not isinstance(weights, dict):
            weights = {}
    except json.JSONDecodeError:
        weights = {}
    return {
        "llm": {
            "provider": str(payload.get("provider") or "OpenAI"),
            "api_key": str(payload.get("api_key") or ""),
            "base_url": str(payload.get("base_url") or ""),
            "model": str(payload.get("model") or "gpt-5.5"),
        },
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
        "metadata": {
            "ui_only": True,
            "no_runtime_reload": True,
            "no_trading_execution": True,
        },
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
    if masked.get("llm", {}).get("api_key"):
        masked["llm"]["api_key"] = "***"
    return masked


def _option(value: str, selected: Any) -> str:
    mark = " selected" if str(value) == str(selected) else ""
    return f'<option value="{_escape(value)}"{mark}>{_escape(value)}</option>'


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


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
