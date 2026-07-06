"""Development registry page for Atlas OS lifecycle traceability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


ROADMAP_PATH = Path("docs/atlas_roadmap.json")


def load_roadmap(path: str | None = None) -> dict[str, Any]:
    """Load the machine-readable Atlas roadmap."""

    target = Path(path) if path else ROADMAP_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_roadmap()
    return data if isinstance(data, dict) else _empty_roadmap()


def roadmap_api_payload(path: str | None = None) -> dict[str, Any]:
    """Return the compact API shape required by /roadmap."""

    roadmap = load_roadmap(path)
    layers = [layer for layer in roadmap.get("layers", []) if isinstance(layer, dict)]
    completed = [layer for layer in layers if layer.get("status") == "completed"]
    planned = [layer for layer in layers if layer.get("status") == "planned"]
    return {
        "version": roadmap.get("version"),
        "current_version": roadmap.get("active_version") or roadmap.get("current_stage"),
        "current_stage": roadmap.get("current_stage"),
        "active_stage": roadmap.get("current_stage"),
        "next_stage": roadmap.get("next_stage"),
        "completed_layers": completed,
        "planned_layers": planned,
        "layers": layers,
        "stability_status": roadmap.get("stability_status"),
        "trust_status": roadmap.get("trust_status"),
        "architecture_evolution": roadmap.get("architecture_evolution", []),
    }


def render_dev_registry_page(roadmap: Mapping[str, Any] | None = None, state: Mapping[str, Any] | None = None) -> str:
    """Render a standalone read-only development registry page."""

    data = dict(roadmap or load_roadmap())
    runtime_state = state if isinstance(state, Mapping) else {}
    layers = [layer for layer in data.get("layers", []) if isinstance(layer, Mapping)]
    edges = [edge for edge in data.get("architecture_evolution", []) if isinstance(edge, Mapping)]
    timeline = "\n".join(_timeline_item(layer) for layer in layers)
    module_rows = "\n".join(_module_row(layer) for layer in layers)
    validation_rows = "\n".join(_validation_row(layer) for layer in layers)
    graph = _architecture_graph(edges)
    state_panel = _state_panel(data, runtime_state)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas OS Dev Registry</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #070a0f;
  --panel: rgba(15, 23, 35, 0.86);
  --line: rgba(148, 163, 184, 0.22);
  --text: #e6edf3;
  --muted: #94a3b8;
  --accent: #5eead4;
  --ok: #86efac;
  --warn: #f8d66d;
  --danger: #fb7185;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-width: 360px;
  background: linear-gradient(135deg, #070a0f 0%, #101622 46%, #090d14 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: 0;
}}
a {{ color: var(--accent); text-decoration: none; }}
.top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  background: rgba(5, 9, 15, 0.9);
}}
.brand h1 {{ margin: 0; font-size: 1.1rem; }}
.brand p {{ margin: 4px 0 0; color: var(--muted); }}
.tabs {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.tab {{
  padding: 8px 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.72);
}}
.tab.active {{ border-color: rgba(94, 234, 212, 0.55); color: var(--accent); }}
.layout {{
  display: grid;
  grid-template-columns: minmax(260px, 0.8fr) minmax(360px, 1.4fr);
  gap: 14px;
  padding: 14px;
}}
.panel {{
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
}}
.panel h2 {{
  margin: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
  font-size: 0.96rem;
}}
.panel-body {{ padding: 14px 16px; }}
.timeline {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.version-item {{
  display: grid;
  grid-template-columns: 64px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.45);
}}
.version {{ color: var(--accent); font-weight: 800; }}
.status {{
  padding: 5px 8px;
  border-radius: 999px;
  border: 1px solid var(--line);
  font-size: 0.75rem;
  text-transform: uppercase;
}}
.status.completed, .status.pass {{ color: var(--ok); border-color: rgba(134, 239, 172, 0.42); }}
.status.planned, .status.pending {{ color: var(--warn); border-color: rgba(248, 214, 109, 0.42); }}
.status.fail {{ color: var(--danger); border-color: rgba(251, 113, 133, 0.42); }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 9px 10px; border-bottom: 1px solid rgba(148, 163, 184, 0.14); text-align: left; vertical-align: top; }}
th {{ color: var(--muted); font-size: 0.75rem; text-transform: uppercase; }}
td {{ color: #dbeafe; }}
.module-list {{ margin: 0; padding-left: 18px; }}
.current-grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}}
.metric {{
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.45);
}}
.metric span {{ display: block; color: var(--muted); font-size: 0.74rem; text-transform: uppercase; }}
.metric strong {{ display: block; margin-top: 5px; overflow-wrap: anywhere; }}
.graph-svg {{
  width: 100%;
  min-height: 250px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.45);
}}
@media (max-width: 980px) {{
  .top {{ align-items: flex-start; flex-direction: column; }}
  .layout {{ grid-template-columns: 1fr; }}
  .current-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<header class="top">
  <div class="brand">
    <h1>Atlas OS Development Registry</h1>
    <p>System lifecycle, roadmap, validation, and architecture traceability</p>
  </div>
  <nav class="tabs" aria-label="Atlas UI tabs">
    <a class="tab" href="/dashboard">System</a>
    <a class="tab" href="/chat">Chat</a>
    <a class="tab" href="/dashboard#inspector">Inspector</a>
    <a class="tab" href="/dashboard#graph">Graph</a>
    <a class="tab" href="/roadmap">Roadmap</a>
    <a class="tab active" href="/dev-registry">Dev Registry</a>
  </nav>
</header>
<main class="layout">
  <section class="panel">
    <h2>Version Timeline</h2>
    <div class="panel-body timeline">{timeline}</div>
  </section>
  <section class="panel">
    <h2>Current System State</h2>
    <div class="panel-body">{state_panel}</div>
  </section>
  <section class="panel">
    <h2>Module Evolution Log</h2>
    <div class="panel-body"><table><thead><tr><th>Version</th><th>Layer</th><th>Modules</th></tr></thead><tbody>{module_rows}</tbody></table></div>
  </section>
  <section class="panel">
    <h2>Validation Results</h2>
    <div class="panel-body"><table><thead><tr><th>Version</th><th>Status</th><th>Result</th></tr></thead><tbody>{validation_rows}</tbody></table></div>
  </section>
  <section class="panel" style="grid-column: 1 / -1;">
    <h2>System Architecture Evolution Graph</h2>
    <div class="panel-body">{graph}</div>
  </section>
</main>
</body>
</html>"""


