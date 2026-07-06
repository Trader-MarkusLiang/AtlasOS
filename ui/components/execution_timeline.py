"""Minimal execution timeline for Atlas OS UI v2.0."""

from __future__ import annotations


def render_execution_timeline() -> str:
    """Render a compressed Event -> Decision -> Feedback chain."""

    steps = [
        ("Event", "input received"),
        ("Cognition", "state interpreted"),
        ("Decision", "contract formed"),
        ("Explanation", "reasoning surfaced"),
        ("Feedback", "next tick context"),
    ]
    nodes = "\n".join(
        f"""
        <div class="v2-timeline-node" data-stage="{label.lower()}">
          <strong>{label}</strong>
          <span>{caption}</span>
        </div>
        """
        for label, caption in steps
    )
    return f"""
    <section class="v2-execution-timeline" data-component="execution-timeline">
      <div class="v2-timeline-header">
        <div>
          <span class="v2-kicker">Flow Timeline</span>
          <h2>Event -> Decision -> Feedback</h2>
        </div>
        <span id="stream-clock" class="v2-stream-clock">Waiting</span>
      </div>
      <div class="v2-timeline-chain" aria-label="Execution timeline stages">
        {nodes}
      </div>
      <div id="event-stream" class="v2-compressed-stream" role="log" aria-live="polite"></div>
    </section>
    """
