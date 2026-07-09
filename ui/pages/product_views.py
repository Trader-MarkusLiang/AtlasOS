"""Product-grade Atlas OS page views.

These views are UI-only projections of existing runtime state. They do not
modify cognition, trading authority, portfolio state, or Decision Contract
semantics.
"""

from __future__ import annotations

import json
from html import escape
from typing import Any, Iterable, Mapping

from ui.components.cognitive_flow_map import render_cognitive_flow_map
from ui.i18n.i18n import current_language, t
from ui.presentation.cognitive_localization import (
    build_cognitive_presentation,
    localize_market_freshness,
    localize_proactive_update,
)


ATLAS_ACTIONS = {"observe", "hold", "reduce", "build", "accumulate"}
ARCHITECTURE_MAPS = {
    "en": "atlas-os-v2.2-architecture_en.png",
    "zh": "atlas-os-v2.2-architecture.png",
}


def home_content(state: Mapping[str, Any]) -> str:
    lang = current_language()
    presentation = build_cognitive_presentation(state, lang)
    hero = presentation["hero"]
    decision = presentation["decision"]
    packet = _packet(state)
    market = _market(state)
    portfolio = _portfolio(state)
    action = decision["action"]
    risk = decision["risk"]
    summary = str(hero.get("summary") or t("home.default_meaning", lang))
    triggers = [
        t("home.trigger_attention", lang),
        t("home.trigger_liquidity", lang),
        t("home.trigger_freshness", lang),
    ]
    invalidations = [
        t("home.invalid_no_data", lang),
        t("home.invalid_trust", lang),
        t("home.invalid_portfolio", lang),
    ]
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(str(hero.get("kicker") or t("home.today_change", lang)))}</span>
      <h1 class="hero-title localized-hero-title">{_dual_block(hero.get("title"), hero.get("secondary"))}</h1>
      <p class="hero-copy">{escape(summary)}</p>
      <div class="primary-decision" style="margin-top: 22px;">
        <div>
          <span class="kicker">{escape(t("home.current_view", lang))}</span>
          <div class="decision-action localized-action">{_dual_block(action.get("primary"), action.get("secondary"))}</div>
          <p class="hero-copy">{escape(t("state.risk", lang))}: {_inline_dual(risk)} · {escape(t("state.confidence", lang))}: {escape(str(decision.get("confidence") or _confidence(packet)))}</p>
        </div>
        {_gauge(_confidence_value(packet))}
      </div>
    </section>

    {_proactive_update_card(state, lang)}

    <section class="section-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("home.portfolio_meaning", lang))}</span>
        <h2>{escape(_portfolio_headline(portfolio, lang))}</h2>
        {_portfolio_minimap(portfolio)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("markets.trajectory", lang))}</span>
        <h2>{escape(t("markets.regime", lang))}</h2>
        {_regime_trajectory(state)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("home.data_freshness", lang))}</span>
        <h2>{escape(t("markets.data_health", lang))}</h2>
        {_freshness_map(market)}
      </article>
    </section>

    <section class="two-grid">
      <article class="focus-card">
        <span class="kicker">{escape(t("home.watch_next", lang))}</span>
        <ul class="plain-list">{_list_items(triggers)}</ul>
      </article>
      <article class="focus-card">
        <span class="kicker">{escape(t("home.invalidate", lang))}</span>
        <ul class="plain-list">{_list_items(invalidations)}</ul>
      </article>
    </section>

    <section class="visual-card">
      <span class="kicker">{escape(t("home.trust", lang))}</span>
      <h2>{escape(t("state.trust_score", lang))}</h2>
      {_trust_trend(state)}
    </section>

    <details class="expert-details">
      <summary>{escape(t("home.expert", lang))}</summary>
      <pre>{escape(json.dumps(_expert_payload(state), ensure_ascii=False, indent=2))}</pre>
    </details>
    """


def _dual_block(primary: Any, secondary: Any = "") -> str:
    primary_text = str(primary or "").strip()
    secondary_text = str(secondary or "").strip()
    if not secondary_text:
        return f"<span>{escape(primary_text)}</span>"
    return f"<span>{escape(primary_text)}</span><small>{escape(secondary_text)}</small>"


def _inline_dual(label: Mapping[str, Any]) -> str:
    primary = str(label.get("primary") or "").strip()
    secondary = str(label.get("secondary") or "").strip()
    if secondary:
        return f'<span class="inline-dual">{escape(primary)}<small>{escape(secondary)}</small></span>'
    return escape(primary)


def ask_content(state: Mapping[str, Any]) -> tuple[str, str]:
    lang = current_language()
    packet = _packet(state)
    suggestions = [
        "What changed today?",
        "Which holdings are most exposed?",
        "Why is Atlas cautious?",
        "Which predictions are still open?",
        "What did Atlas get wrong recently?",
        "What would make Atlas change its mind?",
    ]
    content = f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("page.ask", lang))}</span>
      <h1 class="hero-title">{escape(t("ask.prompt", lang))}</h1>
      <form id="atlas-chat-form" class="focus-card" style="margin-top: 22px;">
        <label>{escape(t("chat.placeholder", lang))}
          <textarea id="atlas-chat-input" rows="4" placeholder="{escape(t("ask.prompt", lang))}"></textarea>
        </label>
        <div class="button-row" style="margin-top: 12px;">
          <button class="primary-button" type="submit">{escape(t("chat.send", lang))}</button>
          <button class="secondary-button" type="button" id="atlas-clear-chat">{escape(t("ask.new", lang))}</button>
        </div>
        <p id="atlas-chat-status" class="hero-copy" role="status"></p>
      </form>
    </section>
    <section class="two-grid">
      <article class="focus-card">
        <span class="kicker">{escape(t("ask.suggested", lang))}</span>
        <div class="pill-row">{''.join(f'<button class="secondary-button suggested-prompt" type="button">{escape(item)}</button>' for item in suggestions)}</div>
      </article>
      <article class="focus-card">
        <span class="kicker">{escape(t("ask.response", lang))}</span>
        <h2>{escape(_safe_action(packet.get("recommended_action")))}</h2>
        <p>{escape(_clean(packet.get("causal_summary"), t("empty.signal", lang)))}</p>
        <div class="pill-row">
          <span class="tag">{escape(t("state.confidence", lang))}: {escape(_confidence(packet))}</span>
          <span class="tag">{escape(t("state.risk", lang))}: {escape(_clean(packet.get("risk_level"), t("empty.signal", lang)))}</span>
        </div>
      </article>
    </section>
    <section class="focus-card">
      <span class="kicker">{escape(t("ask.response", lang))}</span>
      <div id="atlas-chat-history" class="plain-list" aria-live="polite"></div>
    </section>
    """
    script = """
    <script>
    (function () {
      function msg(key) {
        const zh = document.documentElement.lang === "zh";
        const messages = {
          queued: zh ? "已进入下一次 runtime tick 队列。" : "Queued for the next runtime tick.",
          failed: zh ? "无法发送问题。" : "Could not queue message"
        };
        return messages[key] || key;
      }
      const form = document.getElementById("atlas-chat-form");
      const input = document.getElementById("atlas-chat-input");
      const status = document.getElementById("atlas-chat-status");
      const history = document.getElementById("atlas-chat-history");
      document.querySelectorAll(".suggested-prompt").forEach(function (button) {
        button.addEventListener("click", function () { input.value = button.textContent; input.focus(); });
      });
      document.getElementById("atlas-clear-chat").addEventListener("click", function () {
        input.value = "";
        history.innerHTML = "";
        status.textContent = "";
      });
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const message = input.value.trim();
        if (!message) return;
        status.textContent = msg("queued");
        const row = document.createElement("li");
        try {
          const response = await fetch("/chat/send", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ message })
          });
          const data = await response.json();
          row.textContent = response.ok ? message + " -> " + data.status : msg("failed");
        } catch (error) {
          row.textContent = msg("failed");
          status.textContent = msg("failed");
        }
        history.prepend(row);
        input.value = "";
      });
    })();
    </script>
    """
    return content, script


def portfolio_content(state: Mapping[str, Any]) -> str:
    lang = current_language()
    portfolio = _portfolio(state)
    exposure = portfolio.get("exposure_map") if isinstance(portfolio.get("exposure_map"), Mapping) else {}
    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("portfolio.summary", lang))}</span>
      <h1 class="hero-title">{escape(_portfolio_headline(portfolio, lang))}</h1>
      <p class="hero-copy">{escape(t("portfolio.market_impact", lang))}: {escape(_market_impact_summary(state, lang))}</p>
      <div class="section-grid" style="margin-top: 20px;">
        {_metric(t("page.exposure", lang), _pct_text(portfolio.get("exposure_sum_pct")), t("portfolio.no_percentages", lang))}
        {_metric("Unallocated", _pct_text(portfolio.get("cash_or_unassigned_pct")), t("empty.context", lang))}
        {_metric(t("portfolio.positions", lang), str(len(positions)), t("portfolio.summary", lang))}
      </div>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("portfolio.exposure_map", lang))}</span>
        <h2>{escape(t("portfolio.exposure_map", lang))}</h2>
        {_portfolio_bubbles(positions)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("portfolio.theme_concentration", lang))}</span>
        <h2>{escape(t("portfolio.theme_concentration", lang))}</h2>
        {_theme_bars(exposure.get("theme_concentration"))}
      </article>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("portfolio.risk_clusters", lang))}</span>
        <h2>{escape(t("portfolio.risk_clusters", lang))}</h2>
        {_risk_cluster_graph(exposure.get("correlated_risk_clusters"))}
      </article>
      <article class="focus-card">
        <span class="kicker">{escape(t("portfolio.positions", lang))}</span>
        <ul class="plain-list">{_position_rows(positions, lang)}</ul>
      </article>
    </section>
    <section class="focus-card">
      <span class="kicker">{escape(t("portfolio.edit", lang))}</span>
      <p>{escape(t("setup.assets_note", lang))}</p>
      <a class="primary-button" href="/settings#asset-config">{escape(t("portfolio.edit", lang))}</a>
    </section>
    """


def markets_content(state: Mapping[str, Any]) -> str:
    lang = current_language()
    market = _market(state)
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("markets.regime", lang))}</span>
      <h1 class="hero-title">{escape(_main_change(market, _packet(state), lang))}</h1>
      <p class="hero-copy">{escape(t("markets.what_changed", lang))}: {escape(_market_impact_summary(state, lang))}</p>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("markets.trajectory", lang))}</span>
        <h2>{escape(t("markets.trajectory", lang))}</h2>
        {_regime_trajectory(state)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("markets.attention_liquidity", lang))}</span>
        <h2>{escape(t("markets.attention_liquidity", lang))}</h2>
        {_attention_liquidity_phase(state)}
      </article>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("markets.theme_landscape", lang))}</span>
        <h2>{escape(t("markets.theme_landscape", lang))}</h2>
        {_theme_landscape(state)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("markets.data_health", lang))}</span>
        <h2>{escape(t("markets.channel_status", lang))}</h2>
        {_freshness_map(market)}
      </article>
    </section>
    <section class="focus-card">
      <span class="kicker">{escape(t("markets.latest_observations", lang))}</span>
      <div class="pill-row">{_channel_pills(channels)}</div>
    </section>
    """


