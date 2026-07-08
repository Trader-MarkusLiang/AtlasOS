"""Portfolio context page."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_portfolio_page(context: Mapping[str, Any]) -> str:
    lang = current_language()
    exposure = context.get("exposure_map") if isinstance(context.get("exposure_map"), Mapping) else {}
    themes = exposure.get("theme_concentration") if isinstance(exposure.get("theme_concentration"), Mapping) else {}
    bars = "\n".join(
        f'<div class="bar"><span>{escape(str(key))}</span><i style="width:{min(100, float(value or 0))}%"></i><strong>{escape(str(value))}%</strong></div>'
        for key, value in themes.items()
    ) or f'<p>{escape(t("portfolio.no_percentages", lang))}</p>'
    positions = context.get("positions") if isinstance(context.get("positions"), list) else []
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('asset', '')))}</td>"
        f"<td>{escape(str(item.get('market', '')))}</td>"
        f"<td>{escape(str(item.get('portfolio_percentage', '')))}%</td>"
        f"<td>{escape(str(item.get('role', '')))}</td>"
        f"<td>{escape(str(item.get('risk_note', '')))}</td>"
        f"<td>{escape(str(item.get('user_thesis', '')))}</td>"
        "</tr>"
        for item in positions
        if isinstance(item, Mapping)
    ) or f'<tr><td colspan="6">{escape(t("portfolio.no_percentages", lang))}</td></tr>'
    return f"""<!doctype html><html lang="{escape(lang)}"><head><meta charset="utf-8"><title>Atlas Portfolio</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:1100px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}.bar{{display:grid;grid-template-columns:170px 1fr 70px;gap:10px;align-items:center;margin:10px 0}}.bar i{{height:10px;border-radius:999px;background:#7dd3fc}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid rgba(255,255,255,.1);text-align:left;vertical-align:top}}</style></head>
<body><main class="wrap"><nav><a href="/">{escape(t("home.nav.home", lang))}</a> · <a href="/settings#asset-config">{escape(t("page.edit_assets", lang))}</a></nav><h1>{escape(t("portfolio.title", lang))}</h1>
<section class="card"><p>{escape(t("page.status", lang))}: <strong>{escape(str(context.get("status")))}</strong> · {escape(t("page.consistency", lang))}: <strong>{escape(str(context.get("portfolio_consistency")))}</strong> · {escape(t("page.exposure", lang))}: <strong>{escape(str(context.get("exposure_sum_pct")))}%</strong></p><p>{escape(t("page.privacy", lang))}: {escape(str(context.get("privacy")))}</p></section>
<section class="card"><h2>{escape(t("portfolio.theme_concentration", lang))}</h2>{bars}</section>
<section class="card"><h2>{escape(t("portfolio.positions", lang))}</h2><table><thead><tr><th>{escape(t("portfolio.asset", lang))}</th><th>{escape(t("portfolio.market", lang))}</th><th>{escape(t("portfolio.percentage", lang))}</th><th>{escape(t("portfolio.role", lang))}</th><th>{escape(t("portfolio.risk", lang))}</th><th>{escape(t("portfolio.thesis", lang))}</th></tr></thead><tbody>{rows}</tbody></table></section>
</main></body></html>"""
