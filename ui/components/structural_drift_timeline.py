"""Structural drift timeline overlay for the Atlas OS explainability interface."""

from __future__ import annotations


def render_structural_drift_timeline() -> str:
    return """
    <section id="drift-timeline-overlay" class="explainability-overlay hidden" data-component="structural-drift-timeline">
      <div class="overlay-panel">
        <div class="overlay-header">
          <div>
            <span class="panel-kicker">Drift Timeline</span>
            <h2>Trust + Causal + Regime Stability</h2>
          </div>
          <button class="control-button secondary overlay-close" type="button" data-close-overlay>Close</button>
        </div>
        <div class="overlay-body timeline-layout">
          <svg id="drift-timeline-svg" class="timeline-svg" viewBox="0 0 920 320" role="img" aria-label="Structural drift timeline"></svg>
          <div id="drift-timeline-list" class="timeline-list"></div>
        </div>
      </div>
    </section>
    """

