"""Market intelligence status page."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_markets_page(market_state: Mapping[str, Any]) -> str:
    lang = current_language()
    channels = market_state.get("channels") if isinstance(market_state.get("channels"), Mapping) else {}
    rows = "\n".join(
        f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>" for key, value in channels.items()
    )
    observations = market_state.get("observations") if isinstance(market_state.get("observations"), list) else []
    observation_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('source', '')))}</td>"
        f"<td>{escape(str(item.get('type', '')))}</td>"
        f"<td>{escape(str(item.get('timestamp', '')))}</td>"
        "</tr>"
        for item in observations[:12]
        if isinstance(item, Mapping)
    ) or f'<tr><td colspan="3">{escape(t("home.waiting_signal", lang))}</td></tr>'
    return f"""<!doctype html><html lang="{escape(lang)}"><head><meta charset="utf-8"><title>Atlas Markets</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:1100px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid rgba(255,255,255,.1);text-align:left}}pre{{white-space:pre-wrap;overflow:auto}}</style></head>
<body><main class="wrap"><nav><a href="/">{escape(t("home.nav.home", lang))}</a> · <a href="/dashboard">{escape(t("nav.dashboard", lang))}</a></nav><h1>{escape(t("markets.title", lang))}</h1>
<section class="card"><p>{escape(t("page.status", lang))}: <strong>{escape(str(market_state.get("status") or "not_run"))}</strong> · {escape(t("markets.degraded", lang))}: {escape(str(market_state.get("degraded", t("empty.context", lang))))} · {escape(t("markets.events", lang))}: {escape(str(market_state.get("events_enqueued", 0)))}</p></section>
<section class="card"><h2>{escape(t("markets.channel_status", lang))}</h2><table><thead><tr><th>{escape(t("markets.channel", lang))}</th><th>{escape(t("markets.state", lang))}</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="card"><h2>{escape(t("markets.latest_observations", lang))}</h2><table><thead><tr><th>{escape(t("markets.source", lang))}</th><th>{escape(t("markets.type", lang))}</th><th>{escape(t("markets.timestamp", lang))}</th></tr></thead><tbody>{observation_rows}</tbody></table></section>
</main></body></html>"""
