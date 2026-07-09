"""Interactive cognitive flow map for the Atlas Workflow page."""

from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping

from ui.components.workflow_inspector import render_workflow_inspector


TEXT = {
    "en": {
        "summary_title": "How Atlas turns information into judgment",
        "summary": (
            "Data enters the input layer, moves through event fusion, causal understanding, "
            "and the world model, then forms forecasts and a Decision Brief. Reality returns "
            "through feedback to update trust, hypothesis weight, and future judgment."
        ),
        "simple": "Simple",
        "expert": "Expert",
        "latest": "Latest Tick",
        "full": "Full Architecture",
        "zoom_in": "Zoom In",
        "zoom_out": "Zoom Out",
        "fit": "Fit View",
        "reset": "Reset Selection",
        "legend": "Legend",
        "active_path": "Current active path",
        "completed": "Completed path",
        "degraded": "Degraded",
        "failed": "Failed",
        "feedback": "Feedback loop",
        "support": "Support system",
        "support_title": "Secondary support systems",
        "feedback_loop": "Reality and forecast error return to Memory / World Model",
        "status_active": "ACTIVE",
        "status_completed": "COMPLETED",
        "status_waiting": "WAITING",
        "status_degraded": "DEGRADED",
        "status_failed": "FAILED",
        "status_not_used": "NOT_USED",
        "tick_unknown": "No active tick yet",
        "trust_unknown": "Trust unavailable",
    },
    "zh": {
        "summary_title": "Atlas 如何把信息变成判断",
        "summary": (
            "数据首先进入输入层，经过事件融合、因果理解和世界模型，形成预测与决策简报。"
            "现实结果随后进入反馈层，更新信任、假设权重和未来判断。"
        ),
        "simple": "简洁视图",
        "expert": "专家视图",
        "latest": "最近一次 Tick",
        "full": "完整架构",
        "zoom_in": "放大",
        "zoom_out": "缩小",
        "fit": "适配视图",
        "reset": "重置选择",
        "legend": "图例",
        "active_path": "当前活跃路径",
        "completed": "已完成路径",
        "degraded": "降级",
        "failed": "失败",
        "feedback": "反馈回路",
        "support": "支撑系统",
        "support_title": "次级支撑系统",
        "feedback_loop": "现实与预测误差回流到记忆 / 世界模型",
        "status_active": "ACTIVE",
        "status_completed": "COMPLETED",
        "status_waiting": "WAITING",
        "status_degraded": "DEGRADED",
        "status_failed": "FAILED",
        "status_not_used": "NOT_USED",
        "tick_unknown": "暂无活跃 Tick",
        "trust_unknown": "信任数据不足",
    },
}


STAGES = [
    ("input", "01", {"en": "Input", "zh": "输入"}, {"en": "Where signals enter", "zh": "信息进入的位置"}),
    ("understand", "02", {"en": "Understand", "zh": "理解"}, {"en": "Turn events into context", "zh": "把事件转成上下文"}),
    ("model", "03", {"en": "Model", "zh": "建模"}, {"en": "Represent market structure", "zh": "表示市场结构"}),
    ("decide", "04", {"en": "Decide", "zh": "决策"}, {"en": "Produce safe outputs", "zh": "形成安全输出"}),
    ("learn", "05", {"en": "Learn", "zh": "学习反馈"}, {"en": "Feed reality back", "zh": "让现实回流修正"}),
]


