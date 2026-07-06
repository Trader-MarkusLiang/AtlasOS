"""Tiny EN/CN text system for Atlas UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONFIG_PATH = Path("runtime/config/user_config.json")
SUPPORTED_LANGUAGES = {"en", "zh"}


TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "Cognitive Control Center",
        "app.subtitle": "Guided runtime intelligence",
        "nav.dashboard": "Dashboard",
        "nav.workflow": "Workflow",
        "nav.roadmap": "Roadmap",
        "nav.settings": "Settings",
        "nav.language": "Language",
        "system.control": "System Control",
        "system.start": "Start",
        "system.stop": "Stop",
        "system.tick_interval": "Tick interval",
        "system.simulation_mode": "Simulation mode",
        "model.config": "Model Config",
        "model.active_provider": "Active provider",
        "model.model": "Model",
        "model.health": "Health",
        "model.open_settings": "Open provider settings",
        "asset.config": "Asset Config",
        "asset.editor": "Portfolio / assets JSON",
        "asset.load": "Load",
        "asset.save": "Save Config",
        "workspace.system": "System Mode",
        "workspace.chat": "Chat Mode",
        "workspace.workflow": "Workflow Mode",
        "state.current_regime": "Current System State",
        "state.trust_score": "Trust Score",
        "state.active_decision": "Active Decision",
        "state.confidence": "Confidence",
        "state.risk": "Risk",
        "state.attention": "Attention",
        "state.liquidity": "Liquidity",
        "state.status": "System Status",
        "state.tick": "Tick",
        "state.volatility": "Volatility",
        "empty.signal": "Waiting for cognitive signal",
        "empty.context": "Insufficient system context",
        "empty.initializing": "System initializing reasoning layer",
        "chat.placeholder": "Send a runtime-safe Atlas query",
        "chat.send": "Send",
        "right.reasoning": "Reasoning Summary",
        "right.causal": "Causal Snapshot",
        "right.hypothesis": "Hypothesis State",
        "right.health": "System Health",
        "right.active": "Active",
        "right.shadow": "Shadow",
        "right.trust_trend": "Trust trend",
        "right.stability": "Stability",
        "right.llm_calls": "LLM calls",
        "right.latency": "Latency",
        "timeline.title": "Event -> Decision -> Feedback",
        "timeline.kicker": "Flow Timeline",
        "settings.title": "Atlas Settings",
        "settings.subtitle": "Local provider, system, and asset configuration.",
        "settings.save": "Save Settings",
        "settings.providers": "LLM Providers",
        "settings.add_provider": "Add provider",
        "settings.test": "Test",
        "settings.remove": "Remove",
        "settings.api_key": "API key",
        "settings.base_url": "Base URL",
        "settings.fallback": "Fallback chain",
        "settings.system": "Atlas System Config",
        "settings.assets": "User Assets Config",
        "settings.notice": "Config is local metadata. It does not execute trades or mutate cognition.",
    },
    "zh": {
        "app.title": "认知控制中心",
        "app.subtitle": "实时认知运行界面",
        "nav.dashboard": "仪表盘",
        "nav.workflow": "工作流",
        "nav.roadmap": "路线图",
        "nav.settings": "设置",
        "nav.language": "语言",
        "system.control": "系统控制",
        "system.start": "启动",
        "system.stop": "停止",
        "system.tick_interval": "Tick 间隔",
        "system.simulation_mode": "模拟模式",
        "model.config": "模型配置",
        "model.active_provider": "当前 Provider",
        "model.model": "模型",
        "model.health": "健康状态",
        "model.open_settings": "打开 Provider 设置",
        "asset.config": "资产配置",
        "asset.editor": "组合 / 资产 JSON",
        "asset.load": "加载",
        "asset.save": "保存配置",
        "workspace.system": "系统模式",
        "workspace.chat": "对话模式",
        "workspace.workflow": "工作流模式",
        "state.current_regime": "当前系统状态",
        "state.trust_score": "信任分数",
        "state.active_decision": "当前决策",
        "state.confidence": "置信度",
        "state.risk": "风险",
        "state.attention": "注意力",
        "state.liquidity": "流动性",
        "state.status": "系统状态",
        "state.tick": "Tick",
        "state.volatility": "波动率",
        "empty.signal": "等待足够认知信号",
        "empty.context": "系统上下文不足",
        "empty.initializing": "正在初始化推理层",
        "chat.placeholder": "发送安全的 Atlas 运行时问题",
        "chat.send": "发送",
        "right.reasoning": "推理摘要",
        "right.causal": "因果快照",
        "right.hypothesis": "假设状态",
        "right.health": "系统健康",
        "right.active": "当前",
        "right.shadow": "影子假设",
        "right.trust_trend": "信任趋势",
        "right.stability": "稳定性",
        "right.llm_calls": "LLM 调用",
        "right.latency": "延迟",
        "timeline.title": "事件 -> 决策 -> 反馈",
        "timeline.kicker": "执行时间线",
        "settings.title": "Atlas 设置",
        "settings.subtitle": "本地 Provider、系统与资产配置。",
        "settings.save": "保存设置",
        "settings.providers": "LLM Providers",
        "settings.add_provider": "添加 Provider",
        "settings.test": "测试",
        "settings.remove": "删除",
        "settings.api_key": "API Key",
        "settings.base_url": "Base URL",
        "settings.fallback": "Fallback 顺序",
        "settings.system": "Atlas 系统配置",
        "settings.assets": "用户资产配置",
        "settings.notice": "配置仅为本地元数据，不执行交易，也不修改认知核心。",
    },
}


def current_language(path: str | None = None) -> str:
    data = _load_config(path)
    lang = str(data.get("ui", {}).get("language") or data.get("language") or "en").lower()
    return lang if lang in SUPPORTED_LANGUAGES else "en"


def set_language(language: str, path: str | None = None) -> dict[str, str]:
    lang = language.lower() if language.lower() in SUPPORTED_LANGUAGES else "en"
    target = Path(path) if path else CONFIG_PATH
    data = _load_config(path)
    ui = data.get("ui") if isinstance(data.get("ui"), dict) else {}
    ui["language"] = lang
    data["ui"] = ui
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "saved", "language": lang}


def t(key: str, lang: str | None = None) -> str:
    language = lang or current_language()
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))


def translation_payload(lang: str | None = None) -> dict[str, Any]:
    language = lang or current_language()
    return {"language": language, "strings": TRANSLATIONS.get(language, TRANSLATIONS["en"])}


def _load_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}

