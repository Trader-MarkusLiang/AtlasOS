"""Atlas OS lightweight runtime orchestrator.

The orchestrator routes scheduler triggers into existing Atlas workflow names
and produces a runtime-generated Decision Brief. It intentionally avoids
simulation engines, regime prediction, trading execution, CDE changes, and
portfolio modification.
"""

from __future__ import annotations

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
    from runtime.llm_router import call_llm_raw, provider_metadata
    from runtime.logging import log_execution, utc_now_iso
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
    from runtime.llm_router import call_llm_raw, provider_metadata
    from runtime.logging import log_execution, utc_now_iso
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
            "log_path": self.log_path,
            "errors": self.errors,
        }


def run_runtime(
    trigger_type: str,
    event_type: Optional[str] = None,
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt-5.5",
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
            },
        )
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
        errors=errors,
    ).to_dict()


def run_state_runtime(
    system_state: str,
    event: Optional[Dict[str, Any]] = None,
    log_path: Optional[str] = None,
    db_path: Optional[str] = None,
    llm_model: str = "gpt-5.5",
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
        decision_packet, llm_result = _run_decision_contract(
            llm_model,
            cognitive_output=cognition if isinstance(cognition, dict) else {},
            market_state=market_state,
            regime_state=regime_state,
            risk_level=risk_level,
            action_bias=action_bias,
            runtime_context={
                "trigger_type": trigger_type,
                "system_state": system_state,
                "event_type": event_type,
                "pipeline": pipeline,
                "portfolio_state": portfolio_state,
            },
        )
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


def _read_portfolio_snapshot() -> Dict[str, str]:
    """Return read-only portfolio availability without exposing private data."""

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
    raw_text = call_llm_raw(llm_model, prompt, contract_context)
    packet = parse_decision_packet(raw_text)
    metadata = provider_metadata(llm_model)
    status = "validated_decision_packet"
    if (
        packet.get("recommended_action") == "neutral"
        and packet.get("risk_level") == "unknown"
        and float(packet.get("confidence", 0.0)) == 0.0
    ):
        status = "failsafe_decision_packet"
    return packet, {
        "provider": metadata["provider"],
        "model": metadata["model"],
        "status": status,
        "raw_text_only": True,
        "raw_output_stored": False,
    }


def _packet_action_to_bias(recommended_action: str) -> str:
    if recommended_action == "reduce":
        return "Reduce exposure suggestion"
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
            "Allowed action vocabulary: Hold, Reduce exposure suggestion, Observe, Rebalance suggestion.",
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
