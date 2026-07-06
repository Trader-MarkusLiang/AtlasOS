"""First-load onboarding overlay for Atlas OS UI."""

from __future__ import annotations


def render_onboarding_overlay() -> str:
    """Render the cognitive runtime onboarding modal."""

    return """
    <div id="onboarding-overlay" class="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div class="onboarding-card">
        <div class="panel-kicker">First Load</div>
        <h1 id="onboarding-title">Welcome to Atlas OS Runtime Cognitive System</h1>
        <p>
          Atlas OS runs a real-time cognitive loop. Every tick collects or simulates events,
          passes them through cognitive layers, and updates the visible system state.
        </p>
        <div class="onboarding-grid">
          <div>
            <strong>Probabilistic output</strong>
            <span>Outputs express current interpretation, confidence, and trust. They are not deterministic commands.</span>
          </div>
          <div>
            <strong>UNKNOWN</strong>
            <span>System has not yet converged on this metric or has no usable signal.</span>
          </div>
          <div>
            <strong>NEUTRAL</strong>
            <span>No strong regime signal is active. The runtime is observing rather than leaning.</span>
          </div>
        </div>
        <div class="boot-sequence" aria-live="polite">
          <div class="boot-step" data-step="0">Booting Atlas OS Cognitive Runtime...</div>
          <div class="boot-step" data-step="1">Initializing Event Stream...</div>
          <div class="boot-step" data-step="2">Loading Cognitive Layers...</div>
          <div class="boot-step" data-step="3">System Ready</div>
        </div>
        <div class="onboarding-actions">
          <button id="start-system-tour" class="control-button" type="button">Start System Tour</button>
          <a class="control-button secondary" href="/roadmap">View Roadmap</a>
          <button id="enter-dashboard" class="control-button secondary" type="button">Enter Dashboard</button>
        </div>
      </div>
    </div>
    """
