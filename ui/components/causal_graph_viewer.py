"""Causal graph overlay for the Atlas OS explainability interface."""

from __future__ import annotations


def render_causal_graph_viewer() -> str:
    return """
    <section id="causal-graph-overlay" class="explainability-overlay hidden" data-component="causal-graph-viewer">
      <div class="overlay-panel">
        <div class="overlay-header">
          <div>
            <span class="panel-kicker">Causal Graph</span>
            <h2>Cognitive Variable Relations</h2>
          </div>
          <button class="control-button secondary overlay-close" type="button" data-close-overlay>Close</button>
        </div>
        <div class="overlay-body graph-layout">
          <svg id="causal-graph-svg" class="explainability-svg" viewBox="0 0 720 420" role="img" aria-label="Causal graph"></svg>
          <div class="overlay-side">
            <h3>Drifted Edges</h3>
            <div id="causal-edge-list" class="mini-list"></div>
          </div>
        </div>
      </div>
    </section>
    """

