"""Context inspector for Atlas product pages."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import t
from ui.presentation.cognitive_localization import build_cognitive_presentation


def render_context_inspector(state: Mapping[str, Any], lang: str) -> str:
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    presentation = build_cognitive_presentation(state, lang)
    inspector = presentation.get("inspector") if isinstance(presentation.get("inspector"), Mapping) else {}
    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    factors = _top_factors(inspector, lang)
    sections = inspector.get("sections") if isinstance(inspector.get("sections"), list) else []
    summary = str(inspector.get("reasoning_summary") or packet.get("causal_summary") or t("empty.signal", lang))
    hypothesis = _active_hypothesis(state, packet, lang)
    return f"""
    <aside class="context-inspector" aria-label="{escape(t("right.inspector", lang))}">
      <section class="panel">
        <span class="kicker">{escape(t("right.reasoning", lang))}</span>
        <h2>{escape(t("right.why", lang))}</h2>
        {_reason_sections(sections, summary)}
      </section>
      <section class="panel">
        <span class="kicker">{escape(t("right.causal", lang))}</span>
        <h2>{escape(t("right.top_factors", lang))}</h2>
        <div class="pill-row">{factors}</div>
      </section>
      <section class="panel">
        <span class="kicker">{escape(t("right.hypothesis", lang))}</span>
        <h2>{escape(hypothesis)}</h2>
        <p>{escape(t("right.shadow_hint", lang))}: {escape(str(_shadow_count(state)))}</p>
      </section>
      <section class="panel">
        <span class="kicker">{escape(t("right.health", lang))}</span>
        <h2>{escape(t("state.trust_score", lang))}: {escape(_trust_text(state, lang))}</h2>
        <p>{escape(t("portfolio.title", lang))}: {escape(_portfolio_status(portfolio.get("status"), lang))}</p>
      </section>
      <section class="panel">
        <span class="kicker">{escape(t("right.inspector", lang))}</span>
        <h2>{escape(t("workflow.active_path", lang))}</h2>
        <p data-viz-global-feedback>{escape(t("viz.inspect_hint", lang))}</p>
      </section>
    </aside>
    """


def _top_factors(inspector: Mapping[str, Any], lang: str) -> str:
    factors = inspector.get("factors") if isinstance(inspector.get("factors"), list) else []
    labels: list[str] = []
    for item in factors[:3]:
        if isinstance(item, Mapping):
            primary = str(item.get("primary") or "")
            secondary = str(item.get("secondary") or "")
            if secondary:
                labels.append(f"{escape(primary)}<small>{escape(secondary)}</small>")
            else:
                labels.append(escape(primary))
    if not labels:
        labels = [escape(t("state.attention", lang)), escape(t("state.liquidity", lang)), escape(t("state.volatility", lang))]
    return "\n".join(f'<span class="tag">{label}</span>' for label in labels[:3])


def _reason_sections(sections: list[Any], fallback: str) -> str:
    if not sections:
        return f"<p>{escape(fallback)}</p>"
    items = []
    for item in sections[:3]:
        if not isinstance(item, Mapping):
            continue
        items.append(
            f'<li><strong>{escape(str(item.get("title") or ""))}</strong><span>{escape(str(item.get("body") or ""))}</span></li>'
        )
    return '<ul class="localized-reason-list">' + "".join(items) + "</ul>" if items else f"<p>{escape(fallback)}</p>"


def _active_hypothesis(state: Mapping[str, Any], packet: Mapping[str, Any], lang: str) -> str:
    coevolution = state.get("structural_coevolution_state") if isinstance(state.get("structural_coevolution_state"), Mapping) else {}
    value = coevolution.get("active_hypothesis") or packet.get("active_hypothesis")
    return str(value or t("empty.signal", lang))


def _shadow_count(state: Mapping[str, Any]) -> int:
    coevolution = state.get("structural_coevolution_state") if isinstance(state.get("structural_coevolution_state"), Mapping) else {}
    shadows = coevolution.get("shadow_hypotheses")
    return len(shadows) if isinstance(shadows, list) else 0


def _trust_text(state: Mapping[str, Any], lang: str) -> str:
    trust = state.get("trust_index")
    if isinstance(trust, (int, float)):
        return f"{float(trust):.2f}"
    return t("empty.signal", lang)


def _portfolio_status(value: Any, lang: str) -> str:
    status = str(value or "").lower()
    if status == "configured":
        return "已配置" if lang == "zh" else "Configured"
    if status in {"not_loaded", "missing", ""}:
        return t("empty.context", lang)
    return status.replace("_", " ").title()
