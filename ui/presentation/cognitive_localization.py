"""Locale-aware projection of Atlas cognitive runtime output.

This module does not mutate DecisionPacket source evidence. It builds a
read-only UI presentation layer from existing runtime state so browser views can
show localized, concise Decision Briefs while keeping raw model output available
under expert details.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping
from zoneinfo import ZoneInfo


ConceptLabel = dict[str, str]


CONCEPT_LABELS: dict[str, ConceptLabel] = {
    "liquidity_stress": {"zh": "流动性压力", "en": "Liquidity Stress"},
    "liquidity_shock": {"zh": "流动性冲击", "en": "Liquidity Shock"},
    "volatility_shock": {"zh": "波动冲击", "en": "Volatility Shock"},
    "volatility_pressure": {"zh": "波动压力", "en": "Volatility Pressure"},
    "risk_off": {"zh": "风险防御", "en": "Risk-Off"},
    "attention_pressure": {"zh": "注意力压力", "en": "Attention Pressure"},
    "narrative_pressure": {"zh": "叙事压力", "en": "Narrative Pressure"},
    "institutional_flow": {"zh": "机构资金流", "en": "Institutional Flow"},
    "retail_flow": {"zh": "散户资金流", "en": "Retail Flow"},
    "price_momentum": {"zh": "价格动量", "en": "Price Momentum"},
    "data_insufficient": {"zh": "数据不足", "en": "Data Insufficient"},
    "distribution_risk": {"zh": "分布风险", "en": "Distribution Risk"},
    "crash_stress": {"zh": "崩盘压力", "en": "Crash Stress"},
    "portfolio_relevance": {"zh": "组合相关性", "en": "Portfolio Relevance"},
    "neutral_state": {"zh": "中性观察", "en": "Neutral State"},
    "market_state_change": {"zh": "市场状态发生变化", "en": "Market State Change"},
}


CONCEPT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "liquidity_stress": (
        "liquidity stress",
        "liquidity constraints",
        "liquidity constraint",
        "liquidity-driven",
        "liquidity score is severely weak",
        "流动性压力",
    ),
    "liquidity_shock": ("liquidity shock", "流动性冲击"),
    "volatility_shock": ("volatility shock", "波动冲击"),
    "volatility_pressure": ("volatility pressure", "liquidity -> volatility", "波动压力"),
    "risk_off": ("risk_off", "risk off", "defensive", "防御"),
    "attention_pressure": ("attention pressure", "attention", "注意力"),
    "narrative_pressure": ("narrative pressure", "narrative", "叙事"),
    "institutional_flow": ("institutional flow", "机构"),
    "retail_flow": ("retail flow", "散户"),
    "price_momentum": ("price momentum", "价格动量"),
    "data_insufficient": ("data-insufficient", "data insufficient", "data confidence is limited", "limited data", "数据不足"),
    "distribution_risk": ("distribution risk", "分布风险"),
    "crash_stress": ("crash stress", "崩盘压力"),
    "portfolio_relevance": ("portfolio relevance", "portfolio relevant", "portfolio context", "组合"),
}


ACTION_LABELS: dict[str, ConceptLabel] = {
    "observe": {"zh": "观察", "en": "Observe"},
    "hold": {"zh": "保持", "en": "Hold"},
    "reduce": {"zh": "降低暴露", "en": "Reduce"},
    "build": {"zh": "逐步建立", "en": "Build"},
    "accumulate": {"zh": "逐步增加", "en": "Accumulate"},
    "neutral": {"zh": "中性观察", "en": "Neutral"},
}


RISK_LABELS: dict[str, ConceptLabel] = {
    "high": {"zh": "高", "en": "High"},
    "medium": {"zh": "中", "en": "Medium"},
    "moderate": {"zh": "中", "en": "Moderate"},
    "low": {"zh": "低", "en": "Low"},
    "unknown": {"zh": "未知", "en": "Unknown"},
}


CHANNEL_LABELS: dict[str, ConceptLabel] = {
    "market_breadth": {"zh": "市场广度", "en": "Market Breadth"},
    "news_announcement": {"zh": "新闻与公告", "en": "News & Announcements"},
    "narrative_attention": {"zh": "叙事与注意力", "en": "Narrative & Attention"},
    "macro_policy": {"zh": "宏观政策", "en": "Macro Policy"},
    "price_volume": {"zh": "价格与成交量", "en": "Price & Volume"},
    "portfolio_relevance": {"zh": "组合相关性", "en": "Portfolio Relevance"},
    "liquidity_proxy": {"zh": "流动性代理", "en": "Liquidity Proxy"},
    "volatility": {"zh": "波动率", "en": "Volatility"},
}


STATUS_LABELS: dict[str, ConceptLabel] = {
    "LIVE": {"zh": "实时", "en": "Live"},
    "DELAYED": {"zh": "延迟", "en": "Delayed"},
    "CACHED": {"zh": "缓存", "en": "Cached"},
    "SIMULATED": {"zh": "模拟", "en": "Simulated"},
    "NOT_CONFIGURED": {"zh": "未配置", "en": "Not Configured"},
    "RATE_LIMITED": {"zh": "限流", "en": "Rate Limited"},
    "FAILED": {"zh": "失败", "en": "Failed"},
    "Available": {"zh": "可用", "en": "Available"},
    "Unavailable": {"zh": "不可用", "en": "Unavailable"},
    "Partial": {"zh": "部分可用", "en": "Partial"},
    "Unknown": {"zh": "未知", "en": "Unknown"},
    "planned": {"zh": "已计划", "en": "Planned"},
    "completed": {"zh": "已完成", "en": "Completed"},
    "waiting": {"zh": "等待信号", "en": "Waiting"},
}


MARKET_LABELS: dict[str, ConceptLabel] = {
    "A-share": {"zh": "A股", "en": "A-share"},
    "A_SHARE": {"zh": "A股", "en": "A-share"},
    "HK": {"zh": "港股", "en": "HK"},
    "US": {"zh": "美股", "en": "US"},
}


THEME_LABELS: dict[str, ConceptLabel] = {
    "Semiconductor Materials": {"zh": "半导体材料", "en": "Semiconductor Materials"},
    "PCB / Materials / AI Infrastructure": {"zh": "PCB / 材料 / AI 基础设施", "en": "PCB / Materials / AI Infrastructure"},
    "PCB / AI Hardware Manufacturing": {"zh": "PCB / AI 硬件制造", "en": "PCB / AI Hardware Manufacturing"},
}


FACTOR_LABELS: dict[str, ConceptLabel] = {
    **CONCEPT_LABELS,
    "Narrative Pressure": {"zh": "叙事压力", "en": "Narrative Pressure"},
    "Attention": {"zh": "市场注意力", "en": "Attention"},
    "Institutional Flow": {"zh": "机构资金流", "en": "Institutional Flow"},
    "Liquidity": {"zh": "流动性", "en": "Liquidity"},
    "Volatility": {"zh": "波动率", "en": "Volatility"},
    "Retail Flow": {"zh": "散户资金流", "en": "Retail Flow"},
    "Price Momentum": {"zh": "价格动量", "en": "Price Momentum"},
}


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def build_cognitive_presentation(state: Mapping[str, Any], lang: str = "en") -> dict[str, Any]:
    """Return a localized UI projection for Home and live inspector refresh."""

    lang = _safe_lang(lang)
    packet = _packet(state)
    market = _market(state)
    proactive = _mapping(state.get("proactive_update_state"))
    portfolio = _portfolio(state)
    concepts = _extract_concepts(state)
    primary = _primary_concept(concepts, packet, state)
    secondary = _secondary_concept(concepts, primary)
    sections = _reason_sections(state, primary, secondary, lang)
    summary = " ".join(section["body"] for section in sections)
    action = localized_action(packet.get("recommended_action"), lang)
    risk = localized_risk(packet.get("risk_level"), lang)

    return {
        "language": lang,
        "hero": {
            "kicker": "当前主导状态" if lang == "zh" else "Current dominant state",
            "title": label_for_concept(primary, lang)["primary"],
            "secondary": label_for_concept(primary, lang)["secondary"],
            "summary": summary,
        },
        "decision": {
            "action": action,
            "confidence": _confidence(packet),
            "risk": risk,
            "attention": localized_state_value(packet.get("attention_state") or state.get("attention"), lang, "attention"),
            "liquidity": localized_state_value(packet.get("liquidity_state") or state.get("liquidity"), lang, "liquidity"),
            "summary": summary,
        },
        "inspector": {
            "why_title": "为什么会这样" if lang == "zh" else "Why this happened",
            "sections": sections,
            "reasoning_summary": summary,
            "causal_summary": summary,
            "factors": localized_factors(state, packet, lang),
            "regime_influence": _regime_influence(state, action, lang),
            "trust_impact": _trust_impact(state, lang),
            "trust_trend": _trust_trend(state, lang),
            "stability": _stability_label(state, lang),
        },
        "market": localize_market_freshness(market, lang),
        "proactive": localize_proactive_update(proactive, lang),
        "raw_available": True,
        "source_fields": ["last_decision_packet", "market_intelligence", "proactive_update_state"],
    }


def localized_action(value: Any, lang: str = "en") -> dict[str, str]:
    key = str(value or "neutral").strip().lower()
    if key in {"neutral", "unknown", "wait"}:
        labels = ACTION_LABELS["observe"]
        return _dual(labels, lang, raw=key)
    labels = ACTION_LABELS.get(key, ACTION_LABELS["neutral"])
    return _dual(labels, lang, raw=key)


def localized_risk(value: Any, lang: str = "en") -> dict[str, str]:
    key = str(value or "unknown").strip().lower()
    labels = RISK_LABELS.get(key, RISK_LABELS["unknown"])
    return _dual(labels, lang, raw=key)


def label_for_concept(key: str, lang: str = "en") -> dict[str, str]:
    labels = CONCEPT_LABELS.get(key, CONCEPT_LABELS["market_state_change"])
    return _dual(labels, lang, raw=key)


def localized_state_value(value: Any, lang: str, category: str = "") -> dict[str, str]:
    text = str(value if value is not None else "").strip()
    if not text:
        return {"primary": "等待认知信号" if lang == "zh" else "Waiting for cognitive signal", "secondary": "", "raw": ""}
    concepts = _concepts_from_text(text)
    if concepts:
        primary = concepts[0]
        label = label_for_concept(primary, lang)
        if lang == "zh" and category == "attention" and "not dominant" in text.lower():
            label["primary"] = "市场注意力不是主导压力"
            label["secondary"] = "Attention not dominant"
        return {**label, "raw": text}
    if lang == "zh":
        if category == "attention":
            return {"primary": "注意力状态待确认", "secondary": "", "raw": text}
        if category == "liquidity":
            return {"primary": "流动性状态待确认", "secondary": "", "raw": text}
        return {"primary": "等待认知信号", "secondary": "", "raw": text}
    return {"primary": _humanize(text), "secondary": "", "raw": text}


def localize_market_freshness(market: Mapping[str, Any], lang: str = "en") -> dict[str, Any]:
    lang = _safe_lang(lang)
    channels = _mapping(market.get("channels"))
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    channel_rows = [
        {
            "key": str(key),
            "label": localize_channel_name(str(key), lang),
            "status": localize_status(value, lang),
            "css": _status_css(str(value)),
        }
        for key, value in channels.items()
    ]
    observation_rows = [_localized_observation(item, lang) for item in observations if isinstance(item, Mapping)]
    return {
        "summary": _market_summary(channels, observation_rows, lang),
        "channels": channel_rows,
        "observations": observation_rows,
        "empty": "实时市场数据暂不可用，Atlas 正在降级模式下运行。" if lang == "zh" else "Live market data is unavailable. Atlas is running in degraded mode.",
        "timestamp": format_timestamp(market.get("timestamp"), lang, prefix="上次更新" if lang == "zh" else "Last update"),
    }


def localize_proactive_update(proactive: Mapping[str, Any], lang: str = "en") -> dict[str, Any]:
    lang = _safe_lang(lang)
    if not proactive:
        return {
            "available": False,
            "title": "主动更新" if lang == "zh" else "Proactive update",
            "heading": "等待首次主动更新运行" if lang == "zh" else "Waiting for the first proactive update",
            "subtitle": _proactive_subtitle(lang),
        }
    channels = proactive.get("market_channels_to_refresh") if isinstance(proactive.get("market_channels_to_refresh"), list) else []
    focus = proactive.get("research_focus") if isinstance(proactive.get("research_focus"), list) else []
    channel_labels = [localize_channel_name(str(item), lang) for item in channels[:8]]
    fallback_focus = ["尚未配置组合；先刷新宽口径市场上下文"] if lang == "zh" else ["No configured portfolio yet; refresh broad context"]
    return {
        "available": True,
        "title": "主动更新" if lang == "zh" else "Proactive update",
        "heading": "下一轮关注什么" if lang == "zh" else "What Atlas will refresh next",
        "subtitle": _proactive_subtitle(lang),
        "status": localize_status(proactive.get("status") or "waiting", lang),
        "cadence": duration_text(proactive.get("cadence_seconds"), lang),
        "last_run": format_timestamp(proactive.get("timestamp"), lang, prefix="上次更新" if lang == "zh" else "Last update"),
        "next_due": format_timestamp(proactive.get("next_due_at"), lang, prefix="下次更新" if lang == "zh" else "Next update"),
        "channels_text": "、".join(channel_labels) if lang == "zh" else ", ".join(channel_labels),
        "focus_items": [localize_research_focus(str(item), lang) for item in focus[:8]] or fallback_focus,
    }


def localized_factors(state: Mapping[str, Any], packet: Mapping[str, Any] | None = None, lang: str = "en") -> list[dict[str, str]]:
    packet = packet or _packet(state)
    concepts = _extract_concepts(state)
    preferred = [item for item in ("liquidity_stress", "volatility_shock", "data_insufficient", "portfolio_relevance") if item in concepts]
    graph = _dashboard_graph_factors(state)
    keys: list[str] = []
    for key in preferred + graph:
        if key not in keys:
            keys.append(key)
    if not keys:
        keys = ["attention_pressure", "liquidity_stress", "volatility_pressure"]
    return [localized_factor(key, lang) for key in keys[:3]]


def localized_factor(value: Any, lang: str = "en") -> dict[str, str]:
    text = str(value or "").strip()
    labels = FACTOR_LABELS.get(text) or CONCEPT_LABELS.get(text)
    if labels:
        return _dual(labels, lang, raw=text)
    concept = _concepts_from_text(text)
    if concept:
        return label_for_concept(concept[0], lang)
    human = _humanize(text or "Unknown")
    if lang == "zh":
        return {"primary": "未识别因果因素", "secondary": human, "raw": text}
    return {"primary": human, "secondary": "", "raw": text}


def localize_channel_name(key: str, lang: str = "en") -> str:
    labels = CHANNEL_LABELS.get(str(key), None)
    if labels:
        return labels.get(_safe_lang(lang), labels["en"])
    return _humanize(str(key))


def localize_status(value: Any, lang: str = "en") -> dict[str, str]:
    raw = str(value or "Unknown")
    key = raw if raw in STATUS_LABELS else raw.upper()
    labels = STATUS_LABELS.get(key) or STATUS_LABELS.get(raw) or {"zh": _humanize(raw), "en": _humanize(raw)}
    return _dual(labels, lang, raw=raw)


def localize_market_label(value: Any, lang: str = "en") -> str:
    raw = str(value or "").strip()
    labels = MARKET_LABELS.get(raw) or MARKET_LABELS.get(raw.upper())
    if labels:
        return labels.get(_safe_lang(lang), labels["en"])
    return raw or ("未知市场" if lang == "zh" else "Unknown market")


def localize_theme(value: Any, lang: str = "en", *, bilingual: bool = True) -> str:
    raw = str(value or "").strip()
    labels = THEME_LABELS.get(raw)
    if not labels:
        return raw or ("未指定主题" if lang == "zh" else "Unspecified theme")
    if lang == "zh" and bilingual and labels["zh"] != labels["en"]:
        return f"{labels['zh']}（{labels['en']}）"
    return labels.get(_safe_lang(lang), labels["en"])


def localize_research_focus(text: str, lang: str = "en") -> str:
    text = " ".join(str(text or "").split())
    asset_match = re.match(r"^(.+?)\s+\(([^)]+)\)\s+price, volume, liquidity, and announcement freshness$", text, re.I)
    if asset_match:
        asset, market = asset_match.groups()
        market_label = localize_market_label(market, lang)
        if lang == "zh":
            return f"{asset}（{market_label}）：价格、成交量、流动性与公告更新"
        return f"{asset} ({market_label}): price, volume, liquidity, and announcement freshness"
    refresh_match = re.match(r"^Refresh degraded channels:\s*(.+)$", text, re.I)
    if refresh_match:
        channels = [localize_channel_name(item.strip(), lang) for item in refresh_match.group(1).split(",") if item.strip()]
        return ("刷新降级通道：" + "、".join(channels)) if lang == "zh" else ("Refresh degraded channels: " + ", ".join(channels))
    theme_match = re.match(r"^(.+?)\s+narrative, macro, and attention change$", text, re.I)
    if theme_match:
        theme = localize_theme(theme_match.group(1), lang)
        if lang == "zh":
            return f"{theme}：叙事、宏观与注意力变化"
        return f"{theme}: narrative, macro, and attention change"
    if "overnight operating-cycle" in text.lower():
        return "执行隔夜运行周期检查，并更新下一份决策简报" if lang == "zh" else "Apply overnight operating-cycle checks to the next Decision Brief"
    if lang == "zh":
        return "待本地化的研究焦点；原文见专家详情"
    return text


def format_timestamp(value: Any, lang: str = "en", prefix: str | None = None) -> str:
    dt = _parse_datetime(value)
    if dt is None:
        text = "等待信号" if lang == "zh" else "Waiting for signal"
    else:
        local = dt.astimezone(_local_timezone())
        if lang == "zh":
            text = f"{local.year}年{local.month}月{local.day}日 {local.hour:02d}:{local.minute:02d}"
        else:
            text = f"{MONTHS[local.month - 1]} {local.day}, {local.year} {local.hour:02d}:{local.minute:02d}"
    return f"{prefix}：{text}" if prefix and lang == "zh" else f"{prefix}: {text}" if prefix else text


def duration_text(value: Any, lang: str = "en") -> str:
    seconds = _float(value, 0.0)
    if seconds >= 3600:
        hours = seconds / 3600
        return f"{hours:.1f} 小时" if lang == "zh" else f"{hours:.1f}h"
    if seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.0f} 分钟" if lang == "zh" else f"{minutes:.0f}m"
    return f"{seconds:.0f} 秒" if lang == "zh" else f"{seconds:.0f}s"


def _reason_sections(state: Mapping[str, Any], primary: str, secondary: str, lang: str) -> list[dict[str, str]]:
    return [
        {
            "title": "主要驱动" if lang == "zh" else "Primary driver",
            "body": _primary_driver_sentence(primary, secondary, lang),
        },
        {
            "title": "组合影响" if lang == "zh" else "Portfolio impact",
            "body": _portfolio_sentence(_portfolio(state), lang),
        },
        {
            "title": "不确定性" if lang == "zh" else "Uncertainty",
            "body": _uncertainty_sentence(_market(state), lang),
        },
    ]


def _primary_driver_sentence(primary: str, secondary: str, lang: str) -> str:
    primary_label = label_for_concept(primary, lang)["primary"]
    secondary_label = label_for_concept(secondary, lang)["primary"] if secondary else ""
    if lang == "zh":
        if secondary_label:
            return f"当前运行状态主要由{primary_label}主导，{secondary_label}是次要驱动因素。"
        return f"当前运行状态主要由{primary_label}主导。"
    if secondary_label:
        return f"The current runtime state is primarily driven by {primary_label}, with {secondary_label} as the secondary driver."
    return f"The current runtime state is primarily driven by {primary_label}."


def _portfolio_sentence(portfolio: Mapping[str, Any], lang: str) -> str:
    if portfolio.get("status") != "configured":
        return "组合尚未配置，当前简报只反映系统状态。" if lang == "zh" else "Portfolio is not configured, so the brief reflects system state only."
    exposure = _float(portfolio.get("exposure_sum_pct"), 0.0)
    exposure_map = _mapping(portfolio.get("exposure_map"))
    markets = _mapping(exposure_map.get("market_concentration"))
    themes = _mapping(exposure_map.get("theme_concentration"))
    market_names = [localize_market_label(key, lang) for key in list(markets.keys())[:2]]
    theme_names = [localize_theme(key, lang, bilingual=False) for key in list(themes.keys())[:2]]
    if lang == "zh":
        parts = []
        if market_names:
            parts.append("、".join(market_names))
        if theme_names:
            parts.append("、".join(theme_names))
        tail = "与该状态相关" if not parts else f"在{'与'.join(parts)}上有集中暴露"
        return f"组合已配置约 {exposure:.1f}% 暴露，{tail}，因此该状态会影响组合解释。"
    parts = []
    if market_names:
        parts.append(", ".join(market_names))
    if theme_names:
        parts.append(", ".join(theme_names))
    tail = "is relevant to this state" if not parts else f"has concentration in {' and '.join(parts)}"
    return f"The configured portfolio has about {exposure:.1f}% exposure and {tail}, so this state matters for the brief."


def _uncertainty_sentence(market: Mapping[str, Any], lang: str) -> str:
    channels = _mapping(market.get("channels"))
    missing = [localize_channel_name(key, lang) for key, value in channels.items() if str(value).upper() == "NOT_CONFIGURED"]
    failed = [localize_channel_name(key, lang) for key, value in channels.items() if str(value).upper() in {"FAILED", "RATE_LIMITED"}]
    if lang == "zh":
        if missing or failed:
            pieces = []
            if missing:
                pieces.append("未配置：" + "、".join(missing[:4]))
            if failed:
                pieces.append("异常：" + "、".join(failed[:3]))
            return "部分数据通道仍不完整（" + "；".join(pieces) + "），当前判断置信度有限。"
        return "主要数据通道已有信号，但 Atlas 仍会等待更多交叉验证。"
    if missing or failed:
        pieces = []
        if missing:
            pieces.append("not configured: " + ", ".join(missing[:4]))
        if failed:
            pieces.append("degraded: " + ", ".join(failed[:3]))
        return "Some data channels remain incomplete (" + "; ".join(pieces) + "), so confidence is limited."
    return "Core data channels have signal, but Atlas still waits for cross-checking."


def _market_summary(channels: Mapping[str, Any], observations: list[Mapping[str, Any]], lang: str) -> str:
    live = sum(1 for value in channels.values() if str(value).upper() == "LIVE")
    simulated = sum(1 for value in channels.values() if str(value).upper() == "SIMULATED")
    failed = sum(1 for value in channels.values() if str(value).upper() in {"FAILED", "RATE_LIMITED"})
    missing = sum(1 for value in channels.values() if str(value).upper() == "NOT_CONFIGURED")
    available = sum(1 for item in observations if item.get("status_key") in {"Available", "Partial"})
    partial = sum(1 for item in observations if item.get("status_key") == "Partial")
    total = len(observations)
    if lang == "zh":
        parts = [f"价格 {available}/{total} 有信号"] if total else []
        if partial:
            parts.append(f"{partial} 个部分可用")
        parts.append(f"{live} 个实时通道")
        if simulated:
            parts.append(f"{simulated} 个模拟通道")
        if failed:
            parts.append(f"{failed} 个异常通道")
        if missing:
            parts.append(f"{missing} 个未配置")
        return " · ".join(parts)
    parts = [f"Price {available}/{total} with signal"] if total else []
    if partial:
        parts.append(f"{partial} partial")
    parts.append(f"{live} live channels")
    if simulated:
        parts.append(f"{simulated} simulated")
    if failed:
        parts.append(f"{failed} degraded")
    if missing:
        parts.append(f"{missing} not configured")
    return " · ".join(parts)


def _localized_observation(item: Mapping[str, Any], lang: str) -> dict[str, Any]:
    status_key = str(item.get("data_quality_status") or "Unknown")
    market = localize_market_label(item.get("market"), lang)
    asset = str(item.get("asset") or "Unknown")
    source = str(item.get("source") or "")
    source_label = "暂无数据源" if lang == "zh" and source in {"", "none", "None"} else "No source" if source in {"", "none", "None"} else _humanize(source)
    return {
        "asset": asset,
        "market": market,
        "asset_display": f"{asset}（{market}）" if lang == "zh" else f"{asset} ({market})",
        "description": "价格、成交量、流动性与公告更新" if lang == "zh" else "price, volume, liquidity, and announcement freshness",
        "status": localize_status(status_key, lang),
        "status_key": status_key,
        "source": source_label,
        "css": "ok" if status_key == "Available" else "warn" if status_key == "Partial" else "bad",
    }


def _extract_concepts(state: Mapping[str, Any]) -> list[str]:
    packet = _packet(state)
    text = " ".join(str(packet.get(key, "")) for key in ("regime_state", "risk_level", "attention_state", "liquidity_state", "causal_summary", "reasoning_trace"))
    text = f"{text} {state.get('regime_state', '')} {state.get('volatility', '')}"
    concepts = _concepts_from_text(text)
    if _float(state.get("liquidity"), 0.0) <= 1:
        concepts.append("liquidity_stress")
    if str(state.get("regime_state") or "").upper().startswith("RISK_OFF"):
        concepts.append("risk_off")
    output: list[str] = []
    for concept in concepts:
        if concept not in output:
            output.append(concept)
    return output


def _concepts_from_text(text: str) -> list[str]:
    lowered = str(text or "").lower()
    output: list[str] = []
    for concept, keywords in CONCEPT_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            output.append(concept)
    return output


def _primary_concept(concepts: list[str], packet: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    for key in ("liquidity_stress", "liquidity_shock", "risk_off", "volatility_shock", "attention_pressure", "data_insufficient"):
        if key in concepts:
            return key
    regime = str(packet.get("regime_state") or state.get("regime_state") or "").upper()
    if "RISK_OFF" in regime:
        return "risk_off"
    return "market_state_change"


def _secondary_concept(concepts: list[str], primary: str) -> str:
    for key in ("volatility_shock", "volatility_pressure", "data_insufficient", "portfolio_relevance", "attention_pressure", "risk_off"):
        if key in concepts and key != primary:
            return key
    return ""


def _dashboard_graph_factors(state: Mapping[str, Any]) -> list[str]:
    dashboard = _mapping(state.get("dashboard"))
    graph = _mapping(dashboard.get("causal_graph_snapshot"))
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    output: list[str] = []
    for item in edges[:3]:
        if isinstance(item, Mapping):
            label = str(item.get("from") or item.get("source") or item.get("name") or "").strip()
            if label:
                output.append(label)
    return output


def _regime_influence(state: Mapping[str, Any], action: Mapping[str, str], lang: str) -> str:
    regime = label_for_concept("risk_off", lang)["primary"] if str(state.get("regime_state") or "").upper().startswith("RISK_OFF") else label_for_concept("market_state_change", lang)["primary"]
    if lang == "zh":
        return f"{regime} → {action['primary']}"
    return f"{regime} -> {action['primary']}"


def _trust_impact(state: Mapping[str, Any], lang: str) -> str:
    trust = _float(state.get("trust_index"), -1)
    if trust < 0:
        return "信任状态等待信号" if lang == "zh" else "Trust state is waiting for signal"
    if lang == "zh":
        if trust >= 0.7:
            return "高信任度支持当前解释权重"
        if trust >= 0.4:
            return "中等信任度会约束解释强度"
        return "低信任度限制当前解释强度"
    if trust >= 0.7:
        return "High trust supports the explanation weight"
    if trust >= 0.4:
        return "Moderate trust tempers explanation weight"
    return "Low trust limits explanation weight"


def _trust_trend(state: Mapping[str, Any], lang: str) -> str:
    trust = _float(state.get("trust_index"), -1)
    if trust >= 0.7:
        return "信任场稳定" if lang == "zh" else "Stable trust field"
    if trust >= 0.4:
        return "信任场中等" if lang == "zh" else "Moderate trust field"
    if trust >= 0:
        return "信任场偏低" if lang == "zh" else "Low trust field"
    return "等待信任信号" if lang == "zh" else "Waiting for trust signal"


def _stability_label(state: Mapping[str, Any], lang: str) -> str:
    trust = _float(state.get("trust_index"), -1)
    if trust >= 0.7:
        return "稳定" if lang == "zh" else "Stable"
    if trust >= 0.4:
        return "谨慎观察" if lang == "zh" else "Watchful"
    return "系统上下文不足" if lang == "zh" else "Insufficient system context"


def _proactive_subtitle(lang: str) -> str:
    return "Atlas 会按周期读取组合与市场通道，决定下一轮要刷新什么。" if lang == "zh" else "Atlas periodically reads portfolio and channel freshness to decide what to refresh next."


def _dual(labels: Mapping[str, str], lang: str, *, raw: str = "") -> dict[str, str]:
    lang = _safe_lang(lang)
    primary = labels.get(lang) or labels.get("en") or raw
    secondary = labels.get("en", "")
    if lang == "en":
        secondary = ""
    elif secondary == primary:
        secondary = ""
    return {"primary": primary, "secondary": secondary, "raw": raw}


def _packet(state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(state.get("last_decision_packet"))


def _market(state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(state.get("market_intelligence"))


def _portfolio(state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(state.get("portfolio_context"))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _confidence(packet: Mapping[str, Any]) -> str:
    value = _float(packet.get("confidence"), 0.0)
    if value <= 1:
        value *= 100
    return f"{max(0.0, min(100.0, value)):.0f}%"


def _status_css(value: str) -> str:
    status = value.upper()
    if status == "LIVE":
        return "signal-live"
    if status in {"FAILED", "RATE_LIMITED"}:
        return "signal-failed"
    if status in {"SIMULATED", "CACHED", "DELAYED"}:
        return "signal-simulated"
    return ""


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            return None
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _local_timezone() -> timezone:
    try:
        return ZoneInfo("Asia/Shanghai")
    except Exception:
        return datetime.now().astimezone().tzinfo or timezone.utc


def _safe_lang(lang: str) -> str:
    return "zh" if str(lang).lower().startswith("zh") else "en"


def _float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _humanize(value: str) -> str:
    text = str(value or "").replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Unknown"
    return " ".join(word[:1].upper() + word[1:] for word in text.split())