def predictions_content(ledger: Mapping[str, Any]) -> str:
    lang = current_language()
    metrics = ledger.get("metrics") if isinstance(ledger.get("metrics"), Mapping) else {}
    forecasts = ledger.get("forecasts") if isinstance(ledger.get("forecasts"), list) else []
    open_items = [item for item in forecasts if isinstance(item, Mapping) and item.get("status") == "OPEN"]
    misses = [item for item in forecasts if isinstance(item, Mapping) and item.get("status") == "INVALIDATED"]
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("predictions.title", lang))}</span>
      <h1 class="hero-title">{escape(t("predictions.outcomes", lang))}</h1>
      <p class="hero-copy">{escape(str(ledger.get("sample_warning") or t("predictions.low_sample", lang)))}</p>
      <div class="section-grid" style="margin-top: 20px;">
        {_metric(t("predictions.open", lang), _compact(metrics.get("open")), t("predictions.open_predictions", lang))}
        {_metric(t("predictions.evaluated", lang), _compact(metrics.get("evaluated")), t("predictions.outcomes", lang))}
        {_metric(t("predictions.accuracy", lang), _compact(metrics.get("accuracy"), t("predictions.low_sample", lang)), t("predictions.reliability", lang))}
      </div>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("predictions.calibration", lang))}</span>
        <h2>{escape(t("predictions.calibration", lang))}</h2>
        {_calibration_chart(forecasts)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("predictions.timeline", lang))}</span>
        <h2>{escape(t("predictions.timeline", lang))}</h2>
        {_forecast_timeline(forecasts)}
      </article>
    </section>
    <section class="two-grid">
      <article class="focus-card">
        <span class="kicker">{escape(t("predictions.open_predictions", lang))}</span>
        <ul class="plain-list">{_forecast_rows(open_items[:5], empty=t("empty.signal", lang))}</ul>
      </article>
      <article class="focus-card">
        <span class="kicker">{escape(t("predictions.misses", lang))}</span>
        <ul class="plain-list">{_forecast_rows(misses[:5], empty=t("predictions.low_sample", lang))}</ul>
      </article>
    </section>
    """


def learning_content(ledger: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    lang = current_language()
    forecasts = ledger.get("forecasts") if isinstance(ledger.get("forecasts"), list) else []
    evaluated = [item for item in forecasts if isinstance(item, Mapping) and item.get("status") in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}]
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("learning.changed_mind", lang))}</span>
      <h1 class="hero-title">{escape(t("learning.flow", lang))}</h1>
      <p class="hero-copy">{escape(str(ledger.get("sample_warning") or t("predictions.low_sample", lang)))}</p>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">{escape(t("learning.trust_timeline", lang))}</span>
        <h2>{escape(t("learning.trust_timeline", lang))}</h2>
        {_trust_trend(state)}
      </article>
      <article class="visual-card">
        <span class="kicker">{escape(t("learning.hypothesis", lang))}</span>
        <h2>{escape(t("learning.hypothesis", lang))}</h2>
        {_hypothesis_competition(state)}
      </article>
    </section>
    <section class="visual-card">
      <span class="kicker">{escape(t("learning.flow", lang))}</span>
      <h2>{escape(t("learning.changed_mind", lang))}</h2>
      {_learning_flow(evaluated[:4], lang)}
    </section>
    """


def workflow_content(state: Mapping[str, Any]) -> tuple[str, str]:
    lang = current_language()
    flow_html, flow_script = render_cognitive_flow_map(state, lang)
    content = f"""
    <section class="hero-panel workflow-hero-panel">
      <span class="kicker">{escape(t("architecture.kicker", lang))}</span>
      <h1 class="hero-title">{escape(t("workflow.hero_title", lang))}</h1>
      <p class="hero-copy">{escape(t("workflow.hero_copy", lang))}</p>
      <div class="button-row workflow-hero-actions">
        <a class="primary-button" href="#architecture-map">{escape(t("workflow.jump_architecture", lang))}</a>
        <a class="secondary-button" href="#cognitive-flow-map">{escape(t("workflow.jump_path", lang))}</a>
      </div>
      {_workflow_priority_strip(lang)}
    </section>
    {_architecture_map(lang)}
    {_workflow_reading_path(lang)}
    <section class="workflow-map-section" id="cognitive-flow-map" aria-labelledby="workflow-global-map-title">
      <div class="workflow-section-intro">
        <span class="workflow-section-label"><strong>02</strong>{escape(t("workflow.step_map_title", lang))}</span>
        <div>
          <span class="kicker">{escape(t("workflow.interactive_map", lang))}</span>
          <h2 id="workflow-global-map-title">{escape(t("workflow.map_title", lang))}</h2>
          <p>{escape(t("workflow.path_copy", lang))}</p>
        </div>
      </div>
      {flow_html}
    </section>
    """
    return content, flow_script


def _workflow_priority_strip(lang: str) -> str:
    cards = [
        ("01", t("workflow.step_overview_title", lang), t("workflow.priority_architecture", lang), "#architecture-map"),
        ("02", t("workflow.step_map_title", lang), t("workflow.priority_map", lang), "#cognitive-flow-map"),
    ]
    items = "".join(
        f"""
        <a class="workflow-priority-item" href="{escape(href)}">
          <span>{escape(number)}</span>
          <div>
            <strong>{escape(title)}</strong>
            <p>{escape(copy)}</p>
          </div>
        </a>
        """
        for number, title, copy, href in cards
    )
    return f"""
    <nav class="workflow-priority-strip" aria-label="{escape(t("workflow.reading_path", lang))}">
      {items}
    </nav>
    """