NODES = [
    {
        "key": "external_information",
        "stage": "input",
        "kind": "primary",
        "label": {"en": "External Information", "zh": "外部信息"},
        "purpose": {"en": "Collects market, news, user, and system input at the UI/runtime boundary.", "zh": "在 UI / 运行时边界接收市场、新闻、用户与系统输入。"},
        "inputs": {"en": ["User query", "market events", "provider state"], "zh": ["用户问题", "市场事件", "Provider 状态"]},
        "outputs": {"en": ["raw runtime-safe input"], "zh": ["运行时安全的原始输入"]},
        "affects": ["input_router"],
        "brief": {"en": "Defines what Atlas is allowed to consider.", "zh": "决定 Atlas 可以纳入判断的信息范围。"},
    },
    {
        "key": "market_data",
        "stage": "input",
        "kind": "support",
        "label": {"en": "Market Data", "zh": "市场数据"},
        "purpose": {"en": "Provides price, volume, volatility, and freshness observations.", "zh": "提供价格、成交量、波动和新鲜度观察。"},
        "inputs": {"en": ["configured assets", "market providers"], "zh": ["已配置资产", "市场数据源"]},
        "outputs": {"en": ["normalized market observations"], "zh": ["标准化市场观察"]},
        "affects": ["input_router", "forecast"],
        "brief": {"en": "Limits or strengthens market context in the brief.", "zh": "增强或限制简报中的市场上下文。"},
    },
    {
        "key": "portfolio_context",
        "stage": "input",
        "kind": "support",
        "label": {"en": "Portfolio Context", "zh": "组合上下文"},
        "purpose": {"en": "Adds read-only asset, theme, and exposure relevance.", "zh": "加入只读的资产、主题和暴露相关性。"},
        "inputs": {"en": ["local user config", "percentage exposure"], "zh": ["本地用户配置", "百分比暴露"]},
        "outputs": {"en": ["portfolio relevance"], "zh": ["组合相关性"]},
        "affects": ["input_router", "decision_brief"],
        "brief": {"en": "Makes the brief specific to the user's configured context without trading.", "zh": "让简报贴合用户配置，但不执行交易。"},
    },
    {
        "key": "user_context",
        "stage": "input",
        "kind": "support",
        "label": {"en": "User Context", "zh": "用户上下文"},
        "purpose": {"en": "Carries safe questions and configuration preferences.", "zh": "承载安全问题和配置偏好。"},
        "inputs": {"en": ["Ask Atlas inbox", "UI settings"], "zh": ["Ask Atlas 收件箱", "UI 设置"]},
        "outputs": {"en": ["user event"], "zh": ["用户事件"]},
        "affects": ["event_stream"],
        "brief": {"en": "Shapes what the next tick should explain.", "zh": "影响下一次 tick 应解释什么。"},
    },
    {
        "key": "provider_context",
        "stage": "input",
        "kind": "support",
        "label": {"en": "Provider Context", "zh": "Provider 上下文"},
        "purpose": {"en": "Provides current LLM provider, model, health, and latency state.", "zh": "提供当前 LLM Provider、模型、健康和延迟状态。"},
        "inputs": {"en": ["provider registry", "health checks"], "zh": ["Provider 注册表", "健康检查"]},
        "outputs": {"en": ["provider availability"], "zh": ["Provider 可用性"]},
        "affects": ["llm_router"],
        "brief": {"en": "Determines whether LLM reasoning is available or degraded.", "zh": "决定 LLM 推理是否可用或降级。"},
    },
    {
        "key": "input_router",
        "stage": "understand",
        "kind": "primary",
        "label": {"en": "Input Router", "zh": "输入路由"},
        "purpose": {"en": "Routes safe events into the runtime path without changing cognition.", "zh": "把安全事件路由到运行路径，不改变认知语义。"},
        "inputs": {"en": ["external information", "market data", "user context"], "zh": ["外部信息", "市场数据", "用户上下文"]},
        "outputs": {"en": ["typed event"], "zh": ["类型化事件"]},
        "affects": ["event_stream"],
        "brief": {"en": "Keeps the brief grounded in validated inputs.", "zh": "让简报只基于已验证输入。"},
    },
    {
        "key": "event_stream",
        "stage": "understand",
        "kind": "primary",
        "label": {"en": "Event Stream", "zh": "事件流"},
        "purpose": {"en": "Queues each tick's normalized events.", "zh": "排队每次 tick 的标准化事件。"},
        "inputs": {"en": ["typed event"], "zh": ["类型化事件"]},
        "outputs": {"en": ["runtime event batch"], "zh": ["运行时事件批次"]},
        "affects": ["event_fusion"],
        "brief": {"en": "Defines what the latest tick actually processed.", "zh": "说明最近一次 tick 实际处理了什么。"},
    },
    {
        "key": "event_fusion",
        "stage": "understand",
        "kind": "primary",
        "label": {"en": "Event Fusion", "zh": "事件融合"},
        "purpose": {"en": "Combines multiple event types into a coherent observation frame.", "zh": "把多类事件融合成一致的观察框架。"},
        "inputs": {"en": ["runtime event batch"], "zh": ["运行时事件批次"]},
        "outputs": {"en": ["fused observation state"], "zh": ["融合后的观察状态"]},
        "affects": ["memory", "causal_inference"],
        "brief": {"en": "Prevents one raw signal from dominating the brief.", "zh": "避免单个原始信号主导简报。"},
    },
    {
        "key": "memory",
        "stage": "understand",
        "kind": "primary",
        "label": {"en": "Memory", "zh": "记忆"},
        "acronym": {"en": "Regime Memory", "zh": "Regime Memory"},
        "purpose": {"en": "Provides recent regime and feedback context.", "zh": "提供近期状态与反馈上下文。"},
        "inputs": {"en": ["fused observations", "feedback loop"], "zh": ["融合观察", "反馈回路"]},
        "outputs": {"en": ["memory context"], "zh": ["记忆上下文"]},
        "affects": ["causal_inference", "world_model"],
        "brief": {"en": "Connects this tick to prior state.", "zh": "把当前 tick 与历史状态连接起来。"},
    },
    {
        "key": "causal_inference",
        "stage": "understand",
        "kind": "primary",
        "label": {"en": "Causal Inference", "zh": "因果理解"},
        "acronym": {"en": "CIL", "zh": "CIL"},
        "purpose": {"en": "Identifies plausible causal drivers behind observed changes.", "zh": "识别观察变化背后的可能因果驱动。"},
        "inputs": {"en": ["fused events", "memory context", "market state"], "zh": ["融合事件", "记忆上下文", "市场状态"]},
        "outputs": {"en": ["causal candidates", "ranked explanations"], "zh": ["因果候选", "排序解释"]},
        "affects": ["world_model", "hypothesis", "forecast"],
        "brief": {"en": "Explains why Atlas reaches a decision posture.", "zh": "解释 Atlas 为什么形成当前判断姿态。"},
    },
    {
        "key": "world_model",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "World Model", "zh": "世界模型"},
        "purpose": {"en": "Maintains the interpretable market representation.", "zh": "维护可解释的市场表征。"},
        "inputs": {"en": ["memory context", "causal candidates"], "zh": ["记忆上下文", "因果候选"]},
        "outputs": {"en": ["market representation"], "zh": ["市场表征"]},
        "affects": ["hypothesis", "forecast", "decision_contract"],
        "brief": {"en": "Sets the structural context for forecasts and decisions.", "zh": "为预测和决策设置结构性上下文。"},
    },
    {
        "key": "lmse",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "Market Meaning", "zh": "市场语义"},
        "acronym": {"en": "LMSE", "zh": "LMSE"},
        "purpose": {"en": "Extracts latent market meaning from observed structure.", "zh": "从观察结构中提取隐含市场语义。"},
        "inputs": {"en": ["world model", "market observations"], "zh": ["世界模型", "市场观察"]},
        "outputs": {"en": ["latent structure summary"], "zh": ["隐含结构摘要"]},
        "affects": ["hypothesis", "mpce"],
        "brief": {"en": "Improves explanation without becoming a signal engine.", "zh": "增强解释能力，但不变成信号引擎。"},
    },
    {
        "key": "mpce",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "Causal Prediction", "zh": "因果预测"},
        "acronym": {"en": "MPCE", "zh": "MPCE"},
        "purpose": {"en": "Checks predictive causal constraints and violations.", "zh": "检查因果预测约束与违反情况。"},
        "inputs": {"en": ["market meaning", "constraint state"], "zh": ["市场语义", "约束状态"]},
        "outputs": {"en": ["constraint violations"], "zh": ["约束违反"]},
        "affects": ["mle", "forecast"],
        "brief": {"en": "Flags when explanations are structurally weak.", "zh": "标记解释何时结构较弱。"},
    },
    {
        "key": "mle",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "Learning Engine", "zh": "学习引擎"},
        "acronym": {"en": "MLE", "zh": "MLE"},
        "purpose": {"en": "Tracks emergent law candidates from repeated structure.", "zh": "跟踪重复结构中浮现的规律候选。"},
        "inputs": {"en": ["constraint violations", "repeated patterns"], "zh": ["约束违反", "重复模式"]},
        "outputs": {"en": ["law state summary"], "zh": ["规律状态摘要"]},
        "affects": ["umis", "hypothesis"],
        "brief": {"en": "Shows whether Atlas is learning durable structure.", "zh": "说明 Atlas 是否在学习可复用结构。"},
    },
    {
        "key": "umis",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "Uncertainty Model", "zh": "不确定性模型"},
        "acronym": {"en": "UMIS", "zh": "UMIS"},
        "purpose": {"en": "Models uncertainty before output is turned into a brief.", "zh": "在输出变成简报前建模不确定性。"},
        "inputs": {"en": ["law state", "hypotheses", "trust"], "zh": ["规律状态", "假设", "信任"]},
        "outputs": {"en": ["uncertainty context"], "zh": ["不确定性上下文"]},
        "affects": ["decision_contract"],
        "brief": {"en": "Prevents confidence from being mistaken for certainty.", "zh": "防止把置信度误认为确定性。"},
    },
    {
        "key": "hypothesis",
        "stage": "model",
        "kind": "primary",
        "label": {"en": "Hypothesis", "zh": "因果假设"},
        "purpose": {"en": "Keeps competing explanations instead of one forced truth.", "zh": "保留竞争解释，而不是强行合并成单一真相。"},
        "inputs": {"en": ["world model", "learning engine", "feedback"], "zh": ["世界模型", "学习引擎", "反馈"]},
        "outputs": {"en": ["active and shadow hypotheses"], "zh": ["活跃与影子假设"]},
        "affects": ["forecast", "decision_contract"],
        "brief": {"en": "Makes the brief explainable under model plurality.", "zh": "让简报在多模型下仍可解释。"},
    },
    {
        "key": "forecast",
        "stage": "decide",
        "kind": "primary",
        "label": {"en": "Forecast", "zh": "预测记录"},
        "purpose": {"en": "Records non-binding expectations before outcomes are known.", "zh": "在结果出现前记录非约束性预期。"},
        "inputs": {"en": ["hypothesis", "market context"], "zh": ["因果假设", "市场上下文"]},
        "outputs": {"en": ["forecast ledger entry"], "zh": ["预测账本记录"]},
        "affects": ["decision_contract", "forecast_evaluation"],
        "brief": {"en": "Creates accountability without trading authority.", "zh": "提供问责，而不产生交易权限。"},
    },
    {
        "key": "decision_contract",
        "stage": "decide",
        "kind": "primary",
        "label": {"en": "Decision Contract", "zh": "决策契约"},
        "purpose": {"en": "Validates output into a strict, interpretable packet.", "zh": "把输出验证成严格、可解释的数据包。"},
        "inputs": {"en": ["uncertainty context", "forecast", "hypothesis"], "zh": ["不确定性上下文", "预测", "假设"]},
        "outputs": {"en": ["DecisionPacket"], "zh": ["DecisionPacket"]},
        "affects": ["llm_router", "decision_brief"],
        "brief": {"en": "Keeps the system from becoming unstructured LLM output.", "zh": "防止系统变成非结构化 LLM 输出。"},
    },
    {
        "key": "cde_decision_layer",
        "stage": "decide",
        "kind": "primary",
        "label": {"en": "Decision Layer", "zh": "决策层"},
        "acronym": {"en": "CDE", "zh": "CDE"},
        "purpose": {"en": "Represents read-only decision authority boundaries.", "zh": "表示只读决策权限边界。"},
        "inputs": {"en": ["DecisionPacket", "portfolio context"], "zh": ["DecisionPacket", "组合上下文"]},
        "outputs": {"en": ["action boundary", "decision posture"], "zh": ["行动边界", "决策姿态"]},
        "affects": ["decision_brief"],
        "brief": {"en": "Prevents brief language from bypassing Atlas authority rules.", "zh": "防止简报绕过 Atlas 权限规则。"},
    },
    {
        "key": "llm_router",
        "stage": "decide",
        "kind": "support",
        "label": {"en": "LLM Router", "zh": "LLM 路由"},
        "purpose": {"en": "Routes reasoning to the configured provider behind a safe adapter.", "zh": "通过安全适配器把推理路由到配置 Provider。"},
        "inputs": {"en": ["validated packet", "provider context"], "zh": ["已验证数据包", "Provider 上下文"]},
        "outputs": {"en": ["raw reasoning text"], "zh": ["原始推理文本"]},
        "affects": ["decision_brief", "feedback"],
        "brief": {"en": "Adds reasoning without directly mutating cognition.", "zh": "增加推理，但不直接修改认知。"},
    },
    {
        "key": "decision_brief",
        "stage": "decide",
        "kind": "output",
        "label": {"en": "Decision Brief", "zh": "决策简报"},
        "purpose": {"en": "Presents the primary user-facing cognitive output.", "zh": "呈现面向用户的核心认知输出。"},
        "inputs": {"en": ["DecisionPacket", "reasoning", "portfolio context"], "zh": ["DecisionPacket", "推理", "组合上下文"]},
        "outputs": {"en": ["brief", "watch conditions", "risk posture"], "zh": ["简报", "观察条件", "风险姿态"]},
        "affects": ["feedback", "user_context"],
        "brief": {"en": "This is the main output the user should read first.", "zh": "这是用户最先应该阅读的核心输出。"},
    },
    {
        "key": "reality_outcome",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Reality / Outcome", "zh": "现实 / 结果"},
        "purpose": {"en": "Represents later observed outcomes after a forecast or brief.", "zh": "表示预测或简报之后观察到的后续结果。"},
        "inputs": {"en": ["market outcome", "fresh observations"], "zh": ["市场结果", "新观察"]},
        "outputs": {"en": ["outcome evidence"], "zh": ["结果证据"]},
        "affects": ["forecast_evaluation"],
        "brief": {"en": "Separates expectation from later reality.", "zh": "把预期与后续现实分开。"},
    },
    {
        "key": "forecast_evaluation",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Forecast Evaluation", "zh": "预测评估"},
        "purpose": {"en": "Computes forecast error and calibration when outcomes mature.", "zh": "当结果成熟时计算预测误差和校准。"},
        "inputs": {"en": ["forecast ledger", "outcome evidence"], "zh": ["预测账本", "结果证据"]},
        "outputs": {"en": ["error", "calibration"], "zh": ["误差", "校准"]},
        "affects": ["feedback", "trust_update"],
        "brief": {"en": "Makes learning accountable instead of decorative.", "zh": "让学习有问责，而不是装饰。"},
    },
    {
        "key": "feedback",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Feedback", "zh": "反馈"},
        "purpose": {"en": "Feeds bounded error and reasoning deltas back into future context.", "zh": "把有边界的误差和推理变化回流到未来上下文。"},
        "inputs": {"en": ["evaluation", "Decision Brief", "LLM reasoning"], "zh": ["评估", "决策简报", "LLM 推理"]},
        "outputs": {"en": ["bounded update signal"], "zh": ["有边界的更新信号"]},
        "affects": ["trust_update", "memory", "world_model"],
        "brief": {"en": "Explains how the system can change later behavior.", "zh": "解释系统如何改变后续行为。"},
    },
    {
        "key": "trust_update",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Trust Update", "zh": "信任更新"},
        "purpose": {"en": "Updates reliability metadata without overriding cognition.", "zh": "更新可靠性元数据，但不覆盖认知。"},
        "inputs": {"en": ["feedback", "stability", "provider reliability"], "zh": ["反馈", "稳定性", "Provider 可靠性"]},
        "outputs": {"en": ["trust index"], "zh": ["信任指数"]},
        "affects": ["hypothesis_reweight", "memory"],
        "brief": {"en": "Modulates how strongly future signals are trusted.", "zh": "调节未来信号被信任的强度。"},
    },
    {
        "key": "hypothesis_reweight",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Hypothesis Reweight", "zh": "假设重加权"},
        "purpose": {"en": "Adjusts active and shadow causal hypotheses over time.", "zh": "随时间调整活跃和影子因果假设。"},
        "inputs": {"en": ["trust update", "forecast error"], "zh": ["信任更新", "预测误差"]},
        "outputs": {"en": ["hypothesis ranking delta"], "zh": ["假设排序变化"]},
        "affects": ["hypothesis", "self_iteration"],
        "brief": {"en": "Shows why Atlas may explain similar events differently later.", "zh": "说明 Atlas 以后为什么可能不同地解释类似事件。"},
    },
    {
        "key": "self_iteration",
        "stage": "learn",
        "kind": "primary",
        "label": {"en": "Self-Iteration", "zh": "自我迭代"},
        "purpose": {"en": "Closes the behavioral loop into future memory and world modeling.", "zh": "把行为回路闭合到未来记忆和世界建模中。"},
        "inputs": {"en": ["hypothesis reweight", "trust update"], "zh": ["假设重加权", "信任更新"]},
        "outputs": {"en": ["future context adjustment"], "zh": ["未来上下文调整"]},
        "affects": ["memory", "world_model"],
        "brief": {"en": "Makes Atlas a learning runtime rather than a static report.", "zh": "让 Atlas 成为学习运行时，而不是静态报告。"},
    },
    {
        "key": "state_store",
        "stage": "support",
        "kind": "support",
        "label": {"en": "State Store", "zh": "状态存储"},
        "purpose": {"en": "Persists runtime state for the UI and later ticks.", "zh": "为 UI 和后续 tick 持久化运行状态。"},
        "inputs": {"en": ["runtime outputs"], "zh": ["运行时输出"]},
        "outputs": {"en": ["state snapshots"], "zh": ["状态快照"]},
        "affects": ["decision_brief"],
        "brief": {"en": "Allows Home and Workflow to show current runtime state.", "zh": "让首页和 Workflow 展示当前运行状态。"},
    },
    {
        "key": "forecast_ledger",
        "stage": "support",
        "kind": "support",
        "label": {"en": "Forecast Ledger", "zh": "预测账本"},
        "purpose": {"en": "Stores forecast lifecycle and accountability records.", "zh": "存储预测生命周期和问责记录。"},
        "inputs": {"en": ["forecast", "outcome"], "zh": ["预测", "结果"]},
        "outputs": {"en": ["ledger rows"], "zh": ["账本记录"]},
        "affects": ["forecast_evaluation"],
        "brief": {"en": "Keeps prediction accountability visible.", "zh": "让预测问责可见。"},
    },
    {
        "key": "telemetry",
        "stage": "support",
        "kind": "support",
        "label": {"en": "Telemetry", "zh": "遥测"},
        "purpose": {"en": "Records decision, LLM, and state traces for replay.", "zh": "记录决策、LLM 和状态轨迹用于回放。"},
        "inputs": {"en": ["tick outputs"], "zh": ["tick 输出"]},
        "outputs": {"en": ["trace logs"], "zh": ["轨迹日志"]},
        "affects": ["feedback"],
        "brief": {"en": "Makes the workflow auditable.", "zh": "让 workflow 可审计。"},
    },
    {
        "key": "cache",
        "stage": "support",
        "kind": "support",
        "label": {"en": "Cache", "zh": "缓存"},
        "purpose": {"en": "Holds short-lived runtime data without becoming durable knowledge.", "zh": "保存短期运行数据，但不成为长期知识。"},
        "inputs": {"en": ["runtime data"], "zh": ["运行时数据"]},
        "outputs": {"en": ["cached context"], "zh": ["缓存上下文"]},
        "affects": ["input_router"],
        "brief": {"en": "Improves runtime continuity when available.", "zh": "在可用时提升运行连续性。"},
    },
]