def _timeline_item(layer: Mapping[str, Any]) -> str:
    status = str(layer.get("status", "unknown"))
    return (
        '<a class="version-item" href="#version-'
        + _escape(str(layer.get("version", ""))).replace(".", "-")
        + '">'
        + f'<span class="version">{_escape(str(layer.get("version", "Unknown")))}</span>'
        + f'<span>{_escape(str(layer.get("name", "Unknown")))}</span>'
        + f'<span class="status {status}">{_escape(status)}</span>'
        + "</a>"
    )


def _module_row(layer: Mapping[str, Any]) -> str:
    modules = layer.get("modules_added", [])
    if isinstance(modules, list) and modules:
        module_html = "<ul class=\"module-list\">" + "".join(f"<li>{_escape(str(item))}</li>" for item in modules) + "</ul>"
    else:
        module_html = '<span style="color: var(--muted);">None yet</span>'
    return (
        f'<tr id="version-{_escape(str(layer.get("version", ""))).replace(".", "-")}">'
        f'<td>{_escape(str(layer.get("version", "Unknown")))}</td>'
        f'<td>{_escape(str(layer.get("name", "Unknown")))}</td>'
        f"<td>{module_html}</td>"
        "</tr>"
    )


def _validation_row(layer: Mapping[str, Any]) -> str:
    validation = layer.get("validation", {}) if isinstance(layer.get("validation"), Mapping) else {}
    status = str(validation.get("status", "UNKNOWN")).lower()
    result_file = validation.get("result_file")
    result = _escape(str(result_file)) if result_file else "Pending validation result"
    return (
        "<tr>"
        f'<td>{_escape(str(layer.get("version", "Unknown")))}</td>'
        f'<td><span class="status {status}">{_escape(status.upper())}</span></td>'
        f"<td>{result}</td>"
        "</tr>"
    )


def _state_panel(roadmap: Mapping[str, Any], runtime_state: Mapping[str, Any]) -> str:
    trust = runtime_state.get("trust_index") if isinstance(runtime_state, Mapping) else None
    regime = runtime_state.get("regime_state") if isinstance(runtime_state, Mapping) else None
    return f"""
    <div class="current-grid">
      <div class="metric"><span>Active Version</span><strong>{_escape(str(roadmap.get("active_version") or roadmap.get("current_stage") or "Unknown"))}</strong></div>
      <div class="metric"><span>Stability</span><strong>{_escape(str(roadmap.get("stability_status", "Unknown")))}</strong></div>
      <div class="metric"><span>Trust Status</span><strong>{_escape(str(roadmap.get("trust_status", "Unknown")))}</strong></div>
      <div class="metric"><span>Runtime Regime</span><strong>{_escape(str(regime or "Unknown"))}</strong></div>
      <div class="metric"><span>Runtime Trust Index</span><strong>{_escape(str(trust if trust is not None else "Unknown"))}</strong></div>
      <div class="metric"><span>Next Stage</span><strong>{_escape(str(roadmap.get("next_stage", "Unknown")))}</strong></div>
    </div>
    """


def _architecture_graph(edges: list[Mapping[str, Any]]) -> str:
    if not edges:
        edges = [{"from": "Runtime", "to": "Registry"}]
    labels = []
    for edge in edges:
        labels.extend([str(edge.get("from", "")), str(edge.get("to", ""))])
    nodes = []
    for label in labels:
        if label and label not in nodes:
            nodes.append(label)
    width = 980
    height = 280
    gap = width / max(1, len(nodes) + 1)
    positions = {node: (int(gap * (index + 1)), 140 + (-45 if index % 2 == 0 else 45)) for index, node in enumerate(nodes)}
    line_parts = []
    for edge in edges:
        source = str(edge.get("from", ""))
        target = str(edge.get("to", ""))
        if source not in positions or target not in positions:
            continue
        sx, sy = positions[source]
        tx, ty = positions[target]
        line_parts.append(f'<line x1="{sx}" y1="{sy}" x2="{tx}" y2="{ty}" stroke="#5eead4" stroke-width="2" opacity="0.68" />')
    node_parts = []
    for node, (x, y) in positions.items():
        node_parts.append(f'<circle cx="{x}" cy="{y}" r="36" fill="rgba(15, 23, 35, 0.95)" stroke="#5eead4" stroke-width="1.5" />')
        node_parts.append(f'<text x="{x}" y="{y + 4}" fill="#e6edf3" font-size="10" text-anchor="middle">{_escape(_short(node))}</text>')
    return f'<svg class="graph-svg" viewBox="0 0 {width} {height}" role="img" aria-label="Architecture evolution graph">{"".join(line_parts + node_parts)}</svg>'


def _short(value: str) -> str:
    return value if len(value) <= 18 else value[:16] + ".."


def _empty_roadmap() -> dict[str, Any]:
    return {
        "version": "unknown",
        "current_stage": "unknown",
        "next_stage": "unknown",
        "layers": [],
        "architecture_evolution": [],
    }


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
