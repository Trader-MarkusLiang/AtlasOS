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
from ui.presentation.home_intelligence import build_home_intelligence


ATLAS_ACTIONS = {"observe", "hold", "reduce", "build", "accumulate"}
ARCHITECTURE_MAPS = {
    "en": "atlas-os-architecture-20260709.png",
    "zh": "atlas-os-architecture-cn-20260709.png",
}

HOME_INTELLIGENCE_TEXT = {
    "en": {
        "view_modes": "Home view modes",
        "brief": "Brief",
        "outlook": "Outlook",
        "candidates": "Candidates",
        "expert": "Expert",
        "current_state": "Current State",
        "forward_outlook": "Forward Outlook",
        "portfolio_impact": "Portfolio Impact",
        "research_candidates": "Research Candidates",
        "forecast_accountability": "Forecast Accountability",
        "expert_analysis": "Expert Analysis",
        "key_drivers": "Key drivers",
        "market_outlook": "Market Outlook",
        "scenario_map": "Scenario Map",
        "base_case": "Base Case",
        "upside_scenario": "Upside Scenario",
        "downside_scenario": "Downside Scenario",
        "horizon": "Horizon",
        "source": "Source",
        "invalidation_conditions": "Invalidation Conditions",
        "insufficient_evidence": "insufficient evidence",
        "insufficient_outlook": "Insufficient evidence to form a forward view.",
        "why_holdings_matter": "Why this matters to current holdings",
        "candidate_pool": "Candidate Pool",
        "view_full_candidate_pool": "View Full Candidate Pool",
        "candidate_safety": "Candidate Ranking is not a trading action. It shows research priority only.",
        "all": "All",
        "portfolio_related": "Portfolio-related",
        "high_priority": "High priority",
        "new": "New",
        "changed_recently": "Changed recently",
        "asset_theme": "Asset / theme",
        "priority": "Priority",
        "relevance": "Relevance",
        "evidence_strength": "Evidence strength",
        "thesis_direction": "Thesis direction",
        "status": "Status",
        "details": "Details",
        "no_candidates": "No research candidate pool has formed yet.",
        "candidate_changes": "Candidate Changes",
        "no_candidate_changes": "No recent candidate changes recorded in source.",
        "forecast_ledger": "Forecast Ledger",
        "forecast_accountability_title": "Does Atlas deserve trust?",
        "view_all_forecasts": "View all forecasts",
        "does_atlas_deserve_trust": "Trust check",
        "low_sample": "Sample is still small; calibration is directional only.",
        "latest_open": "Latest open forecast",
        "no_forecasts": "Atlas has not accumulated enough verifiable forecasts yet.",
        "causal_chain": "Causal Chain",
        "hypothesis_state": "Hypothesis State",
        "regime_state": "Regime State",
        "confidence_composition": "Confidence Composition",
        "data_quality": "Data Quality",
        "portfolio_sensitivity": "Portfolio Sensitivity",
        "forecast_evidence": "Forecast Evidence",
        "raw_evidence": "Raw Evidence",
        "expand_raw": "Raw evidence",
        "dominant_edges": "Dominant edges",
        "active_hypothesis": "Active hypothesis",
        "competing_hypotheses": "Competing hypotheses",
        "recent_change": "Recent change",
        "live_channels": "Live channels",
        "simulated_channels": "Simulated channels",
        "missing_channels": "Missing channels",
        "stale_channels": "Stale channels",
        "forecast_vs_outlook": "Market Outlook is the current forward view. Forecast Ledger is the accountability record.",
        "research_only": "Research",
        "watch": "Watch",
        "elevated": "Elevated",
        "deprioritized": "Deprioritized",
        "observe": "Observe",
    },
    "zh": {
        "view_modes": "首页视图切换",
        "brief": "简报",
        "outlook": "前瞻",
        "candidates": "候选",
        "expert": "专家",
        "current_state": "当前状态",
        "forward_outlook": "前瞻判断",
        "portfolio_impact": "组合影响",
        "research_candidates": "研究候选",
        "forecast_accountability": "预测与兑现",
        "expert_analysis": "专家分析",
        "key_drivers": "关键驱动",
        "market_outlook": "市场前瞻",
        "scenario_map": "情景图",
        "base_case": "基准情景",
        "upside_scenario": "上行情景",
        "downside_scenario": "下行情景",
        "horizon": "观察周期",
        "source": "来源",
        "invalidation_conditions": "失效条件",
        "insufficient_evidence": "证据不足",
        "insufficient_outlook": "当前证据不足，无法形成更强前瞻判断。",
        "why_holdings_matter": "为什么这会影响当前持仓",
        "candidate_pool": "候选池",
        "view_full_candidate_pool": "查看完整候选池",
        "candidate_safety": "候选排序不是交易动作，只代表研究优先级。",
        "all": "全部",
        "portfolio_related": "组合相关",
        "high_priority": "高优先级",
        "new": "新进入",
        "changed_recently": "近期变化",
        "asset_theme": "资产 / 主题",
        "priority": "优先级",
        "relevance": "相关性",
        "evidence_strength": "证据强度",
        "thesis_direction": "论点方向",
        "status": "状态",
        "details": "详情",
        "no_candidates": "尚未形成研究候选池。",
        "candidate_changes": "候选变化",
        "no_candidate_changes": "来源中没有记录近期候选变化。",
        "forecast_ledger": "预测账本",
        "forecast_accountability_title": "Atlas 是否值得信任？",
        "view_all_forecasts": "查看全部预测",
        "does_atlas_deserve_trust": "信任检查",
        "low_sample": "样本仍然较少，校准只能作为方向参考。",
        "latest_open": "最新未完成预测",
        "no_forecasts": "Atlas 尚未积累足够的可验证预测。",
        "causal_chain": "因果链",
        "hypothesis_state": "假设状态",
        "regime_state": "市场状态",
        "confidence_composition": "置信度构成",
        "data_quality": "数据质量",
        "portfolio_sensitivity": "组合敏感性",
        "forecast_evidence": "预测证据",
        "raw_evidence": "原始证据",
        "expand_raw": "原始证据",
        "dominant_edges": "主导边",
        "active_hypothesis": "主假设",
        "competing_hypotheses": "竞争假设",
        "recent_change": "近期变化",
        "live_channels": "实时通道",
        "simulated_channels": "模拟通道",
        "missing_channels": "缺失通道",
        "stale_channels": "过期通道",
        "forecast_vs_outlook": "市场前瞻是当前对未来的判断；预测账本是已记录、可验证的责任链。",
        "research_only": "研究",
        "watch": "观察",
        "elevated": "重点研究",
        "deprioritized": "降优先级",
        "observe": "观察",
    },
}


def home_content(state: Mapping[str, Any]) -> str:
    lang = current_language()
    intelligence = build_home_intelligence(state)
    practical = intelligence["practical_brief"]
    expert = intelligence["expert_analysis"]
    action = _mapping(practical.get("action_today"))
    core = _mapping(practical.get("core_judgment"))
    predictions = _mapping(practical.get("strongest_predictions"))
    bottlenecks = _mapping(practical.get("ai_bottleneck_index"))
    relay = _mapping(practical.get("capital_relay"))
    holdings = _mapping(practical.get("current_holdings"))
    allocation = _mapping(practical.get("capital_allocation"))
    triggers = _mapping(practical.get("waiting_triggers"))
    research = _mapping(practical.get("research_tasks"))
    truth = _mapping(practical.get("candidate_source_truth"))
    alerts = _mapping(practical.get("intelligence_alerts"))
    counter = _mapping(practical.get("counter_argument"))
    review = _mapping(practical.get("review_plan"))
    forecast = _mapping(practical.get("forecast_accountability"))
    portfolio_command = _mapping(practical.get("portfolio_command"))
    material_changes = _mapping(practical.get("material_changes"))
    reasoning_chain = _mapping(practical.get("reasoning_chain"))
    scenarios = _mapping(practical.get("scenario_outlook"))
    playbook = _mapping(practical.get("action_playbook"))
    candidate_board = _mapping(practical.get("candidate_board"))
    return f"""
    {_home_intelligence_style()}
    <main class="decision-home-shell practical-brief-shell investor-home" data-home-layout="portfolio-first-investor-brief">
      <section class="portfolio-first-viewport" id="home-first-viewport" aria-label="{escape(_brief_copy("portfolio_command", lang))}">
        <article class="decision-card portfolio-command-card" id="home-portfolio-command" data-practical-section="portfolio_command">
          <div class="journey-step"><span>01</span>{escape(_brief_copy("portfolio_command", lang))}</div>
          <div class="home-section-header">
            <div>
              <span class="kicker">{escape(_brief_copy("portfolio_state_first", lang))}</span>
              <h1>{escape(_brief_copy("portfolio_overview", lang))}</h1>
            </div>
            <div class="portfolio-header-status">
              <div class="posture-pill">{escape(_localized(portfolio_command.get("posture"), lang))}</div>
              <small>{escape(_brief_copy("action_review_today", lang))}</small>
              <strong>{escape(_runtime_label(portfolio_command.get("action_status") or "NO", lang))}</strong>
            </div>
          </div>
          {_portfolio_command_view(portfolio_command, lang)}
        </article>

        <article class="decision-card holdings-primary-card" id="home-current-holdings" data-practical-section="current_holdings">
          <div class="journey-step"><span>02</span>{escape(_brief_copy("current_holdings", lang))}</div>
          <div class="home-section-header">
            <div>
              <h2>{escape(_brief_copy("actual_configured_holdings", lang))}</h2>
              <p class="home-safety-note">{escape(_brief_copy("privacy_percent_only", lang))}</p>
            </div>
          </div>
          {_holding_action_board(holdings, lang)}
        </article>

        <article class="decision-card action-today-card" id="home-action-today" data-practical-section="action_today">
          <div class="journey-step"><span>03</span>{escape(_brief_copy("action_today", lang))}</div>
          <span class="kicker">{escape(_brief_copy("first_answer", lang))}</span>
          <h1 class="action-answer">{escape(_runtime_label(action.get("status") or "NO", lang))}</h1>
          <div class="posture-pill">{escape(_localized(action.get("posture_label"), lang))}</div>
          <p class="decision-change">{escape(_localized(action.get("reason"), lang))}</p>
          <p class="home-safety-note">{escape(_localized(action.get("helper"), lang))}</p>
        </article>

        <article class="decision-card core-judgment-card" id="home-core-judgment" data-practical-section="core_judgment">
          <div class="journey-step"><span>04</span>{escape(_brief_copy("core_judgment", lang))}</div>
          <span class="kicker">{escape(_brief_copy("one_total_judgment", lang))}</span>
          <h2>{escape(_localized(core.get("headline"), lang))}</h2>
          <p>{escape(_localized(core.get("supporting_sentence"), lang))}</p>
        </article>
      </section>

      <section class="investor-evidence-grid" aria-label="{escape(_brief_copy("what_changed", lang))}">
        <article class="decision-support-card material-change-card" id="home-material-changes" data-practical-section="material_changes">
          <div class="journey-step"><span>05</span>{escape(_brief_copy("what_changed", lang))}</div>
          <div class="home-section-header">
            <div>
              <h2>{escape(_brief_copy("material_evidence", lang))}</h2>
              <p class="home-safety-note">{escape(_brief_copy("news_not_action", lang))}</p>
            </div>
            <a class="secondary-button" href="/markets">{escape(_brief_copy("view_market_evidence", lang))}</a>
          </div>
          {_material_changes_view(material_changes, lang)}
        </article>

        <article class="decision-support-card reasoning-chain-card" id="home-reasoning-chain" data-practical-section="reasoning_chain">
          <div class="journey-step"><span>06</span>{escape(_brief_copy("reasoning_chain", lang))}</div>
          <h2>{escape(_brief_copy("from_signal_to_decision", lang))}</h2>
          {_reasoning_chain_view(reasoning_chain, lang)}
        </article>
      </section>

      <section class="scenario-section" aria-label="{escape(_brief_copy("scenario_outlook", lang))}">
        <article class="decision-support-card scenario-outlook-card" id="home-scenario-outlook" data-practical-section="scenario_outlook">
          <div class="journey-step"><span>07</span>{escape(_brief_copy("scenario_outlook", lang))}</div>
          <div class="home-section-header">
            <div><h2>{escape(_brief_copy("four_scenarios", lang))}</h2><p class="home-safety-note">{escape(_brief_copy("no_uncalibrated_probability", lang))}</p></div>
          </div>
          {_scenario_outlook_view(scenarios, lang)}
        </article>

        <article class="decision-support-card action-playbook-card" id="home-action-playbook" data-practical-section="action_playbook">
          <div class="journey-step"><span>08</span>{escape(_brief_copy("conditional_actions", lang))}</div>
          <h2>{escape(_brief_copy("scenario_action_playbook", lang))}</h2>
          {_action_playbook_view(playbook, lang)}
        </article>
      </section>

      <section class="candidate-score-section">
        <article class="decision-support-card" id="home-candidate-board" data-practical-section="candidate_board">
          <div class="journey-step"><span>09</span>{escape(_brief_copy("candidate_board", lang))}</div>
          <div class="home-section-header">
            <div><h2>{escape(_brief_copy("candidate_score_basis", lang))}</h2><p class="home-safety-note">{escape(_brief_copy("candidate_not_authority", lang))}</p></div>
            <a class="secondary-button" href="/candidates">{escape(_home_label("view_full_candidate_pool", lang))}</a>
          </div>
          {_candidate_score_board_view(candidate_board, lang)}
        </article>
      </section>

      <section class="forecast-compact-card" id="home-forecast-accountability" data-accountability-block="forecast">
        <div class="home-section-header">
          <div>
            <span class="journey-step"><span>10</span>{escape(_home_label("forecast_accountability", lang))}</span>
            <h2>{escape(_brief_copy("forecast_compact", lang))}</h2>
          </div>
          <div class="button-row">
            <a class="secondary-button" href="/predictions">{escape(_home_label("view_all_forecasts", lang))}</a>
            <a class="secondary-button" href="/learning">{escape(_brief_copy("view_learning", lang))}</a>
          </div>
        </div>
        {_forecast_compact_strip(forecast, lang)}
        <div class="forecast-learning-row">
          <p><strong>{escape(_brief_copy("recent_miss", lang))}:</strong> {escape(_localized(forecast.get("recent_miss"), lang))}</p>
          <p><strong>{escape(_brief_copy("changed_afterward", lang))}:</strong> {escape(_localized(forecast.get("what_changed_afterward"), lang))}</p>
        </div>
      </section>

      <details class="supporting-context" id="home-supporting-context">
        <summary>{escape(_brief_copy("supporting_context", lang))}</summary>
        <div class="supporting-context-grid">
          <article class="decision-support-card" id="home-ai-bottleneck-index"><h2>{escape(_brief_copy("bottleneck_index", lang))}</h2><p class="home-safety-note">{escape(_localized(bottlenecks.get("honest_label"), lang))}</p>{_bottleneck_index_table(bottlenecks, lang)}</article>
          <article class="decision-support-card" id="home-capital-relay"><h2>{escape(_localized(relay.get("current_stage"), lang))}</h2><p class="home-safety-note">{escape(_localized(relay.get("distinction"), lang))}</p>{_capital_relay_view(relay, lang)}</article>
          <article class="decision-support-card" id="home-capital-allocation"><h2>{escape(_brief_copy("capital_allocation", lang))}</h2>{_capital_allocation_panel(allocation, lang)}</article>
          <article class="decision-support-card" id="home-waiting-triggers"><h2>{escape(_brief_copy("waiting_triggers", lang))}</h2>{_waiting_trigger_table(triggers, lang)}</article>
          <article class="decision-support-card" id="home-research-tasks"><h2>{escape(_brief_copy("research_tasks", lang))}</h2><p class="home-safety-note">{escape(_localized(truth.get("label"), lang))}</p>{_research_task_cards(research, lang)}</article>
          <article class="decision-support-card" id="home-intelligence-alerts"><h2>{escape(_brief_copy("intelligence_alerts", lang))}</h2>{_intelligence_alert_cards(alerts, lang)}</article>
          <article class="decision-support-card" id="home-counter-argument"><h2>{escape(_brief_copy("counter_argument", lang))}</h2>{_counter_argument_view(counter, lang)}</article>
          <article class="decision-support-card" id="home-review-plan"><h2>{escape(_brief_copy("review_plan", lang))}</h2>{_review_plan_view(review, lang)}</article>
        </div>
      </details>

      <section class="home-expert-secondary" id="home-expert-analysis" data-expert-block="secondary_collapsed">
        <div class="home-section-header">
          <div>
            <span class="kicker">{escape(_brief_copy("secondary_detail", lang))}</span>
            <h2>{escape(_home_label("expert_analysis", lang))}</h2>
          </div>
        </div>
        {_expert_analysis_panel(expert, lang)}
      </section>
    </main>
    {_home_intelligence_script(include_candidate_filters=False)}
    """


def _portfolio_command_view(command: Mapping[str, Any], lang: str) -> str:
    metrics = [
        (_brief_copy("configured_exposure", lang), _pct_text(command.get("exposure_pct"))),
        (_brief_copy("unassigned_capital", lang), _pct_text(command.get("unassigned_pct"))),
        (_brief_copy("portfolio_consistency", lang), _runtime_label(command.get("portfolio_consistency") or "Unknown", lang)),
        (_brief_copy("usable_market_evidence", lang), f"{_mapping(command.get('market_evidence')).get('usable', 0)}/{_mapping(command.get('market_evidence')).get('total', 0)}"),
    ]
    metric_html = "".join(f'<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>' for label, value in metrics)
    largest = _mapping(command.get("largest_theme"))
    market_rows = "".join(
        f'<li><span>{escape(str(name))}</span><strong>{escape(_pct_text(value))}</strong></li>'
        for name, value in _mapping(command.get("market_concentration")).items()
    )
    return f"""
    <div class="portfolio-command-metrics">{metric_html}</div>
    <div class="portfolio-command-analysis">
      <div><span>{escape(_brief_copy("largest_theme", lang))}</span><strong>{escape(str(largest.get("theme") or "Unknown"))} · {escape(_pct_text(largest.get("exposure_pct")))}</strong></div>
      <div><span>{escape(_brief_copy("liquidity_sensitivity", lang))}</span><strong>{escape(_runtime_label(command.get("liquidity_sensitivity") or "Unknown", lang))}</strong></div>
      <div><span>{escape(_brief_copy("regime_sensitivity", lang))}</span><strong>{escape(_runtime_label(command.get("regime_sensitivity") or "Unknown", lang))}</strong></div>
      <ul>{market_rows}</ul>
    </div>
    <div class="portfolio-risk-callout"><span>{escape(_brief_copy("primary_portfolio_risk", lang))}</span><p>{escape(_localized(command.get("primary_risk"), lang))}</p></div>
    <p class="decision-change">{escape(_localized(command.get("action_reason"), lang))}</p>
    """


