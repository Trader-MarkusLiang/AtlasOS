"""Workflow graph visualization for Atlas OS UI."""

from __future__ import annotations

from typing import Any, Mapping


WORKFLOW_NODES = [
    ("event_stream", "Event Stream", "External input enters the safe runtime boundary."),
    ("cognitive_pipeline", "Cognitive Pipeline", "Fusion and memory convert events into system context."),
    ("causal_layer", "Causal Layer", "Causal structure explains how forces interact."),
    ("world_model", "World Model", "Market state evolves as an interpretable structure."),
    ("hypothesis_engine", "Hypothesis Engine", "Competing causal models are kept in view."),
    ("decision_contract", "Decision Contract", "Output is normalized into a strict packet."),
    ("llm_router", "LLM Router", "Reasoning provider is isolated behind the router."),
    ("feedback_loop", "Feedback Loop", "Bounded feedback updates the next tick context."),
]


def render_workflow_graph(active_stage: str = "event_stream") -> str:
    """Render clickable workflow nodes."""

    active = str(active_stage or "event_stream")
    active_index = next((index for index, item in enumerate(WORKFLOW_NODES) if item[0] == active), 0)
    nodes = "\n".join(
        f"""
        <a class="workflow-node {'active active-path' if key == active else 'active-path' if index <= active_index else 'inactive'}"
           href="/workflow?stage={key}" data-workflow-node="{key}" data-explanation="{_escape(description)}">
          <span>{label}</span>
        </a>
        """
        for index, (key, label, description) in enumerate(WORKFLOW_NODES)
    )
    selected = next((item for item in WORKFLOW_NODES if item[0] == active), WORKFLOW_NODES[0])
    return f"""
    <section class="workflow-graph-card" data-component="workflow-graph">
      <div class="card-heading">
        <span class="panel-kicker">Workflow</span>
        <h2>Minimal Active Path</h2>
      </div>
      <div class="workflow-graph" aria-label="Atlas workflow graph">
        {nodes}
      </div>
      <aside class="workflow-explanation" id="workflow-node-explanation">
        <strong>{_escape(selected[1])}</strong>
        <span>{_escape(selected[2])}</span>
      </aside>
    </section>
    """


def infer_active_workflow_stage(state: Mapping[str, Any] | None) -> str:
    """Infer a UI-only active stage from available display state."""

    data = state if isinstance(state, Mapping) else {}
    if data.get("last_decision_packet"):
        return "decision_contract"
    if data.get("trust_index") is not None:
        return "feedback_loop"
    if data.get("regime_state"):
        return "cognitive_pipeline"
    return "event_stream"


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
