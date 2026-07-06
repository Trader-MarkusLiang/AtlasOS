"""System state panel for the Atlas OS system interface."""

from __future__ import annotations


def render_system_state_panel() -> str:
    return """
    <aside class="panel left-panel" data-component="system-state-panel">
      <div class="panel-header">
        <span class="panel-kicker">State</span>
        <h2>System State</h2>
      </div>
      <div class="state-stack">
        <div class="metric primary">
          <span class="metric-label">Regime</span>
          <strong id="state-regime">Unknown</strong>
        </div>
        <div class="metric">
          <span class="metric-label">Trust Score</span>
          <strong id="state-trust">Unknown</strong>
          <div class="meter"><span id="trust-meter"></span></div>
        </div>
        <div class="metric-grid">
          <div class="metric">
            <span class="metric-label">Liquidity</span>
            <strong id="state-liquidity">Unknown</strong>
          </div>
          <div class="metric">
            <span class="metric-label">Attention</span>
            <strong id="state-attention">Unknown</strong>
          </div>
          <div class="metric">
            <span class="metric-label">Volatility</span>
            <strong id="state-volatility">Unknown</strong>
          </div>
          <div class="metric">
            <span class="metric-label">Tick</span>
            <strong id="state-tick">0</strong>
          </div>
        </div>
      </div>
    </aside>
    """

