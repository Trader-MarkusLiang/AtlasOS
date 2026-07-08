"""Context inspector for Atlas product pages."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from ui.i18n.i18n import t


def render_context_inspector(state: Mapping[str, Any], lang: str) -> str:
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    portfolio = state.get("portfolio_context") if isinstance(state.get("portfolio_context"), Mapping) else {}
    dashboard = state.get("dashboard") if isinstance(state.get("dashboard"), Mapping) else {}
    causal = dashboard.get("causal_graph_snapshot") if isinstance(dashboard.get("causal_graph_snapshot"), Mapping) else {}
    factors = _top_factors(causal)
    summary = str(packet.get("causal_summary") or t("empty.signal", lang))
    hypothesis = _active_hypothesis(state, packet, lang)
    return f"""
    <aside class="context-inspector" aria-label="{escape(t("right.inspector", lang))}">
      <section class="panel">
        <span class="kicker">{escape(t("right.reasoning", lang))}</span>
        <h2>{escape(t("right.why", lang))}</h2>
        <p>{escape(summary)}</p>
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
        <p>{escape(t("portfolio.title", lang))}: {escape(str(portfolio.get("status") or t("empty.context", lang)))}</p>
      </section>
    </aside>
    """


def _top_factors(causal: Mapping[str, Any]) -> str:
    edges = causal.get("edges") if isinstance(causal.get("edges"), list) else []
    labels: list[str] = []
    for item in edges[:3]:
        if isinstance(item, Mapping):
            labels.append(str(item.get("from") or item.get("source") or item.get("name") or "causal factor"))
    if not labels:
        labels = ["attention", "liquidity", "volatility"]
    return "\n".join(f'<span class="tag">{escape(label)}</span>' for label in labels[:3])


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
