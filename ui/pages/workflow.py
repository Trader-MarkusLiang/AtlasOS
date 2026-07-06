"""Polished Workflow page for Atlas OS UI."""

from __future__ import annotations

from ui.components.workflow_graph import WORKFLOW_NODES


STAGE_META = {
    "event_stream": {
        "boundary": "Input boundary",
        "output": "Schema-safe event",
        "risk": "Never bypass validation",
    },
    "cognitive_pipeline": {
        "boundary": "Cognition core",
        "output": "Contextual state",
        "risk": "No direct infrastructure coupling",
    },
    "causal_layer": {
        "boundary": "Reasoning layer",
        "output": "Causal interpretation",
        "risk": "No signal-engine collapse",
    },
    "world_model": {
        "boundary": "Market representation",
        "output": "Evolving structure",
        "risk": "No forecasting shortcut",
    },
    "hypothesis_engine": {
        "boundary": "Model plurality",
        "output": "Active and shadow hypotheses",
        "risk": "Avoid oscillation",
    },
    "decision_contract": {
        "boundary": "Strict schema",
        "output": "Validated DecisionPacket",
        "risk": "No unstructured output",
    },
    "llm_router": {
        "boundary": "Provider isolation",
        "output": "Raw reasoning text",
        "risk": "No direct cognition mutation",
    },
    "feedback_loop": {
        "boundary": "Bounded feedback",
        "output": "Next tick adjustment",
        "risk": "Trust-gated only",
    },
}