def _material_changes_view(changes: Mapping[str, Any], lang: str) -> str:
    items = [_mapping(item) for item in _list(changes.get("items")) if isinstance(item, Mapping)]
    if not items:
        return f'<div class="empty-state">{escape(_localized(changes.get("empty_message"), lang))}</div>'
    cards = []
    for item in items[:8]:
        url = str(item.get("source_url") or "")
        source = escape(str(item.get("source") or "Data Missing"))
        source_html = f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{source}</a>' if url.startswith("http") else source
        affected = ", ".join(str(value) for value in _list(item.get("affected_assets")) + _list(item.get("affected_themes")) if value)
        cards.append(
            f"""
            <article class="material-evidence-item">
              <div class="evidence-truth-row"><span>{escape(_runtime_label(item.get("classification") or "UNVERIFIED", lang))}</span><em>{escape(_runtime_label(item.get("freshness") or "Unknown", lang))}</em></div>
              <h3>{escape(str(item.get("headline") or "Data Missing"))}</h3>
              <dl>
                <div><dt>{escape(_brief_copy("source", lang))}</dt><dd>{source_html}</dd></div>
                <div><dt>{escape(_brief_copy("published_at", lang))}</dt><dd>{escape(str(item.get("timestamp") or "Unknown"))}</dd></div>
                <div><dt>{escape(_brief_copy("affected_scope", lang))}</dt><dd>{escape(affected or str(item.get("world_model_node") or "Unknown"))}</dd></div>
                <div><dt>{escape(_brief_copy("thesis_change", lang))}</dt><dd>{escape(_runtime_label(item.get("thesis_changed") or "UNASSESSED", lang))}</dd></div>
              </dl>
            </article>
            """
        )
    return '<div class="material-evidence-list">' + "".join(cards) + "</div>"


def _reasoning_chain_view(reasoning: Mapping[str, Any], lang: str) -> str:
    labels = {
        "en": {"signal": "Signal", "evidence": "Evidence", "structure": "Structural interpretation", "causal": "Causal drivers", "thesis": "Thesis impact", "portfolio": "Portfolio impact", "counter": "Counter-evidence", "missing": "Missing evidence", "conclusion": "Conclusion"},
        "zh": {"signal": "信号", "evidence": "证据", "structure": "结构解释", "causal": "因果驱动", "thesis": "论点影响", "portfolio": "组合影响", "counter": "反方证据", "missing": "缺失证据", "conclusion": "结论"},
    }[lang]
    rows = []
    for index, step in enumerate(_list(reasoning.get("steps")), start=1):
        if not isinstance(step, Mapping):
            continue
        key = str(step.get("key") or "")
        rows.append(f'<li><span>{index:02d}</span><div><small>{escape(labels.get(key, key))} · {escape(_runtime_label(step.get("truth") or "UNVERIFIED", lang))}</small><p>{escape(_runtime_label(step.get("value") or "Data Missing", lang))}</p></div></li>')
    return '<ol class="investor-reasoning-chain">' + "".join(rows) + "</ol>"


def _scenario_outlook_view(scenarios: Mapping[str, Any], lang: str) -> str:
    names = {
        "en": {"base": "Base", "upside": "Upside continuation", "downside": "Downside acceleration", "range": "Range / volatility"},
        "zh": {"base": "基准情景", "upside": "上行延续", "downside": "下行加速", "range": "震荡 / 波动"},
    }[lang]
    cards = []
    for item in _list(scenarios.get("items")):
        if not isinstance(item, Mapping):
            continue
        key = str(item.get("key") or "base")
        drivers = "".join(f"<li>{escape(_localized(value, lang))}</li>" for value in _list(item.get("drivers")))
        invalidation = "".join(f"<li>{escape(_localized(value, lang))}</li>" for value in _list(item.get("invalidation")))
        cards.append(f"""
        <article class="scenario-card scenario-{escape(key)}">
          <span>{escape(names.get(key, key))}</span>
          <h3>{escape(_localized(item.get("statement"), lang))}</h3>
          <div><small>{escape(_brief_copy("supporting_drivers", lang))}</small><ul>{drivers}</ul></div>
          <div><small>{escape(_brief_copy("invalidation", lang))}</small><ul>{invalidation}</ul></div>
          <dl><dt>{escape(_brief_copy("horizon", lang))}</dt><dd>{escape(_localized(item.get("horizon") or "Unknown", lang))}</dd><dt>{escape(_brief_copy("evidence_confidence", lang))}</dt><dd>{escape(_localized(item.get("evidence_confidence") or "Limited", lang))}</dd></dl>
        </article>
        """)
    return '<div class="scenario-grid">' + "".join(cards) + "</div>"


def _action_playbook_view(playbook: Mapping[str, Any], lang: str) -> str:
    scenario_names = {"base": "基准" if lang == "zh" else "Base", "upside": "上行" if lang == "zh" else "Upside", "downside": "下行" if lang == "zh" else "Downside", "range": "震荡" if lang == "zh" else "Range"}
    rows = []
    for item in _list(playbook.get("items")):
        if not isinstance(item, Mapping):
            continue
        scenario = str(item.get("scenario") or "base")
        rows.append(f"""
        <tr>
          <td><strong>{escape(scenario_names.get(scenario, scenario))}</strong></td>
          <td>{escape(_localized(item.get("trigger") or "Unknown", lang))}</td>
          <td><span class="trigger-status">{escape(_runtime_label(item.get("posture") or "Observe", lang))}</span></td>
          <td>{escape(str(item.get("affected_holdings") or "Configured portfolio"))}</td>
          <td>{escape(_localized(item.get("cde_authority") or "Not created by runtime", lang))}</td>
          <td>{escape(_localized(item.get("limiting_factor") or "Unknown", lang))}</td>
        </tr>
        """)
    return f"""
    <div class="playbook-warning">{escape(_brief_copy("authority_warning", lang))}</div>
    <div class="table-scroll"><table class="practical-table action-playbook-table"><thead><tr><th>{escape(_brief_copy("scenario", lang))}</th><th>{escape(_brief_copy("trigger", lang))}</th><th>{escape(_brief_copy("posture", lang))}</th><th>{escape(_brief_copy("affected_holdings", lang))}</th><th>CDE</th><th>{escape(_brief_copy("limiting_factor", lang))}</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
    """


def _candidate_score_board_view(board: Mapping[str, Any], lang: str) -> str:
    validated = [item for item in _list(board.get("validated_items")) if isinstance(item, Mapping)]
    pending = [item for item in _list(board.get("pending_items")) if isinstance(item, Mapping)]
    rows = []
    for item in validated:
        if not isinstance(item, Mapping):
            continue
        rows.append(f"""
        <tr>
          <td><strong>{escape(str(item.get("candidate") or "Unknown"))}</strong><small>{escape(str(item.get("code") or ""))}</small></td>
          <td>{escape(_runtime_label(item.get("identity_status") or "Needs Validation", lang))}</td>
          <td>{escape(str(item.get("tier") or "N/A"))}</td>
          <td>{escape(_runtime_label(item.get("portfolio_overlap") or "Unknown", lang))}</td>
          <td>{escape(_runtime_label(item.get("evidence_quality") or "Unverified", lang))}</td>
          <td>{escape(_localized(item.get("market_confirmation"), lang))}</td>
        </tr>
        """)
    pending_rows = "".join(
        f'<li><strong>{escape(str(item.get("candidate") or "Unknown"))}</strong><span>{escape(_runtime_label(item.get("identity_status") or "Needs Validation", lang))} · {escape(str(item.get("tier") or "N/A"))}</span></li>'
        for item in pending
    )
    dimensions = " · ".join(str(item) for item in _list(board.get("score_dimensions")))
    return f"""
    <p class="candidate-coverage-note">{escape(_localized(board.get("coverage_note"), lang))}</p>
    <div class="table-scroll"><table class="practical-table candidate-score-table"><thead><tr><th>{escape(_brief_copy("candidate", lang))}</th><th>{escape(_brief_copy("identity", lang))}</th><th>{escape(_brief_copy("tier", lang))}</th><th>{escape(_brief_copy("portfolio_overlap", lang))}</th><th>{escape(_brief_copy("evidence", lang))}</th><th>{escape(_brief_copy("market_confirmation", lang))}</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
    <details class="pending-candidates" {'open' if not validated else ''}>
      <summary>{escape((_brief_copy("pending_candidates", lang)).format(count=len(pending)))}</summary>
      <ul>{pending_rows}</ul>
    </details>
    <details class="score-methodology"><summary>{escape(_brief_copy("score_methodology", lang))}</summary><p>{escape(dimensions)}</p><p>{escape(_localized((board.get("items") or [{}])[0].get("score_explanation") if board.get("items") else "", lang))}</p></details>
    """


def _home_label(key: str, lang: str) -> str:
    return HOME_INTELLIGENCE_TEXT.get(lang, HOME_INTELLIGENCE_TEXT["en"]).get(key, key.replace("_", " ").title())


def _journey_copy(key: str, lang: str) -> str:
    text = {
        "en": {
            "first_viewport": "Atlas user decision journey",
            "what_changed": "What changed?",
            "strongest_judgment": "What is Atlas's strongest judgment?",
            "portfolio_question": "What does this mean for me?",
            "focus_question": "What should I focus on now?",
            "view_change_question": "What would change the view?",
            "research_question": "What deserves deeper research?",
            "today_core_judgment": "Today's Core Judgment",
            "strongest_forward_view": "Strongest Forward View",
            "portfolio_relevance": "Portfolio Relevance",
            "decision_agenda": "Decision Agenda",
            "evidence_quality": "Evidence quality",
            "updated": "Updated",
            "falsification": "Falsification condition",
            "conviction_hierarchy": "Conviction Hierarchy",
            "level_1": "Level 1 · Core Judgment",
            "level_2": "Level 2 · Key Predictions",
            "level_3": "Level 3 · Watch Hypotheses",
            "level_4": "Level 4 · Research Candidates",
            "supporting": "Supporting decision evidence",
            "what_changes_view": "What Would Change the View",
            "positive_confirmation": "Positive confirmation",
            "negative_confirmation": "Negative confirmation",
            "top_three_research": "Today's Top 3 Research Priorities",
            "forecast_compact": "Forecast Accountability, compact",
            "view_learning": "View learning record",
            "recent_miss": "Recent miss",
            "changed_afterward": "What Atlas changed afterward",
            "secondary_detail": "Secondary detail",
            "shared_risk": "Primary shared risk",
            "most_sensitive": "Most sensitive holding",
            "strongest_buffer": "Strongest buffer",
            "why_now": "Why now",
            "evidence_change": "Evidence change",
            "relationship": "Portfolio relationship",
            "truth_label": "Priority truth",
            "open": "OPEN",
            "verified": "VERIFIED",
            "invalidated": "INVALIDATED",
            "inconclusive": "INCONCLUSIVE",
            "current_open": "Current open",
            "legacy_open": "Legacy unclassified",
            "matured": "Matured",
        },
        "zh": {
            "first_viewport": "Atlas 用户决策旅程",
            "what_changed": "发生了什么？",
            "strongest_judgment": "Atlas 最强判断是什么？",
            "portfolio_question": "这和我有什么关系？",
            "focus_question": "我现在该关注什么？",
            "view_change_question": "什么会改变判断？",
            "research_question": "哪里值得深入研究？",
            "today_core_judgment": "今日核心判断",
            "strongest_forward_view": "最强前瞻判断",
            "portfolio_relevance": "组合相关性",
            "decision_agenda": "决策议程",
            "evidence_quality": "证据质量",
            "updated": "更新时间",
            "falsification": "失效条件",
            "conviction_hierarchy": "判断强度层级",
            "level_1": "Level 1 · 核心判断",
            "level_2": "Level 2 · 关键预测",
            "level_3": "Level 3 · 观察假设",
            "level_4": "Level 4 · 研究候选",
            "supporting": "决策支撑证据",
            "what_changes_view": "什么会改变判断",
            "positive_confirmation": "支持增强",
            "negative_confirmation": "风险恶化",
            "top_three_research": "今天最值得深入研究 Top 3",
            "forecast_compact": "预测责任检查（精简）",
            "view_learning": "查看学习记录",
            "recent_miss": "近期失误",
            "changed_afterward": "Atlas 后续改变",
            "secondary_detail": "二级细节",
            "shared_risk": "主要共享风险",
            "most_sensitive": "最敏感持仓",
            "strongest_buffer": "主要缓冲",
            "why_now": "为什么现在看",
            "evidence_change": "证据变化",
            "relationship": "组合关系",
            "truth_label": "优先级真实性",
            "open": "进行中",
            "verified": "已验证",
            "invalidated": "已失效",
            "inconclusive": "无法判断",
            "current_open": "当前未完成",
            "legacy_open": "历史未分类",
            "matured": "已到期",
        },
    }
    return text.get(lang, text["en"]).get(key, key.replace("_", " ").title())


def _brief_copy(key: str, lang: str) -> str:
    text = {
        "en": {
            "portfolio_command": "Portfolio Command View",
            "portfolio_state_first": "Your capital and positions come first",
            "portfolio_overview": "Current Portfolio State",
            "action_review_today": "Decision review today",
            "configured_exposure": "Configured exposure",
            "unassigned_capital": "Unassigned capital",
            "portfolio_consistency": "Portfolio consistency",
            "usable_market_evidence": "Usable market evidence",
            "largest_theme": "Largest theme exposure",
            "liquidity_sensitivity": "Liquidity sensitivity",
            "regime_sensitivity": "Regime sensitivity",
            "primary_portfolio_risk": "Primary portfolio risk",
            "what_changed": "What materially changed",
            "material_evidence": "Latest Evidence That Matters",
            "news_not_action": "News is Signal, not Action. Only thesis-relevant changes appear here.",
            "view_market_evidence": "View market evidence",
            "published_at": "Published / observed",
            "affected_scope": "Affected scope",
            "thesis_change": "Thesis change",
            "reasoning_chain": "Atlas Reasoning Chain",
            "from_signal_to_decision": "From Signal to Conditional Conclusion",
            "scenario_outlook": "Scenario Outlook",
            "four_scenarios": "Four Accountable Scenarios",
            "no_uncalibrated_probability": "No precise probability is shown before forecast calibration is supported.",
            "supporting_drivers": "Supporting drivers",
            "evidence_confidence": "Evidence confidence",
            "conditional_actions": "Conditional Actions",
            "scenario_action_playbook": "Portfolio Action Playbook",
            "authority_warning": "CDE authority is permission, not action. Runtime has not created deployment authority.",
            "scenario": "Scenario",
            "trigger": "Trigger",
            "affected_holdings": "Affected holdings",
            "limiting_factor": "Limiting factor",
            "candidate_board": "Strategic Candidate Pool",
            "candidate_score_basis": "Candidate Priority and Score Basis",
            "candidate_not_authority": "Strategic Candidate Score ranks research priority; it is not CDE authority.",
            "candidate": "Candidate",
            "identity": "Identity",
            "tier": "Tier",
            "market_confirmation": "Market confirmation",
            "portfolio_overlap": "Portfolio overlap",
            "strategic_score": "Strategic score",
            "pending_candidates": "{count} candidates need identity or market-data validation",
            "score_methodology": "Scoring methodology and current limitation",
            "supporting_context": "Open supporting framework context",
            "first_viewport": "Practical Decision Brief",
            "first_answer": "First answer",
            "action_today": "Action Today?",
            "core_judgment": "Today's Core Judgment",
            "one_total_judgment": "One total judgment",
            "strongest_predictions": "Highest-Conviction Predictions",
            "max_three": "Maximum 3; evidence-labeled",
            "secondary": "Decision framework evidence",
            "bottleneck_index": "AI Bottleneck Index",
            "capital_relay": "Capital Relay",
            "current_holdings": "Current Holdings",
            "actual_configured_holdings": "Actual configured holdings only",
            "privacy_percent_only": "Private values follow local visibility settings and never enter Atlas reasoning or external LLMs.",
            "capital_allocation": "Capital Allocation Board",
            "operational": "Operational checks",
            "waiting_triggers": "Waiting Triggers",
            "trigger_progress": "Trigger Progress",
            "research_tasks": "Today's Research Tasks",
            "intelligence_alerts": "Intelligence & Alerts",
            "control": "Control and accountability",
            "counter_argument": "Counter Argument",
            "review_plan": "Review Plan",
            "forecast_compact": "Recent forecast accountability",
            "view_learning": "View learning record",
            "recent_miss": "Recent miss",
            "changed_afterward": "What Atlas changed afterward",
            "secondary_detail": "Secondary evidence depth",
            "judgment": "Judgment",
            "confidence": "Confidence",
            "evidence": "Evidence",
            "invalidation": "Invalidation",
            "source": "Source",
            "trend": "Trend",
            "key_change": "Key change",
            "evidence_type": "Evidence type",
            "posture": "Atlas posture",
            "why": "Why",
            "key_trigger": "Key trigger",
            "review_priority": "Review priority",
            "rebalance_today": "Rebalance today?",
            "funding_source": "Funding source",
            "destination": "Destination",
            "execution_style": "Execution style",
            "status": "Status",
            "question": "Question",
            "why_now": "Why now",
            "evidence_gap": "Evidence gap",
            "related": "Related asset / theme",
            "supporting_evidence": "Supporting evidence",
            "more_likely_if": "More likely if",
            "next_review": "Next review",
            "recheck": "Re-check",
            "forecast_due": "Forecast due",
            "empty_prediction": "No high-conviction prediction has enough evidence yet.",
        },
        "zh": {
            "portfolio_command": "组合指挥视图",
            "portfolio_state_first": "先看你的资本与持仓",
            "portfolio_overview": "当前组合状态",
            "action_review_today": "今日决策复核",
            "configured_exposure": "已配置暴露",
            "unassigned_capital": "未部署资金",
            "portfolio_consistency": "组合一致性",
            "usable_market_evidence": "可用市场证据",
            "largest_theme": "最大主题暴露",
            "liquidity_sensitivity": "流动性敏感度",
            "regime_sensitivity": "市场状态敏感度",
            "primary_portfolio_risk": "当前组合首要风险",
            "what_changed": "发生了什么重要变化",
            "material_evidence": "真正影响判断的最新证据",
            "news_not_action": "新闻只是信号，不是行动；这里只展示与论点相关的变化。",
            "view_market_evidence": "查看市场证据",
            "published_at": "发布 / 观测时间",
            "affected_scope": "影响范围",
            "thesis_change": "论点变化",
            "reasoning_chain": "Atlas 推理链",
            "from_signal_to_decision": "从信号到条件结论",
            "scenario_outlook": "情景推演",
            "four_scenarios": "四种可问责情景",
            "no_uncalibrated_probability": "预测校准未成立前，不展示看似精确的概率。",
            "supporting_drivers": "支持驱动",
            "evidence_confidence": "证据置信度",
            "conditional_actions": "条件行动",
            "scenario_action_playbook": "组合条件行动方案",
            "authority_warning": "CDE 权限只是许可，不是行动；当前运行时尚未创建资本部署权限。",
            "scenario": "情景",
            "trigger": "触发条件",
            "affected_holdings": "影响持仓",
            "limiting_factor": "限制因素",
            "candidate_board": "重点候选池",
            "candidate_score_basis": "候选优先级与评分依据",
            "candidate_not_authority": "Strategic Candidate Score 只代表研究优先级，不代表 CDE 资本权限。",
            "candidate": "候选",
            "identity": "身份校验",
            "tier": "等级",
            "market_confirmation": "市场确认",
            "portfolio_overlap": "组合重合度",
            "strategic_score": "战略候选评分",
            "pending_candidates": "{count} 个候选仍需身份或行情核验",
            "score_methodology": "评分方法与当前限制",
            "supporting_context": "展开底层框架与复核上下文",
            "first_viewport": "实际决策简报",
            "first_answer": "第一答案",
            "action_today": "今日是否行动",
            "core_judgment": "今日总判断",
            "one_total_judgment": "只保留一个总判断",
            "strongest_predictions": "最强预测",
            "max_three": "最多 3 条，必须标注证据",
            "secondary": "决策框架证据",
            "bottleneck_index": "AI 瓶颈指数",
            "capital_relay": "资本迁移",
            "current_holdings": "当前持仓",
            "actual_configured_holdings": "仅显示实际配置持仓",
            "privacy_percent_only": "私密数值遵循本地显示设置，不进入 Atlas 推理或外部 LLM。",
            "capital_allocation": "资金调度",
            "operational": "操作检查",
            "waiting_triggers": "等待触发条件",
            "trigger_progress": "触发进度",
            "research_tasks": "今日研究任务",
            "intelligence_alerts": "情报与预警",
            "control": "控制与问责",
            "counter_argument": "反方观点",
            "review_plan": "复盘计划",
            "forecast_compact": "近期预测责任检查",
            "view_learning": "查看学习记录",
            "recent_miss": "近期失误",
            "changed_afterward": "Atlas 后续改变",
            "secondary_detail": "二级证据深度",
            "judgment": "判断",
            "confidence": "置信度",
            "evidence": "核心证据",
            "invalidation": "失效条件",
            "source": "来源",
            "trend": "趋势",
            "key_change": "关键变化",
            "evidence_type": "证据类型",
            "posture": "Atlas 姿态",
            "why": "原因",
            "key_trigger": "关键触发",
            "review_priority": "复核优先级",
            "rebalance_today": "今天是否调仓",
            "funding_source": "潜在资金来源",
            "destination": "潜在资金去向",
            "execution_style": "建议执行方式",
            "status": "状态",
            "question": "问题",
            "why_now": "为什么现在",
            "evidence_gap": "证据缺口",
            "related": "相关资产 / 主题",
            "supporting_evidence": "支持证据",
            "more_likely_if": "何时更可能成立",
            "next_review": "下次复盘",
            "recheck": "重点检查",
            "forecast_due": "到期预测",
            "empty_prediction": "当前没有足够证据形成高强度预测。",
        },
    }
    return text.get(lang, text["en"]).get(key, key.replace("_", " ").title())