EDGES = [
    ("external_information", "input_router"),
    ("market_data", "input_router"),
    ("portfolio_context", "input_router"),
    ("user_context", "event_stream"),
    ("provider_context", "llm_router"),
    ("input_router", "event_stream"),
    ("event_stream", "event_fusion"),
    ("event_fusion", "memory"),
    ("event_fusion", "causal_inference"),
    ("memory", "causal_inference"),
    ("causal_inference", "world_model"),
    ("world_model", "lmse"),
    ("lmse", "mpce"),
    ("mpce", "mle"),
    ("mle", "umis"),
    ("world_model", "hypothesis"),
    ("umis", "decision_contract"),
    ("hypothesis", "forecast"),
    ("forecast", "decision_contract"),
    ("decision_contract", "cde_decision_layer"),
    ("decision_contract", "llm_router"),
    ("llm_router", "decision_brief"),
    ("cde_decision_layer", "decision_brief"),
    ("decision_brief", "feedback"),
    ("forecast", "forecast_ledger"),
    ("forecast_ledger", "forecast_evaluation"),
    ("reality_outcome", "forecast_evaluation"),
    ("forecast_evaluation", "feedback"),
    ("feedback", "trust_update"),
    ("trust_update", "hypothesis_reweight"),
    ("hypothesis_reweight", "self_iteration"),
    ("self_iteration", "memory"),
    ("self_iteration", "world_model"),
    ("state_store", "decision_brief"),
    ("telemetry", "feedback"),
    ("cache", "input_router"),
]


