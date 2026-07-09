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
    const channels = market.channels || {};
    const observations = Array.isArray(market.observations) ? market.observations : [];
    const keys = Object.keys(channels);
    if (keys.length) {
      const live = keys.filter((key) => String(channels[key]).toUpperCase() === "LIVE").length;
      const failed = keys.filter((key) => ["FAILED", "RATE_LIMITED"].includes(String(channels[key]).toUpperCase())).length;
      const missing = keys.filter((key) => String(channels[key]).toUpperCase() === "NOT_CONFIGURED").length;
      const available = observations.filter((item) => item && ["Available", "Partial"].includes(item.data_quality_status)).length;
      const partial = observations.filter((item) => item && item.data_quality_status === "Partial").length;
      const zh = document.documentElement.lang === "zh";
      const prefix = observations.length ? (zh ? `价格 ${available}/${observations.length}` : `price ${available}/${observations.length}`) : (zh ? `${live} 实时` : `${live} live`);
      if (failed) return zh ? `${prefix} · ${failed} 失败` : `${prefix} · ${failed} failed`;
      if (partial) return zh ? `${prefix} · ${partial} 部分` : `${prefix} · ${partial} partial`;
      if (missing) return zh ? `${prefix} · ${missing} 未配置` : `${prefix} · ${missing} not configured`;
      return zh ? `${prefix} · 可用` : `${prefix} · available`;
    }
    return market.status === "not_run" ? "System initializing reasoning layer" : "Insufficient system context";
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
        const status = String(runtime.status || (runtime.running === true ? "running" : "stopped")).toLowerCase();
        statusNode.className = "status-pill status-" + status;
        const zh = document.documentElement.lang === "zh";
        const labels = zh
          ? { running: "运行中", starting: "启动中", stopped: "已停止", degraded: "降级", error: "错误" }
          : { running: "Running", starting: "Starting", stopped: "Stopped", degraded: "Degraded", error: "Error" };
        statusNode.innerHTML = '<i class="status-dot"></i>' + (labels[status] || labels.degraded);
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
  function activateViz(target) {
    if (!target) return;
    document.querySelectorAll("[data-viz-id]").forEach(function (node) {
      node.classList.remove("viz-selected");
      node.setAttribute("aria-pressed", "false");
    });
    target.classList.add("viz-selected");
    target.setAttribute("aria-pressed", "true");
    document.body.dataset.selectedViz = target.dataset.vizId || "";
    const question = target.dataset.vizQuestion || target.getAttribute("aria-label") || "Visualization";
    const feedback = target.querySelector("[data-viz-feedback]");
    if (feedback) feedback.textContent = question;
    const inspector = document.querySelector("[data-viz-global-feedback]");
    if (inspector) inspector.textContent = question;
  }
  document.addEventListener("click", function (event) {
    const target = event.target.closest && event.target.closest("[data-viz-id]");
    if (target) activateViz(target);
  });
  document.addEventListener("focusin", function (event) {
    const target = event.target.closest && event.target.closest("[data-viz-id]");
    if (target) activateViz(target);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Enter" && event.key !== " ") return;
    const target = event.target.closest && event.target.closest("[data-viz-id]");
    if (!target) return;
    event.preventDefault();
    activateViz(target);
    if (target.querySelector("[data-workflow-node]")) {
      const first = target.querySelector("[data-workflow-node]");
      if (first && first.dispatchEvent) first.dispatchEvent(new Event("click", { bubbles: true }));
    }
  });
  setInterval(refreshTopbar, 2000);
})();
"""
