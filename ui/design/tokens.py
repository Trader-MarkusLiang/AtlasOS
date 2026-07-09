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
.workflow-hero-panel {
  min-height: 260px;
  background:
    linear-gradient(135deg, rgba(219, 234, 254, 0.12), rgba(255, 255, 255, 0.045)),
    var(--surface);
}
.workflow-hero-actions {
  margin-top: 22px;
}
.workflow-priority-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  max-width: 980px;
  margin-top: 24px;
}
.workflow-priority-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  min-height: 92px;
  padding: 14px;
  border: 1px solid rgba(219, 234, 254, 0.16);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.052);
  transition: transform var(--fast), border-color var(--fast), background var(--fast);
}
.workflow-priority-item:hover {
  transform: translateY(-1px);
  border-color: rgba(219, 234, 254, 0.32);
  background: rgba(255,255,255,0.074);
}
.workflow-priority-item > span,
.workflow-section-label strong {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(219, 234, 254, 0.12);
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 780;
  flex: 0 0 auto;
}
.workflow-priority-item strong {
  display: block;
  line-height: 1.2;
}
.workflow-priority-item p {
  margin: 6px 0 0;
  color: var(--subtle);
  font-size: 0.88rem;
  line-height: 1.45;
}
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
.localized-hero-title,
.localized-action {
  display: grid;
  gap: 8px;
}
.localized-hero-title small,
.localized-action small,
.v2-regime-title small,
.v2-decision-line strong small,
.inline-dual small {
  display: block;
  color: var(--muted);
  font-size: clamp(0.86rem, 1.2vw, 1.02rem);
  font-weight: 640;
  line-height: 1.25;
}
.inline-dual {
  display: inline-grid;
  gap: 2px;
  vertical-align: middle;
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
.flow-summary-card,
.cognitive-flow-shell {
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: var(--surface);
  box-shadow: var(--shadow);
  backdrop-filter: blur(22px);
}
.flow-summary-card {
  padding: 20px 22px;
}
.flow-summary-card p {
  max-width: 940px;
  margin: 8px 0 0;
  color: var(--subtle);
  line-height: 1.55;
}
.workflow-map-section {
  display: grid;
  gap: 14px;
  scroll-margin-top: 96px;
}
.workflow-section-intro {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  max-width: 940px;
  padding: 4px 2px 0;
}
.workflow-section-label {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  margin-bottom: 10px;
  color: var(--subtle);
  font-size: 0.86rem;
  font-weight: 720;
}
.workflow-section-intro h2 {
  margin: 0;
  font-size: clamp(1.55rem, 2.6vw, 2.6rem);
  line-height: 1.08;
}
.workflow-section-intro p {
  margin: 0;
  color: var(--subtle);
  line-height: 1.55;
}
.cognitive-flow-shell {
  --flow-zoom: 1;
  --stage-input: #79b8ff;
  --stage-understand: #67e8f9;
  --stage-model: #c4b5fd;
  --stage-decide: #9ee6b8;
  --stage-learn: #f6d77a;
  padding: 16px;
}
.flow-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 14px;
}
.segmented-control,
.flow-zoom-controls {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 5px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255,255,255,0.035);
}
.segmented-control button,
.flow-zoom-controls button {
  min-height: 32px;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--subtle);
  cursor: pointer;
}
.segmented-control button[aria-pressed="true"],
.flow-zoom-controls button:hover {
  background: var(--accent);
  color: var(--bg);
}
.flow-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}
.flow-map-viewport {
  overflow: auto;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.018)),
    rgba(5, 8, 13, 0.42);
}
.flow-stage-grid {
  min-width: 840px;
  display: grid;
  grid-template-columns: repeat(5, minmax(150px, 1fr));
  gap: 10px;
  transform: scale(var(--flow-zoom));
  transform-origin: top left;
  width: calc(100% / var(--flow-zoom));
  transition: transform var(--fast);
}
.flow-stage {
  min-height: 528px;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.035);
}
.flow-stage-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-height: 74px;
}
.flow-stage-header > span {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 760;
}
.flow-stage-header h3 {
  margin: 0;
  font-size: 1.05rem;
}
.flow-stage-header p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.35;
}
.flow-stage-input { border-color: color-mix(in srgb, var(--stage-input) 34%, transparent); }
.flow-stage-understand { border-color: color-mix(in srgb, var(--stage-understand) 34%, transparent); }
.flow-stage-model { border-color: color-mix(in srgb, var(--stage-model) 34%, transparent); }
.flow-stage-decide { border-color: color-mix(in srgb, var(--stage-decide) 38%, transparent); }
.flow-stage-learn { border-color: color-mix(in srgb, var(--stage-learn) 40%, transparent); }
.flow-node-list,
.support-node-row {
  display: grid;
  gap: 8px;
  align-content: start;
}
.flow-node {
  position: relative;
  min-height: 58px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 9px;
  align-items: center;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.045);
  color: var(--text);
  text-align: left;
  cursor: pointer;
  transition: opacity var(--fast), border-color var(--fast), background var(--fast), transform var(--fast);
}
.flow-node:hover,
.flow-node:focus-visible {
  border-color: rgba(219, 234, 254, 0.45);
  background: rgba(219, 234, 254, 0.08);
  transform: translateY(-1px);
}
.flow-node-status {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--muted);
}
.flow-node-main {
  min-width: 0;
  display: grid;
  gap: 2px;
}
.flow-node-main strong {
  min-width: 0;
  overflow-wrap: anywhere;
  line-height: 1.15;
}
.flow-node-acronym {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
}
.flow-node-output {
  min-height: 78px;
  border-color: rgba(158, 230, 184, 0.48);
  background: rgba(158, 230, 184, 0.1);
}
.flow-node-support {
  background: rgba(148, 163, 184, 0.065);
}
.status-active {
  border-color: rgba(219, 234, 254, 0.62);
  box-shadow: 0 0 0 1px rgba(219, 234, 254, 0.12), 0 14px 32px rgba(0,0,0,0.18);
}
.status-active .flow-node-status {
  background: var(--accent);
  box-shadow: 0 0 0 5px rgba(219, 234, 254, 0.11);
  animation: activePulse 1.6s ease-in-out infinite;
}
.status-completed .flow-node-status { background: var(--positive); }
.status-waiting .flow-node-status { background: var(--muted); }
.status-degraded .flow-node-status { background: var(--warning); }
.status-failed .flow-node-status { background: var(--danger); }
.status-not_used .flow-node-status { background: rgba(148, 163, 184, 0.42); }
.flow-node.selected {
  border-color: var(--accent);
  background: rgba(219, 234, 254, 0.13);
}
.flow-node.upstream {
  border-color: rgba(103, 232, 249, 0.44);
  background: rgba(103, 232, 249, 0.075);
}
.flow-node.downstream {
  border-color: rgba(158, 230, 184, 0.44);
  background: rgba(158, 230, 184, 0.075);
}
.cognitive-flow-shell[data-selected-node]:not([data-selected-node=""]) .flow-node.unrelated {
  opacity: 0.34;
}
.cognitive-flow-shell[data-architecture-mode="latest"] .flow-node.not-current-path {
  opacity: 0.22;
}
.cognitive-flow-shell[data-architecture-mode="latest"] .support-shelf {
  display: none;
}
.cognitive-flow-shell[data-flow-mode="simple"] .flow-node-acronym {
  display: none;
}
.cognitive-flow-shell[data-flow-mode="expert"] .flow-node-acronym {
  display: inline;
  color: var(--accent);
}
.feedback-loop-strip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 54px;
  margin: 12px 4px 0;
  padding: 10px 14px;
  border: 1px solid rgba(246, 215, 122, 0.34);
  border-radius: var(--r16);
  background: rgba(246, 215, 122, 0.065);
  color: var(--subtle);
  text-align: center;
}
.feedback-loop-strip::before {
  content: "↺";
  color: var(--warning);
  font-size: 1.35rem;
}
.feedback-loop-strip::after {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  border: 1px solid rgba(246, 215, 122, 0.18);
  animation: feedbackTrace 2.6s ease-in-out infinite;
  pointer-events: none;
}
.support-shelf {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(148, 163, 184, 0.045);
}
.support-node-row {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 8px;
}
.support-node-row .flow-node {
  grid-template-columns: minmax(0, 1fr);
}
.support-node-row .flow-node-status {
  position: absolute;
  top: 10px;
  right: 10px;
}
.support-node-row .flow-node-main {
  padding-right: 18px;
}
.flow-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  color: var(--muted);
  font-size: 0.78rem;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  padding: 5px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255,255,255,0.035);
}
.legend-item i {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--muted);
}
.legend-active i { background: var(--accent); }
.legend-completed i { background: var(--positive); }
.legend-degraded i { background: var(--warning); }
.legend-failed i { background: var(--danger); }
.legend-feedback i { background: var(--warning); box-shadow: 0 0 0 4px rgba(246, 215, 122, 0.12); }
.legend-support i { background: #94a3b8; }
.flow-tooltip {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: calc(100% + 6px);
  z-index: 4;
  display: none;
  padding: 8px 9px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(6, 10, 16, 0.96);
  color: var(--subtle);
  font-size: 0.76rem;
  line-height: 1.35;
  box-shadow: var(--shadow);
}
.flow-node:hover .flow-tooltip,
.flow-node:focus-visible .flow-tooltip {
  display: block;
}
.flow-inspector {
  position: static;
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background: rgba(255,255,255,0.055);
}
.flow-inspector h2 {
  margin: 0;
  font-size: 1.25rem;
  overflow-wrap: anywhere;
}
.flow-inspector > p {
  margin: -4px 0 4px;
  color: var(--muted);
}
.flow-inspector-section {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.035);
}
.flow-inspector-section h3 {
  margin: 0 0 5px;
  color: var(--muted);
  font-size: 0.76rem;
  text-transform: uppercase;
}
.flow-inspector-section p,
.flow-inspector-section ul,
.flow-inspector-details p {
  margin: 0;
  color: var(--subtle);
  line-height: 1.42;
}
.flow-inspector-section ul {
  padding-left: 18px;
}
.flow-inspector-details {
  border: 1px solid var(--line);
  border-radius: var(--r12);
  padding: 10px;
  background: rgba(255,255,255,0.025);
}
.flow-inspector-details summary {
  cursor: pointer;
  color: var(--subtle);
}
@keyframes activePulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.25); opacity: 0.72; }
}
@keyframes feedbackTrace {
  0%, 100% { opacity: 0.24; }
  50% { opacity: 0.72; }
}
.architecture-card {
  min-height: auto;
  padding: 18px;
  border-color: rgba(219, 234, 254, 0.2);
  background:
    linear-gradient(180deg, rgba(219, 234, 254, 0.07), rgba(255, 255, 255, 0.035)),
    var(--surface-muted);
}
.architecture-card-primary {
  position: relative;
  overflow: hidden;
  scroll-margin-top: 96px;
  padding: 22px;
  border-color: rgba(219, 234, 254, 0.26);
  background:
    linear-gradient(135deg, rgba(219, 234, 254, 0.11), rgba(158, 230, 184, 0.045) 42%, rgba(255, 255, 255, 0.026)),
    var(--surface-muted);
}
.architecture-card-primary::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(255,255,255,0.08), transparent 24%);
  opacity: 0.34;
}
.architecture-card-primary > * {
  position: relative;
}
.architecture-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}
.architecture-card-header p {
  max-width: 760px;
  margin: 0;
}
.architecture-card-header h2 {
  font-size: clamp(1.35rem, 2.2vw, 2.35rem);
  line-height: 1.08;
}
.architecture-meta-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
.architecture-meta-pills span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 10px;
  border: 1px solid rgba(219, 234, 254, 0.18);
  border-radius: 999px;
  background: rgba(255,255,255,0.055);
  color: var(--text);
  font-size: 0.8rem;
  font-weight: 720;
}
.architecture-image-frame {
  display: block;
  overflow: auto;
  max-height: min(74vh, 780px);
  border: 1px solid rgba(219, 234, 254, 0.18);
  border-radius: var(--r16);
  background: rgba(4, 8, 14, 0.72);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 24px 70px rgba(0,0,0,0.22);
}
.architecture-image-frame img {
  display: block;
  width: 100%;
  min-width: 860px;
  height: auto;
}
.architecture-card-primary .architecture-image-frame {
  max-height: min(76vh, 840px);
  border-color: rgba(219, 234, 254, 0.24);
}
.architecture-lens {
  display: grid;
  grid-template-columns: minmax(190px, 0.52fr) minmax(0, 1.8fr);
  gap: 14px;
  align-items: stretch;
  margin-top: 14px;
  padding: 14px;
  border: 1px solid rgba(219, 234, 254, 0.14);
  border-radius: var(--r16);
  background: rgba(6, 12, 22, 0.42);
}
.architecture-lens h3 {
  max-width: 320px;
  margin: 7px 0 0;
  font-size: 1.05rem;
  line-height: 1.18;
}
.architecture-lens-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
}
.architecture-lens-card {
  min-height: 112px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 9px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.045);
}
.architecture-lens-card > span {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(219, 234, 254, 0.11);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 780;
}
.architecture-lens-card strong {
  display: block;
  line-height: 1.2;
  font-size: 0.88rem;
}
.architecture-lens-card p {
  margin: 6px 0 0;
  color: var(--subtle);
  font-size: 0.8rem;
  line-height: 1.42;
}
.workflow-reading-path {
  display: grid;
  grid-template-columns: minmax(220px, 0.72fr) minmax(0, 1.6fr);
  gap: 14px;
  align-items: stretch;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: var(--r16);
  background:
    linear-gradient(135deg, rgba(158, 230, 184, 0.075), rgba(219, 234, 254, 0.045)),
    rgba(255,255,255,0.035);
}
.workflow-reading-path h2 {
  max-width: 420px;
  margin: 7px 0 0;
  font-size: 1.25rem;
  line-height: 1.18;
}
.workflow-reading-path > div > p {
  max-width: 460px;
  margin: 10px 0 0;
  color: var(--subtle);
  font-size: 0.92rem;
  line-height: 1.48;
}
.workflow-reading-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
}
.workflow-reading-step {
  min-height: 124px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  padding: 13px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--r12);
  background: rgba(255,255,255,0.045);
}
.workflow-reading-step > span {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(219, 234, 254, 0.11);
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 780;
}
.workflow-reading-step strong {
  display: block;
  line-height: 1.2;
}
.workflow-reading-step p {
  margin: 6px 0 0;
  color: var(--subtle);
  font-size: 0.86rem;
  line-height: 1.42;
}
.architecture-entry-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}
.architecture-entry-card > div {
  min-width: min(100%, 420px);
  flex: 1;
}
.workflow-path-card {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.025)),
    var(--surface-muted);
}
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
.freshness-row span small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.28;
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
.localized-reason-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.localized-reason-list li {
  display: grid;
  gap: 5px;
}
.localized-reason-list strong {
  color: var(--text);
  font-size: 0.86rem;
}
.localized-reason-list span {
  color: var(--subtle);
  line-height: 1.48;
}
.factor-chip small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.68rem;
}
.tag small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.68rem;
}
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
  .atlas-shell { grid-template-columns: 1fr; }
  .atlas-sidebar {
    position: static;
    height: auto;
    padding: 14px;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
  .atlas-brand { padding-bottom: 10px; }
  .sidebar-nav { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .sidebar-status-card { margin-top: 10px; }
  .global-topbar {
    position: static;
    align-items: flex-start;
    flex-direction: column;
    padding: 14px;
  }
  .topbar-controls { justify-content: flex-start; }
  .workspace { grid-template-columns: 1fr; }
  .context-inspector { position: static; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .section-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .workflow-reading-path { grid-template-columns: 1fr; }
  .architecture-lens { grid-template-columns: 1fr; }
  .architecture-lens-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .flow-workspace { grid-template-columns: 1fr; }
  .flow-inspector { position: static; }
  .flow-stage-grid {
    min-width: 0;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .flow-stage-learn {
    grid-column: 1 / -1;
    min-height: auto;
  }
  .flow-stage { min-height: 420px; }
  .support-node-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .sidebar-nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .section-grid, .two-grid, .context-inspector, .form-grid { grid-template-columns: 1fr; }
  .workflow-priority-strip,
  .workflow-section-intro { grid-template-columns: 1fr; }
  .flow-toolbar { align-items: stretch; flex-direction: column; }
  .segmented-control, .flow-zoom-controls { border-radius: var(--r16); }
  .flow-stage-grid { grid-template-columns: 1fr; }
  .flow-stage { min-height: auto; }
  .support-node-row { grid-template-columns: 1fr; }
  .workflow-reading-steps { grid-template-columns: 1fr; }
  .architecture-lens-grid { grid-template-columns: 1fr; }
  .architecture-card-header { flex-direction: column; }
  .architecture-image-frame img { min-width: 760px; }
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