LATEST_PATH = {
    "external_information",
    "market_data",
    "portfolio_context",
    "user_context",
    "provider_context",
    "input_router",
    "event_stream",
    "event_fusion",
    "memory",
    "causal_inference",
    "world_model",
    "lmse",
    "mpce",
    "mle",
    "umis",
    "hypothesis",
    "forecast",
    "decision_contract",
    "cde_decision_layer",
    "llm_router",
    "decision_brief",
    "feedback",
    "trust_update",
    "hypothesis_reweight",
    "self_iteration",
}


def render_cognitive_flow_map(state: Mapping[str, Any], lang: str) -> tuple[str, str]:
    """Render the interactive Workflow Map v2 and its page script."""

    language = lang if lang in TEXT else "en"
    text = TEXT[language]
    statuses = _node_statuses(state)
    nodes = _localized_nodes(language, statuses, state)
    node_by_key = {str(node["key"]): node for node in nodes}
    default_node = node_by_key.get(_default_node(statuses), node_by_key["input_router"])
    html = f"""
    <section class="flow-summary-card">
      <span class="kicker">{escape(text["summary_title"])}</span>
      <p>{escape(text["summary"])}</p>
    </section>
    <section class="cognitive-flow-shell" data-cognitive-flow data-flow-mode="simple" data-architecture-mode="latest" data-selected-node="">
      {_toolbar(text)}
      <div class="flow-workspace">
        <div class="flow-map-viewport">
          <div class="flow-stage-grid" data-flow-canvas>
            {_stage_columns(nodes, language)}
          </div>
          {_feedback_loop(text)}
          {_support_shelf(nodes, text)}
        </div>
        {render_workflow_inspector(default_node, language)}
      </div>
      {_legend(text)}
    </section>
    """
    script = _script(nodes, language, default_node["key"])
    return html, script


