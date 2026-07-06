"""Right intelligence panel for Atlas OS UI v2.0."""

from __future__ import annotations

from ui.i18n.i18n import t


def render_intelligence_panel() -> str:
    """Render explanation-only intelligence context."""

    return f"""
    <aside class="v2-intelligence-panel" data-component="intelligence-panel">
      <section class="v2-intelligence-card primary">
        <div class="v2-section-title">{t("right.reasoning")}</div>
        <p id="decision-why">{t("empty.initializing")}</p>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">{t("right.causal")}</div>
        <div id="dominant-causal-factors" class="v2-causal-list" aria-live="polite"></div>
        <p id="causal-summary" class="v2-muted-copy">{t("empty.signal")}</p>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">{t("right.hypothesis")}</div>
        <dl class="v2-fact-grid">
          <dt>{t("right.active")}</dt><dd id="active-hypothesis">{t("empty.context")}</dd>
          <dt>{t("right.shadow")}</dt><dd id="shadow-hypothesis-count">0</dd>
        </dl>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">{t("right.health")}</div>
        <dl class="v2-fact-grid">
          <dt>{t("right.trust_trend")}</dt><dd id="trust-trend">{t("empty.signal")}</dd>
          <dt>{t("right.stability")}</dt><dd id="stability-index">{t("empty.context")}</dd>
          <dt>{t("right.llm_calls")}</dt><dd id="llm-call-count">0</dd>
          <dt>{t("model.model")}</dt><dd id="llm-model">{t("empty.signal")}</dd>
          <dt>{t("right.latency")}</dt><dd id="llm-latency">{t("empty.signal")}</dd>
        </dl>
      </section>

      <span id="decision-trace" class="v2-sr-only"></span>
      <span id="structural-state" class="v2-sr-only"></span>
      <span id="regime-influence" class="v2-sr-only">{t("empty.signal")}</span>
      <span id="trust-impact" class="v2-sr-only">{t("empty.signal")}</span>
    </aside>
    """