def _prediction_cards(predictions: Mapping[str, Any], lang: str) -> str:
    items = [item for item in _list(predictions.get("items")) if isinstance(item, Mapping)][:3]
    if not items:
        return f'<div class="empty-state practical-empty">{escape(_localized(predictions.get("empty_message"), lang) or _brief_copy("empty_prediction", lang))}</div>'
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append(
            f"""
            <article class="prediction-item" data-prediction="{index}">
              <div class="prediction-topline">
                <span class="priority-index">{index}</span>
                <div>
                  <h3>{escape(_localized(item.get("judgment"), lang))}</h3>
                  <p class="home-safety-note">{escape(_localized(item.get("quality_label"), lang))}</p>
                </div>
              </div>
              <div class="forward-metrics compact-metrics">
                <span><small>{escape(_brief_copy("confidence", lang))}</small><strong>{escape(str(item.get("confidence_text") or ""))}</strong></span>
                <span><small>{escape(_home_label("horizon", lang))}</small><strong>{escape(_horizon_label(item.get("horizon"), lang))}</strong></span>
              </div>
              <dl class="decision-dl">
                <dt>{escape(_brief_copy("evidence", lang))}</dt><dd>{escape(_join_evidence(item.get("evidence"), lang))}</dd>
                <dt>{escape(_brief_copy("invalidation", lang))}</dt><dd>{escape(_join_evidence(item.get("invalidation"), lang))}</dd>
              </dl>
            </article>
            """
        )
    return '<div class="prediction-stack">' + "".join(rows) + "</div>"


def _bottleneck_index_table(bottlenecks: Mapping[str, Any], lang: str) -> str:
    domains = [item for item in _list(bottlenecks.get("domains")) if isinstance(item, Mapping)]
    required = [item for item in domains if item.get("domain") in {"Memory", "Equipment", "Materials", "Bandwidth", "Power"}]
    if not required:
        return f'<div class="empty-state">{escape("AI Bottleneck Index unavailable" if lang == "en" else "AI 瓶颈指数不可用")}</div>'
    rows = []
    for item in required:
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(str(item.get("domain") or ""))}</strong></td>
              <td>{escape(str(item.get("strength") or ""))}</td>
              <td>{escape(_trend_label(str(item.get("trend") or ""), lang))}</td>
              <td>{escape(str(item.get("key_change") or ""))}</td>
            </tr>
            """
        )
    return f"""
    <table class="practical-table bottleneck-table">
      <thead><tr><th>Domain</th><th>Strength</th><th>{escape(_brief_copy("trend", lang))}</th><th>{escape(_brief_copy("key_change", lang))}</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def _capital_relay_view(relay: Mapping[str, Any], lang: str) -> str:
    path = [item for item in _list(relay.get("path")) if isinstance(item, Mapping)]
    if not path:
        return f'<div class="empty-state">{escape("Capital relay unconfirmed" if lang == "en" else "当前资本迁移尚未确认。")}</div>'
    nodes = []
    for item in path:
        state = str(item.get("state_zh") if lang == "zh" else item.get("state") or "")
        nodes.append(
            f"""
            <div class="relay-node">
              <strong>{escape(str(item.get("name") or ""))}</strong>
              <span>{escape(state)}</span>
              <small>{escape(str(item.get("evidence_type") or ""))}</small>
            </div>
            """
        )
    return '<div class="capital-relay-path">' + '<span class="relay-arrow">→</span>'.join(nodes) + "</div>"


def _holding_action_board(holdings: Mapping[str, Any], lang: str) -> str:
    items = [item for item in _list(holdings.get("holdings")) if isinstance(item, Mapping)]
    if not items:
        return f'<div class="empty-state">{escape(t("portfolio.no_percentages", lang))}</div>'
    rows = []
    for item in items:
        valuation = _mapping(item.get("valuation"))
        rows.append(
            f"""
            <article class="holding-brief-card" data-valuation-status="{escape(str(valuation.get('valuation_status') or 'LIMITED').lower())}">
              <div class="holding-valuation-column">
                <div class="holding-title-row">
                  <div><h3>{escape(str(item.get("asset") or ""))}</h3><p class="home-safety-note">{escape(_theme_label(item.get("theme"), lang))}</p></div>
                  <div class="allocation-badge"><small>{escape(_valuation_copy('configured_allocation', lang))}</small><strong>{escape(_pct_text(item.get("exposure_pct")))}</strong></div>
                </div>
                {_holding_valuation_view(valuation, lang)}
              </div>
              <div class="holding-decision-column">
                <span class="kicker">{escape(_valuation_copy('decision_context', lang))}</span>
                <dl class="decision-dl">
                  <dt>{escape(_brief_copy("posture", lang))}</dt><dd>{escape(_localized(item.get("posture_label"), lang))}</dd>
                  <dt>{escape(_brief_copy("why", lang))}</dt><dd>{escape(_localized(item.get("why"), lang))}</dd>
                  <dt>{escape(_brief_copy("key_trigger", lang))}</dt><dd>{escape(_localized(item.get("key_trigger"), lang))}</dd>
                  <dt>{escape(_brief_copy("review_priority", lang))}</dt><dd>{escape(_runtime_label(item.get("review_priority") or "", lang))}</dd>
                </dl>
              </div>
            </article>
            """
        )
    return _valuation_summary(_mapping(holdings.get("valuation_summary")), lang) + '<div class="holding-brief-grid">' + "".join(rows) + "</div>"


def _holding_valuation_view(valuation: Mapping[str, Any], lang: str) -> str:
    if not valuation:
        return f'<div class="valuation-empty">{escape(_valuation_copy("market_missing", lang))}</div>'
    currency = str(valuation.get("position_currency") or valuation.get("price_currency") or "")
    latest = valuation.get("latest_price")
    cost = valuation.get("average_cost_price")
    return_pct = valuation.get("unrealized_return_pct")
    price_comparison = _cost_price_comparison(cost, latest, currency, lang)
    pnl_bar = _pnl_diverging_bar(return_pct, lang)
    amounts = _amount_metrics(valuation, currency, lang)
    limitations = _valuation_limitations(_list(valuation.get("limitations")), lang)
    observed = str(valuation.get("observed_at") or _valuation_copy("time_missing", lang))
    source = str(valuation.get("source") or _valuation_copy("source_missing", lang))
    freshness = str(valuation.get("provider_status") or valuation.get("freshness") or "NOT_CONFIGURED")
    return f"""
    <div class="valuation-visuals">
      {price_comparison}
      {pnl_bar}
      {amounts}
    </div>
    <div class="valuation-provenance">
      <span class="freshness-badge freshness-{escape(freshness.lower())}">{escape(freshness.replace('_', ' '))}</span>
      <span>{escape(source)}</span>
      <time>{escape(observed)}</time>
    </div>
    {limitations}
    """


def _cost_price_comparison(cost: Any, latest: Any, currency: str, lang: str) -> str:
    if cost is None:
        return f'<div class="valuation-empty">{escape(_valuation_copy("cost_missing", lang))}</div>'
    if latest is None:
        return f'<div class="valuation-empty">{escape(_valuation_copy("market_missing", lang))}</div>'
    cost_num = _num(cost, 0)
    latest_num = _num(latest, 0)
    low = min(cost_num, latest_num)
    high = max(cost_num, latest_num)
    span = max(high - low, high * .08, .000001)
    floor = max(0, low - span * .45)
    ceiling = high + span * .45
    cost_left = max(3, min(97, (cost_num - floor) / max(ceiling - floor, .000001) * 100))
    latest_left = max(3, min(97, (latest_num - floor) / max(ceiling - floor, .000001) * 100))
    return f"""
    <div class="cost-price-chart" role="img" aria-label="{escape(_valuation_copy('cost_vs_price', lang))}">
      <div class="valuation-chart-head"><span>{escape(_valuation_copy('cost_vs_price', lang))}</span><small>{escape(currency)}</small></div>
      <div class="cost-price-values">
        <span><small>{escape(_valuation_copy('cost', lang))}</small><strong>{cost_num:,.2f}</strong></span>
        <span><small>{escape(_valuation_copy('latest', lang))}</small><strong>{latest_num:,.2f}</strong></span>
      </div>
      <div class="cost-price-track">
        <i class="cost-marker" style="left:{cost_left:.2f}%"><b></b></i>
        <i class="price-marker" style="left:{latest_left:.2f}%"><b></b></i>
      </div>
    </div>
    """


def _pnl_diverging_bar(value: Any, lang: str) -> str:
    if value is None:
        return f'<div class="valuation-empty">{escape(_valuation_copy("return_unavailable", lang))}</div>'
    number = _num(value, 0)
    width = min(50, abs(number) / 100 * 50)
    css = "gain" if number >= 0 else "loss"
    left = 50 if number >= 0 else 50 - width
    return f"""
    <div class="pnl-chart {css}" role="img" aria-label="{escape(_valuation_copy('unrealized_return', lang))} {number:+.2f}%">
      <div class="valuation-chart-head"><span>{escape(_valuation_copy('unrealized_return', lang))}</span><strong>{number:+.2f}%</strong></div>
      <div class="pnl-track"><i style="left:{left:.2f}%;width:{width:.2f}%"></i><b></b></div>
      <div class="pnl-axis"><span>-100%</span><span>0</span><span>+100%</span></div>
    </div>
    """


def _amount_metrics(valuation: Mapping[str, Any], currency: str, lang: str) -> str:
    quantity = valuation.get("quantity")
    market_value = valuation.get("current_market_value")
    pnl = valuation.get("unrealized_pnl_amount")
    if quantity is None and market_value is None and pnl is None:
        return ""
    metrics = []
    if quantity is not None:
        metrics.append((_valuation_copy("quantity", lang), f"{_num(quantity, 0):,.4f}".rstrip("0").rstrip(".")))
    if market_value is not None:
        metrics.append((f'{_valuation_copy("market_value", lang)} ({currency})', f'{_num(market_value, 0):,.2f}'))
    if pnl is not None:
        pnl_value = _num(pnl, 0)
        metrics.append((f'{_valuation_copy("pnl_amount", lang)} ({currency})', f'{"+" if pnl_value > 0 else ""}{pnl_value:,.2f}'))
    return '<div class="valuation-amount-grid">' + "".join(
        f'<span><small>{escape(label)}</small><strong>{escape(value)}</strong></span>' for label, value in metrics
    ) + '</div>'


def _valuation_limitations(limitations: list[Any], lang: str) -> str:
    visible = []
    for value in limitations:
        key = str(value or "")
        if key == "PRICE_NOT_LIVE":
            visible.append(_valuation_copy("price_delayed", lang))
        elif key == "AVERAGE_COST_NOT_CONFIGURED":
            visible.append(_valuation_copy("cost_missing", lang))
        elif key == "QUANTITY_NOT_CONFIGURED":
            visible.append(_valuation_copy("quantity_missing", lang))
        elif key == "MARKET_DATA_MISSING" or key == "MARKET_DATA_UNAVAILABLE":
            visible.append(_valuation_copy("market_missing", lang))
        elif key == "PRICE_COST_CURRENCY_MISMATCH":
            visible.append(_valuation_copy("currency_mismatch", lang))
        elif key == "IDENTITY_MISMATCH":
            visible.append(_valuation_copy("identity_mismatch", lang))
        elif key == "SIMULATED_PRICE_BLOCKED":
            visible.append(_valuation_copy("simulated_blocked", lang))
        elif key == "INVALID_PRIVATE_INPUT":
            visible.append(_valuation_copy("invalid_input", lang))
    unique = list(dict.fromkeys(visible))
    if not unique:
        return ""
    return '<ul class="valuation-limitations">' + "".join(f'<li>{escape(item)}</li>' for item in unique) + '</ul>'


def _valuation_summary(summary: Mapping[str, Any], lang: str) -> str:
    if not summary:
        return ""
    complete = summary.get("return_complete_positions", 0)
    total = summary.get("total_positions", 0)
    limitations = _list(summary.get("limitations"))
    fx_limited = "FX_DATA_MISSING_AGGREGATE_VALUATION_LIMITED" in limitations
    return f"""
    <div class="valuation-summary-strip">
      <span><small>{escape(_valuation_copy('return_coverage', lang))}</small><strong>{escape(str(complete))}/{escape(str(total))}</strong></span>
      <span><small>{escape(_valuation_copy('current_weight', lang))}</small><strong>{escape(_valuation_copy('unavailable', lang))}</strong></span>
      <p>{escape(_valuation_copy('fx_limited', lang) if fx_limited else _valuation_copy('weight_limited', lang))}</p>
    </div>
    """


def _valuation_copy(key: str, lang: str) -> str:
    text = {
        "en": {
            "configured_allocation": "Configured allocation", "decision_context": "Atlas decision context",
            "cost_vs_price": "Cost vs latest price", "cost": "Cost", "latest": "Latest",
            "unrealized_return": "Unrealized return", "quantity": "Quantity", "market_value": "Market value",
            "pnl_amount": "Unrealized PnL", "cost_missing": "Average cost not configured - PnL unavailable",
            "quantity_missing": "Return percentage available - Amount and live weight unavailable",
            "market_missing": "Market Data Missing or Unavailable - Valuation Limited",
            "price_delayed": "Latest price is delayed - Verify before acting",
            "currency_mismatch": "Price / Cost Currency Mismatch - PnL Blocked",
            "identity_mismatch": "Candidate Identity Mismatch - Valuation Blocked",
            "simulated_blocked": "Simulated price is not used for real PnL", "invalid_input": "Private position input is invalid",
            "return_unavailable": "Unrealized return unavailable", "time_missing": "Observation time unavailable",
            "source_missing": "Source unavailable", "return_coverage": "PnL coverage", "current_weight": "Estimated current weight",
            "unavailable": "Unavailable", "fx_limited": "FX Data Missing - Aggregate Valuation Limited",
            "weight_limited": "Current weight unavailable until quantity, complete prices, currency normalization, and cash value are available",
        },
        "zh": {
            "configured_allocation": "配置比例", "decision_context": "Atlas 决策上下文",
            "cost_vs_price": "成本价与最新价", "cost": "成本", "latest": "最新",
            "unrealized_return": "未实现盈亏", "quantity": "持仓数量", "market_value": "当前市值",
            "pnl_amount": "未实现盈亏金额", "cost_missing": "未配置平均成本，无法计算盈亏",
            "quantity_missing": "可显示盈亏比例；金额与实时权重不可用",
            "market_missing": "市场数据缺失或不可用，估值受限",
            "price_delayed": "最新价格为延迟数据，行动前请复核",
            "currency_mismatch": "价格与成本币种不一致，盈亏计算已阻止",
            "identity_mismatch": "标的身份不匹配，估值已阻止",
            "simulated_blocked": "模拟价格不用于真实盈亏", "invalid_input": "私密持仓输入无效",
            "return_unavailable": "未实现盈亏不可用", "time_missing": "观测时间不可用",
            "source_missing": "数据来源不可用", "return_coverage": "盈亏覆盖", "current_weight": "估算当前权重",
            "unavailable": "不可用", "fx_limited": "FX 数据缺失，组合汇总估值受限",
            "weight_limited": "需补齐数量、价格、币种归一化和现金价值后才能估算当前权重",
        },
    }
    return text.get(lang, text["en"]).get(key, key.replace("_", " "))


def _money(value: float, currency: str, *, signed: bool = False) -> str:
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:,.2f} {currency}".strip()


def _capital_allocation_panel(allocation: Mapping[str, Any], lang: str) -> str:
    sources = "".join(f"<li>{escape(_localized(item, lang))}</li>" for item in _list(allocation.get("source_of_funds")))
    flow = _mapping(allocation.get("funding_flow"))
    return f"""
    <dl class="decision-dl allocation-dl">
      <dt>{escape(_brief_copy("rebalance_today", lang))}</dt><dd><strong>{escape(str(allocation.get("rebalance_today") or "NO"))}</strong></dd>
      <dt>{escape(_brief_copy("funding_source", lang))}</dt><dd><ul class="plain-list">{sources}</ul></dd>
      <dt>{escape(_brief_copy("destination", lang))}</dt><dd>{escape(_localized(allocation.get("destination"), lang))}</dd>
      <dt>{escape(_brief_copy("trigger_progress", lang))}</dt><dd>{escape(str(allocation.get("trigger_status") or ""))}</dd>
      <dt>{escape(_brief_copy("execution_style", lang))}</dt><dd>{escape(_localized(allocation.get("execution_style"), lang))}</dd>
    </dl>
    <div class="funding-flow" aria-label="Funding Source to Destination">
      <span>{escape(_localized(flow.get("source"), lang))}</span>
      <strong>→</strong>
      <span>{escape(_localized(flow.get("destination"), lang))}</span>
      <p>{escape(_localized(flow.get("why"), lang))}</p>
    </div>
    """


def _waiting_trigger_table(triggers: Mapping[str, Any], lang: str) -> str:
    items = [item for item in _list(triggers.get("items")) if isinstance(item, Mapping)]
    rows = []
    for item in items:
        status = str(item.get("status") or "UNKNOWN")
        rows.append(
            f"""
            <tr>
              <td>{escape(_localized(item.get("condition"), lang))}</td>
              <td><span class="trigger-status status-{escape(status.lower().replace('_', '-'))}">{escape(_trigger_status_label(status, lang))}</span></td>
              <td>{escape(str(item.get("source") or ""))}</td>
            </tr>
            """
        )
    return f"""
    <table class="practical-table waiting-trigger-table">
      <thead><tr><th>{escape(_brief_copy("question", lang))}</th><th>{escape(_brief_copy("status", lang))}</th><th>{escape(_brief_copy("source", lang))}</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def _research_task_cards(research: Mapping[str, Any], lang: str) -> str:
    tasks = [item for item in _list(research.get("items")) if isinstance(item, Mapping)][:3]
    if not tasks:
        return f'<div class="empty-state">{escape("No research tasks" if lang == "en" else "暂无今日研究任务")}</div>'
    cards = []
    for index, item in enumerate(tasks, start=1):
        cards.append(
            f"""
            <article class="research-priority-card" data-research-task="{index}">
              <div class="research-item-main">
                <span class="priority-index">{index}</span>
                <div>
                  <h3>{escape(_localized(item.get("question"), lang))}</h3>
                  <p class="home-safety-note">{escape(str(item.get("related_asset_theme") or ""))}</p>
                </div>
              </div>
              <dl class="research-item-detail">
                <div><dt>{escape(_brief_copy("why_now", lang))}</dt><dd>{escape(_localized(item.get("why_now"), lang))}</dd></div>
                <div><dt>{escape(_brief_copy("evidence_gap", lang))}</dt><dd>{escape(_localized(item.get("evidence_gap"), lang))}</dd></div>
              </dl>
            </article>
            """
        )
    return '<div class="research-priority-list">' + "".join(cards) + "</div>"


def _intelligence_alert_cards(alerts: Mapping[str, Any], lang: str) -> str:
    items = [item for item in _list(alerts.get("items")) if isinstance(item, Mapping)][:5]
    if not items:
        return f'<div class="empty-state">{escape("No new alert" if lang == "en" else "暂无新增预警")}</div>'
    rows = "".join(
        f"""
        <li>
          <strong>{escape(_localized(item.get("category"), lang))}</strong>
          <span>{escape(_localized(item.get("message"), lang))}</span>
        </li>
        """
        for item in items
    )
    return f'<ul class="intelligence-alert-list">{rows}</ul>'


def _counter_argument_view(counter: Mapping[str, Any], lang: str) -> str:
    return f"""
    <dl class="decision-dl">
      <dt>{escape(_brief_copy("counter_argument", lang))}</dt><dd>{escape(_localized(counter.get("thesis"), lang))}</dd>
      <dt>{escape(_brief_copy("supporting_evidence", lang))}</dt><dd>{escape(_localized(counter.get("supporting_evidence"), lang))}</dd>
      <dt>{escape(_brief_copy("more_likely_if", lang))}</dt><dd>{escape(_localized(counter.get("more_likely_if"), lang))}</dd>
    </dl>
    """


def _review_plan_view(review: Mapping[str, Any], lang: str) -> str:
    recheck = "".join(f"<li>{escape(_localized(item, lang))}</li>" for item in _list(review.get("recheck")))
    trigger_rows = "".join(
        f"<li>{escape(_localized(_mapping(item).get('condition'), lang))} · {escape(_trigger_status_label(str(_mapping(item).get('status') or 'UNKNOWN'), lang))}</li>"
        for item in _list(review.get("triggers_may_change"))
        if isinstance(item, Mapping)
    )
    return f"""
    <dl class="decision-dl">
      <dt>{escape(_brief_copy("next_review", lang))}</dt><dd>{escape(_localized(review.get("next_review_time"), lang))}</dd>
      <dt>{escape(_brief_copy("recheck", lang))}</dt><dd><ul class="plain-list">{recheck}</ul></dd>
      <dt>{escape(_brief_copy("forecast_due", lang))}</dt><dd>{escape(str(review.get("forecast_due") or ""))}</dd>
      <dt>{escape(_brief_copy("waiting_triggers", lang))}</dt><dd><ul class="plain-list">{trigger_rows}</ul></dd>
    </dl>
    """


def _join_evidence(items: Any, lang: str) -> str:
    values = [str(item).replace("_", " ") for item in _list(items) if str(item).strip()]
    if not values:
        return _home_label("insufficient_evidence", lang)
    return " / ".join(values[:4])


def _trend_label(value: str, lang: str) -> str:
    labels = {
        "up": "↑" if lang == "zh" else "up",
        "flat": "→" if lang == "zh" else "flat",
        "watch": "观察" if lang == "zh" else "watch",
        "unknown": "未知" if lang == "zh" else "unknown",
    }
    return labels.get(value, value)


def _trigger_status_label(value: str, lang: str) -> str:
    normalized = value.upper()
    if lang == "zh":
        return {
            "MET": "已满足",
            "PARTIAL": "部分满足",
            "NOT_MET": "未满足",
            "UNKNOWN": "未知",
        }.get(normalized, value)
    return normalized.replace("_", " ")


def _localized(value: Any, lang: str) -> str:
    if isinstance(value, Mapping):
        text = value.get(lang) or value.get("en") or value.get("zh")
        return str(text or "")
    return str(value or "")


def _runtime_label(value: Any, lang: str) -> str:
    text = _localized(value, lang).strip()
    if lang != "zh":
        return text.replace("_", " ")
    labels = {
        "CONDITIONAL": "需要条件确认",
        "YES": "需要复核",
        "NO": "暂不需要",
        "PASS": "通过",
        "UNKNOWN": "尚不明确",
        "UNASSESSED": "尚未评估",
        "UNVERIFIED": "尚未验证",
        "VERIFIED": "已验证",
        "VALIDATED": "已核验",
        "NEEDS VALIDATION": "待核验",
        "DATA MISSING": "证据待补充",
        "LIVE": "实时",
        "DELAYED": "延迟",
        "CACHED": "缓存",
        "FAILED": "失败",
        "NOT CONFIGURED": "未配置",
        "LIVE OBSERVATION": "实时观测",
        "PROVIDER OBSERVATION": "数据源观测",
        "VERIFIED PROVIDER RESPONSE": "数据源响应已验证",
        "STRUCTURAL INTERPRETATION": "结构解释",
        "FRAMEWORK SNAPSHOT": "框架快照",
        "INFERENCE": "推断",
        "SIGNAL": "信号",
        "PORTFOLIO MAPPING": "组合映射",
        "CONDITIONAL CONCLUSION": "条件结论",
        "OBSERVE": "观察",
        "HOLD": "持有",
        "REDUCE": "降低",
        "BUILD": "建立",
        "ACCUMULATE": "积累",
        "LIMITED": "有限",
        "MEDIUM": "中",
        "HIGH": "高",
        "LOW": "低",
        "CURRENT HOLDING": "当前持仓",
        "RESEARCH POOL": "研究池",
        "NONE": "无直接重合",
    }
    normalized = text.replace("_", " ").upper()
    return labels.get(normalized, text.replace("_", " "))


def _theme_label(value: Any, lang: str) -> str:
    text = str(value or "")
    if lang != "zh":
        return text
    replacements = {
        "Semiconductor Materials": "半导体材料",
        "AI Hardware Manufacturing": "AI 硬件制造",
        "AI Infrastructure": "AI 基础设施",
        "Materials": "材料",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _localized_list_items(items: Any, lang: str) -> str:
    values = items if isinstance(items, list) else []
    return "".join(f"<li>{escape(_localized(item, lang))}</li>" for item in values)


def _horizon_label(value: Any, lang: str) -> str:
    text = str(value or "").strip()
    if lang == "zh":
        return {
            "next_runtime_cycle": "下一运行周期",
            "insufficient evidence": "证据不足",
        }.get(text, text.replace("_", " "))
    return text.replace("_", " ") if text else "next runtime cycle"


def _holding_label(holding: Mapping[str, Any], lang: str) -> str:
    asset = str(holding.get("asset") or ("未知" if lang == "zh" else "Unknown"))
    pct = _pct_text(holding.get("exposure_pct"))
    return f"{asset} · {pct}"


def _conviction_hierarchy_panel(hierarchy: Mapping[str, Any], lang: str) -> str:
    level_1 = hierarchy.get("level_1") if isinstance(hierarchy.get("level_1"), list) else []
    level_2 = hierarchy.get("level_2") if isinstance(hierarchy.get("level_2"), list) else []
    level_3 = hierarchy.get("level_3") if isinstance(hierarchy.get("level_3"), list) else []
    level_4 = hierarchy.get("level_4") if isinstance(hierarchy.get("level_4"), Mapping) else {}
    level1_html = "".join(
        f"<li>{escape(_localized(item.get('item'), lang))}</li>"
        for item in level_1
        if isinstance(item, Mapping)
    )
    level2_html = "".join(
        f"<li>{escape(_localized(item.get('statement'), lang))}<small>{escape(_horizon_label(item.get('horizon'), lang))} · {escape(_pct_text(float(item.get('confidence') or 0) * 100))}</small></li>"
        for item in level_2[:3]
        if isinstance(item, Mapping)
    )
    return f"""
    <details class="conviction-hierarchy" id="home-conviction-hierarchy">
      <summary>{escape(_journey_copy("conviction_hierarchy", lang))}</summary>
      <div class="conviction-grid">
        <div><strong>{escape(_journey_copy("level_1", lang))}</strong><ul class="plain-list">{level1_html}</ul></div>
        <div><strong>{escape(_journey_copy("level_2", lang))}</strong><ul class="plain-list">{level2_html}</ul></div>
        <div><strong>{escape(_journey_copy("level_3", lang))}</strong><ul class="plain-list">{_localized_list_items(level_3[:3], lang)}</ul></div>
        <div><strong>{escape(_journey_copy("level_4", lang))}</strong><p>{escape(str(level_4.get("count_on_home") or 0))} / 3 · <a href="{escape(str(level_4.get("full_pool_link") or "/candidates"))}">{escape(_home_label("view_full_candidate_pool", lang))}</a></p></div>
      </div>
    </details>
    """


def _research_priority_cards(items: Any, lang: str) -> str:
    priorities = [item for item in (items if isinstance(items, list) else []) if isinstance(item, Mapping)][:3]
    if not priorities:
        return f'<div class="empty-state">{escape(_home_label("no_candidates", lang))}</div>'
    rows = []
    for index, item in enumerate(priorities, start=1):
        rows.append(
            f"""
            <article class="research-priority-card" data-research-priority="{index}">
              <span class="priority-index">{index}</span>
              <div>
                <h3>{escape(str(item.get("asset") or ""))}</h3>
                <p class="home-safety-note">{escape(str(item.get("theme") or ""))}</p>
              </div>
              <dl class="decision-dl">
                <dt>{escape(_journey_copy("why_now", lang))}</dt><dd>{escape(_localized(item.get("why_now"), lang))}</dd>
                <dt>{escape(_journey_copy("evidence_change", lang))}</dt><dd>{escape(_localized(item.get("evidence_change"), lang))}</dd>
                <dt>{escape(_journey_copy("relationship", lang))}</dt><dd>{escape(_relationship_phrase(str(item.get("portfolio_relationship") or ""), lang))}</dd>
                <dt>{escape(_journey_copy("truth_label", lang))}</dt><dd>{escape(_truth_label(str(item.get("truth_label") or ""), lang))}</dd>
              </dl>
            </article>
            """
        )
    return "".join(rows)


def _relationship_phrase(value: str, lang: str) -> str:
    if lang == "zh":
        mapping = {
            "Direct current portfolio exposure": "当前组合直接暴露",
            "Direct": "直接相关",
            "None": "无直接暴露",
        }
        return mapping.get(value, value)
    return value


def _truth_label(value: str, lang: str) -> str:
    if lang == "zh":
        mapping = {
            "Portfolio-Relevant": "组合相关",
            "Portfolio-Relevant / Not in Static Research Pool": "组合相关 / 不在静态候选池",
            "Static Research Pool": "静态研究池",
        }
        return mapping.get(value, value)
    return value


def _candidate_truth_text(research: Mapping[str, Any], lang: str) -> str:
    truth = research.get("candidate_priority_truth") if isinstance(research.get("candidate_priority_truth"), Mapping) else {}
    if lang == "zh":
        return "来源是真实仓库候选池 + 当前组合相关性展示排序；不是交易建议，也不伪装成动态运行态排名。"
    return "Source truth: static repository pool plus presentation-only current portfolio relevance; not a trading recommendation or dynamic runtime ranking."


def _forecast_compact_strip(forecast: Mapping[str, Any], lang: str) -> str:
    counts = forecast.get("counts") if isinstance(forecast.get("counts"), Mapping) else {}
    keys = ("current_open", "legacy_open", "matured", "verified", "invalidated", "inconclusive")
    strip = '<div class="forecast-compact-strip">' + "".join(
        f'<span><strong>{escape(str(counts.get(key, 0)))}</strong>{escape(_journey_copy(key, lang))}</span>'
        for key in keys
    ) + "</div>"
    return strip + f'<p class="home-safety-note">{escape(_localized(forecast.get("legacy_policy"), lang))}</p>'


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _home_outlook_title(outlook: Mapping[str, Any], lang: str) -> str:
    base_state = str(outlook.get("base_state") or "").replace("_", " ").strip()
    if not base_state or base_state.lower() == "unknown":
        return _home_label("insufficient_outlook", lang)
    if lang == "zh":
        mapping = {
            "RISK OFF": "基准：风险防御仍需观察",
            "NORMAL": "基准：中性状态延续",
            "ATTENTION EXPANSION": "基准：注意力扩张待确认",
            "BREAKOUT": "基准：突破信号待验证",
        }
        return mapping.get(base_state.upper(), f"基准：{base_state}")
    return f"Base case: {base_state.title()}"


def _driver_chips(packet: Mapping[str, Any], state: Mapping[str, Any], lang: str) -> str:
    drivers = [
        (t("state.attention", lang), packet.get("attention_state") or state.get("attention")),
        (t("state.liquidity", lang), packet.get("liquidity_state") or state.get("liquidity")),
        (t("state.volatility", lang), state.get("volatility")),
        (t("state.trust_score", lang), state.get("trust_index")),
    ]
    return "".join(
        f'<span class="tag">{escape(str(label))}: {escape(_compact(value, t("empty.signal", lang)))}</span>'
        for label, value in drivers
    )


def _scenario_map(outlook: Mapping[str, Any], lang: str) -> str:
    scenarios = [
        ("base", _home_label("base_case", lang), outlook.get("base_case")),
        ("upside", _home_label("upside_scenario", lang), outlook.get("upside_scenario")),
        ("downside", _home_label("downside_scenario", lang), outlook.get("downside_scenario")),
    ]
    cards = "".join(
        f"""
        <article class="scenario-card scenario-{escape(kind)}">
          <strong>{escape(label)}</strong>
          <p>{escape(_localized_outlook_text(text, lang) or _home_label("insufficient_evidence", lang))}</p>
        </article>
        """
        for kind, label, text in scenarios
    )
    return f"""
    <div class="home-scenario-grid">{cards}</div>
    <p class="home-safety-note">{escape(_home_label("forecast_vs_outlook", lang))}</p>
    """


def _localized_outlook_text(value: Any, lang: str) -> str:
    text = str(value or "").strip()
    if not text or lang != "zh":
        return text
    mapping = {
        "Non-binding structural runtime forecast: current causal structure remains coherent until contradicted by later observed state.": "非约束性结构预测：当前因果结构仍保持一致，除非后续观测状态与之冲突。",
        "Liquidity improves while market breadth and data freshness recover.": "流动性改善，同时市场广度与数据新鲜度修复。",
        "Liquidity and credit-sensitive signals deteriorate together.": "流动性与信用敏感信号同步恶化。",
        "Evidence quality improves and the current state stabilizes.": "证据质量改善，当前状态趋于稳定。",
        "Trust, data freshness, or portfolio-sensitive channels weaken.": "信任、数据新鲜度或组合敏感通道转弱。",
        "Attention converts into broader market participation and confirmed liquidity.": "注意力转化为更广泛的市场参与，并得到流动性确认。",
        "Attention remains elevated but liquidity confirmation fails.": "注意力仍然偏高，但流动性确认失败。",
    }
    return mapping.get(text, text)


def _localized_invalidations(items: Any, lang: str) -> list[str]:
    raw = items if isinstance(items, list) else []
    if not raw:
        return [_home_label("insufficient_evidence", lang)]
    if lang != "zh":
        return [str(item).replace("_", " ") for item in raw[:5]]
    mapping = {
        "live_market_channel_interrupts_or_delays": "实时市场通道中断或延迟",
        "market_data_remains_unavailable": "市场数据持续不可用",
        "trust_score_deteriorates": "信任分数继续下降",
        "portfolio_exposure_changes_materially": "组合暴露发生明显变化",
        "later_runtime_state_conflicts_with_expected_structure": "后续运行状态与当前结构判断冲突",
        "forecast_outcome_marked_invalidated_through_supported_lifecycle": "预测在支持的生命周期中被标记为失效",
    }
    return [mapping.get(str(item), str(item).replace("_", " ")) for item in raw[:5]]


def _portfolio_impact_summary(portfolio: Mapping[str, Any], market: Mapping[str, Any], lang: str) -> str:
    exposure = portfolio.get("exposure_map") if isinstance(portfolio.get("exposure_map"), Mapping) else {}
    holdings = exposure.get("asset_concentration") if isinstance(exposure.get("asset_concentration"), list) else []
    clusters = exposure.get("correlated_risk_clusters") if isinstance(exposure.get("correlated_risk_clusters"), list) else []
    top_holdings = "".join(
        f'<li><strong>{escape(str(item.get("asset") or "Asset"))}</strong> · {escape(_pct_text(item.get("exposure_pct")))}</li>'
        for item in holdings[:3]
        if isinstance(item, Mapping)
    )
    cluster_rows = "".join(
        f'<li>{escape(str(item.get("cluster") or "Cluster"))}: {escape(_pct_text(item.get("exposure_pct")))} · {escape(str(item.get("risk") or ""))}</li>'
        for item in clusters[:3]
        if isinstance(item, Mapping)
    )
    buffer_label = "未分配缓冲" if lang == "zh" else "Unallocated buffer"
    market_label = "当前市场影响" if lang == "zh" else "Current market impact"
    return f"""
    <div class="home-impact-stack">
      <div><strong>{escape(_home_label("portfolio_related", lang))}</strong><ul class="plain-list">{top_holdings or f'<li>{escape(t("portfolio.no_percentages", lang))}</li>'}</ul></div>
      <div><strong>{escape("集中风险" if lang == "zh" else "Concentration risk")}</strong><ul class="plain-list">{cluster_rows or f'<li>{escape(t("empty.context", lang))}</li>'}</ul></div>
      <div class="pill-row">
        <span class="tag">{escape(buffer_label)}: {escape(_pct_text(portfolio.get("cash_or_unassigned_pct")))}</span>
        <span class="tag">{escape(market_label)}: {escape(_clean(market.get("status"), t("empty.signal", lang)))}</span>
      </div>
    </div>
    """


def _candidate_title(candidates: Mapping[str, Any], lang: str) -> str:
    count = len(candidates.get("items") if isinstance(candidates.get("items"), list) else [])
    if count:
        return f"{count} {_home_label('research_candidates', lang)}"
    return _home_label("no_candidates", lang)


def _candidate_filters(candidates: Mapping[str, Any], lang: str) -> str:
    filters = candidates.get("filters") if isinstance(candidates.get("filters"), Mapping) else {}
    entries = [
        ("all", _home_label("all", lang)),
        ("portfolio", _home_label("portfolio_related", lang)),
        ("high", _home_label("high_priority", lang)),
        ("new", _home_label("new", lang)),
        ("changed", _home_label("changed_recently", lang)),
    ]
    counts = {
        "all": filters.get("all", 0),
        "portfolio": filters.get("portfolio_related", 0),
        "high": filters.get("high_priority", 0),
        "new": filters.get("new", 0),
        "changed": filters.get("changed_recently", 0),
    }
    buttons = "".join(
        f'<button class="secondary-button candidate-filter{" active" if key == "all" else ""}" type="button" data-candidate-filter="{escape(key)}">{escape(label)} <span>{escape(str(counts.get(key, 0)))}</span></button>'
        for key, label in entries
    )
    return f'<div class="candidate-filter-row">{buttons}</div>'


def _candidate_table(items: Any, lang: str, *, limit: int | None = None) -> str:
    candidates = [item for item in (items if isinstance(items, list) else []) if isinstance(item, Mapping)]
    if limit:
        candidates = candidates[:limit]
    if not candidates:
        return f'<div class="empty-state">{escape(_home_label("no_candidates", lang))}</div>'
    rows = []
    for index, item in enumerate(candidates):
        priority = str(item.get("current_priority") or "")
        relationship = str(item.get("portfolio_relationship") or "None")
        status = _candidate_status_label(str(item.get("status") or "Watch"), lang)
        filters = ["all"]
        if relationship != "None":
            filters.append("portfolio")
        if priority in {"S", "A"}:
            filters.append("high")
        if index < 2:
            filters.append("changed")
        rows.append(
            f"""
            <article class="candidate-row" data-candidate-row data-candidate-filters="{escape(' '.join(filters))}">
              <div>
                <strong>{escape(str(item.get("asset") or ""))}</strong>
                <span>{escape(str(item.get("theme") or ""))}</span>
              </div>
              <span>{escape(priority)}</span>
              <span>{escape(_relationship_label(relationship, lang))}</span>
              <span>{escape(str(item.get("evidence_strength") or _home_label("insufficient_evidence", lang)))}</span>
              <span>{escape(status)}</span>
              <details class="candidate-detail">
                <summary>{escape(_home_label("details", lang))}</summary>
                <p><strong>{escape(_home_label("thesis_direction", lang))}:</strong> {escape(str(item.get("thesis_direction") or ""))}</p>
                <p><strong>{escape(t("home.top_risks", lang))}:</strong> {escape(str(item.get("key_risk") or ""))}</p>
                <p><strong>{escape("Next trigger" if lang == "en" else "下一触发")}:</strong> {escape(str(item.get("next_trigger") or ""))}</p>
                <p><strong>{escape(_home_label("source", lang))}:</strong> {escape(str(item.get("source_category") or ""))} · {escape(str(item.get("source") or ""))}</p>
              </details>
            </article>
            """
        )
    return f"""
    <div class="candidate-table" role="table" aria-label="{escape(_home_label("research_candidates", lang))}">
      <div class="candidate-header" role="row">
        <span>{escape(_home_label("asset_theme", lang))}</span>
        <span>{escape(_home_label("priority", lang))}</span>
        <span>{escape(_home_label("relevance", lang))}</span>
        <span>{escape(_home_label("evidence_strength", lang))}</span>
        <span>{escape(_home_label("status", lang))}</span>
        <span>{escape(_home_label("details", lang))}</span>
      </div>
      {''.join(rows)}
    </div>
    """


def _candidate_status_label(status: str, lang: str) -> str:
    key = status.strip().lower().replace(" ", "_")
    return {
        "research": _home_label("research_only", lang),
        "watch": _home_label("watch", lang),
        "elevated": _home_label("elevated", lang),
        "deprioritized": _home_label("deprioritized", lang),
        "observe": _home_label("observe", lang),
    }.get(key, status)


def _relationship_label(value: str, lang: str) -> str:
    if lang == "zh":
        return {"Direct": "直接相关", "Indirect": "间接相关", "None": "无直接暴露", "Unknown": "未知"}.get(value, value)
    return value


def _candidate_changes(changes: Any, lang: str) -> str:
    data = [item for item in (changes if isinstance(changes, list) else []) if isinstance(item, Mapping)]
    if not data:
        return f'<section class="candidate-changes"><h3>{escape(_home_label("candidate_changes", lang))}</h3><p>{escape(_home_label("no_candidate_changes", lang))}</p></section>'
    labels = {
        "entered_candidate_pool": "新进入候选池" if lang == "zh" else "Entered candidate pool",
        "priority_raised": "研究优先级上调" if lang == "zh" else "Priority raised",
        "priority_lowered": "研究优先级下调" if lang == "zh" else "Priority lowered",
        "thesis_strengthened": "论点增强" if lang == "zh" else "Thesis strengthened",
        "thesis_weakened": "论点减弱" if lang == "zh" else "Thesis weakened",
    }
    rows = "".join(
        f'<li><strong>{escape(str(item.get("asset") or ""))}</strong> · {escape(labels.get(str(item.get("change_type")), str(item.get("change_type"))))}<br>{escape(str(item.get("why") or ""))}</li>'
        for item in data[:4]
    )
    return f'<section class="candidate-changes"><h3>{escape(_home_label("candidate_changes", lang))}</h3><ul class="plain-list">{rows}</ul></section>'


def _forecast_status_strip(forecast: Mapping[str, Any], lang: str) -> str:
    counts = forecast.get("counts") if isinstance(forecast.get("counts"), Mapping) else {}
    labels = [
        ("open", "进行中" if lang == "zh" else "OPEN"),
        ("matured", "已到期" if lang == "zh" else "MATURED"),
        ("verified", "已验证" if lang == "zh" else "VERIFIED"),
        ("invalidated", "已失效" if lang == "zh" else "INVALIDATED"),
        ("inconclusive", "无法判断" if lang == "zh" else "INCONCLUSIVE"),
    ]
    return '<div class="forecast-status-strip">' + "".join(
        f'<span><strong>{escape(str(counts.get(key, 0)))}</strong>{escape(label)}</span>'
        for key, label in labels
    ) + "</div>"


def _forecast_accountability_copy(forecast: Mapping[str, Any], lang: str) -> str:
    latest = forecast.get("latest") if isinstance(forecast.get("latest"), list) else []
    recent = latest[0] if latest and isinstance(latest[0], Mapping) else {}
    if not recent:
        return f'<p>{escape(_home_label("no_forecasts", lang))}</p>'
    sample = str(forecast.get("sample_warning") or _home_label("low_sample", lang))
    return f"""
    <p>{escape(sample)}</p>
    <dl class="expert-dl">
      <dt>{escape(_home_label("latest_open", lang))}</dt><dd>{escape(str(recent.get("forecast_statement") or recent.get("expected_direction_state") or ""))}</dd>
      <dt>{escape(_home_label("horizon", lang))}</dt><dd>{escape(str(recent.get("horizon") or ""))}</dd>
      <dt>{escape(t("state.confidence", lang))}</dt><dd>{escape(_pct_text(float(recent.get("confidence") or 0) * 100))}</dd>
    </dl>
    """


def _expert_analysis_panel(expert: Mapping[str, Any], lang: str) -> str:
    return f"""
    <details class="expert-details home-expert-panel" id="expert-analysis-panel">
      <summary><span>{escape(_home_label("expert_analysis", lang))}</span><strong>{escape(str(expert.get("section_count") or 0))}</strong></summary>
      <div class="expert-grid">
        {_expert_section("A", _home_label("causal_chain", lang), _expert_causal_chain(expert, lang))}
        {_expert_section("B", _home_label("hypothesis_state", lang), _expert_hypothesis(expert, lang))}
        {_expert_section("C", _home_label("regime_state", lang), _expert_regime(expert, lang))}
        {_expert_section("D", _home_label("confidence_composition", lang), _expert_confidence(expert, lang))}
        {_expert_section("E", _home_label("data_quality", lang), _expert_data_quality(expert, lang))}
        {_expert_section("F", _home_label("portfolio_sensitivity", lang), _expert_portfolio(expert, lang))}
        {_expert_section("G", _home_label("forecast_evidence", lang), _expert_forecast(expert, lang))}
        {_expert_section("H", _home_label("invalidation_conditions", lang), '<ul class="plain-list">' + _list_items(_localized_invalidations(expert.get("invalidation_conditions"), lang)) + '</ul>')}
        {_expert_section("I", _home_label("raw_evidence", lang), _expert_raw(expert, lang))}
      </div>
    </details>
    """


def _expert_section(letter: str, title: str, body: str) -> str:
    return f'<article class="expert-section"><span>{escape(letter)}</span><h3>{escape(title)}</h3>{body}</article>'


def _expert_causal_chain(expert: Mapping[str, Any], lang: str) -> str:
    chain = expert.get("causal_chain") if isinstance(expert.get("causal_chain"), list) else []
    edges = expert.get("causal_edges") if isinstance(expert.get("causal_edges"), list) else []
    chain_html = '<div class="causal-chain">' + "".join(f'<span>{escape(str(item))}</span>' for item in chain[:5]) + "</div>"
    edge_html = "".join(
        f'<li>{escape(str(edge.get("from")))} → {escape(str(edge.get("to")))} · Δ {escape(str(edge.get("weight_delta")))}</li>'
        for edge in edges[:4]
        if isinstance(edge, Mapping)
    )
    empty_row = f"<li>{escape(t('empty.context', lang))}</li>"
    return chain_html + f'<p class="home-safety-note">{escape(_home_label("dominant_edges", lang))}</p><ul class="plain-list">{edge_html or empty_row}</ul>'


def _expert_hypothesis(expert: Mapping[str, Any], lang: str) -> str:
    hypo = expert.get("hypothesis_state") if isinstance(expert.get("hypothesis_state"), Mapping) else {}
    competitors = hypo.get("competing") if isinstance(hypo.get("competing"), list) else []
    return f"""
    <dl class="expert-dl">
      <dt>{escape(_home_label("active_hypothesis", lang))}</dt><dd>{escape(str(hypo.get("active") or t("empty.context", lang)))}</dd>
      <dt>{escape(t("state.confidence", lang))}</dt><dd>{escape(_pct_text(float(hypo.get("confidence") or 0) * 100))}</dd>
      <dt>{escape(_home_label("recent_change", lang))}</dt><dd>{escape(str(hypo.get("recent_change") or ""))}</dd>
    </dl>
    <p><strong>{escape(_home_label("competing_hypotheses", lang))}</strong></p>
    <ul class="plain-list">{_list_items(competitors[:3])}</ul>
    """


def _expert_regime(expert: Mapping[str, Any], lang: str) -> str:
    regime = expert.get("regime_state") if isinstance(expert.get("regime_state"), Mapping) else {}
    return f"""
    <dl class="expert-dl">
      <dt>{escape(t("state.current_regime", lang))}</dt><dd>{escape(str(regime.get("current") or t("empty.signal", lang)))}</dd>
      <dt>{escape("Proposed" if lang == "en" else "建议状态")}</dt><dd>{escape(str(regime.get("proposed") or t("empty.signal", lang)))}</dd>
      <dt>{escape(t("state.volatility", lang))}</dt><dd>{escape(str(regime.get("volatility") or t("empty.signal", lang)))}</dd>
    </dl>
    """


def _expert_confidence(expert: Mapping[str, Any], lang: str) -> str:
    rows = []
    components = expert.get("confidence_composition") if isinstance(expert.get("confidence_composition"), list) else []
    name_map = {
        "evidence_quality": "证据质量",
        "market_data_completeness": "市场数据完整度",
        "hypothesis_stability": "假设稳定性",
        "portfolio_relevance": "组合相关性",
        "forecast_history": "预测历史",
    }
    source_map = {
        "market channel status": "市场通道状态",
        "market_intelligence.channels": "市场情报通道",
        "system_trust_state": "系统信任状态",
        "portfolio_context": "组合上下文",
        "forecast_ledger": "预测账本",
    }
    for item in components:
        if not isinstance(item, Mapping):
            continue
        pct = max(0, min(100, float(item.get("value") or 0) * 100))
        raw_name = str(item.get("name") or "")
        raw_source = str(item.get("source") or "")
        name = name_map.get(raw_name, raw_name.replace("_", " ")) if lang == "zh" else raw_name.replace("_", " ")
        source = source_map.get(raw_source, raw_source) if lang == "zh" else raw_source
        rows.append(
            f'<div class="confidence-row"><span>{escape(name)}</span><strong>{pct:.0f}%</strong><i style="width:{pct:.0f}%"></i><small>{escape(source)}</small></div>'
        )
    return "".join(rows) or f'<p>{escape(t("empty.context", lang))}</p>'


def _expert_data_quality(expert: Mapping[str, Any], lang: str) -> str:
    data = expert.get("data_quality") if isinstance(expert.get("data_quality"), Mapping) else {}
    return f"""
    <div class="forecast-status-strip expert-data-strip">
      <span><strong>{escape(str(data.get("live_channels", 0)))}</strong>{escape(_home_label("live_channels", lang))}</span>
      <span><strong>{escape(str(data.get("simulated_channels", 0)))}</strong>{escape(_home_label("simulated_channels", lang))}</span>
      <span><strong>{escape(str(data.get("missing_channels", 0)))}</strong>{escape(_home_label("missing_channels", lang))}</span>
      <span><strong>{escape(str(data.get("stale_channels", 0)))}</strong>{escape(_home_label("stale_channels", lang))}</span>
    </div>
    <p>{escape(_localized_data_quality_limitation(data.get("limitation"), lang))}</p>
    """


def _localized_data_quality_limitation(value: Any, lang: str) -> str:
    text = str(value or "").strip()
    if not text or lang != "zh":
        return text
    mapping = {
        "Confidence is limited by missing, stale, or unconfigured market channels.": "置信度受到缺失、过期或未配置市场通道的限制。",
        "Confidence is limited because some channels are simulated.": "部分通道仍为模拟数据，因此置信度受限。",
        "Live channels are available, but forecast outcomes still need accumulation.": "已有实时通道，但预测结果样本仍需继续积累。",
        "Confidence is limited because no market channels are currently available.": "当前没有可用市场通道，因此置信度受限。",
    }
    return mapping.get(text, text)


def _expert_portfolio(expert: Mapping[str, Any], lang: str) -> str:
    portfolio = expert.get("portfolio_sensitivity") if isinstance(expert.get("portfolio_sensitivity"), Mapping) else {}
    holdings = portfolio.get("largest_positions") if isinstance(portfolio.get("largest_positions"), list) else []
    rows = "".join(
        f'<li>{escape(str(item.get("asset") or ""))} · {escape(_pct_text(item.get("exposure_pct")))}</li>'
        for item in holdings
        if isinstance(item, Mapping)
    )
    return f"""
    <ul class="plain-list">{rows or f'<li>{escape(t("portfolio.no_percentages", lang))}</li>'}</ul>
    <p>{escape("Privacy: percentage-only; no account value is exposed." if lang == "en" else "隐私：仅展示百分比，不展示账户金额。")}</p>
    """


def _expert_forecast(expert: Mapping[str, Any], lang: str) -> str:
    forecast = expert.get("forecast_evidence") if isinstance(expert.get("forecast_evidence"), Mapping) else {}
    drivers = forecast.get("drivers") if isinstance(forecast.get("drivers"), list) else []
    return f"""
    <dl class="expert-dl">
      <dt>ID</dt><dd>{escape(str(forecast.get("latest_forecast_id") or t("empty.context", lang)))}</dd>
      <dt>{escape(_home_label("status", lang))}</dt><dd>{escape(str(forecast.get("status") or t("empty.context", lang)))}</dd>
      <dt>{escape(_home_label("horizon", lang))}</dt><dd>{escape(str(forecast.get("horizon") or t("empty.context", lang)))}</dd>
    </dl>
    <p>{escape(_localized_outlook_text(forecast.get("statement"), lang) or t("empty.context", lang))}</p>
    <ul class="plain-list">{_list_items(drivers[:3])}</ul>
    """


def _expert_raw(expert: Mapping[str, Any], lang: str) -> str:
    raw = expert.get("raw_evidence") if isinstance(expert.get("raw_evidence"), Mapping) else {}
    return f"""
    <details class="raw-evidence-details">
      <summary>{escape(_home_label("raw_evidence", lang))}</summary>
      <pre>{escape(json.dumps(raw, ensure_ascii=False, indent=2))}</pre>
    </details>
    """


def _home_intelligence_style() -> str:
    return """
    <style>
    .atlas-shell[data-active-page="home"] .workspace.no-inspector { padding:22px clamp(18px, 3vw, 44px) 0; }
    .atlas-shell[data-active-page="home"] .workspace.no-inspector > .page-content { width:100%; }
    .decision-home-shell { display:grid; gap:18px; }
    .investor-home { gap:24px; }
    .portfolio-first-viewport { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; align-items:start; }
    .portfolio-command-card { grid-column:span 8; grid-row:1; min-height:100%; background:radial-gradient(circle at 12% 8%,rgba(158,230,184,.1),transparent 34%),linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.028)); }
    .holdings-primary-card { grid-column:span 8; grid-row:2; min-height:100%; }
    .portfolio-first-viewport .action-today-card { grid-area:auto; grid-column:span 4; grid-row:1; min-height:100%; grid-template-columns:1fr; grid-template-areas:"step" "kicker" "answer" "posture" "reason" "helper"; align-content:start; }
    .portfolio-first-viewport .core-judgment-card { grid-area:auto; grid-column:span 4; grid-row:2; min-height:100%; }
    .portfolio-command-card h1 { margin:8px 0 0; font-size:2rem; line-height:1.05; }
    .portfolio-header-status { display:grid; justify-items:end; gap:5px; text-align:right; }
    .portfolio-header-status small { color:var(--muted); font-size:.72rem; }
    .portfolio-header-status strong { max-width:12ch; font-size:.92rem; line-height:1.25; }
    .portfolio-command-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:18px 0 14px; }
    .portfolio-command-metrics > div { min-height:84px; display:grid; align-content:center; gap:6px; padding:12px; border-top:1px solid rgba(219,234,254,.14); border-bottom:1px solid rgba(219,234,254,.08); }
    .portfolio-command-metrics span,.portfolio-command-analysis span,.portfolio-risk-callout span { color:var(--muted); font-size:.78rem; }
    .portfolio-command-metrics strong { font-size:1.34rem; }
    .portfolio-command-analysis { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
    .portfolio-command-analysis > div,.portfolio-command-analysis ul { min-height:74px; margin:0; padding:11px 12px; background:rgba(0,0,0,.11); border-radius:12px; }
    .portfolio-command-analysis > div { display:grid; gap:6px; align-content:center; }
    .portfolio-command-analysis ul { list-style:none; display:grid; gap:4px; }
    .portfolio-command-analysis li { display:flex; justify-content:space-between; gap:10px; color:var(--subtle); font-size:.78rem; }
    .portfolio-risk-callout { margin-top:12px; padding:13px 14px; border-left:3px solid rgba(244,165,179,.72); background:rgba(244,165,179,.045); }
    .portfolio-risk-callout p { margin:6px 0 0; color:var(--text); }
    .investor-evidence-grid { display:grid; grid-template-columns:minmax(0,1.08fr) minmax(380px,.92fr); gap:16px; align-items:start; }
    .material-evidence-list { display:grid; gap:0; margin-top:12px; }
    .material-evidence-item { padding:15px 2px; border-top:1px solid rgba(219,234,254,.1); }
    .material-evidence-item:first-child { border-top:0; }
    .material-evidence-item h3 { margin:8px 0 10px; font-size:1rem; line-height:1.4; }
    .material-evidence-item dl { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px 14px; margin:0; }
    .material-evidence-item dl div { min-width:0; }
    .material-evidence-item dt { color:var(--muted); font-size:.74rem; }
    .material-evidence-item dd { margin:3px 0 0; color:var(--subtle); overflow-wrap:anywhere; }
    .material-evidence-item a { color:var(--accent); }
    .evidence-truth-row { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .evidence-truth-row span { color:var(--accent); font-size:.72rem; font-weight:780; }
    .evidence-truth-row em { color:var(--muted); font-size:.72rem; font-style:normal; }
    .investor-reasoning-chain { list-style:none; display:grid; gap:0; margin:14px 0 0; padding:0; }
    .investor-reasoning-chain li { display:grid; grid-template-columns:34px minmax(0,1fr); gap:11px; position:relative; padding:0 0 14px; }
    .investor-reasoning-chain li:not(:last-child)::after { content:""; position:absolute; left:16px; top:31px; bottom:2px; width:1px; background:rgba(219,234,254,.16); }
    .investor-reasoning-chain li > span { width:32px; height:32px; display:grid; place-items:center; border-radius:50%; background:rgba(219,234,254,.11); color:var(--accent); font-size:.7rem; }
    .investor-reasoning-chain small { color:var(--muted); }
    .investor-reasoning-chain p { margin:4px 0 0; color:var(--text); line-height:1.42; }
    .scenario-section { display:grid; gap:16px; }
    .scenario-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); margin-top:14px; border-top:1px solid rgba(219,234,254,.12); border-bottom:1px solid rgba(219,234,254,.12); }
    .scenario-card { min-width:0; padding:16px; border-left:1px solid rgba(219,234,254,.1); }
    .scenario-card:first-child { border-left:0; }
    .scenario-card > span { color:var(--accent); font-size:.75rem; font-weight:780; }
    .scenario-card h3 { margin:9px 0 14px; font-size:1rem; line-height:1.4; }
    .scenario-card small { color:var(--muted); }
    .scenario-card ul { margin:7px 0 13px; padding-left:17px; color:var(--subtle); font-size:.85rem; }
    .scenario-card dl { display:grid; grid-template-columns:auto 1fr; gap:5px 8px; margin:0; font-size:.78rem; }
    .scenario-card dt { color:var(--muted); }
    .scenario-card dd { margin:0; }
    .playbook-warning { margin:12px 0; padding:11px 13px; background:rgba(246,215,122,.06); border-left:3px solid rgba(246,215,122,.68); color:var(--subtle); }
    .table-scroll { width:100%; max-width:100%; min-width:0; overflow-x:auto; }
    .action-playbook-table { min-width:980px; }
    .candidate-score-table { min-width:1000px; }
    .candidate-score-table td:first-child { min-width:180px; }
    .candidate-score-table td small { display:block; margin-top:5px; color:var(--muted); max-width:38ch; }
    .score-dimensions { color:var(--muted); font-size:.78rem; line-height:1.6; }
    .candidate-coverage-note { margin:12px 0; color:var(--subtle); line-height:1.5; }
    .pending-candidates,.score-methodology { margin-top:12px; padding-top:10px; border-top:1px solid rgba(219,234,254,.1); }
    .pending-candidates summary,.score-methodology summary { cursor:pointer; color:var(--subtle); font-weight:720; }
    .pending-candidates ul { list-style:none; display:grid; gap:8px; margin:10px 0 0; padding:0; }
    .pending-candidates li { display:flex; justify-content:space-between; gap:14px; padding:9px 0; border-bottom:1px solid rgba(219,234,254,.07); }
    .pending-candidates li span,.score-methodology p { color:var(--muted); font-size:.82rem; }
    .supporting-context { border-top:1px solid rgba(219,234,254,.12); padding-top:10px; }
    .supporting-context > summary { cursor:pointer; color:var(--subtle); padding:12px 2px; font-weight:740; }
    .supporting-context-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; margin-top:8px; }
    .decision-first-viewport { display:grid; grid-template-columns:minmax(0,1.18fr) minmax(0,.92fr); gap:14px; align-items:stretch; }
    .practical-brief-shell { min-width:0; gap:24px; width:100%; max-width:1440px; margin:0 auto; }
    .practical-brief-shell > section,
    .practical-brief-shell > details,
    .portfolio-first-viewport > *,
    .investor-evidence-grid > *,
    .scenario-section > *,
    .candidate-score-section > *,
    .supporting-context-grid > * { min-width:0; max-width:100%; }
    .practical-first-viewport { display:grid; grid-template-columns:minmax(0,.94fr) minmax(0,1.06fr); grid-template-areas:"action action" "core predictions"; gap:16px; align-items:stretch; }
    .action-today-card { container-type:inline-size; grid-area:action; min-height:230px; display:grid; grid-template-columns:minmax(420px,.52fr) minmax(0,1fr); grid-template-areas:"step reason" "kicker reason" "answer reason" "posture helper"; column-gap:28px; row-gap:8px; align-items:center; overflow:hidden; }
    .action-today-card .journey-step { grid-area:step; align-self:start; }
    .action-today-card .kicker { grid-area:kicker; align-self:end; }
    .action-today-card .action-answer { grid-area:answer; }
    .action-today-card .posture-pill { grid-area:posture; justify-self:start; }
    .action-today-card .decision-change { grid-area:reason; align-self:end; max-width:62ch; }
    .action-today-card .home-safety-note { grid-area:helper; align-self:start; max-width:68ch; }
    .core-judgment-card { grid-area:core; }
    .predictions-card { grid-area:predictions; }
    .action-answer { margin:0; max-width:100%; font-size:clamp(2rem, 7cqw, 3.4rem) !important; line-height:1 !important; letter-spacing:0; white-space:normal; overflow-wrap:anywhere; }
    .practical-secondary-grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; align-items:start; }
    .practical-secondary-grid #home-ai-bottleneck-index { grid-column:span 8; }
    .practical-secondary-grid #home-capital-relay { grid-column:span 4; }
    .practical-secondary-grid #home-current-holdings { grid-column:1 / -1; }
    .practical-secondary-grid #home-capital-allocation { grid-column:1 / -1; }
    .practical-operational-grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; align-items:start; }
    .practical-operational-grid #home-waiting-triggers { grid-column:1 / -1; }
    .practical-operational-grid #home-research-tasks { grid-column:1 / -1; }
    .practical-operational-grid #home-intelligence-alerts { grid-column:1 / -1; }
    .practical-control-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; align-items:start; }
    .prediction-stack { display:grid; gap:10px; }
    .prediction-item, .holding-brief-card { padding:15px; border:1px solid rgba(219,234,254,.11); border-radius:18px; background:rgba(255,255,255,.035); }
    .prediction-topline { display:grid; grid-template-columns:auto minmax(0,1fr); gap:10px; align-items:start; }
    .prediction-topline h3 { margin:0 0 5px; font-size:1.02rem; line-height:1.25; }
    .compact-metrics { margin-top:10px; }
    .compact-metrics span { min-height:58px; }
    .practical-table { width:100%; border-collapse:separate; border-spacing:0 8px; margin-top:12px; table-layout:auto; }
    .practical-table th { color:var(--muted); font-size:.75rem; text-transform:uppercase; text-align:left; padding:0 9px 3px; }
    .practical-table td { padding:11px 10px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:rgba(255,255,255,.032); vertical-align:top; line-height:1.35; }
    .practical-table td:first-child { border-left:1px solid var(--line); border-radius:12px 0 0 12px; }
    .practical-table td:last-child { border-right:1px solid var(--line); border-radius:0 12px 12px 0; }
    .capital-relay-path { display:flex; align-items:stretch; gap:8px; overflow-x:auto; padding:10px 0 2px; }
    .relay-node { min-width:128px; flex:1 0 128px; display:grid; gap:5px; align-content:center; padding:12px; border:1px solid rgba(219,234,254,.11); border-radius:16px; background:rgba(255,255,255,.04); }
    .relay-node span { color:var(--accent); font-weight:760; }
    .relay-node small { color:var(--muted); }
    .relay-arrow { align-self:center; color:var(--muted); font-size:1.25rem; }
    .valuation-summary-strip { display:grid; grid-template-columns:150px 210px minmax(0,1fr); gap:12px; align-items:center; margin:8px 0 14px; padding:12px 14px; border:1px solid rgba(219,234,254,.1); border-radius:14px; background:rgba(0,0,0,.11); }
    .valuation-summary-strip span { display:grid; gap:3px; } .valuation-summary-strip small { color:var(--muted); } .valuation-summary-strip p { margin:0; color:var(--subtle); font-size:.82rem; }
    .holding-brief-grid { display:grid; grid-template-columns:1fr; gap:12px; }
    .holding-brief-card { display:grid; grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr); gap:20px; padding:16px; border-radius:16px; }
    .holding-title-row { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; } .holding-title-row h3 { margin:0 0 4px; font-size:1.1rem; }
    .allocation-badge { display:grid; justify-items:end; gap:3px; } .allocation-badge small { color:var(--muted); font-size:.72rem; } .allocation-badge strong { font-size:1.12rem; }
    .holding-decision-column { padding-left:18px; border-left:1px solid rgba(219,234,254,.1); }
    .valuation-visuals { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-top:14px; }
    .cost-price-chart,.pnl-chart,.valuation-empty { min-height:138px; padding:12px; border:1px solid rgba(219,234,254,.1); border-radius:13px; background:rgba(0,0,0,.12); }
    .valuation-empty { display:grid; place-items:center; color:var(--muted); text-align:center; font-size:.82rem; }
    .valuation-chart-head { display:flex; justify-content:space-between; gap:8px; color:var(--muted); font-size:.76rem; } .valuation-chart-head strong { color:var(--text); font-size:.92rem; }
    .cost-price-values { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; margin-top:11px; } .cost-price-values span { min-width:0; display:grid; gap:2px; } .cost-price-values small { color:var(--muted); font-size:.66rem; } .cost-price-values strong { font-size:.76rem; line-height:1.2; white-space:nowrap; }
    .cost-price-track { position:relative; height:18px; margin:22px 8px 0; border-top:2px solid rgba(219,234,254,.16); }
    .cost-price-track i { position:absolute; top:-7px; width:1px; height:17px; font-style:normal; } .cost-price-track i b { display:block; width:12px; height:12px; margin-left:-6px; border-radius:50%; background:var(--accent); }
    .cost-price-track .price-marker b { background:#9ee6b8; }
    .pnl-track { position:relative; height:10px; margin-top:22px; border-radius:999px; background:rgba(255,255,255,.07); overflow:hidden; } .pnl-track b { position:absolute; left:50%; top:0; width:1px; height:100%; background:rgba(255,255,255,.56); }
    .pnl-track i { position:absolute; top:0; height:100%; background:#9ee6b8; } .pnl-chart.loss .pnl-track i { background:#f4a5b3; }
    .pnl-axis { display:flex; justify-content:space-between; margin-top:7px; color:var(--muted); font-size:.66rem; }
    .valuation-amount-grid { grid-column:1/-1; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:6px; } .valuation-amount-grid span { min-width:0; display:grid; gap:4px; padding:9px 8px; border:1px solid rgba(219,234,254,.08); border-radius:9px; background:rgba(255,255,255,.025); } .valuation-amount-grid small { color:var(--muted); font-size:.66rem; } .valuation-amount-grid strong { font-size:clamp(.72rem,1vw,.88rem); white-space:nowrap; }
    .valuation-provenance { display:flex; flex-wrap:wrap; gap:8px 12px; align-items:center; margin-top:10px; color:var(--muted); font-size:.74rem; }
    .freshness-badge { display:inline-flex; min-height:24px; align-items:center; padding:3px 8px; border-radius:999px; background:rgba(246,215,122,.1); color:#ffe59a; font-weight:760; } .freshness-live { color:#9ee6b8; background:rgba(158,230,184,.1); } .freshness-failed,.freshness-not_configured { color:#f4a5b3; background:rgba(244,165,179,.1); }
    .valuation-limitations { display:flex; flex-wrap:wrap; gap:6px 12px; margin:10px 0 0; padding:0; list-style:none; color:var(--muted); font-size:.76rem; } .valuation-limitations li::before { content:"!"; display:inline-grid; place-items:center; width:16px; height:16px; margin-right:6px; border-radius:50%; background:rgba(246,215,122,.12); color:#ffe59a; font-size:.66rem; }
    .holding-brief-card .decision-dl { grid-template-columns:1fr; gap:3px; font-size:.82rem; }
    .holding-brief-card .decision-dl dt { margin-top:6px; }
    .waiting-trigger-table { display:block; max-width:100%; overflow-x:auto; }
    .allocation-dl .plain-list { margin:0; }
    .funding-flow { margin-top:14px; display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); gap:10px; align-items:center; padding:13px; border:1px solid rgba(219,234,254,.18); border-radius:16px; background:rgba(219,234,254,.055); }
    .funding-flow span { min-height:54px; display:grid; place-items:center; text-align:center; border-radius:12px; background:rgba(0,0,0,.12); padding:9px; }
    .funding-flow strong { color:var(--accent); font-size:1.4rem; }
    .funding-flow p { grid-column:1 / -1; margin:2px 0 0; }
    .trigger-progress { color:var(--accent) !important; font-weight:780; }
    .trigger-status { display:inline-flex; min-height:28px; align-items:center; padding:5px 9px; border-radius:999px; font-size:.78rem; font-weight:780; background:rgba(255,255,255,.07); }
    .status-met { color:#9ee6b8; }
    .status-partial { color:#ffe59a; }
    .status-not-met { color:#f4a5b3; }
    .status-unknown { color:var(--muted); }
    .intelligence-alert-list { list-style:none; display:grid; gap:9px; padding:0; margin:12px 0 0; }
    .intelligence-alert-list li { display:grid; grid-template-columns:minmax(150px,.24fr) minmax(0,1fr); gap:14px; padding:13px; border:1px solid rgba(219,234,254,.11); border-radius:15px; background:rgba(255,255,255,.035); }
    .intelligence-alert-list span { color:var(--subtle); }
    .practical-empty { min-height:120px; display:grid; place-items:center; text-align:center; }
    .decision-card, .decision-support-card, .forecast-compact-card, .home-expert-secondary { border:1px solid rgba(219,234,254,.105); border-radius:24px; background:linear-gradient(145deg, rgba(255,255,255,.066), rgba(255,255,255,.028)); box-shadow:0 18px 52px rgba(0,0,0,.18); backdrop-filter:blur(20px); padding:20px; }
    .action-today-card { background:radial-gradient(circle at 14% 44%, rgba(219,234,254,.18), transparent 38%), radial-gradient(circle at 88% 12%, rgba(158,230,184,.08), transparent 34%), linear-gradient(145deg, rgba(255,255,255,.088), rgba(255,255,255,.032)); }
    .decision-card-primary { grid-row:span 2; padding:22px; }
    .decision-card h1 { margin:12px 0 10px; font-size:clamp(2rem, 2.6vw, 3.15rem); line-height:1.02; letter-spacing:0; max-width:16ch; }
    .decision-card h2, .decision-support-card h2, .forecast-compact-card h2, .home-expert-secondary h2 { margin:8px 0 10px; font-size:1.24rem; line-height:1.18; letter-spacing:0; }
    .decision-card p, .decision-support-card p, .forecast-compact-card p { color:var(--subtle); line-height:1.52; }
    .decision-change { color:var(--text) !important; font-size:1.06rem; line-height:1.52 !important; }
    .journey-step { display:flex; align-items:center; gap:9px; color:var(--muted); font-size:.84rem; font-weight:760; }
    .journey-step span { width:30px; height:30px; display:grid; place-items:center; border-radius:999px; background:rgba(219,234,254,.13); color:var(--accent); font-size:.76rem; }
    .decision-meta-row, .forward-metrics { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
    .forward-metrics span { flex:1 1 120px; min-height:76px; display:grid; align-content:center; gap:5px; padding:11px; border:1px solid var(--line); border-radius:15px; background:rgba(255,255,255,.035); }
    .forward-metrics small { color:var(--muted); }
    .forward-metrics strong { font-size:1rem; }
    .falsification { border-left:3px solid rgba(244,165,179,.75); padding-left:10px; }
    .posture-pill { display:inline-flex; align-items:center; justify-content:center; min-height:44px; padding:9px 18px; border-radius:999px; background:var(--accent); color:var(--bg); font-size:1.08rem; font-weight:820; margin:8px 0 8px; }
    .focus-list { display:grid; gap:8px; margin:12px 0 0; padding-left:20px; }
    .focus-list li { color:var(--text); line-height:1.42; }
    .decision-dl { display:grid; grid-template-columns:minmax(100px,.42fr) minmax(0,1fr); gap:9px; margin:14px 0 0; }
    .decision-dl dt { color:var(--muted); }
    .decision-dl dd { margin:0; color:var(--text); overflow-wrap:anywhere; }
    .conviction-hierarchy { margin-top:14px; border:1px solid var(--line); border-radius:16px; background:rgba(0,0,0,.12); }
    .conviction-hierarchy summary { cursor:pointer; padding:12px 14px; color:var(--accent); font-weight:780; }
    .conviction-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; padding:0 14px 14px; }
    .conviction-grid > div { padding:11px; border:1px solid var(--line); border-radius:13px; background:rgba(255,255,255,.035); }
    .conviction-grid small { display:block; color:var(--muted); margin-top:4px; }
    .decision-support-grid { display:grid; grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr); gap:14px; }
    .trigger-columns { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
    .trigger-columns h3 { margin:8px 0; font-size:1rem; }
    .positive-confirmation li::marker { color:#9ee6b8; }
    .negative-confirmation li::marker { color:#f4a5b3; }
    .research-priority-list { display:grid; grid-template-columns:1fr; gap:12px; margin-top:14px; }
    .research-priority-card { display:grid; grid-template-columns:1fr; gap:13px; align-items:start; padding:16px; border:1px solid rgba(219,234,254,.11); border-radius:18px; background:rgba(255,255,255,.035); }
    .research-item-main { display:grid; grid-template-columns:auto minmax(0,1fr); gap:12px; align-items:start; }
    .research-item-main h3 { margin:0 0 8px; font-size:1.1rem; line-height:1.28; max-width:none; overflow-wrap:break-word; word-break:normal; }
    .research-item-detail { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:0; }
    .research-item-detail > div { min-height:100px; display:grid; align-content:start; gap:7px; padding:12px; border:1px solid rgba(219,234,254,.1); border-radius:14px; background:rgba(0,0,0,.11); }
    .research-item-detail dt { color:var(--muted); font-size:.82rem; font-weight:760; }
    .research-item-detail dd { margin:0; color:var(--text); line-height:1.45; overflow-wrap:break-word; word-break:normal; }
    .priority-index { width:30px; height:30px; display:grid; place-items:center; border-radius:999px; background:rgba(219,234,254,.16); color:var(--accent); font-weight:820; }
    .forecast-compact-strip { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:8px; margin:14px 0; }
    .forecast-compact-strip span { min-height:68px; display:grid; place-items:center; gap:4px; padding:9px; border:1px solid var(--line); border-radius:15px; background:rgba(255,255,255,.035); color:var(--muted); text-align:center; font-size:.75rem; }
    .forecast-compact-strip strong { color:var(--text); font-size:1.35rem; }
    .forecast-learning-row { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
    .home-view-switch { position: sticky; top: 82px; z-index: 7; display:flex; flex-wrap:wrap; gap:8px; padding:10px; border:1px solid var(--line); border-radius:var(--r16); background:rgba(11,15,20,.72); backdrop-filter:blur(18px); }
    .home-view-switch button { min-height:36px; display:inline-flex; align-items:center; gap:7px; padding:7px 11px; border:1px solid var(--line); border-radius:999px; background:rgba(255,255,255,.04); color:var(--subtle); cursor:pointer; }
    .home-view-switch button.active { background:var(--accent); color:var(--bg); }
    .home-view-switch span { min-width:22px; min-height:22px; display:grid; place-items:center; border-radius:999px; background:rgba(0,0,0,.14); font-size:.72rem; }
    .home-zone { display:grid; gap:14px; scroll-margin-top:140px; }
    .home-zone-label { display:inline-flex; align-items:center; gap:10px; color:var(--subtle); font-weight:740; }
    .home-zone-label span { width:34px; height:34px; display:grid; place-items:center; border-radius:999px; background:rgba(219,234,254,.12); color:var(--accent); font-size:.78rem; }
    .home-primary-decision { margin-top:22px; }
    .home-key-drivers { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
    .home-outlook-layout { display:grid; grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr); gap:14px; }
    .home-outlook-main { min-height:230px; }
    .home-scenario-grid { display:grid; gap:10px; }
    .scenario-card { padding:13px; border:1px solid var(--line); border-radius:var(--r12); background:rgba(255,255,255,.035); }
    .scenario-card strong { display:block; margin-bottom:7px; }
    .scenario-base { border-color:rgba(219,234,254,.3); }
    .scenario-upside { border-color:rgba(158,230,184,.28); }
    .scenario-downside { border-color:rgba(244,165,179,.28); }
    .home-safety-note { color:var(--muted); font-size:.86rem; line-height:1.45; }
    .home-impact-stack { display:grid; gap:12px; }
    .home-section-header { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; flex-wrap:wrap; }
    .candidate-filter-row { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
    .candidate-filter.active { background:var(--accent); color:var(--bg); }
    .candidate-table { display:grid; gap:7px; overflow-x:auto; }
    .candidate-header, .candidate-row { min-width:840px; display:grid; grid-template-columns:1.5fr .48fr .7fr .8fr .7fr 1fr; gap:8px; align-items:start; padding:10px; border:1px solid var(--line); border-radius:var(--r12); }
    .candidate-header { color:var(--muted); background:rgba(255,255,255,.025); font-size:.78rem; font-weight:760; text-transform:uppercase; }
    .candidate-row { background:rgba(255,255,255,.04); }
    .candidate-row strong, .candidate-row span { overflow-wrap:anywhere; }
    .candidate-row > div > span { display:block; margin-top:4px; color:var(--muted); font-size:.78rem; }
    .candidate-detail summary { cursor:pointer; color:var(--accent); }
    .candidate-detail p { margin:8px 0 0; font-size:.86rem; }
    .candidate-changes { margin-top:16px; }
    .forecast-status-strip { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:8px; margin:12px 0; }
    .forecast-status-strip span { min-height:70px; display:grid; place-items:center; gap:4px; padding:9px; border:1px solid var(--line); border-radius:var(--r12); background:rgba(255,255,255,.035); color:var(--muted); text-align:center; font-size:.72rem; }
    .forecast-status-strip strong { color:var(--text); font-size:1.25rem; }
    .home-expert-panel summary { justify-content:space-between; gap:12px; }
    .home-expert-panel summary strong { min-width:30px; height:30px; display:grid; place-items:center; border-radius:999px; background:var(--accent); color:var(--bg); }
    .expert-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; padding:14px; border-top:1px solid var(--line); }
    .expert-section { min-height:160px; padding:14px; border:1px solid var(--line); border-radius:var(--r12); background:rgba(255,255,255,.035); }
    .expert-section > span { display:inline-grid; place-items:center; width:28px; height:28px; border-radius:999px; background:rgba(219,234,254,.12); color:var(--accent); font-weight:780; }
    .expert-section h3 { margin:9px 0; font-size:1rem; }
    .causal-chain { display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
    .causal-chain span { display:inline-flex; align-items:center; min-height:34px; padding:7px 10px; border:1px solid var(--line); border-radius:999px; background:rgba(255,255,255,.04); }
    .causal-chain span:not(:last-child)::after { content:"↓"; margin-left:9px; color:var(--accent); }
    .expert-dl { display:grid; grid-template-columns:minmax(100px,.45fr) minmax(0,1fr); gap:8px; margin:0; }
    .expert-dl dt { color:var(--muted); }
    .expert-dl dd { margin:0; overflow-wrap:anywhere; }
    .confidence-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:6px; align-items:center; margin:8px 0; }
    .confidence-row i { grid-column:1 / -1; display:block; height:7px; border-radius:999px; background:var(--accent); }
    .confidence-row small { grid-column:1 / -1; color:var(--muted); }
    .expert-data-strip { grid-template-columns:repeat(4,minmax(0,1fr)); }
    .raw-evidence-details pre { max-height:300px; overflow:auto; white-space:pre-wrap; color:var(--subtle); }
    @media (max-width:1180px) { .portfolio-command-card,.holdings-primary-card,.portfolio-first-viewport .action-today-card,.portfolio-first-viewport .core-judgment-card { grid-column:1 / -1; grid-row:auto; } .investor-evidence-grid,.supporting-context-grid,.decision-first-viewport, .decision-support-grid, .home-outlook-layout, .expert-grid, .practical-secondary-grid,.practical-operational-grid,.practical-control-grid { grid-template-columns:1fr; } .scenario-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .scenario-card:nth-child(3) { border-left:0; border-top:1px solid rgba(219,234,254,.1); } .scenario-card:nth-child(4) { border-top:1px solid rgba(219,234,254,.1); } .practical-secondary-grid > *, .practical-operational-grid > *, .practical-operational-grid #home-intelligence-alerts { grid-column:auto !important; } .practical-first-viewport { grid-template-columns:1fr; grid-template-areas:"action" "core" "predictions"; } .action-today-card { min-height:0; } .decision-card-primary { grid-row:auto; } .research-priority-list { grid-template-columns:1fr; } }
    @media (max-width:900px) { .portfolio-command-metrics,.portfolio-command-analysis,.scenario-grid,.material-evidence-item dl,.holding-brief-grid,.holding-brief-card,.valuation-summary-strip { grid-template-columns:1fr; } .holding-decision-column { padding-left:0; padding-top:14px; border-left:0; border-top:1px solid rgba(219,234,254,.1); } .scenario-card,.scenario-card:nth-child(3) { border-left:0; border-top:1px solid rgba(219,234,254,.1); } .home-view-switch { position:static; } .candidate-header { display:none; } .candidate-row { min-width:0; grid-template-columns:1fr; } .forecast-status-strip, .expert-data-strip, .forecast-compact-strip, .forecast-learning-row, .trigger-columns, .conviction-grid, .funding-flow, .intelligence-alert-list li, .research-priority-card, .research-item-detail { grid-template-columns:1fr; } .action-today-card { grid-template-columns:1fr !important; grid-template-areas:"step" "kicker" "answer" "posture" "reason" "helper"; } .action-answer { font-size:clamp(2.2rem, 10vw, 3.4rem) !important; white-space:normal; overflow-wrap:anywhere; } .decision-card h1 { max-width:none; } .practical-table { display:block; overflow-x:auto; } }
    @media (max-width:640px) { .atlas-shell[data-active-page="home"] .workspace.no-inspector { padding:14px; } .portfolio-header-status { justify-items:start; text-align:left; } .valuation-visuals,.valuation-amount-grid { grid-template-columns:1fr; } .valuation-amount-grid { grid-column:auto; } .holding-title-row { align-items:flex-start; } }
    </style>
    """


def _home_intelligence_script(*, include_candidate_filters: bool = True) -> str:
    if not include_candidate_filters:
        return """
    <script>
    (function () {
      const expert = document.getElementById("expert-analysis-panel");
      if (expert) expert.open = false;
    })();
    </script>
    """
    candidate_script = """
      document.querySelectorAll("[data-candidate-filter]").forEach(function (button) {
        button.addEventListener("click", function () {
          const filter = button.getAttribute("data-candidate-filter") || "all";
          document.querySelectorAll("[data-candidate-filter]").forEach(function (item) { item.classList.toggle("active", item === button); });
          document.querySelectorAll("[data-candidate-row]").forEach(function (row) {
            const filters = (row.getAttribute("data-candidate-filters") || "all").split(" ");
            row.style.display = filters.indexOf(filter) >= 0 ? "" : "none";
          });
        });
      });
    """ if include_candidate_filters else ""
    return """
    <script>
    (function () {
      const savedMode = localStorage.getItem("atlasHomeMode") || "brief";
      function activateMode(mode, scroll) {
        document.querySelectorAll("[data-home-mode]").forEach(function (button) {
          const active = button.getAttribute("data-home-mode") === mode;
          button.classList.toggle("active", active);
          if (active && scroll) {
            const target = document.getElementById(button.getAttribute("data-home-target"));
            if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
        localStorage.setItem("atlasHomeMode", mode);
      }
      document.querySelectorAll("[data-home-mode]").forEach(function (button) {
        button.addEventListener("click", function () { activateMode(button.getAttribute("data-home-mode"), true); });
      });
      activateMode(savedMode, false);
      const expert = document.getElementById("expert-analysis-panel");
      if (expert) {
        expert.open = false;
      }
      %s
    })();
    </script>
    """ % candidate_script


def candidate_pool_content(state: Mapping[str, Any]) -> str:
    lang = current_language()
    candidates = build_home_intelligence(state)["candidate_pool"]
    return f"""
    {_home_intelligence_style()}
    <section class="hero-panel">
      <span class="kicker">{escape(_home_label("candidate_pool", lang))}</span>
      <h1 class="hero-title">{escape(_candidate_title(candidates, lang))}</h1>
      <p class="hero-copy">{escape(_home_label("candidate_safety", lang))}</p>
      <div class="pill-row" style="margin-top:18px;">
        <span class="tag">{escape(_home_label("source", lang))}: {escape(str(candidates.get("source") or ""))}</span>
        <span class="tag">{escape(_home_label("status", lang))}: {escape(str(candidates.get("status") or ""))}</span>
      </div>
    </section>
    <section class="focus-card">
      {_candidate_filters(candidates, lang)}
      {_candidate_table(candidates.get("items"), lang)}
      {_candidate_changes(candidates.get("changes"), lang)}
    </section>
    {_home_intelligence_script()}
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


def _invalidation_items(market: Mapping[str, Any], lang: str) -> list[str]:
    data_item = t("home.invalid_data_interruption", lang) if _price_has_signal(market) else t("home.invalid_no_data", lang)
    return [
        data_item,
        t("home.invalid_trust", lang),
        t("home.invalid_portfolio", lang),
    ]


def _price_has_signal(market: Mapping[str, Any]) -> bool:
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    return any(
        isinstance(item, Mapping) and item.get("data_quality_status") in {"Available", "Partial"}
        for item in observations
    )


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
    <section class="focus-card">
      <span class="kicker">{escape(t("markets.asset_sources", lang))}</span>
      <h2>{escape(t("markets.asset_sources", lang))}</h2>
      <p>{escape(t("markets.asset_sources_note", lang))}</p>
      {_asset_source_table(market, lang)}
    </section>
    """


def _asset_source_table(market: Mapping[str, Any], lang: str) -> str:
    asset_rows = market.get("asset_source_map") if isinstance(market.get("asset_source_map"), list) else []
    if not asset_rows:
        return f'<p class="empty-state">{escape(t("markets.no_source", lang))}</p>'
    rows = []
    for item in asset_rows:
        if not isinstance(item, Mapping):
            continue
        sources = item.get("sources") if isinstance(item.get("sources"), list) else []
        price = _source_cell(sources, "price_volume", lang)
        disclosure = _source_cell(sources, "company_disclosure", lang)
        attention = _source_cell(sources, "public_attention", lang)
        summary = item.get("summary") if isinstance(item.get("summary"), Mapping) else {}
        health = (
            f'{summary.get("used", 0)} {_source_status_label("USED", lang)} · '
            f'{summary.get("standby", 0)} {_source_status_label("STANDBY", lang)} · '
            f'{summary.get("failed", 0)} {_source_status_label("FAILED", lang)}'
        )
        rows.append(
            "<tr>"
            f'<td><strong>{escape(str(item.get("asset") or "Unknown"))}</strong><small>{escape(str(item.get("market") or ""))}</small></td>'
            f"<td>{price}</td><td>{disclosure}</td><td>{attention}</td><td>{escape(health)}</td>"
            "</tr>"
        )
    return f"""
    <div class="table-scroll"><table class="practical-table">
      <thead><tr>
        <th>{escape(t("markets.asset", lang))}</th>
        <th>{escape(t("markets.price_source", lang))}</th>
        <th>{escape(t("markets.disclosure_source", lang))}</th>
        <th>{escape(t("markets.attention_source", lang))}</th>
        <th>{escape(t("markets.source_health", lang))}</th>
      </tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    """


def _source_cell(sources: list[Any], channel: str, lang: str) -> str:
    selected = [item for item in sources if isinstance(item, Mapping) and item.get("channel") == channel]
    if not selected:
        return escape(t("markets.no_source", lang))
    active = [item for item in selected if item.get("status") in {"USED", "CHECKED_NO_RECENT_RECORD", "CHECKED_NOT_IN_SAMPLE", "MANUAL_REVIEW"}]
    visible = active or selected[:1]
    parts = []
    for item in visible[:2]:
        label = escape(str(item.get("label") or item.get("source_id") or "Unknown"))
        status = escape(_source_status_label(str(item.get("status") or ""), lang))
        url = str(item.get("url") or "")
        source_label = f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{label}</a>' if url else label
        parts.append(f"{source_label}<small>{status}</small>")
    return "<br>".join(parts)


def _source_status_label(status: str, lang: str) -> str:
    labels = {
        "USED": ("Used", "已使用"),
        "STANDBY": ("Standby", "待命"),
        "FAILED": ("Failed", "失败"),
        "CHECKED_NO_RECENT_RECORD": ("Checked · no recent record", "已检查 · 无近期记录"),
        "CHECKED_NOT_IN_SAMPLE": ("Checked · not in sample", "已检查 · 未进入样本"),
        "MANUAL_REVIEW": ("Manual review", "人工复核"),
    }
    en, zh = labels.get(status, (status or "Unknown", status or "未知"))
    return zh if lang == "zh" else en


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
    task_routes = state.get("llm_task_routes") if isinstance(state.get("llm_task_routes"), Mapping) else config.get("llm_task_routes", {})
    task_runtime = state.get("llm_task_runtime_state") if isinstance(state.get("llm_task_runtime_state"), Mapping) else {}
    system = config.get("system") if isinstance(config.get("system"), Mapping) else {}
    assets = config.get("assets") if isinstance(config.get("assets"), Mapping) else {}
    privacy = config.get("portfolio_privacy") if isinstance(config.get("portfolio_privacy"), Mapping) else {}
    positions = _config_positions(assets)
    available = [p for p in providers if isinstance(p, Mapping) and str(p.get("health")) in {"healthy", "reachable"}]
    other = [p for p in providers if isinstance(p, Mapping) and p not in available]
    provider_models = {
        str(provider.get("id")): provider.get("available_models", [])
        for provider in providers
        if isinstance(provider, Mapping) and isinstance(provider.get("available_models"), list)
    }
    provider_models_json = json.dumps(provider_models, ensure_ascii=False).replace("<", "\\u003c")
    content = f"""
    <style>
      .settings-position-editor {{ display:grid; gap:14px; }}
      .settings-position-editor .asset-row {{ display:block; padding:18px; }}
      .position-row-head {{ display:grid; grid-template-columns:minmax(180px,1.25fr) minmax(120px,.7fr) minmax(120px,.55fr) auto; gap:10px; align-items:end; }}
      .position-row-fields {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-top:14px; padding-top:14px; border-top:1px solid var(--line); }}
      .position-row-fields .position-wide {{ grid-column:span 2; }}
      .position-row-fields textarea {{ min-height:74px; resize:vertical; }}
      .position-field-note {{ display:block; margin-top:6px; color:var(--subtle); font-size:.76rem; line-height:1.4; }}
      .portfolio-privacy-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-top:14px; }}
      .privacy-option {{ display:flex; align-items:center; gap:10px; min-height:48px; padding:10px 12px; border:1px solid var(--line); border-radius:12px; background:rgba(255,255,255,.025); }}
      .privacy-option input {{ width:18px; min-height:18px; margin:0; }}
      [data-field-error="true"] {{ border-color:rgba(248,113,113,.72) !important; box-shadow:0 0 0 2px rgba(248,113,113,.12); }}
      @media (max-width:900px) {{ .position-row-head,.position-row-fields,.portfolio-privacy-grid {{ grid-template-columns:1fr 1fr; }} .position-row-fields .position-wide {{ grid-column:1/-1; }} }}
      @media (max-width:580px) {{ .position-row-head,.position-row-fields,.portfolio-privacy-grid {{ grid-template-columns:1fr; }} .position-row-fields .position-wide {{ grid-column:auto; }} }}
    </style>
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
    <section id="task-routing-config" class="focus-card">
      <span class="kicker">{escape(t("task_routing.title", lang))}</span>
      <h2>{escape(t("task_routing.title", lang))}</h2>
      <p>{escape(t("task_routing.subtitle", lang))}</p>
      <div class="page-content">{_task_route_controls(task_routes, task_runtime, providers, lang)}</div>
      <script type="application/json" id="task-provider-models">{provider_models_json}</script>
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
      <h2>{escape(t("portfolio.valuation_title", lang))}</h2>
      <p>{escape(t("portfolio.valuation_note", lang))}</p>
      <div id="asset-rows" class="settings-position-editor">{_asset_rows(positions, lang)}</div>
      <div class="button-row" style="margin-top: 12px;">
        <button class="secondary-button" type="button" id="add-asset-row">{escape(t("setup.add_asset", lang))}</button>
      </div>
      <div class="portfolio-privacy-grid" aria-label="{escape(t('portfolio.privacy_title', lang))}">
        <label class="privacy-option"><input id="show-cost-price" type="checkbox"{' checked' if privacy.get('show_cost_price', True) else ''}><span>{escape(t("portfolio.show_cost", lang))}</span></label>
        <label class="privacy-option"><input id="show-pnl-percentage" type="checkbox"{' checked' if privacy.get('show_pnl_percentage', True) else ''}><span>{escape(t("portfolio.show_return", lang))}</span></label>
        <label class="privacy-option"><input id="show-quantity" type="checkbox"{' checked' if privacy.get('show_quantity', False) else ''}><span>{escape(t("portfolio.show_quantity", lang))}</span></label>
        <label class="privacy-option"><input id="show-amounts" type="checkbox"{' checked' if privacy.get('show_amounts', False) else ''}><span>{escape(t("portfolio.show_amounts", lang))}</span></label>
      </div>
      <p class="home-safety-note">{escape(t("portfolio.private_local_note", lang))}</p>
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
      ,task_testing: zh ? "正在测试任务路由..." : "Testing task route..."
      ,task_checked: zh ? "任务路由测试完成" : "Task route test complete"
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
      if (item.average_cost_price) item.average_cost_price = Number(item.average_cost_price);
      else delete item.average_cost_price;
      if (item.quantity) item.quantity = Number(item.quantity);
      else delete item.quantity;
      if (item.average_cost_price) {
        item.cost_basis_method = "user_supplied_adjusted_average_cost";
        if (String(item.average_cost_price) !== String(row.dataset.originalCost || "")) item.cost_updated_at = new Date().toISOString();
      } else {
        delete item.position_currency;
        delete item.cost_updated_at;
      }
      return item;
    }).filter(function (item) { return item.asset; });
  }
  function taskRoutes() {
    const routes = {};
    document.querySelectorAll("[data-task-route]").forEach(function (card) {
      const role = card.dataset.taskRoute;
      routes[role] = {
        enabled: card.querySelector('[data-task-field="enabled"]').checked,
        provider_id: card.querySelector('[data-task-field="provider_id"]').value,
        model: card.querySelector('[data-task-field="model"]').value.trim(),
        fallback_chain: card.querySelector('[data-task-field="fallback_chain"]').value.split(",").map(function (x) { return x.trim(); }).filter(Boolean),
        timeout_seconds: Number(card.querySelector('[data-task-field="timeout_seconds"]').value || 30),
        max_output_tokens: Number(card.querySelector('[data-task-field="max_output_tokens"]').value || 2000),
        reasoning_effort: card.querySelector('[data-task-field="reasoning_effort"]').value
      };
    });
    return routes;
  }
  function assetTemplate() {
    const clone = document.querySelector("[data-asset-row]").cloneNode(true);
    clone.dataset.originalCost = "";
    clone.querySelectorAll("[data-asset-field]").forEach(function (field) {
      field.value = field.dataset.assetField === "position_currency" ? "CNY" : "";
      field.removeAttribute("data-field-error");
      field.setCustomValidity("");
    });
    return clone.outerHTML;
  }
  function validatePositions() {
    let valid = true;
    document.querySelectorAll("#asset-rows [data-asset-row]").forEach(function (row) {
      row.querySelectorAll("[data-asset-field]").forEach(function (field) { field.setCustomValidity(""); field.removeAttribute("data-field-error"); });
      const cost = row.querySelector('[data-asset-field="average_cost_price"]');
      const quantity = row.querySelector('[data-asset-field="quantity"]');
      const currency = row.querySelector('[data-asset-field="position_currency"]');
      if (cost.value && Number(cost.value) <= 0) { cost.setCustomValidity("positive"); cost.dataset.fieldError = "true"; valid = false; }
      if (quantity.value && Number(quantity.value) <= 0) { quantity.setCustomValidity("positive"); quantity.dataset.fieldError = "true"; valid = false; }
      if (cost.value && !currency.value) { currency.setCustomValidity("required"); currency.dataset.fieldError = "true"; valid = false; }
    });
    if (!valid) document.querySelector("#asset-rows :invalid")?.reportValidity();
    return valid;
  }
  async function saveSettings() {
    if (!validatePositions()) {
      document.getElementById("settings-result").textContent = document.documentElement.lang === "zh" ? "保存前请检查高亮的持仓字段。" : "Check the highlighted position fields before saving.";
      return { status: "validation_error" };
    }
    const assets = assetRows("asset-rows");
    const payload = {
      ui: { language: document.getElementById("global-language-select") ? document.getElementById("global-language-select").value : "en" },
      llm_registry: {
        active_provider: document.getElementById("settings-active-provider").value,
        strict_provider_list: true,
        fallback_chain: providerCards().map(function (p) { return p.id; }),
        providers: providerCards()
      },
      llm_task_routes: taskRoutes(),
      system: {
        tick_interval: Number(document.getElementById("tick-interval-setting").value || 60),
        proactive_update_enabled: true,
        proactive_update_interval_seconds: Number(document.getElementById("proactive-update-interval-setting").value || 7200),
        runtime_mode: document.getElementById("runtime-mode-setting").value,
        trust_threshold: Number(document.getElementById("trust-threshold-setting").value || 0.45),
        hypothesis_switching_sensitivity: Number(document.getElementById("hypothesis-sensitivity-setting").value || 0.08)
      },
      assets: { portfolio_json: JSON.stringify({ positions: assets }), asset_list: assets.map(function (x) { return x.asset; }), weights: Object.fromEntries(assets.map(function (x) { return [x.asset, x.portfolio_percentage]; })) },
      portfolio_privacy: {
        show_cost_price: document.getElementById("show-cost-price").checked,
        show_pnl_percentage: document.getElementById("show-pnl-percentage").checked,
        show_quantity: document.getElementById("show-quantity").checked,
        show_amounts: document.getElementById("show-amounts").checked
      },
      metadata: { ui_only: true, no_runtime_reload: true, no_trading_execution: true }
    };
    const response = await fetch("/settings", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (data.status === "validation_error") {
      (data.errors || []).forEach(function (error) {
        const row = document.querySelectorAll("#asset-rows [data-asset-row]")[error.position_index];
        const field = row?.querySelector('[data-asset-field="' + error.field + '"]');
        if (field) { field.dataset.fieldError = "true"; field.setCustomValidity(error.code || "invalid"); }
      });
      document.getElementById("settings-result").textContent = document.documentElement.lang === "zh" ? "保存前请检查高亮的持仓字段。" : "Check the highlighted position fields before saving.";
    } else {
      document.getElementById("settings-result").textContent = data.status === "saved" ? msg("saved") : msg("save_failed");
    }
    return data;
  }
  document.getElementById("save-settings").addEventListener("click", saveSettings);
  document.getElementById("add-asset-row").addEventListener("click", function () {
    document.getElementById("asset-rows").insertAdjacentHTML("beforeend", assetTemplate());
  });
  document.getElementById("asset-rows").addEventListener("click", function (event) {
    if (!event.target.matches("[data-remove-asset]")) return;
    const rows = document.querySelectorAll("#asset-rows [data-asset-row]");
    if (rows.length > 1) event.target.closest("[data-asset-row]").remove();
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
  document.querySelectorAll("[data-test-task-route]").forEach(function (button) {
    button.addEventListener("click", async function () {
      await saveSettings();
      const card = button.closest("[data-task-route]");
      const role = card.dataset.taskRoute;
      const status = card.querySelector("[data-task-call-status]");
      status.textContent = msg("task_testing");
      try {
        const response = await fetch("/llm/task-route/test", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ task_role: role }) });
        const data = await response.json();
        status.textContent = (data.status || "unknown") + " · " + (data.provider || "--") + " · " + (data.latency_ms ?? "--") + "ms";
      } catch (error) {
        status.textContent = msg("test_failed");
      }
    });
  });
  const providerModels = JSON.parse(document.getElementById("task-provider-models")?.textContent || "{}");
  document.querySelectorAll('[data-task-field="provider_id"]').forEach(function (select) {
    select.addEventListener("change", function () {
      const card = select.closest("[data-task-route]");
      const datalist = card.querySelector("datalist");
      datalist.innerHTML = (providerModels[select.value] || []).map(function (model) { return '<option value="' + String(model).replace(/"/g, "&quot;") + '"></option>'; }).join("");
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


def _task_route_controls(
    routes: Mapping[str, Any],
    runtime: Mapping[str, Any],
    providers: list[Any],
    lang: str,
) -> str:
    controls = []
    for role in ("workhorse", "research", "decision"):
        route = routes.get(role, {}) if isinstance(routes.get(role), Mapping) else {}
        latest = runtime.get(role, {}) if isinstance(runtime.get(role), Mapping) else {}
        provider_id = str(route.get("provider_id") or "")
        provider = next(
            (item for item in providers if isinstance(item, Mapping) and str(item.get("id")) == provider_id),
            {},
        )
        models = provider.get("available_models", []) if isinstance(provider.get("available_models"), list) else []
        usage = latest.get("usage", {}) if isinstance(latest.get("usage"), Mapping) else {}
        total_tokens = usage.get("total_tokens")
        usage_text = str(total_tokens) if total_tokens is not None else "Unknown"
        latency = latest.get("latency_ms")
        route_status = str(route.get("route_status") or ("ACTIVE" if route.get("enabled") else "DISABLED"))
        decision_style = "background:rgba(255,255,255,.035);border-left:3px solid rgba(244,247,251,.72);padding-left:18px;" if role == "decision" else ""
        controls.append(
            f"""
            <div data-task-route="{role}" style="padding:18px 0;border-top:1px solid rgba(255,255,255,.08);{decision_style}">
              <div class="section-heading">
                <div><span class="kicker">{escape(t(f'task_routing.{role}', lang))}</span><h3>{escape(t(f'task_routing.{role}', lang))}</h3></div>
                <span class="status-pill">{escape(route_status)}{' · ' + escape(t('task_routing.authoritative', lang)) if role == 'decision' else ''}</span>
              </div>
              <p>{escape(t(f'task_routing.{role}_note', lang))}</p>
              <div class="form-grid">
                <label><span>{escape(t('task_routing.enabled', lang))}</span><input data-task-field="enabled" type="checkbox" style="width:18px;height:18px;min-height:0;padding:0;"{' checked' if route.get('enabled') else ''}></label>
                <label>{escape(t('task_routing.provider', lang))}<select data-task-field="provider_id">{_provider_options(providers, provider_id)}</select></label>
                <label>{escape(t('model.model', lang))}<input data-task-field="model" list="task-models-{role}" value="{escape(str(route.get('model') or ''))}" placeholder="{escape(t('provider.custom_model_placeholder', lang))}"><datalist id="task-models-{role}">{''.join(f'<option value="{escape(str(model))}"></option>' for model in models)}</datalist></label>
                <label>{escape(t('settings.fallback', lang))}<input data-task-field="fallback_chain" value="{escape(', '.join(str(item) for item in route.get('fallback_chain', [])))}"></label>
                <label>{escape(t('task_routing.timeout', lang))}<input data-task-field="timeout_seconds" type="number" min="1" max="120" value="{escape(str(route.get('timeout_seconds') or 30))}"></label>
                <label>{escape(t('task_routing.max_tokens', lang))}<input data-task-field="max_output_tokens" type="number" min="128" max="32000" value="{escape(str(route.get('max_output_tokens') or 2000))}"></label>
                <label>{escape(t('task_routing.reasoning', lang))}<select data-task-field="reasoning_effort"><option value="">--</option><option value="low"{_selected(route.get('reasoning_effort'), 'low')}>low</option><option value="medium"{_selected(route.get('reasoning_effort'), 'medium')}>medium</option><option value="high"{_selected(route.get('reasoning_effort'), 'high')}>high</option></select></label>
              </div>
              <div class="section-grid" style="margin-top:12px;">
                {_metric(t('provider.latency', lang), str(latency) + 'ms' if latency is not None else '--', str(provider.get('health') or 'unknown'))}
                {_metric(t('task_routing.usage', lang), usage_text, t('task_routing.last_call', lang))}
                {_metric(t('task_routing.cost', lang), str(latest.get('cost_status') or 'Unknown'), str(latest.get('estimated_cost', 'Unknown')))}
              </div>
              <div class="button-row" style="margin-top:12px;"><button class="secondary-button" type="button" data-test-task-route>{escape(t('task_routing.test', lang))}</button><span data-task-call-status>{escape(str(latest.get('status') or 'not_run'))}</span></div>
            </div>
            """
        )
    return "".join(controls)


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
    cost = str(item.get("average_cost_price") or "")
    quantity = str(item.get("quantity") or "")
    currency = str(item.get("position_currency") or _default_position_currency(item) or "CNY")
    cost_updated = str(item.get("cost_updated_at") or "")
    return f"""
    <div class="asset-row" data-asset-row data-original-cost="{escape(cost)}">
      <div class="position-row-head">
        <label>{escape(t("setup.asset", lang))}<input data-asset-field="asset" value="{escape(str(item.get("asset") or ""))}" placeholder="002384.SZ"></label>
        <label>{escape(t("setup.market", lang))}<input data-asset-field="market" value="{escape(str(item.get("market") or ""))}" placeholder="A-share / HK / US"></label>
        <label>{escape(t("setup.percentage", lang))}<input data-asset-field="portfolio_percentage" type="number" min="0" max="100" step="0.1" value="{escape(str(item.get("portfolio_percentage") or ""))}"></label>
        <button class="ghost-button" type="button" data-remove-asset>{escape(t("settings.remove", lang))}</button>
      </div>
      <div class="position-row-fields">
        <label>{escape(t("portfolio.average_cost", lang))}<input data-asset-field="average_cost_price" type="number" min="0.000001" step="any" inputmode="decimal" value="{escape(cost)}"><small class="position-field-note">{escape(t("portfolio.cost_missing_note", lang))}</small></label>
        <label>{escape(t("portfolio.quantity_optional", lang))}<input data-asset-field="quantity" type="number" min="0.000001" step="any" inputmode="decimal" value="{escape(quantity)}"><small class="position-field-note">{escape(t("portfolio.quantity_optional_note", lang))}</small></label>
        <label>{escape(t("portfolio.cost_currency", lang))}<select data-asset-field="position_currency"><option value="CNY"{_selected(currency, 'CNY')}>CNY</option><option value="HKD"{_selected(currency, 'HKD')}>HKD</option><option value="USD"{_selected(currency, 'USD')}>USD</option></select></label>
        <label>{escape(t("portfolio.cost_updated", lang))}<input data-asset-field="cost_updated_at" type="hidden" value="{escape(cost_updated)}"><span class="position-field-note">{escape(cost_updated or ('保存成本后记录' if lang == 'zh' else 'Recorded after cost is saved'))}</span></label>
        <label>{escape(t("setup.theme", lang))}<input data-asset-field="theme" value="{escape(str(item.get("theme") or ""))}" placeholder="AI"></label>
        <label>{escape(t("setup.role", lang))}<input data-asset-field="role" value="{escape(str(item.get("role") or ""))}" placeholder="Core"></label>
        <label class="position-wide">{escape(t("setup.thesis", lang))}<textarea data-asset-field="user_thesis" rows="2">{escape(str(item.get("user_thesis") or item.get("thesis") or ""))}</textarea></label>
        <label class="position-wide">{escape(t("setup.risk_note", lang))}<textarea data-asset-field="risk_note" rows="2">{escape(str(item.get("risk_note") or ""))}</textarea></label>
      </div>
    </div>
    """


def _default_position_currency(item: Mapping[str, Any]) -> str:
    market = str(item.get("market") or "").strip().lower()
    asset = str(item.get("asset") or "").strip().upper()
    if asset.endswith(".HK") or market == "hk":
        return "HKD"
    if asset.endswith((".SH", ".SS", ".SZ")) or market in {"a-share", "ashare", "cn"}:
        return "CNY"
    return "USD" if market == "us" else "CNY"


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