def _toolbar(text: Mapping[str, str]) -> str:
    return f"""
      <div class="flow-toolbar" aria-label="Workflow map controls">
        <div class="segmented-control" role="group" aria-label="Map detail mode">
          <button type="button" data-flow-mode-control="simple" aria-pressed="true">{escape(text["simple"])}</button>
          <button type="button" data-flow-mode-control="expert" aria-pressed="false">{escape(text["expert"])}</button>
        </div>
        <div class="segmented-control" role="group" aria-label="Architecture scope">
          <button type="button" data-architecture-mode-control="latest" aria-pressed="true">{escape(text["latest"])}</button>
          <button type="button" data-architecture-mode-control="full" aria-pressed="false">{escape(text["full"])}</button>
        </div>
        <div class="flow-zoom-controls" role="group" aria-label="Map zoom controls">
          <button type="button" data-flow-zoom="in">{escape(text["zoom_in"])}</button>
          <button type="button" data-flow-zoom="out">{escape(text["zoom_out"])}</button>
          <button type="button" data-flow-zoom="fit">{escape(text["fit"])}</button>
          <button type="button" data-flow-reset>{escape(text["reset"])}</button>
        </div>
      </div>
    """


def _stage_columns(nodes: list[dict[str, Any]], lang: str) -> str:
    stage_html = []
    for key, number, labels, descriptions in STAGES:
        stage_nodes = [node for node in nodes if node["stage"] == key]
        cards = "".join(_node_card(node) for node in stage_nodes)
        stage_html.append(
            f"""
            <section class="flow-stage flow-stage-{escape(key)}" data-flow-stage="{escape(key)}">
              <header class="flow-stage-header">
                <span>{escape(number)}</span>
                <div>
                  <h3>{escape(labels[lang])}</h3>
                  <p>{escape(descriptions[lang])}</p>
                </div>
              </header>
              <div class="flow-node-list">{cards}</div>
            </section>
            """
        )
    return "".join(stage_html)


