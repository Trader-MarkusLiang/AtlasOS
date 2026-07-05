"""Atlas OS minimal runtime orchestrator.

The orchestrator routes scheduler triggers into existing Atlas workflow names
and produces a runtime-generated Decision Brief stub. It intentionally avoids
simulation engines, regime prediction, trading execution, CDE changes, and
portfolio modification.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from runtime.logging import log_execution, utc_now_iso
except ModuleNotFoundError:  # pragma: no cover - supports direct script usage
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import log_execution, utc_now_iso


TRIGGER_DAILY = "daily_run"
TRIGGER_WEEKLY = "weekly_run"
TRIGGER_EVENT = "event_trigger"

PIPELINE_LIVE_ANALYSIS = "Live Analysis"
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
) -> Dict[str, Any]:
    """Route a runtime trigger and return execution status.

    Supported triggers:
    - daily_run -> atlas-daily pipeline
    - weekly_run -> simulation placeholder
    - event_trigger -> risk check + attention summary placeholder
    """

    run_id = str(uuid.uuid4())
    timestamp = utc_now_iso()
    errors: List[str] = []

    try:
        pipeline, modules = _route(trigger_type)
        module_results = [_call_atlas_module(module) for module in modules]
        modules_executed = [result["module"] for result in module_results]
        portfolio_state = _read_portfolio_snapshot()
        decision_brief = _generate_decision_brief(
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            modules_executed=modules_executed,
            portfolio_state=portfolio_state,
        )
        status = "success"
    except Exception as exc:  # Keep scheduler safe and observable.
        pipeline = "Unknown"
        modules_executed = []
        portfolio_state = _read_portfolio_snapshot()
        decision_brief = _generate_decision_brief(
            trigger_type=trigger_type,
            pipeline=pipeline,
            event_type=event_type,
            modules_executed=modules_executed,
            portfolio_state=portfolio_state,
            status="failure",
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
        "status": status,
        "errors": errors,
    }
    written_log = log_execution(record, log_path=log_path)
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
        return PIPELINE_LIVE_ANALYSIS, ["atlas-daily"]
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


def _generate_decision_brief(
    trigger_type: str,
    pipeline: str,
    event_type: Optional[str],
    modules_executed: List[str],
    portfolio_state: Dict[str, str],
    status: str = "success",
) -> str:
    """Generate the unified runtime output required by Step 1."""

    action_bias = "Observe / Hold only; non-binding; CDE authority still required."
    if status != "success":
        action_bias = "Observe only; runtime failure requires manual review."

    event_line = event_type if event_type else "None"
    modules_line = ", ".join(modules_executed) if modules_executed else "None"

    return "\n".join(
        [
            "# Atlas Decision Brief (Runtime Generated)",
            "",
            f"Trigger Type: {trigger_type}",
            f"Event Type: {event_line}",
            f"Pipeline: {pipeline}",
            "",
            "Market State: Placeholder only. No regime prediction implemented.",
            (
                "Portfolio State: "
                f"{portfolio_state['status']} / {portfolio_state['privacy']}"
            ),
            f"Modules Executed: {modules_line}",
            f"Action Bias: {action_bias}",
            "",
            "Safety: No automatic trading execution. No portfolio modification. No CDE logic change.",
        ]
    )
