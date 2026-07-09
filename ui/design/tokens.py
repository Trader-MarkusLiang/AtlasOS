"""Shared CSS tokens for the Atlas OS product UI."""

from __future__ import annotations


DESIGN_CSS = """
:root {
  color-scheme: dark;
  --bg: #0b0f14;
  --bg-soft: #10151d;
  --surface: rgba(255, 255, 255, 0.065);
  --surface-strong: rgba(255, 255, 255, 0.1);
  --surface-muted: rgba(255, 255, 255, 0.04);
  --line: rgba(255, 255, 255, 0.11);
  --line-strong: rgba(255, 255, 255, 0.2);
  --text: #f4f7fb;
  --muted: #9aa5b5;
  --subtle: #cbd5e1;
  --accent: #dbeafe;
  --positive: #9ee6b8;
  --warning: #f6d77a;
  --danger: #f4a5b3;
  --info: #9fd3ff;
  --r8: 8px;
  --r12: 12px;
  --r16: 16px;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.26);
  --fast: 160ms ease;
}
* { box-sizing: border-box; }
html, body { min-height: 100%; }
body {
  margin: 0;
  min-width: 360px;
  background:
    radial-gradient(circle at 14% 0%, rgba(148, 163, 184, 0.14), transparent 34%),
    radial-gradient(circle at 82% 10%, rgba(125, 211, 252, 0.08), transparent 30%),
    linear-gradient(180deg, #0b0f14 0%, #0d1219 52%, #080b10 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: 0;
}
a { color: inherit; text-decoration: none; }
button, input, select, textarea { font: inherit; }
button, a, input, select, textarea { outline-color: transparent; }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
  outline: 2px solid rgba(219, 234, 254, 0.8);
  outline-offset: 2px;
}
.atlas-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
}
.atlas-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 20px 14px;
  border-right: 1px solid var(--line);
  background: rgba(11, 15, 20, 0.74);
  backdrop-filter: blur(24px);
}
.atlas-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 8px 18px;
}
.atlas-brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: var(--r12);
  background: rgba(255, 255, 255, 0.08);
  font-weight: 760;
}
.atlas-brand strong, .atlas-brand span { display: block; }
.atlas-brand span { color: var(--muted); font-size: 0.78rem; margin-top: 2px; }
.sidebar-section {
  margin: 14px 0 8px;
  padding: 0 8px;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}
.sidebar-nav { display: grid; gap: 4px; }
.sidebar-link {
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid transparent;
  border-radius: var(--r12);
  color: var(--subtle);
  transition: background var(--fast), border-color var(--fast), color var(--fast);
}
.sidebar-link:hover { background: var(--surface-muted); border-color: var(--line); }
.sidebar-link.active { background: var(--accent); color: var(--bg); }
.sidebar-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.6;
}
.sidebar-status-card {
  margin: 18px 2px 0;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface-muted);
}
.sidebar-status-card span { display: block; color: var(--muted); font-size: 0.76rem; }
.sidebar-status-card strong { display: block; margin-top: 4px; overflow-wrap: anywhere; }
.atlas-main { min-width: 0; }
.global-topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  min-height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--line);
  background: rgba(11, 15, 20, 0.76);
  backdrop-filter: blur(22px);
}
.page-title-block strong { display: block; font-size: 0.98rem; }
.page-title-block span { display: block; margin-top: 2px; color: var(--muted); font-size: 0.82rem; }
.topbar-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}
.status-pill, .mini-pill {
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--subtle);
  font-size: 0.78rem;
}
.topbar-link:hover { border-color: var(--line-strong); background: var(--surface-strong); }
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--muted);
}
.status-running .status-dot { background: var(--positive); }
.status-error .status-dot, .status-stopped .status-dot { background: var(--danger); }
.status-degraded .status-dot, .status-starting .status-dot { background: var(--warning); }
.language-toggle {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 3px 8px 3px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--muted);
}
.language-toggle select {
  width: auto;
  min-height: 28px;
  border: 0;
  background: transparent;
  color: var(--text);
}
.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 330px);
  gap: 16px;
  padding: 20px 24px 0;
}
.workspace.no-inspector { grid-template-columns: 1fr; }
.page-content {
  min-width: 0;
  display: grid;
  gap: 16px;
}
.context-inspector {
  position: sticky;
  top: 88px;
  align-self: start;
  display: grid;
  gap: 12px;
}
.panel, .hero-panel, .focus-card {
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface);
  box-shadow: var(--shadow);
  backdrop-filter: blur(22px);
}
.hero-panel { min-height: 300px; padding: 28px; }
.focus-card { padding: 22px; }
.panel { padding: 16px; box-shadow: none; }
.kicker {
  color: var(--muted);
  font-size: 0.74rem;
  font-weight: 720;
  text-transform: uppercase;
}
.hero-title {
  max-width: 900px;
  margin: 12px 0 0;
  font-size: clamp(2.15rem, 4.4vw, 4.8rem);
  line-height: 1.02;
  font-weight: 760;
  overflow-wrap: anywhere;
  text-wrap: balance;
}
.hero-copy {
  max-width: 760px;
  margin: 16px 0 0;
  color: var(--subtle);
  font-size: 1rem;
  line-height: 1.58;
}
.section-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.two-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.metric-card {
  min-height: 116px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface-muted);
}
.metric-card span { display: block; color: var(--muted); font-size: 0.78rem; }
.metric-card strong { display: block; margin-top: 7px; font-size: 1.3rem; overflow-wrap: anywhere; }
.metric-card p { margin: 10px 0 0; color: var(--subtle); line-height: 1.45; }
.primary-decision {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: end;
}
.decision-action {
  margin: 8px 0 0;
  font-size: clamp(2.2rem, 5vw, 4.6rem);
  line-height: 0.95;
}
.gauge {
  width: 126px;
  height: 126px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background:
    conic-gradient(var(--accent) calc(var(--value, 0) * 1%), rgba(255,255,255,0.08) 0),
    rgba(255,255,255,0.05);
}
.gauge span {
  width: 98px;
  height: 98px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #0b0f14;
  color: var(--text);
  font-weight: 760;
}
.visual-card {
  min-height: 250px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface-muted);
  overflow: hidden;
}
.visual-card h2, .focus-card h2, .panel h2 { margin: 6px 0 10px; font-size: 1rem; }
.visual-card p, .panel p, .focus-card p { color: var(--subtle); line-height: 1.48; }
.atlas-viz {
  width: 100%;
  min-height: 160px;
  display: block;
}
.viz-frame {
  display: grid;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  border: 1px solid transparent;
  border-radius: var(--r12);
  background: rgba(255,255,255,0.025);
  transition: border-color var(--fast), background var(--fast), transform var(--fast);
}
.viz-frame:hover, .viz-frame:focus-visible, .viz-frame.viz-selected {
  border-color: rgba(219, 234, 254, 0.45);
  background: rgba(219, 234, 254, 0.055);
}
.viz-frame:focus-visible {
  outline: 2px solid rgba(219, 234, 254, 0.8);
  outline-offset: 2px;
}
.viz-question {
  color: var(--subtle);
  font-size: 0.82rem;
  line-height: 1.4;
}
.viz-feedback {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  color: var(--muted);
  font-size: 0.78rem;
}
.viz-selected .viz-feedback { color: var(--accent); }
.freshness-summary {
  margin-bottom: 10px;
  color: var(--subtle);
  font-weight: 700;
  line-height: 1.45;
}
.freshness-rows {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}
.freshness-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 8px;
  align-items: center;
  min-height: 34px;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(255, 255, 255, 0.035);
}
.freshness-row span,
.freshness-row strong,
.freshness-row em {
  min-width: 0;
  overflow-wrap: anywhere;
}
.freshness-row strong {
  color: var(--subtle);
  font-size: 0.78rem;
}
.freshness-row em {
  color: var(--muted);
  font-size: 0.76rem;
  font-style: normal;
}
.freshness-row.ok { border-color: rgba(158, 230, 184, 0.35); }
.freshness-row.warn { border-color: rgba(246, 215, 122, 0.35); }
.freshness-row.bad { border-color: rgba(244, 165, 179, 0.35); }
.pill-row { display: flex; flex-wrap: wrap; gap: 8px; }
.tag, .signal-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 9px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255,255,255,0.045);
  color: var(--subtle);
  font-size: 0.8rem;
}
.signal-live { color: var(--positive); border-color: rgba(158, 230, 184, 0.34); }
.signal-failed { color: var(--danger); border-color: rgba(244, 165, 179, 0.34); }
.signal-simulated { color: var(--warning); border-color: rgba(246, 215, 122, 0.34); }
.plain-list { margin: 8px 0 0; padding: 0; list-style: none; display: grid; gap: 8px; }
.plain-list li {
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.035);
  color: var(--subtle);
}
.expert-details {
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface-muted);
  overflow: hidden;
}
.expert-details summary {
  min-height: 46px;
  display: flex;
  align-items: center;
  padding: 12px 14px;
  cursor: pointer;
  color: var(--subtle);
}
.expert-details pre {
  margin: 0;
  padding: 14px;
  max-height: 320px;
  overflow: auto;
  border-top: 1px solid var(--line);
  white-space: pre-wrap;
  color: var(--subtle);
}
label { display: grid; gap: 6px; color: var(--muted); font-size: 0.82rem; }
input, select, textarea {
  width: 100%;
  min-height: 42px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(7, 10, 15, 0.8);
  color: var(--text);
}
textarea { resize: vertical; min-height: 96px; }
.button-row { display: flex; flex-wrap: wrap; gap: 8px; }
.primary-button, .secondary-button, .ghost-button {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 13px;
  border: 1px solid var(--line);
  border-radius: 999px;
  cursor: pointer;
}
.primary-button { background: var(--accent); color: var(--bg); }
.secondary-button { background: var(--surface-muted); color: var(--text); }
.ghost-button { background: transparent; color: var(--subtle); }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.asset-row {
  display: grid;
  grid-template-columns: 1fr 120px 120px 1fr auto;
  gap: 8px;
  align-items: end;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.035);
}
.timeline-strip {
  margin: 18px 24px 20px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface);
}
.timeline-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}
.timeline-step {
  min-height: 58px;
  display: grid;
  place-items: center;
  padding: 8px;
  border-radius: var(--r12);
  background: rgba(255,255,255,0.045);
  color: var(--subtle);
  text-align: center;
}
.timeline-step.active { background: var(--accent); color: var(--bg); }
.empty-state {
  min-height: 120px;
  display: grid;
  place-items: center;
  padding: 20px;
  border: 1px dashed var(--line);
  border-radius: var(--r16);
  color: var(--muted);
  background: rgba(255,255,255,0.025);
}
.loading-dots::after {
  content: "";
  animation: dots 1.4s infinite;
}
@keyframes dots {
  0% { content: ""; }
  33% { content: "."; }
  66% { content: ".."; }
  100% { content: "..."; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
}
@media (max-width: 1180px) {
  .workspace { grid-template-columns: 1fr; }
  .context-inspector { position: static; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .section-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .atlas-shell { grid-template-columns: 1fr; }
  .atlas-sidebar { position: static; height: auto; }
  .sidebar-nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .global-topbar { position: static; align-items: flex-start; flex-direction: column; }
  .section-grid, .two-grid, .context-inspector, .form-grid { grid-template-columns: 1fr; }
  .asset-row { grid-template-columns: 1fr; }
  .timeline-steps { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .workspace { padding: 14px; }
  .hero-panel { padding: 20px; }
  .hero-title { font-size: 2.45rem; }
  .primary-decision { grid-template-columns: 1fr; }
}
"""