def _node_card(node: Mapping[str, Any]) -> str:
    acronym = str(node.get("acronym") or "")
    acronym_html = f'<span class="flow-node-acronym">{escape(acronym)}</span>' if acronym else ""
    classes = [
        "flow-node",
        f"flow-node-{node['kind']}",
        f"status-{node['status']}",
        "current-path" if node.get("current_path") else "not-current-path",
        "expert-node" if node.get("expert_focus") else "concept-node",
    ]
    tooltip = f"{node['label']} — {node['purpose']} — {node['status_label']}"
    return f"""
      <button type="button"
        class="{' '.join(classes)}"
        data-flow-node="{escape(str(node['key']))}"
        data-stage="{escape(str(node['stage']))}"
        data-node-kind="{escape(str(node['kind']))}"
        data-status="{escape(str(node['status']))}"
        aria-pressed="false"
        title="{escape(tooltip)}">
        <span class="flow-node-status" aria-hidden="true"></span>
        <span class="flow-node-main">
          <strong>{escape(str(node['label']))}</strong>
          {acronym_html}
        </span>
        <span class="flow-tooltip" role="tooltip">{escape(tooltip)}</span>
      </button>
    """


def _feedback_loop(text: Mapping[str, str]) -> str:
    return f"""
      <div class="feedback-loop-strip" data-feedback-loop>
        <span>{escape(text["feedback"])}</span>
        <strong>{escape(text["feedback_loop"])}</strong>
      </div>
    """


def _support_shelf(nodes: list[dict[str, Any]], text: Mapping[str, str]) -> str:
    support = [node for node in nodes if node["stage"] == "support"]
    return f"""
      <section class="support-shelf" data-support-systems>
        <span class="kicker">{escape(text["support_title"])}</span>
        <div class="support-node-row">{''.join(_node_card(node) for node in support)}</div>
      </section>
    """


def _legend(text: Mapping[str, str]) -> str:
    items = [
        ("active", text["active_path"]),
        ("completed", text["completed"]),
        ("degraded", text["degraded"]),
        ("failed", text["failed"]),
        ("feedback", text["feedback"]),
        ("support", text["support"]),
    ]
    return f"""
      <div class="flow-legend" data-flow-legend>
        <span class="kicker">{escape(text["legend"])}</span>
        {''.join(f'<span class="legend-item legend-{key}"><i></i>{escape(label)}</span>' for key, label in items)}
      </div>
    """


