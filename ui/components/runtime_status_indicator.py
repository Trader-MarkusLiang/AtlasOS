"""Runtime status indicator component."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import t


def render_runtime_status_indicator(state: Mapping[str, Any], lang: str) -> str:
    runtime = state.get("runtime") if isinstance(state.get("runtime"), Mapping) else {}
    raw = str(runtime.get("status") or ("running" if runtime.get("running") is True else "stopped")).lower()
    status = raw if raw in {"running", "starting", "stopped", "degraded", "error"} else "degraded"
    label = {
        "running": t("status.running", lang),
        "starting": t("status.starting", lang),
        "stopped": t("status.stopped", lang),
        "degraded": t("status.degraded", lang),
        "error": t("status.error", lang),
    }.get(status, t("status.degraded", lang))
    return (
        f'<span class="status-pill status-{escape(status)}" data-runtime-status>'
        f'<i class="status-dot"></i>{escape(label)}</span>'
    )
