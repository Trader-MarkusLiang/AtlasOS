"""Learning/accountability summary page."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_learning_page(ledger: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    metrics = ledger.get("metrics") if isinstance(ledger.get("metrics"), Mapping) else {}
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Atlas Learning</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:980px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}</style></head>
<body><main class="wrap"><nav><a href="/">Home</a> · <a href="/predictions">Predictions</a></nav><h1>Learning & Accountability</h1>
<section class="card"><h2>Prediction Error</h2><p>Evaluated forecasts: {escape(str(metrics.get("evaluated")))} · Mean forecast error: {escape(str(metrics.get("mean_forecast_error") or "Low sample"))}</p></section>
<section class="card"><h2>Calibration</h2><p>Mean calibration error: {escape(str(metrics.get("mean_calibration_error") or "Low sample"))}</p><p>{escape(str(ledger.get("sample_warning")))}</p></section>
<section class="card"><h2>Trust State</h2><p>Rolling trust index: {escape(str(state.get("trust_index") or "Waiting for cognitive signal"))}</p></section>
</main></body></html>"""