def _script(nodes: list[dict[str, Any]], lang: str, default_node: str) -> str:
    payload = {
        "nodes": {str(node["key"]): node for node in nodes},
        "edges": EDGES,
        "defaultNode": default_node,
        "lang": lang,
    }
    return f"""
    <script>
    (function () {{
      const payload = {json.dumps(payload, ensure_ascii=False)};
      const root = document.querySelector("[data-cognitive-flow]");
      if (!root) return;
      const nodes = payload.nodes;
      const edges = payload.edges;
      const forward = Object.create(null);
      const backward = Object.create(null);
      edges.forEach(function (edge) {{
        const from = edge[0], to = edge[1];
        (forward[from] || (forward[from] = [])).push(to);
        (backward[to] || (backward[to] = [])).push(from);
      }});
      let zoom = 1;

      function stored(name, fallback) {{
        try {{ return localStorage.getItem(name) || fallback; }} catch (error) {{ return fallback; }}
      }}
      function persist(name, value) {{
        try {{ localStorage.setItem(name, value); }} catch (error) {{}}
      }}
      function walk(map, start) {{
        const seen = new Set();
        const stack = (map[start] || []).slice();
        while (stack.length) {{
          const item = stack.pop();
          if (!item || seen.has(item)) continue;
          seen.add(item);
          (map[item] || []).forEach(function (next) {{ stack.push(next); }});
        }}
        return seen;
      }}
      function setPressed(selector, value) {{
        root.querySelectorAll(selector).forEach(function (button) {{
          button.setAttribute("aria-pressed", button.getAttribute(selector.includes("architecture") ? "data-architecture-mode-control" : "data-flow-mode-control") === value ? "true" : "false");
        }});
      }}
      function applyMode(mode) {{
        const safe = mode === "expert" ? "expert" : "simple";
        root.dataset.flowMode = safe;
        setPressed("[data-flow-mode-control]", safe);
        persist("atlas.workflow.flowMode", safe);
      }}
      function applyArchitecture(mode) {{
        const safe = mode === "full" ? "full" : "latest";
        root.dataset.architectureMode = safe;
        setPressed("[data-architecture-mode-control]", safe);
        persist("atlas.workflow.architectureMode", safe);
      }}
      function listHtml(items) {{
        return (Array.isArray(items) && items.length ? items : ["Unknown"]).map(function (item) {{
          return "<li>" + String(item).replace(/[&<>]/g, function (ch) {{ return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;" }}[ch]; }}) + "</li>";
        }}).join("");
      }}
      function text(selector, value) {{
        const el = root.querySelector(selector);
        if (el) el.textContent = value || "Unknown";
      }}
      function html(selector, value) {{
        const el = root.querySelector(selector);
        if (el) el.innerHTML = value || "<li>Unknown</li>";
      }}
      function updateInspector(key) {{
        const node = nodes[key];
        if (!node) return;
        text("[data-inspector-title]", node.label);
        text("[data-inspector-subtitle]", node.acronym ? node.label + " · " + node.acronym : node.label);
        text("[data-inspector-purpose]", node.purpose);
        html("[data-inspector-inputs]", listHtml(node.inputs));
        html("[data-inspector-outputs]", listHtml(node.outputs));
        text("[data-inspector-status]", node.status_text);
        text("[data-inspector-tick]", node.last_tick_text);
        text("[data-inspector-trust]", node.trust_text);
        html("[data-inspector-affects]", listHtml(node.affects_labels));
        text("[data-inspector-brief]", node.brief_impact);
        text("[data-inspector-technical]", node.technical);
      }}
      function selectNode(key) {{
        if (!nodes[key]) return;
        const upstream = walk(backward, key);
        const downstream = walk(forward, key);
        root.dataset.selectedNode = key;
        root.querySelectorAll("[data-flow-node]").forEach(function (button) {{
          const id = button.getAttribute("data-flow-node");
          const selected = id === key;
          button.classList.toggle("selected", selected);
          button.classList.toggle("upstream", upstream.has(id));
          button.classList.toggle("downstream", downstream.has(id));
          button.classList.toggle("unrelated", !selected && !upstream.has(id) && !downstream.has(id));
          button.setAttribute("aria-pressed", selected ? "true" : "false");
        }});
        updateInspector(key);
      }}
      function clearSelection() {{
        root.dataset.selectedNode = "";
        root.querySelectorAll("[data-flow-node]").forEach(function (button) {{
          button.classList.remove("selected", "upstream", "downstream", "unrelated");
          button.setAttribute("aria-pressed", "false");
        }});
        updateInspector(payload.defaultNode);
      }}
      function setZoom(value) {{
        zoom = Math.max(0.82, Math.min(1.22, value));
        root.style.setProperty("--flow-zoom", String(zoom));
      }}

      root.querySelectorAll("[data-flow-mode-control]").forEach(function (button) {{
        button.addEventListener("click", function () {{ applyMode(button.getAttribute("data-flow-mode-control")); }});
      }});
      root.querySelectorAll("[data-architecture-mode-control]").forEach(function (button) {{
        button.addEventListener("click", function () {{ applyArchitecture(button.getAttribute("data-architecture-mode-control")); }});
      }});
      root.querySelectorAll("[data-flow-node]").forEach(function (button) {{
        button.addEventListener("click", function () {{ selectNode(button.getAttribute("data-flow-node")); }});
        button.addEventListener("keydown", function (event) {{
          if (event.key === "Enter" || event.key === " ") {{
            event.preventDefault();
            selectNode(button.getAttribute("data-flow-node"));
          }}
        }});
      }});
      root.querySelectorAll("[data-flow-zoom]").forEach(function (button) {{
        button.addEventListener("click", function () {{
          const action = button.getAttribute("data-flow-zoom");
          if (action === "in") setZoom(zoom + 0.08);
          if (action === "out") setZoom(zoom - 0.08);
          if (action === "fit") setZoom(0.92);
          root.dataset.zoomAction = action || "";
        }});
      }});
      const reset = root.querySelector("[data-flow-reset]");
      if (reset) reset.addEventListener("click", function () {{ clearSelection(); setZoom(1); root.dataset.zoomAction = "reset"; }});
      document.addEventListener("keydown", function (event) {{
        if (event.key === "Escape") clearSelection();
      }});
      applyMode(stored("atlas.workflow.flowMode", "simple"));
      applyArchitecture(stored("atlas.workflow.architectureMode", "latest"));
      setZoom(1);
      updateInspector(payload.defaultNode);
    }})();
    </script>
    """


