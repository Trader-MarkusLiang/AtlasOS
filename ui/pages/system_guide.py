"""Read-only Atlas OS system guide page."""

from __future__ import annotations


def render_system_guide_page() -> str:
    """Render the human-readable guide for Atlas UI state semantics."""

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas OS System Guide</title>
<style>
:root {
  color-scheme: dark;
  --bg: #070a0f;
  --panel: rgba(15, 23, 35, 0.88);
  --line: rgba(148, 163, 184, 0.22);
  --text: #e6edf3;
  --muted: #94a3b8;
  --accent: #5eead4;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-width: 360px;
  background: linear-gradient(135deg, #070a0f 0%, #101622 48%, #090d14 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--accent); text-decoration: none; }
.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  background: rgba(5, 9, 15, 0.9);
}
.top h1 { margin: 0; font-size: 1.1rem; }
.top p { margin: 4px 0 0; color: var(--muted); }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; }
.tab {
  padding: 8px 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(15, 23, 35, 0.72);
}
.layout {
  display: grid;
  grid-template-columns: minmax(260px, 0.8fr) minmax(360px, 1.4fr);
  gap: 14px;
  padding: 14px;
}
.panel {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  overflow: hidden;
}
.panel h2 {
  margin: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
  font-size: 1rem;
}
.panel-body { padding: 14px 16px; }
.state-list { display: grid; gap: 10px; }
.state-item {
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 8px;
  background: rgba(2, 6, 12, 0.45);
}
.state-item strong { color: var(--accent); }
.state-item span { display: block; margin-top: 5px; color: #cbd5e1; }
.flow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.flow span {
  padding: 9px 11px;
  border: 1px solid rgba(94, 234, 212, 0.34);
  border-radius: 8px;
  background: rgba(94, 234, 212, 0.08);
}
ul { margin: 0; padding-left: 20px; color: #cbd5e1; }
li + li { margin-top: 7px; }
@media (max-width: 900px) {
  .top { align-items: flex-start; flex-direction: column; }
  .layout { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<header class="top">
  <div>
    <h1>Atlas OS System Guide</h1>
    <p>How to read the runtime interface without touching cognition or execution.</p>
  </div>
  <nav class="tabs" aria-label="Atlas UI tabs">
    <a class="tab" href="/dashboard">Dashboard</a>
    <a class="tab" href="/roadmap">Roadmap</a>
    <a class="tab" href="/dev-registry">Dev Registry</a>
    <a class="tab" href="/system-guide">System Guide</a>
  </nav>
</header>
<main class="layout">
  <section class="panel">
    <h2>What Is Atlas OS</h2>
    <div class="panel-body">
      <p>Atlas OS is a cognitive runtime system. It watches an event stream, fuses signals, updates
      memory, reasons through causal layers, and displays a non-binding decision packet.</p>
      <p>It is an event-driven inference engine, not a trading bot and not an execution system.</p>
    </div>
  </section>
  <section class="panel">
    <h2>State Meaning</h2>
    <div class="panel-body state-list">
      <div class="state-item"><strong>UNKNOWN</strong><span>Waiting for sufficient cognitive signal. The system has not yet converged on this metric.</span></div>
      <div class="state-item"><strong>NEUTRAL</strong><span>No strong regime signal is active. The runtime is observing.</span></div>
      <div class="state-item"><strong>ATTENTION</strong><span>Market attention or narrative pressure is elevated relative to baseline.</span></div>
      <div class="state-item"><strong>LIQUIDITY</strong><span>Capital depth, flow availability, or liquidity pressure is a key factor.</span></div>
      <div class="state-item"><strong>VOLATILITY</strong><span>Stress, dispersion, or instability is influencing the current interpretation.</span></div>
    </div>
  </section>
  <section class="panel">
    <h2>Decision Flow</h2>
    <div class="panel-body">
      <div class="flow" aria-label="Decision flow">
        <span>Event</span>
        <span>Cognitive Layers</span>
        <span>Decision</span>
        <span>Explanation</span>
        <span>Trust Update</span>
      </div>
    </div>
  </section>
  <section class="panel">
    <h2>What To Look At</h2>
    <div class="panel-body">
      <ul>
        <li>Regime: the current market-state interpretation.</li>
        <li>Trust score: how reliable the system thinks the current interpretation is.</li>
        <li>Decision trace: what packet was produced and why.</li>
        <li>Causal summary: which forces are driving the interpretation.</li>
      </ul>
    </div>
  </section>
</main>
</body>
</html>"""
