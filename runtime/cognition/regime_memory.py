"""Regime memory for Atlas Runtime v0.3."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.logging import utc_now_iso
    from runtime.state_store import StateStore


class RegimeMemory:
    """Weighted memory of recent regime states."""

    def __init__(self, db_path: Optional[str] = None, max_states: int = 20, decay: float = 0.72) -> None:
        self.store = StateStore(db_path=db_path)
        self.max_states = max_states
        self.decay = decay

    def record(self, state: str, fusion: Dict[str, Any], causal: Dict[str, Any]) -> Dict[str, Any]:
        memory = self.store.get_state("regime_memory")
        sequence: List[Dict[str, Any]] = memory.get("sequence", [])
        sequence.append(
            {
                "state": state,
                "stress_score": fusion.get("stress_score", 0),
                "attention_pressure": fusion.get("attention_pressure", 0),
                "liquidity_score": fusion.get("liquidity_score", 50),
                "primary_driver": causal.get("primary_driver", "Unknown"),
                "recorded_at": utc_now_iso(),
            }
        )
        sequence = sequence[-self.max_states :]
        summary = self._summarize(sequence)
        self.store.set_state("regime_memory", {"sequence": sequence, "summary": summary})
        return summary

    def summary(self) -> Dict[str, Any]:
        memory = self.store.get_state("regime_memory")
        sequence = memory.get("sequence", [])
        if not sequence:
            return {"dominant_state": "NORMAL", "weighted_scores": {}, "sequence_length": 0}
        return self._summarize(sequence)

    def sequence(self) -> List[Dict[str, Any]]:
        return self.store.get_state("regime_memory").get("sequence", [])

    def _summarize(self, sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        weighted: Dict[str, float] = {}
        for age, item in enumerate(reversed(sequence)):
            weight = self.decay**age
            state = item["state"]
            weighted[state] = weighted.get(state, 0.0) + weight
        dominant = max(weighted, key=weighted.get) if weighted else "NORMAL"
        return {
            "dominant_state": dominant,
            "weighted_scores": {key: round(value, 4) for key, value in weighted.items()},
            "sequence_length": len(sequence),
            "last_state": sequence[-1]["state"] if sequence else "NORMAL",
        }