def roadmap_content(payload: Mapping[str, Any]) -> str:
    lang = current_language()
    tracks = payload.get("tracks") if isinstance(payload.get("tracks"), list) else []
    layers = payload.get("layers") if isinstance(payload.get("layers"), list) else []
    current = _clean(payload.get("current_stage"), "Production Trial Candidate")
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("roadmap.swimlanes", lang))}</span>
      <h1 class="hero-title">{escape(_roadmap_title(current))}</h1>
      <p class="hero-copy">{escape(t("roadmap.why", lang))}: Atlas Core, Runtime, UI, Cognitive Overlay, and Data mature independently; evidence level matters more than a single version label.</p>
    </section>
    <section class="visual-card">
      <span class="kicker">{escape(t("roadmap.swimlanes", lang))}</span>
      <h2>{escape(t("roadmap.swimlanes", lang))}</h2>
      {_roadmap_swimlanes(tracks, layers)}
    </section>
    <section class="two-grid">
      <article class="focus-card">
        <span class="kicker">{escape(t("roadmap.why", lang))}</span>
        <p>{escape(str(payload.get("next_stage") or t("empty.context", lang)))}</p>
      </article>
      <article class="focus-card">
        <span class="kicker">Evidence</span>
        <ul class="plain-list">{_roadmap_layer_rows(layers[:6])}</ul>
      </article>
    </section>
    {_architecture_entry_card(lang)}
    """


def _architecture_map(lang: str) -> str:
    selected = ARCHITECTURE_MAPS.get(lang, ARCHITECTURE_MAPS["en"])
    english = ARCHITECTURE_MAPS["en"]
    chinese = ARCHITECTURE_MAPS["zh"]
    title = t("architecture.title", lang)
    subtitle = t("architecture.subtitle", lang)
    lenses = [
        ("01", t("workflow.lens_surface_title", lang), t("workflow.lens_surface_copy", lang)),
        ("02", t("workflow.lens_cognition_title", lang), t("workflow.lens_cognition_copy", lang)),
        ("03", t("workflow.lens_decision_title", lang), t("workflow.lens_decision_copy", lang)),
        ("04", t("workflow.lens_feedback_title", lang), t("workflow.lens_feedback_copy", lang)),
    ]
    lens_cards = "".join(
        f"""
        <article class="architecture-lens-card">
          <span>{escape(number)}</span>
          <div>
            <strong>{escape(label)}</strong>
            <p>{escape(copy)}</p>
          </div>
        </article>
        """
        for number, label, copy in lenses
    )
    return f"""
    <section class="visual-card architecture-card architecture-card-primary" id="architecture-map">
      <div class="architecture-card-header">
        <div>
          <span class="workflow-section-label"><strong>01</strong>{escape(t("workflow.step_overview_title", lang))}</span>
          <span class="kicker">{escape(t("architecture.kicker", lang))}</span>
          <h2>{escape(title)}</h2>
          <p>{escape(subtitle)}</p>
          <div class="architecture-meta-pills" aria-label="{escape(t("architecture.kicker", lang))}">
            <span>{escape(t("architecture.current_map", lang))}</span>
            <span>{escape(t("architecture.version_badge", lang))}</span>
          </div>
        </div>
        <div class="button-row">
          <a class="secondary-button" href="/assets/{escape(chinese)}" target="_blank" rel="noopener">{escape(t("architecture.open_cn", lang))}</a>
          <a class="secondary-button" href="/assets/{escape(english)}" target="_blank" rel="noopener">{escape(t("architecture.open_en", lang))}</a>
        </div>
      </div>
      <a class="architecture-image-frame" href="/assets/{escape(selected)}" target="_blank" rel="noopener" aria-label="{escape(title)}">
        <img src="/assets/{escape(selected)}" alt="{escape(title)}" loading="lazy">
      </a>
      <div class="architecture-lens">
        <div>
          <span class="kicker">{escape(t("workflow.map_lens", lang))}</span>
          <h3>{escape(t("workflow.map_lens_title", lang))}</h3>
        </div>
        <div class="architecture-lens-grid">{lens_cards}</div>
      </div>
    </section>
    """


def _workflow_reading_path(lang: str) -> str:
    steps = [
        ("01", t("workflow.step_overview_title", lang), t("workflow.step_overview_copy", lang)),
        ("02", t("workflow.step_map_title", lang), t("workflow.step_map_copy", lang)),
        ("03", t("workflow.step_inspector_title", lang), t("workflow.step_inspector_copy", lang)),
    ]
    cards = "".join(
        f"""
        <article class="workflow-reading-step">
          <span>{escape(number)}</span>
          <div>
            <strong>{escape(title)}</strong>
            <p>{escape(copy)}</p>
          </div>
        </article>
        """
        for number, title, copy in steps
    )
    return f"""
    <section class="workflow-reading-path" aria-label="{escape(t("workflow.reading_path", lang))}">
      <div>
        <span class="kicker">{escape(t("workflow.reading_path", lang))}</span>
        <h2>{escape(t("workflow.reading_title", lang))}</h2>
        <p>{escape(t("workflow.reading_copy", lang))}</p>
      </div>
      <div class="workflow-reading-steps">{cards}</div>
    </section>
    """


def _architecture_entry_card(lang: str) -> str:
    selected = ARCHITECTURE_MAPS.get(lang, ARCHITECTURE_MAPS["en"])
    return f"""
    <section class="focus-card architecture-entry-card">
      <div>
        <span class="kicker">{escape(t("architecture.kicker", lang))}</span>
        <h2>{escape(t("architecture.title", lang))}</h2>
        <p>{escape(t("architecture.roadmap_hint", lang))}</p>
      </div>
      <a class="primary-button" href="/workflow#architecture-map">{escape(t("architecture.view_in_workflow", lang))}</a>
      <a class="secondary-button" href="/assets/{escape(selected)}" target="_blank" rel="noopener">{escape(t("architecture.open_full", lang))}</a>
    </section>
    """


def dev_registry_content(roadmap: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    lang = current_language()
    layers = roadmap.get("layers") if isinstance(roadmap.get("layers"), list) else []
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("registry.history", lang))}</span>
      <h1 class="hero-title">{escape(t("registry.history", lang))}</h1>
      <p class="hero-copy">Project progress is summarized as capability evolution, validation evidence, and current maturity instead of raw commit logs.</p>
    </section>
    <section class="two-grid">
      <article class="visual-card">
        <span class="kicker">Capability Evolution</span>
        <h2>Capability Evolution</h2>
        {_capability_evolution(layers)}
      </article>
      <article class="visual-card">
        <span class="kicker">Validation History</span>
        <h2>Validation History</h2>
        {_validation_history(layers)}
      </article>
    </section>
    <section class="focus-card">
      <span class="kicker">{escape(t("state.status", lang))}</span>
      <div class="section-grid">
        {_metric("Active", _clean(roadmap.get("active_version") or roadmap.get("current_stage"), t("empty.context", lang)), "Current stage")}
        {_metric("Trust", _compact(state.get("trust_index"), t("empty.signal", lang)), "Runtime trust")}
        {_metric("Regime", _clean(state.get("regime_state"), t("empty.signal", lang)), "Runtime state")}
      </div>
    </section>
    """


def settings_content(config: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[str, str]:
    lang = current_language()
    registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    providers = registry.get("providers") if isinstance(registry.get("providers"), list) else []
    active = str(registry.get("active_provider") or "")
    system = config.get("system") if isinstance(config.get("system"), Mapping) else {}
    assets = config.get("assets") if isinstance(config.get("assets"), Mapping) else {}
    positions = _config_positions(assets)
    available = [p for p in providers if isinstance(p, Mapping) and str(p.get("health")) in {"healthy", "reachable"}]
    other = [p for p in providers if isinstance(p, Mapping) and p not in available]
    content = f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("page.settings", lang))}</span>
      <h1 class="hero-title">{escape(t("settings.providers_clean", lang))}</h1>
      <p class="hero-copy">{escape(t("settings.notice", lang))}</p>
    </section>
    <section id="provider-config" class="focus-card">
      <span class="kicker">{escape(t("settings.providers", lang))}</span>
      <div class="section-grid">
        {_metric(t("provider.online", lang), f"{len(available)}/{len(providers)}", t("model.health", lang))}
        {_metric(t("model.active_provider", lang), active or t("empty.context", lang), t("settings.fallback", lang))}
        {_metric(t("provider.fastest", lang), _fastest_provider(available, lang), t("provider.latency", lang))}
      </div>
      <label style="margin-top: 14px;">{escape(t("model.active_provider", lang))}
        <select id="settings-active-provider">{_provider_options(providers, active)}</select>
      </label>
      <div class="button-row" style="margin-top: 12px;">
        <button class="secondary-button" type="button" id="test-all-providers">{escape(t("provider.test_all", lang))}</button>
        <button class="primary-button" type="button" id="save-settings">{escape(t("settings.save", lang))}</button>
      </div>
      <div id="settings-result" class="hero-copy" role="status"></div>
    </section>
    <section class="two-grid">
      <article class="focus-card">
        <span class="kicker">{escape(t("provider.available_section", lang))}</span>
        <div id="available-provider-list" class="page-content">{_provider_cards(available, active, lang)}</div>
      </article>
      <article class="focus-card">
        <details{' open' if not available else ''}>
          <summary>{escape(t("provider.other_section", lang))}</summary>
          <div id="other-provider-list" class="page-content" style="margin-top: 12px;">{_provider_cards(other, active, lang)}</div>
        </details>
      </article>
    </section>
    <section id="asset-config" class="focus-card">
      <span class="kicker">{escape(t("settings.assets_clean", lang))}</span>
      <h2>{escape(t("portfolio.edit", lang))}</h2>
      <p>{escape(t("setup.assets_note", lang))}</p>
      <div id="asset-rows" class="page-content">{_asset_rows(positions, lang)}</div>
      <div class="button-row" style="margin-top: 12px;">
        <button class="secondary-button" type="button" id="add-asset-row">{escape(t("setup.add_asset", lang))}</button>
      </div>
    </section>
    <section class="focus-card">
      <span class="kicker">{escape(t("settings.system", lang))}</span>
      <div class="form-grid">
        <div class="metric-card">
          <span>{escape(t("system.tick_interval", lang))}</span>
          <strong>{escape(t("system.tick_interval_fixed", lang))}</strong>
          <p>{escape(t("system.tick_interval_note", lang))}</p>
          <input id="tick-interval-setting" type="hidden" value="60">
        </div>
        <label>Proactive update cadence (seconds)<input id="proactive-update-interval-setting" type="number" min="60" value="{escape(str(system.get("proactive_update_interval_seconds", 7200)))}"></label>
        <label>Runtime mode<select id="runtime-mode-setting"><option value="simulation"{_selected(system.get("runtime_mode"), "simulation")}>simulation</option><option value="live"{_selected(system.get("runtime_mode"), "live")}>live</option></select></label>
        <label>Trust threshold<input id="trust-threshold-setting" type="number" min="0" max="1" step="0.01" value="{escape(str(system.get("trust_threshold", 0.45)))}"></label>
        <label>Hypothesis sensitivity<input id="hypothesis-sensitivity-setting" type="number" min="0" max="1" step="0.01" value="{escape(str(system.get("hypothesis_switching_sensitivity", 0.08)))}"></label>
      </div>
      <div class="button-row" style="margin-top: 12px;">
        <button class="secondary-button" type="button" id="settings-start-runtime">{escape(t("system.start", lang))}</button>
        <button class="secondary-button" type="button" id="settings-stop-runtime">{escape(t("system.stop", lang))}</button>
      </div>
    </section>
    <details class="expert-details">
      <summary>{escape(t("settings.advanced", lang))}</summary>
      <pre>{escape(json.dumps({"metadata": config.get("metadata", {}), "read_only": True}, ensure_ascii=False, indent=2))}</pre>
    </details>
    """
    return content, SETTINGS_JS


def setup_content(config: Mapping[str, Any]) -> tuple[str, str]:
    lang = current_language()
    registry = config.get("llm_registry") if isinstance(config.get("llm_registry"), Mapping) else {}
    providers = registry.get("providers") if isinstance(registry.get("providers"), list) else []
    active = str(registry.get("active_provider") or "openai")
    active_provider = next((p for p in providers if isinstance(p, Mapping) and str(p.get("id")) == active), {})
    content = f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("setup.progress", lang))}</span>
      <h1 class="hero-title">{escape(t("setup.title", lang))}</h1>
      <p class="hero-copy">{escape(t("setup.subtitle", lang))}</p>
    </section>
    <form id="setup-form" class="page-content">
      {_setup_step("1", t("setup.welcome_title", lang), t("setup.welcome_body", lang))}
      <section class="focus-card"><span class="kicker">2</span><h2>{escape(t("setup.language_title", lang))}</h2><select name="language"><option value="en"{_selected(lang, "en")}>English</option><option value="zh"{_selected(lang, "zh")}>中文</option></select></section>
      <section class="focus-card"><span class="kicker">3</span><h2>{escape(t("setup.provider_title", lang))}</h2><div class="form-grid"><label>{escape(t("setup.provider", lang))}<select name="active_provider">{_provider_options(providers, active)}</select></label><label>{escape(t("setup.model", lang))}<input name="model" value="{escape(str(active_provider.get("model") or ""))}"></label></div><label>{escape(t("setup.base_url", lang))}<input name="base_url" value="{escape(str(active_provider.get("base_url") or ""))}"></label><label>{escape(t("setup.api_key", lang))}<input name="api_key" type="password" placeholder="{escape(t("setup.api_key_hint", lang))}"></label><button class="secondary-button" type="button" id="setup-test-provider">{escape(t("setup.test_connection", lang))}</button></section>
      {_setup_step("4", t("setup.market_mode_title", lang), t("setup.simulation_fallback", lang))}
      <section class="focus-card"><span class="kicker">5</span><h2>{escape(t("setup.assets_title", lang))}</h2><p>{escape(t("setup.assets_note", lang))}</p><div id="setup-asset-rows" class="page-content">{_asset_rows([], lang)}</div><button class="secondary-button" type="button" id="setup-add-asset">{escape(t("setup.add_asset", lang))}</button></section>
      <section class="focus-card"><span class="kicker">6</span><h2>{escape(t("setup.risk_title", lang))}</h2><select name="risk_preference"><option value="balanced">{escape(t("setup.balanced", lang))}</option><option value="conservative">{escape(t("setup.conservative", lang))}</option><option value="research_only">{escape(t("setup.research_only", lang))}</option></select></section>
      {_setup_step("7", "Review", "Review provider, assets, and runtime mode before starting.")}
      <section class="focus-card"><span class="kicker">8-10</span><h2>{escape(t("setup.start_title", lang))}</h2><div class="button-row"><button class="primary-button" type="submit">{escape(t("setup.save", lang))}</button><button class="secondary-button" type="button" id="setup-start-runtime">{escape(t("setup.start_runtime", lang))}</button><a class="ghost-button" href="/">{escape(t("setup.show_brief", lang))}</a></div><p id="setup-result" role="status">{escape(t("setup.waiting", lang))}</p></section>
    </form>
    """
    return content, SETUP_JS


