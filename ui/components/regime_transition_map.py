"""Regime transition overlay for the Atlas OS explainability interface."""

from __future__ import annotations


def render_regime_transition_map() -> str:
    return """
    <section id="regime-map-overlay" class="explainability-overlay hidden" data-component="regime-transition-map">
      <div class="overlay-panel">
        <div class="overlay-header">
          <div>
            <span class="panel-kicker">Regime Map</span>
            <h2>Attractors + Transition Pressure</h2>
          </div>
          <button class="control-button secondary overlay-close" type="button" data-close-overlay>Close</button>
        </div>
        <div class="overlay-body graph-layout">
          <svg id="regime-map-svg" class="explainability-svg" viewBox="0 0 720 420" role="img" aria-label="Regime transition map"></svg>
          <div class="overlay-side">
            <h3>Transition Weights</h3>
            <div id="regime-transition-list" class="mini-list"></div>
          </div>
        </div>
      </div>
    </section>
    """

