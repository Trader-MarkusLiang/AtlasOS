"""Decision Brief-first Atlas Home page."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping


def render_home_page(state: Mapping[str, Any]) -> str:
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    action = str(packet.get("recommended_action") or "neutral").upper()
    summary = str(packet.get("causal_summary") or "Atlas is waiting for sufficient cognitive signal.")
    channel_summary = _channel_summary(channels)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Home</title>
<style>
:root {{ color-scheme: dark; --bg:#0b0f14; --panel:rgba(255,255,255,.065); --line:rgba(255,255,255,.12); --text:#eef2f7; --muted:#99a3b3; --accent:#7dd3fc; --warn:#f8d66d; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:linear-gradient(140deg,#0b0f14,#111827 52%,#080b10); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
a {{ color:var(--accent); text-decoration:none; }}
.shell {{ max-width:1180px; margin:0 auto; padding:28px 22px 44px; }}
.nav {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:28px; }}
.nav a {{ padding:8px 12px; border:1px solid var(--line); border-radius:12px; background:rgba(255,255,255,.04); }}
.hero {{ min-height:330px; display:grid; align-content:center; gap:18px; padding:32px; border:1px solid var(--line); border-radius:22px; background:rgba(255,255,255,.07); box-shadow:0 24px 80px rgba(0,0,0,.35); }}
.kicker {{ color:var(--muted); font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }}
h1 {{ margin:0; font-size:clamp(2.4rem,6vw,5.4rem); letter-spacing:0; }}
.summary {{ max-width:760px; color:#d4dae4; font-size:1.08rem; line-height:1.55; }}
.grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-top:14px; }}
.card {{ min-height:150px; padding:18px; border:1px solid var(--line); border-radius:18px; background:var(--panel); }}
.card strong {{ display:block; margin-top:8px; font-size:1.2rem; }}
.wide {{ grid-column:span 2; }}
pre {{ margin:10px 0 0; max-height:230px; overflow:auto; white-space:pre-wrap; color:#d6deea; }}
@media (max-width:820px) {{ .grid {{ grid-template-columns:1fr; }} .wide {{ grid-column:auto; }} }}
</style>
</head>
<body>
<main class="shell">
  <nav class="nav">
    <a href="/">Home</a><a href="/dashboard">Ask Atlas</a><a href="/portfolio">Portfolio</a><a href="/markets">Markets</a>
    <a href="/predictions">Predictions</a><a href="/learning">Learning</a><a href="/workflow">Workflow</a><a href="/roadmap">Roadmap</a><a href="/settings">Settings</a>
  </nav>
  <section class="hero">
    <span class="kicker">Today&apos;s Atlas Brief</span>
    <h1>{escape(action)}</h1>
    <p class="summary">{escape(summary)}</p>
    <div class="summary">Trust: {escape(str(state.get("trust_index") or "Waiting for cognitive signal"))} · Regime: {escape(str(state.get("regime_state") or "Waiting for cognitive signal"))} · Last updated: {escape(str(state.get("timestamp") or ""))}</div>
  </section>
  <section class="grid">
    <article class="card">
      <span class="kicker">Current Market Context</span>
      <strong>{escape(str(market.get("status") or "Waiting for market refresh"))}</strong>
      <p>{escape(channel_summary)}</p>
    </article>
    <article class="card">
      <span class="kicker">Portfolio Impact</span>
      <strong>{escape(str(portfolio.get("status") or "No portfolio percentages configured"))}</strong>
      <p>Exposure sum: {escape(str(portfolio.get("exposure_sum_pct") or "Unknown"))}</p>
    </article>
    <article class="card">
      <span class="kicker">Data Freshness</span>
      <strong>{escape(str(market.get("timestamp") or "Unknown"))}</strong>
      <p>{escape(str(market.get("degraded", "Unknown")))}</p>
    </article>
    <article class="card wide">
      <span class="kicker">Trigger Conditions</span>
      <pre>{escape(json.dumps(packet.get("reasoning_trace") or "Show system details for raw trace.", ensure_ascii=False, indent=2))}</pre>
    </article>
    <article class="card">
      <span class="kicker">Top Risks</span>
      <strong>{escape(str(packet.get("risk_level") or "unknown"))}</strong>
      <p>Confidence: {escape(str(packet.get("confidence", 0.0)))}</p>
    </article>
  </section>
</main>
</body>
</html>"""


def _channel_summary(channels: Mapping[str, Any]) -> str:
    if not channels:
        return "Waiting for market channels."
    live = [key for key, value in channels.items() if str(value) == "LIVE"]
    simulated = [key for key, value in channels.items() if str(value) == "SIMULATED"]
    failed = [key for key, value in channels.items() if str(value) in {"FAILED", "RATE_LIMITED"}]
    missing = [key for key, value in channels.items() if str(value) == "NOT_CONFIGURED"]
    parts = []
    if live:
        parts.append("Live: " + ", ".join(live))
    if simulated:
        parts.append("Simulated: " + ", ".join(simulated))
    if failed:
        parts.append("Needs attention: " + ", ".join(failed))
    if missing:
        parts.append("Not configured: " + ", ".join(missing[:4]))
    return " · ".join(parts) or "Waiting for sufficient market signal."
