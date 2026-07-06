"""Event stream panel for the Atlas OS system interface."""

from __future__ import annotations


def render_event_stream_panel() -> str:
    return """
    <section class="panel stream-panel" data-component="event-stream-panel">
      <div class="panel-header stream-header">
        <div>
          <span class="panel-kicker">Stream</span>
          <h2>Real-Time Runtime Stream</h2>
        </div>
        <span id="stream-clock" class="stream-clock">Waiting</span>
      </div>
      <div id="event-stream" class="event-stream" role="log" aria-live="polite"></div>
    </section>
    """
