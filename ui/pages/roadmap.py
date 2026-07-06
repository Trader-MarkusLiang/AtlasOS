"""Polished Roadmap page for Atlas OS UI."""

from __future__ import annotations

from typing import Any, Mapping


def render_roadmap_page(payload: Mapping[str, Any]) -> str:
    """Render a browser-first roadmap page from the machine-readable payload."""

    layers = [layer for layer in payload.get("layers", []) if isinstance(layer, Mapping)]
    completed = [layer for layer in layers if layer.get("status") == "completed"]
    planned = [layer for layer in layers if layer.get("status") == "planned"]
    completion = int((len(completed) / max(1, len(layers))) * 100)
    layer_cards = "\n".join(_layer_card(layer) for layer in layers)
    architecture = "\n".join(_edge_card(edge, index) for index, edge in enumerate(payload.get("architecture_evolution", [])) if isinstance(edge, Mapping))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Roadmap</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #0b0f14;
  --panel: rgba(18, 24, 32, 0.74);
  --panel-soft: rgba(255, 255, 255, 0.045);
  --line: rgba(255, 255, 255, 0.08);
  --text: #f4f7fb;
  --muted: #8c97a6;
  --subtle: #cbd5e1;
  --ok: #d9f99d;
  --pending: #fde68a;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-width: 360px;
  background:
    radial-gradient(circle at 18% 10%, rgba(148, 163, 184, 0.16), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), transparent 30%),
    var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
