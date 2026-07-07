"""Market intelligence status page."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping


def render_markets_page(market_state: Mapping[str, Any]) -> str:
    channels = market_state.get("channels") if isinstance(market_state.get("channels"), Mapping) else {}
    rows = "\n".join(
        f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>" for key, value in channels.items()
    )
    observations = market_state.get("observations") if isinstance(market_state.get("observations"), list) else []
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Atlas Markets</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:1100px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid rgba(255,255,255,.1);text-align:left}}pre{{white-space:pre-wrap;overflow:auto}}</style></head>
<body><main class="wrap"><nav><a href="/">Home</a> · <a href="/dashboard">Dashboard</a></nav><h1>Market Intelligence</h1>
<section class="card"><p>Status: <strong>{escape(str(market_state.get("status") or "not_run"))}</strong> · Degraded: {escape(str(market_state.get("degraded", "Unknown")))} · Events enqueued: {escape(str(market_state.get("events_enqueued", 0)))}</p></section>
<section class="card"><h2>Channel Status</h2><table><tbody>{rows}</tbody></table></section>
<section class="card"><h2>Latest Observations</h2><pre>{escape(json.dumps(observations[:12], ensure_ascii=False, indent=2))}</pre></section>
</main></body></html>"""
