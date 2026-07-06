"""Inspector panel for the Atlas OS system interface."""

from __future__ import annotations


def render_inspector_panel() -> str:
    return """
    <aside class="panel right-panel" data-component="inspector-panel">
      <div class="panel-header">
        <span class="panel-kicker">Inspector</span>
        <h2>Runtime Trace</h2>
      </div>
      <section class="inspector-section">
        <h3>Latest LLM Trace</h3>
        <dl class="inline-facts">
          <dt>Calls</dt><dd id="llm-call-count">0</dd>
          <dt>Model</dt><dd id="llm-model">Unknown</dd>
          <dt>Latency</dt><dd id="llm-latency">Unknown</dd>
        </dl>
      </section>
      <section class="inspector-section">
        <h3>Why This Decision Happened</h3>
        <p id="decision-why">Waiting for DecisionPacket.</p>
      </section>
      <section class="inspector-section">
        <h3>Dominant Causal Factors</h3>
        <div id="dominant-causal-factors" class="factor-list"></div>
      </section>
      <section class="inspector-section">
        <h3>Regime + Trust Influence</h3>
        <dl class="inline-facts">
          <dt>Regime</dt><dd id="regime-influence">Unknown</dd>
          <dt>Trust</dt><dd id="trust-impact">Unknown</dd>
        </dl>
      </section>
      <section class="inspector-section">
        <h3>Decision Trace</h3>
        <pre id="decision-trace">{}</pre>
      </section>
      <section class="inspector-section">
        <h3>Causal Summary</h3>
        <p id="causal-summary">Unknown</p>
      </section>
      <section class="inspector-section">
        <h3>Structural Co-Evolution</h3>
        <pre id="structural-state">{}</pre>
      </section>
    </aside>
    """