a {{ color: inherit; text-decoration: none; }}
.shell {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
.topbar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}}
.brand {{ display: flex; align-items: center; gap: 12px; }}
.brand-mark {{
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  font-weight: 760;
}}
.brand strong, .brand span {{ display: block; }}
.brand span {{ color: var(--muted); font-size: 0.86rem; margin-top: 2px; }}
.nav {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.nav a {{
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  padding: 8px 13px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.055);
}}
.nav a.active {{ background: var(--text); color: var(--bg); }}
.hero {{
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) 420px;
  gap: 16px;
  margin-bottom: 16px;
}}
.card {{
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(20px);
}}
.hero-main {{ min-height: 300px; padding: 28px; }}
.kicker {{ color: var(--muted); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; }}
h1 {{
  max-width: 840px;
  margin: 14px 0 0;
  font-size: clamp(3.2rem, 7vw, 7rem);
  line-height: 0.92;
  letter-spacing: 0;
}}
.hero-main p {{ max-width: 760px; margin: 18px 0 0; color: var(--subtle); line-height: 1.55; }}
.summary-card {{ padding: 22px; }}
.summary-card h2 {{ margin: 8px 0 12px; font-size: 1.4rem; }}
.progress {{ height: 14px; overflow: hidden; border-radius: 999px; background: rgba(255, 255, 255, 0.08); }}
.progress span {{ display: block; width: {completion}%; height: 100%; border-radius: inherit; background: #f4f7fb; }}
.metric-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 16px; }}
.metric {{ padding: 12px; border-radius: 16px; background: var(--panel-soft); }}
.metric span {{ display: block; color: var(--muted); font-size: 0.76rem; }}
.metric strong {{ display: block; margin-top: 4px; overflow-wrap: anywhere; }}
.timeline {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}}
.layer-card {{ padding: 16px; min-height: 190px; }}
.layer-top {{ display: flex; justify-content: space-between; gap: 12px; }}
.version {{ color: var(--text); font-weight: 760; }}
.status {{
  align-self: flex-start;
  padding: 5px 8px;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.72rem;
  text-transform: uppercase;
}}
.status.completed {{ color: var(--ok); border-color: rgba(217, 249, 157, 0.36); }}
.status.planned {{ color: var(--pending); border-color: rgba(253, 230, 138, 0.36); }}
.layer-card h3 {{ margin: 14px 0 8px; font-size: 1rem; }}
.layer-card p {{ margin: 0; color: var(--subtle); line-height: 1.45; }}
.modules {{ margin-top: 12px; color: var(--muted); font-size: 0.8rem; }}
.section-head {{ display: flex; align-items: end; justify-content: space-between; gap: 16px; margin: 26px 0 12px; }}
.section-head h2 {{ margin: 0; font-size: 1.2rem; }}
.section-head p {{ margin: 4px 0 0; color: var(--muted); }}
.architecture {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}}
.edge-card {{ padding: 14px; border-radius: 18px; background: var(--panel-soft); border: 1px solid var(--line); }}
.edge-card span {{ color: var(--muted); font-size: 0.72rem; }}
.edge-card strong {{ display: block; margin-top: 7px; line-height: 1.35; }}
.api-note {{ margin-top: 16px; color: var(--muted); font-size: 0.86rem; }}
.api-note code {{ color: var(--text); }}
@media (max-width: 980px) {{
  .hero {{ grid-template-columns: 1fr; }}
  .topbar {{ align-items: flex-start; flex-direction: column; }}
}}
@media (max-width: 640px) {{
  .shell {{ padding: 16px; }}
  h1 {{ font-size: 3.2rem; }}
  .metric-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<main class="shell">
  <header class="topbar">
    <a class="brand" href="/dashboard">
      <span class="brand-mark">A</span>
      <span><strong>Atlas Roadmap</strong><span>Lifecycle and validation view</span></span>
    </a>
    <nav class="nav" aria-label="Atlas navigation">
      <a href="/dashboard">Dashboard</a>
      <a href="/workflow">Workflow</a>
      <a class="active" href="/roadmap">Roadmap</a>
      <a href="/settings">Settings</a>
    </nav>
  </header>

  <section class="hero">
    <div class="card hero-main">
      <div class="kicker">Current Stage</div>
      <h1>{_escape(str(payload.get("current_stage", "Unknown")))}</h1>
      <p>{_escape(str(payload.get("next_stage", "Unknown")))}. Roadmap is shown as lifecycle state,
      validation evidence, and architecture evolution instead of raw API output.</p>
    </div>
    <aside class="card summary-card">
      <div class="kicker">Release Progress</div>
      <h2>{completion}% completed</h2>
      <div class="progress" aria-label="Roadmap completion"><span></span></div>
      <div class="metric-grid">
        <div class="metric"><span>Range</span><strong>{_escape(str(payload.get("version", "Unknown")))}</strong></div>
        <div class="metric"><span>Completed</span><strong>{len(completed)}</strong></div>
        <div class="metric"><span>Planned</span><strong>{len(planned)}</strong></div>
        <div class="metric"><span>Trust</span><strong>{_escape(str(payload.get("trust_status", "Unknown")))}</strong></div>
      </div>
    </aside>
  </section>

  <div class="section-head">
    <div><div class="kicker">Version Timeline</div><h2>Layer progression</h2><p>Completed layers stay visible for traceability; planned layers remain explicit.</p></div>
  </div>
  <section class="timeline">{layer_cards}</section>

  <div class="section-head">
    <div><div class="kicker">Architecture Evolution</div><h2>How the system moved</h2><p>This is a governance view, not runtime execution.</p></div>
  </div>
  <section class="card" style="padding: 16px;">
    <div class="architecture">{architecture or '<div class="edge-card"><span>Pending</span><strong>No architecture edges available</strong></div>'}</div>
    <p class="api-note">Machine-readable roadmap: <code>/roadmap?format=json</code> or <code>/roadmap.json</code>.</p>
  </section>
</main>
</body>
</html>"""


def _layer_card(layer: Mapping[str, Any]) -> str:
    modules = layer.get("modules_added", [])
    module_count = len(modules) if isinstance(modules, list) else 0
    validation = layer.get("validation", {}) if isinstance(layer.get("validation"), Mapping) else {}
    status = str(layer.get("status", "unknown")).lower()
    return f"""
    <article class="card layer-card">
      <div class="layer-top">
        <span class="version">{_escape(str(layer.get("version", "Unknown")))}</span>
        <span class="status {status}">{_escape(status)}</span>
      </div>
      <h3>{_escape(str(layer.get("name", "Unknown")))}</h3>
      <p>{_escape(str(layer.get("category", "uncategorized")))} layer with validation status {_escape(str(validation.get("status", "UNKNOWN")))}.</p>
      <div class="modules">{module_count} modules added</div>
    </article>
    """


def _edge_card(edge: Mapping[str, Any], index: int) -> str:
    return f"""
    <article class="edge-card">
      <span>Step {index + 1:02d}</span>
      <strong>{_escape(str(edge.get("from", "Unknown")))} -> {_escape(str(edge.get("to", "Unknown")))}</strong>
    </article>
    """


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