def system_guide_content() -> str:
    lang = current_language()
    states = [
        ("Waiting for cognitive signal", "System has not converged on this metric yet."),
        ("Observe", "No strong regime signal is active; Atlas is monitoring."),
        ("Attention", "Narrative or market attention pressure is elevated."),
        ("Liquidity", "Capital depth, flow, or liquidity pressure is central."),
        ("Volatility", "Stress, dispersion, or instability is shaping interpretation."),
    ]
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("page.system_guide", lang))}</span>
      <h1 class="hero-title">Atlas OS</h1>
      <p class="hero-copy">Atlas is a cognitive runtime that observes events, forms structured interpretations, records forecasts, and explains confidence. It does not execute trades.</p>
    </section>
    <section class="two-grid">
      <article class="focus-card"><span class="kicker">{escape(t("state.status", lang))}</span><ul class="plain-list">{_list_items([f"{a}: {b}" for a, b in states])}</ul></article>
      <article class="visual-card"><span class="kicker">{escape(t("timeline.title", lang))}</span><h2>{escape(t("timeline.title", lang))}</h2>{_learning_flow([], lang)}</article>
    </section>
    """


def replay_content(replay_data: Mapping[str, Any]) -> str:
    rows = replay_data.get("decision_timeline") if isinstance(replay_data.get("decision_timeline"), list) else []
    return f"""
    <section class="hero-panel">
      <span class="kicker">Replay</span>
      <h1 class="hero-title">Decision replay</h1>
      <p class="hero-copy">Past ticks are reconstructed from telemetry without mutating cognition.</p>
    </section>
    <section class="focus-card">
      <ul class="plain-list">{''.join(f'<li>Tick {escape(str(item.get("tick")))} · {escape(str(item.get("regime_state") or ""))}</li>' for item in rows[:20] if isinstance(item, Mapping)) or '<li>Waiting for replay data</li>'}</ul>
    </section>
    """


def control_content(panel: Mapping[str, Any]) -> str:
    lang = current_language()
    return f"""
    <section class="hero-panel">
      <span class="kicker">{escape(t("system.control", lang))}</span>
      <h1 class="hero-title">{escape(t("state.status", lang))}</h1>
      <p class="hero-copy">Runtime controls signal the daemon. They do not directly mutate cognition.</p>
      <div class="button-row" style="margin-top: 18px;">
        <form method="post" action="/control/start"><button class="primary-button" type="submit">{escape(t("system.start", lang))}</button></form>
        <form method="post" action="/control/stop"><button class="secondary-button" type="submit">{escape(t("system.stop", lang))}</button></form>
      </div>
    </section>
    <details class="expert-details"><summary>Control state</summary><pre>{escape(json.dumps(panel, ensure_ascii=False, indent=2))}</pre></details>
    """


SETTINGS_JS = """
<script>
(function () {
  function msg(key) {
    const zh = document.documentElement.lang === "zh";
    const messages = {
      saved: zh ? "已保存" : "Saved",
      save_failed: zh ? "无法保存设置" : "Could not save settings",
      testing: zh ? "正在测试 Provider..." : "Testing providers...",
      checked: zh ? "Provider 检测完成" : "Provider check complete",
      test_failed: zh ? "Provider 测试失败" : "Provider test failed",
      starting: zh ? "正在启动 runtime..." : "Starting runtime...",
      started: zh ? "runtime 已启动" : "Runtime started",
      stopping: zh ? "正在停止 runtime..." : "Stopping runtime...",
      stopped: zh ? "runtime 已停止" : "Runtime stopped",
      runtime_failed: zh ? "Runtime 控制失败" : "Runtime control failed"
    };
    return messages[key] || key;
  }
  function providerCards() {
    return Array.from(document.querySelectorAll("[data-provider-card]")).map(function (card) {
      const item = {};
      card.querySelectorAll("[data-provider-field]").forEach(function (field) {
        item[field.getAttribute("data-provider-field")] = field.value;
      });
      item.label = card.getAttribute("data-label") || item.id;
      item.enabled = true;
      item.available_models = Array.from(card.querySelectorAll("datalist option")).map(function (option) { return option.value; });
      return item;
    });
  }
  function assetRows(rootId) {
    return Array.from(document.querySelectorAll("#" + rootId + " [data-asset-row]")).map(function (row) {
      const item = {};
      row.querySelectorAll("[data-asset-field]").forEach(function (field) { item[field.dataset.assetField] = field.value.trim(); });
      item.portfolio_percentage = Number(item.portfolio_percentage || 0);
      return item;
    }).filter(function (item) { return item.asset; });
  }
  function assetTemplate() {
    return document.querySelector("[data-asset-row]").outerHTML.replace(/value="[^"]*"/g, 'value=""').replace(/>[^<]*<\\/textarea>/g, '></textarea>');
  }
  async function saveSettings() {
    const assets = assetRows("asset-rows");
    const payload = {
      ui: { language: document.getElementById("global-language-select") ? document.getElementById("global-language-select").value : "en" },
      llm_registry: {
        active_provider: document.getElementById("settings-active-provider").value,
        strict_provider_list: true,
        fallback_chain: providerCards().map(function (p) { return p.id; }),
        providers: providerCards()
      },
      system: {
        tick_interval: Number(document.getElementById("tick-interval-setting").value || 60),
        proactive_update_enabled: true,
        proactive_update_interval_seconds: Number(document.getElementById("proactive-update-interval-setting").value || 7200),
        runtime_mode: document.getElementById("runtime-mode-setting").value,
        trust_threshold: Number(document.getElementById("trust-threshold-setting").value || 0.45),
        hypothesis_switching_sensitivity: Number(document.getElementById("hypothesis-sensitivity-setting").value || 0.08)
      },
      assets: { portfolio_json: JSON.stringify({ positions: assets }), asset_list: assets.map(function (x) { return x.asset; }), weights: Object.fromEntries(assets.map(function (x) { return [x.asset, x.portfolio_percentage]; })) },
      metadata: { ui_only: true, no_runtime_reload: true, no_trading_execution: true }
    };
    const response = await fetch("/settings", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
    const data = await response.json();
    document.getElementById("settings-result").textContent = data.status === "saved" ? msg("saved") : msg("save_failed");
    return data;
  }
  document.getElementById("save-settings").addEventListener("click", saveSettings);
  document.getElementById("add-asset-row").addEventListener("click", function () {
    document.getElementById("asset-rows").insertAdjacentHTML("beforeend", assetTemplate());
  });
  document.getElementById("test-all-providers").addEventListener("click", async function () {
    await saveSettings();
    document.getElementById("settings-result").textContent = msg("testing");
    try {
      const response = await fetch("/llm/providers/test_all", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
      const data = await response.json();
      document.getElementById("settings-result").textContent = msg("checked") + ": " + (data.summary ? data.summary.online_count + "/" + data.summary.total_count : "");
    } catch (error) {
      document.getElementById("settings-result").textContent = msg("test_failed");
    }
  });
  document.querySelectorAll("[data-test-provider]").forEach(function (button) {
    button.addEventListener("click", async function () {
      await saveSettings();
      const card = button.closest("[data-provider-card]");
      const id = card.querySelector('[data-provider-field="id"]').value;
      card.querySelector("[data-provider-health]").textContent = msg("testing");
      try {
        const response = await fetch("/llm/provider/test", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ provider_id: id }) });
        const data = await response.json();
        card.querySelector("[data-provider-health]").textContent = data.status || data.health || msg("checked");
      } catch (error) {
        card.querySelector("[data-provider-health]").textContent = msg("test_failed");
      }
    });
  });
  document.getElementById("settings-start-runtime").addEventListener("click", async function () {
    const result = document.getElementById("settings-result");
    result.textContent = msg("starting");
    try {
      await saveSettings();
      const response = await fetch("/control/start", { method: "POST" });
      const data = await response.json();
      result.textContent = data.status === "started" ? msg("started") : (data.status || msg("runtime_failed"));
    } catch (error) {
      result.textContent = msg("runtime_failed");
    }
  });
  document.getElementById("settings-stop-runtime").addEventListener("click", async function () {
    const result = document.getElementById("settings-result");
    result.textContent = msg("stopping");
    try {
      const response = await fetch("/control/stop", { method: "POST" });
      const data = await response.json();
      result.textContent = ["stop_requested", "stopped"].includes(data.status) ? msg("stopped") : (data.status || msg("runtime_failed"));
    } catch (error) {
      result.textContent = msg("runtime_failed");
    }
  });
})();
</script>
"""


SETUP_JS = """
<script>
(function () {
  function msg(key) {
    const zh = document.documentElement.lang === "zh";
    const messages = {
      saved: zh ? "设置已保存" : "Setup saved",
      save_failed: zh ? "无法保存设置" : "Could not save setup",
      testing: zh ? "正在测试 Provider..." : "Testing provider...",
      test_complete: zh ? "Provider 测试完成" : "Provider test complete",
      test_failed: zh ? "Provider 测试失败" : "Provider test failed",
      starting: zh ? "正在启动 runtime..." : "Starting runtime...",
      started: zh ? "runtime 已启动" : "Runtime started",
      start_failed: zh ? "Runtime 启动失败" : "Runtime start failed"
    };
    return messages[key] || key;
  }
  function assetTemplate() {
    return document.querySelector("[data-asset-row]").outerHTML.replace(/value="[^"]*"/g, 'value=""').replace(/>[^<]*<\\/textarea>/g, '></textarea>');
  }
  function assets() {
    return Array.from(document.querySelectorAll("#setup-asset-rows [data-asset-row]")).map(function (row) {
      const item = {};
      row.querySelectorAll("[data-asset-field]").forEach(function (field) { item[field.dataset.assetField] = field.value.trim(); });
      item.portfolio_percentage = Number(item.portfolio_percentage || 0);
      return item;
    }).filter(function (item) { return item.asset; });
  }
  function payload() {
    const form = new FormData(document.getElementById("setup-form"));
    const rows = assets();
    return {
      active_provider: form.get("active_provider"),
      language: form.get("language"),
      model: form.get("model"),
      base_url: form.get("base_url"),
      api_key: form.get("api_key"),
      portfolio_json: JSON.stringify({ positions: rows })
    };
  }
  async function save() {
    const response = await fetch("/settings", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload()) });
    return await response.json();
  }
  document.getElementById("setup-add-asset").addEventListener("click", function () {
    document.getElementById("setup-asset-rows").insertAdjacentHTML("beforeend", assetTemplate());
  });
  document.getElementById("setup-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    const result = document.getElementById("setup-result");
    try {
      const data = await save();
      result.textContent = data.status === "saved" ? msg("saved") : msg("save_failed");
    } catch (error) {
      result.textContent = msg("save_failed");
    }
  });
  document.getElementById("setup-test-provider").addEventListener("click", async function () {
    const result = document.getElementById("setup-result");
    result.textContent = msg("testing");
    try {
      await save();
      const response = await fetch("/llm/provider/test", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ provider_id: payload().active_provider }) });
      const data = await response.json();
      result.textContent = msg("test_complete") + ": " + (data.status || data.health || "checked");
    } catch (error) {
      result.textContent = msg("test_failed");
    }
  });
  document.getElementById("setup-start-runtime").addEventListener("click", async function () {
    const result = document.getElementById("setup-result");
    result.textContent = msg("starting");
    try {
      await save();
      const response = await fetch("/control/start", { method: "POST" });
      const data = await response.json();
      result.textContent = data.status === "started" ? msg("started") : (data.status || msg("start_failed"));
    } catch (error) {
      result.textContent = msg("start_failed");
    }
  });
})();
</script>
"""


def _packet(state: Mapping[str, Any]) -> Mapping[str, Any]:
    packet = state.get("last_decision_packet")
    return packet if isinstance(packet, Mapping) else {}


def _market(state: Mapping[str, Any]) -> Mapping[str, Any]:
    market = state.get("market_intelligence")
    return market if isinstance(market, Mapping) else {}


def _portfolio(state: Mapping[str, Any]) -> Mapping[str, Any]:
    portfolio = state.get("portfolio_context")
    return portfolio if isinstance(portfolio, Mapping) else {}


def _safe_action(value: Any) -> str:
    action = str(value or "observe").strip().lower()
    if action in {"neutral", "unknown", "wait"}:
        action = "observe"
    if action not in ATLAS_ACTIONS:
        action = "observe"
    return action.title()


def _clean(value: Any, fallback: str) -> str:
    text = str(value if value not in {None, "", "Unknown", "UNKNOWN", "null"} else fallback).replace("\x00", " ").strip()
    if "llm reasoning unavailable" in text.lower():
        return fallback
    return text or fallback


def _compact(value: Any, fallback: str = "Waiting for signal") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _confidence(packet: Mapping[str, Any]) -> str:
    value = _confidence_value(packet)
    return f"{round(value)}%"


def _confidence_value(packet: Mapping[str, Any]) -> float:
    try:
        value = float(packet.get("confidence", 0.0))
    except (TypeError, ValueError):
        value = 0.0
    if value <= 1:
        value *= 100
    return max(0.0, min(100.0, value))


def _main_change(market: Mapping[str, Any], packet: Mapping[str, Any], lang: str) -> str:
    summary = str(packet.get("causal_summary") or "").strip()
    if "llm reasoning unavailable" in summary.lower():
        summary = ""
    if summary and summary.lower() not in {"unknown", "none", "null"}:
        headline = _headline_from_summary(summary)
        if headline:
            return headline
    regime = _clean(packet.get("regime_state"), "").split("/")[0].strip()
    if regime:
        return _regime_headline(regime, lang)
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    live = [key for key, value in channels.items() if str(value) == "LIVE"]
    failed = [key for key, value in channels.items() if str(value) in {"FAILED", "RATE_LIMITED"}]
    if live:
        return "实时市场上下文部分可用" if lang == "zh" else "Live market context active"
    if failed:
        return "市场数据通道降级" if lang == "zh" else "Market data degraded"
    return t("home.default_change", lang)


def _headline_from_summary(summary: str) -> str:
    text = " ".join(summary.replace("\n", " ").split())
    lowered = text.lower()
    markers = [
        "primary driver is ",
        "dominated by ",
        "dominant pressure source is ",
    ]
    for marker in markers:
        index = lowered.find(marker)
        if index < 0:
            continue
        start = index + len(marker)
        fragment = text[start:]
        for stop in [", where ", ", with ", ", while ", ", and ", ": ", ". "]:
            stop_index = fragment.lower().find(stop)
            if 0 <= stop_index <= 72:
                fragment = fragment[:stop_index]
                break
        return _headline_text(fragment)
    for token in ["RISK_OFF", "ATTENTION_EXPANSION", "BREAKOUT", "NORMAL"]:
        if token in text:
            return token.replace("_", " ").title()
    return ""


def _headline_text(value: str) -> str:
    text = value.strip(" .,:;")
    if not text:
        return ""
    if len(text) <= 58:
        return text
    words = text.split()
    output: list[str] = []
    for word in words:
        candidate = " ".join(output + [word])
        if len(candidate) > 58:
            break
        output.append(word)
    return " ".join(output).strip(" .,:;") or text[:58].strip(" .,:;")


def _regime_headline(regime: str, lang: str) -> str:
    key = regime.strip().upper().replace(" ", "_")
    zh = {
        "RISK_OFF": "风险防御",
        "ATTENTION_EXPANSION": "注意力扩张",
        "BREAKOUT": "突破观察",
        "NORMAL": "中性观察",
    }
    en = {
        "RISK_OFF": "Risk-off Review",
        "ATTENTION_EXPANSION": "Attention Expansion",
        "BREAKOUT": "Breakout Watch",
        "NORMAL": "Neutral Market State",
    }
    mapping = zh if lang == "zh" else en
    return mapping.get(key, regime.replace("_", " ").title())


def _portfolio_headline(portfolio: Mapping[str, Any], lang: str) -> str:
    if portfolio.get("status") == "configured":
        exposure = portfolio.get("exposure_sum_pct")
        return f"已配置暴露：{_pct_text(exposure)}" if lang == "zh" else f"Configured exposure: {_pct_text(exposure)}"
    return t("home.no_portfolio", lang)


def _market_impact_summary(state: Mapping[str, Any], lang: str) -> str:
    market = _market(state)
    status = str(market.get("status") or "")
    if status and status != "not_run":
        return status.replace("_", " ")
    return t("home.default_meaning", lang)


def _pct_text(value: Any) -> str:
    if value is None:
        return "Waiting for signal"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return str(value)


def _metric(label: str, value: str, note: str) -> str:
    return f'<article class="metric-card"><span>{escape(label)}</span><strong>{escape(value)}</strong><p>{escape(note)}</p></article>'


def _viz_shell(viz_id: str, question_key: str, inner_html: str) -> str:
    lang = current_language()
    question = t(question_key, lang)
    return (
        f'<div class="viz-frame" data-viz-id="{escape(viz_id)}" '
        f'data-viz-question="{escape(question)}" tabindex="0" role="button" '
        f'aria-pressed="false" aria-label="{escape(question)}">'
        f'<div class="viz-question">{escape(question)}</div>'
        f'{inner_html}'
        f'<div class="viz-feedback" data-viz-feedback>{escape(t("viz.inspect_hint", lang))}</div>'
        f'</div>'
    )


def _list_items(items: Iterable[str]) -> str:
    return "".join(f"<li>{escape(str(item))}</li>" for item in items)


def _gauge(value: float) -> str:
    return f'<div class="gauge" style="--value:{value:.0f};" aria-label="confidence"><span>{value:.0f}%</span></div>'


def _portfolio_minimap(portfolio: Mapping[str, Any]) -> str:
    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []
    if not positions:
        return _empty_portfolio_svg()
    return _portfolio_bubbles(positions[:6], compact=True)


def _portfolio_bubbles(positions: list[Any], compact: bool = False) -> str:
    valid = [item for item in positions if isinstance(item, Mapping)]
    if not valid:
        return _empty_portfolio_svg()
    width, height = 520, 230 if not compact else 170
    circles = []
    for index, item in enumerate(valid[:9]):
        weight = _num(item.get("portfolio_percentage"), 5)
        radius = max(18, min(72, 16 + weight * 1.4))
        x = 72 + (index % 3) * 160
        y = 70 + (index // 3) * 78
        color = ["#dbeafe", "#9ee6b8", "#f6d77a", "#9fd3ff", "#f4a5b3"][index % 5]
        label = escape(str(item.get("asset") or "Asset")[:10])
        circles.append(f'<g tabindex="0"><circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" fill-opacity="0.26" stroke="{color}"/><text x="{x}" y="{y}" text-anchor="middle" fill="#f4f7fb" font-size="13">{label}</text><text x="{x}" y="{y+18}" text-anchor="middle" fill="#9aa5b5" font-size="11">{weight:.1f}%</text></g>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 {width} {height}" role="img" aria-label="Portfolio exposure map">{"".join(circles)}</svg>'
    return _viz_shell("portfolio_exposure", "viz.portfolio_exposure", svg)


def _empty_portfolio_svg() -> str:
    svg = """
    <svg class="atlas-viz" viewBox="0 0 520 210" role="img" aria-label="Portfolio exposure map waiting for assets">
      <circle cx="140" cy="105" r="56" fill="#dbeafe" fill-opacity=".12" stroke="#dbeafe" stroke-dasharray="6 6"/>
      <circle cx="260" cy="105" r="42" fill="#9ee6b8" fill-opacity=".1" stroke="#9ee6b8" stroke-dasharray="6 6"/>
      <circle cx="365" cy="105" r="34" fill="#f6d77a" fill-opacity=".1" stroke="#f6d77a" stroke-dasharray="6 6"/>
      <text x="260" y="186" text-anchor="middle" fill="#9aa5b5" font-size="13">Add your first asset to see portfolio impact.</text>
    </svg>
    """
    return _viz_shell("portfolio_exposure", "viz.portfolio_exposure", svg)


def _theme_bars(values: Any, viz_id: str = "theme_concentration", question_key: str = "viz.theme_concentration") -> str:
    data = values if isinstance(values, Mapping) else {}
    if not data:
        return _viz_shell(viz_id, question_key, '<div class="empty-state">Add assets with themes to see concentration.</div>')
    bars = []
    for index, (label, value) in enumerate(list(data.items())[:6]):
        pct = max(0, min(100, _num(value, 0)))
        bars.append(f'<div class="metric-card"><span>{escape(str(label))}</span><strong>{pct:.1f}%</strong><div style="height:8px;border-radius:999px;background:rgba(255,255,255,.08);margin-top:10px;"><i style="display:block;width:{pct}%;height:100%;border-radius:999px;background:#dbeafe;"></i></div></div>')
    return _viz_shell(viz_id, question_key, "".join(bars))


def _risk_cluster_graph(clusters: Any) -> str:
    data = clusters if isinstance(clusters, list) else []
    if not data:
        return _viz_shell("risk_cluster_graph", "viz.risk_cluster", '<div class="empty-state">No correlated risk cluster yet.</div>')
    nodes = []
    edges = []
    for index, item in enumerate(data[:5]):
        if not isinstance(item, Mapping):
            continue
        x = 90 + index * 92
        y = 90 + (28 if index % 2 else -18)
        color = "#f4a5b3" if "high" in str(item.get("risk")) else "#dbeafe"
        nodes.append(f'<circle cx="{x}" cy="{y}" r="{26 + _num(item.get("exposure_pct"), 0) / 4}" fill="{color}" fill-opacity=".18" stroke="{color}"/><text x="{x}" y="{y+4}" text-anchor="middle" fill="#f4f7fb" font-size="11">{escape(str(item.get("cluster"))[:10])}</text>')
        if index:
            edges.append(f'<line x1="{x-92}" y1="{90 + (28 if (index-1) % 2 else -18)}" x2="{x}" y2="{y}" stroke="rgba(255,255,255,.18)"/>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 540 180" role="img" aria-label="Risk cluster graph">{"".join(edges)}{"".join(nodes)}</svg>'
    return _viz_shell("risk_cluster_graph", "viz.risk_cluster", svg)


def _regime_trajectory(state: Mapping[str, Any]) -> str:
    timeline = state.get("dashboard", {}).get("regime_state_timeline", []) if isinstance(state.get("dashboard"), Mapping) else []
    points = []
    for index, item in enumerate(timeline[:12]):
        if not isinstance(item, Mapping):
            continue
        y = 130 - (index % 5) * 18
        points.append((30 + index * 38, y))
    if len(points) < 2:
        points = [(30, 130), (110, 112), (190, 120), (270, 88), (350, 96), (430, 68)]
    path = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(points))
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#dbeafe"/>' for x, y in points)
    svg = f'<svg class="atlas-viz" viewBox="0 0 500 170" role="img" aria-label="Market regime trajectory"><path d="{path}" fill="none" stroke="#dbeafe" stroke-width="3"/>{dots}</svg>'
    return _viz_shell("market_regime_trajectory", "viz.regime_trajectory", svg)


def _attention_liquidity_phase(state: Mapping[str, Any]) -> str:
    data = state.get("dashboard", {}).get("attention_liquidity_charts", []) if isinstance(state.get("dashboard"), Mapping) else []
    points = []
    for index, item in enumerate(data[:10]):
        if not isinstance(item, Mapping):
            continue
        x = 40 + _num(item.get("attention"), index * 0.08) * 360
        y = 150 - _num(item.get("liquidity"), index * 0.07) * 110
        points.append((max(35, min(455, x)), max(35, min(150, y))))
    if len(points) < 2:
        points = [(60, 132), (120, 118), (190, 98), (250, 118), (340, 76), (420, 60)]
    path = " ".join(("M" if i == 0 else "Q" if i == 2 else "L") + f"{x},{y}" for i, (x, y) in enumerate(points))
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#9ee6b8"/>' for x, y in points)
    svg = f'<svg class="atlas-viz" viewBox="0 0 500 180" role="img" aria-label="Attention liquidity phase space"><line x1="35" y1="150" x2="465" y2="150" stroke="rgba(255,255,255,.18)"/><line x1="35" y1="25" x2="35" y2="150" stroke="rgba(255,255,255,.18)"/><path d="{path}" fill="none" stroke="#9ee6b8" stroke-width="3"/>{dots}<text x="360" y="170" fill="#9aa5b5" font-size="12">attention</text><text x="8" y="35" fill="#9aa5b5" font-size="12">liquidity</text></svg>'
    return _viz_shell("attention_liquidity", "viz.attention_liquidity", svg)


def _theme_landscape(state: Mapping[str, Any]) -> str:
    portfolio = _portfolio(state)
    exposure = portfolio.get("exposure_map") if isinstance(portfolio.get("exposure_map"), Mapping) else {}
    themes = exposure.get("theme_concentration") if isinstance(exposure.get("theme_concentration"), Mapping) else {}
    if not themes:
        themes = {"early discovery": 18, "crowded": 36, "fading": 14, "accelerating": 28}
    return _theme_bars(themes, "theme_landscape", "viz.theme_concentration")


def _freshness_map(market: Mapping[str, Any]) -> str:
    lang = current_language()
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    view = localize_market_freshness(market, lang)
    if not channels:
        return _viz_shell("data_freshness_map", "viz.data_freshness", f'<div class="empty-state">{escape(str(view.get("empty") or ""))}</div>')
    summary = str(view.get("summary") or "")
    observations = _observation_health_rows(view.get("observations") if isinstance(view.get("observations"), list) else [])
    pills = _localized_channel_pills(view.get("channels") if isinstance(view.get("channels"), list) else [])
    return _viz_shell(
        "data_freshness_map",
        "viz.data_freshness",
        f'<div class="freshness-summary">{escape(summary)}</div><div class="pill-row">{pills}</div>{observations}',
    )


def _market_freshness_summary(market: Mapping[str, Any], lang: str) -> str:
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    live = sum(1 for value in channels.values() if str(value).upper() == "LIVE")
    simulated = sum(1 for value in channels.values() if str(value).upper() == "SIMULATED")
    failed = sum(1 for value in channels.values() if str(value).upper() in {"FAILED", "RATE_LIMITED"})
    missing = sum(1 for value in channels.values() if str(value).upper() == "NOT_CONFIGURED")
    available_assets = sum(1 for item in observations if isinstance(item, Mapping) and item.get("data_quality_status") == "Available")
    total_assets = len([item for item in observations if isinstance(item, Mapping)])
    if lang == "zh":
        parts = [f"价格 {available_assets}/{total_assets} 可用"] if total_assets else []
        parts.append(f"{live} 个实时通道")
        if simulated:
            parts.append(f"{simulated} 个模拟通道")
        if failed:
            parts.append(f"{failed} 个失败通道")
        if missing:
            parts.append(f"{missing} 个未配置")
        return " · ".join(parts)
    parts = [f"Price {available_assets}/{total_assets} available"] if total_assets else []
    parts.append(f"{live} live channels")
    if simulated:
        parts.append(f"{simulated} simulated")
    if failed:
        parts.append(f"{failed} failed")
    if missing:
        parts.append(f"{missing} not configured")
    return " · ".join(parts)


def _observation_health_rows(observations: Any) -> str:
    if not isinstance(observations, list):
        observations = []
    rows = []
    for item in observations[:4]:
        if not isinstance(item, Mapping):
            continue
        status = item.get("status") if isinstance(item.get("status"), Mapping) else {}
        status_text = str(status.get("primary") or item.get("data_quality_status") or "Unknown")
        source = str(item.get("source") or "none")
        asset = str(item.get("asset_display") or item.get("asset") or "Unknown")
        description = str(item.get("description") or "")
        css = str(item.get("css") or "bad")
        rows.append(
            f'<div class="freshness-row {css}"><span>{escape(asset)}<small>{escape(description)}</small></span><strong>{escape(status_text)}</strong><em>{escape(source)}</em></div>'
        )
    if not rows:
        return ""
    return '<div class="freshness-rows">' + "".join(rows) + "</div>"


def _proactive_update_card(state: Mapping[str, Any], lang: str) -> str:
    proactive = state.get("proactive_update_state") if isinstance(state.get("proactive_update_state"), Mapping) else {}
    view = localize_proactive_update(proactive, lang)
    title = str(view.get("title") or ("主动更新" if lang == "zh" else "Proactive update"))
    subtitle = str(view.get("subtitle") or "")
    if not proactive:
        waiting = str(view.get("heading") or "")
        return f"""
        <section class="focus-card">
          <span class="kicker">{escape(title)}</span>
          <h2>{escape(waiting)}</h2>
          <p>{escape(subtitle)}</p>
        </section>
        """
    status = view.get("status") if isinstance(view.get("status"), Mapping) else {}
    status_text = str(status.get("primary") or "")
    focus_items = view.get("focus_items") if isinstance(view.get("focus_items"), list) else []
    channel_text = str(view.get("channels_text") or ("等待通道状态" if lang == "zh" else "waiting for channel status"))
    return f"""
    <section class="focus-card">
      <span class="kicker">{escape(title)} · {escape(status_text)}</span>
      <h2>{escape(str(view.get("heading") or ""))}</h2>
      <p>{escape(subtitle)}</p>
      <div class="pill-row" style="margin: 10px 0 12px;">
        <span class="tag">{escape("周期" if lang == "zh" else "Cadence")}: {escape(str(view.get("cadence") or ""))}</span>
        <span class="tag">{escape(str(view.get("last_run") or ""))}</span>
        <span class="tag">{escape(str(view.get("next_due") or ""))}</span>
      </div>
      <p><strong>{escape("刷新通道" if lang == "zh" else "Channels")}:</strong> {escape(channel_text)}</p>
      <ul class="plain-list">{_list_items(focus_items)}</ul>
    </section>
    """


def _localized_channel_pills(channels: list[Any]) -> str:
    parts = []
    for item in channels:
        if not isinstance(item, Mapping):
            continue
        status = item.get("status") if isinstance(item.get("status"), Mapping) else {}
        parts.append(
            f'<span class="signal-pill {escape(str(item.get("css") or ""))}">{escape(str(item.get("label") or ""))}: {escape(str(status.get("primary") or ""))}</span>'
        )
    return "".join(parts)


def _channel_pills(channels: Mapping[str, Any]) -> str:
    parts = []
    for key, value in channels.items():
        status = str(value)
        css = "signal-live" if status == "LIVE" else "signal-failed" if status in {"FAILED", "RATE_LIMITED"} else "signal-simulated" if status in {"SIMULATED", "CACHED", "DELAYED"} else ""
        parts.append(f'<span class="signal-pill {css}">{escape(str(key).replace("_", " "))}: {escape(status.replace("_", " ").title())}</span>')
    return "".join(parts)


def _trust_trend(state: Mapping[str, Any]) -> str:
    latest = _num(state.get("trust_index"), 0.45)
    points = [(30, 130), (105, 118), (180, 124), (255, 92), (330, 102), (430, 145 - latest * 110)]
    path = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(points))
    svg = f'<svg class="atlas-viz" viewBox="0 0 500 170" role="img" aria-label="Trust trend"><path d="{path}" fill="none" stroke="#f6d77a" stroke-width="3"/><circle cx="{points[-1][0]}" cy="{points[-1][1]}" r="7" fill="#f6d77a"/><text x="30" y="156" fill="#9aa5b5" font-size="12">trust</text></svg>'
    return _viz_shell("trust_evolution", "viz.trust_evolution", svg)


def _calibration_chart(forecasts: list[Any]) -> str:
    evaluated = [f for f in forecasts if isinstance(f, Mapping) and f.get("status") in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}]
    if len(evaluated) < 3:
        return _viz_shell("prediction_calibration", "viz.prediction_calibration", '<div class="empty-state">Atlas has not recorded enough prediction outcomes yet.</div>')
    dots = []
    for item in evaluated[:20]:
        conf = _num(item.get("confidence"), 0.5)
        err = _num(item.get("forecast_error"), 0.5)
        x = 45 + conf * 390
        y = 150 - (1 - err) * 120
        color = "#9ee6b8" if item.get("status") == "VERIFIED" else "#f4a5b3"
        dots.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" fill-opacity=".85"/>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 500 180" role="img" aria-label="Prediction calibration chart"><line x1="45" y1="150" x2="455" y2="30" stroke="rgba(255,255,255,.18)" stroke-dasharray="5 5"/>{dots}<text x="330" y="170" fill="#9aa5b5" font-size="12">confidence</text></svg>'
    return _viz_shell("prediction_calibration", "viz.prediction_calibration", svg)


def _forecast_timeline(forecasts: list[Any]) -> str:
    valid = [f for f in forecasts if isinstance(f, Mapping)]
    if not valid:
        return _viz_shell("forecast_timeline", "viz.forecast_timeline", '<div class="empty-state">Atlas has not recorded enough predictions yet.</div>')
    nodes = []
    for index, item in enumerate(valid[:8]):
        x = 45 + index * 56
        status = str(item.get("status") or "OPEN")
        color = {"OPEN": "#dbeafe", "MATURED": "#f6d77a", "VERIFIED": "#9ee6b8", "INVALIDATED": "#f4a5b3"}.get(status, "#9fd3ff")
        nodes.append(f'<g><circle cx="{x}" cy="82" r="16" fill="{color}" fill-opacity=".25" stroke="{color}"/><text x="{x}" y="124" text-anchor="middle" fill="#9aa5b5" font-size="10">{escape(status[:8])}</text></g>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 520 150" role="img" aria-label="Forecast timeline"><line x1="45" y1="82" x2="455" y2="82" stroke="rgba(255,255,255,.16)"/>{"".join(nodes)}</svg>'
    return _viz_shell("forecast_timeline", "viz.forecast_timeline", svg)


def _forecast_rows(forecasts: list[Any], *, empty: str) -> str:
    if not forecasts:
        return f"<li>{escape(empty)}</li>"
    rows = []
    for item in forecasts:
        if isinstance(item, Mapping):
            rows.append(f"<li><strong>{escape(str(item.get('subject') or 'Forecast'))}</strong><br>{escape(str(item.get('forecast_statement') or item.get('expected_direction_state') or 'Waiting for outcome'))}</li>")
    return "".join(rows)


def _hypothesis_competition(state: Mapping[str, Any]) -> str:
    values = [42, 28, 18, 12]
    labels = ["active", "shadow A", "shadow B", "reserve"]
    bars = []
    for index, value in enumerate(values):
        bars.append(f'<rect x="50" y="{30 + index*34}" width="{value*8}" height="18" rx="8" fill="#dbeafe" fill-opacity="{0.7 - index*0.12}"/><text x="50" y="{24 + index*34}" fill="#9aa5b5" font-size="11">{labels[index]}</text>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 500 180" role="img" aria-label="Hypothesis competition">{"".join(bars)}</svg>'
    return _viz_shell("hypothesis_competition", "viz.hypothesis_competition", svg)


def _learning_flow(items: list[Any], lang: str) -> str:
    labels = ["Before", "Reality", "Error", "Update", "Now"]
    if lang == "zh":
        labels = ["之前", "现实", "错误", "更新", "现在"]
    cards = []
    for index, label in enumerate(labels):
        x = 30 + index * 94
        cards.append(f'<g tabindex="0"><rect x="{x}" y="45" width="76" height="70" rx="14" fill="rgba(255,255,255,.06)" stroke="rgba(255,255,255,.16)"/><text x="{x+38}" y="84" text-anchor="middle" fill="#f4f7fb" font-size="12">{escape(label)}</text></g>')
        if index < len(labels) - 1:
            cards.append(f'<line x1="{x+78}" y1="80" x2="{x+92}" y2="80" stroke="#dbeafe"/>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 520 155" role="img" aria-label="Learning evolution flow">{"".join(cards)}</svg>'
    return _viz_shell("learning_evolution_flow", "viz.learning_flow", svg)


def _workflow_svg(active: str) -> str:
    nodes = [
        ("external", "External Info", "Market, portfolio, user, provider context"),
        ("input_router", "Input Router", "Normalize input safely"),
        ("event_stream", "Event Stream", "Queue tick events"),
        ("fusion", "Fusion", "Fuse observed variables"),
        ("memory", "Memory", "Regime memory context"),
        ("causal", "Causal", "Causal interpretation"),
        ("world", "World Model", "Market representation"),
        ("lmse", "LMSE", "Latent structure"),
        ("mpce", "MPCE", "Physics constraints"),
        ("mle", "MLE", "Law emergence"),
        ("hypothesis", "Hypothesis", "Competing models"),
        ("forecast", "Forecast", "Accountability ledger"),
        ("contract", "Decision Contract", "Strict packet"),
        ("llm", "LLM Router", "Provider reasoning"),
        ("feedback", "Feedback", "Bounded update"),
        ("trust", "Trust", "Reliability"),
        ("iteration", "Self-Iteration", "Behavioral loop"),
        ("brief", "Decision Brief", "User view"),
    ]
    active_index = next((i for i, (key, _, _) in enumerate(nodes) if key == active), 12)
    parts = []
    for index, (key, label, desc) in enumerate(nodes):
        row = index // 6
        col = index % 6
        x = 28 + col * 82
        y = 30 + row * 82
        cls = "active" if index <= active_index else ""
        fill = "#dbeafe" if index <= active_index else "rgba(255,255,255,.05)"
        text = "#0b0f14" if index <= active_index else "#cbd5e1"
        parts.append(f'<g data-workflow-node="{key}" data-label="{escape(label)}" data-description="{escape(desc)}" tabindex="0" role="button" style="cursor:pointer"><rect x="{x}" y="{y}" width="70" height="48" rx="12" fill="{fill}" fill-opacity="{1 if index <= active_index else .7}" stroke="rgba(255,255,255,.16)"/><text x="{x+35}" y="{y+28}" text-anchor="middle" fill="{text}" font-size="9">{escape(label[:14])}</text></g>')
        if index < len(nodes) - 1 and col < 5:
            parts.append(f'<line x1="{x+70}" y1="{y+24}" x2="{x+82}" y2="{y+24}" stroke="rgba(219,234,254,.35)"/>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 540 280" role="img" aria-label="Global system workflow">{"".join(parts)}</svg>'
    return _viz_shell("workflow_graph", "viz.workflow_graph", svg)


def _active_workflow(state: Mapping[str, Any]) -> str:
    if _packet(state):
        return "contract"
    if state.get("trust_index") is not None:
        return "trust"
    return "event_stream"


def _roadmap_title(current: str) -> str:
    text = current.replace("_", " ").strip()
    if len(text) > 62:
        return "Production Trial Candidate"
    return text.title()


def _roadmap_swimlanes(tracks: list[Any], layers: list[Any]) -> str:
    if not tracks:
        tracks = [{"track": "Core", "status": "production trial"}, {"track": "Runtime", "status": "proven"}, {"track": "UI/Product", "status": "partial"}]
    lane_parts = []
    for row, track in enumerate(tracks[:5]):
        if not isinstance(track, Mapping):
            continue
        y = 35 + row * 40
        label = str(track.get("track") or "Track")
        status = str(track.get("status") or track.get("current_focus") or "partial")
        lane_parts.append(f'<text x="20" y="{y+6}" fill="#cbd5e1" font-size="12">{escape(label[:18])}</text><line x1="150" y1="{y}" x2="480" y2="{y}" stroke="rgba(255,255,255,.16)"/><circle cx="{240 + row*42}" cy="{y}" r="12" fill="#dbeafe" fill-opacity=".28" stroke="#dbeafe"/><text x="500" y="{y+5}" fill="#9aa5b5" font-size="11">{escape(status[:18])}</text>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 620 250" role="img" aria-label="Roadmap swimlanes">{"".join(lane_parts)}</svg>'
    return _viz_shell("roadmap_swimlanes", "viz.roadmap_swimlanes", svg)


def _roadmap_layer_rows(layers: list[Any]) -> str:
    if not layers:
        return "<li>Roadmap data is waiting for signal.</li>"
    rows = []
    for item in layers:
        if isinstance(item, Mapping):
            rows.append(f"<li>{escape(str(item.get('version') or 'version'))}: {escape(str(item.get('name') or 'capability'))} · {escape(str(item.get('status') or 'status'))}</li>")
    return "".join(rows)


def _capability_evolution(layers: list[Any]) -> str:
    count = len([item for item in layers if isinstance(item, Mapping)])
    points = [(35 + i * 42, 145 - min(110, i * 9)) for i in range(max(3, min(count, 11)))]
    path = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(points))
    svg = f'<svg class="atlas-viz" viewBox="0 0 520 170" role="img" aria-label="Capability evolution"><path d="{path}" fill="none" stroke="#9ee6b8" stroke-width="3"/><text x="35" y="160" fill="#9aa5b5" font-size="12">{count} layers</text></svg>'
    return _viz_shell("capability_evolution", "viz.capability_evolution", svg)


def _validation_history(layers: list[Any]) -> str:
    bars = []
    for index, item in enumerate(layers[:8]):
        if not isinstance(item, Mapping):
            continue
        validation = item.get("validation") if isinstance(item.get("validation"), Mapping) else {}
        status = str(validation.get("status") or item.get("status") or "partial")
        color = "#9ee6b8" if "PROVEN" in status.upper() or status in {"completed", "implemented"} else "#f6d77a"
        bars.append(f'<rect x="{45 + index*54}" y="60" width="28" height="70" rx="8" fill="{color}" fill-opacity=".45"/><text x="{59 + index*54}" y="145" text-anchor="middle" fill="#9aa5b5" font-size="9">{escape(str(item.get("version") or "")[:5])}</text>')
    svg = f'<svg class="atlas-viz" viewBox="0 0 520 170" role="img" aria-label="Validation history">{"".join(bars)}</svg>'
    return _viz_shell("validation_history", "viz.validation_history", svg)


def _provider_cards(providers: list[Any], active: str, lang: str) -> str:
    if not providers:
        return f'<div class="empty-state">{escape(t("provider.none_available", lang))}</div>'
    return "".join(_provider_card(provider, active, lang) for provider in providers if isinstance(provider, Mapping))


def _provider_card(provider: Mapping[str, Any], active: str, lang: str) -> str:
    provider_id = str(provider.get("id") or "custom")
    health = str(provider.get("health") or "unknown")
    health_label = _provider_health_label(health, lang)
    latency = provider.get("last_latency_ms")
    model = str(provider.get("model") or "")
    reasoning_effort = str(provider.get("reasoning_effort") or ("medium" if provider_id in {"morecode", "openai"} else ""))
    models = provider.get("available_models") if isinstance(provider.get("available_models"), list) else []
    return f"""
    <article class="metric-card" data-provider-card data-label="{escape(str(provider.get("label") or provider_id))}">
      <span>{escape(str(provider.get("label") or provider_id))}{' · active' if provider_id == active else ''}</span>
      <strong data-provider-health>{escape(health_label)}</strong>
      <p>{escape(t("provider.latency", lang))}: {escape(str(latency) + 'ms' if latency is not None else '--')}</p>
      <input type="hidden" data-provider-field="id" value="{escape(provider_id)}">
      <input type="hidden" data-provider-field="type" value="{escape(str(provider.get("type") or provider_id))}">
      <input type="hidden" data-provider-field="reasoning_effort" value="{escape(reasoning_effort)}">
      <label>{escape(t("model.model", lang))}
        <input data-provider-field="model" list="models-{escape(provider_id)}" value="{escape(model)}" placeholder="{escape(t("provider.custom_model_placeholder", lang))}">
        <datalist id="models-{escape(provider_id)}">{''.join(f'<option value="{escape(str(m))}"></option>' for m in models)}</datalist>
      </label>
      <label>{escape(t("settings.base_url", lang))}<input data-provider-field="base_url" value="{escape(str(provider.get("base_url") or ""))}"></label>
      <label>{escape(t("settings.api_key", lang))}<input data-provider-field="api_key" type="password" placeholder="{escape("saved" if provider.get("api_key") else "not stored")}"></label>
      <div class="button-row"><button class="secondary-button" type="button" data-test-provider>{escape(t("settings.test", lang))}</button></div>
    </article>
    """


def _provider_health_label(health: str, lang: str) -> str:
    normalized = str(health or "unknown").lower()
    labels = {
        "unknown": t("provider.unknown", lang),
        "healthy": t("provider.reachable", lang),
        "reachable": t("provider.reachable", lang),
        "error": t("provider.error", lang),
        "not_configured": t("provider.needs_config", lang),
    }
    return labels.get(normalized, normalized.replace("_", " ").title())


def _provider_options(providers: list[Any], active: str) -> str:
    if not providers:
        return '<option value="openai">OpenAI-compatible</option><option value="claude">Anthropic</option><option value="ollama">Ollama</option><option value="custom">Custom</option>'
    return "\n".join(
        f'<option value="{escape(str(item.get("id")))}"{_selected(item.get("id"), active)}>{escape(str(item.get("label") or item.get("id")))}</option>'
        for item in providers
        if isinstance(item, Mapping)
    )


def _fastest_provider(providers: list[Mapping[str, Any]], lang: str) -> str:
    fastest = sorted((p for p in providers if p.get("last_latency_ms") is not None), key=lambda p: int(p.get("last_latency_ms") or 0))
    if not fastest:
        return t("provider.none", lang)
    return f"{fastest[0].get('label') or fastest[0].get('id')} · {fastest[0].get('last_latency_ms')}ms"


def _config_positions(assets: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = assets.get("portfolio_json") if isinstance(assets, Mapping) else "{}"
    try:
        data = json.loads(str(raw or "{}"))
    except json.JSONDecodeError:
        data = {}
    positions = data.get("positions") if isinstance(data, Mapping) else []
    return positions if isinstance(positions, list) else []


def _asset_rows(positions: list[Mapping[str, Any]], lang: str) -> str:
    rows = positions or [{}]
    return "".join(_asset_row(item if isinstance(item, Mapping) else {}, lang) for item in rows)


def _asset_row(item: Mapping[str, Any], lang: str) -> str:
    return f"""
    <div class="asset-row" data-asset-row>
      <label>{escape(t("setup.asset", lang))}<input data-asset-field="asset" value="{escape(str(item.get("asset") or ""))}" placeholder="AAPL"></label>
      <label>{escape(t("setup.market", lang))}<input data-asset-field="market" value="{escape(str(item.get("market") or ""))}" placeholder="US"></label>
      <label>{escape(t("setup.percentage", lang))}<input data-asset-field="portfolio_percentage" type="number" min="0" max="100" step="0.1" value="{escape(str(item.get("portfolio_percentage") or ""))}"></label>
      <label>{escape(t("setup.theme", lang))}<input data-asset-field="theme" value="{escape(str(item.get("theme") or ""))}" placeholder="AI"></label>
      <label>{escape(t("setup.role", lang))}<input data-asset-field="role" value="{escape(str(item.get("role") or ""))}" placeholder="Core"></label>
    </div>
    """


def _setup_step(number: str, title: str, body: str) -> str:
    return f'<section class="focus-card"><span class="kicker">{escape(number)}</span><h2>{escape(title)}</h2><p>{escape(body)}</p></section>'


def _position_rows(positions: list[Any], lang: str) -> str:
    if not positions:
        return f'<li>{escape(t("portfolio.no_percentages", lang))}</li>'
    rows = []
    for item in positions[:8]:
        if isinstance(item, Mapping):
            rows.append(f'<li><strong>{escape(str(item.get("asset") or "Asset"))}</strong> · {escape(_pct_text(item.get("portfolio_percentage")))}<br>{escape(str(item.get("theme") or "Unspecified"))} · {escape(str(item.get("risk_note") or t("empty.context", lang)))}</li>')
    return "".join(rows)


def _expert_payload(state: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "regime_state": state.get("regime_state"),
        "trust_index": state.get("trust_index"),
        "last_decision_packet": state.get("last_decision_packet"),
        "market_intelligence": state.get("market_intelligence"),
        "proactive_update_state": state.get("proactive_update_state"),
    }


def _duration_text(value: Any, lang: str) -> str:
    seconds = _num(value, 0)
    if seconds >= 3600:
        hours = seconds / 3600
        return f"{hours:.1f} 小时" if lang == "zh" else f"{hours:.1f}h"
    if seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.0f} 分钟" if lang == "zh" else f"{minutes:.0f}m"
    return f"{seconds:.0f} 秒" if lang == "zh" else f"{seconds:.0f}s"


def _selected(value: Any, selected: Any) -> str:
    return " selected" if str(value) == str(selected) else ""


def _num(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback
