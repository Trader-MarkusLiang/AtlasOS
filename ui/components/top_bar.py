"""Top bar component for the Atlas OS system interface."""

from __future__ import annotations


def render_top_bar() -> str:
    return """
    <header class="top-bar" data-component="top-bar">
      <div class="brand-block">
        <div class="brand-mark">ATLAS</div>
        <div>
          <div class="brand-title">Cognitive Control Center</div>
          <div class="brand-subtitle">Guided runtime intelligence</div>
        </div>
      </div>
      <div class="runtime-controls" aria-label="Runtime controls">
        <nav class="nav-tabs" aria-label="Atlas UI tabs">
          <a class="nav-tab" href="/dashboard">Dashboard</a>
          <a class="nav-tab" href="/workflow">Workflow</a>
          <a class="nav-tab" href="/roadmap">Roadmap</a>
          <a class="nav-tab" href="/settings">Settings</a>
        </nav>
        <span id="runtime-status-pill" class="status-pill status-unknown">INITIALIZING</span>
      </div>
    </header>
    """