def _localized_nodes(lang: str, statuses: Mapping[str, str], state: Mapping[str, Any]) -> list[dict[str, Any]]:
    labels_by_key = {node["key"]: _local(node["label"], lang) for node in NODES}
    tick = _tick(state)
    trust = _trust_text(state, lang)
    localized: list[dict[str, Any]] = []
    for node in NODES:
        key = str(node["key"])
        status = statuses.get(key, "waiting")
        affects_keys = [str(item) for item in node.get("affects", [])]
        localized.append(
            {
                "key": key,
                "stage": node["stage"],
                "kind": node["kind"],
                "label": labels_by_key[key],
                "acronym": _local(node.get("acronym", ""), lang),
                "purpose": _local(node["purpose"], lang),
                "inputs": _local_list(node["inputs"], lang),
                "outputs": _local_list(node["outputs"], lang),
                "affects": affects_keys,
                "affects_labels": [labels_by_key.get(item, item) for item in affects_keys],
                "brief_impact": _local(node["brief"], lang),
                "technical": _technical_detail(node, lang),
                "status": status,
                "status_label": TEXT[lang].get(f"status_{status}", status.upper()),
                "status_text": _status_text(key, status, state, lang),
                "last_tick_text": str(tick) if key in LATEST_PATH and tick is not None else TEXT[lang]["tick_unknown"],
                "trust_text": trust if key in {"decision_contract", "decision_brief", "feedback", "trust_update", "hypothesis_reweight", "self_iteration"} else TEXT[lang]["trust_unknown"],
                "current_path": key in LATEST_PATH,
                "expert_focus": bool(node.get("acronym")) or key in {"state_store", "forecast_ledger", "telemetry", "cache"},
            }
        )
    return localized


def _node_statuses(state: Mapping[str, Any]) -> dict[str, str]:
    runtime = state.get("runtime") if isinstance(state.get("runtime"), Mapping) else {}
    running = bool(runtime.get("running"))
    packet = state.get("last_decision_packet") if isinstance(state.get("last_decision_packet"), Mapping) else {}
    statuses = {str(node["key"]): "waiting" for node in NODES}
    if running:
        for key in LATEST_PATH:
            statuses[key] = "completed"
        statuses["decision_brief"] = "active" if packet else "waiting"
        statuses["feedback"] = "completed" if state.get("trust_index") is not None else "waiting"
        statuses["trust_update"] = "completed" if state.get("trust_index") is not None else "waiting"
    statuses["market_data"] = _market_status(state)
    statuses["provider_context"] = _provider_status(state)
    statuses["llm_router"] = _llm_status(packet)
    statuses["reality_outcome"] = "waiting"
    statuses["forecast_evaluation"] = _forecast_eval_status(state)
    statuses["state_store"] = "completed" if running or state else "waiting"
    statuses["forecast_ledger"] = "completed" if _forecast_counts(state).get("total", 0) else "waiting"
    statuses["telemetry"] = "completed" if running else "waiting"
    statuses["cache"] = "not_used"
    return statuses


def _market_status(state: Mapping[str, Any]) -> str:
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), Mapping) else {}
    channels = market.get("channels") if isinstance(market.get("channels"), Mapping) else {}
    if not channels:
        return "waiting"
    values = {str(value).upper() for value in channels.values()}
    if "FAILED" in values:
        return "failed"
    if "RATE_LIMITED" in values or "NOT_CONFIGURED" in values:
        return "degraded"
    if values & {"LIVE", "SIMULATED", "CACHED", "DELAYED"}:
        return "completed"
    return "waiting"


def _provider_status(state: Mapping[str, Any]) -> str:
    registry = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), Mapping) else {}
    active = registry.get("active_provider")
    return "completed" if active else "waiting"


def _llm_status(packet: Mapping[str, Any]) -> str:
    trace = str(packet.get("reasoning_trace") or packet.get("causal_summary") or "").lower()
    if not packet:
        return "waiting"
    if "all_providers_failed" in trace or "unavailable" in trace or "invalid" in trace:
        return "degraded"
    return "completed"


def _forecast_eval_status(state: Mapping[str, Any]) -> str:
    counts = _forecast_counts(state)
    return "completed" if counts.get("evaluated", 0) else "waiting"


def _forecast_counts(state: Mapping[str, Any]) -> dict[str, int]:
    daily = state.get("daily_cycle") if isinstance(state.get("daily_cycle"), Mapping) else {}
    review = daily.get("forecast_review") if isinstance(daily.get("forecast_review"), Mapping) else {}
    return {
        "total": int(review.get("total") or review.get("open") or 0),
        "evaluated": int(review.get("evaluated") or 0),
    }


def _default_node(statuses: Mapping[str, str]) -> str:
    if statuses.get("decision_brief") == "active":
        return "decision_brief"
    if statuses.get("feedback") == "completed":
        return "feedback"
    return "input_router"


def _status_text(key: str, status: str, state: Mapping[str, Any], lang: str) -> str:
    label = TEXT[lang].get(f"status_{status}", status.upper())
    tick = _tick(state)
    if tick is not None and key in LATEST_PATH:
        return f"{label} on Tick {tick}" if lang == "en" else f"{label} · Tick {tick}"
    return label


def _tick(state: Mapping[str, Any]) -> Any:
    return state.get("tick_counter") if state.get("tick_counter") is not None else None


def _trust_text(state: Mapping[str, Any], lang: str) -> str:
    value = state.get("trust_index")
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    runtime = state.get("runtime") if isinstance(state.get("runtime"), Mapping) else {}
    value = runtime.get("rolling_trust_index")
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return TEXT[lang]["trust_unknown"]


def _technical_detail(node: Mapping[str, Any], lang: str) -> str:
    acronym = _local(node.get("acronym", ""), lang)
    if acronym:
        return f"{acronym}: {node['key']}"
    return str(node["key"])


def _local(value: Any, lang: str) -> str:
    if isinstance(value, Mapping):
        return str(value.get(lang) or value.get("en") or "")
    return str(value or "")


def _local_list(value: Any, lang: str) -> list[str]:
    if isinstance(value, Mapping):
        raw = value.get(lang) or value.get("en") or []
    else:
        raw = value
    return [str(item) for item in raw] if isinstance(raw, list) else [str(raw)]
