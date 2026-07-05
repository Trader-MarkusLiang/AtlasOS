"""Event Fusion Engine for Atlas Runtime v0.3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List

try:
    from runtime.cognition.attention_liquidity_model import compute_attention_liquidity
    from runtime.logging import utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.cognition.attention_liquidity_model import compute_attention_liquidity
    from runtime.logging import utc_now_iso


@dataclass
class MarketFusionState:
    stress_level: str
    stress_score: int
    attention_pressure: int
    liquidity_condition: str
    liquidity_score: int
    volatility_regime: str
    narrative_intensity: int
    fused_event_count: int
    source_event_ids: List[str]
    source_event_types: List[str]
    proposed_state: str
    stability_score: int
    attention_liquidity: Dict[str, Any]
    fused_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stress_level": self.stress_level,
            "stress_score": self.stress_score,
            "attention_pressure": self.attention_pressure,
            "liquidity_condition": self.liquidity_condition,
            "liquidity_score": self.liquidity_score,
            "volatility_regime": self.volatility_regime,
            "narrative_intensity": self.narrative_intensity,
            "fused_event_count": self.fused_event_count,
            "source_event_ids": self.source_event_ids,
            "source_event_types": self.source_event_types,
            "proposed_state": self.proposed_state,
            "stability_score": self.stability_score,
            "attention_liquidity": self.attention_liquidity,
            "fused_at": self.fused_at,
        }


class EventFusionEngine:
    """Fuse simultaneous events into one market reality vector."""

    def __init__(self, window_minutes: int = 30) -> None:
        self.window_minutes = window_minutes

    def fuse(self, events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        windowed = _filter_window(list(events), self.window_minutes)
        if not windowed:
            return MarketFusionState(
                stress_level="Low",
                stress_score=0,
                attention_pressure=0,
                liquidity_condition="Data Missing",
                liquidity_score=50,
                volatility_regime="Data Missing",
                narrative_intensity=0,
                fused_event_count=0,
                source_event_ids=[],
                source_event_types=[],
                proposed_state="NORMAL",
                stability_score=40,
                attention_liquidity={},
                fused_at=utc_now_iso(),
            ).to_dict()

        attention_liquidity = compute_attention_liquidity(windowed)
        stress_score = 0
        volatility_score = 0
        narrative_intensity = 0

        for event in windowed:
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            priority = int(event.get("priority", 50))

            if event_type == "portfolio_drawdown":
                stress_score += 45
            if event_type in {"market_anomaly", "liquidity_shock"}:
                stress_score += 40
                volatility_score += 25
            if event_type == "volatility_spike":
                stress_score += 25
                volatility_score += 40
            if event_type == "volume_price_breakout":
                volatility_score += 20
            if event_type in {"attention_spike", "news_narrative_spike"}:
                narrative_intensity += 35
            if priority >= 90:
                stress_score += 10
            if _contains(payload, ["panic", "crisis", "暴跌", "流动性危机", "gap_down", "contracting"]):
                stress_score += 30
            if _contains(payload, ["viral", "dominant", "500%", "exploding", "mania"]):
                narrative_intensity += 25

        stress_score = _clamp(stress_score)
        volatility_score = _clamp(volatility_score)
        narrative_intensity = _clamp(narrative_intensity)
        attention_pressure = attention_liquidity.get("attention_index", 0)
        liquidity_score = attention_liquidity.get("liquidity_index", 50)
        proposed_state = _propose_state(
            stress_score=stress_score,
            volatility_score=volatility_score,
            attention_pressure=attention_pressure,
            liquidity_score=liquidity_score,
            narrative_intensity=narrative_intensity,
            event_types=[event.get("event_type") for event in windowed],
        )
        stability_score = _clamp(
            max(stress_score, attention_pressure, volatility_score, narrative_intensity)
            - min(30, attention_liquidity.get("divergence_score", 0) // 3)
        )
        if proposed_state in {"CRASH_STRESS", "RISK_OFF", "HIGH_VOLATILITY"}:
            stability_score = max(stability_score, 70)

        return MarketFusionState(
            stress_level=_level(stress_score),
            stress_score=stress_score,
            attention_pressure=attention_pressure,
            liquidity_condition=_liquidity_condition(liquidity_score),
            liquidity_score=liquidity_score,
            volatility_regime=_level(volatility_score),
            narrative_intensity=narrative_intensity,
            fused_event_count=len(windowed),
            source_event_ids=[event.get("event_id", "") for event in windowed],
            source_event_types=[event.get("event_type", "") for event in windowed],
            proposed_state=proposed_state,
            stability_score=stability_score,
            attention_liquidity=attention_liquidity,
            fused_at=utc_now_iso(),
        ).to_dict()


def _filter_window(events: List[Dict[str, Any]], window_minutes: int) -> List[Dict[str, Any]]:
    if not events:
        return []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=window_minutes)
    kept = []
    for event in events:
        created_at = _parse_time(event.get("created_at"))
        if created_at is None or created_at >= cutoff:
            kept.append(event)
    return kept


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _contains(payload: Dict[str, Any], needles: list[str]) -> bool:
    text = " ".join(str(value).lower() for value in payload.values())
    return any(needle.lower() in text for needle in needles)


def _propose_state(
    *,
    stress_score: int,
    volatility_score: int,
    attention_pressure: int,
    liquidity_score: int,
    narrative_intensity: int,
    event_types: list[str],
) -> str:
    if stress_score >= 85 and liquidity_score <= 35:
        return "CRASH_STRESS"
    if "portfolio_drawdown" in event_types:
        return "RISK_OFF"
    if "portfolio_drawdown" in event_types or (stress_score >= 75 and liquidity_score <= 45):
        return "RISK_OFF"
    if volatility_score >= 70 or stress_score >= 65:
        return "HIGH_VOLATILITY"
    if attention_pressure >= 70 and narrative_intensity >= 60 and liquidity_score < 45:
        return "DISTRIBUTION"
    if "volume_price_breakout" in event_types and liquidity_score >= 45:
        return "BREAKOUT"
    if attention_pressure >= 60 or narrative_intensity >= 50:
        return "ATTENTION_EXPANSION"
    return "NORMAL"


def _level(score: int) -> str:
    if score >= 85:
        return "Severe"
    if score >= 65:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def _liquidity_condition(score: int) -> str:
    if score <= 25:
        return "Liquidity Shock"
    if score <= 45:
        return "Tight / Weak"
    if score >= 70:
        return "Supportive"
    return "Neutral"


def _clamp(value: int) -> int:
    return max(0, min(100, value))
