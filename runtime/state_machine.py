"""Atlas Runtime state machine.

This state machine is runtime control logic, not an investment engine. It maps
event-stream signals into conservative runtime states used by the orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from runtime.event_stream import (
        EVENT_ATTENTION_SPIKE,
        EVENT_MARKET_ANOMALY,
        EVENT_NEWS_NARRATIVE_SPIKE,
        EVENT_PORTFOLIO_DRAWDOWN,
        EVENT_VOLUME_PRICE_BREAKOUT,
    )
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.event_stream import (
        EVENT_ATTENTION_SPIKE,
        EVENT_MARKET_ANOMALY,
        EVENT_NEWS_NARRATIVE_SPIKE,
        EVENT_PORTFOLIO_DRAWDOWN,
        EVENT_VOLUME_PRICE_BREAKOUT,
    )
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore


STATE_NORMAL = "NORMAL"
STATE_ATTENTION_EXPANSION = "ATTENTION_EXPANSION"
STATE_RISK_OFF = "RISK_OFF"
STATE_BREAKOUT = "BREAKOUT"
STATE_DISTRIBUTION = "DISTRIBUTION"
STATE_HIGH_VOLATILITY = "HIGH_VOLATILITY"


@dataclass
class TransitionResult:
    previous_state: str
    current_state: str
    reason: str
    event_id: Optional[str]
    event_type: Optional[str]
    confidence: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "reason": self.reason,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "updated_at": self.updated_at,
        }


class RuntimeStateMachine:
    """Persistent Atlas runtime state machine."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.store = StateStore(db_path=db_path)

    def current_state(self) -> str:
        state = self.store.get_system_state()
        return state.get("current_state", STATE_NORMAL)

    def transition(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        previous = self.current_state()
        current, reason, confidence = self._next_state(previous, event)
        result = TransitionResult(
            previous_state=previous,
            current_state=current,
            reason=reason,
            event_id=event.get("event_id") if event else None,
            event_type=event.get("event_type") if event else None,
            confidence=confidence,
            updated_at=utc_now_iso(),
        )
        self.store.save_system_state(result.to_dict())
        self.store.append_state_transition(result.to_dict())
        return result.to_dict()

    def _next_state(
        self,
        previous: str,
        event: Optional[Dict[str, Any]],
    ) -> tuple[str, str, str]:
        if not event:
            return previous, "No new event; state maintained.", "Low"

        event_type = event.get("event_type")
        priority = int(event.get("priority", 50))
        payload = event.get("payload", {})

        if event_type == EVENT_PORTFOLIO_DRAWDOWN:
            return STATE_RISK_OFF, "Portfolio drawdown event entered the queue.", "Medium"
        if event_type in {EVENT_MARKET_ANOMALY, "volatility_spike"} or priority >= 90:
            return STATE_HIGH_VOLATILITY, "High-priority anomaly / volatility event.", "Medium"
        if event_type == EVENT_VOLUME_PRICE_BREAKOUT:
            return STATE_BREAKOUT, "Volume / price breakout event.", "Medium"
        if event_type in {EVENT_ATTENTION_SPIKE, EVENT_NEWS_NARRATIVE_SPIKE}:
            if payload.get("leadership_fragility") in {"high", "severe"}:
                return STATE_DISTRIBUTION, "Attention spike with leadership fragility.", "Medium"
            return STATE_ATTENTION_EXPANSION, "Attention or narrative event entered the queue.", "Medium"
        if event_type == "market_close":
            return STATE_NORMAL, "Market close housekeeping event.", "Low"
        return previous, f"Event {event_type} does not require state change.", "Low"


def route_for_state(state: str) -> Dict[str, str]:
    """Return orchestrator route metadata for a runtime state."""

    routes = {
        STATE_NORMAL: {
            "pipeline": "Standard Daily Analysis",
            "route": "daily",
            "description": "run standard daily analysis",
        },
        STATE_ATTENTION_EXPANSION: {
            "pipeline": "Attention + Flow Inference",
            "route": "attention_flow",
            "description": "run attention and flow inference",
        },
        STATE_HIGH_VOLATILITY: {
            "pipeline": "Risk Reduction + Anomaly Check",
            "route": "risk_anomaly",
            "description": "run risk review and anomaly check",
        },
        STATE_BREAKOUT: {
            "pipeline": "Candidate Evaluation",
            "route": "candidate_evaluation",
            "description": "run candidate evaluation",
        },
        STATE_DISTRIBUTION: {
            "pipeline": "Portfolio Risk Scan",
            "route": "portfolio_risk_scan",
            "description": "run portfolio risk scan",
        },
        STATE_RISK_OFF: {
            "pipeline": "Risk-Off Portfolio Review",
            "route": "risk_off",
            "description": "run defensive risk review",
        },
    }
    return routes.get(state, routes[STATE_NORMAL])
