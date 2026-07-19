"""Read-only Home intelligence presentation adapter.

This module only projects existing Atlas repository/runtime evidence into UI
view models. It does not create forecasts, mutate cognition, alter portfolio
state, or change trading authority.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from ui.presentation.cognitive_localization import (
    localize_evidence_headline,
    localize_inline_tokens,
    localize_regime,
    localized_risk,
)


CANDIDATE_SOURCE_PATH = Path("02_Databases/AI_Shovel_100.md")
TICKER_REGISTRY_PATH = Path("tools/market_data/ticker_registry.yaml")
BOTTLENECK_MAP_PATH = Path("04_Current_State/Bottleneck_Map_v1.md")
CAPITAL_RELAY_PATH = Path("01_Framework/Capital_Relay.md")
AI_CAPITAL_MAP_PATH = Path("04_Current_State/AI_Capital_Map_v1.md")
CAPITAL_ALLOCATION_PATH = Path("03_Trading_OS/Capital_Allocation_Board.md")
CAPITAL_ROTATION_PATH = Path("03_Trading_OS/Capital_Rotation_Table.md")
RISK_RADAR_PATH = Path("02_Databases/Risk_Radar.md")
FORECAST_STATUSES = ("OPEN", "MATURED", "VERIFIED", "INVALIDATED", "INCONCLUSIVE")
NO_TRADE_ACTIONS = {"buy", "sell"}
USABLE_OBSERVATION_QUALITY = {"available", "partial"}
UNUSABLE_SOURCES = {"", "none", "unknown", "unavailable", "data missing"}
FRESH_FRESHNESS = {"live", "fresh", "available"}


def build_home_intelligence(state: Mapping[str, Any]) -> dict[str, Any]:
    """Build all read-only Home intelligence panels from current state."""

    ledger = _mapping(state.get("forecast_ledger"))
    candidate_pool = _mapping(state.get("candidate_pool")) or build_candidate_pool(
        portfolio_context=_mapping(state.get("portfolio_context"))
    )
    market_outlook = build_market_outlook(state, ledger)
    forecast_accountability = build_forecast_accountability(ledger)
    expert_analysis = build_expert_analysis(state, ledger)
    return {
        "practical_brief": build_practical_decision_brief(
            state,
            forecast_accountability=forecast_accountability,
            candidate_pool=candidate_pool,
            expert_analysis=expert_analysis,
        ),
        "decision_home": build_user_decision_home(
            state,
            market_outlook=market_outlook,
            forecast_accountability=forecast_accountability,
            candidate_pool=candidate_pool,
            expert_analysis=expert_analysis,
        ),
        "market_outlook": market_outlook,
        "forecast_accountability": forecast_accountability,
        "candidate_pool": candidate_pool,
        "expert_analysis": expert_analysis,
        "source_boundaries": {
            "read_only": True,
            "no_new_cognition": True,
            "no_trading_execution": True,
            "candidate_ranking_not_buy_recommendation": True,
        },
    }


def build_practical_decision_brief(
    state: Mapping[str, Any],
    *,
    forecast_accountability: Mapping[str, Any],
    candidate_pool: Mapping[str, Any],
    expert_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the user-validated practical decision brief chain.

    This is a presentation projection only. It reads current runtime state and
    repository truth sources, but does not create forecasts, mutate portfolio
    state, or change CDE/trading authority.
    """

    packet = _mapping(state.get("last_decision_packet"))
    market = _mapping(state.get("market_intelligence"))
    local_valuation = _mapping(state.get("local_portfolio_valuation"))
    portfolio = _mapping(state.get("portfolio_context"))
    brief_runtime = _mapping(state.get("brief_runtime_state"))
    evidence_assessment = _mapping(state.get("evidence_assessment_state"))
    candidate_overlay = _mapping(state.get("candidate_runtime_overlay"))
    ledger = _mapping(state.get("forecast_ledger"))
    bottlenecks = _bottleneck_index()
    capital_relay = _capital_relay()
    triggers = _waiting_triggers(market, forecast_accountability, bottlenecks)
    allocation = _capital_allocation_board(portfolio, bottlenecks, triggers)
    predictions = _strongest_predictions(ledger, packet, market)
    holdings = _current_holdings_board(portfolio, market, local_valuation, packet)
    action = _action_today(packet, market, portfolio)
    portfolio_command = _portfolio_command(portfolio, market, action)
    material_changes = _material_changes(market, evidence_assessment)
    reasoning_chain = _investor_reasoning_chain(material_changes, portfolio, packet)
    scenarios = _scenario_outlook(state, market, portfolio, forecast_accountability)
    playbook = _conditional_action_playbook(scenarios, portfolio)
    candidate_board = _candidate_score_board(candidate_pool, market, candidate_overlay)
    return {
        "chain_order": [
            "portfolio_command",
            "current_holdings",
            "action_today",
            "material_changes",
            "reasoning_chain",
            "scenario_outlook",
            "action_playbook",
            "candidate_board",
            "forecast_accountability",
            "supporting_context",
        ],
        "portfolio_command": portfolio_command,
        "action_today": action,
        "core_judgment": _practical_core_judgment(
            packet,
            market,
            portfolio,
            capital_relay,
            evidence_assessment,
        ),
        "strongest_predictions": predictions,
        "material_changes": material_changes,
        "reasoning_chain": reasoning_chain,
        "scenario_outlook": scenarios,
        "action_playbook": playbook,
        "candidate_board": candidate_board,
        "ai_bottleneck_index": bottlenecks,
        "capital_relay": capital_relay,
        "current_holdings": holdings,
        "capital_allocation": allocation,
        "waiting_triggers": triggers,
        "research_tasks": _top_research_tasks(portfolio, candidate_pool),
        "candidate_source_truth": _candidate_source_truth(candidate_pool),
        "intelligence_alerts": _intelligence_alerts(state, market, portfolio),
        "counter_argument": _counter_argument(),
        "review_plan": _review_plan(state, ledger, triggers),
        "forecast_accountability": _decision_forecast_compact(forecast_accountability),
        "expert_analysis": {
            "collapsed_by_default": True,
            "section_count": expert_analysis.get("section_count", 0),
        },
        "brief_runtime": brief_runtime,
        "source_boundaries": {
            "presentation_only": True,
            "read_only": True,
            "no_cognition_semantics_change": True,
            "no_forecast_semantics_change": True,
            "no_portfolio_mutation": True,
            "no_trading_execution": True,
            "private_amounts_local_home_only": True,
            "no_private_amounts_in_cognition_or_llm": True,
        },
    }


def _portfolio_command(
    portfolio: Mapping[str, Any],
    market: Mapping[str, Any],
    action: Mapping[str, Any],
) -> dict[str, Any]:
    exposure = _mapping(portfolio.get("exposure_map"))
    asset_concentration = [_mapping(item) for item in _list(exposure.get("asset_concentration")) if isinstance(item, Mapping)]
    theme_concentration = _mapping(exposure.get("theme_concentration"))
    largest_asset = asset_concentration[0] if asset_concentration else {}
    largest_theme = max(theme_concentration.items(), key=lambda item: _safe_number(item[1], 0.0)) if theme_concentration else ("Unknown", 0.0)
    exposure_pct = _safe_number(portfolio.get("exposure_sum_pct"), 0.0)
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    consistency = _text(portfolio.get("portfolio_consistency"), "Unknown")
    usable = _usable_market_observations(market)
    return {
        "status": portfolio.get("status", "missing"),
        "source": portfolio.get("source"),
        "portfolio_consistency": consistency,
        "exposure_pct": exposure_pct,
        "unassigned_pct": buffer_pct,
        "position_count": len(_list(portfolio.get("positions"))),
        "largest_asset": largest_asset,
        "largest_theme": {"theme": largest_theme[0], "exposure_pct": largest_theme[1]},
        "market_concentration": _mapping(exposure.get("market_concentration")),
        "theme_concentration": theme_concentration,
        "liquidity_sensitivity": exposure.get("liquidity_sensitivity", "Unknown"),
        "regime_sensitivity": exposure.get("regime_sensitivity", "Unknown"),
        "primary_risk": _bilingual(
            f"Largest theme exposure is {largest_theme[0]} at {_safe_number(largest_theme[1], 0.0):.1f}%; correlated evidence or liquidity shocks can affect several positions together.",
            f"最大主题暴露为 {largest_theme[0]}，占 {_safe_number(largest_theme[1], 0.0):.1f}%；相关证据或流动性冲击可能同时影响多个持仓。",
        ),
        "market_evidence": {
            "usable": len(usable),
            "total": len(_list(market.get("observations"))),
            "timestamp": market.get("timestamp"),
        },
        "action_status": action.get("status"),
        "posture": action.get("posture_label"),
        "action_reason": action.get("reason"),
        "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
        "human_summary": _human_summary(portfolio, market, action, largest_theme, usable),
        "because_bullets": _because_bullets(portfolio, market, action, largest_theme, usable),
    }


def _human_summary(
    portfolio: Mapping[str, Any],
    market: Mapping[str, Any],
    action: Mapping[str, Any],
    largest_theme: tuple[str, float],
    usable: list[dict[str, Any]],
) -> dict[str, str]:
    exposure_pct = _safe_number(portfolio.get("exposure_sum_pct"), 0.0)
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    regime = _text(action.get("regime_state") or market.get("regime_state"), "Unknown")
    posture_key = _text(action.get("posture") or action.get("recommended_action"), "observe").lower()
    posture = _action_label(posture_key).get("en", "Observe")
    review = "a portfolio risk review is required" if posture_key == "reduce" else "no new capital deployment is suggested right now"
    review_zh = "需要进行组合风险复核" if posture_key == "reduce" else "目前不建议新增资本部署"
    en = (
        f"Atlas sees {len(usable)} usable market signals today. "
        f"Your portfolio is {exposure_pct:.1f}% exposed, mostly to {largest_theme[0]} ({largest_theme[1]:.1f}%). "
        f"The market state is {localize_regime(regime, 'en')}. "
        f"Atlas's posture is {posture}: {review}."
    )
    zh = (
        f"Atlas 今天看到 {len(usable)} 个可用市场信号。"
        f"你的组合已配置 {exposure_pct:.1f}%，最大暴露主题是 {largest_theme[0]}（{largest_theme[1]:.1f}%）。"
        f"当前市场状态为「{localize_regime(regime, 'zh')}」。"
        f"Atlas 的姿态是「{_action_label(posture_key).get('zh', '观察')}」：{review_zh}。"
    )
    return _bilingual(en, zh)


def _because_bullets(
    portfolio: Mapping[str, Any],
    market: Mapping[str, Any],
    action: Mapping[str, Any],
    largest_theme: tuple[str, float],
    usable: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    exposure_pct = _safe_number(portfolio.get("exposure_sum_pct"), 0.0)
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    regime = _text(action.get("regime_state") or market.get("regime_state"), "Unknown")
    total = len(_list(market.get("observations")))
    bullets = [
        _bilingual(
            f"{len(usable)} of {total} market observations are usable and portfolio-linked.",
            f"{total} 个市场观测中有 {len(usable)} 个可用且与组合相关。",
        ),
        _bilingual(
            f"The largest theme is {largest_theme[0]} at {largest_theme[1]:.1f}%; liquidity and theme confirmation matter more than index direction.",
            f"最大主题是 {largest_theme[0]}（{largest_theme[1]:.1f}%），流动性和主题确认比单纯指数方向更重要。",
        ),
        _bilingual(
            f"Market state is {localize_regime(regime, 'en')} with {buffer_pct:.1f}% unassigned buffer, so Atlas keeps observing before raising risk.",
            f"市场状态为「{localize_regime(regime, 'zh')}」，未部署资金 {buffer_pct:.1f}%，因此 Atlas 选择先观察再考虑提高风险。",
        ),
    ]
    return bullets


def _material_changes(
    market: Mapping[str, Any],
    evidence_assessment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    assessment = _mapping(evidence_assessment)
    assessed_items = _mapping(assessment.get("items"))
    items: list[dict[str, Any]] = []
    for observation in _usable_market_observations(market):
        asset = _text(observation.get("asset"), "Unknown")
        evidence_id = _observation_evidence_id(observation)
        runtime_assessment = _mapping(assessed_items.get(evidence_id))
        price = observation.get("latest_price")
        change = observation.get("daily_change_pct")
        headline = f"{asset}: provider price observation available"
        if price is not None:
            headline = f"{asset}: {price}"
            if change is not None:
                headline += f" ({_safe_float(change, 0.0):+.2f}%)"
        items.append(
            {
                "headline": headline,
                "source": observation.get("source"),
                "source_url": observation.get("source_url"),
                "timestamp": observation.get("timestamp"),
                "freshness": observation.get("freshness"),
                "source_type": observation.get("source_type"),
                "classification": "LIVE_OBSERVATION" if _text(observation.get("freshness"), "").upper() == "LIVE" else "PROVIDER_OBSERVATION",
                "verification_status": "VERIFIED_PROVIDER_RESPONSE",
                "affected_assets": [asset],
                "affected_themes": [observation.get("theme")],
                "world_model_node": "Price / Volume",
                "evidence_id": evidence_id,
                "thesis_changed": runtime_assessment.get("status", "UNCERTAIN"),
                "assessment_reason": runtime_assessment.get("reason", "price_observation_requires_context"),
                "market_session_status": observation.get("market_session_status"),
            }
        )
    for evidence in _list(market.get("evidence_items")):
        if isinstance(evidence, Mapping):
            item = dict(evidence)
            evidence_id = _text(item.get("evidence_id"), "")
            runtime_assessment = _mapping(assessed_items.get(evidence_id))
            item["thesis_changed"] = runtime_assessment.get(
                "status",
                item.get("thesis_changed", "NEEDS_REVIEW"),
            )
            item["assessment_reason"] = runtime_assessment.get("reason", "assessment_not_available")
            items.append(item)
    items.sort(key=lambda item: _text(item.get("timestamp"), ""), reverse=True)
    return {
        "items": items[:8],
        "total": len(items),
        "empty_message": _bilingual(
            "No verified material evidence is currently available.",
            "当前没有可用的已验证重要证据。",
        ),
        "news_is_signal_not_action": True,
        "review_summary": assessment.get("summary", {}),
        "reviewed_at": assessment.get("assessed_at"),
    }


def _investor_reasoning_chain(
    changes: Mapping[str, Any],
    portfolio: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    items = [_mapping(item) for item in _list(changes.get("items")) if isinstance(item, Mapping)]
    primary = items[0] if items else {}
    fallback = _decision_packet_is_fallback(packet)
    affected = _list(primary.get("affected_assets"))
    raw_action = _text(packet.get("recommended_action"), "neutral").lower()
    risk = _text(packet.get("risk_level"), "unknown").lower()
    if fallback:
        conclusion = _bilingual(
            "Preserve the previous valid posture; latest reasoning is unavailable and no execution authority is created.",
            "保留上一有效姿态；最新推理不可用，不创建任何执行权限。",
        )
    elif raw_action == "reduce" or risk in {"high", "severe"}:
        conclusion = _bilingual(
            "Reduce is the current portfolio-level review posture; no order or holding-specific execution authority is generated.",
            "当前组合级复核姿态为降低暴露；不生成订单或单持仓执行权限。",
        )
    else:
        conclusion = _bilingual(
            "Observe is the current portfolio-level posture; no thesis or capital-authority change is claimed.",
            "当前组合级姿态为观察；不主张论点或资本权限变化。",
        )
    thesis_status = primary.get("thesis_changed", "UNASSESSED")
    thesis_zh = {
        "UNCHANGED": "结论不变",
        "CHANGED": "判断已改变",
        "NEEDS_REVIEW": "待复核",
        "UNCERTAIN": "不确定",
        "UNASSESSED": "尚未评估",
    }.get(str(thesis_status).upper(), str(thesis_status))
    verification = str(primary.get("verification_status", "UNVERIFIED"))
    verification_zh = {
        "VERIFIED_PROVIDER_RESPONSE": "数据源响应已验证",
        "UNVERIFIED": "尚未验证",
    }.get(verification.upper(), verification)
    node = str(primary.get("world_model_node", "Unknown"))
    node_zh = {"Price / Volume": "价格 / 成交量"}.get(node, node)
    causal_text = (
        _bilingual("Not evaluated: latest LLM reasoning failed", "未评估：最新推理失败")
        if fallback
        else _bilingual(_text(packet.get("causal_summary"), "Unknown"), localize_inline_tokens(_text(packet.get("causal_summary"), "未知"), "zh"))
    )
    return {
        "status": "evidence_available" if primary else "data_missing",
        "steps": [
            {"key": "signal", "value": primary.get("headline") and _bilingual(str(primary.get("headline")), localize_evidence_headline(primary.get("headline"), "zh")) or _bilingual("Data Missing", "数据缺失"), "truth": "SIGNAL" if primary else "DATA MISSING"},
            {"key": "evidence", "value": _bilingual(f"{primary.get('source', 'Data Missing')} · {verification}", f"{primary.get('source', '数据缺失')} · {verification_zh}"), "truth": primary.get("classification", "DATA MISSING")},
            {"key": "structure", "value": _bilingual(node, node_zh), "truth": "STRUCTURAL INTERPRETATION" if primary else "DATA MISSING"},
            {"key": "causal", "value": causal_text, "truth": "UNVERIFIED" if fallback else "INFERENCE"},
            {"key": "thesis", "value": _bilingual(str(thesis_status), thesis_zh), "truth": str(thesis_status)},
            {"key": "portfolio", "value": ", ".join(str(item) for item in affected) if affected else f"Broad portfolio exposure {_safe_number(portfolio.get('exposure_sum_pct'), 0.0):.1f}%", "truth": "PORTFOLIO MAPPING"},
            {"key": "counter", "value": _bilingual("No conclusion until counter-evidence and invalidation conditions are reviewed.", "复核反证与失效条件前不下结论。"), "truth": "FRAMEWORK SNAPSHOT"},
            {"key": "missing", "value": _bilingual("Narrative/attention and evaluated forecast evidence remain incomplete.", "叙事/关注度与已评估预测证据仍不完整。"), "truth": "DATA MISSING"},
            {"key": "conclusion", "value": conclusion, "truth": "CONDITIONAL CONCLUSION"},
        ],
    }


def _scenario_outlook(
    state: Mapping[str, Any],
    market: Mapping[str, Any],
    portfolio: Mapping[str, Any],
    forecast: Mapping[str, Any],
) -> dict[str, Any]:
    channels = _mapping(market.get("channels"))
    metrics = _mapping(forecast.get("metrics"))
    calibrated = _safe_number(metrics.get("evaluated"), 0.0) >= 20
    top_assets = [str(_mapping(item).get("asset")) for item in _list(_mapping(portfolio.get("exposure_map")).get("asset_concentration"))[:3]]
    sensitivity = ", ".join(top_assets) or "Configured portfolio"
    common = {
        "horizon": _bilingual("Next review cycle", "下一复核周期"),
        "portfolio_sensitivity": sensitivity,
        "evidence_confidence": _bilingual("Limited", "有限") if not calibrated else _bilingual("Calibrated", "已校准"),
        "probability": None,
    }
    scenarios = [
        {
            **common,
            "key": "base",
            "statement": _bilingual("Evidence remains mixed; preserve optionality while source freshness and thesis impact are verified.", "证据仍然混合；在数据新鲜度和论点影响完成验证前，保留组合选择权。"),
            "drivers": [_bilingual("Portfolio context", "当前组合结构"), _bilingual("Available provider evidence", "可用数据源证据"), _bilingual("Framework snapshot", "框架快照")],
            "counter_evidence": [_bilingual("Narrative and attention coverage is incomplete", "叙事与关注度覆盖尚不完整"), _bilingual("No sufficient evaluated forecast sample", "已评估预测样本不足")],
            "invalidation": [_bilingual("Verified evidence materially strengthens or weakens the portfolio thesis", "已验证证据实质性强化或削弱组合论点")],
            "next_trigger": _bilingual("Fresh multi-channel confirmation", "多个通道出现新的同向确认"),
        },
        {
            **common,
            "key": "upside",
            "statement": _bilingual("Upside continuation requires price participation, breadth, liquidity, and company evidence to improve together.", "上行情景需要价格参与度、市场广度、流动性与公司证据同步改善。"),
            "drivers": [_bilingual("Market breadth improves", "市场广度改善"), _bilingual("Holding prices confirm", "持仓价格形成确认"), _bilingual("Announcement evidence strengthens", "公司公告证据增强")],
            "counter_evidence": [_bilingual("Valuation or expectation risk", "估值或预期风险"), _bilingual("Portfolio concentration risk", "组合集中度风险")],
            "invalidation": [_bilingual("Breadth weakens or company evidence contradicts the thesis", "市场广度转弱或公司证据与论点矛盾")],
            "next_trigger": _bilingual("Live breadth and fresh holding evidence", "实时市场广度与持仓新证据同步改善"),
        },
        {
            **common,
            "key": "downside",
            "statement": _bilingual("Downside acceleration becomes relevant if liquidity weakens and portfolio-linked evidence invalidates existing theses.", "若流动性转弱且持仓相关证据使现有论点失效，下行加速情景将变得重要。"),
            "drivers": [_bilingual("Liquidity deterioration", "流动性恶化"), _bilingual("Negative company evidence", "公司负面证据"), _bilingual("Correlated theme pressure", "同主题资产共同承压")],
            "counter_evidence": [_bilingual("Unassigned capital buffer", "未部署资金缓冲"), _bilingual("Existing thesis remains intact", "现有论点仍未被破坏")],
            "invalidation": [_bilingual("Liquidity stabilizes and negative evidence does not persist", "流动性企稳且负面证据未持续")],
            "next_trigger": _bilingual("Verified thesis deterioration", "已验证证据显示论点恶化"),
        },
        {
            **common,
            "key": "range",
            "statement": _bilingual("A range-bound regime remains plausible while directional evidence is incomplete or conflicting.", "当方向性证据不完整或相互冲突时，震荡情景仍然成立。"),
            "drivers": [_bilingual("Mixed channel freshness", "各数据通道新鲜度不一"), _bilingual("Conflicting signals", "信号相互冲突"), _bilingual("Low forecast confidence", "预测置信度较低")],
            "counter_evidence": [_bilingual("Broad multi-channel breakout or breakdown", "多个通道同步突破或转弱")],
            "invalidation": [_bilingual("Participation and liquidity align directionally", "市场参与度与流动性形成同向变化")],
            "next_trigger": _bilingual("Directional breadth and liquidity alignment", "市场广度与流动性形成方向共振"),
        },
    ]
    return {
        "items": scenarios,
        "calibration_supported": calibrated,
        "sample_warning": forecast.get("sample_warning"),
        "channel_context": channels,
    }


def _conditional_action_playbook(
    scenarios: Mapping[str, Any],
    portfolio: Mapping[str, Any],
) -> dict[str, Any]:
    actions = {"base": "Observe", "upside": "Observe", "downside": "Hold", "range": "Hold"}
    rows = []
    for scenario in _list(scenarios.get("items")):
        if not isinstance(scenario, Mapping):
            continue
        key = _text(scenario.get("key"), "base")
        rows.append(
            {
                "scenario": key,
                "trigger": scenario.get("next_trigger"),
                "posture": actions.get(key, "Observe"),
                "affected_holdings": scenario.get("portfolio_sensitivity"),
                "exposure_direction": "unchanged_pending_confirmation",
                "cde_authority": _bilingual("No available authority for this scenario", "本情景无可用资本权限"),
                "limiting_factor": _bilingual("Evidence and CDE authority are incomplete", "证据与 CDE 权限均不完整"),
                "review_time": scenario.get("horizon"),
                "could_change": _list(scenario.get("invalidation")),
            }
        )
    return {
        "items": rows,
        "unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
        "authority_is_permission_not_action": True,
        "no_trading_execution": True,
    }


def _candidate_score_board(
    candidate_pool: Mapping[str, Any],
    market: Mapping[str, Any] | None = None,
    runtime_overlay: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    observations = {
        _text(item.get("asset"), "").upper(): item
        for item in _list(_mapping(market).get("observations"))
        if isinstance(item, Mapping) and item.get("latest_price") is not None
    }
    overlay_assets = _mapping(_mapping(runtime_overlay).get("assets"))
    output = []
    for item in _list(candidate_pool.get("items"))[:8]:
        if not isinstance(item, Mapping):
            continue
        priority = _text(item.get("current_priority"), "B")
        candidate = _text(item.get("asset"), "Data Missing")
        explicit_ticker = _text(item.get("ticker"), "")
        registry_ticker, registry_status = _candidate_registry_identity(candidate)
        parsed_ticker = _ticker_from_candidate_name(candidate)
        ticker = explicit_ticker or registry_ticker or parsed_ticker
        observation = observations.get(ticker.upper(), {}) if ticker else {}
        overlay = _candidate_overlay_for_item(overlay_assets, candidate, ticker)
        confirmation = _bilingual(
            "Not included in this portfolio market refresh.",
            "未纳入本次组合行情刷新。",
        )
        if observation:
            confirmation = _candidate_market_confirmation(observation)
        output.append(
            {
                "code": ticker or "",
                "candidate": candidate,
                "identity_status": "Validated" if explicit_ticker or registry_status == "Validated" else "Needs Validation",
                "source_category": item.get("source_category"),
                "portfolio_overlap": item.get("portfolio_relationship", "Unknown"),
                "thesis_relevance": item.get("thesis_direction", "Unverified"),
                "evidence_quality": item.get("evidence_strength", "Unverified"),
                "market_confirmation": confirmation,
                "valuation_risk": _bilingual("Not assessed", "尚未评估"),
                "strategic_candidate_score": "N/A",
                "tier": priority,
                "score_explanation": _bilingual(
                    "Repository priority is available, but an evidence-backed 0-100 score has not been assigned.",
                    "仓库研究优先级可用，但尚未形成有证据支持的 0-100 分评分。",
                ),
                "cde_authority": _bilingual("Not created by runtime", "运行时尚未生成"),
                "last_reviewed_at": overlay.get("last_reviewed_at"),
                "runtime_assessment": overlay.get("assessment", "NOT_REVIEWED"),
                "runtime_evidence_ids": _list(overlay.get("evidence_ids")),
                "priority_delta": overlay.get("priority_delta", "unchanged"),
                "priority_delta_reason": overlay.get("reason", "no_runtime_overlay"),
            }
        )
    return {
        "items": output,
        "validated_items": [item for item in output if item.get("identity_status") == "Validated"],
        "pending_items": [item for item in output if item.get("identity_status") != "Validated"],
        "score_dimensions": [
            _bilingual("Thesis Fit /20", "论点匹配 /20"),
            _bilingual("Industry Cycle /15", "行业周期 /15"),
            _bilingual("Evidence Quality /15", "证据质量 /15"),
            _bilingual("Market Confirmation /15", "市场确认 /15"),
            _bilingual("Valuation Risk /10", "估值风险 /10"),
            _bilingual("Technical Structure /10", "技术结构 /10"),
            _bilingual("Portfolio Fit /10", "组合匹配 /10"),
            _bilingual("Trigger Readiness /5", "触发就绪 /5"),
        ],
        "research_priority_is_not_trading_authority": True,
        "source": candidate_pool.get("source"),
        "runtime_overlay_updated_at": _mapping(runtime_overlay).get("updated_at"),
        "coverage_note": _bilingual(
            "Market confirmation is shown only when a validated candidate is present in the current runtime market refresh. Numeric candidate scoring and CDE authority remain separate and are not fabricated.",
            "只有已核验候选进入当前运行态行情刷新时才显示市场确认；数值候选评分与 CDE 权限保持分离，不会伪造。",
        ),
    }


def _ticker_from_candidate_name(candidate: str) -> str:
    match = re.search(r"[（(](\d{5,6})[）)]", candidate)
    if not match:
        return ""
    code = match.group(1)
    if len(code) == 5:
        return f"{code}.HK"
    return f"{code}.SH" if code.startswith(("5", "6", "9")) else f"{code}.SZ"


def _candidate_registry_identity(candidate: str) -> tuple[str, str]:
    normalized = re.sub(r"[（(].*?[）)]", "", candidate).strip().lower()
    for item in _ticker_registry():
        aliases = [item.get("name"), *_list(item.get("aliases"))]
        if not any(normalized == _text(alias, "").strip().lower() for alias in aliases):
            continue
        code = _text(item.get("code"), "")
        if not code:
            return "", _text(item.get("identity_status"), "Needs Validation")
        market = _text(item.get("market"), "")
        exchange = _text(item.get("exchange"), "")
        if market == "HK" or exchange == "HKEX":
            ticker = f"{code.zfill(5)}.HK"
        else:
            ticker = f"{code.zfill(6)}.SH" if exchange == "SH" or code.startswith(("5", "6", "9")) else f"{code.zfill(6)}.SZ"
        return ticker, _text(item.get("identity_status"), "Needs Validation")
    return "", "Needs Validation"


@lru_cache(maxsize=1)
def _ticker_registry() -> list[dict[str, Any]]:
    try:
        import yaml

        payload = yaml.safe_load(TICKER_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return []
    items = payload.get("tickers", []) if isinstance(payload, Mapping) else []
    return [dict(item) for item in items if isinstance(item, Mapping)]


def _candidate_market_confirmation(observation: Mapping[str, Any]) -> dict[str, str]:
    daily = observation.get("daily_change_pct")
    change_20d = observation.get("change_20d_pct")
    price = _safe_number(observation.get("latest_price"), 0.0)
    parts = [f"{price:.2f}".rstrip("0").rstrip(".")]
    if daily is not None:
        parts.append(f"1d {float(daily):+.1f}%")
    if change_20d is not None:
        parts.append(f"20d {float(change_20d):+.1f}%")
    summary = " · ".join(parts)
    freshness = _text(observation.get("freshness"), "Unknown")
    freshness_zh = {
        "LIVE": "实时",
        "DELAYED": "延迟",
        "CACHED": "缓存",
    }.get(freshness.upper(), "状态待确认")
    return _bilingual(f"{summary} · {freshness}", f"{summary} · {freshness_zh}")


def build_user_decision_home(
    state: Mapping[str, Any],
    *,
    market_outlook: Mapping[str, Any],
    forecast_accountability: Mapping[str, Any],
    candidate_pool: Mapping[str, Any],
    expert_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    """Project existing evidence into the reduced user-decision Home journey."""

    packet = _mapping(state.get("last_decision_packet"))
    market = _mapping(state.get("market_intelligence"))
    portfolio = _mapping(state.get("portfolio_context"))
    evidence_quality = _home_evidence_quality(market, forecast_accountability)
    core = _decision_core_judgment(state, packet, market, market_outlook, evidence_quality)
    forward = _decision_forward_view(state, packet, market_outlook, evidence_quality)
    portfolio_relevance = _decision_portfolio_relevance(portfolio)
    agenda = _decision_agenda(packet, market, portfolio, evidence_quality)
    triggers = _decision_triggers(market, forecast_accountability)
    research = _decision_research_priorities(candidate_pool, portfolio)
    forecast = _decision_forecast_compact(forecast_accountability)
    hierarchy = _decision_conviction_hierarchy(core, forward, triggers, research)
    return {
        "journey_order": [
            "what_changed",
            "strongest_judgment",
            "portfolio_relevance",
            "decision_agenda",
            "view_change_triggers",
            "research_priorities",
        ],
        "first_viewport_blocks": [
            "core_judgment",
            "strongest_forward_view",
            "portfolio_relevance",
            "decision_agenda",
        ],
        "core_judgment": core,
        "strongest_forward_view": forward,
        "conviction_hierarchy": hierarchy,
        "portfolio_relevance": portfolio_relevance,
        "decision_agenda": agenda,
        "decision_triggers": triggers,
        "research_priorities": research,
        "forecast_accountability": forecast,
        "expert_analysis": {
            "collapsed_by_default": True,
            "section_count": expert_analysis.get("section_count", 0),
        },
        "source_boundaries": {
            "presentation_only": True,
            "read_only": True,
            "no_cognition_semantics_change": True,
            "no_forecast_semantics_change": True,
            "no_candidate_semantics_change": True,
            "no_trading_execution": True,
        },
    }


def build_candidate_pool(
    *,
    portfolio_context: Mapping[str, Any] | None = None,
    source_path: Path | str = CANDIDATE_SOURCE_PATH,
) -> dict[str, Any]:
    """Parse the existing repository candidate pool into a safe UI view."""

    source = Path(source_path)
    if not source.exists():
        return {
            "status": "absent",
            "source": str(source),
            "items": [],
            "changes": [],
            "filters": {},
            "absence_reason": "candidate source file not found",
            "candidate_ranking_not_buy_recommendation": True,
        }
    text = source.read_text(encoding="utf-8")
    portfolio = _portfolio_needles(portfolio_context or {})
    items: list[dict[str, Any]] = []
    items.extend(_parse_priority_table(text, "Priority S", "S", portfolio, source))
    items.extend(_parse_priority_table(text, "Priority A", "A", portfolio, source))
    items.extend(_parse_watch_pool(text, portfolio, source))
    items = [_sanitize_candidate(item) for item in items]
    items = [item for item in items if item.get("asset")]
    changes = _candidate_changes(items)
    return {
        "status": "available" if items else "empty",
        "source": str(source),
        "items": items,
        "top_items": items[:5],
        "changes": changes,
        "filters": {
            "all": len(items),
            "portfolio_related": sum(1 for item in items if item.get("portfolio_relationship") != "None"),
            "high_priority": sum(1 for item in items if item.get("current_priority") in {"S", "A"}),
            "new": sum(1 for item in changes if item.get("change_type") == "entered_candidate_pool"),
            "changed_recently": len(changes),
        },
        "candidate_ranking_not_buy_recommendation": True,
        "no_trading_execution": True,
    }


def build_market_outlook(state: Mapping[str, Any], ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Create a current forward view from existing state and ledger evidence."""

    ledger = _mapping(ledger)
    forecasts = _list(ledger.get("forecasts"))
    latest = _mapping(forecasts[0]) if forecasts else {}
    packet = _mapping(state.get("last_decision_packet"))
    regime = _text(state.get("regime_state") or packet.get("regime_state"), "Unknown")
    confidence = latest.get("confidence")
    if confidence is None:
        confidence = packet.get("confidence", 0.0)
    expected_state = _text(latest.get("expected_direction_state") or regime, "Unknown")
    statement = _text(latest.get("forecast_statement"), "")
    base_case = statement if statement else f"Current runtime state remains anchored around {expected_state} until contradicted."
    if not latest and regime.lower() == "unknown":
        base_case = "Insufficient evidence to form a forward view."
    invalidations = _list(latest.get("invalidation_conditions"))
    if not invalidations:
        invalidations = _default_invalidations(state)
    return {
        "status": "available" if latest or regime.lower() != "unknown" else "insufficient_evidence",
        "source": "forecast_ledger + current_runtime_state" if latest else "current_runtime_state",
        "base_case": base_case,
        "base_state": expected_state,
        "upside_scenario": _scenario_text(expected_state, "upside"),
        "downside_scenario": _scenario_text(expected_state, "downside"),
        "horizon": _text(latest.get("horizon"), "insufficient evidence"),
        "confidence": _safe_confidence(confidence),
        "invalidation_conditions": invalidations[:5],
        "distinct_from_forecast_ledger": True,
        "latest_forecast_id": latest.get("forecast_id"),
    }


def _decision_core_judgment(
    state: Mapping[str, Any],
    packet: Mapping[str, Any],
    market: Mapping[str, Any],
    outlook: Mapping[str, Any],
    evidence_quality: Mapping[str, Any],
) -> dict[str, Any]:
    regime = _text(state.get("regime_state") or packet.get("regime_state"), "Unknown")
    confidence = _safe_confidence(packet.get("confidence", outlook.get("confidence", 0.0)))
    observations = [_mapping(item) for item in _list(market.get("observations")) if isinstance(item, Mapping)]
    available = [item for item in observations if _text(item.get("data_quality_status"), "").lower() in {"available", "partial"}]
    breakouts = [item for item in available if _text(item.get("normalized_event_type"), "") == "price_breakout"]
    decision_fallback = _decision_packet_is_fallback(packet)
    if regime.upper() == "RISK_OFF" and breakouts:
        title = _bilingual(
            "Portfolio-linked prices are moving, but Atlas still treats the setup as risk-constrained.",
            "组合相关价格在移动，但 Atlas 仍将当前环境视为风险约束状态。",
        )
        explanation = _bilingual(
            "Price strength needs breadth, liquidity, and valid reasoning confirmation before it becomes an expansion signal.",
            "价格强势需要市场广度、流动性和有效推理共同确认，才会升级为扩张信号。",
        )
        changed = _bilingual(
            f"{len(breakouts)} portfolio-relevant price observations refreshed; several macro/news/breadth channels remain unconfigured.",
            f"{len(breakouts)} 个组合相关价格观测已刷新，但宏观、新闻、市场广度等通道仍未配置。",
        )
    elif regime.upper() == "RISK_OFF":
        title = _bilingual(
            "Risk constraint is active; Atlas has not confirmed a directional expansion signal.",
            "风险约束仍在，Atlas 尚未确认方向性扩张信号。",
        )
        explanation = _bilingual(
            "The current state favors observation until liquidity and breadth improve.",
            "当前更适合观察，等待流动性和市场广度改善。",
        )
        changed = _bilingual(
            "Runtime state refreshed into RISK_OFF while evidence quality remains partial.",
            "运行状态刷新为 RISK_OFF，但证据质量仍然只是部分充分。",
        )
    elif regime.upper() in {"ATTENTION_EXPANSION", "BREAKOUT"}:
        title = _bilingual(
            "Attention is expanding, but Atlas still requires confirmation before risk expansion.",
            "注意力正在扩张，但 Atlas 仍需要确认后才会提升风险暴露判断。",
        )
        explanation = _bilingual(
            "The useful signal is participation quality, not the regime label alone.",
            "真正有用的信号是参与质量，而不是单独的状态标签。",
        )
        changed = _bilingual(
            f"Runtime state refreshed into {regime.replace('_', ' ')}.",
            f"市场状态刷新为「{localize_regime(regime, 'zh')}」。",
        )
    else:
        title = _bilingual(
            "Atlas does not yet have enough signal for a high-confidence market judgment.",
            "Atlas 目前还没有足够信号形成高置信市场判断。",
        )
        explanation = _bilingual(
            "Use portfolio relevance and freshness checks first; avoid treating unknown state as a trade signal.",
            "先看组合相关性和数据新鲜度，不要把未知状态当成交易信号。",
        )
        changed = _bilingual(
            "Runtime refreshed, but the latest cognitive packet is still low-confidence.",
            "运行状态已刷新，但最新认知包仍是低置信。",
        )
    if decision_fallback:
        explanation = _bilingual(
            "The DecisionPacket fell back to neutral/observe because LLM reasoning was unavailable or invalid; Atlas should rely on evidence checks before changing posture.",
            "由于 LLM 推理不可用或无效，决策结论回退到中性/观察；Atlas 需要先依赖证据校验，再考虑改变姿态。",
        )
    return {
        "question": "what_changed",
        "title": title,
        "what_changed": changed,
        "explanation": explanation,
        "confidence": confidence,
        "confidence_text": _confidence_text(confidence),
        "evidence_quality": evidence_quality,
        "updated_at": _text(state.get("timestamp") or market.get("timestamp"), "Unknown"),
    }


def _decision_forward_view(
    state: Mapping[str, Any],
    packet: Mapping[str, Any],
    outlook: Mapping[str, Any],
    evidence_quality: Mapping[str, Any],
) -> dict[str, Any]:
    regime = _text(outlook.get("base_state") or state.get("regime_state"), "Unknown")
    confidence = _safe_confidence(outlook.get("confidence", packet.get("confidence", 0.0)))
    horizon = _text(outlook.get("horizon"), "next_runtime_cycle")
    low_evidence = confidence < 0.2 or evidence_quality.get("status") in {"limited", "insufficient"}
    if low_evidence:
        statement = _bilingual(
            "Current evidence is not enough for a high-conviction forecast; the strongest structural view is to observe risk constraints until breadth and liquidity confirm.",
            "当前没有足够证据形成高强度预测；最强结构判断是继续观察风险约束，直到市场广度和流动性确认。",
        )
        falsification = _bilingual(
            "Breadth and liquidity turn live/positive while the next runtime cycle no longer conflicts with the expected structure.",
            "市场广度和流动性转为实时/正向，且下一运行周期不再与预期结构冲突。",
        )
        evidence_note = _bilingual(
            "Partial evidence: latest forecast confidence is low and several channels are not configured.",
            "证据部分充分：最新预测置信度较低，且多个通道尚未配置。",
        )
    elif regime.upper() == "RISK_OFF":
        statement = _bilingual(
            "Risk constraints likely remain the working structure over the next runtime cycle unless liquidity and breadth repair.",
            "除非流动性和市场广度修复，否则风险约束大概率仍是下一运行周期的工作结构。",
        )
        falsification = _bilingual(
            "Risk-sensitive channels improve together and the forecast outcome does not invalidate the structure.",
            "风险敏感通道同步改善，且预测结果没有使该结构失效。",
        )
        evidence_note = _bilingual("Supported by current regime plus latest open forecast.", "由当前状态和最新未完成预测支持。")
    else:
        statement = _bilingual(
            f"{regime.replace('_', ' ')} remains the working forward structure until contradicted by later observed state.",
            f"「{localize_regime(regime, 'zh')}」仍是当前前瞻工作结构，除非后续观测状态与之冲突。",
        )
        falsification = _bilingual(
            "Later runtime state conflicts with the expected structure or a supported forecast lifecycle invalidates it.",
            "后续运行状态与预期结构冲突，或受支持的预测生命周期将其标记为失效。",
        )
        evidence_note = _bilingual("Evidence is directional, not trading authority.", "证据只代表方向性判断，不构成交易权限。")
    return {
        "question": "strongest_judgment",
        "statement": statement,
        "horizon": horizon,
        "confidence": confidence,
        "confidence_text": _confidence_text(confidence),
        "evidence_quality": evidence_quality,
        "evidence_note": evidence_note,
        "falsification_condition": falsification,
        "source": outlook.get("source"),
        "latest_forecast_id": outlook.get("latest_forecast_id"),
    }


def _decision_conviction_hierarchy(
    core: Mapping[str, Any],
    forward: Mapping[str, Any],
    triggers: Mapping[str, Any],
    research: Mapping[str, Any],
) -> dict[str, Any]:
    level2 = [
        {
            "statement": forward.get("statement"),
            "confidence": forward.get("confidence"),
            "horizon": forward.get("horizon"),
        }
    ]
    negative = _list(triggers.get("negative_confirmation"))
    positive = _list(triggers.get("positive_confirmation"))
    if positive:
        level2.append({"statement": _bilingual("Confirmation improves if breadth/liquidity repair.", "若市场广度/流动性修复，确认度会提升。"), "confidence": forward.get("confidence"), "horizon": "next_runtime_cycle"})
    if negative:
        level2.append({"statement": _bilingual("Risk worsens if liquidity, data freshness, or forecast outcomes deteriorate.", "若流动性、数据新鲜度或预测结果恶化，风险会升高。"), "confidence": forward.get("confidence"), "horizon": "next_runtime_cycle"})
    return {
        "level_1": [{"label": "Core Judgment", "item": core.get("title")}],
        "level_2": level2[:3],
        "level_3": positive[:3] + negative[:3],
        "level_4": {
            "surface": "research_candidates",
            "count_on_home": len(_list(research.get("items"))),
            "full_pool_link": research.get("full_pool_link"),
        },
        "presentation_only": True,
    }


def _decision_portfolio_relevance(portfolio: Mapping[str, Any]) -> dict[str, Any]:
    exposure_map = _mapping(portfolio.get("exposure_map"))
    holdings = [_mapping(item) for item in _list(exposure_map.get("asset_concentration")) if isinstance(item, Mapping)]
    clusters = [_mapping(item) for item in _list(exposure_map.get("correlated_risk_clusters")) if isinstance(item, Mapping)]
    relevance = _safe_number(exposure_map.get("portfolio_relevance_score"), 0.0)
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    sensitive = holdings[0] if holdings else {}
    shared = clusters[0] if clusters else {}
    if relevance >= 60:
        impact = _bilingual("Medium-high portfolio relevance", "组合相关性中高")
    elif relevance >= 35:
        impact = _bilingual("Medium portfolio relevance", "组合相关性中等")
    elif relevance > 0:
        impact = _bilingual("Low portfolio relevance", "组合相关性较低")
    else:
        impact = _bilingual("Portfolio relevance unavailable", "组合相关性不可用")
    return {
        "question": "portfolio_relevance",
        "overall_impact": impact,
        "primary_shared_risk": _bilingual(
            str(shared.get("cluster") or exposure_map.get("regime_sensitivity") or "theme concentration"),
            str(shared.get("cluster") or "主题集中风险"),
        ),
        "most_sensitive_holding": {
            "asset": _text(sensitive.get("asset"), "Unknown"),
            "exposure_pct": sensitive.get("exposure_pct"),
        },
        "strongest_buffer": _bilingual(
            f"{buffer_pct:.1f}% unassigned buffer" if buffer_pct else "No explicit buffer available",
            f"{buffer_pct:.1f}% 未部署缓冲" if buffer_pct else "没有明确缓冲",
        ),
        "explanation": _bilingual(
            "The portfolio is concentrated in semiconductor materials and PCB / AI hardware themes, so liquidity and theme confirmation matter more than generic index direction.",
            "组合集中在半导体材料与 PCB / AI 硬件主题，因此流动性和主题确认比单纯指数方向更重要。",
        ),
        "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
    }


def _decision_agenda(
    packet: Mapping[str, Any],
    market: Mapping[str, Any],
    portfolio: Mapping[str, Any],
    evidence_quality: Mapping[str, Any],
) -> dict[str, Any]:
    raw_action = _text(packet.get("recommended_action"), "observe").lower()
    posture = raw_action if raw_action in {"observe", "hold", "reduce", "build", "accumulate"} else "observe"
    focus_items = [
        _bilingual("Confirm whether market breadth improves beyond portfolio-linked price strength.", "确认市场广度是否跟上组合相关价格强势。"),
        _bilingual("Check whether liquidity pressure falls or remains only simulated/partial.", "检查流动性压力是否下降，还是仍停留在模拟/部分证据。"),
        _bilingual("Refresh holding-specific evidence for the most sensitive position.", "刷新最敏感持仓的个股证据。"),
    ]
    if evidence_quality.get("status") == "insufficient":
        focus_items[0] = _bilingual("Restore live data channels before upgrading conviction.", "先恢复实时数据通道，再提升判断强度。")
    sensitive = _mapping(_mapping(portfolio.get("exposure_map")).get("asset_concentration")[0]) if _list(_mapping(portfolio.get("exposure_map")).get("asset_concentration")) else {}
    if sensitive.get("asset"):
        focus_items[2] = _bilingual(
            f"Refresh holding-specific evidence for {sensitive.get('asset')}.",
            f"刷新 {sensitive.get('asset')} 的持仓相关证据。",
        )
    return {
        "question": "decision_agenda",
        "posture": posture,
        "posture_label": _action_label(posture),
        "explanation": _bilingual(
            "This is a decision agenda, not trade execution. Current evidence supports observation before increasing risk.",
            "这是决策议程，不是交易执行。当前证据支持先观察，再考虑是否提高风险暴露。",
        ),
        "focus_items": focus_items[:3],
        "raw_decision_packet_action": raw_action,
        "no_trading_execution": True,
    }


def _decision_triggers(market: Mapping[str, Any], forecast: Mapping[str, Any]) -> dict[str, Any]:
    channels = _mapping(market.get("channels"))
    counts = _mapping(forecast.get("counts"))
    positive = [
        _bilingual("Market breadth channel becomes configured/live and confirms participation.", "市场广度通道完成配置/转为实时，并确认参与度改善。"),
        _bilingual("Liquidity proxy improves without relying only on simulated evidence.", "流动性代理改善，且不只依赖模拟证据。"),
        _bilingual("Portfolio-linked strength is confirmed by fresh price/volume observations.", "组合相关强势得到新鲜价量观测确认。"),
    ]
    negative = [
        _bilingual("Liquidity or volatility channels deteriorate together.", "流动性或波动率通道同步恶化。"),
        _bilingual("Price/volume freshness fails or portfolio-relevant observations become stale.", "价量新鲜度失效，或组合相关观测变为过期。"),
        _bilingual("A high-confidence forecast is invalidated through the supported lifecycle.", "高置信预测在受支持生命周期中被验证为失效。"),
    ]
    if not channels:
        positive[0] = _bilingual("At least one live market data channel becomes available.", "至少一个实时市场数据通道可用。")
    if not counts.get("invalidated"):
        negative[2] = _bilingual("Any forecast miss appears after maturity and changes calibration pressure.", "预测到期后出现失误，并改变校准压力。")
    return {
        "question": "view_change_triggers",
        "positive_confirmation": positive[:3],
        "negative_confirmation": negative[:3],
    }


def _decision_research_priorities(candidate_pool: Mapping[str, Any], portfolio: Mapping[str, Any]) -> dict[str, Any]:
    positions = [_mapping(item) for item in _list(portfolio.get("positions")) if isinstance(item, Mapping)]
    candidates = [_mapping(item) for item in _list(candidate_pool.get("items")) if isinstance(item, Mapping)]
    used_assets: set[str] = set()
    priorities: list[dict[str, Any]] = []
    for position in sorted(positions, key=lambda item: _safe_number(item.get("portfolio_percentage"), 0.0), reverse=True):
        match = _match_position_candidate(position, candidates)
        item = match or {}
        asset = _text(item.get("asset") or position.get("asset"), "Unknown")
        if asset in used_assets:
            continue
        used_assets.add(asset)
        priorities.append(
            {
                "asset": asset,
                "theme": _text(item.get("theme") or position.get("theme"), "Unknown"),
                "why_now": _bilingual(
                    f"{position.get('portfolio_percentage', 'Unknown')}% portfolio exposure makes this the first evidence-refresh priority.",
                    f"{position.get('portfolio_percentage', '未知')}% 组合暴露使其成为第一批证据刷新重点。",
                ),
                "evidence_change": _bilingual(
                    _text(item.get("next_trigger") or position.get("risk_note"), "Refresh order, margin, valuation, and liquidity evidence."),
                    _text(item.get("next_trigger") or position.get("risk_note"), "刷新订单、利润率、估值和流动性证据。"),
                ),
                "portfolio_relationship": "Direct current portfolio exposure",
                "truth_label": "Portfolio-Relevant" if match else "Portfolio-Relevant / Not in Static Research Pool",
                "source": item.get("source") or portfolio.get("source"),
            }
        )
        if len(priorities) >= 3:
            break
    if len(priorities) < 3:
        for item in candidates:
            asset = _text(item.get("asset"), "")
            if not asset or asset in used_assets:
                continue
            priorities.append(
                {
                    "asset": asset,
                    "theme": _text(item.get("theme"), "Unknown"),
                    "why_now": _bilingual(
                        _text(item.get("reason"), "Repository priority requires evidence refresh."),
                        _text(item.get("reason"), "仓库优先级需要证据刷新。"),
                    ),
                    "evidence_change": _bilingual(
                        _text(item.get("next_trigger"), "No new runtime evidence; review trigger is repository-defined."),
                        _text(item.get("next_trigger"), "没有新的运行态证据；复核触发来自仓库。"),
                    ),
                    "portfolio_relationship": _text(item.get("portfolio_relationship"), "None"),
                    "truth_label": "Static Research Pool",
                    "source": item.get("source"),
                }
            )
            if len(priorities) >= 3:
                break
    return {
        "question": "research_priorities",
        "items": priorities[:3],
        "full_pool_link": "/candidates",
        "candidate_priority_truth": {
            "source": candidate_pool.get("source"),
            "classification": "Static Research Pool + presentation-only current portfolio relevance overlay",
            "not_claimed": [
                "dynamic runtime ranking",
                "trading recommendation",
                "evidence-aware ranking unless evidence change is explicitly shown",
            ],
        },
    }


def _decision_forecast_compact(forecast: Mapping[str, Any]) -> dict[str, Any]:
    counts = _mapping(forecast.get("counts"))
    recent_miss = _mapping(forecast.get("recent_miss"))
    if recent_miss:
        miss_summary = _bilingual(
            _text(recent_miss.get("forecast_statement") or recent_miss.get("expected_direction_state"), "Recent miss recorded."),
            _text(recent_miss.get("forecast_statement") or recent_miss.get("expected_direction_state"), "已记录近期预测失误。"),
        )
        changed = _bilingual(
            "Atlas exposes the miss through Forecast Ledger; later calibration effects must be verified through runtime behavior.",
            "Atlas 已通过预测账本暴露该失误；后续校准影响必须通过运行态行为验证。",
        )
    else:
        miss_summary = _bilingual(
            "No evaluated miss is available yet.",
            "当前还没有已评估的预测失误。",
        )
        changed = _bilingual(
            "No behavior-change claim is made until a miss matures and is evaluated.",
            "在预测到期并完成评估前，不宣称 Atlas 已因此改变行为。",
        )
    return {
        "counts": {
            "open": counts.get("open", 0),
            "current_open": counts.get("current_open", counts.get("open", 0)),
            "legacy_open": counts.get("legacy_open", 0),
            "matured": counts.get("matured", 0),
            "verified": counts.get("verified", 0),
            "invalidated": counts.get("invalidated", 0),
            "inconclusive": counts.get("inconclusive", 0),
        },
        "metrics": {
            "total": forecast.get("metrics", {}).get("total", 0),
            "open": forecast.get("metrics", {}).get("open", 0),
            "matured": forecast.get("metrics", {}).get("matured", 0),
            "evaluated": forecast.get("metrics", {}).get("evaluated", 0),
            "verified": forecast.get("metrics", {}).get("verified", 0),
            "invalidated": forecast.get("metrics", {}).get("invalidated", 0),
            "inconclusive": forecast.get("metrics", {}).get("inconclusive", 0),
            "accuracy": forecast.get("metrics", {}).get("accuracy"),
            "minimum_sample_size_met": forecast.get("metrics", {}).get("minimum_sample_size_met", False),
        },
        "recent_miss": miss_summary,
        "what_changed_afterward": changed,
        "sample_warning": forecast.get("sample_warning"),
        "legacy_policy": forecast.get("legacy_policy"),
        "links": {"predictions": "/predictions", "learning": "/learning"},
    }


def _action_today(packet: Mapping[str, Any], market: Mapping[str, Any], portfolio: Mapping[str, Any]) -> dict[str, Any]:
    confidence = _safe_confidence(packet.get("confidence", 0.0))
    channels = _mapping(market.get("channels"))
    live_count = sum(1 for value in channels.values() if _text(value, "").upper() == "LIVE")
    missing_count = sum(1 for value in channels.values() if _text(value, "").upper() in {"NOT_CONFIGURED", "FAILED"})
    observations = _usable_market_observations(market)
    configured = _text(portfolio.get("status"), "").lower() == "configured"
    raw_action = _text(packet.get("recommended_action"), "neutral").lower()
    risk_level = _text(packet.get("risk_level"), "unknown").lower()
    fallback = _decision_packet_is_fallback(packet)
    posture = raw_action if raw_action in {"observe", "reduce"} else "observe"
    if raw_action == "reduce" or risk_level in {"high", "severe"}:
        status = "YES"
        reason = _bilingual(
            f"The validated DecisionPacket requires a risk review: Atlas posture is Reduce and risk is {risk_level}. No order is generated.",
            f"最新有效决策结论要求进行风险复核：Atlas 姿态为降低暴露，风险等级为{localized_risk(risk_level, 'zh')['primary']}。系统不会生成订单。",
        )
    elif fallback:
        status = "CONDITIONAL"
        reason = _bilingual(
            "The latest reasoning result is unavailable or failsafe. Atlas preserves the previous valid posture and requires review before any change.",
            "最新推理结果不可用或处于故障保护状态。Atlas 保留上一有效姿态，任何变化前都需要复核。",
        )
    elif configured and observations and missing_count:
        status = "CONDITIONAL"
        reason = _bilingual(
            "Portfolio-linked price data is live, but breadth/news/macro channels remain incomplete; review is justified, execution is not.",
            "组合相关价量数据已更新，但市场广度、新闻、宏观等通道仍不完整；需要复核，不支持执行。",
        )
    elif confidence >= 0.65 and live_count >= 3 and observations:
        status = "YES"
        reason = _bilingual(
            "Evidence quality is strong enough to justify a portfolio decision review.",
            "证据质量足以支持进入组合决策复核。",
        )
    else:
        status = "NO"
        reason = (
            _bilingual(
                "Portfolio market observations are unavailable; keep the brief in observation mode until real evidence is restored.",
                "组合相关市场观测当前不可用；在真实证据恢复前，简报保持观察模式。",
            )
            if configured and not observations
            else _bilingual(
                "Current evidence does not justify new portfolio action; keep the brief in observation mode.",
                "当前证据不足以支持新增组合动作，简报保持观察模式。",
            )
        )
    return {
        "status": status,
        "posture": posture,
        "posture_label": _action_label(posture),
        "decision_packet_action": raw_action,
        "risk_level": risk_level,
        "regime_state": _text(packet.get("regime_state"), "Unknown").split("/")[0].strip(),
        "reason": reason,
        "helper": _bilingual(
            "YES / NO / CONDITIONAL means whether evidence justifies decision review today, not an order.",
            "这里判断的是今天是否值得进入决策复核，不代表交易指令。",
        ),
        "confidence": confidence,
        "execution_status": "USER_CONFIRMATION_REQUIRED",
        "no_trading_execution": True,
    }


def _practical_core_judgment(
    packet: Mapping[str, Any],
    market: Mapping[str, Any],
    portfolio: Mapping[str, Any],
    capital_relay: Mapping[str, Any],
    evidence_assessment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    regime = _text(packet.get("regime_state"), "Unknown").split("/")[0].strip()
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    observations = _usable_market_observations(market)
    assessment = _mapping(evidence_assessment)
    summary = _mapping(assessment.get("summary"))
    reviewed = int(_safe_number(summary.get("reviewed_count"), 0.0))
    changed = int(_safe_number(summary.get("CHANGED"), 0.0))
    unchanged = int(_safe_number(summary.get("UNCHANGED"), 0.0))
    needs_review = int(_safe_number(summary.get("NEEDS_REVIEW"), 0.0))
    action = _text(packet.get("recommended_action"), "neutral").lower()
    risk = _text(packet.get("risk_level"), "unknown").lower()
    confidence = _safe_confidence(packet.get("confidence"))
    if _decision_packet_is_fallback(packet):
        headline = _bilingual(
            "Latest reasoning is unavailable; preserve the previous valid view and review new evidence.",
            "最新推理不可用；保留上一有效判断，并复核新增证据。",
        )
    elif action == "reduce" or risk in {"high", "severe"}:
        headline = _bilingual(
            f"Risk is {risk}; Atlas posture is Reduce and a portfolio risk review is required.",
            f"当前风险等级为{localized_risk(risk, 'zh')['primary']}；Atlas 姿态为降低暴露，需要进行组合风险复核。",
        )
    elif changed:
        headline = _bilingual(
            f"{changed} reviewed evidence item(s) changed the working interpretation; reassess the portfolio before changing exposure.",
            f"有 {changed} 条已复核证据改变了当前工作判断；调整暴露前应重新评估组合。",
        )
    elif reviewed and unchanged:
        headline = _bilingual(
            f"Atlas reviewed {reviewed} item(s); the working thesis remains unchanged.",
            f"Atlas 已复核 {reviewed} 条信息；当前工作论点没有变化。",
        )
    elif needs_review:
        headline = _bilingual(
            f"{needs_review} relevant item(s) still need research review; no thesis change is claimed.",
            f"仍有 {needs_review} 条相关信息需要研究复核；当前不主张论点发生变化。",
        )
    else:
        headline = _bilingual(
            "No validated thesis change is available; keep the current posture until material evidence arrives.",
            "当前没有已验证的论点变化；在重要证据出现前保持现有姿态。",
        )
    support = _bilingual(
        f"Market state is {localize_regime(regime, 'en') if regime else 'Unknown'} with {len(observations)} usable portfolio-linked observations. Decision confidence is {confidence:.0%}; causal summary: {_text(packet.get('causal_summary'), 'Unknown')}. Unassigned buffer is {buffer_pct:.1f}%.",
        f"当前市场状态为「{localize_regime(regime, 'zh') if regime else '未知'}」，有 {len(observations)} 个可用的组合相关观测。决策置信度为 {confidence:.0%}；因果摘要：{localize_inline_tokens(_text(packet.get('causal_summary'), '未知'), 'zh')}。未部署资金为 {buffer_pct:.1f}%。",
    )
    if not observations:
        support = _bilingual(
            f"Portfolio market observations are unavailable. The {localize_regime(regime, 'en') if regime else 'Unknown'} market state and Capital Relay are inference/framework context only, so today's judgment remains observation-first; unassigned buffer is {buffer_pct:.1f}%.",
            f"组合相关市场观测当前不可用。「{localize_regime(regime, 'zh') if regime else '未知'}」市场状态与资本接力仅属于推断/框架上下文，因此今日判断保持观察优先；未部署资金为 {buffer_pct:.1f}%。",
        )
    return {
        "headline": headline,
        "supporting_sentence": support,
        "source": "DecisionPacket + market_intelligence + portfolio_context + Capital Relay snapshot",
        "relay_stage": capital_relay.get("current_stage"),
        "because_bullets": [
            _bilingual(
                f"DecisionPacket posture: {_action_label(action if action in {'observe', 'reduce'} else 'observe')['en']}; risk: {risk}; confidence: {confidence:.0%}.",
                f"决策结论姿态：{_action_label(action if action in {'observe', 'reduce'} else 'observe')['zh']}；风险：{localized_risk(risk, 'zh')['primary']}；置信度：{confidence:.0%}。",
            ),
            _bilingual(
                f"Evidence review: {reviewed} reviewed, {changed} changed, {unchanged} unchanged, {needs_review} pending review.",
                f"证据复核：已复核 {reviewed} 条，改变判断 {changed} 条，结论不变 {unchanged} 条，待复核 {needs_review} 条。",
            ),
            _bilingual(
                f"Portfolio-linked market observations: {len(observations)} usable; unassigned buffer: {buffer_pct:.1f}%.",
                f"组合相关市场观测：{len(observations)} 个可用；未部署缓冲：{buffer_pct:.1f}%。",
            ),
        ],
    }


def _observation_evidence_id(observation: Mapping[str, Any]) -> str:
    return "observation:{asset}:{timestamp}".format(
        asset=_text(observation.get("asset"), "Unknown"),
        timestamp=_text(observation.get("timestamp"), "Unknown"),
    )


def _candidate_overlay_for_item(
    overlay_assets: Mapping[str, Any],
    candidate: str,
    ticker: str,
) -> dict[str, Any]:
    normalized = {str(key).strip().lower(): value for key, value in overlay_assets.items()}
    candidates = [candidate, ticker, re.sub(r"[（(].*?[）)]", "", candidate).strip()]
    for key in candidates:
        value = normalized.get(str(key).strip().lower())
        if isinstance(value, Mapping):
            return dict(value)
    return {}


def _strongest_predictions(ledger: Mapping[str, Any], packet: Mapping[str, Any], market: Mapping[str, Any]) -> dict[str, Any]:
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    predictions: list[dict[str, Any]] = []
    latest = forecasts[0] if forecasts else {}
    confidence = _safe_confidence(latest.get("confidence", packet.get("confidence", 0.0)))
    if latest:
        evidence = _list(latest.get("causal_drivers"))
        if _usable_market_observations(market):
            evidence.append("usable_portfolio_market_observations")
        predictions.append(
            {
                "judgment": _bilingual(
                    _text(
                        latest.get("forecast_statement"),
                        "Current causal structure remains coherent until contradicted by later observed state.",
                    ),
                    "当前因果结构仍可作为工作假设，但必须等待后续观测验证。",
                ),
                "quality_label": _bilingual(
                    "Strongest available runtime forecast; low conviction, not a high-conviction call.",
                    "当前最强可追踪运行态预测；低置信，不是高强度判断。",
                ),
                "confidence": confidence,
                "confidence_text": _confidence_text(confidence),
                "horizon": _text(latest.get("horizon"), "next_runtime_cycle"),
                "evidence": evidence[:4] or ["forecast_ledger_runtime_lineage"],
                "invalidation": _list(latest.get("invalidation_conditions"))[:3]
                or ["later_runtime_state_conflicts_with_expected_structure"],
                "source": "forecast_ledger",
                "forecast_id": latest.get("forecast_id"),
            }
        )
    return {
        "items": predictions[:3],
        "empty_message": _bilingual(
            "No high-conviction prediction has enough evidence yet.",
            "当前没有足够证据形成高强度预测。",
        ),
        "max_items": 3,
    }


def _bottleneck_index(source_path: Path = BOTTLENECK_MAP_PATH) -> dict[str, Any]:
    rows = _read_first_table(source_path)
    domains = []
    required = {"Memory", "Equipment", "Materials", "Bandwidth", "Power"}
    for row in rows:
        if len(row) < 3 or row[0] == "Bottleneck":
            continue
        domain = row[0]
        domains.append(
            {
                "domain": domain,
                "strength": row[1],
                "trend": _bottleneck_trend(domain),
                "key_change": row[2],
                "required_domain": domain in required,
            }
        )
    return {
        "status": "available" if domains else "absent",
        "source": str(source_path),
        "source_type": "manual_current_ranking_snapshot",
        "domains": domains,
        "honest_label": _bilingual(
            "Manual current-state snapshot, not runtime-derived scoring.",
            "手动维护的当前状态快照，不是运行态自动评分。",
        ),
    }


def _capital_relay(
    relay_path: Path = CAPITAL_RELAY_PATH,
    map_path: Path = AI_CAPITAL_MAP_PATH,
) -> dict[str, Any]:
    relay_text = relay_path.read_text(encoding="utf-8") if relay_path.exists() else ""
    map_text = map_path.read_text(encoding="utf-8") if map_path.exists() else ""
    path = [
        {"name": "Memory", "state": "strengthening", "state_zh": "强化", "evidence_type": "INFERRED"},
        {"name": "PCB / CCL", "state": "leading", "state_zh": "主导", "evidence_type": "INFERRED"},
        {"name": "Equipment", "state": "relay", "state_zh": "接力", "evidence_type": "INFERRED"},
        {"name": "Materials", "state": "emerging", "state_zh": "启动", "evidence_type": "INFERRED"},
        {"name": "Bandwidth", "state": "upgraded", "state_zh": "升级", "evidence_type": "HYPOTHESIZED"},
    ]
    return {
        "status": "available" if relay_text or map_text else "unconfirmed",
        "source": [str(relay_path), str(map_path)],
        "source_type": "framework_snapshot",
        "current_stage": _bilingual(
            "Memory strengthening -> Equipment relay -> Materials starting.",
            "Memory 强化 → Equipment 接力 → Materials 启动。",
        ),
        "path": path,
        "distinction": _bilingual(
            "Capital relay is inferred from Atlas framework snapshots; portfolio price observations are observed separately.",
            "资本迁移来自 Atlas 框架快照推断；组合价量观测另行标记为已观测。",
        ),
    }


def _current_holdings_board(
    portfolio: Mapping[str, Any],
    market: Mapping[str, Any],
    local_valuation: Mapping[str, Any] | None = None,
    packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    observations = {
        _text(_mapping(item).get("asset"), ""): _mapping(item)
        for item in _usable_market_observations(market)
        if isinstance(item, Mapping)
    }
    holdings = []
    valuation = _mapping(local_valuation)
    decision_packet = _mapping(packet)
    raw_action = _text(decision_packet.get("recommended_action"), "neutral").lower()
    global_posture = raw_action if raw_action in {"observe", "reduce"} else "observe"
    valuation_by_asset = {
        _text(_mapping(item).get("asset"), ""): _mapping(item)
        for item in _list(valuation.get("positions"))
        if isinstance(item, Mapping)
    }
    for item in _list(portfolio.get("positions")):
        if not isinstance(item, Mapping):
            continue
        asset = _text(item.get("asset"), "Unknown")
        observation = observations.get(asset, {})
        trigger = _text(item.get("risk_note"), "Refresh thesis, price/volume, and liquidity evidence.")
        changes = []
        if observation:
            if observation.get("change_5d_pct") is not None:
                changes.append(f"5d {float(observation['change_5d_pct']):.1f}%")
            if observation.get("change_20d_pct") is not None:
                changes.append(f"20d {float(observation['change_20d_pct']):.1f}%")
            trigger = "; ".join(changes) if changes else "Multi-day change data missing"
        holdings.append(
            {
                "asset": asset,
                "theme": _text(item.get("theme"), "Unknown"),
                "exposure_pct": item.get("portfolio_percentage"),
                "posture": global_posture,
                "posture_label": _action_label(global_posture),
                "posture_scope": "portfolio_level_decision_packet",
                "why": _bilingual(
                    _text(item.get("user_thesis"), "Configured holding requires evidence refresh."),
                    f"该持仓属于 {_text(item.get('theme'), '未分类主题')}，需要结合公司、行业与市场证据持续复核。",
                ),
                "key_trigger": _bilingual(
                    f"{trigger}; refresh thesis evidence before changing posture",
                    "多周期涨跌数据缺失；改变姿态前需先刷新论点证据" if not changes else f"{trigger}；改变姿态前需先刷新论点证据",
                ),
                "review_priority": _holding_priority(item, observation),
                "source": portfolio.get("source"),
                "valuation": valuation_by_asset.get(asset, {}),
            }
        )
    return {
        "status": "configured" if holdings else "missing",
        "source": portfolio.get("source"),
        "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
        "holdings": holdings,
        "valuation_summary": valuation.get("summary", {}),
        "valuation_privacy": valuation.get("privacy", {}),
        "valuation_scope": valuation.get("scope"),
        "global_posture": global_posture,
        "global_posture_label": _action_label(global_posture),
        "holding_execution_authority": False,
        "only_actual_configured_holdings": True,
    }


def _capital_allocation_board(
    portfolio: Mapping[str, Any],
    bottlenecks: Mapping[str, Any],
    triggers: Mapping[str, Any],
) -> dict[str, Any]:
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    progress = _mapping(triggers.get("progress"))
    destination = "Equipment / Materials observation pool"
    if not _bottleneck_has(bottlenecks, "Equipment") and not _bottleneck_has(bottlenecks, "Materials"):
        destination = "Unconfirmed destination"
    return {
        "rebalance_today": "NO",
        "source_of_funds": [
            _bilingual(
                f"Unassigned buffer ({buffer_pct:.1f}% allocation)",
                f"未部署缓冲（{buffer_pct:.1f}% 配置）",
            ),
            _bilingual(
                "Extended current holding review only if trigger evidence appears.",
                "只有触发证据出现时，才复核高位持仓是否可成为资金来源。",
            ),
        ],
        "destination": _bilingual(destination, "Equipment / Materials 观察池"),
        "trigger_status": f"{progress.get('met', 0)} / {progress.get('total', 0)}",
        "execution_style": _bilingual(
            "Wait; do not front-run without trigger confirmation.",
            "等待，不提前抢跑。",
        ),
        "funding_flow": {
            "source": _bilingual("Unassigned buffer / reviewed extended exposure", "未部署缓冲 / 经复核的高位暴露"),
            "destination": _bilingual(destination, "Equipment / Materials 观察池"),
            "why": _bilingual(
                "Improves optionality only if relay evidence and risk/reward reset confirm together.",
                "只有资本接力证据与风险收益重置同时确认时，才改善组合选择权。",
            ),
        },
        "source": str(CAPITAL_ALLOCATION_PATH),
        "no_trading_execution": True,
    }


def _waiting_triggers(
    market: Mapping[str, Any],
    forecast: Mapping[str, Any],
    bottlenecks: Mapping[str, Any],
) -> dict[str, Any]:
    channels = _mapping(market.get("channels"))
    counts = _mapping(forecast.get("counts"))
    observations = _fresh_market_observations(market)
    items = [
        {
            "condition": _bilingual(
                "Equipment / Materials remain confirmed in Bottleneck Map.",
                "Equipment / Materials 仍在瓶颈图中被确认。",
            ),
            "status": "MET" if _bottleneck_has(bottlenecks, "Equipment") and _bottleneck_has(bottlenecks, "Materials") else "UNKNOWN",
            "source": str(BOTTLENECK_MAP_PATH),
        },
        {
            "condition": _bilingual(
                "Portfolio-linked price/volume observations are fresh.",
                "组合相关价量观测保持新鲜。",
            ),
            "status": "MET" if observations else "UNKNOWN",
            "source": "market_intelligence.observations",
        },
        {
            "condition": _bilingual(
                "Market breadth channel confirms participation.",
                "市场广度通道确认参与度。",
            ),
            "status": "MET" if _text(channels.get("market_breadth"), "").upper() == "LIVE" else "NOT_MET",
            "source": "market_intelligence.channels.market_breadth",
        },
        {
            "condition": _bilingual(
                "News / announcement / KOL source is verified.",
                "新闻、公告或 KOL 情报源可验证。",
            ),
            "status": "MET" if _text(channels.get("news_announcement"), "").upper() == "LIVE" else "UNKNOWN",
            "source": "market_intelligence.channels.news_announcement",
        },
        {
            "condition": _bilingual(
                "Forecast lifecycle has matured/evaluated evidence.",
                "预测生命周期已有到期或评估证据。",
            ),
            "status": "MET" if (counts.get("verified") or counts.get("invalidated") or counts.get("inconclusive")) else "UNKNOWN",
            "source": "forecast_ledger",
        },
        {
            "condition": _bilingual(
                "High-severity Risk Radar blockers are reviewed before allocation change.",
                "调度前已复核 Risk Radar 高严重度阻碍。",
            ),
            "status": "PARTIAL",
            "source": str(RISK_RADAR_PATH),
        },
    ]
    met = sum(1 for item in items if item["status"] == "MET")
    return {
        "items": items,
        "progress": {"met": met, "total": len(items), "label": f"{met} / {len(items)}"},
        "status_vocabulary": ["MET", "PARTIAL", "NOT_MET", "UNKNOWN"],
    }


def _top_research_tasks(portfolio: Mapping[str, Any], candidate_pool: Mapping[str, Any]) -> dict[str, Any]:
    positions = [_mapping(item) for item in _list(portfolio.get("positions")) if isinstance(item, Mapping)]
    tasks = []
    for item in sorted(positions, key=lambda value: _safe_number(value.get("portfolio_percentage"), 0.0), reverse=True):
        asset = _text(item.get("asset"), "Unknown")
        theme = _text(item.get("theme"), "Unknown")
        question = _bilingual(
            f"Verify whether {asset} still has fresh order, margin, or qualification evidence.",
            f"核验 {asset} 是否仍有新的订单、利润率或认证证据。",
        )
        tasks.append(
            {
                "question": question,
                "why_now": _bilingual(
                    f"{asset} is an actual configured holding and affects portfolio-level interpretation.",
                    f"{asset} 是当前真实配置持仓，会影响组合层面的解释。",
                ),
                "evidence_gap": _bilingual(
                    _text(item.get("risk_note"), "Holding-specific evidence needs refresh."),
                    _text(item.get("risk_note"), "持仓个别证据需要刷新。"),
                ),
                "related_asset_theme": f"{asset} / {theme}",
            }
        )
        if len(tasks) >= 2:
            break
    tasks.append(
        {
            "question": _bilingual(
                "Verify whether Equipment relay evidence is improving through order/backlog signals.",
                "核验 Equipment 接力是否通过订单或 backlog 信号增强。",
            ),
            "why_now": _bilingual(
                "Equipment is S+ in the current Bottleneck Map and is the next relay destination.",
                "Equipment 在当前瓶颈图中为 S+，也是下一阶段接力方向。",
            ),
            "evidence_gap": _bilingual(
                "Order, backlog, and customer evidence are still the main gap.",
                "订单、backlog 与客户证据仍是主要缺口。",
            ),
            "related_asset_theme": "Equipment / Materials",
        }
    )
    return {
        "items": tasks[:3],
        "full_pool_link": "/candidates",
        "candidate_priority_truth": _candidate_source_truth(candidate_pool),
        "max_items": 3,
    }


def _candidate_source_truth(candidate_pool: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": candidate_pool.get("source") or str(CANDIDATE_SOURCE_PATH),
        "classification": "static_markdown_manual_priority_with_portfolio_overlay",
        "label": _bilingual(
            "Static research pool with manual S/A/B priority; Home only overlays current configured-holding relevance.",
            "静态研究池 + 人工 S/A/B 优先级；首页只叠加当前配置持仓相关性。",
        ),
        "not_runtime_dynamic": True,
        "candidate_ranking_not_trading_action": True,
        "count": len(_list(candidate_pool.get("items"))),
    }


def _intelligence_alerts(state: Mapping[str, Any], market: Mapping[str, Any], portfolio: Mapping[str, Any]) -> dict[str, Any]:
    channels = _mapping(market.get("channels"))
    observations = _usable_market_observations(market)
    alerts = [
        {
            "category": _bilingual("Market sentiment", "市场情绪"),
            "message": _bilingual(
                f"Runtime state is {_text(state.get('regime_state'), 'Unknown')}; attention is low-to-moderate and breadth is not configured.",
                f"市场状态为「{localize_regime(_text(state.get('regime_state'), ''), 'zh') or '未知'}」；注意力偏低到中等，市场广度尚未配置。",
            ),
        },
        {
            "category": _bilingual("Important KOL view changes", "重要观点变化"),
            "message": _bilingual(
                "No verified KOL intelligence source is connected.",
                "当前未接入可验证的 KOL 情报源。",
            ),
        },
        {
            "category": _bilingual("Holding-related signals", "持仓相关信号"),
            "message": (
                _bilingual(
                    f"{len(observations)} configured-holding market observations are usable.",
                    f"{len(observations)} 个配置持仓市场观测可用。",
                )
                if observations
                else _bilingual(
                    "Configured-holding market observations are unavailable; no live holding signal is claimed.",
                    "配置持仓的市场观测当前不可用；Atlas 不宣称存在实时持仓信号。",
                )
            ),
        },
        {
            "category": _bilingual("High-priority alert", "高优先级预警"),
            "message": _bilingual(
                "Risk Radar warns that price may already reflect the thesis after vertical moves.",
                "Risk Radar 提醒：快速上行后价格可能已反映论点。",
            ),
        },
        {
            "category": _bilingual("High-priority alert", "高优先级预警"),
            "message": _bilingual(
                "AI CapEx growth without ROI improvement would pressure AI infrastructure supplier valuation.",
                "如果 AI CapEx 增长但 ROI 不改善，AI 基建供应链估值可能承压。",
            ),
        },
    ]
    if _text(channels.get("news_announcement"), "").upper() == "LIVE":
        alerts[1]["message"] = _bilingual("News/announcement channel is live; verify source quality before treating it as evidence.", "新闻/公告通道可用；仍需验证来源质量后才能作为证据。")
    return {"items": alerts[:5], "max_items": 5}


def _counter_argument() -> dict[str, Any]:
    return {
        "thesis": _bilingual(
            "If AI CapEx ROI deteriorates, AI infrastructure supplier logic can face valuation compression even if infrastructure demand remains visible.",
            "如果 AI CapEx ROI 继续恶化，即使基础设施需求仍可见，AI 基建供应链逻辑也可能面临估值压缩。",
        ),
        "supporting_evidence": _bilingual(
            "Risk Radar records high-severity risks: price already reflects thesis, ROI deterioration, and backlog decline weakening Equipment relay.",
            "Risk Radar 记录了高严重度风险：价格已反映论点、ROI 恶化、backlog 下滑削弱 Equipment 接力。",
        ),
        "more_likely_if": _bilingual(
            "CapEx guidance stays high while AI revenue, FCF, backlog, or utilization evidence weakens.",
            "CapEx 指引维持高位，但 AI 收入、FCF、backlog 或利用率证据转弱。",
        ),
        "source": str(RISK_RADAR_PATH),
    }


def _review_plan(state: Mapping[str, Any], ledger: Mapping[str, Any], triggers: Mapping[str, Any]) -> dict[str, Any]:
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    latest = forecasts[0] if forecasts else {}
    proactive = _mapping(state.get("proactive_update_state"))
    cadence = proactive.get("cadence_seconds") or proactive.get("cadence")
    next_review = "next scheduled proactive update"
    if cadence:
        next_review = f"next scheduled proactive update (~{cadence}s cadence)"
    return {
        "next_review_time": _bilingual(next_review, f"下一次计划主动更新（约 {cadence or '默认'} 秒周期）"),
        "recheck": [
            _bilingual("Capital relay confirmation", "资本迁移是否确认"),
            _bilingual("Forecast deviation or maturity", "预测是否偏离或到期"),
            _bilingual("Waiting trigger count and status", "等待触发条件数量与状态"),
            _bilingual("Holding-specific evidence refresh", "持仓个别证据刷新"),
        ],
        "forecast_due": latest.get("forecast_id") or "No open forecast exposed",
        "triggers_may_change": _list(triggers.get("items"))[:3],
    }


def _read_first_table(source_path: Path) -> list[list[str]]:
    if not source_path.exists():
        return []
    text = source_path.read_text(encoding="utf-8")
    return _table_rows(text)


def _bottleneck_trend(domain: str) -> str:
    return {
        "Memory": "up",
        "Equipment": "up",
        "Materials": "up",
        "Bandwidth": "flat",
        "Power": "flat",
        "Workflow": "watch",
        "Industry AI": "watch",
    }.get(domain, "unknown")


def _bottleneck_has(bottlenecks: Mapping[str, Any], domain: str) -> bool:
    for item in _list(bottlenecks.get("domains")):
        if isinstance(item, Mapping) and _text(item.get("domain"), "").lower() == domain.lower():
            return bool(item.get("strength"))
    return False


def _holding_priority(position: Mapping[str, Any], observation: Mapping[str, Any]) -> str:
    exposure = _safe_number(position.get("portfolio_percentage"), 0.0)
    five_day = abs(_safe_float(observation.get("change_5d_pct"), 0.0)) if observation else 0.0
    if exposure >= 30 or five_day >= 10:
        return "High"
    if exposure >= 20:
        return "Medium"
    return "Normal"


def build_forecast_accountability(ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Summarize existing forecast ledger accountability without changing it."""

    ledger = _mapping(ledger)
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    metrics = _mapping(ledger.get("metrics"))
    # Use full-ledger metrics for counts, not the limited forecasts list.
    open_count = _safe_number(metrics.get("open"), 0)
    matured_count = _safe_number(metrics.get("matured"), 0)
    verified_count = _safe_number(metrics.get("verified"), 0)
    invalidated_count = _safe_number(metrics.get("invalidated"), 0)
    inconclusive_count = _safe_number(metrics.get("inconclusive"), 0)
    # Legacy open: open forecasts without material_signature (from the limited sample).
    legacy_open = [
        item
        for item in forecasts
        if _text(item.get("status"), "").upper() == "OPEN" and not _text(item.get("material_signature"), "")
    ]
    current_open = max(0, open_count - len(legacy_open))
    counts = {
        "open": int(open_count),
        "current_open": int(current_open),
        "legacy_open": len(legacy_open),
        "matured": int(matured_count),
        "verified": int(verified_count),
        "invalidated": int(invalidated_count),
        "inconclusive": int(inconclusive_count),
    }
    evaluated = [
        item
        for item in forecasts
        if _text(item.get("status"), "").upper() in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}
    ]
    misses = [item for item in forecasts if _text(item.get("status"), "").upper() == "INVALIDATED"]
    return {
        "status": "available" if forecasts else "empty",
        "counts": counts,
        "metrics": metrics,
        "sample_warning": _text(ledger.get("sample_warning"), "Low sample size: calibration is directional only."),
        "latest": forecasts[:5],
        "recent_miss": misses[0] if misses else {},
        "evaluated_count": len(evaluated),
        "legacy_policy": _bilingual(
            "Legacy open forecasts without a material signature remain unclassified and are not bulk-evaluated from one observation.",
            "缺少 material signature 的历史未完成预测保持未分类，不会依据单次观测批量结算。",
        ),
        "ledger_link": "/predictions",
        "learning_link": "/learning",
        "learning_log": _forecast_learning_log(counts, metrics),
    }


def _forecast_learning_log(counts: Mapping[str, int], metrics: Mapping[str, Any]) -> dict[str, Any]:
    verified = _safe_number(counts.get("verified"), 0)
    invalidated = _safe_number(counts.get("invalidated"), 0)
    evaluated = _safe_number(metrics.get("evaluated"), 0)
    if verified == 0 and invalidated == 0:
        return {
            "has_lessons": False,
            "message": _bilingual(
                "No forecasts have matured and been evaluated yet. As they do, Atlas will show what it learned from verified and invalidated predictions here.",
                "还没有预测成熟并被评估。一旦有，Atlas 会在这里展示从已验证和已失效预测中学到的东西。",
            ),
        }
    return {
        "has_lessons": True,
        "verified": verified,
        "invalidated": invalidated,
        "evaluated": evaluated,
        "message": _bilingual(
            f"Atlas has evaluated {evaluated:.0f} forecasts so far: {verified:.0f} verified, {invalidated:.0f} invalidated. Each result updates how much trust Atlas places in future predictions.",
            f"Atlas 目前已评估 {evaluated:.0f} 个预测：{verified:.0f} 个被验证，{invalidated:.0f} 个被失效。每个结果都会更新 Atlas 对未来预测的信任度。",
        ),
    }


def build_expert_analysis(state: Mapping[str, Any], ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build structured expert analysis from state, ledger, and data quality."""

    ledger = _mapping(ledger)
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    latest_forecast = forecasts[0] if forecasts else {}
    packet = _mapping(state.get("last_decision_packet"))
    market = _mapping(state.get("market_intelligence"))
    portfolio = _mapping(state.get("portfolio_context"))
    edges = _top_edges(state)
    causal_chain = _causal_chain(edges, packet)
    channels = _mapping(market.get("channels"))
    live = sum(1 for value in channels.values() if _text(value, "").upper() == "LIVE")
    simulated = sum(1 for value in channels.values() if _text(value, "").upper() == "SIMULATED")
    missing = sum(1 for value in channels.values() if _text(value, "").upper() == "NOT_CONFIGURED")
    stale = sum(1 for value in channels.values() if _text(value, "").upper() in {"DELAYED", "CACHED", "RATE_LIMITED", "FAILED"})
    confidence_components = _confidence_components(state, ledger)
    raw_evidence = {
        "regime_state": state.get("regime_state"),
        "last_decision_packet": packet,
        "market_intelligence": {
            "status": market.get("status"),
            "channels": channels,
            "degraded": market.get("degraded"),
            "observations": _list(market.get("observations"))[:5],
        },
        "portfolio_context": {
            "status": portfolio.get("status"),
            "privacy": portfolio.get("privacy"),
            "exposure_sum_pct": portfolio.get("exposure_sum_pct"),
            "cash_or_unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
            "exposure_map": portfolio.get("exposure_map"),
        },
        "forecast_ledger_summary": {
            "metrics": _mapping(ledger.get("metrics")),
            "sample_warning": ledger.get("sample_warning"),
            "latest_forecast_id": latest_forecast.get("forecast_id"),
        },
        "structural_coevolution_state": _compact_mapping(_mapping(state.get("structural_coevolution_state"))),
        "self_organization_state": _compact_mapping(_mapping(state.get("self_organization_state"))),
    }
    return {
        "status": "available",
        "section_count": 9,
        "causal_chain": causal_chain,
        "causal_edges": edges,
        "hypothesis_state": {
            "active": _text(latest_forecast.get("active_hypothesis"), "Insufficient system context"),
            "competing": _competing_hypotheses(state, latest_forecast),
            "confidence": _safe_confidence(latest_forecast.get("confidence", packet.get("confidence", 0.0))),
            "recent_change": _recent_hypothesis_change(state),
        },
        "regime_state": {
            "current": _text(state.get("regime_state"), "Unknown"),
            "proposed": _text(state.get("proposed_state"), "Unknown"),
            "volatility": _text(state.get("volatility"), "Unknown"),
        },
        "confidence_composition": confidence_components,
        "data_quality": {
            "live_channels": live,
            "simulated_channels": simulated,
            "missing_channels": missing,
            "stale_channels": stale,
            "limitation": _data_quality_limitation(live, simulated, missing, stale),
        },
        "portfolio_sensitivity": {
            "largest_positions": _list(_mapping(portfolio.get("exposure_map")).get("asset_concentration"))[:3],
            "theme_concentration": _mapping(_mapping(portfolio.get("exposure_map")).get("theme_concentration")),
            "cash_or_unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
            "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
        },
        "forecast_evidence": {
            "latest_forecast_id": latest_forecast.get("forecast_id"),
            "status": latest_forecast.get("status"),
            "horizon": latest_forecast.get("horizon"),
            "statement": latest_forecast.get("forecast_statement"),
            "drivers": _list(latest_forecast.get("causal_drivers")),
        },
        "invalidation_conditions": _list(latest_forecast.get("invalidation_conditions")) or _default_invalidations(state),
        "raw_evidence": raw_evidence,
    }


def _parse_priority_table(
    text: str,
    heading: str,
    priority: str,
    portfolio_needles: set[str],
    source: Path,
) -> list[dict[str, Any]]:
    section = _section_after_heading(text, heading)
    rows = _table_rows(section)
    items: list[dict[str, Any]] = []
    for row in rows:
        if len(row) < 17:
            continue
        company = row[0]
        thesis = row[9]
        portfolio_relation = _portfolio_relationship(row, portfolio_needles)
        items.append(
            {
                "asset": company,
                "theme": row[2],
                "current_priority": priority,
                "portfolio_relationship": portfolio_relation,
                "evidence_strength": row[14],
                "thesis_direction": thesis,
                "status": "Elevated" if priority == "S" else "Research",
                "source_category": f"Priority {priority}",
                "source": str(source),
                "key_risk": row[11],
                "next_trigger": row[12],
                "last_update": row[15],
                "review_frequency": row[16],
                "reason": row[10],
            }
        )
    return items


def _parse_watch_pool(text: str, portfolio_needles: set[str], source: Path) -> list[dict[str, Any]]:
    section = _section_after_heading(text, "Priority B")
    rows = _table_rows(section)
    items: list[dict[str, Any]] = []
    for row in rows:
        if len(row) < 10:
            continue
        items.append(
            {
                "asset": row[0],
                "theme": row[2],
                "current_priority": "B",
                "portfolio_relationship": _portfolio_relationship(row, portfolio_needles),
                "evidence_strength": row[8],
                "thesis_direction": row[5],
                "status": "Watch",
                "source_category": "Priority B",
                "source": str(source),
                "key_risk": "Evidence not yet sufficient for promotion",
                "next_trigger": row[6],
                "last_update": row[9],
                "review_frequency": "event-driven",
                "reason": row[5],
            }
        )
    return items


def _section_after_heading(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    rest = text[start + len(marker) :]
    next_heading = rest.find("\n## ")
    return rest[:next_heading] if next_heading >= 0 else rest


def _table_rows(section: str) -> list[list[str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if cells[0].lower() in {"company", "company / chain"}:
            continue
        rows.append(cells)
    return rows


def _portfolio_needles(portfolio_context: Mapping[str, Any]) -> set[str]:
    needles: set[str] = set()
    for item in _list(portfolio_context.get("positions")):
        if not isinstance(item, Mapping):
            continue
        for key in ("asset", "user_thesis"):
            text = _text(item.get(key), "")
            if text:
                if key == "asset":
                    needles.add(text.lower())
                for token in _portfolio_tokens(text):
                    if token:
                        needles.add(token.lower())
    return needles


def _portfolio_tokens(text: str) -> list[str]:
    separators = "/,;，；()（）[]【】"
    cleaned = text
    for separator in separators:
        cleaned = cleaned.replace(separator, " ")
    stopwords = {
        "pcb",
        "materials",
        "material",
        "ai",
        "hardware",
        "exposure",
        "chain",
        "semiconductor",
        "infrastructure",
        "manufacturing",
        "risk",
        "requires",
        "monitoring",
        "thesis",
    }
    tokens = []
    for token in cleaned.split():
        stripped = token.strip(".:：")
        if not stripped:
            continue
        if stripped.lower() in stopwords:
            continue
        if any("\u4e00" <= char <= "\u9fff" for char in stripped):
            if len(stripped) >= 3:
                tokens.append(stripped)
            continue
        if "." in stripped or stripped.isupper() or stripped in {"Kingboard", "Dongshan", "Anji"}:
            tokens.append(stripped)
    return tokens


def _portfolio_relationship(row: list[str], portfolio_needles: set[str]) -> str:
    joined = " ".join(row).lower()
    if " yes " in f" {joined} " or "|yes|" in joined:
        return "Direct"
    if any(needle and needle in joined for needle in portfolio_needles):
        return "Direct"
    return "None"


def _sanitize_candidate(item: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(item)
    for key, value in list(record.items()):
        if isinstance(value, str):
            text = value.replace("\x00", " ").strip()
            for forbidden in NO_TRADE_ACTIONS:
                text = text.replace(forbidden.title(), "Capital Action").replace(forbidden.upper(), "CAPITAL ACTION")
            record[key] = text
    status = _text(record.get("status"), "Watch")
    if status not in {"Observe", "Research", "Watch", "Elevated", "Deprioritized"}:
        status = "Watch"
    record["status"] = status
    return record


def _candidate_changes(items: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    changes = []
    for item in items[:6]:
        change = "entered_candidate_pool"
        if item.get("current_priority") == "S":
            change = "priority_raised"
        changes.append(
            {
                "asset": item.get("asset"),
                "change_type": change,
                "why": item.get("reason") or item.get("next_trigger") or "Repository candidate pool evidence",
                "last_update": item.get("last_update"),
            }
        )
    return changes


def _scenario_text(base_state: str, kind: str) -> str:
    state = base_state.upper().replace(" ", "_")
    if kind == "upside":
        if state in {"RISK_OFF", "LIQUIDITY_STRESS"}:
            return "Liquidity improves while market breadth and data freshness recover."
        if state in {"ATTENTION_EXPANSION", "BREAKOUT"}:
            return "Attention converts into broader market participation and confirmed liquidity."
        return "Evidence quality improves and the current state stabilizes."
    if state in {"RISK_OFF", "LIQUIDITY_STRESS"}:
        return "Liquidity and credit-sensitive signals deteriorate together."
    if state in {"ATTENTION_EXPANSION", "BREAKOUT"}:
        return "Attention remains elevated but liquidity confirmation fails."
    return "Trust, data freshness, or portfolio-sensitive channels weaken."


def _default_invalidations(state: Mapping[str, Any]) -> list[str]:
    market = _mapping(state.get("market_intelligence"))
    channels = _mapping(market.get("channels"))
    items = ["trust_score_deteriorates", "portfolio_exposure_changes_materially"]
    if channels:
        items.insert(0, "live_market_channel_interrupts_or_delays")
    else:
        items.insert(0, "market_data_remains_unavailable")
    return items


def _top_edges(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    structural = _mapping(state.get("structural_coevolution_state"))
    self_org = _mapping(state.get("self_organization_state"))
    candidates: dict[str, float] = {}
    for source in (
        _mapping(_mapping(structural.get("applied_drift")).get("edge_weights")),
        _mapping(_mapping(structural.get("mutation")).get("edge_weight_updates")),
        _mapping(self_org.get("causal_reweight_delta")),
    ):
        for key, value in source.items():
            try:
                candidates[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
    edges = []
    for key, value in sorted(candidates.items(), key=lambda pair: abs(pair[1]), reverse=True)[:6]:
        parts = key.split("->") if "->" in key else key.split(":")
        edges.append(
            {
                "from": parts[0].strip() if parts else "Source",
                "to": parts[1].strip() if len(parts) > 1 else "Target",
                "weight_delta": round(value, 4),
            }
        )
    return edges


def _causal_chain(edges: list[Mapping[str, Any]], packet: Mapping[str, Any]) -> list[str]:
    if edges:
        chain = []
        for edge in edges[:4]:
            chain.append(f"{edge.get('from')} -> {edge.get('to')}")
        return chain
    summary = _text(packet.get("causal_summary"), "")
    if summary and "unavailable" not in summary.lower():
        return [summary]
    return [_bilingual("Insufficient causal-chain evidence in current state.", "当前状态缺乏足够的因果链证据。")]


def _competing_hypotheses(state: Mapping[str, Any], latest_forecast: Mapping[str, Any]) -> list[str]:
    distribution = _mapping(
        _mapping(state.get("last_decision_packet")).get("causal_hypothesis_score_distribution")
    )
    if distribution:
        return [str(key) for key, _ in sorted(distribution.items(), key=lambda pair: pair[1], reverse=True)[:3]]
    active = _text(latest_forecast.get("active_hypothesis"), "")
    if active:
        return [_bilingual("No competing hypothesis exposed by current state.", "当前状态未暴露竞争假设。")]
    return [_bilingual("Insufficient hypothesis evidence.", "假设证据不足。")]


def _recent_hypothesis_change(state: Mapping[str, Any]) -> Any:
    self_org = _mapping(state.get("self_organization_state"))
    shift = self_org.get("structural_shift_index") or _mapping(state.get("structural_coevolution_state")).get("structural_shift_index")
    if shift is None:
        return _bilingual("No recent hypothesis change exposed.", "近期未暴露假设变化。")
    return _bilingual(f"Structural shift index {shift}", f"结构位移指数 {shift}")


def _confidence_components(state: Mapping[str, Any], ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    market = _mapping(state.get("market_intelligence"))
    channels = _mapping(market.get("channels"))
    total = max(1, len(channels))
    live_or_sim = sum(1 for value in channels.values() if _text(value, "").upper() in {"LIVE", "SIMULATED", "CACHED", "DELAYED"})
    trust = _safe_float(state.get("trust_index"), 0.0)
    portfolio = _mapping(state.get("portfolio_context"))
    relevance = _safe_float(_mapping(portfolio.get("exposure_map")).get("portfolio_relevance_score"), 0.0) / 100.0
    metrics = _mapping(ledger.get("metrics"))
    evaluated = _safe_float(metrics.get("evaluated"), 0.0)
    return [
        {"name": "evidence_quality", "value": round(min(1.0, live_or_sim / total), 4), "source": "market channel status"},
        {"name": "market_data_completeness", "value": round(min(1.0, live_or_sim / total), 4), "source": "market_intelligence.channels"},
        {"name": "hypothesis_stability", "value": round(max(0.0, min(1.0, trust)), 4), "source": "system_trust_state"},
        {"name": "portfolio_relevance", "value": round(max(0.0, min(1.0, relevance)), 4), "source": "portfolio_context"},
        {"name": "forecast_history", "value": round(min(1.0, evaluated / 20.0), 4), "source": "forecast_ledger"},
    ]


def _data_quality_limitation(live: int, simulated: int, missing: int, stale: int) -> str:
    if missing or stale:
        return "Confidence is limited by missing, stale, or unconfigured market channels."
    if simulated:
        return "Confidence is limited because some channels are simulated."
    if live:
        return "Live channels are available, but forecast outcomes still need accumulation."
    return "Confidence is limited because no market channels are currently available."


def _compact_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "status",
        "bounded",
        "trust_gate",
        "structural_shift_index",
        "mutation_intensity",
        "graph_edge_count",
        "graph_node_count",
        "no_node_creation",
        "no_topology_rewrite",
    )
    return {key: value.get(key) for key in keys if key in value}


def _home_evidence_quality(market: Mapping[str, Any], forecast: Mapping[str, Any]) -> dict[str, Any]:
    channels = _mapping(market.get("channels"))
    total = max(1, len(channels))
    live = sum(1 for value in channels.values() if _text(value, "").upper() == "LIVE")
    usable = sum(1 for value in channels.values() if _text(value, "").upper() in {"LIVE", "DELAYED", "CACHED", "SIMULATED"})
    configured = sum(1 for value in channels.values() if _text(value, "").upper() != "NOT_CONFIGURED")
    usable_observations = _usable_market_observations(market)
    score = round(min(1.0, usable / total), 4)
    if _list(market.get("observations")) and not usable_observations:
        score = 0.0
    if live >= 2 and configured >= total / 2:
        status = "partial"
        label = _bilingual("Partial live evidence", "部分实时证据")
    elif usable:
        status = "limited"
        label = _bilingual("Limited evidence", "证据有限")
    else:
        status = "insufficient"
        label = _bilingual("Insufficient evidence", "证据不足")
    metrics = _mapping(forecast.get("metrics"))
    evaluated = _safe_float(metrics.get("evaluated"), 0.0)
    if evaluated <= 0:
        sample = _bilingual("No evaluated forecast sample yet", "尚无已评估预测样本")
    else:
        sample = _bilingual(f"{evaluated:.0f} evaluated forecasts", f"{evaluated:.0f} 个已评估预测")
    return {
        "status": status,
        "label": label,
        "score": score,
        "live_channels": live,
        "usable_channels": usable,
        "usable_observations": len(usable_observations),
        "total_channels": len(channels),
        "forecast_sample": sample,
    }


def _usable_market_observations(market: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        _mapping(item)
        for item in _list(market.get("observations"))
        if isinstance(item, Mapping) and _observation_is_usable(item)
    ]


def _fresh_market_observations(market: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in _usable_market_observations(market)
        if _text(item.get("freshness"), "").strip().lower() in FRESH_FRESHNESS
    ]


def _observation_is_usable(observation: Mapping[str, Any]) -> bool:
    quality = _text(observation.get("data_quality_status"), "").strip().lower()
    source = _text(observation.get("source"), "").strip().lower()
    if quality not in USABLE_OBSERVATION_QUALITY or source in UNUSABLE_SOURCES:
        return False
    if "latest_price_available" in observation and observation.get("latest_price_available") is False:
        return False
    return True


def _decision_packet_is_fallback(packet: Mapping[str, Any]) -> bool:
    trace = _text(packet.get("reasoning_trace"), "").lower()
    summary = _text(packet.get("causal_summary"), "").lower()
    action = _text(packet.get("recommended_action"), "").lower()
    return "invalid_llm_output" in trace or "unavailable" in summary or action == "neutral"


def _confidence_text(value: Any) -> str:
    return f"{_safe_confidence(value) * 100:.0f}%"


def _action_label(action: str) -> dict[str, str]:
    labels = {
        "observe": _bilingual("Observe", "观察"),
        "hold": _bilingual("Hold", "持有"),
        "reduce": _bilingual("Reduce", "降低暴露"),
        "build": _bilingual("Build", "建立观察仓位"),
        "accumulate": _bilingual("Accumulate", "逐步增加"),
    }
    return labels.get(action, labels["observe"])


def _match_position_candidate(position: Mapping[str, Any], candidates: list[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    raw_position_text = " ".join(
        _text(position.get(key), "")
        for key in ("asset", "theme", "role", "user_thesis")
    )
    tokens = {token.lower() for token in _portfolio_tokens(raw_position_text)}
    asset = _text(position.get("asset"), "")
    if asset:
        tokens.add(asset.lower())
    for item in candidates:
        item_text = " ".join(
            _text(item.get(key), "")
            for key in ("asset", "theme", "thesis_direction", "reason")
        ).lower()
        if any(token and token.lower() in item_text for token in tokens):
            return item
    return None


def _bilingual(en: str, zh: str) -> dict[str, str]:
    return {"en": en, "zh": zh}


def _safe_confidence(value: Any) -> float:
    return round(max(0.0, min(1.0, _safe_float(value, 0.0))), 4)


def _safe_float(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number > 1:
        number /= 100
    return number


def _safe_number(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _text(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).replace("\x00", " ").strip()
    if not text or text.lower() in {"none", "null"}:
        return fallback
    return text
