"""Right intelligence panel for Atlas OS UI v2.0."""

from __future__ import annotations


def render_intelligence_panel() -> str:
    """Render explanation-only intelligence context."""

    return """
    <aside class="v2-intelligence-panel" data-component="intelligence-panel">
      <section class="v2-intelligence-card primary">
        <div class="v2-section-title">Reasoning Summary</div>
        <p id="decision-why">System initializing reasoning layer</p>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">Causal Snapshot</div>
        <div id="dominant-causal-factors" class="v2-causal-list" aria-live="polite"></div>
        <p id="causal-summary" class="v2-muted-copy">Waiting for cognitive signal</p>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">Hypothesis State</div>
        <dl class="v2-fact-grid">
          <dt>Active</dt><dd id="active-hypothesis">Insufficient system context</dd>
          <dt>Shadow</dt><dd id="shadow-hypothesis-count">0</dd>
        </dl>
      </section>

      <section class="v2-intelligence-card">
        <div class="v2-section-title">System Health</div>
        <dl class="v2-fact-grid">
          <dt>Trust trend</dt><dd id="trust-trend">Waiting for cognitive signal</dd>
          <dt>Stability</dt><dd id="stability-index">Insufficient system context</dd>
          <dt>LLM calls</dt><dd id="llm-call-count">0</dd>
          <dt>Model</dt><dd id="llm-model">Waiting for cognitive signal</dd>
          <dt>Latency</dt><dd id="llm-latency">Waiting for cognitive signal</dd>
        </dl>
      </section>

      <section class="v2-intelligence-card compact">
        <div class="v2-section-title">Decision Trace</div>
        <pre id="decision-trace">{}</pre>
      </section>

      <section class="v2-intelligence-card compact">
        <div class="v2-section-title">Structural State</div>
        <pre id="structural-state">{}</pre>
      </section>

      <span id="regime-influence" class="v2-sr-only">Waiting for cognitive signal</span>
      <span id="trust-impact" class="v2-sr-only">Waiting for cognitive signal</span>
    </aside>
    """
