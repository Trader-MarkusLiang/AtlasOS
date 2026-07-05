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
    from runtime.decision_brief import choose_action_bias, generate_decision_brief
    from runtime.llm_router import call_llm
    from runtime.logging import log_execution, utc_now_iso
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover - supports direct script usage
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.decision_brief import choose_action_bias, generate_decision_brief
    from runtime.llm_router import call_llm
    from runtime.logging import log_execution, utc_now_iso
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
        llm_result = call_llm(
            llm_model,
            _build_prompt(trigger_type, event_type, pipeline),
            {
                "market_state": market_state,
                "regime_state": regime_state,
                "portfolio_state": portfolio_state,
                "risk_level": risk_level,
                "action_bias": action_bias,
                "safety": "No automatic trading. CDE remains mandatory.",
            },
        )
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
