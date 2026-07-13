"""Atlas OS lightweight runtime orchestrator.

The orchestrator routes scheduler triggers into existing Atlas workflow names
and produces a runtime-generated Decision Brief. It intentionally avoids
simulation engines, regime prediction, trading execution, CDE changes, and
portfolio modification.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from runtime.cognition.decision_contract import (
        build_decision_contract_context,
        build_decision_contract_prompt,
        parse_decision_packet,
    )
    from runtime.decision_brief import choose_action_bias, generate_decision_brief
    from runtime.llm_router import call_llm_for_task
    from runtime.logging import log_execution, utc_now_iso
    from runtime.portfolio_context import build_portfolio_context
    from runtime.state_machine import route_for_state
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover - supports direct script usage
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.cognition.decision_contract import (
        build_decision_contract_context,
        build_decision_contract_prompt,
        parse_decision_packet,
    )
    from runtime.decision_brief import choose_action_bias, generate_decision_brief
    from runtime.llm_router import call_llm_for_task
    from runtime.logging import log_execution, utc_now_iso
    from runtime.portfolio_context import build_portfolio_context
    from runtime.state_machine import route_for_state
    from runtime.state_store import StateStore


TRIGGER_DAILY = "daily_run"
TRIGGER_INTRADAY = "intraday_run"
TRIGGER_WEEKLY = "weekly_run"
TRIGGER_EVENT = "event_trigger"

PIPELINE_LIVE_ANALYSIS = "Live Analysis"
PIPELINE_INTRADAY = "Intraday Runtime Check"
PIPELINE_SIMULATION = "Simulation Placeholder"
PIPELINE_RISK_CHECK = "Risk Check"

ATLAS_SKILLS = {
    "atlas-daily": ".agents/skills/atlas-daily/SKILL.md",
    "atlas-research": ".agents/skills/atlas-research/SKILL.md",
    "atlas-portfolio": ".agents/skills/atlas-portfolio/SKILL.md",
}


@dataclass
class RuntimeResult:
    """Structured runtime result returned to scheduler callers."""

    run_id: str
    trigger_type: str
    pipeline: str
    timestamp: str
    modules_executed: List[str]
    status: str
    decision_brief: str
    log_path: str
    event_type: Optional[str] = None
    decision_packet: Dict[str, Any] = field(default_factory=dict)
    decision_packet_fresh: bool = True
    llm_tasks: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "trigger_type": self.trigger_type,
            "event_type": self.event_type,
            "pipeline": self.pipeline,
            "timestamp": self.timestamp,
            "modules_executed": self.modules_executed,
            "status": self.status,
            "decision_brief": self.decision_brief,
            "decision_packet": self.decision_packet,
            "decision_packet_fresh": self.decision_packet_fresh,
            "llm_tasks": self.llm_tasks,
            "log_path": self.log_path,
            "errors": self.errors,
        }


def run_runtime(
    trigger_type: str,
    event_type: Optional[str] = None,
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt5.5",
) -> Dict[str, Any]:
    """Route a runtime trigger and return execution status.

    Supported triggers:
    - daily_run -> atlas-daily pipeline
    - intraday_run -> regime check + attention update
    - weekly_run -> simulation placeholder
    - event_trigger -> risk evaluation + anomaly detection
    """

    run_id = str(uuid.uuid4())
    brief_id = f"brief-{run_id}"
    timestamp = utc_now_iso()
    errors: List[str] = []
    store = StateStore(db_path=db_path)

    try:
        pipeline, modules = _route(trigger_type)
        module_results = [_call_atlas_module(module) for module in modules]
        modules_executed = [result["module"] for result in module_results]
        portfolio_state = _read_portfolio_snapshot()
        market_state = _build_market_state(trigger_type, event_type)
        regime_state = _build_regime_state(trigger_type, event_type)
        risk_level = _derive_risk_level(trigger_type, event_type)
        action_bias = choose_action_bias(trigger_type, risk_level)
        task_context = {
            "trigger_kind": "scheduled_runtime",
            "events": [{"event_type": event_type or trigger_type, "source": "runtime_scheduler", "payload": {}}],
        }
        supporting_tasks = _run_supporting_tasks(
            task_context=task_context,
            cognitive_output={},
            portfolio_state=portfolio_state,
            runtime_context={"trigger_type": trigger_type, "event_type": event_type, "pipeline": pipeline},
            store=store,
        )
        decision_packet, llm_result = _run_decision_contract(
            llm_model,
            cognitive_output={},
            market_state=market_state,
            regime_state=regime_state,
            risk_level=risk_level,
            action_bias=action_bias,
            runtime_context={
                "trigger_type": trigger_type,
                "event_type": event_type,
                "pipeline": pipeline,
                "portfolio_state": portfolio_state,
                "research_synthesis": supporting_tasks["research"].get("output", {}),
                "decision_packet_id": brief_id,
            },
        )
        decision_packet_fresh = llm_result.get("status") == "validated_decision_packet"
        supporting_tasks["decision"] = _task_result_summary(llm_result, output=decision_packet)
        risk_level = _packet_risk_to_runtime(decision_packet["risk_level"], fallback=risk_level)
        action_bias = _packet_action_to_bias(decision_packet["recommended_action"])
        decision_brief = generate_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            market_state=market_state,
            regime_state=regime_state,
            portfolio_state=portfolio_state,
            risk_level=risk_level,
            action_bias=action_bias,
            modules_executed=modules_executed,
            llm_result=llm_result,
        )
        store.save_portfolio_snapshot(portfolio_state)
        store.save_regime_state(regime_state)
        store.append_attention_signal(_build_attention_signal(trigger_type, event_type))
        store.save_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            event_type=event_type,
            content=decision_brief,
            metadata={
                "pipeline": pipeline,
                "risk_level": risk_level,
                "action_bias": action_bias,
                "llm_provider": llm_result.get("provider"),
                "llm_model": llm_result.get("model"),
                "llm_status": llm_result.get("status"),
                "decision_packet": decision_packet,
                "llm_tasks": supporting_tasks,
                "raw_llm_output_stored": False,
            },
        )
        status = "success"
    except Exception as exc:  # Keep scheduler safe and observable.
        pipeline = "Unknown"
        modules_executed = []
        portfolio_state = _read_portfolio_snapshot()
        market_state = {"summary": "Runtime failure", "data_status": "Error"}
        regime_state = {"status": "Data Insufficient", "confidence": "Low"}
        risk_level = "Unknown"
        llm_result = {"provider": "none", "status": "not_called", "model": "none"}
        decision_brief = generate_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            market_state=market_state,
            regime_state=regime_state,
            portfolio_state=portfolio_state,
            risk_level=risk_level,
            action_bias="Observe",
            modules_executed=modules_executed,
            llm_result=llm_result,
        )
        decision_packet = _failure_decision_packet()
        decision_packet_fresh = False
        supporting_tasks = {}
        status = "failure"
        errors.append(str(exc))

    record = {
        "run_id": run_id,
        "trigger_type": trigger_type,
        "event_type": event_type,
        "pipeline": pipeline,
        "timestamp": timestamp,
        "modules_executed": modules_executed,
        "llm_model_used": llm_result.get("model"),
        "llm_provider": llm_result.get("provider"),
        "decision_packet": decision_packet,
        "decision_packet_fresh": decision_packet_fresh,
        "llm_tasks": supporting_tasks,
        "decision_brief_id": brief_id,
        "status": status,
        "errors": errors,
    }
    written_log = log_execution(record, log_path=log_path)
    store.append_system_log(record)
    return RuntimeResult(
        run_id=run_id,
        trigger_type=trigger_type,
        event_type=event_type,
        pipeline=pipeline,
        timestamp=timestamp,
        modules_executed=modules_executed,
        status=status,
        decision_brief=decision_brief,
        log_path=str(written_log),
        decision_packet=decision_packet,
        decision_packet_fresh=decision_packet_fresh,
        llm_tasks=supporting_tasks,
        errors=errors,
    ).to_dict()


def run_state_runtime(
    system_state: str,
    event: Optional[Dict[str, Any]] = None,
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt5.5",
) -> Dict[str, Any]:
    """Route autonomous runtime by state-machine state and event context."""

    run_id = str(uuid.uuid4())
    brief_id = f"brief-{run_id}"
    timestamp = utc_now_iso()
    errors: List[str] = []
    store = StateStore(db_path=db_path)
    event_type = event.get("event_type") if event else None
    route = route_for_state(system_state)
    trigger_type = "autonomous_state_loop"
    pipeline = route["pipeline"]

    try:
        modules = _route_state_modules(route["route"])
        module_results = [_call_atlas_module(module) for module in modules]
        modules_executed = [result["module"] for result in module_results]
        portfolio_state = _read_portfolio_snapshot()
        market_state = _build_state_market_state(system_state, event, route)
        regime_state = _build_state_regime_state(system_state, event)
        risk_level = _derive_state_risk_level(system_state, event)
        action_bias = choose_action_bias(trigger_type, risk_level)
        cognition = (event or {}).get("payload", {}).get("cognition", {})
        task_context = _task_context_from_event(event)
        runtime_context = {
            "trigger_type": trigger_type,
            "system_state": system_state,
            "event_type": event_type,
            "pipeline": pipeline,
            "portfolio_state": portfolio_state,
        }
        supporting_tasks = _run_supporting_tasks(
            task_context=task_context,
            cognitive_output=cognition if isinstance(cognition, dict) else {},
            portfolio_state=portfolio_state,
            runtime_context=runtime_context,
            store=store,
        )
        decision_hash = _stable_hash(
            {
                "task_context": task_context,
                "system_state": system_state,
                "market_state": market_state,
                "regime_state": regime_state,
                "research": supporting_tasks["research"].get("output", {}),
            }
        )
        if _decision_call_required(task_context, decision_hash, store):
            decision_packet, llm_result = _run_decision_contract(
                llm_model,
                cognitive_output=cognition if isinstance(cognition, dict) else {},
                market_state=market_state,
                regime_state=regime_state,
                risk_level=risk_level,
                action_bias=action_bias,
                runtime_context={
                    **runtime_context,
                    "research_synthesis": supporting_tasks["research"].get("output", {}),
                    "decision_packet_id": brief_id,
                },
            )
            decision_packet_fresh = llm_result.get("status") == "validated_decision_packet"
            if decision_packet_fresh:
                _store_task_state(store, "decision", decision_hash, decision_packet, llm_result)
        else:
            decision_packet = _latest_valid_decision_packet(store)
            llm_result = {
                "provider": "not_called",
                "model": "not_called",
                "status": "skipped_no_meaningful_delta",
                "task_role": "decision",
                "latency_ms": 0,
                "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
                "estimated_cost": "Unknown",
                "cost_status": "not_called",
                "cache_status": "no_input_delta",
                "fallback_attempts": [],
            }
            decision_packet_fresh = False
        supporting_tasks["decision"] = _task_result_summary(llm_result, output=decision_packet)
        risk_level = _packet_risk_to_runtime(decision_packet["risk_level"], fallback=risk_level)
        action_bias = _packet_action_to_bias(decision_packet["recommended_action"])
        decision_brief = generate_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            market_state=market_state,
            regime_state=regime_state,
            portfolio_state=portfolio_state,
            risk_level=risk_level,
            action_bias=action_bias,
            modules_executed=modules_executed,
            llm_result=llm_result,
        )
        store.save_portfolio_snapshot(portfolio_state)
        store.save_regime_state(regime_state)
        store.save_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            event_type=event_type,
            content=decision_brief,
            metadata={
                "pipeline": pipeline,
                "system_state": system_state,
                "risk_level": risk_level,
                "action_bias": action_bias,
                "llm_provider": llm_result.get("provider"),
                "llm_model": llm_result.get("model"),
                "llm_status": llm_result.get("status"),
                "decision_packet": decision_packet,
                "decision_packet_fresh": decision_packet_fresh,
                "llm_tasks": supporting_tasks,
                "raw_llm_output_stored": False,
            },
        )
        status = "success"
    except Exception as exc:
        modules_executed = []
        portfolio_state = _read_portfolio_snapshot()
        market_state = {"summary": "Autonomous runtime failure", "data_status": "Error"}
        regime_state = {"status": "Data Insufficient", "confidence": "Low"}
        risk_level = "Unknown"
        llm_result = {"provider": "none", "status": "not_called", "model": "none"}
        decision_brief = generate_decision_brief(
            brief_id=brief_id,
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            market_state=market_state,
            regime_state=regime_state,
            portfolio_state=portfolio_state,
            risk_level=risk_level,
            action_bias="Observe",
            modules_executed=modules_executed,
            llm_result=llm_result,
        )
        decision_packet = _failure_decision_packet()
        decision_packet_fresh = False
        supporting_tasks = {}
        status = "failure"
        errors.append(str(exc))

    record = {
        "run_id": run_id,
        "trigger_type": trigger_type,
        "event_type": event_type,
        "system_state": system_state,
        "pipeline": pipeline,
        "timestamp": timestamp,
        "modules_executed": modules_executed,
        "llm_model_used": llm_result.get("model"),
        "llm_provider": llm_result.get("provider"),
        "decision_packet": decision_packet,
        "decision_packet_fresh": decision_packet_fresh,
        "llm_tasks": supporting_tasks,
        "decision_brief_id": brief_id,
        "status": status,
        "errors": errors,
    }
    written_log = log_execution(record, log_path=log_path)
    store.append_system_log(record)
    return RuntimeResult(
        run_id=run_id,
        trigger_type=trigger_type,
        event_type=event_type,
        pipeline=pipeline,
        timestamp=timestamp,
        modules_executed=modules_executed,
        status=status,
        decision_brief=decision_brief,
        log_path=str(written_log),
        decision_packet=decision_packet,
        decision_packet_fresh=decision_packet_fresh,
        llm_tasks=supporting_tasks,
        errors=errors,
    ).to_dict()


def _route(trigger_type: str) -> tuple[str, List[str]]:
    if trigger_type == TRIGGER_DAILY:
        return PIPELINE_LIVE_ANALYSIS, ["atlas-daily", "atlas-portfolio"]
    if trigger_type == TRIGGER_INTRADAY:
        return PIPELINE_INTRADAY, [
            "atlas-research",
            "atlas-portfolio",
            "regime_check_placeholder",
            "attention_update_placeholder",
        ]
    if trigger_type == TRIGGER_WEEKLY:
        return PIPELINE_SIMULATION, [
            "atlas-research",
            "atlas-portfolio",
            "simulation_placeholder",
        ]
    if trigger_type == TRIGGER_EVENT:
        return PIPELINE_RISK_CHECK, [
            "atlas-research",
            "atlas-portfolio",
            "risk_evaluation_placeholder",
            "anomaly_detection_placeholder",
            "attention_summary_placeholder",
        ]
    raise ValueError(f"Unsupported trigger type: {trigger_type}")


def _route_state_modules(route_name: str) -> List[str]:
    routes = {
        "daily": ["atlas-daily", "atlas-portfolio"],
        "attention_flow": [
            "atlas-research",
            "atlas-portfolio",
            "attention_flow_placeholder",
        ],
        "risk_anomaly": [
            "atlas-research",
            "atlas-portfolio",
            "risk_evaluation_placeholder",
            "anomaly_detection_placeholder",
        ],
        "candidate_evaluation": [
            "atlas-research",
            "atlas-portfolio",
            "candidate_evaluation_placeholder",
        ],
        "portfolio_risk_scan": [
            "atlas-research",
            "atlas-portfolio",
            "portfolio_risk_scan_placeholder",
        ],
        "risk_off": [
            "atlas-research",
            "atlas-portfolio",
            "risk_off_placeholder",
        ],
        "crash_stress": [
            "atlas-research",
            "atlas-portfolio",
            "crash_stress_placeholder",
            "liquidity_risk_placeholder",
        ],
    }
    return routes.get(route_name, routes["daily"])


def _call_atlas_module(module_name: str) -> Dict[str, str]:
    """Connect to an existing Atlas skill name or approved placeholder."""

    if module_name.endswith("_placeholder"):
        return {
            "module": module_name,
            "status": "placeholder_only",
            "note": "No simulation, regime prediction, or investment engine implemented.",
        }

    skill_path = Path(ATLAS_SKILLS[module_name])
    if not skill_path.exists():
        raise FileNotFoundError(f"Atlas module skill not found: {module_name}")
    return {
        "module": module_name,
        "status": "available",
        "note": "Runtime skeleton routed to existing Atlas skill boundary.",
    }


def _read_portfolio_snapshot() -> Dict[str, Any]:
    """Return read-only portfolio availability without exposing private data."""

    runtime_context = build_portfolio_context()
    if runtime_context.get("status") == "configured":
        return runtime_context

    local_path = Path("06_Portfolio/portfolio.local.yaml")
    if local_path.exists():
        return {
            "source": "06_Portfolio/portfolio.local.yaml",
            "status": "read_only_available",
            "privacy": "redacted",
        }
    return {
        "source": "none",
        "status": "missing",
        "privacy": "no_private_data_loaded",
    }


def _build_market_state(trigger_type: str, event_type: Optional[str]) -> Dict[str, str]:
    if trigger_type == TRIGGER_DAILY:
        return {
            "summary": "Daily runtime market summary placeholder. Market data modules may enrich this later.",
            "data_status": "Placeholder",
        }
    if trigger_type == TRIGGER_INTRADAY:
        return {
            "summary": "Intraday runtime check placeholder for regime and attention updates.",
            "data_status": "Placeholder",
        }
    return {
        "summary": f"Event runtime check for {event_type or 'unknown event'}.",
        "data_status": "Placeholder",
    }


def _build_regime_state(trigger_type: str, event_type: Optional[str]) -> Dict[str, object]:
    # This is a confidence-limited runtime context, not a prediction model.
    vector = {
        "bull_regime": 0,
        "distribution_risk": 0,
        "transition_to_exhaustion": 0,
        "crash_stress": 0,
        "consolidation": 0,
        "data_insufficient": 100,
    }
    if event_type in {"attention_spike", "volatility_spike"}:
        vector["distribution_risk"] = 20
        vector["transition_to_exhaustion"] = 20
        vector["data_insufficient"] = 60
    return {
        "status": "Data Insufficient / Runtime Context Only",
        "probability_vector": vector,
        "confidence": "Low",
        "note": "No regime prediction implementation. CDE authority unchanged.",
    }


def _build_attention_signal(trigger_type: str, event_type: Optional[str]) -> Dict[str, str]:
    if event_type == "attention_spike":
        level = "High / User or event supplied"
    else:
        level = "Data Missing"
    return {
        "trigger_type": trigger_type,
        "event_type": event_type or "None",
        "attention_level": level,
        "confidence": "Low",
    }


def _derive_risk_level(trigger_type: str, event_type: Optional[str]) -> str:
    if event_type in {"volatility_spike", "attention_spike"}:
        return "High"
    if trigger_type == TRIGGER_EVENT:
        return "Medium"
    return "Low"


def _task_context_from_event(event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(event, dict):
        return {"trigger_kind": "scheduled_runtime", "events": []}
    payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
    supplied = payload.get("task_context")
    if isinstance(supplied, dict):
        context = dict(supplied)
        context["trigger_kind"] = _task_trigger_kind(context)
        return context
    bounded_payload = {key: value for key, value in payload.items() if key != "cognition"}
    context = {
        "events": [
            {
                "event_type": str(event.get("event_type") or "unknown"),
                "source": str(event.get("source") or "unknown"),
                "payload": bounded_payload,
            }
        ]
    }
    context["trigger_kind"] = _task_trigger_kind(context)
    return context


def _run_supporting_tasks(
    *,
    task_context: Dict[str, Any],
    cognitive_output: Dict[str, Any],
    portfolio_state: Dict[str, Any],
    runtime_context: Dict[str, Any],
    store: StateStore,
) -> Dict[str, Any]:
    trigger_kind = _task_trigger_kind(task_context)
    bounded_runtime_context = {
        key: runtime_context.get(key)
        for key in ("trigger_type", "system_state", "event_type", "pipeline")
        if runtime_context.get(key) is not None
    }
    base_context = {
        "task_context": task_context,
        "runtime_context": {**bounded_runtime_context, "task_trigger_kind": trigger_kind},
    }
    workhorse_input_hash = _stable_hash({"role": "workhorse", "task_context": task_context})
    if _has_workhorse_input(task_context):
        workhorse = _run_task_with_cache(
            role="workhorse",
            prompt=_workhorse_prompt(),
            context=base_context,
            input_hash=workhorse_input_hash,
            store=store,
            parser=_parse_workhorse_packet,
        )
    else:
        workhorse = _not_called_task("workhorse", "no_unstructured_or_research_input")

    research_input = {
        "role": "research",
        "task_context": task_context,
        "workhorse_evidence": workhorse.get("output", {}),
        "cognitive_output": cognitive_output,
        "portfolio_state": portfolio_state,
    }
    research_input_hash = _stable_hash(research_input)
    if trigger_kind in {"user_query", "proactive_update", "material_event", "scheduled_runtime"}:
        research = _run_task_with_cache(
            role="research",
            prompt=_research_prompt(),
            context={
                **base_context,
                "workhorse_evidence": workhorse.get("output", {}),
                "cognitive_output": cognitive_output,
                "portfolio_state": portfolio_state,
            },
            input_hash=research_input_hash,
            store=store,
            parser=_parse_research_packet,
        )
    else:
        research = _not_called_task("research", "no_research_trigger")
    return {"trigger_kind": trigger_kind, "workhorse": workhorse, "research": research}


def _run_task_with_cache(
    *,
    role: str,
    prompt: str,
    context: Dict[str, Any],
    input_hash: str,
    store: StateStore,
    parser: Any,
) -> Dict[str, Any]:
    previous = _task_state(store).get(role, {})
    if (
        previous.get("status") == "ok"
        and previous.get("input_hash") == input_hash
        and isinstance(previous.get("output"), dict)
        and previous["output"].get("status") not in {"invalid", "unavailable"}
    ):
        return {
            "task_role": role,
            "status": "cached",
            "route_status": previous.get("route_status", "ACTIVE"),
            "provider": previous.get("provider", "unknown"),
            "model": previous.get("model", "unknown"),
            "latency_ms": 0,
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "estimated_cost": 0.0,
            "cost_status": "cache_hit",
            "cache_status": "hit",
            "fallback_attempts": [],
            "output": previous["output"],
        }
    routed = call_llm_for_task(role, prompt, context, cache_status="miss")
    output = parser(str(routed.get("content") or ""), routed)
    result = _task_result_summary(routed, output=output)
    if result["status"] == "ok" and output.get("status") not in {"invalid", "unavailable"}:
        _store_task_state(store, role, input_hash, output, routed)
    return result


def _workhorse_prompt() -> str:
    return (
        "Return one JSON object only, with no markdown or reasoning before it. Use exactly this schema: "
        '{"status":"ok","query_intent":"string","signals":['
        '{"claim":"string","source":"string","timestamp":"string or Unknown",'
        '"evidence_type":"string","confidence":0.0}],"unknowns":["string"]}. '
        "Do not add top-level fields. Extract only supplied facts and source references. Never recommend an "
        "investment action, set a regime, score a portfolio, or infer missing evidence. Use status ok or "
        "insufficient_input and keep at most 12 signals."
    )


def _research_prompt() -> str:
    return (
        "Return one JSON object only, with no markdown or reasoning before it. Use exactly this schema: "
        '{"status":"ok","summary":"string","portfolio_relevance":["string"],'
        '"causal_factors":["string"],"counter_evidence":["string"],'
        '"hypotheses":["string"],"uncertainties":["string"]}. '
        "Every list may contain strings only, at most 8 items. Do not add fields, nested objects, scores, "
        "percentages not present in context, regime labels, actions, or portfolio authority. Use only supplied "
        "evidence and cognition, separate facts from hypotheses, preserve unknowns, and include counter-evidence."
    )


def _parse_workhorse_packet(raw_text: str, routed: Dict[str, Any]) -> Dict[str, Any]:
    fallback = {
        "status": "unavailable" if routed.get("status") != "ok" else "invalid",
        "query_intent": "Unknown",
        "signals": [],
        "unknowns": [str(routed.get("error") or "invalid_workhorse_output")[:200]],
    }
    data = _parse_json_object(raw_text)
    required = {"status", "query_intent", "signals", "unknowns"}
    if not data or set(data) != required or not isinstance(data.get("signals"), list) or not isinstance(data.get("unknowns"), list):
        return fallback
    signals = []
    for item in data["signals"][:24]:
        if not isinstance(item, dict):
            continue
        signals.append(
            {
                "claim": str(item.get("claim") or "")[:600],
                "source": str(item.get("source") or "Unknown")[:240],
                "timestamp": str(item.get("timestamp") or "Unknown")[:80],
                "evidence_type": str(item.get("evidence_type") or "Unverified")[:80],
                "confidence": _bounded_float(item.get("confidence"), 0.0, 1.0),
            }
        )
    return {
        "status": str(data.get("status") or "invalid")[:40],
        "query_intent": str(data.get("query_intent") or "Unknown")[:500],
        "signals": signals,
        "unknowns": [str(item)[:300] for item in data["unknowns"][:20]],
    }


def _parse_research_packet(raw_text: str, routed: Dict[str, Any]) -> Dict[str, Any]:
    fields = {
        "status",
        "summary",
        "portfolio_relevance",
        "causal_factors",
        "counter_evidence",
        "hypotheses",
        "uncertainties",
    }
    fallback = {
        "status": "unavailable" if routed.get("status") != "ok" else "invalid",
        "summary": "Research synthesis unavailable.",
        "portfolio_relevance": [],
        "causal_factors": [],
        "counter_evidence": [],
        "hypotheses": [],
        "uncertainties": [str(routed.get("error") or "invalid_research_output")[:200]],
    }
    data = _parse_json_object(raw_text)
    if not data or set(data) != fields:
        return fallback
    for key in fields - {"status", "summary"}:
        if not isinstance(data.get(key), list):
            return fallback
    return {
        "status": str(data.get("status") or "invalid")[:40],
        "summary": str(data.get("summary") or "")[:1600],
        "portfolio_relevance": [str(item)[:500] for item in data["portfolio_relevance"][:16]],
        "causal_factors": [str(item)[:500] for item in data["causal_factors"][:16]],
        "counter_evidence": [str(item)[:500] for item in data["counter_evidence"][:16]],
        "hypotheses": [str(item)[:500] for item in data["hypotheses"][:16]],
        "uncertainties": [str(item)[:500] for item in data["uncertainties"][:16]],
    }


def _parse_json_object(raw_text: str) -> Dict[str, Any]:
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start < 0:
            return {}
        try:
            data, _end = json.JSONDecoder().raw_decode(text[start:])
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


def _task_result_summary(routed: Dict[str, Any], *, output: Dict[str, Any]) -> Dict[str, Any]:
    status = str(routed.get("status") or "unknown")
    if output.get("status") in {"invalid", "unavailable"} and status == "ok":
        status = "invalid_output"
    return {
        "task_role": str(routed.get("task_role") or "unknown"),
        "status": status,
        "route_status": routed.get("route_status", "unknown"),
        "provider": routed.get("provider", "unknown"),
        "model": routed.get("model", "unknown"),
        "latency_ms": routed.get("latency_ms", 0),
        "usage": routed.get("usage", {}),
        "estimated_cost": routed.get("estimated_cost", "Unknown"),
        "cost_status": routed.get("cost_status", "Unknown"),
        "cache_status": routed.get("cache_status", "unknown"),
        "fallback_attempts": routed.get("fallback_attempts", []),
        "error": routed.get("error", ""),
        "output": output,
    }


def _not_called_task(role: str, reason: str) -> Dict[str, Any]:
    return {
        "task_role": role,
        "status": "not_called",
        "route_status": "CONFIGURED_NOT_ACTIVE",
        "provider": "not_called",
        "model": "not_called",
        "latency_ms": 0,
        "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
        "estimated_cost": "Unknown",
        "cost_status": "not_called",
        "cache_status": "not_applicable",
        "fallback_attempts": [],
        "error": reason,
        "output": {},
    }


def _task_state(store: StateStore) -> Dict[str, Any]:
    value = store.get_state("llm_task_runtime_state")
    return value if isinstance(value, dict) else {}


def _store_task_state(
    store: StateStore,
    role: str,
    input_hash: str,
    output: Dict[str, Any],
    routed: Dict[str, Any],
) -> None:
    state = _task_state(store)
    state[role] = {
        "input_hash": input_hash,
        "output": output,
        "provider": routed.get("provider"),
        "model": routed.get("model"),
        "status": routed.get("status"),
        "route_status": routed.get("route_status"),
        "latency_ms": routed.get("latency_ms"),
        "usage": routed.get("usage", {}),
        "estimated_cost": routed.get("estimated_cost", "Unknown"),
        "cost_status": routed.get("cost_status", "Unknown"),
        "fallback_attempts": routed.get("fallback_attempts", []),
        "updated_at": utc_now_iso(),
    }
    store.set_state("llm_task_runtime_state", state)


def _decision_call_required(task_context: Dict[str, Any], input_hash: str, store: StateStore) -> bool:
    if _task_trigger_kind(task_context) == "heartbeat":
        return False
    previous = _task_state(store).get("decision", {})
    return previous.get("input_hash") != input_hash


def _latest_valid_decision_packet(store: StateStore) -> Dict[str, Any]:
    latest = store.get_latest_decision_brief()
    metadata = latest.get("metadata", {}) if isinstance(latest, dict) else {}
    packet = metadata.get("decision_packet", {}) if isinstance(metadata, dict) else {}
    if isinstance(packet, dict):
        parsed = parse_decision_packet(json.dumps(packet, ensure_ascii=False))
        if parsed.get("reasoning_trace") != "invalid_llm_output":
            return parsed
    return _failure_decision_packet()


def _task_trigger_kind(task_context: Dict[str, Any]) -> str:
    events = task_context.get("events", []) if isinstance(task_context, dict) else []
    if not isinstance(events, list) or not events:
        return str(task_context.get("trigger_kind") or "scheduled_runtime")
    event_types = {str(item.get("event_type") or "") for item in events if isinstance(item, dict)}
    sources = {str(item.get("source") or "") for item in events if isinstance(item, dict)}
    if "user_input_event" in event_types or "ui_chat" in sources:
        return "user_query"
    if "proactive_update" in sources or any(
        isinstance(item, dict)
        and isinstance(item.get("payload"), dict)
        and item["payload"].get("update_kind") == "proactive_context_refresh"
        for item in events
    ):
        return "proactive_update"
    if event_types and event_types <= {"heartbeat"}:
        return "heartbeat"
    return "material_event"


def _has_workhorse_input(task_context: Dict[str, Any]) -> bool:
    if _task_trigger_kind(task_context) in {"user_query", "proactive_update"}:
        return True
    text = json.dumps(task_context, ensure_ascii=False, sort_keys=True).lower()
    return any(key in text for key in ('"query"', '"content"', '"headline"', '"title"', '"summary"', '"text"'))


def _stable_hash(value: Any) -> str:
    normalized = _stable_value(value)
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_value(value: Any) -> Any:
    volatile = {
        "timestamp",
        "created_at",
        "updated_at",
        "fused_at",
        "last_checked_at",
        "event_id",
        "update_cycle_id",
        "decision_packet_id",
    }
    if isinstance(value, dict):
        return {key: _stable_value(item) for key, item in value.items() if key not in volatile}
    if isinstance(value, list):
        return [_stable_value(item) for item in value]
    if isinstance(value, str):
        return value[:4000]
    return value


def _bounded_float(value: Any, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = minimum
    return round(max(minimum, min(maximum, parsed)), 4)


def _run_decision_contract(
    llm_model: str,
    *,
    cognitive_output: Dict[str, Any],
    market_state: Dict[str, Any],
    regime_state: Dict[str, Any],
    risk_level: str,
    action_bias: str,
    runtime_context: Dict[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    contract_context = build_decision_contract_context(
        cognitive_output=cognitive_output,
        market_state=market_state,
        regime_state=regime_state,
        risk_level=risk_level,
        action_bias=action_bias,
        runtime_context=runtime_context,
    )
    prompt = build_decision_contract_prompt(contract_context)
    routed = call_llm_for_task("decision", prompt, contract_context)
    raw_text = str(routed.get("content") or "")
    packet = parse_decision_packet(raw_text)
    status = "validated_decision_packet"
    if (
        packet.get("recommended_action") == "neutral"
        and packet.get("risk_level") == "unknown"
        and float(packet.get("confidence", 0.0)) == 0.0
    ):
        status = "failsafe_decision_packet"
    return packet, {
        "provider": str(routed.get("provider") or "unknown"),
        "model": str(routed.get("model") or llm_model),
        "status": status,
        "task_role": "decision",
        "route_status": routed.get("route_status"),
        "latency_ms": routed.get("latency_ms"),
        "usage": routed.get("usage", {}),
        "estimated_cost": routed.get("estimated_cost", "Unknown"),
        "cost_status": routed.get("cost_status", "Unknown"),
        "cache_status": routed.get("cache_status", "miss"),
        "fallback_attempts": routed.get("fallback_attempts", []),
        "error": routed.get("error", ""),
        "raw_text_only": True,
        "raw_output_stored": False,
    }


def _packet_action_to_bias(recommended_action: str) -> str:
    if recommended_action == "reduce":
        return "Reduce"
    if recommended_action == "observe":
        return "Observe"
    return "Observe"


def _packet_risk_to_runtime(risk_level: str, fallback: str) -> str:
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "severe": "Severe",
        "unknown": "Unknown",
    }
    return mapping.get(risk_level, fallback)


def _failure_decision_packet() -> Dict[str, Any]:
    return {
        "regime_state": "unknown",
        "confidence": 0.0,
        "risk_level": "unknown",
        "attention_state": "unknown",
        "liquidity_state": "unknown",
        "causal_summary": "Runtime exception before validated LLM reasoning.",
        "recommended_action": "neutral",
        "reasoning_trace": "runtime_failure_failsafe",
    }


def _build_prompt(trigger_type: str, event_type: Optional[str], pipeline: str) -> str:
    return "\n".join(
        [
            "Generate a concise Atlas Runtime Decision Brief supplement.",
            f"Trigger: {trigger_type}",
            f"Event: {event_type or 'None'}",
            f"Pipeline: {pipeline}",
            "Rules: no trading execution, no portfolio modification, no CDE bypass.",
            "Allowed action vocabulary: Observe, Hold, Reduce, Build, Accumulate.",
        ]
    )


def _build_state_market_state(
    system_state: str,
    event: Optional[Dict[str, Any]],
    route: Dict[str, str],
) -> Dict[str, str]:
    event_type = event.get("event_type") if event else "none"
    cognition = (event or {}).get("payload", {}).get("cognition", {})
    fusion = cognition.get("fusion", {})
    causal = cognition.get("causal", {})
    return {
        "summary": f"State-driven runtime route: {route['description']} from {system_state}.",
        "data_status": "Event Stream / Confidence Limited",
        "event_type": event_type,
        "fusion_stress_level": fusion.get("stress_level", "Data Missing"),
        "primary_driver": causal.get("primary_driver", "Unknown"),
    }


def _build_state_regime_state(
    system_state: str,
    event: Optional[Dict[str, Any]],
) -> Dict[str, object]:
    cognition = (event or {}).get("payload", {}).get("cognition", {})
    fusion = cognition.get("fusion", {})
    causal = cognition.get("causal", {})
    controller = cognition.get("controller", {})
    vector = {
        "bull_regime": 0,
        "distribution_risk": 0,
        "transition_to_exhaustion": 0,
        "crash_stress": 0,
        "consolidation": 0,
        "data_insufficient": 60,
    }
    if system_state == "BREAKOUT":
        vector["bull_regime"] = 25
        vector["data_insufficient"] = 45
    elif system_state == "DISTRIBUTION":
        vector["distribution_risk"] = 35
        vector["transition_to_exhaustion"] = 20
        vector["data_insufficient"] = 45
    elif system_state in {"RISK_OFF", "HIGH_VOLATILITY"}:
        vector["crash_stress"] = 20
        vector["distribution_risk"] = 25
        vector["data_insufficient"] = 55
    elif system_state == "ATTENTION_EXPANSION":
        vector["bull_regime"] = 15
        vector["transition_to_exhaustion"] = 15
        vector["data_insufficient"] = 70
    elif system_state == "CRASH_STRESS":
        vector["crash_stress"] = 55
        vector["distribution_risk"] = 25
        vector["data_insufficient"] = 20
    return {
        "status": f"{system_state} / Runtime State Context",
        "probability_vector": vector,
        "confidence": "Low",
        "event_id": event.get("event_id") if event else None,
        "fusion_stress_score": fusion.get("stress_score"),
        "fusion_attention_pressure": fusion.get("attention_pressure"),
        "fusion_liquidity_condition": fusion.get("liquidity_condition"),
        "causal_primary_driver": causal.get("primary_driver"),
        "transition_allowed": controller.get("transition_allowed"),
        "note": "Cognition-layer route only. No market prediction or CDE authority.",
    }


def _derive_state_risk_level(system_state: str, event: Optional[Dict[str, Any]]) -> str:
    if system_state == "CRASH_STRESS":
        return "Severe"
    if system_state in {"RISK_OFF", "HIGH_VOLATILITY", "DISTRIBUTION"}:
        return "High"
    if event and int(event.get("priority", 50)) >= 80:
        return "Medium"
    return "Low"


def _build_state_prompt(
    system_state: str,
    event: Optional[Dict[str, Any]],
    pipeline: str,
) -> str:
    return "\n".join(
        [
            "Generate a concise Atlas autonomous runtime Decision Brief supplement.",
            f"System State: {system_state}",
            f"Event Type: {event.get('event_type') if event else 'None'}",
            f"Pipeline: {pipeline}",
            "Rules: no trading execution, no portfolio modification, no CDE bypass.",
            "Output must remain non-binding and use Atlas action vocabulary only.",
        ]
    )
