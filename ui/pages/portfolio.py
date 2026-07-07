"""Portfolio context page."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping


def render_portfolio_page(context: Mapping[str, Any]) -> str:
    exposure = context.get("exposure_map") if isinstance(context.get("exposure_map"), Mapping) else {}
    themes = exposure.get("theme_concentration") if isinstance(exposure.get("theme_concentration"), Mapping) else {}
    bars = "\n".join(
        f'<div class="bar"><span>{escape(str(key))}</span><i style="width:{min(100, float(value or 0))}%"></i><strong>{escape(str(value))}%</strong></div>'
        for key, value in themes.items()
    ) or '<p>No portfolio percentages configured.</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Atlas Portfolio</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:1100px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}.bar{{display:grid;grid-template-columns:170px 1fr 70px;gap:10px;align-items:center;margin:10px 0}}.bar i{{height:10px;border-radius:999px;background:#7dd3fc}}pre{{white-space:pre-wrap;overflow:auto}}</style></head>
<body><main class="wrap"><nav><a href="/">Home</a> · <a href="/settings#asset-config">Edit assets</a></nav><h1>Portfolio Context</h1>
<section class="card"><p>Status: <strong>{escape(str(context.get("status")))}</strong> · Consistency: <strong>{escape(str(context.get("portfolio_consistency")))}</strong> · Exposure: <strong>{escape(str(context.get("exposure_sum_pct")))}%</strong></p><p>Privacy: {escape(str(context.get("privacy")))}</p></section>
<section class="card"><h2>Theme Concentration</h2>{bars}</section>
<section class="card"><h2>Exposure Map</h2><pre>{escape(json.dumps(exposure, ensure_ascii=False, indent=2))}</pre></section>
</main></body></html>"""
