"""Decision Brief-first Atlas Home page."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_home_page(state: Mapping[str, Any]) -> str:
    lang = current_language()
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    action = str(packet.get("recommended_action") or "neutral").upper()
    summary = str(packet.get("causal_summary") or t("home.waiting_summary", lang))
    channel_summary = _channel_summary(channels, lang)
    trigger_trace = str(packet.get("reasoning_trace") or t("home.trace_placeholder", lang))
    return f"""<!doctype html>
<html lang="{escape(lang)}">
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
    <a href="/">{escape(t("home.nav.home", lang))}</a><a href="/dashboard">{escape(t("home.nav.ask", lang))}</a><a href="/portfolio">{escape(t("home.nav.portfolio", lang))}</a><a href="/markets">{escape(t("home.nav.markets", lang))}</a>
    <a href="/predictions">{escape(t("home.nav.predictions", lang))}</a><a href="/learning">{escape(t("home.nav.learning", lang))}</a><a href="/workflow">{escape(t("nav.workflow", lang))}</a><a href="/roadmap">{escape(t("nav.roadmap", lang))}</a><a href="/settings">{escape(t("nav.settings", lang))}</a>
  </nav>
  <section class="hero">
    <span class="kicker">{escape(t("home.kicker", lang))}</span>
    <h1>{escape(action)}</h1>
    <p class="summary">{escape(summary)}</p>
    <div class="summary">{escape(t("home.trust", lang))}: {escape(str(state.get("trust_index") or t("empty.signal", lang)))} · {escape(t("home.regime", lang))}: {escape(str(state.get("regime_state") or t("empty.signal", lang)))} · {escape(t("home.updated", lang))}: {escape(str(state.get("timestamp") or ""))}</div>
  </section>
  <section class="grid">
    <article class="card">
      <span class="kicker">{escape(t("home.market_context", lang))}</span>
      <strong>{escape(str(market.get("status") or t("home.market_waiting", lang)))}</strong>
      <p>{escape(channel_summary)}</p>
    </article>
    <article class="card">
      <span class="kicker">{escape(t("home.portfolio_impact", lang))}</span>
      <strong>{escape(str(portfolio.get("status") or t("home.no_portfolio", lang)))}</strong>
      <p>{escape(t("home.exposure_sum", lang))}: {escape(str(portfolio.get("exposure_sum_pct") or t("empty.context", lang)))}</p>
    </article>
    <article class="card">
      <span class="kicker">{escape(t("home.data_freshness", lang))}</span>
      <strong>{escape(str(market.get("timestamp") or t("empty.context", lang)))}</strong>
      <p>{escape(str(market.get("degraded", t("empty.context", lang))))}</p>
    </article>
    <article class="card wide">
      <span class="kicker">{escape(t("home.trigger_conditions", lang))}</span>
      <pre>{escape(trigger_trace)}</pre>
    </article>
    <article class="card">
      <span class="kicker">{escape(t("home.top_risks", lang))}</span>
      <strong>{escape(str(packet.get("risk_level") or "unknown"))}</strong>
      <p>{escape(t("home.confidence", lang))}: {escape(str(packet.get("confidence", 0.0)))}</p>
    </article>
  </section>
</main>
</body>
</html>"""


def _channel_summary(channels: Mapping[str, Any], lang: str = "en") -> str:
    if not channels:
        return t("home.waiting_market", lang)
    live = [key for key, value in channels.items() if str(value) == "LIVE"]
    simulated = [key for key, value in channels.items() if str(value) == "SIMULATED"]
    failed = [key for key, value in channels.items() if str(value) in {"FAILED", "RATE_LIMITED"}]
    missing = [key for key, value in channels.items() if str(value) == "NOT_CONFIGURED"]
    parts = []
    if live:
        parts.append(f"{t('home.live', lang)}: " + ", ".join(live))
    if simulated:
        parts.append(f"{t('home.simulated', lang)}: " + ", ".join(simulated))
    if failed:
        parts.append(f"{t('home.needs_attention', lang)}: " + ", ".join(failed))
    if missing:
        parts.append(f"{t('home.not_configured', lang)}: " + ", ".join(missing[:4]))
    return " · ".join(parts) or t("home.waiting_signal", lang)
