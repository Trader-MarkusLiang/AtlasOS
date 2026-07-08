"""Forecast ledger page."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_predictions_page(ledger: Mapping[str, Any]) -> str:
    lang = current_language()
    metrics = ledger.get("metrics") if isinstance(ledger.get("metrics"), Mapping) else {}
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(item.get('forecast_id')))}</td>"
        f"<td>{escape(str(item.get('status')))}</td>"
        f"<td>{escape(str(item.get('subject')))}</td>"
        f"<td>{escape(str(item.get('forecast_statement')))}</td>"
        f"<td>{escape(str(item.get('confidence')))}</td>"
        "</tr>"
        for item in ledger.get("forecasts", [])
        if isinstance(item, Mapping)
    )
    return f"""<!doctype html><html lang="{escape(lang)}"><head><meta charset="utf-8"><title>Atlas Predictions</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:1180px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}input,textarea,button{{font:inherit;border-radius:10px;border:1px solid rgba(255,255,255,.14);background:#101722;color:#edf2f7;padding:9px}}button{{background:#dbeafe;color:#0b0f14}}table{{width:100%;border-collapse:collapse}}td,th{{padding:9px;border-bottom:1px solid rgba(255,255,255,.1);text-align:left;vertical-align:top}}pre{{white-space:pre-wrap;overflow:auto}}</style></head>
<body><main class="wrap"><nav><a href="/">{escape(t("home.nav.home", lang))}</a> · <a href="/predictions?format=json">JSON</a></nav><h1>{escape(t("predictions.title", lang))}</h1>
<section class="card"><p>{escape(t("predictions.open", lang))}: <strong>{escape(str(metrics.get("open")))}</strong> · {escape(t("predictions.evaluated", lang))}: <strong>{escape(str(metrics.get("evaluated")))}</strong> · {escape(t("predictions.accuracy", lang))}: <strong>{escape(str(metrics.get("accuracy") or t("predictions.low_sample", lang)))}</strong></p><p>{escape(str(ledger.get("sample_warning")))}</p></section>
<section class="card"><h2>{escape(t("predictions.create", lang))}</h2><form id="forecast-form"><input name="subject" placeholder="subject"><input name="horizon" placeholder="horizon"><input name="expected_direction_state" placeholder="expected state"><input name="confidence" placeholder="0.0-1.0"><textarea name="forecast_statement" rows="3" placeholder="Non-price structural forecast"></textarea><button type="submit">{escape(t("predictions.record", lang))}</button></form><pre id="forecast-result"></pre></section>
<section class="card"><h2>{escape(t("predictions.ledger", lang))}</h2><table><thead><tr><th>ID</th><th>{escape(t("page.status", lang))}</th><th>Subject</th><th>Statement</th><th>{escape(t("state.confidence", lang))}</th></tr></thead><tbody>{rows}</tbody></table></section>
</main><script>
document.getElementById('forecast-form').addEventListener('submit', async (event) => {{
  event.preventDefault();
  const form = new FormData(event.target);
  const body = Object.fromEntries(form.entries());
  const response = await fetch('/predictions', {{method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(body)}});
  document.getElementById('forecast-result').textContent = JSON.stringify(await response.json(), null, 2);
}});
</script></body></html>"""