def render_workflow_page(active_stage: str = "event_stream") -> str:
    """Render a standalone product-grade Workflow page."""

    active = active_stage if active_stage in STAGE_META else "event_stream"
    active_index = _active_index(active)
    stage_cards = "\n".join(_stage_card(key, label, description, index, active_index) for index, (key, label, description) in enumerate(WORKFLOW_NODES))
    active_label = next((label for key, label, _ in WORKFLOW_NODES if key == active), "Event Stream")
    active_description = next((description for key, _, description in WORKFLOW_NODES if key == active), "")
    meta = STAGE_META.get(active, STAGE_META["event_stream"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Workflow</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #0b0f14;
  --panel: rgba(18, 24, 32, 0.74);
  --panel-soft: rgba(255, 255, 255, 0.045);
  --line: rgba(255, 255, 255, 0.08);
  --line-strong: rgba(255, 255, 255, 0.18);
  --text: #f4f7fb;
  --muted: #8c97a6;
  --subtle: #cbd5e1;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-width: 360px;
  background:
    radial-gradient(circle at 82% 8%, rgba(148, 163, 184, 0.14), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), transparent 28%),
    var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: 0;
}}
a {{ color: inherit; text-decoration: none; }}
.page-shell {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
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
  grid-template-columns: minmax(0, 1.2fr) 360px;
  gap: 16px;
  margin-bottom: 16px;
}}
.hero-card, .detail-card, .stage-map, .principle-card {{
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(20px);
}}
.hero-card {{ min-height: 260px; padding: 28px; }}
.kicker {{
  color: var(--muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}}
h1 {{
  max-width: 780px;
  margin: 14px 0 0;
  font-size: clamp(3rem, 7vw, 6.6rem);
  line-height: 0.92;
  letter-spacing: 0;
}}
.hero-card p {{ max-width: 780px; margin: 18px 0 0; color: var(--subtle); line-height: 1.55; }}
.detail-card {{ padding: 22px; }}
.detail-card h2 {{ margin: 8px 0 8px; font-size: 1.45rem; }}
.detail-card p {{ margin: 0; color: var(--subtle); line-height: 1.5; }}
.fact-grid {{ display: grid; gap: 10px; margin-top: 18px; }}
.fact-grid div {{ padding: 12px; border-radius: 16px; background: var(--panel-soft); }}
.fact-grid span {{ display: block; color: var(--muted); font-size: 0.76rem; }}
.fact-grid strong {{ display: block; margin-top: 4px; }}
.stage-map {{ padding: 18px; }}
.stage-rail {{
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
}}
.stage-card {{
  min-height: 164px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
  opacity: 0.44;
  transition: opacity 180ms ease, transform 180ms ease, border-color 180ms ease;
}}
.stage-card.done {{ opacity: 0.82; }}
.stage-card.active {{ opacity: 1; border-color: var(--line-strong); background: var(--text); color: var(--bg); }}
.stage-card:hover {{ opacity: 1; transform: translateY(-2px); }}
.stage-index {{ color: var(--muted); font-size: 0.76rem; }}
.stage-card.active .stage-index {{ color: #475569; }}
.stage-card strong {{ display: block; margin-top: 10px; line-height: 1.12; }}
.stage-card span:last-child {{ display: block; margin-top: 10px; color: var(--muted); font-size: 0.78rem; line-height: 1.35; }}
.stage-card.active span:last-child {{ color: #334155; }}
.principles {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}}
.principle-card {{ padding: 18px; }}
.principle-card h3 {{ margin: 8px 0 8px; font-size: 1rem; }}
.principle-card p {{ margin: 0; color: var(--subtle); line-height: 1.5; }}
@media (max-width: 1180px) {{
  .hero {{ grid-template-columns: 1fr; }}
  .stage-rail {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
}}
@media (max-width: 720px) {{
  .page-shell {{ padding: 16px; }}
  .topbar {{ align-items: flex-start; flex-direction: column; }}
  .stage-rail, .principles {{ grid-template-columns: 1fr; }}
  h1 {{ font-size: 3.2rem; }}
}}
</style>
</head>
<body>
<main class="page-shell">
  <header class="topbar">
    <a class="brand" href="/dashboard">
      <span class="brand-mark">A</span>
      <span><strong>Atlas Workflow</strong><span>Cognitive pipeline map</span></span>
    </a>
    <nav class="nav" aria-label="Atlas navigation">
      <a href="/dashboard">Dashboard</a>
      <a class="active" href="/workflow">Workflow</a>
      <a href="/roadmap">Roadmap</a>
      <a href="/settings">Settings</a>
    </nav>
  </header>

  <section class="hero">
    <div class="hero-card">
      <div class="kicker">Guided Execution Path</div>
      <h1>From event to bounded feedback.</h1>
      <p>Atlas does not expose a raw debug chain here. This page shows the system boundary,
      stage responsibility, and active path through the cognitive runtime.</p>
    </div>
    <aside class="detail-card" id="stage-detail">
      <div class="kicker">Active Stage</div>
      <h2>{_escape(active_label)}</h2>
      <p>{_escape(active_description)}</p>
      <div class="fact-grid">
        <div><span>Boundary</span><strong>{_escape(meta["boundary"])}</strong></div>
        <div><span>Output</span><strong>{_escape(meta["output"])}</strong></div>
        <div><span>Guardrail</span><strong>{_escape(meta["risk"])}</strong></div>
      </div>
    </aside>
  </section>

  <section class="stage-map">
    <div class="kicker">Active Path</div>
    <div class="stage-rail" aria-label="Atlas workflow stages">{stage_cards}</div>
  </section>

  <section class="principles">
    <div class="principle-card"><div class="kicker">Boundary</div><h3>Read-only UI</h3><p>The page explains the runtime path without importing cognition or mutating state.</p></div>
    <div class="principle-card"><div class="kicker">Contract</div><h3>Structured outputs</h3><p>Decision output remains mediated by the Decision Contract and validation layers.</p></div>
    <div class="principle-card"><div class="kicker">Feedback</div><h3>Bounded adaptation</h3><p>Feedback is shown as a controlled loop, not as trading execution or prediction.</p></div>
  </section>
</main>
<script>
(function () {{
  const meta = __STAGE_META_JSON__;
  document.querySelectorAll("[data-stage-key]").forEach(function (card) {{
    card.addEventListener("click", function (event) {{
      event.preventDefault();
      const key = card.getAttribute("data-stage-key");
      const detail = document.getElementById("stage-detail");
      const data = meta[key] || {{}};
      document.querySelectorAll("[data-stage-key]").forEach(function (item) {{ item.classList.remove("active"); }});
      card.classList.add("active");
      if (detail) {{
        detail.querySelector("h2").textContent = card.getAttribute("data-stage-label") || "";
        detail.querySelector("p").textContent = card.getAttribute("data-stage-description") || "";
        const facts = detail.querySelectorAll(".fact-grid strong");
        if (facts[0]) facts[0].textContent = data.boundary || "UI boundary";
        if (facts[1]) facts[1].textContent = data.output || "Interpretable output";
        if (facts[2]) facts[2].textContent = data.risk || "Preserve constraints";
      }}
      history.replaceState(null, "", "/workflow?stage=" + encodeURIComponent(key));
    }});
  }});
}})();
</script>
</body>
</html>""".replace("__STAGE_META_JSON__", _stage_meta_json())


def _stage_card(key: str, label: str, description: str, index: int, active_index: int) -> str:
    state = "active" if index == active_index else "done" if index < active_index else "future"
    return f"""
    <a class="stage-card {state}" href="/workflow?stage={_escape(key)}" data-stage-key="{_escape(key)}"
       data-stage-label="{_escape(label)}" data-stage-description="{_escape(description)}">
      <span class="stage-index">{index + 1:02d}</span>
      <span><strong>{_escape(label)}</strong><span>{_escape(description)}</span></span>
    </a>
    """


def _active_index(active: str) -> int:
    return next((index for index, item in enumerate(WORKFLOW_NODES) if item[0] == active), 0)


def _stage_meta_json() -> str:
    import json

    return json.dumps(STAGE_META, ensure_ascii=False)


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
