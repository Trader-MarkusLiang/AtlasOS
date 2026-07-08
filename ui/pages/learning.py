"""Learning/accountability summary page."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import current_language, t


def render_learning_page(ledger: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    lang = current_language()
    metrics = ledger.get("metrics") if isinstance(ledger.get("metrics"), Mapping) else {}
    return f"""<!doctype html><html lang="{escape(lang)}"><head><meta charset="utf-8"><title>Atlas Learning</title><style>
body{{margin:0;background:#0b0f14;color:#edf2f7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.wrap{{max-width:980px;margin:0 auto;padding:30px 22px}}a{{color:#7dd3fc}}.card{{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:18px;background:rgba(255,255,255,.06);margin:14px 0}}</style></head>
<body><main class="wrap"><nav><a href="/">{escape(t("home.nav.home", lang))}</a> · <a href="/predictions">{escape(t("home.nav.predictions", lang))}</a></nav><h1>{escape(t("learning.title", lang))}</h1>
<section class="card"><h2>{escape(t("learning.prediction_error", lang))}</h2><p>{escape(t("learning.evaluated_forecasts", lang))}: {escape(str(metrics.get("evaluated")))} · {escape(t("learning.mean_forecast_error", lang))}: {escape(str(metrics.get("mean_forecast_error") or t("predictions.low_sample", lang)))}</p></section>
<section class="card"><h2>{escape(t("learning.calibration", lang))}</h2><p>{escape(t("learning.mean_calibration_error", lang))}: {escape(str(metrics.get("mean_calibration_error") or t("predictions.low_sample", lang)))}</p><p>{escape(str(ledger.get("sample_warning")))}</p></section>
<section class="card"><h2>{escape(t("learning.trust_state", lang))}</h2><p>{escape(t("learning.rolling_trust", lang))}: {escape(str(state.get("trust_index") or t("empty.signal", lang)))}</p></section>
</main></body></html>"""
