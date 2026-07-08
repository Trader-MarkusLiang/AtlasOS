"""Shared Atlas OS product shell."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping

from ui.components.context_inspector import render_context_inspector
from ui.components.global_sidebar import render_global_sidebar
from ui.components.global_topbar import render_global_topbar
from ui.design.tokens import DESIGN_CSS
from ui.i18n.i18n import current_language, t


def render_app_shell(
    *,
    active: str,
    content: str,
    state: Mapping[str, Any],
    title: str | None = None,
    inspector: str | None = None,
    include_inspector: bool = True,
    page_script: str = "",
) -> str:
    """Render one consistent product shell for all Atlas UI pages."""

    lang = current_language()
    page_title = title or t("app.title", lang)
    right = inspector if inspector is not None else render_context_inspector(state, lang)
    inspector_html = right if include_inspector else ""
    workspace_class = "workspace" if include_inspector else "workspace no-inspector"
    return f"""<!doctype html>
<html lang="{escape(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page_title)} - Atlas OS</title>
<style>{DESIGN_CSS}</style>
</head>
<body>
<div class="atlas-shell" data-active-page="{escape(active)}">
  {render_global_sidebar(active, state, lang)}
  <main class="atlas-main">
    {render_global_topbar(active, state, lang)}
    <div class="{workspace_class}">
      <div class="page-content">{content}</div>
      {inspector_html}
    </div>
    {render_execution_timeline(lang)}
  </main>
</div>
<script>
{SHELL_JS}
</script>
{page_script}
</body>
</html>"""


def render_execution_timeline(lang: str) -> str:
    steps = [
        ("event", t("flow.event", lang)),
        ("cognition", t("flow.cognition", lang)),
        ("decision", t("flow.decision", lang)),
        ("explanation", t("flow.explanation", lang)),
        ("feedback", t("flow.feedback", lang)),
    ]
    html = "\n".join(
        f'<div class="timeline-step{" active" if key in {"event", "decision"} else ""}" data-flow-step="{escape(key)}">{escape(label)}</div>'
        for key, label in steps
    )
    return f"""
    <section class="timeline-strip" aria-label="{escape(t("timeline.title", lang))}">
      <span class="kicker">{escape(t("timeline.kicker", lang))}</span>
      <div class="timeline-steps">{html}</div>
    </section>
    """


SHELL_JS = """
(function () {
  function text(selector, value) {
    document.querySelectorAll(selector).forEach(function (node) {
      node.textContent = value;
    });
  }
  function providerName(state) {
    return state && state.llm_provider_registry ? (state.llm_provider_registry.active_provider || "Waiting for signal") : "Waiting for signal";
  }
  function freshness(state) {
    const market = state && state.market_intelligence ? state.market_intelligence : {};
    return market.timestamp || (market.status === "not_run" ? "System initializing reasoning layer" : "Insufficient system context");
  }
  async function refreshTopbar() {
    try {
      const response = await fetch("/state", { cache: "no-store" });
      if (!response.ok) return;
      const state = await response.json();
      text("[data-provider-name]", providerName(state));
      text("[data-freshness]", freshness(state));
      text("[data-tick-counter]", state.tick_counter === undefined || state.tick_counter === null ? "Waiting for signal" : String(state.tick_counter));
      text("[data-trust-index]", typeof state.trust_index === "number" ? state.trust_index.toFixed(2) : "Waiting for signal");
      const runtime = state.runtime || {};
      const statusNode = document.querySelector("[data-runtime-status]");
      if (statusNode) {
        const status = String(runtime.status || "stopped").toLowerCase();
        statusNode.className = "status-pill status-" + status;
      }
    } catch (error) {
      const statusNode = document.querySelector("[data-runtime-status]");
      if (statusNode) statusNode.className = "status-pill status-error";
    }
  }
  const language = document.getElementById("global-language-select");
  if (language) {
    language.addEventListener("change", async function () {
      await fetch("/ui/language", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ language: language.value })
      });
      window.location.reload();
    });
  }
  setInterval(refreshTopbar, 2000);
})();
"""
