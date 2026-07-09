"""Context inspector for the Atlas Workflow cognitive flow map."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping


TEXT = {
    "en": {
        "title": "Context Inspector",
        "purpose": "Purpose",
        "inputs": "Receives",
        "outputs": "Produces",
        "status": "Current Status",
        "affects": "Affects",
        "details": "Technical Details",
        "tick": "Last active tick",
        "trust": "Trust / confidence",
        "brief": "Why it matters to Decision Brief",
    },
    "zh": {
        "title": "上下文检查器",
        "purpose": "作用",
        "inputs": "接收",
        "outputs": "产出",
        "status": "当前状态",
        "affects": "影响",
        "details": "技术细节",
        "tick": "最近活跃 Tick",
        "trust": "信任 / 置信度",
        "brief": "为什么影响决策简报",
    },
}


def render_workflow_inspector(node: Mapping[str, Any], lang: str) -> str:
    """Render the initial read-only context inspector."""

    labels = TEXT.get(lang, TEXT["en"])
    title = _clean(node.get("label"))
    acronym = _clean(node.get("acronym"))
    subtitle = f"{title} · {acronym}" if acronym else title
    return f"""
    <aside class="flow-inspector" data-flow-inspector aria-live="polite">
      <span class="kicker">{escape(labels["title"])}</span>
      <h2 data-inspector-title>{escape(title)}</h2>
      <p data-inspector-subtitle>{escape(subtitle)}</p>
      {_section("purpose", labels["purpose"], _clean(node.get("purpose")))}
      {_list_section("inputs", labels["inputs"], node.get("inputs"))}
      {_list_section("outputs", labels["outputs"], node.get("outputs"))}
      {_section("status", labels["status"], _clean(node.get("status_text")))}
      {_section("tick", labels["tick"], _clean(node.get("last_tick_text")))}
      {_section("trust", labels["trust"], _clean(node.get("trust_text")))}
      {_list_section("affects", labels["affects"], node.get("affects"))}
      {_section("brief", labels["brief"], _clean(node.get("brief_impact")))}
      <details class="flow-inspector-details">
        <summary>{escape(labels["details"])}</summary>
        <p data-inspector-technical>{escape(_clean(node.get("technical")))}</p>
      </details>
    </aside>
    """


def _section(key: str, label: str, value: str) -> str:
    return f"""
      <section class="flow-inspector-section" data-inspector-section="{escape(key)}">
        <h3>{escape(label)}</h3>
        <p data-inspector-{escape(key)}>{escape(value)}</p>
      </section>
    """


def _list_section(key: str, label: str, values: Any) -> str:
    items = values if isinstance(values, list) else []
    body = "".join(f"<li>{escape(_clean(item))}</li>" for item in items) or "<li>Unknown</li>"
    return f"""
      <section class="flow-inspector-section" data-inspector-section="{escape(key)}">
        <h3>{escape(label)}</h3>
        <ul data-inspector-{escape(key)}>{body}</ul>
      </section>
    """


def _clean(value: Any, fallback: str = "Unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback
