"""Runtime-generated Atlas Decision Brief.

This generator is intentionally non-binding. It does not create CDE authority
and does not produce trading execution instructions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


ALLOWED_ACTION_BIASES = {
    "Hold",
    "Reduce exposure suggestion",
    "Observe",
    "Rebalance suggestion",
}


def generate_decision_brief(
    *,
    brief_id: str,
    trigger_type: str,
    event_type: Optional[str],
    pipeline: str,
    market_state: Dict[str, Any],
    regime_state: Dict[str, Any],
    portfolio_state: Dict[str, Any],
    risk_level: str,
    action_bias: str,
    modules_executed: List[str],
    llm_result: Dict[str, Any],
) -> str:
    """Generate one unified runtime Decision Brief."""

    if action_bias not in ALLOWED_ACTION_BIASES:
        action_bias = "Observe"

    regime_vector = regime_state.get(
        "probability_vector",
        {
            "bull_regime": 0,
            "distribution_risk": 0,
            "transition_to_exhaustion": 0,
            "crash_stress": 0,
            "consolidation": 0,
            "data_insufficient": 100,
        },
    )
    vector_line = ", ".join(f"{key}: {value}" for key, value in regime_vector.items())
    event_line = event_type if event_type else "None"
    modules_line = ", ".join(modules_executed) if modules_executed else "None"

    return "\n".join(
        [
            "# Atlas Decision Brief (Runtime Generated)",
            "",
            f"Brief ID: {brief_id}",
            f"Trigger Type: {trigger_type}",
            f"Event Type: {event_line}",
            f"Pipeline: {pipeline}",
            "",
            "## Market State",
            f"Summary: {market_state.get('summary', 'Data Missing')}",
            f"Data Status: {market_state.get('data_status', 'Data Missing')}",
            "",
            "## Regime Status",
            f"Status: {regime_state.get('status', 'Data Insufficient')}",
            f"Probability Vector: {vector_line}",
            f"Confidence: {regime_state.get('confidence', 'Low')}",
            "",
            "## Portfolio Exposure",
            f"Portfolio State: {portfolio_state.get('status', 'missing')} / {portfolio_state.get('privacy', 'redacted')}",
            f"Source: {portfolio_state.get('source', 'none')}",
            f"Status: {portfolio_state.get('status', 'missing')}",
            f"Privacy: {portfolio_state.get('privacy', 'redacted')}",
            "",
            "## Risk",
            f"Risk Level: {risk_level}",
            "",
            "## Runtime Execution",
            f"Modules Executed: {modules_line}",
            f"LLM Provider: {llm_result.get('provider', 'offline')}",
            f"LLM Status: {llm_result.get('status', 'unknown')}",
            "",
            "## Action Bias",
            f"{action_bias} (NON-BINDING)",
            "",
            "CDE Authority: Not created by runtime.",
            "Execution: No automatic trading execution. User confirmation remains mandatory.",
            "Safety: No portfolio modification. No CDE logic change.",
        ]
    )


def choose_action_bias(trigger_type: str, risk_level: str) -> str:
    """Choose a conservative non-binding action bias."""

    if risk_level in {"High", "Severe"}:
        return "Reduce exposure suggestion"
    if trigger_type == "event_trigger":
        return "Observe"
    if trigger_type == "intraday_run":
        return "Observe"
    return "Hold"
