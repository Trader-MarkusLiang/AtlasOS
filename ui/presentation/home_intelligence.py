"""Read-only Home intelligence presentation adapter.

This module only projects existing Atlas repository/runtime evidence into UI
view models. It does not create forecasts, mutate cognition, alter portfolio
state, or change trading authority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


CANDIDATE_SOURCE_PATH = Path("02_Databases/AI_Shovel_100.md")
BOTTLENECK_MAP_PATH = Path("04_Current_State/Bottleneck_Map_v1.md")
CAPITAL_RELAY_PATH = Path("01_Framework/Capital_Relay.md")
AI_CAPITAL_MAP_PATH = Path("04_Current_State/AI_Capital_Map_v1.md")
CAPITAL_ALLOCATION_PATH = Path("03_Trading_OS/Capital_Allocation_Board.md")
CAPITAL_ROTATION_PATH = Path("03_Trading_OS/Capital_Rotation_Table.md")
RISK_RADAR_PATH = Path("02_Databases/Risk_Radar.md")
FORECAST_STATUSES = ("OPEN", "MATURED", "VERIFIED", "INVALIDATED", "INCONCLUSIVE")
NO_TRADE_ACTIONS = {"buy", "sell"}


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
    portfolio = _mapping(state.get("portfolio_context"))
    ledger = _mapping(state.get("forecast_ledger"))
    bottlenecks = _bottleneck_index()
    capital_relay = _capital_relay()
    triggers = _waiting_triggers(market, forecast_accountability, bottlenecks)
    allocation = _capital_allocation_board(portfolio, bottlenecks, triggers)
    predictions = _strongest_predictions(ledger, packet, market)
    holdings = _current_holdings_board(portfolio, market)
    return {
        "chain_order": [
            "action_today",
            "core_judgment",
            "strongest_predictions",
            "ai_bottleneck_index",
            "capital_relay",
            "current_holdings",
            "capital_allocation",
            "waiting_triggers",
            "research_tasks",
            "intelligence_alerts",
            "counter_argument",
            "review_plan",
        ],
        "action_today": _action_today(packet, market, portfolio),
        "core_judgment": _practical_core_judgment(packet, market, portfolio, capital_relay),
        "strongest_predictions": predictions,
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
        "source_boundaries": {
            "presentation_only": True,
            "read_only": True,
            "no_cognition_semantics_change": True,
            "no_forecast_semantics_change": True,
            "no_portfolio_mutation": True,
            "no_trading_execution": True,
            "no_private_amounts": True,
        },
    }


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
            f"运行状态刷新为 {regime.replace('_', ' ')}。",
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
            "由于 LLM 推理不可用或无效，DecisionPacket 回退到中性/观察；Atlas 需要先依赖证据校验，再考虑改变姿态。",
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
            f"{regime.replace('_', ' ')} 仍是当前前瞻工作结构，除非后续观测状态与之冲突。",
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
            "verified": counts.get("verified", 0),
            "invalidated": counts.get("invalidated", 0),
            "inconclusive": counts.get("inconclusive", 0),
        },
        "recent_miss": miss_summary,
        "what_changed_afterward": changed,
        "sample_warning": forecast.get("sample_warning"),
        "links": {"predictions": "/predictions", "learning": "/learning"},
    }


def _action_today(packet: Mapping[str, Any], market: Mapping[str, Any], portfolio: Mapping[str, Any]) -> dict[str, Any]:
    confidence = _safe_confidence(packet.get("confidence", 0.0))
    channels = _mapping(market.get("channels"))
    live_count = sum(1 for value in channels.values() if _text(value, "").upper() == "LIVE")
    missing_count = sum(1 for value in channels.values() if _text(value, "").upper() in {"NOT_CONFIGURED", "FAILED"})
    observations = _list(market.get("observations"))
    configured = _text(portfolio.get("status"), "").lower() == "configured"
    if configured and observations and missing_count:
        status = "CONDITIONAL"
        reason = _bilingual(
            "Portfolio-linked price data is live, but breadth/news/macro channels remain incomplete; review is justified, execution is not.",
            "组合相关价量数据已更新，但市场广度、新闻、宏观等通道仍不完整；需要复核，不支持执行。",
        )
    elif confidence >= 0.65 and live_count >= 3:
        status = "YES"
        reason = _bilingual(
            "Evidence quality is strong enough to justify a portfolio decision review.",
            "证据质量足以支持进入组合决策复核。",
        )
    else:
        status = "NO"
        reason = _bilingual(
            "Current evidence does not justify new portfolio action; keep the brief in observation mode.",
            "当前证据不足以支持新增组合动作，简报保持观察模式。",
        )
    return {
        "status": status,
        "posture": "observe",
        "posture_label": _action_label("observe"),
        "reason": reason,
        "helper": _bilingual(
            "YES / NO / CONDITIONAL means whether evidence justifies decision review today, not an order.",
            "YES / NO / CONDITIONAL 表示今天是否值得进入决策复核，不是交易指令。",
        ),
        "confidence": confidence,
        "no_trading_execution": True,
    }


def _practical_core_judgment(
    packet: Mapping[str, Any],
    market: Mapping[str, Any],
    portfolio: Mapping[str, Any],
    capital_relay: Mapping[str, Any],
) -> dict[str, Any]:
    regime = _text(packet.get("regime_state"), "Unknown").split("/")[0].strip()
    buffer_pct = _safe_number(portfolio.get("cash_or_unassigned_pct"), 0.0)
    observations = _list(market.get("observations"))
    headline = _bilingual(
        "AI infrastructure thesis is not invalidated, but Atlas should wait for confirmation before expanding risk.",
        "AI 基建主线未被证伪，但 Atlas 需要等待确认后再扩大风险暴露。",
    )
    support = _bilingual(
        f"Runtime is {regime or 'Unknown'}, {len(observations)} portfolio-linked price observations are live, and the relay map still points toward Equipment / Materials; unassigned buffer is {buffer_pct:.1f}%.",
        f"运行态为 {regime or 'Unknown'}，{len(observations)} 个组合相关价量观测可用，资本接力仍指向 Equipment / Materials；未部署缓冲为 {buffer_pct:.1f}%。",
    )
    if not observations:
        support = _bilingual(
            "Market observations are insufficient, so the core judgment is observation-first.",
            "市场观测不足，因此今日总判断以观察为先。",
        )
    return {
        "headline": headline,
        "supporting_sentence": support,
        "source": "DecisionPacket + market_intelligence + portfolio_context + Capital Relay snapshot",
        "relay_stage": capital_relay.get("current_stage"),
    }


def _strongest_predictions(ledger: Mapping[str, Any], packet: Mapping[str, Any], market: Mapping[str, Any]) -> dict[str, Any]:
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    predictions: list[dict[str, Any]] = []
    latest = forecasts[0] if forecasts else {}
    confidence = _safe_confidence(latest.get("confidence", packet.get("confidence", 0.0)))
    if latest:
        evidence = _list(latest.get("causal_drivers"))
        if _list(market.get("observations")):
            evidence.append("fresh_portfolio_price_volume_observations")
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


def _current_holdings_board(portfolio: Mapping[str, Any], market: Mapping[str, Any]) -> dict[str, Any]:
    observations = {
        _text(_mapping(item).get("asset"), ""): _mapping(item)
        for item in _list(market.get("observations"))
        if isinstance(item, Mapping)
    }
    holdings = []
    for item in _list(portfolio.get("positions")):
        if not isinstance(item, Mapping):
            continue
        asset = _text(item.get("asset"), "Unknown")
        observation = observations.get(asset, {})
        trigger = _text(item.get("risk_note"), "Refresh thesis, price/volume, and liquidity evidence.")
        if observation:
            trigger = f"5d {round(_safe_float(observation.get('change_5d_pct'), 0.0), 1)}%, 20d {round(_safe_float(observation.get('change_20d_pct'), 0.0), 1)}%; refresh thesis evidence before changing posture"
        holdings.append(
            {
                "asset": asset,
                "theme": _text(item.get("theme"), "Unknown"),
                "exposure_pct": item.get("portfolio_percentage"),
                "posture": "observe",
                "posture_label": _action_label("observe"),
                "why": _bilingual(
                    _text(item.get("user_thesis"), "Configured holding requires evidence refresh."),
                    _text(item.get("user_thesis"), "当前配置持仓需要刷新证据。"),
                ),
                "key_trigger": _bilingual(trigger, trigger),
                "review_priority": _holding_priority(item, observation),
                "source": portfolio.get("source"),
            }
        )
    return {
        "status": "configured" if holdings else "missing",
        "source": portfolio.get("source"),
        "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
        "holdings": holdings,
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
    observations = _list(market.get("observations"))
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
    observations = _list(market.get("observations"))
    alerts = [
        {
            "category": _bilingual("Market sentiment", "市场情绪"),
            "message": _bilingual(
                f"Runtime state is {_text(state.get('regime_state'), 'Unknown')}; attention is low-to-moderate and breadth is not configured.",
                f"运行态为 {_text(state.get('regime_state'), 'Unknown')}；注意力偏低到中等，市场广度尚未配置。",
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
            "message": _bilingual(
                f"{len(observations)} configured-holding price/volume observations are available.",
                f"{len(observations)} 个配置持仓价量观测可用。",
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
    counts = {status.lower(): sum(1 for item in forecasts if _text(item.get("status"), "").upper() == status) for status in FORECAST_STATUSES}
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
        "ledger_link": "/predictions",
        "learning_link": "/learning",
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
    return ["Insufficient causal-chain evidence in current state."]


def _competing_hypotheses(state: Mapping[str, Any], latest_forecast: Mapping[str, Any]) -> list[str]:
    distribution = _mapping(
        _mapping(state.get("last_decision_packet")).get("causal_hypothesis_score_distribution")
    )
    if distribution:
        return [str(key) for key, _ in sorted(distribution.items(), key=lambda pair: pair[1], reverse=True)[:3]]
    active = _text(latest_forecast.get("active_hypothesis"), "")
    if active:
        return ["No competing hypothesis exposed by current state."]
    return ["Insufficient hypothesis evidence."]


def _recent_hypothesis_change(state: Mapping[str, Any]) -> str:
    self_org = _mapping(state.get("self_organization_state"))
    shift = self_org.get("structural_shift_index") or _mapping(state.get("structural_coevolution_state")).get("structural_shift_index")
    if shift is None:
        return "No recent hypothesis change exposed."
    return f"Structural shift index {shift}"


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
    score = round(min(1.0, usable / total), 4)
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
        "total_channels": len(channels),
        "forecast_sample": sample,
    }


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
